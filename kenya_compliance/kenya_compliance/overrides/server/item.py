import json

import deprecation
import frappe
import frappe.defaults
from frappe.model.document import Document

from .... import __version__
from ...apis.apis import perform_item_registration


@deprecation.deprecated(
    deprecated_in="0.6.2",
    removed_in="1.0.0",
    current_version=__version__,
    details="Use the Register Item button in Item record",
)
def before_insert(doc: Document, method: str) -> None:
    """Item doctype before insertion hook"""

    item_registration_data = {
        "name": doc.name,
        "company_name": frappe.defaults.get_user_default("Company"),
        "itemCd": doc.custom_item_code_etims,
        "itemClsCd": doc.custom_item_classification,
        "itemTyCd": doc.custom_product_type,
        "itemNm": doc.item_name,
        "temStdNm": None,
        "orgnNatCd": doc.custom_etims_country_of_origin_code,
        "pkgUnitCd": doc.custom_packaging_unit_code,
        "qtyUnitCd": doc.custom_unit_of_quantity_code,
        "taxTyCd": ("B" if not doc.custom_taxation_type else doc.custom_taxation_type),
        "btchNo": None,
        "bcd": None,
        "dftPrc": doc.valuation_rate,
        "grpPrcL1": None,
        "grpPrcL2": None,
        "grpPrcL3": None,
        "grpPrcL4": None,
        "grpPrcL5": None,
        "addInfo": None,
        "sftyQty": None,
        "isrcAplcbYn": "Y",
        "useYn": "Y",
        "regrId": doc.owner,
        "regrNm": doc.owner,
        "modrId": doc.modified_by,
        "modrNm": doc.modified_by,
    }

    perform_item_registration(json.dumps(item_registration_data))


def validate(doc: Document, method: str) -> None:
    padded_series = str(doc.idx).zfill(7)
    item_code = f"{doc.custom_etims_country_of_origin_code}{doc.custom_product_type}{doc.custom_packaging_unit_code}{doc.custom_unit_of_quantity_code}{padded_series}"

    doc.custom_item_code_etims = item_code

    if doc.custom_taxation_type:
        relevant_tax_templates = frappe.get_all(
            "Item Tax Template",
            ["*"],
            {
                "name": ["like", "%Kenya%"],
                "custom_etims_taxation_type": doc.custom_taxation_type,
            },
        )

        if relevant_tax_templates:
            doc.set("taxes", [])
            for template in relevant_tax_templates:
                doc.append("taxes", {"item_tax_template": template.name})
 