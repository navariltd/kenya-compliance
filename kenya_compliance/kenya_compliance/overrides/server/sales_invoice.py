import asyncio

import aiohttp
import frappe
from frappe.model.document import Document

from ...handlers import handle_errors
from ...logger import etims_logger
from ...utils import (
    build_headers,
    build_invoice_payload,
    get_last_request_date,
    get_route_path,
    get_server_url,
    log_api_responses,
    make_post_request,
    queue_request,
)


def on_submit(doc: Document, method: str) -> None:
    """Intercepts submit event for document"""
    if not doc.custom_defer_invoice_submission_to_kra:
        error_messages = None
        company_tax_id = doc.company_tax_id

        headers = build_headers(company_tax_id)
        last_request_date = get_last_request_date()

        if headers and last_request_date:
            server_url = get_server_url(company_tax_id)
            route_path = get_route_path("TrnsSalesSaveWrReq")

            if server_url and route_path:
                url = f"{server_url}{route_path}"
                payload = build_invoice_payload(doc, "S")

                try:
                    # TODO: Run job in background
                    response = asyncio.run(make_post_request(url, payload, headers))

                    if response:
                        if response["resultCd"] == "000":
                            data = response["data"]

                            # Update Invoice fields from KRA's response
                            frappe.db.set_value(
                                "Sales Invoice",
                                doc.name,
                                {
                                    "custom_current_receipt_number": data["curRcptNo"],
                                    "custom_total_receipt_number": data["totRcptNo"],
                                    "custom_internal_data": data["intrlData"],
                                    "custom_receipt_signature": data["rcptSign"],
                                    "custom_control_unit_date_time": data[
                                        "sdcDateTime"
                                    ],
                                    "custom_successfully_submitted": 1,
                                },
                            )

                        else:
                            # TODO: Fix issue with commiting in log_api_responses causing premature submission of this doc
                            # log_api_responses(response, url, payload, "Failed")
                            handle_errors(response, doc.name, doc)

                except aiohttp.client_exceptions.ClientConnectorError as error:
                    etims_logger.exception(error, exc_info=True)
                    frappe.throw(
                        "Connection failed",
                        error,
                        title="Connection Error",
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
