# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from ..doctype_names_mapping import (
    ROUTES_TABLE_DOCTYPE_NAME,
    ROUTES_TABLE_CHILD_DOCTYPE_NAME,
)


class TestNavariKRAeTimsRouteTable(FrappeTestCase):
    """Test Cases"""

    def test_url_path_formatting(self) -> None:
        """Tests the proper formatting of url paths upon creation of a record"""
        child = frappe.new_doc(ROUTES_TABLE_CHILD_DOCTYPE_NAME)
        child.url_path_function = "testing"
        child.url_path = "test_url_path"
        child.parent = ROUTES_TABLE_DOCTYPE_NAME
        child.parenttype = ROUTES_TABLE_DOCTYPE_NAME
        child.parent_field = "routes_table"
        child.save()

        added_child = frappe.db.get_value(
            ROUTES_TABLE_CHILD_DOCTYPE_NAME,
            {"url_path_function": "testing"},
            ["*"],
            as_dict=True,
        )

        self.assertTrue(added_child.url_path.startswith("/"))
        self.assertEqual(added_child.url_path, "/test_url_path")
