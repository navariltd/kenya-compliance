from functools import partial
from typing import Literal

import frappe
from frappe.model.document import Document

from ...apis.api_builder import EndpointsBuilder
from ...apis.remote_response_status_handlers import (
    on_error,
    sales_information_submission_on_success,
)
from ...utils import (
    build_headers,
    build_invoice_payload,
    get_current_environment_state,
    get_environment_settings,
    get_route_path,
    get_server_url,
)

endpoints_builder = EndpointsBuilder()


def generic_invoices_on_submit_override(
    doc: Document, invoice_type: Literal["Sales Invoice", "POS Invoice"]
) -> None:
    """Defines a function to handle sending of Sales information from relevant invoice documents

    Args:
        doc (Document): The doctype object or record
        invoice_type (Literal[&quot;Sales Invoice&quot;, &quot;POS Invoice&quot;]): The Type of the invoice. Either Sales, or POS
    """
    company_name = doc.company

    current_environment = get_current_environment_state()
    settings = get_environment_settings(company_name, environment=current_environment)

    if (
        settings
        and doc.custom_transaction_progres
        == settings.transaction_progress_status_to_submit
    ):
        headers = build_headers(company_name)
        server_url = get_server_url(company_name)
        route_path, last_request_date = get_route_path("TrnsSalesSaveWrReq")

        if headers and server_url and route_path:
            url = f"{server_url}{route_path}"

            invoice_identifier = "C" if doc.is_return else "S"
            payload = build_invoice_payload(doc, invoice_identifier)

            endpoints_builder.headers = headers
            endpoints_builder.url = url
            endpoints_builder.payload = payload
            endpoints_builder.success_callback = partial(
                sales_information_submission_on_success,
                document_name=doc.name,
                invoice_type=invoice_type,
            )
            endpoints_builder.error_callback = on_error

            frappe.enqueue(
                endpoints_builder.make_remote_call,
                is_async=True,
                queue="default",
                timeout=300,
                job_id=f"{doc.name}_send_sales_request",
                doctype=invoice_type,
                document_name=doc.name,
            )
