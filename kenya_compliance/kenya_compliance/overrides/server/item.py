import json
import frappe
import frappe.defaults
from frappe.model.document import Document

from ...apis.apis import perform_item_registration


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
