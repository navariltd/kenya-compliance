# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

from datetime import datetime
from zoneinfo import ZoneInfo

import frappe
from frappe.model.document import Document


class NavariKRAeTimsIntegrationLog(Document):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = None

    def validate(self) -> None:
        """Validation Hook"""
        if not self.log_time:
            self.log_time = datetime.now(tz=ZoneInfo("Africa/Nairobi"))
