# Copyright (c) 2023, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from ...logger import etims_logger
from ...utils import is_valid_kra_pin, is_valid_url


class eTimsIntegrationSettings(Document):
    """Settings Doctype"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = None

    def validate(self) -> None:
        """Validation hook"""
        if not self.tin:
            self.error = "Please Provide the Tax-Payer's PIN"

            etims_logger.error(self.error)
            frappe.throw(
                self.error,
                frappe.ValidationError,
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

        if self.dvcsrlno:
            if len(self.dvcsrlno) > 100:
                self.error = "Invalid Device Serial Number"

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError(self.error),
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

        if self.server_url:
            if not is_valid_url(self.server_url):
                self.error = "The URL Provided is invalid"
                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title="Validation Error",
                )

        if self.sandbox:
            self.server_url = "https://etims-api-sbx.kra.go.ke/etims-api/"
        else:
            self.server_url = "https://etims-api.kra.go.ke/etims-api/"
