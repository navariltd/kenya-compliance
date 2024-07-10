from collections import defaultdict

from frappe.model.document import Document
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data

from .shared_overrides import generic_invoices_on_submit_override


def on_submit(doc: Document, method: str) -> None:
    """Intercepts submit event for document"""

    if not doc.is_consolidated and not doc.custom_successfully_submitted:
        generic_invoices_on_submit_override(doc, "Sales Invoice")


def on_save(doc: Document, method: str) -> None:
    item_taxes = get_itemised_tax_breakup_data(doc)

    taxes_breakdown = defaultdict(list)
    taxable_breakdown = defaultdict(list)
    for index, item in enumerate(doc.items):
        taxes_breakdown[item.custom_taxation_type_code].append(
            item_taxes[index]["VAT"]["tax_amount"]
        )
        taxable_breakdown[item.custom_taxation_type_code].append(
            item_taxes[index]["taxable_amount"]
        )

    update_tax_breakdowns(doc, (taxes_breakdown, taxable_breakdown))


def update_tax_breakdowns(invoice: Document, mapping: tuple) -> None:
    invoice.custom_tax_a = sum(mapping[0]["A"])
    invoice.custom_tax_b = sum(mapping[0]["B"])
    invoice.custom_tax_c = sum(mapping[0]["C"])
    invoice.custom_tax_d = sum(mapping[0]["D"])
    invoice.custom_tax_e = sum(mapping[0]["E"])

    invoice.custom_taxbl_amount_a = sum(mapping[1]["A"])
    invoice.custom_taxbl_amount_b = sum(mapping[1]["B"])
    invoice.custom_taxbl_amount_c = sum(mapping[1]["C"])
    invoice.custom_taxbl_amount_d = sum(mapping[1]["D"])
    invoice.custom_taxbl_amount_e = sum(mapping[1]["E"])
