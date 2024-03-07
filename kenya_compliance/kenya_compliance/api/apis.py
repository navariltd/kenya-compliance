import asyncio
import json

import frappe

from ..utils import (
    build_headers,
    get_route_path,
    get_server_url,
    make_post_request,
    queue_request,
)


@frappe.whitelist()
def perform_customer_search(request_data: str) -> None:
    data = json.loads(request_data)
    server_url = get_server_url(data["document"])
    route_path = get_route_path("CustSearchReq")

    if server_url and route_path:
        url = f"{server_url}{route_path}"

        payload = {"custmTin": data["document"]["tax_id"]}
        headers = build_headers(data["document"])

        response = asyncio.run(make_post_request(url, payload, headers))

        if response["resultCd"] == "00":
            return response["data"]

        frappe.throw(response["resultMsg"], title="Error Response")
