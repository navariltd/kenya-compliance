# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

from datetime import datetime

import frappe
from frappe.model.document import Document

from ...logger import etims_logger


class KRAeTimsCommunicationKeys(Document):
    """Communication Key Store doctype"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = None

    def validate(self) -> None:
        """Validation hook"""
        if not self.communication_key:
            self.error = "Communication Key must be present"

            etims_logger.error(self.error)
            frappe.throw(
                self.error,
                frappe.ValidationError,
                title="Validation Error",
            )

        if not self.fetch_time:
            # TODO: Handle timezones correctly
            self.fetch_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
