import asyncio
from datetime import datetime

import frappe

from .logger import etims_logger
from .utils import (
    get_customer_pin,
    get_last_request_date,
    get_latest_communication_key,
    get_server_url,
    get_settings_record,
    make_post_request,
    save_communication_key_to_doctype,
)


def fetch_communication_key(response: dict[str, str]) -> None:
    try:
        communication_key = response["data"]["info"]["cmcKey"]

        if communication_key:
            saved_key = save_communication_key_to_doctype(
                communication_key, datetime.now(), "eTims Communication Keys"
            )

            frappe.errprint(f"Saved Key: {saved_key}")
    except KeyError as error:
        etims_logger.exception(error)


@frappe.whitelist(allow_guest=True)
def perform_code_search() -> dict:
    """Performs a code search to /selectCodeList

    Returns:
        dict: Response of code search
    """
    settings_record = "A123456789Z-Sandbox-005"
    server_url = get_server_url(settings_record)
    settings = get_settings_record(settings_record)
    last_request_date = get_last_request_date()
    communication_key = get_latest_communication_key()

    payload = {
        "tin": settings.get("tin"),
        "bhfId": settings.get("bhfId"),
        "cmcKey": communication_key,
        "lastReqDt": last_request_date,
    }

    response = asyncio.run(make_post_request(f"{server_url}/selectCodeList", payload))

    return response


@frappe.whitelist(allow_guest=True)
def perform_customer_search() -> dict:
    """Performs a customer search to /selectCustomer

    Returns:
        dict: Response of Customer Search
    """
    settings_record = "A123456789Z-Sandbox-005"
    server_url = get_server_url(settings_record)
    settings = get_settings_record(settings_record)
    communication_key = get_latest_communication_key()
    customer_pin = get_customer_pin()

    payload = {
        "tin": settings.get("tin"),
        "bhfId": settings.get("bhfId"),
        "cmcKey": communication_key,
        "custmTin": customer_pin,
    }

    response = asyncio.run(make_post_request(f"{server_url}/selectCustomer", payload))

    return response


@frappe.whitelist(allow_guest=True)
def perform_notice_search() -> dict:
    """Performs a notice search to /selectNoticeList

    Returns:
        dict: Response of Notice Search
    """
    settings_record = "A123456789Z-Sandbox-005"
    server_url = get_server_url(settings_record)
    settings = get_settings_record(settings_record)
    communication_key = get_latest_communication_key()
    last_request_date = get_last_request_date()

    payload = {
        "tin": settings.get("tin"),
        "bhfId": settings.get("bhfId"),
        "cmcKey": communication_key,
        "lastReqDt": last_request_date,
    }

    response = asyncio.run(make_post_request(f"{server_url}/selectNoticeList", payload))

    return response


@frappe.whitelist(allow_guest=True)
def perform_item_classification_search() -> dict:
    """Performs an item classification search to /selectItemClsList

    Returns:
        dict: Response of Item Classification Search
    """
    settings_record = "A123456789Z-Sandbox-005"
    server_url = get_server_url(settings_record)
    settings = get_settings_record(settings_record)
    communication_key = get_latest_communication_key()
    last_request_date = get_last_request_date()

    payload = {
        "tin": settings.get("tin"),
        "bhfId": settings.get("bhfId"),
        "cmcKey": communication_key,
        "lastReqDt": last_request_date,
    }

    response = asyncio.run(
        make_post_request(f"{server_url}/selectItemClsList", payload)
    )

    return response


@frappe.whitelist(allow_guest=True)
def perform_item_search() -> dict:
    """Performs an item search to /selectItemList

    Returns:
        dict: Response of Item Classification Search
    """
    settings_record = "A123456789Z-Sandbox-005"
    server_url = get_server_url(settings_record)
    settings = get_settings_record(settings_record)
    communication_key = get_latest_communication_key()
    last_request_date = get_last_request_date()

    payload = {
        "tin": settings.get("tin"),
        "bhfId": settings.get("bhfId"),
        "cmcKey": communication_key,
        "lastReqDt": last_request_date,
    }

    response = asyncio.run(make_post_request(f"{server_url}/selectItemList", payload))

    return response


@frappe.whitelist(allow_guest=True)
def perform_branch_search() -> dict:
    """Performs an item search to /selectItemList

    Returns:
        dict: Response of Item Classification Search
    """
    settings_record = "A123456789Z-Sandbox-005"
    server_url = get_server_url(settings_record)
    settings = get_settings_record(settings_record)
    communication_key = get_latest_communication_key()
    last_request_date = get_last_request_date()

    payload = {
        "tin": settings.get("tin"),
        "bhfId": settings.get("bhfId"),
        "cmcKey": communication_key,
        "lastReqDt": last_request_date,
    }

    response = asyncio.run(make_post_request(f"{server_url}/selectItemList", payload))

    return response
