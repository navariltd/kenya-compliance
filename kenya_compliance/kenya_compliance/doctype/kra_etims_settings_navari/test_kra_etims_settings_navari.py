# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from ...utils import get_server_url, get_settings_record
from ..doctype_names_mapping import (
    PRODUCTION_SERVER_URL,
    SANDBOX_SERVER_URL,
    SETTINGS_DOCTYPE_NAME,
)


class TestKRAeTimsSettingsNavari(FrappeTestCase):
    """Test Cases"""

    def setUp(self) -> None:
        super().setUp()

        sandbox = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
        sandbox.tin = "A123456789W"
        sandbox.dvcsrlno = "987654321"
        sandbox.bhfid = "00"

        sandbox.save()

        production = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
        production.tin = "A123456789W"
        production.dvcsrlno = "123456789"
        production.bhfid = "00"
        production.sandbox = 0

        production.save()

    def test_no_pin_supplied(self) -> None:
        """Tests cases when no pin is supplied"""
        with self.assertRaises(frappe.ValidationError):
            settings = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
            settings.dvcsrlno = "777"
            settings.bhfid = "00"
            settings.save()

    def test_invalid_branch_id_supplied(self) -> None:
        """Tests cases invalid branch id is supplied"""
        with self.assertRaises(frappe.ValidationError):
            settings_1 = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
            settings_1.tin = "A123456789W"
            settings_1.dvcsrlno = "777"
            settings_1.bhfid = "1"
            settings_1.save()

            settings_2 = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.dvcsrlno = "777"
            settings_2.bhfid = "111"
            settings_2.save()

            settings_2 = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.dvcsrlno = "777"
            settings_2.bhfid = ""
            settings_2.save()

    def test_invalid_device_serial_number(self) -> None:
        """Tests cases when invalid device serial number is supplied"""
        with self.assertRaises(frappe.ValidationError):
            settings_1 = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
            settings_1.tin = "A123456789W"
            settings_1.dvcsrlno = "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
            settings_1.bhfid = "00"
            settings_1.save()

            settings_2 = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.dvcsrlno = ""
            settings_2.bhfid = "00"
            settings_2.save()

    def test_server_url_in_sandbox(self) -> None:
        """Test to ensure correct server url is provided in sandbox environment"""
        new_settings = frappe.db.get_value(
            SETTINGS_DOCTYPE_NAME,
            {"dvcsrlno": "987654321"},
            ["server_url", "sandbox"],
            as_dict=True,
        )

        server_url = new_settings.server_url
        new_settings_sandbox_value = new_settings.sandbox

        self.assertEqual(server_url, SANDBOX_SERVER_URL)
        self.assertEqual(
            int(new_settings_sandbox_value), 1
        )  # Defaults to 1 when not supplied

    def test_server_url_in_production(self) -> None:
        """Tests to ensure correct server url is provided in prod environment"""
        new_settings = frappe.db.get_value(
            SETTINGS_DOCTYPE_NAME,
            {"sandbox": 0},
            ["server_url", "sandbox"],
            as_dict=True,
        )

        server_url = new_settings.server_url
        new_settings_sandbox_value = new_settings.sandbox

        self.assertEqual(server_url, PRODUCTION_SERVER_URL)
        self.assertEqual(int(new_settings_sandbox_value), 0)
