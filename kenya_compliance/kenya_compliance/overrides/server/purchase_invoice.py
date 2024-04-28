from functools import partial

import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from frappe.model.document import Document

from ...apis.api_builder import EndpointsBuilder
from ...apis.remote_response_status_handlers import (
    on_error,
    purchase_invoice_submission_on_success,
)
from ...utils import (
    build_headers,
    extract_document_series_number,
    get_route_path,
    get_server_url,
)

endpoints_builder = EndpointsBuilder()


def on_submit(doc: Document, method: str) -> None:
    company_name = doc.company

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("TrnsPurchaseSaveReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"
        payload = build_purchase_invoice_payload(doc)

        endpoints_builder.url = url
        endpoints_builder.headers = headers
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = partial(
            purchase_invoice_submission_on_success, document_name=doc.name
        )

        endpoints_builder.error_callback = on_error

        frappe.enqueue(
            endpoints_builder.make_remote_call,
            is_async=True,
            queue="default",
            timeout=300,
            job_name=f"{doc.name}_send_purchase_information",
            doctype="Purchase Invoice",
            document_name=doc.name,
        )


def build_purchase_invoice_payload(doc: Document) -> dict:
    series_no = extract_document_series_number(doc)
    items_list = get_items_details(doc)

    payload = {
        "invcNo": series_no,
        "orgInvcNo": 0,
        "spplrTin": None,
        "spplrBhfId": None,
        "spplrNm": None,
        "spplrInvcNo": None,
        "regTyCd": "A",
        "pchsTyCd": doc.custom_purchase_type_code,
        "rcptTyCd": doc.custom_receipt_type_code,
        "pmtTyCd": doc.custom_payment_type_code,
        "pchsSttsCd": doc.custom_purchase_status_code,
        "cfmDt": None,
        "pchsDt": "".join(str(doc.posting_date).split("-")),
        "wrhsDt": "",
        "cnclReqDt": "",
        "cnclDt": "",
        "rfdDt": "",
        "totItemCnt": len(items_list),
        "taxblAmtA": abs(doc.base_net_total),
        "taxblAmtB": 0,
        "taxblAmtC": 0,
        "taxblAmtD": 0,
        "taxblAmtE": 0,
        "taxRtA": round((doc.total_taxes_and_charges / doc.net_total) * 100, 2),
        "taxRtB": 0,
        "taxRtC": 0,
        "taxRtD": 0,
        "taxRtE": 0,
        "taxAmtA": abs(doc.total_taxes_and_charges),
        "taxAmtB": 0,
        "taxAmtC": 0,
        "taxAmtD": 0,
        "taxAmtE": 0,
        "totTaxblAmt": abs(doc.base_net_total),
        "totTaxAmt": abs(doc.total_taxes_and_charges),
        "totAmt": abs(doc.base_net_total),
        "remark": None,
        "regrNm": doc.owner,
        "regrId": doc.owner,
        "modrNm": doc.modified_by,
        "modrId": doc.modified_by,
        "itemList": items_list,
    }

    return payload


def get_items_details(doc: Document) -> list:
    items_list = []
    item_taxes = get_itemised_tax_breakup_data(doc)

    for index, item in enumerate(doc.items):
        print(index, item)
        taxable_amount = round(int(item_taxes[index]["taxable_amount"]) / item.qty, 2)
        tax_amount = round(item_taxes[index]["VAT"]["tax_amount"] / item.qty, 2)

        items_list.append(
            {
                "itemSeq": item.idx,
                "itemCd": None,
                "itemClsCd": item.custom_item_classification_code,
                "itemNm": item.item_name,
                "bcd": "",
                "spplrItemClsCd": None,
                "spplrItemCd": None,
                "spplrItemNm": None,
                "pkgUnitCd": item.custom_packaging_unit_code,
                "pkg": 1,
                "qtyUnitCd": item.custom_unit_of_quantity_code,
                "qty": abs(item.qty),
                "prc": item.base_rate,
                "splyAmt": item.base_rate,
                "dcRt": 0,
                "dcAmt": 0,
                "taxblAmt": taxable_amount,
                "taxTyCd": item.custom_taxation_type or "B",
                "taxAmt": tax_amount,
                "totAmt": taxable_amount,
                "itemExprDt": None,
            }
        )

    return items_list
