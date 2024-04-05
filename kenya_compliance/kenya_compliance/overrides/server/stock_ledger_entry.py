import asyncio

import aiohttp
import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from frappe.integrations.utils import create_request_log
from frappe.model.document import Document

from ...handlers import handle_errors
from ...logger import etims_logger
from ...utils import (
    build_headers,
    extract_document_series_number,
    get_route_path,
    get_server_url,
    make_post_request,
    update_last_request_date,
)


def on_update(doc: Document, method: str | None = None) -> None:
    company_name = doc.company
    all_items = frappe.db.get_all(
        "Item", ["*"]
    )  # Get all items to filter and fetch metadata
    record = frappe.get_doc(doc.voucher_type, doc.voucher_no)
    series_no = extract_document_series_number(record)
    payload = {
        "sarNo": series_no,
        "orgSarNo": series_no,
        "regTyCd": "M",
        "custTin": None,
        "custNm": None,
        "custBhfId": None,
        "ocrnDt": record.posting_date.strftime("%Y%m%d"),
        "totTaxblAmt": 0,
        "totItemCnt": len(record.items),
        "totTaxAmt": 0,
        "totAmt": 0,
        "remark": None,
        "regrId": record.owner,
        "regrNm": record.owner,
        "modrNm": record.modified_by,
        "modrId": record.modified_by,
    }

    if doc.voucher_type == "Stock Reconciliation":
        items_list = get_stock_recon_movement_items_details(
            record.items, all_items
        )  # Get details abt item using the function
        current_item = list(
            filter(lambda item: item["itemNm"] == doc.item_code, items_list)
        )  # filter only the item referenced in this stock ledger entry
        qty_diff = int(
            current_item[0].pop("quantity_difference")
        )  # retrieve the quantity difference from the items dict. Only applies to stock recons
        payload["itemList"] = current_item
        payload["totItemCnt"] = len(current_item)

        if record.purpose == "Opening Stock":
            # Stock Recons of type "opening stock" are never negative, so just short-curcuit
            payload["sarTyCd"] = "06"

        else:
            # Stock recons of other types apart from "opening stock"
            if qty_diff < 0:
                # If the quantity difference is negative, apply etims stock in/out code 16
                payload["sarTyCd"] = "16"

            else:
                # If the quantity difference is positive, apply etims stock in/out code 06
                payload["sarTyCd"] = "06"

    if doc.voucher_type == "Stock Entry":
        items_list = get_stock_entry_movement_items_details(record.items, all_items)
        current_item = list(
            filter(lambda item: item["itemNm"] == doc.item_code, items_list)
        )

        payload["itemList"] = current_item
        payload["totItemCnt"] = len(current_item)

        if record.stock_entry_type == "Material Receipt":
            payload["sarTyCd"] = "04"

        # if record.stock_entry_type == "Material Transfer":
        #     payload["sarTyCd"] = "04"

        if record.stock_entry_type == "Manufacture":
            if doc.actual_qty > 0:
                payload["sarTyCd"] = "05"

            else:
                payload["sarTyCd"] = "14"

        if record.stock_entry_type in ("Send to Subcontractor", "Material Issue"):
            payload["sarTyCd"] = "13"

        if record.stock_entry_type == "Repack":
            if doc.actual_qty < 0:
                # Negative repack
                payload["sarTyCd"] = "14"

            else:
                payload["sarTyCd"] = "05"

    if doc.voucher_type in ("Purchase Receipt", "Purchase Invoice"):
        # TODO: This is very bad looking. Clean it up
        items_list = get_purchase_docs_items_details(record.items, all_items)
        item_taxes = get_itemised_tax_breakup_data(record)

        current_item = list(
            filter(lambda item: item["itemNm"] == doc.item_code, items_list)
        )
        tax_details = list(filter(lambda i: i["item"] == doc.item_code, item_taxes))[0]

        current_item[0]["taxblAmt"] = round(
            tax_details["taxable_amount"] / current_item[0]["qty"], 2
        )
        current_item[0]["totAmt"] = round(
            tax_details["taxable_amount"] / current_item[0]["qty"], 2
        )
        current_item[0]["taxAmt"] = round(
            tax_details["VAT"]["tax_amount"] / current_item[0]["qty"], 2
        )

        payload["itemList"] = current_item
        payload["totItemCnt"] = len(current_item)

        # TODO: use qty change field from SLE
        if record.is_return:
            payload["sarTyCd"] = "12"

        else:
            payload["sarTyCd"] = "02"

    if doc.voucher_type in ("Delivery Note", "Sales Invoice"):
        items_list = get_notes_docs_items_details(record.items, all_items)
        item_taxes = get_itemised_tax_breakup_data(record)

        current_item = list(
            filter(lambda item: item["itemNm"] == doc.item_code, items_list)
        )  # Get current item only
        tax_details = list(filter(lambda i: i["item"] == doc.item_code, item_taxes))[
            0
        ]  # filter current items tax details

        current_item[0]["taxblAmt"] = (
            tax_details["taxable_amount"] / current_item[0]["qty"]
        )  # calculate taxable amt
        current_item[0]["totAmt"] = (
            tax_details["taxable_amount"] / current_item[0]["qty"]
        )  # calculate total amt
        current_item[0]["taxAmt"] = (
            tax_details["VAT"]["tax_amount"] / current_item[0]["qty"]
        )  # calculate tax amt

        payload["itemList"] = current_item
        payload["totItemCnt"] = len(current_item)

        # TODO: opposite of previous, and use qty change field
        # TODO: These map to sales returns
        if record.is_return:
            # if is_return is checked, it turns to different type of docs
            if doc.actual_qty > 0:
                payload["sarTyCd"] = "03"

            else:
                payload["sarTyCd"] = "11"

    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("StockIOSaveReq")
    url = f"{server_url}{route_path}"
    headers = build_headers(company_name)

    integration_request = create_request_log(
        data=payload,
        name=doc.name,
        request_headers=headers,
        is_remote_request=True,
        url=url,
        service_name="eTims",
        reference_docname=doc.name,
        reference_doctype="Stock Ledger Entry",
    )

    frappe.enqueue(
        send_stock_movement_request,
        queue="default",
        is_async=True,
        timeout=300,
        job_name=f"{record.name}_send_stock_information",
        doc=doc,
        payload=payload,
        url=url,
        headers=headers,
        route_path=route_path,
    )


