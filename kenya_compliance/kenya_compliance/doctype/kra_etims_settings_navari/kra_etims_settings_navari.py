# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

from typing import Final

import frappe
from frappe.model.document import Document

from ...logger import etims_logger
from ...utils import is_valid_kra_pin, is_valid_url

SANDBOX_SERVER_URL: Final[str] = "https://etims-api-sbx.kra.go.ke/etims-api/"
PRODUCTION_SERVER_URL: Final[str] = "https://etims-api.kra.go.ke/etims-api/"


class KRAeTimsSettingsNavari(Document):
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
                    frappe.ValidationError(self.error),
                    title="Validation Error",
                )

        if self.dvcsrlno:
            if len(self.dvcsrlno) > 100:
                self.error = "Invalid Device Serial Number"

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError(self.error),
                    title="Validation Error",
                )

        if self.tin:
            is_valid_pin = is_valid_kra_pin(self.tin)

            if not is_valid_pin:
                self.error = (
                    "The TaxPayer's PIN you entered does not resemble a valid PIN"
                )

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title="Validation Error",
                )
