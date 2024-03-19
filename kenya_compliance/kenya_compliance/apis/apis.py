import asyncio
import json

import frappe

from ..handlers import handle_errors
from ..utils import (
    build_headers,
    get_route_path,
    get_server_url,
    make_post_request,
    queue_request,
)


@frappe.whitelist()
def perform_customer_search(request_data: str) -> dict | None:
    """Search customer details in the eTims Server

    Args:
        request_data (str): Data received from the client

    Returns:
        dict | None: The server's response
    """
    data = json.loads(request_data)
    server_url = get_server_url(data["company_name"])
    route_path = get_route_path("CustSearchReq")

    if server_url and route_path:
        url = f"{server_url}{route_path}"

        payload = {"custmTin": data["tax_id"]}
        headers = build_headers(data["company_name"])

        # TODO: Enqueue in background jobs queue
        response = asyncio.run(make_post_request(url, payload, headers))

        if response["resultCd"] == "000":
            return response["data"]

        handle_errors(response, data["name"], "Customer")
