# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

from typing import Final

import frappe
from frappe.tests.utils import FrappeTestCase

from ...utils import get_server_url, get_settings_document

INTEGRATION_SETTINGS_DOCTYPE_NAME: Final[str] = "KRA eTims Settings Navari"
SANDBOX_SERVER_URL: Final[str] = "https://etims-api-sbx.kra.go.ke/etims-api/"
PRODUCTION_SERVER_URL: Final[str] = "https://etims-api.kra.go.ke/etims-api/"


class TestKRAeTimsSettingsNavari(FrappeTestCase):
    """Test Cases"""

    def test_no_pin_supplied(self) -> None:
        """Tests cases when no pin is supplied"""
        with self.assertRaises(frappe.ValidationError):
            settings = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings.tin = "a"
            settings.dvcsrlno = "777"
            settings.bhfid = "00"
            settings.save()

    def test_invalid_branch_id_supplied(self) -> None:
        """Tests cases invalid branch id is supplied"""
        with self.assertRaises(frappe.ValidationError):
            settings_1 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_1.tin = "A123456789W"
            settings_1.dvcsrlno = "777"
            settings_1.bhfid = "1"
            settings_1.save()

            settings_2 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.dvcsrlno = "777"
            settings_2.bhfid = "111"
            settings_2.save()

            settings_2 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.dvcsrlno = "777"
            settings_2.bhfid = ""
            settings_2.save()

    def test_invalid_device_serial_number(self) -> None:
        """Tests cases when invalid device serial number is supplied"""
        with self.assertRaises(frappe.ValidationError):
            settings_1 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_1.tin = "A123456789W"
            settings_1.dvcsrlno = "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
            settings_1.bhfid = "00"
            settings_1.save()

            settings_2 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.dvcsrlno = ""
            settings_2.bhfid = "00"
            settings_2.save()

    def test_server_url_in_sandbox(self) -> None:
        """Test to ensure correct server url is provided in sandbox environment"""
        settings = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
        settings.tin = "A123456789W"
        settings.dvcsrlno = "123456789"
        settings.bhfid = "00"

        settings.save()

        server_url = get_server_url(INTEGRATION_SETTINGS_DOCTYPE_NAME)
        settings_doctype = get_settings_document(INTEGRATION_SETTINGS_DOCTYPE_NAME)

        self.assertEqual(server_url, SANDBOX_SERVER_URL)
        self.assertEqual(
            int(settings_doctype.sandbox), 1
        )  # Defaults to 1 when not supplied

    def test_server_url_in_production(self) -> None:
        """Tests to ensure correct server url is provided in prod environment"""
        settings = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
        settings.tin = "A123456789W"
        settings.dvcsrlno = "123456789"
        settings.bhfid = "00"
        settings.sandbox = 0

        settings.save()

        server_url = get_server_url(INTEGRATION_SETTINGS_DOCTYPE_NAME)
        settings_doctype = get_settings_document(INTEGRATION_SETTINGS_DOCTYPE_NAME)

        self.assertEqual(server_url, PRODUCTION_SERVER_URL)
        self.assertEqual(int(settings_doctype.sandbox), 0)
