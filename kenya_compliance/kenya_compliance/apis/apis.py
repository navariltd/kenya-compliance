import asyncio
import json

import frappe
from datetime import datetime

from kenya_compliance.kenya_compliance.utils import update_last_request_date

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
    route_path, last_request_date = get_route_path("CustSearchReq")

    if server_url and route_path:
        url = f"{server_url}{route_path}"

        payload = {"custmTin": data["tax_id"]}
        headers = build_headers(data["company_name"])

        # TODO: Enqueue in background jobs queue
        response = asyncio.run(make_post_request(url, payload, headers))

        if response["resultCd"] == "000":
            frappe.db.set_value(
                "Customer",
                data["name"],
                {
                    "custom_current_receipt_number": data["curRcptNo"],
                    "custom_total_receipt_number": data["totRcptNo"],
                    "custom_internal_data": data["intrlData"],
                    "custom_receipt_signature": data["rcptSign"],
                    "custom_control_unit_date_time": data["sdcDateTime"],
                    "custom_successfully_submitted": 1,
                },
            )

            update_last_request_date(response, route_path)

        handle_errors(response, route_path, data["name"], "Customer")
