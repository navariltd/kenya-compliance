# Copyright (c) 2023, Navari Ltd and Contributors
# See license.txt

from typing import Final

import frappe
from frappe.tests.utils import FrappeTestCase

INTEGRATION_SETTINGS_DOCTYPE_NAME: Final[str] = "eTims Integration Settings"


class TesteTimsIntegrationSettings(FrappeTestCase):
    """Test Cases"""

    def test_no_pin_supplied(self) -> None:
        with self.assertRaises(frappe.ValidationError):
            settings = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings.tin = "a"
            settings.server_url = "https://etims-api-sbx.kra.go.ke/etims-api"
            settings.dvcSrlNo = "777"
            settings.bhfid = "00"
            settings.save()

    def test_invalid_url_supplied(self) -> None:
        with self.assertRaises(frappe.ValidationError):
            settings = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings.tin = "A123456789W"
            settings.server_url = "a"
            settings.dvcSrlNo = "777"
            settings.bhfid = "00"
            settings.save()

    def test_invalid_branch_id_supplied(self) -> None:
        with self.assertRaises(frappe.ValidationError):
            settings_1 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_1.tin = "A123456789W"
            settings_1.server_url = "https://etims-api-sbx.kra.go.ke/etims-api"
            settings_1.dvcSrlNo = "777"
            settings_1.bhfid = "1"
            settings_1.save()

            settings_2 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.server_url = "https://etims-api-sbx.kra.go.ke/etims-api"
            settings_2.dvcSrlNo = "777"
            settings_2.bhfid = "111"
            settings_2.save()

            settings_2 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.server_url = "https://etims-api-sbx.kra.go.ke/etims-api"
            settings_2.dvcSrlNo = "777"
            settings_2.bhfid = ""
            settings_2.save()

    def test_invalid_device_serial_number(self) -> None:
        with self.assertRaises(frappe.ValidationError):
            settings_1 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_1.tin = "A123456789W"
            settings_1.server_url = "https://etims-api-sbx.kra.go.ke/etims-api"
            settings_1.dvcSrlNo = "11111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111"
            settings_1.bhfid = "00"
            settings_1.save()

            settings_2 = frappe.new_doc(INTEGRATION_SETTINGS_DOCTYPE_NAME)
            settings_2.tin = "A123456789W"
            settings_2.server_url = "https://etims-api-sbx.kra.go.ke/etims-api"
            settings_2.dvcSrlNo = ""
            settings_2.bhfid = "00"
            settings_2.save()
