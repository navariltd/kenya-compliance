# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from ...logger import etims_logger
from ...utils import is_valid_kra_pin, is_valid_url
from ..doctype_names_mapping import PRODUCTION_SERVER_URL, SANDBOX_SERVER_URL


class NavariKRAeTimsSettings(Document):
    """ETims Integration Settings doctype"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = None
        self.message = None

    def validate(self) -> None:
        """Validation Hook"""
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
                    title="Validation Error",
                )

        if self.bhfid:
            if len(self.bhfid) != 2:
                self.error = "Invalid Branch Id"

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title="Validation Error",
                )

        if self.dvcsrlno:
            if len(self.dvcsrlno) > 100:
                self.error = "Invalid Device Serial Number"

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title="Validation Error",
                )

        if not self.company:
            self.error = "Company is Mandatory"

            etims_logger.error(self.error)
            frappe.throw(self.error, frappe.ValidationError, title="Validation Error")

        if not self.tin:
            self.error = "PIN is mandatory to proceed!"

            etims_logger.error(self.error)
            frappe.throw(self.error, frappe.ValidationError, title="Validation Error")

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
                    title="Validation Error",
                )

        if self.name:
            # Check if user is attempting to modify pin, environment type, or serial number after setting record
            # has been created.
            pin, env, device_serial = self.name.split("-")

            if pin != self.tin or env != self.env or device_serial != self.dvcsrlno:
                self.error = "You are attempting to change key details of this integration settings. Please duplicate and save this record instead of modifying it."
                etims_logger.error(self.error)

                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title="Validation Error",
                )
