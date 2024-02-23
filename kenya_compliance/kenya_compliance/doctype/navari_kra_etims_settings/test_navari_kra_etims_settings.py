# Copyright (c) 2024, Navari Ltd and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from ..doctype_names_mapping import (
    PRODUCTION_SERVER_URL,
    SANDBOX_SERVER_URL,
    SETTINGS_DOCTYPE_NAME,
)


def create_test_settings_doctypes() -> None:
    """Creates test setting doctype records"""
    # Sandbox setting with company specified
    sandbox = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
    sandbox.tin = "A123456789W"
    sandbox.dvcsrlno = "987654321"
    sandbox.bhfid = "00"
    sandbox.company = "Test Company 1"

    sandbox.save()

    # Production setting with no company specified
    production = frappe.new_doc(SETTINGS_DOCTYPE_NAME)
    production.tin = "A123456789W"
    production.dvcsrlno = "123456789"
    production.bhfid = "00"
    production.sandbox = 0

    production.save()


def create_test_companies() -> None:
    """creates test company records"""
    company_1 = frappe.new_doc("Company")
    company_1.company_name = "Test Company 1"
    company_1.default_currency = "USD"
    company_1.country = "Kenya"
    company_1.tax_id = "Z123456789A"

    company_1.save()

    company_2 = frappe.new_doc("Company")
    company_2.company_name = "Test Company 2"
    company_2.default_currency = "USD"
    company_2.country = "Kenya"

    company_2.save()

    company_3 = frappe.new_doc("Company")
    company_3.company_name = "Test Company 3"
    company_3.default_currency = "USD"
    company_3.country = "Kenya"
    company_3.tax_id = "AB123456789"

    company_3.save()


class TestNavariKRAeTimsSettings(FrappeTestCase):
    """Test Cases"""

    def setUp(self) -> None:
        create_test_companies()
        create_test_settings_doctypes()

    def tearDown(self) -> None:
        frappe.db.delete(SETTINGS_DOCTYPE_NAME)
        frappe.db.delete(
            "Company",
            {
                "company_name": (
                    "in",
                    ["Test Company 1", "Test Company 2", "Test Company 3"],
                )
            },
        )

    # def test_invalid_url_supplied(self) -> None:
    #     """Tests cases when an invalid url is supplied"""
    #     with self.assertRaises(frappe.ValidationError):
    #         setting = frappe.db.get_value(
    #             SETTINGS_DOCTYPE_NAME,
    #             {"dvcsrlno": "123456789"},
    #             ["*"],
    #             as_dict=True,
    #         )

    #         to_update = frappe.get_doc(
    #             SETTINGS_DOCTYPE_NAME, setting.name, for_update=True
    #         )
    #         to_update.server_url = "failing test url"
    #         to_update.save()

    def test_invalid_pin_supplied(self) -> None:
        """Tests cases when an invalid KRA company PIN (tin) has been supplied"""
        with self.assertRaises(frappe.ValidationError):
            setting = frappe.db.get_value(
                SETTINGS_DOCTYPE_NAME,
                {"dvcsrlno": "123456789"},
                ["*"],
                as_dict=True,
            )

            to_update = frappe.get_doc(
                SETTINGS_DOCTYPE_NAME, setting.name, for_update=True
            )
            to_update.company = "Test Company 3"
            to_update.save()

    def test_no_pin_supplied(self) -> None:
        """Tests cases when no pin is supplied"""
        with self.assertRaises(frappe.ValidationError):
            setting = frappe.db.get_value(
                SETTINGS_DOCTYPE_NAME,
                {"dvcsrlno": "123456789"},
                ["*"],
                as_dict=True,
            )

            to_update = frappe.get_doc(
                SETTINGS_DOCTYPE_NAME, setting.name, for_update=True
            )
            to_update.company = "Test Company 2"
            to_update.save()

    def test_invalid_branch_id_supplied(self) -> None:
        """Tests cases invalid branch id is supplied"""
        with self.assertRaises(frappe.ValidationError, msg="Invalid Branch Id"):
            setting = frappe.db.get_value(
                SETTINGS_DOCTYPE_NAME,
                {"dvcsrlno": "987654321"},
                ["*"],
                as_dict=True,
            )

            to_update = frappe.get_doc(
                SETTINGS_DOCTYPE_NAME, setting.name, for_update=True
            )
            to_update.bhfid = "1"
            to_update.save()

            to_update.bhfid = "111"
            to_update.save()

    def test_invalid_device_serial_number(self) -> None:
        """Tests cases when invalid device serial number is supplied"""
        with self.assertRaises(frappe.ValidationError):
            setting = frappe.db.get_value(
                SETTINGS_DOCTYPE_NAME,
                {"dvcsrlno": "987654321"},
                ["*"],
                as_dict=True,
            )

            to_update = frappe.get_doc(
                SETTINGS_DOCTYPE_NAME, setting.name, for_update=True
            )
            to_update.dvcsrlno = "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
            to_update.save()

    def test_server_url_in_sandbox(self) -> None:
        """Test to ensure correct server url is provided in sandbox environment"""
        settings = frappe.db.get_value(
            SETTINGS_DOCTYPE_NAME,
            {"dvcsrlno": "987654321"},
            ["server_url", "sandbox"],
            as_dict=True,
        )

        server_url = settings.server_url
        new_settings_sandbox_value = settings.sandbox

        self.assertEqual(server_url, SANDBOX_SERVER_URL)
        self.assertEqual(
            int(new_settings_sandbox_value), 1
        )  # Defaults to 1 when not supplied

    def test_server_url_in_production(self) -> None:
        """Tests to ensure correct server url is provided in prod environment"""
        new_settings = frappe.db.get_value(
            SETTINGS_DOCTYPE_NAME,
            {"dvcsrlno": "123456789"},
            ["server_url", "sandbox"],
            as_dict=True,
        )

        server_url = new_settings.server_url
        new_settings_sandbox_value = new_settings.sandbox

        self.assertEqual(server_url, PRODUCTION_SERVER_URL)
        self.assertEqual(int(new_settings_sandbox_value), 0)