def send_stock_movement_request(doc, payload, url, headers, route_path):
    try:
        # TODO: Run job in background
        response = asyncio.run(make_post_request(url, payload, headers))

        if response:
            if response["resultCd"] == "000":
                data = response["data"]

                etims_logger.info("Stock Mvt. Response: %s" % data)
                update_last_request_date(response["resultDt"], route_path)

            else:
                # TODO: Fix issue with commiting in log_api_responses causing submission of this doc
                # log_api_responses(response, url, payload, "Failed")
                handle_errors(response, route_path, doc.name, doc)

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


def get_stock_entry_movement_items_details(
    records: list[Document], all_items: list[Document]
) -> list[dict]:
    items_list = []

    for item in records:
        for fetched_item in all_items:
            if item.item_code == fetched_item.name:
                items_list.append(
                    {
                        "itemSeq": item.idx,
                        "itemCd": None,
                        "itemClsCd": fetched_item.custom_item_classification,
                        "itemNm": fetched_item.item_code,
                        "bcd": None,
                        "pkgUnitCd": fetched_item.custom_packaging_unit_code,
                        "pkg": 1,
                        "qtyUnitCd": fetched_item.custom_unit_of_quantity_code,
                        "qty": abs(item.qty),
                        "itemExprDt": "",
                        "prc": (item.basic_rate if item.basic_rate else 0),
                        "splyAmt": (item.basic_rate if item.basic_rate else 0),
                        # TODO: Handle discounts properly
                        "totDcAmt": 0,
                        "taxTyCd": "B" or fetched_item.custom_taxation_type_code,
                        "taxblAmt": 0,
                        "taxAmt": 0,
                        "totAmt": 0,
                    }
                )

    return items_list


def get_stock_recon_movement_items_details(
    records: list, all_items: list
) -> list[dict]:
    items_list = []
    # current_qty

    for item in records:
        for fetched_item in all_items:
            if item.item_code == fetched_item.name:
                items_list.append(
                    {
                        "itemSeq": item.idx,
                        "itemCd": None,
                        "itemClsCd": fetched_item.custom_item_classification,
                        "itemNm": fetched_item.item_code,
                        "bcd": None,
                        "pkgUnitCd": fetched_item.custom_packaging_unit_code,
                        "pkg": 1,
                        "qtyUnitCd": fetched_item.custom_unit_of_quantity_code,
                        "qty": abs(int(item.quantity_difference)),
                        "itemExprDt": "",
                        "prc": (item.valuation_rate if item.valuation_rate else 0),
                        "splyAmt": (item.valuation_rate if item.valuation_rate else 0),
                        "totDcAmt": 0,
                        "taxTyCd": "B" or fetched_item.custom_taxation_type_code,
                        "taxblAmt": 0,
                        "taxAmt": 0,
                        "totAmt": 0,
                        "quantity_difference": item.quantity_difference,
                    }
                )

    return items_list


def get_purchase_docs_items_details(
    items: list, all_present_items: list[Document]
) -> list[dict]:
    items_list = []

    for item in items:
        for fetched_item in all_present_items:
            if item.item_code == fetched_item.name:
                items_list.append(
                    {
                        "itemSeq": item.idx,
                        "itemCd": None,
                        "itemClsCd": fetched_item.custom_item_classification,
                        "itemNm": fetched_item.item_code,
                        "bcd": None,
                        "pkgUnitCd": fetched_item.custom_packaging_unit_code,
                        "pkg": 1,
                        "qtyUnitCd": fetched_item.custom_unit_of_quantity_code,
                        "qty": abs(item.qty),
                        "itemExprDt": "",
                        "prc": (item.valuation_rate if item.valuation_rate else 0),
                        "splyAmt": (item.valuation_rate if item.valuation_rate else 0),
                        "totDcAmt": 0,
                        "taxTyCd": "B" or fetched_item.custom_taxation_type_code,
                        "taxblAmt": 0,
                        "taxAmt": 0,
                        "totAmt": 0,
                    }
                )

    return items_list


def get_notes_docs_items_details(
    items: list[Document], all_present_items: list[Document]
) -> list[dict]:
    items_list = []

    for item in items:
        for fetched_item in all_present_items:
            if item.item_code == fetched_item.name:
                items_list.append(
                    {
                        "itemSeq": item.idx,
                        "itemCd": None,
                        "itemClsCd": fetched_item.custom_item_classification,
                        "itemNm": fetched_item.item_code,
                        "bcd": None,
                        "pkgUnitCd": fetched_item.custom_packaging_unit_code,
                        "pkg": 1,
                        "qtyUnitCd": fetched_item.custom_unit_of_quantity_code,
                        "qty": abs(item.qty),
                        "itemExprDt": "",
                        "prc": (item.base_net_rate if item.base_net_rate else 0),
                        "splyAmt": (item.base_net_rate if item.base_net_rate else 0),
                        "totDcAmt": 0,
                        "taxTyCd": "B" or fetched_item.custom_taxation_type_code,
                        "taxblAmt": 0,
                        "taxAmt": 0,
                        "totAmt": 0,
                    }
                )

    return items_list
