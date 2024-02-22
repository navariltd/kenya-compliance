# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt
from datetime import date

import frappe
from frappe.model.document import Document

from ...logger import etims_logger
from ...utils import build_date_from_string


class NavariKRAeTimsLastRequestDate(Document):
    """Last Request Date Doctype"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = None

    def validate(self) -> None:
        """Validation Hook"""

        if not self.lastreqdt:
            frappe.throw(
                "Last Request Date is required",
                frappe.ValidationError,
                title="Validation Error",
            )

        if self.lastreqdt:
            today = date.today()

            if isinstance(self.lastreqdt, str):
                self.lastreqdt = build_date_from_string(self.lastreqdt)

            if self.lastreqdt > today:
                self.errors = "Last Request Date cannot appear after today"

                etims_logger.error(self.errors)
                frappe.throw(
                    self.errors,
                    frappe.ValidationError,
                    title="Validation Error",
                )
