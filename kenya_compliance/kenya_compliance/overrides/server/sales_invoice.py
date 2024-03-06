import asyncio

import aiohttp
import frappe
from frappe.model.document import Document

from ...logger import etims_logger
from ...utils import (
    build_headers,
    get_last_request_date,
    get_route_path,
    get_server_url,
    make_post_request,
    queue_request,
)


def on_submit(doc: Document, method: str) -> None:
    """Intercepts submit event for document"""
    error_messages = None
    headers = build_headers(doc)
    last_request_date = get_last_request_date()

    if headers and last_request_date:
        server_url = get_server_url(doc)
        route_path = get_route_path("CodeSearchReq")

        if server_url and route_path:
            url = f"{server_url}{route_path}"

            try:
                # TODO: Run job in background
                response = asyncio.run(
                    make_post_request(url, {"lastReqDt": "20230101000000"}, headers)
                )

                if response:
                    # TODO: Add proper handling of responses
                    print(f"{response}")

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
