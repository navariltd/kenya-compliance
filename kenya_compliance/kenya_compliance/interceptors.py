import asyncio

import frappe
from frappe.model.document import Document

from .utils import get_server_url, get_settings_document, make_post_request


def invoice_on_submit(doc: Document, method: str = None) -> None:
    settings_doctype = get_settings_document()
    server_url = get_server_url()

    response = asyncio.run(
        make_post_request(
            f"{server_url}/selectInitOsdcInfo",
            data={
                "tin": settings_doctype.get("pin"),
                "bhfId": settings_doctype.get("bhfId"),
                "dvcSrlNo": settings_doctype.get("device_serial_number"),
            },
        )
    )

    if response:
        if response["resultCd"] == "000":
            # Perform some action on provided document
            frappe.msgprint(msg="Success", title="Success", indicator="green")
        else:
            # Perform some action on provided document
            frappe.throw(
                f"Response from Server: {response['resultMsg']}",
                exc=frappe.DataError,
                title="Error Occured",
            )
