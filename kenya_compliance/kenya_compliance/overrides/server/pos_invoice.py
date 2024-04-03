from frappe.model.document import Document

from .sales_invoice import on_update
from .shared_overrides import generic_invoices_on_submit_override


def on_submit(doc: Document, method: str) -> None:
    """Intercepts POS invoice on submit event"""

    generic_invoices_on_submit_override(doc, "POS Invoice")


def pos_on_update(doc: Document, method: str) -> None:
    """Intercepts POS Invoice on submit event"""

    on_update(doc, method)
