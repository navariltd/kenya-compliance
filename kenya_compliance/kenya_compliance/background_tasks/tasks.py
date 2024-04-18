from typing import Any

import frappe
import frappe.defaults
from frappe.model.document import Document

from ..apis.api_builder import EndpointsBuilder
from ..apis.remote_response_status_handlers import on_error
from ..doctype.doctype_names_mapping import (
    ITEM_CLASSIFICATIONS_DOCTYPE_NAME,
    PACKAGING_UNIT_DOCTYPE_NAME,
    TAXATION_TYPE_DOCTYPE_NAME,
    UNIT_OF_QUANTITY_DOCTYPE_NAME,
)
from ..utils import build_headers, get_route_path, get_server_url

endpoints_builder = EndpointsBuilder()


@frappe.whitelist(allow_guest=True)
def refresh_code_lists() -> str | None:
    company_name: str | Any = frappe.defaults.get_user_default("Company")

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)

    code_search_route_path, last_request_date = get_route_path(
        "CodeSearchReq"
    )  # endpoint for code search
    item_cls_route_path, last_request_date = get_route_path(
        "ItemClsSearchReq"
    )  # overwriting last_request_date since it's not used elsewhere for this task

    if headers and server_url and code_search_route_path and item_cls_route_path:
        url = f"{server_url}{code_search_route_path}"
        payload = {
            "lastReqDt": "20000101000000"
        }  # Hard-coded to a this date to get all code lists.

        endpoints_builder.url = url
        endpoints_builder.headers = headers
        endpoints_builder.payload = payload
        endpoints_builder.error_callback = on_error

        # Fetch and update codes obtained from CodeSearchReq endpoint
        endpoints_builder.success_callback = run_updater_functions
        endpoints_builder.make_remote_call(doctype=None, document_name=None)

        # Fetch and update item classification codes from ItemClsSearchReq endpoint
        endpoints_builder.url = f"{server_url}{item_cls_route_path}"
        endpoints_builder.success_callback = update_item_classification_codes
        endpoints_builder.make_remote_call(doctype=None, document_name=None)

        return "succeeded"


def run_updater_functions(response: dict) -> None:
    for class_list in response["data"]["clsList"]:
        if class_list["cdClsNm"] == "Quantity Unit":
            update_unit_of_quantity(class_list)

        if class_list["cdClsNm"] == "Taxation Type":
            update_taxation_type(class_list)

        if class_list["cdClsNm"] == "Packing Unit":
            update_packaging_units(class_list)


def update_unit_of_quantity(data: dict) -> None:
    doc: Document | None = None

    for unit_of_quantity in data["dtlList"]:
        try:
            doc = frappe.get_doc(UNIT_OF_QUANTITY_DOCTYPE_NAME, unit_of_quantity["cd"])

        except frappe.DoesNotExistError:
            doc = frappe.new_doc(UNIT_OF_QUANTITY_DOCTYPE_NAME)

        finally:
            doc.code = unit_of_quantity["cd"]
            doc.sort_order = unit_of_quantity["srtOrd"]
            doc.code_name = unit_of_quantity["cdNm"]
            doc.code_description = unit_of_quantity["cdDesc"]

            doc.save()

    frappe.db.commit()


def update_taxation_type(data: dict) -> None:
    doc: Document | None = None

    for taxation_type in data["dtlList"]:
        try:
            doc = frappe.get_doc(TAXATION_TYPE_DOCTYPE_NAME, taxation_type["cd"])

        except frappe.DoesNotExistError:
            doc = frappe.new_doc(TAXATION_TYPE_DOCTYPE_NAME)

        finally:
            doc.cd = taxation_type["cd"]
            doc.cdnm = taxation_type["cdNm"]
            doc.cddesc = taxation_type["cdDesc"]
            doc.useyn = 1 if taxation_type["useYn"] == "Y" else 0
            doc.srtord = taxation_type["srtOrd"]
            doc.userdfncd1 = taxation_type["userDfnCd1"]
            doc.userdfncd2 = taxation_type["userDfnCd2"]
            doc.userdfncd3 = taxation_type["userDfnCd3"]

            doc.save()

    frappe.db.commit()


def update_packaging_units(data: dict) -> None:
    doc: Document | None = None

    for packaging_unit in data["dtlList"]:
        try:
            doc = frappe.get_doc(PACKAGING_UNIT_DOCTYPE_NAME, packaging_unit["cd"])

        except frappe.DoesNotExistError:
            doc = frappe.new_doc(PACKAGING_UNIT_DOCTYPE_NAME)

        finally:
            doc.code = packaging_unit["cd"]
            doc.code_name = packaging_unit["cdNm"]
            doc.sort_order = packaging_unit["srtOrd"]
            doc.code_description = packaging_unit["cdDesc"]

            doc.save()

    frappe.db.commit()


def update_item_classification_codes(response: dict) -> None:
    doc: Document | None = None

    for item_classification in response["data"]["itemClsList"]:
        try:
            doc = frappe.get_doc(
                ITEM_CLASSIFICATIONS_DOCTYPE_NAME, item_classification["itemClsCd"]
            )

        except frappe.DoesNotExistError:
            doc = frappe.new_doc(ITEM_CLASSIFICATIONS_DOCTYPE_NAME)

        finally:
            doc.itemclscd = item_classification["itemClsCd"]
            doc.itemclslvl = item_classification["itemClsLvl"]
            doc.itemclsnm = item_classification["itemClsNm"]
            doc.taxtycd = item_classification["taxTyCd"]
            doc.useyn = 1 if item_classification["useYn"] == "Y" else 0
            doc.mjrtgyn = item_classification["mjrTgYn"]

            doc.save()

        frappe.db.commit()