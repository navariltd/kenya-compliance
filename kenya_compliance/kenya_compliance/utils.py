"""Utility functions"""

import json
import re
from datetime import datetime
from typing import Any, Callable, Literal

import aiohttp
import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from frappe.model.document import Document

from .doctype.doctype_names_mapping import (
    ENVIRONMENT_SPECIFICATION_DOCTYPE_NAME,
    INTEGRATION_LOGS_DOCTYPE_NAME,
    ROUTES_TABLE_CHILD_DOCTYPE_NAME,
    ROUTES_TABLE_DOCTYPE_NAME,
    SETTINGS_DOCTYPE_NAME,
)
from .logger import etims_logger


def is_valid_kra_pin(pin: str) -> bool:
    """Checks if the string provided conforms to the pattern of a KRA PIN.
    This function does not validate if the PIN actually exists, only that
    it resembles a valid KRA PIN.

    Args:
        pin (str): The KRA PIN to test

    Returns:
        bool: True if input is a valid KRA PIN, False otherwise
    """
    pattern = r"^[a-zA-Z]{1}[0-9]{9}[a-zA-Z]{1}$"
    return bool(re.match(pattern, pin))


async def make_get_request(url: str) -> dict[str, str]:
    """Make an Asynchronous GET Request to specified URL

    Args:
        url (str): The URL

    Returns:
        dict: The Response
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def make_post_request(
    url: str,
    data: dict[str, str] | None = None,
    headers: dict[str, str | int] | None = None,
) -> dict[str, str | dict]:
    """Make an Asynchronous POST Request to specified URL

    Args:
        url (str): The URL
        data (dict[str, str] | None, optional): Data to send to server. Defaults to None.
        headers (dict[str, str | int] | None, optional): Headers to set. Defaults to None.

    Returns:
        dict: The Server Response
    """
    # TODO: Refactor to a more efficient handling of creation of the session object
    # as described in documentation
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            return await response.json()


def log_api_responses(
    response: dict,
    url: str,
    payload: dict,
    status: Literal["Success", "Failed"],
    integration_log_doctype: str = INTEGRATION_LOGS_DOCTYPE_NAME,
) -> bool:
    log = frappe.new_doc(integration_log_doctype)
    log.request_url = url
    log.status = status
    log.error_code = response["resultCd"]
    log.log_time = datetime.now()
    log.error_log = response["resultMsg"]
    log.payload = json.dumps(payload)

    log.save()

    # frappe.db.commit()


def build_datetime_from_string(
    date_string: str, format: str = "%Y-%m-%d %H:%M:%S"
) -> datetime:
    """Builds a Datetime object from string, and format provided

    Args:
        date_string (str): The string to build object from
        format (str, optional): The format of the date_string string. Defaults to "%Y-%m-%d".

    Returns:
        datetime: The datetime object
    """
    date_object = datetime.strptime(date_string, format)

    return date_object


def format_last_request_date(last_request_date: datetime) -> str:
    """Returns the last request date formatted into a 14-character long string

    Args:
        last_request_date (datetime): The datetime object to format

    Returns:
        str: The formatted date string
    """
    formatted_date = last_request_date.strftime("%Y%m%d%H%M%S")

    return formatted_date


def is_valid_url(url: str) -> bool:
    """Validates input is a valid URL

    Args:
        input (str): The input to validate

    Returns:
        bool: Validation result
    """
    pattern = r"^(https?|ftp):\/\/[^\s/$.?#].[^\s]*"
    return bool(re.match(pattern, url))


def get_route_path(
    search_field: str,
    routes_table_doctype: str = ROUTES_TABLE_CHILD_DOCTYPE_NAME,
) -> tuple[str, str] | None:

    query = f"""
    SELECT 
        url_path, 
        last_request_date
    FROM `tab{routes_table_doctype}`
    WHERE url_path_function LIKE '{search_field}'
    AND parent LIKE '{ROUTES_TABLE_DOCTYPE_NAME}'
    LIMIT 1
    """

    results = frappe.db.sql(query, as_dict=True)

    if results:
        return (results[0].url_path, results[0].last_request_date)


def get_environment_settings(
    company_name: str,
    doctype: str = SETTINGS_DOCTYPE_NAME,
    environment: str = "Sandbox",
) -> Document | None:
    error_message = None
    query = f"""
    SELECT server_url,
        tin,
        dvcsrlno,
        bhfid,
        company,
        communication_key,
        name
    FROM `tab{doctype}`
    WHERE company = '{company_name}'
        AND env = '{environment}'
        AND name IN (
            SELECT name
            FROM `tab{doctype}`
            WHERE is_active = 1
        );
    """
    setting_doctype = frappe.db.sql(query, as_dict=True)

    if setting_doctype:
        return setting_doctype[0]

    error_message = "No environment setting created. Please ensure a valid eTims Integration Setting record exists"
    etims_logger.error(error_message)
    frappe.throw(error_message, title="Incorrect Setup")


def get_current_environment_state(
    environment_identifier_doctype: str = ENVIRONMENT_SPECIFICATION_DOCTYPE_NAME,
) -> str:
    """Fetches the Environment Identifier from the relevant doctype.

    Args:
        environment_identifier_doctype (str, optional): The doctype containing environment information. Defaults to ENVIRONMENT_SPECIFICATION_DOCTYPE_NAME.

    Returns:
        str: The environment identifier. Either "Sandbox", or "Production"
    """
    environment = frappe.db.get_single_value(
        environment_identifier_doctype, "environment"
    )

    return environment


def get_server_url(company_name: str) -> str | None:
    current_environment = get_current_environment_state(
        ENVIRONMENT_SPECIFICATION_DOCTYPE_NAME
    )
    settings = get_environment_settings(company_name, environment=current_environment)

    if settings:
        server_url = settings.get("server_url")

        return server_url

    return


def build_headers(company_name: str) -> dict[str, str] | None:
    current_environment = get_current_environment_state(
        ENVIRONMENT_SPECIFICATION_DOCTYPE_NAME
    )
    settings = get_environment_settings(company_name, environment=current_environment)

    if settings:
        headers = {
            "tin": settings.get("tin"),
            "bhfId": settings.get("bhfid"),
            "cmcKey": settings.get("communication_key"),
        }

        return headers


def extract_document_series_number(document: Document) -> int | None:
    split_invoice_name = document.name.split("-")

    if len(split_invoice_name) == 4:
        return int(split_invoice_name[-1])

    if len(split_invoice_name) == 5:
        return int(split_invoice_name[-2])


def build_invoice_payload(
    invoice: Document, invoice_type_identifier: Literal["S", "C"]
) -> dict[str, str | int]:
    """Converts relevant invoice data to a JSON payload

    Args:
        invoice (Document): The Invoice record to generate data from
        invoice_type_identifier (Literal[&quot;S&quot;, &quot;C&quot;]): The
        Invoice type identifer. S for Sales Invoice, C for Credit Notes

    Returns:
        dict[str, str | int]: The payload
    """

    # TODO: Check why posting time is always invoice submit time
    posting_date = build_datetime_from_string(
        f"{invoice.posting_date} {invoice.posting_time[:8].replace('.', '')}",
        format="%Y-%m-%d %H:%M:%S",
    )

    validated_date = posting_date.strftime("%Y%m%d%H%M%S")
    sales_date = posting_date.strftime("%Y%m%d")

    items_list = get_invoice_items_list(invoice)

    payload = {
        "invcNo": extract_document_series_number(invoice),
        "orgInvcNo": (
            0
            if invoice_type_identifier == "S"
            else extract_document_series_number(invoice)
        ),
        "trdInvcNo": invoice.name,
        "custTin": invoice.tax_id if invoice.tax_id else None,
        "custNm": None,
        "rcptTyCd": invoice_type_identifier if invoice_type_identifier == "S" else "R",
        "pmtTyCd": invoice.custom_payment_type_code,
        "salesSttsCd": invoice.custom_transaction_progress_code,
        "cfmDt": validated_date,
        "salesDt": sales_date,
        "stockRlsDt": validated_date,
        "cnclReqDt": None,
        "cnclDt": None,
        "rfdDt": None,
        "rfdRsnCd": None,
        "totItemCnt": len(items_list),
        "taxblAmtA": 0,
        "taxblAmtB": abs(invoice.base_net_total),
        "taxblAmtC": 0,
        "taxblAmtD": 0,
        "taxblAmtE": 0,
        "taxRtA": 0,
        "taxRtB": round((invoice.total_taxes_and_charges / invoice.net_total) * 100, 2),
        "taxRtC": 0,
        "taxRtD": 0,
        "taxRtE": 0,
        "taxAmtA": 0,
        "taxAmtB": abs(invoice.total_taxes_and_charges),
        "taxAmtC": 0,
        "taxAmtD": 0,
        "taxAmtE": 0,
        "totTaxblAmt": abs(invoice.base_net_total),
        "totTaxAmt": abs(invoice.total_taxes_and_charges),
        "totAmt": abs(invoice.base_net_total),
        "prchrAcptcYn": "N",
        "remark": None,
        "regrId": invoice.owner,
        "regrNm": invoice.owner,
        "modrId": invoice.modified_by,
        "modrNm": invoice.modified_by,
        "receipt": {
            "custTin": invoice.tax_id if invoice.tax_id else None,
            "custMblNo": None,
            "rptNo": 1,
            "rcptPbctDt": validated_date,
            "trdeNm": "",
            "adrs": "",
            "topMsg": "ERPNext",
            "btmMsg": "Welcome",
            "prchrAcptcYn": "N",
        },
        "itemList": items_list,
    }

    return payload


def get_invoice_items_list(invoice: Document) -> list[dict[str, str | int | None]]:
    """Iterates over the invoice items and extracts relevant data

    Args:
        invoice (Document): The invoice

    Returns:
        list[dict[str, str | int | None]]: The parsed data as a list of dictionaries
    """
    item_taxes = get_itemised_tax_breakup_data(invoice)
    items_list = []

    for index, item in enumerate(invoice.items):
        taxable_amount = int(item_taxes[index]["taxable_amount"]) / item.qty
        tax_amount = item_taxes[index]["VAT"]["tax_amount"] / item.qty

        items_list.append(
            {
                "itemSeq": item.idx,
                "itemCd": None,
                "itemClsCd": item.custom_item_classification,
                "itemNm": item.item_name,
                "bcd": None,
                "pkgUnitCd": item.custom_packaging_unit_code,
                "pkg": 1,
                "qtyUnitCd": item.custom_unit_of_quantity_code,
                "qty": abs(item.qty),
                "prc": item.base_rate,
                "splyAmt": item.base_rate,
                # TODO: Handle discounts properly
                "dcRt": 0,
                "dcAmt": 0,
                "isrccCd": None,
                "isrccNm": None,
                "isrcRt": None,
                "isrcAmt": None,
                "taxTyCd": item.custom_taxation_type_code,
                "taxblAmt": taxable_amount,
                "taxAmt": tax_amount,
                "totAmt": taxable_amount,
            }
        )

    return items_list


def queue_request(
    function_to_queue: Callable[[str, dict[str, str]], dict[str, str]],
    url: str,
    payload: dict,
    headers: dict,
    success_callback: Callable[[Any, Any, Any], Any],
    failure_callback: Callable[[Any, Any, Any, Any, Any], Any],
    queue_type: Literal["default", "short", "long"],
) -> Any:
    """Queues a request function to the Redis Queue

    Args:
        function_to_queue (Callable[[str, dict[str, str]], dict[str, str]]): The function to queue
        url (str): The target request url
        payload (dict): The json request data
        headers (dict): The request headers
        success_callback (Callable[[Any, Any, Any], Any]): Callback to handle successful responses
        failure_callback (Callable[[Any, Any, Any, Any, Any], Any]): Callback to handle failure responses
        queue_type (Literal["default", "short", "long"]): Type of Queue to enqueue job to

    Returns:
        Any: The job id of current job
    """
    job = frappe.enqueue(
        function_to_queue,
        at_front=True,
        url=url,
        data=payload,
        headers=headers,
        is_async=True,
        queue=queue_type,
        on_success=success_callback,
        on_failure=failure_callback,
    )

    return job.id


def update_last_request_date(
    response_datetime: str,
    route: str,
    routes_table: str = ROUTES_TABLE_CHILD_DOCTYPE_NAME,
) -> None:
    doc = frappe.get_doc(
        routes_table,
        {"url_path": route},
        ["*"],
    )

    doc.last_request_date = build_datetime_from_string(
        response_datetime, "%Y%m%d%H%M%S"
    )

    doc.save()
    frappe.db.commit()
