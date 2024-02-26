# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

from datetime import date

import frappe
from dateutil.relativedelta import relativedelta
from frappe.tests.utils import FrappeTestCase

from ..doctype_names_mapping import LAST_REQUEST_DATE_DOCTYPE_NAME


class TestNavariKRAeTimsLastRequestDate(FrappeTestCase):
    """Test Cases"""

    def test_setting_future_last_request_date(self) -> None:
        """Tests case when setting the last request date to a future date (read any day after today)"""
        with self.assertRaises(
            frappe.ValidationError, msg="Last Request Date cannot appear after today"
        ):
            lstreqdt_doc_one_day = frappe.new_doc(LAST_REQUEST_DATE_DOCTYPE_NAME)
            lstreqdt_doc_one_day.lastreqdt = date.today() + relativedelta(days=1)

            lstreqdt_doc_one_day.save()

            lstreqdt_doc_ten_days = frappe.new_doc(
                "eTims Integration Last Request Date"
            )
            lstreqdt_doc_ten_days.lastreqdt = date.today() + relativedelta(days=10)

            lstreqdt_doc_ten_days.save()

    def test_saving_with_no_request_date(self) -> None:
        """Tests cases when doctype is saved without setting the last request date"""
        with self.assertRaises(frappe.ValidationError):
            doc = frappe.new_doc(LAST_REQUEST_DATE_DOCTYPE_NAME)
            doc.save()
