# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from ..doctype_names_mapping import IMPORTED_ITEMS_STATUS_DOCTYPE_NAME


class TestNavarieTimsImportItemStatus(FrappeTestCase):
    def test_imported_item_type_creation(self) -> None:
        doc = frappe.new_doc(IMPORTED_ITEMS_STATUS_DOCTYPE_NAME)

        doc.code = "99"
        doc.sort_order = "99"
        doc.code_name = "Test Status"
        doc.code_description = "Testing Import Status"

        doc.save()

        fetched_doc = frappe.get_doc(
            IMPORTED_ITEMS_STATUS_DOCTYPE_NAME, doc.name, for_update=False
        )

        self.assertEqual(fetched_doc.name, "Test Status")
        self.assertEqual(fetched_doc.code_name, "Test Status")
        self.assertEqual(fetched_doc.sort_order, "99")
        self.assertEqual(fetched_doc.code_description, "Testing Import Status")
