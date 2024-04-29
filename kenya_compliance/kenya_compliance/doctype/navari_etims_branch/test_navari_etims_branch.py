# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from ..doctype_names_mapping import BRANCH_ID_DOCTYPE_NAME


class TestNavarieTimsBranch(FrappeTestCase):
    def test_branch_creation(self) -> None:
        branch_code = "ZZ"
        branch_name = "Test"

        doc = frappe.new_doc(BRANCH_ID_DOCTYPE_NAME)
        doc.branch_code = branch_code
        doc.branch_name = branch_name

        doc.save()

        fetched_doc = frappe.get_doc(BRANCH_ID_DOCTYPE_NAME, doc.name, for_update=False)

        self.assertEqual(fetched_doc.branch_code, branch_code)
        self.assertEqual(fetched_doc.branch_name, branch_name)

    def test_branch_code_length(self) -> None:
        with self.assertRaises(frappe.CharacterLengthExceededError):
            doc = frappe.new_doc(BRANCH_ID_DOCTYPE_NAME)
            doc.branch_code = "123"

            doc.save()
