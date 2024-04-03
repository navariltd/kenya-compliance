import asyncio
import json

import aiohttp
import frappe

from kenya_compliance.kenya_compliance.utils import update_last_request_date

from ..handlers import handle_errors
from ..logger import etims_logger
from ..utils import (
    build_headers,
    get_route_path,
    get_server_url,
    make_post_request,
    update_last_request_date,
)
from ..overrides.server.sales_invoice import on_submit


@frappe.whitelist()
def bulk_submit_invoices(docs_list) -> None:
    data = json.loads(docs_list)

    for record in data:
        frappe.msgprint(f"record: {record}")
        # on_submit(record, method=None)


# TODO: Unify the code to follow same conventions
@frappe.whitelist()
def perform_customer_search(request_data: str) -> dict | None:
    """Search customer details in the eTims Server

    Args:
        request_data (str): Data received from the client

    Returns:
        dict | None: The server's response
    """
    data = json.loads(request_data)

    company_name = data["company_name"]
    headers = build_headers(company_name)

    if headers:
        server_url = get_server_url(company_name)
        route_path, last_request_date = get_route_path("CustSearchReq")

        if server_url and route_path:
            url = f"{server_url}{route_path}s"
            payload = {"custmTin": data["tax_id"]}

            frappe.enqueue(
                make_customer_search_request,
                is_async=True,
                queue="default",
                timeout=300,
                job_name=f"{data['name']}_customer_search",
                data=data,
                headers=headers,
                route_path=route_path,
                url=url,
                payload=payload,
            )


@frappe.whitelist()
def perform_item_registration(request_data: str) -> dict | None:
    data = json.loads(request_data)

    company_name = data.pop("company_name")
    headers = build_headers(company_name)

    if headers:
        server_url = get_server_url(company_name)
        route_path, last_request_date = get_route_path("ItemSaveReq")

        if server_url and route_path:
            url = f"{server_url}{route_path}"

            frappe.enqueue(
                make_item_registration_request,
                is_async=True,
                queue="default",
                timeout=300,
                job_name=f"{data['itemNm']}_item_registration",
                data=data,
                headers=headers,
                route_path=route_path,
                url=url,
            )


def make_item_registration_request(data, headers, route_path, url):
    try:
        response = asyncio.run(make_post_request(url, data, headers))

        if response["resultCd"] == "000":
            frappe.db.set_value("Item", data["name"], "custom_item_registered", 1)
            update_last_request_date(response["resultDt"], route_path)

        else:
            handle_errors(response, route_path, data["itemNm"], "Item")

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


def make_customer_search_request(data, headers, route_path, url, payload) -> None:
    try:
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

            update_last_request_date(response["resultDt"], route_path)

        else:
            handle_errors(response, route_path, data["name"], "Customer")

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