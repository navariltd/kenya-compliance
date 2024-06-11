# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

import frappe

# import frappe
from frappe.tests.utils import FrappeTestCase

from ..doctype_names_mapping import TAXATION_TYPE_DOCTYPE_NAME


class TestNavariKRAeTimsTaxationType(FrappeTestCase):
    """Test Cases"""

    def test_duplicates(self) -> None:
        with self.assertRaises(frappe.DuplicateEntryError):
            doc = frappe.new_doc(TAXATION_TYPE_DOCTYPE_NAME)
            doc.cd = "Z"
            doc.save()

            doc = frappe.new_doc(TAXATION_TYPE_DOCTYPE_NAME)
            doc.cd = "Z"
            doc.save()
