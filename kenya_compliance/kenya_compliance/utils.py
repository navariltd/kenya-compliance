"""Utility functions"""

import re
from datetime import datetime
from typing import Any, Callable, Literal

import aiohttp
import frappe
from frappe.model.document import Document

from .doctype.doctype_names_mapping import (
    COMMUNICATION_KEYS_DOCTYPE_NAME,
    LAST_REQUEST_DATE_DOCTYPE_NAME,
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
) -> dict[str, str]:
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


def save_communication_key_to_doctype(
    communication_key: str,
    fetch_time: datetime,
    doctype: str = COMMUNICATION_KEYS_DOCTYPE_NAME,
) -> Document:
    """Saves the provided Communication to the specified doctype

    Args:
        communication_key (str): The communication key to save
        fetch_time (datetime): The communication key's fetch time
        doctype (str, optional): The doctype to save the key to.
        Defaults to COMMUNICATION_KEYS_DOCTYPE_NAME.

    Returns:
        Document: The created communication key record
    """
    communication_key_doctype = frappe.get_doc(doctype)
    communication_key_doctype.cmckey = communication_key

    communication_key_doctype.insert()

    frappe.db.commit()
    return communication_key_doctype


def get_communication_key(doctype: str = COMMUNICATION_KEYS_DOCTYPE_NAME) -> str | None:
    """Returns the most recent communication key present in the database

    Args:
        doctype (str, optional): The doctype harbouring the communication key. Defaults to COMMUNICATION_KEYS_DOCTYPE_NAME.

    Returns:
        str: The fetched communication key
    """
    error_messages = None
    communication_key = frappe.db.get_single_value(doctype, "cmckey")

    if communication_key:
        return communication_key

    error_messages = "No Communication Key found in %s" % doctype
    etims_logger.error(error_messages)
    frappe.throw(error_messages, title="Incorrect Setup")


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


def get_last_request_date(
    doctype: str = LAST_REQUEST_DATE_DOCTYPE_NAME,
) -> str | None:
    """Returns the Datetime of the last request as a string

    Args:
        doctype (str, optional): The doctype harbouring the last request date. Defaults to LAST_REQUEST_DATE_DOCTYPE_NAME.

    Returns:
        str | None: The last request date
    """
    last_request_date = frappe.db.get_single_value(doctype, "lastreqdt", cache=False)

    if last_request_date:
        formatted_last_request_date = format_last_request_date(last_request_date)
        return formatted_last_request_date


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


def get_current_user_timezone(current_user: str) -> str | None:
    timezone = frappe.db.get_value(
        "User", {"name": current_user}, ["time_zone"], as_dict=True
    )

    if timezone:
        return timezone.time_zone


def get_route_path(
    search_field: str,
    routes_table_doctype: str = ROUTES_TABLE_CHILD_DOCTYPE_NAME,
) -> str | None:
    """Searches and retrieves the route path from the KRA eTims Route Table Navari doctype

    Args:
        search_field (str): The field to search.
        routes_table (str, optional): _description_. Defaults to ROUTES_TABLE_CHILD_DOCTYPE_NAME.

    Returns:
        str | None: The retrieved route
    """

    query = f"""
    SELECT url_path
    FROM `tab{routes_table_doctype}`
    WHERE url_path_function LIKE '{search_field}'
    AND parent LIKE '{ROUTES_TABLE_DOCTYPE_NAME}'
    LIMIT 1
    """

    results = frappe.db.sql(query, as_dict=True)

    if results:
        return results[0].url_path


def get_environment_settings(
    company_pin: str,
    doctype: str = SETTINGS_DOCTYPE_NAME,
    environment: str = "Sandbox",
) -> Document | None:
    """Returns the current environment's settings

    Args:
        company_pin (str): The PIN of the current company
        doctype (str, optional): The settings doctype to fetch from. Defaults to SETTINGS_DOCTYPE_NAME.
        environment (str, optional): The environment state. Defaults to "Sandbox".

    Returns:
        Document | None: The fetched document.
    """
    error_message = None
    query = f"""
    SELECT sandbox,
        server_url,
        tin,
        dvcsrlno,
        bhfid,
        company,
        name
    FROM `tab{doctype}`
    WHERE name like '{company_pin}-{environment}%'
    """
    setting_doctype = frappe.db.sql(query, as_dict=True)

    if setting_doctype:
        return setting_doctype[0]

    error_message = "No environment setting created. Please ensure a valid Navari eTims Integration Setting record exists"
    etims_logger.error(error_message)
    frappe.throw(error_message, title="Incorrect Setup")


def get_server_url(document: Document, environment: str = "Sandbox") -> str | None:
    settings = get_environment_settings(
        document.get("company_tax_id"), environment=environment
    )

    if settings:
        server_url = settings.get("server_url")

        return server_url


def build_headers(
    document: Document, environment: str = "Sandbox"
) -> dict[str, str] | None:
    """Builds the header required for communication with the eTims Server

    Args:
        document (Document): The document to fetch setting information from
        environment (str, optional): Variable denoting environment of current instance. Defaults to "Sandbox".

    Returns:
        dict[str, str] | None: The headers as a dictionary
    """
    settings = get_environment_settings(
        document.get("company_tax_id"), environment=environment
    )
    # TODO: Handle no communication key and request date
    communication_key = get_communication_key()

    if settings and communication_key:
        headers = {
            "tin": settings.get("tin"),
            "bhfId": settings.get("bhfid"),
            "cmcKey": communication_key,
        }

        return headers


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
        url=url,
        data=payload,
        headers=headers,
        is_async=True,
        queue=queue_type,
        on_success=success_callback,
        on_failure=failure_callback,
    )

    return job.id
