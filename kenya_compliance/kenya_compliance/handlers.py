from typing import Any

import frappe
from frappe.model.document import Document

from .logger import etims_logger
from .utils import update_last_request_date


def handle_errors(
    response: dict[str, str],
    route: str,
    document_name: str,
    doctype: str | Document | None = None,
    integration_request_name: str | None = None,
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

        if integration_request_name is not None:
            # Update the integration request doctype
            update_integration_request(integration_request_name, error_message)


def update_integration_request(
    integration_request: str, error: Any = None, success: Any = None
) -> None:
    doc = frappe.get_doc("Integration Request", integration_request, for_update=False)

    if error:
        doc.error = error
        doc.status = "Failed"

    else:
        doc.output = success
        doc.status = "Completed"

    doc.save()
