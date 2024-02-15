from datetime import datetime

import frappe

from .logger import etims_logger
from .utils import save_communication_key_to_doctype


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
