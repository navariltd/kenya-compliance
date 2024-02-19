import asyncio

import frappe
from frappe.model.document import Document

from .utils import get_server_url, get_settings_record, make_post_request
from .logger import etims_logger
from .handlers import fetch_communication_key


def invoice_on_submit(doc: Document, method: str = None) -> None:
    settings_record = "A123456789Z-Sandbox-005"  # TODO: Cleanup
    settings_doctype = get_settings_record(settings_record)
    server_url = get_server_url(settings_record)
    errors, messages = None, None

    payload = {
        "tin": settings_doctype.get("pin"),
        "bhfId": settings_doctype.get("bhfId"),
        "dvcSrlNo": settings_doctype.get("device_serial_number"),
    }

    response = asyncio.run(
        make_post_request(
            f"{server_url}/selectInitOsdcInfo",
            data=payload,
        )
    )

    if response:
        if response["resultCd"] == "000":
            # Perform some action on provided document
            fetch_communication_key(response)
            frappe.msgprint(
                msg="Successful Initialisation", title="Success", indicator="green"
            )
        else:
            # Perform some action on provided document
            errors = (
                "Response from Server: %s with status code: %s. Result Date: %s"
                % (response["resultMsg"], response["resultCd"], response["resultDt"])
            )
            messages = f"Response from Server: {response['resultMsg']}"
            etims_logger.error(errors)
            frappe.throw(
                msg=messages,
                exc=frappe.DataError,
                title=f"Error Status Code {response['resultCd']}",
            )
