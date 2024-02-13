# Copyright (c) 2023, Navari Ltd and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe.model.document import Document


class eTimsCommunicationKeys(Document):
    """Communication Key Store doctype"""

    def validate(self) -> None:
        """Validation hook"""
        if not self.communication_key:
            frappe.throw(
                "Communication Key must be present",
                frappe.ValidationError,
                title="Validation Error",
            )

        if not self.fetch_time:
            self.fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
