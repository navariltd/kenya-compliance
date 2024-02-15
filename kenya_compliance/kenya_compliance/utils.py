"""Utility functions"""

import json
import re
from datetime import date, datetime

import aiohttp
import frappe
from frappe.model.document import Document

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


async def make_get_request(url: str) -> str:
    """Make an Asynchronous Get Request to specified URL

    Args:
        url (str): The URL

    Returns:
        str: The Response
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def make_post_request(
    url: str, data: dict[str, str] | None = None
) -> dict[str, str]:
    """Make an Asynchronous Post Request to specified URL

    Args:
        url (str): The URL
        data (dict[str, str] | None, optional): Data to send to server. Defaults to None.

    Returns:
        dict: The Server Response
    """
    request_data = json.dumps(data).encode()

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=request_data) as response:
            return await response.json()


def get_settings_document(
    document: str = "eTims Integration Settings",
) -> frappe._dict | None:
    """Returns the setting doctype as a dictionary object

    Args:
        document (str, optional): The doctype to be fetched. Defaults to "eTims Integration Settings".

    Returns:
        frappe._dict | None: The fetched doctype
    """
    settings_doctype = frappe.db.get_singles_dict(document)

    if settings_doctype:
        return settings_doctype


def get_server_url(document: str = "eTims Integration Settings") -> str | None:
    """Returns the URL of the eTims Server as specified in the settings doctype

    Args:
        document (str, optional): The settings doctype. Defaults to "eTims Integration Settings".

    Returns:
        str | None: The server url specified in settings doctype
    """
    settings_doctype = get_settings_document(document)

    if settings_doctype:
        server_url = settings_doctype.get("server_url")

        return server_url


def save_communication_key_to_doctype(
    communication_key: str,
    fetch_time: datetime,
    doctype: str = "eTims Communication Keys",
) -> Document:
    """Saves the provided Communication to the specified doctype

    Args:
        communication_key (str): The communication key to save
        fetch_time (datetime): The communication key's fetch time
        doctype (str, optional): The doctype to save the key to.
        Defaults to "eTims Communication Keys".

    Returns:
        Document: The created communication key record
    """
    communication_key_doctype = frappe.new_doc(doctype)
    communication_key_doctype.communication_key = communication_key
    communication_key_doctype.fetch_time = fetch_time

    communication_key_doctype.save()
    etims_logger.info("Communication Key %s saved" % communication_key_doctype.name)

    return communication_key_doctype


def build_date_from_string(date_string: str, format: str = "%Y-%m-%d") -> date:
    """Builds a Date object from string, and format provided

    Args:
        date_string (str): The date string to build object from
        format (str, optional): The format of the date_string string. Defaults to "%Y-%m-%d".

    Returns:
        date: The date object
    """
    date_object = datetime.strptime(date_string, format).date()

    return date_object
