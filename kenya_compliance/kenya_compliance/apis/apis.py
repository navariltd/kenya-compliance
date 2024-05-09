import asyncio
import json
from functools import partial

import aiohttp
import frappe
import frappe.defaults
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password

from ..doctype.doctype_names_mapping import (
    COUNTRIES_DOCTYPE_NAME,
    SETTINGS_DOCTYPE_NAME,
    USER_DOCTYPE_NAME,
)
from ..utils import (
    build_datetime_from_string,
    build_headers,
    get_route_path,
    get_server_url,
    make_get_request,
)
from .api_builder import EndpointsBuilder
from .remote_response_status_handlers import (
    customer_branch_details_submission_on_success,
    customer_insurance_details_submission_on_success,
    customer_search_on_success,
    imported_item_submission_on_success,
    imported_items_search_on_success,
    inventory_submission_on_success,
    item_composition_submission_on_success,
    item_registration_on_success,
    notices_search_on_success,
    on_error,
    purchase_search_on_success,
    search_branch_request_on_success,
    stock_mvt_search_on_success,
    user_details_submission_on_success,
)

endpoints_builder = EndpointsBuilder()


@frappe.whitelist()
def bulk_submit_sales_invoices(docs_list: str) -> None:
    from ..overrides.server.sales_invoice import on_submit

    data = json.loads(docs_list)
    all_sales_invoices = frappe.db.get_all("Sales Invoice", ["*"])

    for record in data:
        for invoice in all_sales_invoices:
            if record == invoice.name:
                doc = frappe.get_doc("Sales Invoice", record, for_update=False)
                on_submit(doc, method=None)


@frappe.whitelist()
def bulk_pos_sales_invoices(docs_list: str) -> None:
    from ..overrides.server.pos_invoice import on_submit

    data = json.loads(docs_list)
    all_pos_invoices = frappe.db.get_all("POS Invoice", ["*"])

    for record in data:
        for invoice in all_pos_invoices:
            if record == invoice.name:
                doc = frappe.get_doc("POS Invoice", record, for_update=False)
                on_submit(doc, method=None)


