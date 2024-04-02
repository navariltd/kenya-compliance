import asyncio
from typing import Literal

import aiohttp
import frappe
from frappe.integrations.utils import make_post_request
from frappe.model.document import Document

from ...handlers import handle_errors
from ...logger import etims_logger
from ...utils import (
    build_headers,
    build_invoice_payload,
    get_current_environment_state,
    get_environment_settings,
    get_route_path,
    get_server_url,
    make_post_request,
    update_last_request_date,
)


def generic_invoices_on_submit_override(
    doc: Document, invoice_type: Literal["Sales Invoice", "POS Invoice"]
) -> None:
    """Defines a function to handle sending of Sales information from relevant invoice documents

    Args:
        doc (Document): The doctype object or record
        invoice_type (Literal[&quot;Sales Invoice&quot;, &quot;POS Invoice&quot;]): The Type of the invoice. Either Sales, or POS
    """
    error_messages = None
    company_name = doc.company

    # TODO: This is an unsighyly hack! Clean it up
    current_environment = get_current_environment_state()
    settings = get_environment_settings(company_name, environment=current_environment)

    if (
        settings
        and doc.custom_transaction_progres
        == settings.transaction_progress_status_to_submit
    ):
        headers = build_headers(company_name)

        if headers:
            server_url = get_server_url(company_name)
            route_path, last_request_date = get_route_path("TrnsSalesSaveWrReq")

            if server_url and route_path:
                url = f"{server_url}{route_path}"

                invoice_identifier = "C" if doc.is_return else "S"
                payload = build_invoice_payload(doc, invoice_identifier)

                frappe.enqueue(
                    send_sales_information,
                    queue="default",
                    is_async=True,
                    timeout=300,
                    job_name=f"{doc.name}_send_sales_request",
                    doc=doc,
                    invoice_type=invoice_type,
                    headers=headers,
                    route_path=route_path,
                    url=url,
                    payload=payload,
                )

        elif not headers:
            error_messages = (
                "Headers not set for %s. Please ensure the tax Id is properly set"
                % doc.name
            )
            etims_logger.error(error_messages)
            frappe.throw(error_messages, title="Incorrect Setup")

        elif not last_request_date:
            error_messages = (
                "Last Request Date is not set for %s. Please ensure it is properly set"
                % doc.name
            )
            etims_logger.error(error_messages)
            frappe.throw(error_messages, title="Incorrect Setup")


def send_sales_information(doc, invoice_type, headers, route_path, url, payload):
    try:
        # TODO: Run job in background
        response = asyncio.run(make_post_request(url, payload, headers))

        if response:
            if response["resultCd"] == "000":
                update_last_request_date(response["resultDt"], route_path)
                data = response["data"]

                # Update Invoice fields from KRA's response
                frappe.db.set_value(
                    invoice_type,
                    doc.name,
                    {
                        "custom_current_receipt_number": data["curRcptNo"],
                        "custom_total_receipt_number": data["totRcptNo"],
                        "custom_internal_data": data["intrlData"],
                        "custom_receipt_signature": data["rcptSign"],
                        "custom_control_unit_date_time": data["sdcDateTime"],
                        "custom_successfully_submitted": 1,
                    },
                )

                doc.reload()

            else:
                # TODO: Fix issue with commiting in log_api_responses causing submission of this doc
                # log_api_responses(response, url, payload, "Failed")
                handle_errors(response, route_path, doc.name, doc)

    except aiohttp.client_exceptions.ClientConnectorError as error:
        etims_logger.exception(error, exc_info=True)
        frappe.throw(
            "Connection failed",
            error,
            title="Connection Error",
        )

    except asyncio.exceptions.TimeoutError as error:
        etims_logger.exception(error, exc_info=True)
        frappe.throw("Timeout Encountered", error, title="Timeout Error")
