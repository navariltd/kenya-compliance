from datetime import datetime

import frappe
from frappe.model.document import Document

from .doctype.doctype_names_mapping import LAST_REQUEST_DATE_DOCTYPE_NAME
from .logger import etims_logger
from .utils import build_datetime_from_string, save_communication_key_to_doctype


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


def handle_errors(response: dict[str, str], doc: Document) -> None:
    """Handles and logs error responses

    Args:
        response (dict[str, str]): The response object
        doc (Document): Doctype calling the function
    """
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
            reference_name=doc.name,
            reference_doctype=doc,
        )
        raise


def update_last_request_date(
    response_date: str, doctype: str = LAST_REQUEST_DATE_DOCTYPE_NAME
) -> str:
    """Updates the last request date

    Args:
        response_date (str): The response date
        doctype (str, optional): The doctype to update. Defaults to LAST_REQUEST_DATE_DOCTYPE_NAME.

    Returns:
        str: The last request date as a string
    """
    result_date = response_date

    request_date_doctype = frappe.get_doc(doctype)
    request_date_doctype.lastreqdt = build_datetime_from_string(
        response_date, "%Y%m%d%H%M%S"
    )

    request_date_doctype.insert()
    frappe.db.commit()

    etims_logger.info(
        "%s set as last request date in doctype %s" % (response_date, doctype)
    )
    return result_date
