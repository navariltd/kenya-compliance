import asyncio
from datetime import datetime

import frappe

from .logger import etims_logger
from .utils import (
    get_last_request_date,
    get_latest_communication_key,
    get_server_url,
    get_settings_document,
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


def perform_code_search() -> dict:
    """Performs a code search

    Returns:
        dict: Response of code search
    """
    server_url = get_server_url()
    settings = get_settings_document()
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
