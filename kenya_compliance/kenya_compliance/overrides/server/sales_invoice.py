from frappe.model.document import Document

from .shared_overrides import generic_invoices_on_submit_override


def on_submit(doc: Document, method: str) -> None:
    """Intercepts submit event for document"""

    if not doc.is_pos and not doc.update_stock:
        generic_invoices_on_submit_override(doc, "Sales Invoice")


def on_update(doc: Document, method: str) -> None:
    """Intercepts update events for document"""

    match doc.docstatus:
        case 0:
            doc.custom_transaction_progres = "Wait for Approval"
        case 1:
            doc.custom_transaction_progres = "Approved"
        case 2:
            doc.custom_transaction_progres = "Cancelled"
        case _:  # Default case
            doc.custom_transaction_progres = "Transferred"
