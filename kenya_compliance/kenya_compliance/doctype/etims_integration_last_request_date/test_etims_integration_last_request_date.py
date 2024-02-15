# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

from datetime import date

import frappe
from dateutil.relativedelta import relativedelta
from frappe.tests.utils import FrappeTestCase


class TesteTimsIntegrationLastRequestDate(FrappeTestCase):
    """Test Cases"""

    def test_setting_future_last_request_date(self) -> None:
        """Tests case when setting the last request date to a future date (read any day after today)"""
        with self.assertRaises(
            frappe.ValidationError, msg="Last Request Date cannot appear after today"
        ):
            lstreqdt_doc_one_day = frappe.new_doc("eTims Integration Last Request Date")
            lstreqdt_doc_one_day.lastreqdt = date.today() + relativedelta(days=1)

            lstreqdt_doc_one_day.save()

            lstreqdt_doc_ten_days = frappe.new_doc(
                "eTims Integration Last Request Date"
            )
            lstreqdt_doc_ten_days.lastreqdt = date.today() + relativedelta(days=10)

            lstreqdt_doc_ten_days.save()
