# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ...logger import etims_logger


class NavariKRAeTimsCommunicationKey(Document):
    """Communication Key doctype"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = None

    def validate(self) -> None:
        """Validation Hook"""
        if self.cmckey:
            if len(self.cmckey) > 255:
                self.error = f"The communication key: {self.cmckey} length is invalid."
                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title="Invalid Communication Key Length",
                )
