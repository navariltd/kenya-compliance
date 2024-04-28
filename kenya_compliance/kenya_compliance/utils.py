"""Utility functions"""

import re
from datetime import datetime, timedelta
from typing import Literal

import aiohttp
import frappe
from erpnext.controllers.taxes_and_totals import get_itemised_tax_breakup_data
from frappe.model.document import Document

from .doctype.doctype_names_mapping import (
    ENVIRONMENT_SPECIFICATION_DOCTYPE_NAME,
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


async def make_get_request(url: str) -> dict[str, str] | str:
    """Make an Asynchronous GET Request to specified URL

    Args:
        url (str): The URL

    Returns:
        dict: The Response
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.content_type.startswith("text"):
                return await response.text()

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
        name,
        tin,
        dvcsrlno,
        bhfid,
        company,
        communication_key,
        most_recent_sales_number
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

    error_message = f"""
        No valid environment setting for env: {environment} exists. 
        Please ensure a valid eTims Integration Setting record exists
    """

    etims_logger.error(error_message)
    frappe.log_error(
        title="Incorrect Setup", message=error_message, reference_doctype=doctype
    )
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
    settings = get_curr_env_etims_settings(company_name)

    if settings:
        server_url = settings.get("server_url")

        return server_url

    return


def build_headers(company_name: str) -> dict[str, str] | None:
    settings = get_curr_env_etims_settings(company_name)

    if settings:
        headers = {
            "tin": settings.get("tin"),
            "bhfId": settings.get("bhfid"),
            "cmcKey": settings.get("communication_key"),
            "Content-Type": "application/json",
        }

        return headers


def extract_document_series_number(document: Document) -> int | None:
    split_invoice_name = document.name.split("-")

    if len(split_invoice_name) == 4:
        return int(split_invoice_name[-1])

    if len(split_invoice_name) == 5:
        return int(split_invoice_name[-2])


def build_invoice_payload(
    invoice: Document, invoice_type_identifier: Literal["S", "C"], company_name: str
) -> dict[str, str | int]:
    """Converts relevant invoice data to a JSON payload

    Args:
        invoice (Document): The Invoice record to generate data from
        invoice_type_identifier (Literal[&quot;S&quot;, &quot;C&quot;]): The
        Invoice type identifer. S for Sales Invoice, C for Credit Notes
        company_name (str): The company name used to fetch the valid settings doctype record

    Returns:
        dict[str, str | int]: The payload
    """
    post_time = invoice.posting_time

    if isinstance(post_time, timedelta):
        # handles instances when the posting_time is not a string
        # especially when doing bulk submissions
        post_time = str(post_time)

    # TODO: Check why posting time is always invoice submit time
    posting_date = build_datetime_from_string(
        f"{invoice.posting_date} {post_time[:8].replace('.', '')}",
        format="%Y-%m-%d %H:%M:%S",
    )

    validated_date = posting_date.strftime("%Y%m%d%H%M%S")
    sales_date = posting_date.strftime("%Y%m%d")

    items_list = get_invoice_items_list(invoice)

    most_recent_sales_number, invoice_number = (
        get_most_recent_sales_number(company_name),
        None,
    )

    if most_recent_sales_number >= 0:
        invoice_number = most_recent_sales_number + 1

    payload = {
        "invcNo": invoice_number,
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
        taxable_amount = round(int(item_taxes[index]["taxable_amount"]) / item.qty, 2)
        tax_amount = round(item_taxes[index]["VAT"]["tax_amount"] / item.qty, 2)

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


def get_curr_env_etims_settings(company_name: str) -> Document | None:
    current_environment = get_current_environment_state(
        ENVIRONMENT_SPECIFICATION_DOCTYPE_NAME
    )
    settings = get_environment_settings(company_name, environment=current_environment)

    if settings:
        return settings


def get_most_recent_sales_number(company_name: str) -> int | None:
    settings = get_curr_env_etims_settings(company_name)

    if settings:
        return settings.most_recent_sales_number

    return
