# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

from typing import Final

import frappe
from frappe.tests.utils import FrappeTestCase
from ..doctype_names_mapping import COMMUNICATION_KEYS_DOCTYPE_NAME


class TestKRAeTimsCommunicationKeysNavari(FrappeTestCase):
    """Test Cases"""

    def test_no_communication_key(self) -> None:
        """Tests raising ValidationError on no communication key provided"""

        with self.assertRaises(frappe.ValidationError):
            invalid_communication_key = frappe.new_doc(COMMUNICATION_KEYS_DOCTYPE_NAME)
            invalid_communication_key.save()

    def test_autogenerate_fetch_time(self) -> None:
        """Tests autogeneration of fetch time"""
        test_communication_key = "test_key"

        communication_key = frappe.new_doc(COMMUNICATION_KEYS_DOCTYPE_NAME)
        communication_key.communication_key = test_communication_key
        communication_key.save()

        fetched_record = frappe.db.get_value(
            COMMUNICATION_KEYS_DOCTYPE_NAME,
            {"communication_key": test_communication_key},
            ["fetch_time", "communication_key"],
            as_dict=True,
        )

        self.assertEqual(fetched_record.communication_key, test_communication_key)
        self.assertIsNotNone(fetched_record.fetch_time)
