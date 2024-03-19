from frappe.model.document import Document

from .shared_overrides import generic_invoices_on_submit_override


def on_submit(doc: Document, method: str) -> None:
    """Intercepts POS invoice on submit event"""

    generic_invoices_on_submit_override(doc, "POS Invoice")