@frappe.whitelist(allow_guest=True)
def perform_customer_search(request_data: str) -> None:
    """Search customer details in the eTims Server

    Args:
        request_data (str): Data received from the client
    """
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("CustSearchReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"
        payload = {"custmTin": data["tax_id"]}

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = partial(
            customer_search_on_success, document_name=data["name"]
        )
        endpoints_builder.error_callback = on_error

        frappe.enqueue(
            endpoints_builder.make_remote_call,
            is_async=True,
            queue="default",
            timeout=300,
            doctype="Customer",
            document_name=data["name"],
            job_name=f"{data['name']}_customer_search",
        )


@frappe.whitelist()
def perform_item_registration(request_data: str) -> dict | None:
    data: dict = json.loads(request_data)

    company_name = data.pop("company_name")

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("ItemSaveReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = data
        endpoints_builder.success_callback = partial(
            item_registration_on_success, document_name=data["name"]
        )
        endpoints_builder.error_callback = on_error

        frappe.enqueue(
            endpoints_builder.make_remote_call,
            is_async=True,
            queue="default",
            timeout=300,
            doctype="Item",
            document_name=data["name"],
            job_name=f"{data['name']}_register_item",
        )


@frappe.whitelist()
def send_insurance_details(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("BhfInsuranceSaveReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"
        payload = {
            "isrccCd": data["insurance_code"],
            "isrccNm": data["insurance_name"],
            "isrcRt": data["premium_rate"],
            "useYn": "Y",
            "regrNm": data["registration_id"],
            "regrId": data["registration_id"],
            "modrNm": data["modifier_id"],
            "modrId": data["modifier_id"],
        }

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = partial(
            customer_insurance_details_submission_on_success, document_name=data["name"]
        )
        endpoints_builder.error_callback = on_error

        frappe.enqueue(
            endpoints_builder.make_remote_call,
            is_async=True,
            queue="default",
            timeout=300,
            doctype="Customer",
            document_name=data["name"],
            job_name=f"{data['name']}_submit_insurance_information",
        )


@frappe.whitelist()
def send_branch_customer_details(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("BhfCustSaveReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"
        payload = {
            "custNo": data["name"][:14],
            "custTin": data["customer_pin"],
            "custNm": data["customer_name"],
            "adrs": None,
            "telNo": None,
            "email": None,
            "faxNo": None,
            "useYn": "Y",
            "remark": None,
            "regrNm": data["registration_id"],
            "regrId": data["registration_id"],
            "modrNm": data["modifier_id"],
            "modrId": data["modifier_id"],
        }

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = partial(
            customer_branch_details_submission_on_success, document_name=data["name"]
        )
        endpoints_builder.error_callback = on_error

        frappe.enqueue(
            endpoints_builder.make_remote_call,
            is_async=True,
            queue="default",
            timeout=300,
            doctype="Customer",
            document_name=data["name"],
            job_name=f"{data['name']}_submit_customer_branch_details",
        )


@frappe.whitelist()
def save_branch_user_details(request_data: str) -> None:
    data: dict = json.loads(request_data)
    company_name = data["company_name"]
    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("BhfUserSaveReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"

        payload = {
            "userId": data["user_id"],
            "userNm": data["full_names"],
            "pwd": "password",  # TODO: Find a fix for this
            "adrs": None,
            "cntc": None,
            "authCd": None,
            "remark": None,
            "useYn": "Y",
            "regrNm": data["registration_id"],
            "regrId": data["registration_id"],
            "modrNm": data["modifier_id"],
            "modrId": data["modifier_id"],
        }

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = partial(
            user_details_submission_on_success, document_name=data["name"]
        )
        endpoints_builder.error_callback = on_error

        frappe.enqueue(
            endpoints_builder.make_remote_call,
            is_async=True,
            queue="default",
            timeout=300,
            job_name=f"{data['name']}_send_branch_user_information",
            doctype=USER_DOCTYPE_NAME,
            document_name=data["name"],
        )


@frappe.whitelist()
def perform_item_search(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]
    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("ItemSearchReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"

        request_date = last_request_date.strftime("%Y%m%d%H%M%S")
        payload = {"lastReqDt": request_date}

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = lambda response: frappe.msgprint(
            f"{response}"
        )
        endpoints_builder.error_callback = on_error

        endpoints_builder.make_remote_call(doctype="Item")


@frappe.whitelist()
def perform_import_item_search(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]
    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("ImportItemSearchReq")

    if headers and server_url and route_path:
        request_date = last_request_date.strftime("%Y%m%d%H%M%S")
        url = f"{server_url}{route_path}"
        payload = {"lastReqDt": request_date}

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = imported_items_search_on_success
        endpoints_builder.error_callback = on_error

        endpoints_builder.make_remote_call(
            doctype="Item",
        )


@frappe.whitelist()
def perform_purchases_search(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("TrnsPurchaseSalesReq")

    if headers and server_url and route_path:
        request_date = last_request_date.strftime("%Y%m%d%H%M%S")

        url = f"{server_url}{route_path}"
        payload = {"lastReqDt": request_date}

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = purchase_search_on_success
        endpoints_builder.error_callback = on_error

        endpoints_builder.make_remote_call(
            doctype="Purchase Invoice",
        )


@frappe.whitelist()
def submit_inventory(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("StockMasterSaveReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"

        query = f"""
            SELECT item_code,
                SUM(actual_qty) AS item_count
            FROM tabBin
            WHERE item_code = '{data["name"]}'
            GROUP BY item_code
            ORDER BY item_code DESC;
            """
        results = frappe.db.sql(query, as_dict=True)

        if results:
            payload = {
                "itemCd": data["itemCd"],
                "rsdQty": results[0].item_count,
                "regrId": data["registered_by"],
                "regrNm": data["registered_by"],
                "modrNm": data["registered_by"],
                "modrId": data["registered_by"],
            }

            endpoints_builder.headers = headers
            endpoints_builder.url = url
            endpoints_builder.payload = payload
            endpoints_builder.success_callback = lambda response: frappe.errprint(
                f"{response}"
            )
            endpoints_builder.error_callback = on_error

            frappe.enqueue(
                endpoints_builder.make_remote_call,
                is_async=True,
                queue="default",
                timeout=300,
                job_name=f"{data['name']}_submit_inventory",
                doctype="Item",
                document_name=data["name"],
            )


@frappe.whitelist()
def perform_item_classification_search(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("ItemClsSearchReq")

    if headers and server_url and route_path:
        request_date = last_request_date.strftime("%Y%m%d%H%M%S")

        url = f"{server_url}{route_path}"
        payload = {"lastReqDt": request_date}

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = lambda response: frappe.msgprint(
            f"{response}"
        )
        endpoints_builder.error_callback = on_error

        endpoints_builder.make_remote_call(
            doctype="Item",
        )


@frappe.whitelist()
def search_branch_request(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("BhfSearchReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"

        request_date = last_request_date.strftime("%Y%m%d%H%M%S")

        payload = {"lastReqDt": "20240101000000"}

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = search_branch_request_on_success
        endpoints_builder.error_callback = on_error

        endpoints_builder.make_remote_call(
            doctype="Customer",
        )


@frappe.whitelist()
def send_imported_item_request(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]
    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("ImportItemUpdateReq")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"
        declaration_date = build_datetime_from_string(
            data["declaration_date"], "%Y-%m-%d %H:%M:%S.%f"
        ).strftime("%Y%m%d")

        payload = {
            "taskCd": data["task_code"],
            "dclDe": declaration_date,
            "itemSeq": data["item_sequence"],
            "hsCd": data["hs_code"],
            "itemClsCd": data["item_classification_code"],
            "itemCd": data["item_code"],
            "imptItemSttsCd": data["import_item_status"],
            "remark": None,
            "modrNm": data["modified_by"],
            "modrId": data["modified_by"],
        }

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = partial(
            imported_item_submission_on_success, document_name=data["name"]
        )
        endpoints_builder.error_callback = on_error

        frappe.enqueue(
            endpoints_builder.make_remote_call,
            is_async=True,
            queue="default",
            timeout=300,
            job_name=f"{data['name']}_submit_imported_item",
            doctype="Item",
            document_name=data["name"],
        )


@frappe.whitelist()
def perform_notice_search(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)

    route_path, last_request_date = get_route_path("NoticeSearchReq")
    request_date = last_request_date.strftime("%Y%m%d%H%M%S")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"
        payload = {"lastReqDt": request_date}

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = notices_search_on_success
        endpoints_builder.error_callback = on_error

        endpoints_builder.make_remote_call(
            doctype=SETTINGS_DOCTYPE_NAME, document_name=data.get("name", None)
        )


@frappe.whitelist()
def perform_stock_movement_search(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)

    route_path, last_request_date = get_route_path("StockMoveReq")
    request_date = last_request_date.strftime("%Y%m%d%H%M%S")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"
        payload = {"lastReqDt": request_date}

        endpoints_builder.headers = headers
        endpoints_builder.url = url
        endpoints_builder.payload = payload
        endpoints_builder.success_callback = stock_mvt_search_on_success
        endpoints_builder.error_callback = on_error

        endpoints_builder.make_remote_call(
            doctype=SETTINGS_DOCTYPE_NAME, document_name=data.get("name", None)
        )


@frappe.whitelist()
def submit_item_composition(request_data: str) -> None:
    data: dict = json.loads(request_data)

    company_name = data["company_name"]

    headers = build_headers(company_name)
    server_url = get_server_url(company_name)
    route_path, last_request_date = get_route_path("SaveItemComposition")

    if headers and server_url and route_path:
        url = f"{server_url}{route_path}"

        all_items = frappe.db.get_all("Item", ["*"])

        # Check if item to manufacture is registered before proceeding
        manufactured_item = frappe.get_value(
            "Item",
            {"name": data["item_name"]},
            ["custom_item_registered", "name"],
            as_dict=True,
        )

        if not manufactured_item.custom_item_registered:
            frappe.throw(
                f"Please register item: <b>{manufactured_item.name}</b> first to proceed.",
                title="Integration Error",
            )

        for item in data["items"]:
            for fetched_item in all_items:
                if item["item_code"] == fetched_item.item_code:
                    if fetched_item.custom_item_registered == 1:
                        payload = {
                            "itemCd": data["item_code"],
                            "cpstItemCd": fetched_item.custom_item_code_etims,
                            "cpstQty": item["qty"],
                            "regrId": data["registration_id"],
                            "regrNm": data["registration_id"],
                        }

                        endpoints_builder.headers = headers
                        endpoints_builder.url = url
                        endpoints_builder.payload = payload
                        endpoints_builder.success_callback = partial(
                            item_composition_submission_on_success,
                            document_name=data["name"],
                        )
                        endpoints_builder.error_callback = on_error

                        frappe.enqueue(
                            endpoints_builder.make_remote_call,
                            is_async=True,
                            queue="default",
                            timeout=300,
                            job_name=f"{data['name']}_submit_item_composition",
                            doctype="BOM",
                            document_name=data["name"],
                        )

                    else:
                        frappe.throw(
                            f"""
                            Item: <b>{fetched_item.name}</b> is not registered. 
                            <b>Ensure ALL Items are registered first to submit this composition</b>""",
                            title="Integration Error",
                        )


@frappe.whitelist()
def create_supplier_from_fetched_registered_purchases(request_data: str) -> None:
    data: dict = json.loads(request_data)

    new_supplier = create_supplier(data["supplier_name"], data["supplier_pin"])

    frappe.msgprint(f"Supplier: {new_supplier.name} created")


def create_supplier(supplier_name: str, supplier_pin: str) -> Document:
    new_supplier = frappe.new_doc("Supplier")

    new_supplier.supplier_name = supplier_name
    new_supplier.tax_id = supplier_pin

    new_supplier.save()

    return new_supplier


@frappe.whitelist()
def create_items_from_fetched_registered_purchases(request_data: str) -> None:
    data = json.loads(request_data)

    if data["items"]:
        items = data["items"]
        for item in items:
            create_item(item)


def create_item(item: dict | frappe._dict) -> Document:
    new_item = frappe.new_doc("Item")
    new_item.item_code = item["item_name"]
    new_item.item_group = "All Item Groups"
    new_item.custom_item_classification = item["item_classification_code"]
    new_item.custom_packaging_unit = item["packaging_unit_code"]
    new_item.custom_unit_of_quantity = item["quantity_unit_code"]
    new_item.custom_taxation_type = item["taxation_type_code"]
    new_item.custom_etims_country_of_origin = frappe.get_doc(
        COUNTRIES_DOCTYPE_NAME,
        {"code": item["item_code"][:2]},
        for_update=False,
    ).name
    new_item.custom_product_type = item["item_code"][2:3]
    new_item.custom_item_code_etims = item["item_code"]

    try:
        new_item.save()

    except frappe.exceptions.DuplicateEntryError:
        pass

    return new_item


@frappe.whitelist()
def create_purchase_invoice_from_registered_purchase(request_data: str) -> None:
    data = json.loads(request_data)

    # Check if supplier exists
    supplier = None
    if not frappe.db.exists("Supplier", data["supplier_name"], cache=False):
        supplier = create_supplier(data["supplier_name"], data["supplier_pin"]).name

    all_items = []
    # Check if item exists
    for received_item in data["items"]:
        if not frappe.db.exists("Item", received_item["item_name"], cache=False):
            created_item = create_item(received_item)
            all_items.append(created_item)

    # Create the Purchase Invoice
    purchase_invoice = frappe.new_doc("Purchase Invoice")
    purchase_invoice.supplier = supplier or data["supplier_name"]

    purchase_invoice.set("items", [])

    for item in data["items"]:
        purchase_invoice.append(
            "items",
            {
                "item_name": item["name"],
                "qty": item["quantity"],
                "rate": item["unit_price"],
                "expense_account": "Cost of Goods Sold - PLM",
                "custom_item_classification": item["item_classification_code"],
                "custom_packaging_unit": item["packaging_unit_code"],
                "custom_unit_of_quantity": item["quantity_unit_code"],
            },
        )

    purchase_invoice.save()


@frappe.whitelist()
def ping_server(request_data: str) -> None:
    url = json.loads(request_data)["server_url"]

    try:
        response = asyncio.run(make_get_request(url))

        if len(response) == 13:
            frappe.msgprint("The Server is Online")
            return

        frappe.msgprint("The Server is Offline")
        return

    except aiohttp.client_exceptions.ClientConnectorError:
        frappe.msgprint("The Server is Offline")
        return
