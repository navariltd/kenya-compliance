# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

from functools import partial

import frappe
from frappe.model.document import Document

from ...apis.api_builder import EndpointsBuilder
from ...apis.remote_response_status_handlers import on_error
from ...logger import etims_logger
from ...utils import get_route_path, is_valid_kra_pin, is_valid_url
from ..doctype_names_mapping import (
    PRODUCTION_SERVER_URL,
    SANDBOX_SERVER_URL,
    SETTINGS_DOCTYPE_NAME,
)

endpoints_builder = EndpointsBuilder()


class NavariKRAeTimsSettings(Document):
    """ETims Integration Settings doctype"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = None
        self.message = None
        self.error_title = None

    def validate(self) -> None:
        """Validation Hook"""
        self.error_title = "Validation Error"

        if self.sandbox:
            self.server_url = SANDBOX_SERVER_URL
            self.env = "Sandbox"
        else:
            self.server_url = PRODUCTION_SERVER_URL
            self.env = "Production"

        if self.server_url:
            if not is_valid_url(self.server_url):
                self.error = "The URL Provided is invalid"
                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title=self.error_title,
                )

        if self.bhfid:
            if len(self.bhfid) != 2:
                self.error = "Invalid Branch Id"

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title=self.error_title,
                )

        if self.dvcsrlno:
            if len(self.dvcsrlno) > 100:
                self.error = "Invalid Device Serial Number"

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title=self.error_title,
                )

        if not self.company:
            self.error = "Company is Mandatory"

            etims_logger.error(self.error)
            frappe.throw(self.error, frappe.ValidationError, title=self.error_title)

        if not self.tin:
            self.error = "PIN is mandatory to proceed!"

            etims_logger.error(self.error)
            frappe.throw(self.error, frappe.ValidationError, title=self.error_title)

        if self.tin:
            is_valid_pin = is_valid_kra_pin(self.tin)

            if not is_valid_pin:
                self.error = (
                    "The Tax Payer's PIN you entered does not resemble a valid PIN"
                )

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title=self.error_title,
                )

        if self.is_active:
            # Ensure mutual exclusivity of is_active field across settings records
            query = f"""
            UPDATE `tab{SETTINGS_DOCTYPE_NAME}`
            SET is_active = 0
            WHERE name != '{self.name}'
                AND company = '{self.company}'
                AND env = '{self.env}'
                AND bhfid = '{self.bhfid}';
            """
            frappe.db.sql(query)

    def on_update(self) -> None:
        """On Change Hook"""
        if not self.is_active:
            active_envs = frappe.get_all(
                SETTINGS_DOCTYPE_NAME,
                filters={
                    "is_active": 1,
                    "company": self.company,
                    "env": self.env,
                    "bhfid": self.bhfid,
                },
                fields=["name", "is_active"],
            )

            if not active_envs:
                frappe.db.set_value(SETTINGS_DOCTYPE_NAME, self.name, "is_active", 1)
                self.reload()

    def before_insert(self) -> None:
        """Before Insertion Hook"""
        route_path, last_request_date = get_route_path("DeviceVerificationReq")

        if route_path:
            url = f"{self.server_url}{route_path}"
            payload = {
                "tin": self.tin,
                "bhfId": self.bhfid,
                "dvcSrlNo": self.dvcsrlno,
            }

            endpoints_builder.url = url
            endpoints_builder.payload = payload
            endpoints_builder.headers = {}  # Empty since headers are not needed here
            endpoints_builder.error_callback = on_error

            endpoints_builder.success_callback = partial(
                device_init_on_success, doc=self
            )

            endpoints_builder.make_remote_call(
                doctype=SETTINGS_DOCTYPE_NAME, document_name=self.name
            )


def device_init_on_success(doc: Document, response: dict) -> None:
    """Device Initialisation/Vertification Success Callback handler

    Args:
        doc (Document): The calling settings doctype
        response (dict): The calling settings doctype record
    """
    doc.communication_key = response["data"]["info"]["cmcKey"]
