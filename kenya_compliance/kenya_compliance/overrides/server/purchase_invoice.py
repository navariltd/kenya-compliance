import asyncio
from datetime import timedelta

import aiohttp
import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from frappe.integrations.utils import create_request_log
from frappe.model.document import Document

from ...handlers import handle_errors, update_integration_request
from ...logger import etims_logger
from ...utils import (
    build_datetime_from_string,
    build_headers,
    extract_document_series_number,
    get_route_path,
    get_server_url,
    make_post_request,
    update_last_request_date,
)


def on_submit(doc: Document, method: str) -> None:
    company_name = doc.company

    headers = build_headers(company_name)

    if headers:
        server_url = get_server_url(company_name)
        route_path, last_request_date = get_route_path("TrnsPurchaseSaveReq")

        if server_url and route_path:
            url = f"{server_url}{route_path}"

            payload = build_purchase_invoice_payload(doc)

            integration_request = create_request_log(
                data=payload,
                is_remote_request=True,
                request_headers=headers,
                service_name="etims",
                reference_docname=doc.name,
                reference_doctype="Purchase Invoice",
            )

            frappe.enqueue(
                send_purchase_request,
                is_async=True,
                queue="default",
                timeout=300,
                doc=doc,
                url=url,
                headers=headers,
                payload=payload,
                route_path=route_path,
                integration_request_name=integration_request.name,
                job_name=f"{doc.name}_send_purchase_request",
            )

        elif not headers:
            error_messages = (
                "Headers not set for %s. Please ensure the tax Id is properly set"
                % doc.name
            )
            etims_logger.error(error_messages)
            frappe.throw(error_messages, title="Incorrect Setup")

        elif not last_request_date:
            error_messages = (
                "Last Request Date is not set for %s. Please ensure it is properly set"
                % doc.name
            )
            etims_logger.error(error_messages)
            frappe.throw(error_messages, title="Incorrect Setup")


def send_purchase_request(
    doc: Document,
    url: str,
    headers: dict,
    payload: dict,
    route_path: str,
    integration_request_name: str | None = None,
) -> None:
    try:
        response = asyncio.run(make_post_request(url, payload, headers))

        if response:
            if response["resultCd"] == "000":
                update_last_request_date(response["resultDt"], route_path)

                # Update Invoice fields from KRA's response
                frappe.db.set_value(
                    "Purchase Invoice",
                    doc.name,
                    {
                        "custom_submitted_successfully": 1,
                    },
                )

                update_integration_request(
                    integration_request_name,
                    success=f"{response['resultCd']}\n{response['resultDt']}",
                )
                doc.reload()
                return

            else:
                handle_errors(
                    response,
                    route_path,
                    doc.name,
                    doc,
                    integration_request_name=integration_request_name,
                )

    except aiohttp.client_exceptions.ClientConnectorError as error:
        etims_logger.exception(error, exc_info=True)
        frappe.throw(
            "Connection failed",
            error,
            title="Connection Error",
        )

    except asyncio.exceptions.TimeoutError as error:
        etims_logger.exception(error, exc_info=True)
        frappe.throw("Timeout Encountered", error, title="Timeout Error")


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
                "taxTyCd": item.custom_taxation_type,
                "taxAmt": tax_amount,
                "totAmt": taxable_amount,
                "itemExprDt": None,
            }
        )

    return items_list
