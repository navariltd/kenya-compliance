import asyncio

import frappe
from frappe.model.document import Document

from .handlers import handle_errors, update_last_request_date
from .utils import (
    build_common_payload,
    get_route_path,
    get_server_url,
    make_post_request,
)


def invoice_on_submit(doc: Document, method: str) -> None:
    # TODO: Add environment identifier
    environment = "Sandbox"
    payload = build_common_payload(doc, environment)
    server_url = get_server_url(doc, environment)

    if payload and server_url:
        route_path = get_route_path("CodeSearchReq")
        response = asyncio.run(
            make_post_request(
                f"{server_url}{route_path}",
                data=payload,
            )
        )

        if response:
            response_code = response["resultCd"]
            update_last_request_date(response["resultDt"])

            if response_code == "000":
                frappe.msgprint(
                    msg=response["resultMsg"],
                    title="Success",
                    indicator="green",
                )
            else:
                handle_errors(response, doc)
