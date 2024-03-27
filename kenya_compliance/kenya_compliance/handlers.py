from datetime import datetime

import frappe
from frappe.model.document import Document

from .logger import etims_logger
from .utils import (
    save_communication_key_to_doctype,
    update_last_request_date,
)


def fetch_communication_key(response: dict[str, str]) -> str | None:
    """Extracts communication Key from reponse object

    Args:
        response (dict[str, str]): The response object

    Returns:
        str | None: The extracted key or None if none is encountered
    """
    try:
        communication_key = response["data"]["info"]["cmcKey"]

        if communication_key:
            saved_key = save_communication_key_to_doctype(
                communication_key, datetime.now()
            )

            return saved_key.cmckey

    except KeyError as error:
        etims_logger.exception(error)
        frappe.throw("KeyError encountered", KeyError, title="Key Error")


def handle_errors(
    response: dict[str, str],
    route: str,
    document_name: str,
    doctype: str | Document | None = None,
) -> None:
    error_message, error_code = response["resultMsg"], response["resultCd"]

    etims_logger.error("%s, Code: %s" % (error_message, error_code))

    try:
        frappe.throw(
            error_message,
            frappe.InvalidStatusError,
            title=f"Error: {error_code}",
        )

    except frappe.InvalidStatusError as error:
        frappe.log_error(
            frappe.get_traceback(with_context=True),
            error,
            reference_name=document_name,
            reference_doctype=doctype,
        )
        raise

    finally:
        update_last_request_date(response["resultDt"], route)
