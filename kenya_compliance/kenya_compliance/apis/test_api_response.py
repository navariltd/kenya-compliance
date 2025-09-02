import frappe
from frappe.tests.utils import FrappeTestCase

from .remote_response_status_handlers import (
    check_duplicate_registered_purchase,
    create_purchase_from_search_details,
)


class TestRemoteResponseStatusHandlers(FrappeTestCase):
    def setUp(self):
        super().setUp()

        # Cleanup before tests
        frappe.db.delete("Navari eTims Registered Purchases")
        frappe.db.delete("Integration Request")
        frappe.db.delete("Error Log")
        frappe.db.commit()

        # Ensure required payment type exists
        if not frappe.db.exists("Navari KRA eTims Payment Type", {"code": "CASH"}):
            frappe.get_doc({
                "doctype": "Navari KRA eTims Payment Type",
                "code": "CASH",
                "description": "Cash Payment",
            }).insert(ignore_permissions=True)

    def tearDown(self):
        super().tearDown()
        frappe.db.delete("Navari eTims Registered Purchases")
        frappe.db.delete("Integration Request")
        frappe.db.delete("Error Log")
        frappe.db.commit()

    # ------------------------
    # Test Methods
    # ------------------------

    def test_check_duplicate_registered_purchase_logs_error(self):
        sale = {"spplrTin": "123", "spplrInvcNo": "INV-001"}

        # First call should not find duplicate
        self.assertIsNone(check_duplicate_registered_purchase(sale))

        # Insert purchase with correct composite key
        frappe.get_doc({
            "doctype": "Navari eTims Registered Purchases",
            "supplier_pin": "123",
            "supplier_invoice_number": "INV-001",
            "supplier_name": "Test Supplier",
        }).insert(ignore_permissions=True)


        duplicate_id = check_duplicate_registered_purchase(sale)

        # Assert correct composite key string is returned
        self.assertEqual(duplicate_id, "123-INV-001")

        logs = frappe.get_all("Error Log", fields=["name"])
        self.assertGreater(len(logs), 0)

    def test_create_purchase_from_search_details_creates_purchase(self):
        sale = {
            "spplrNm": "Vendor",
            "spplrTin": "456",
            "spplrBhfId": "001",
            "spplrInvcNo": "INV-002",
            "rcptTyCd": "A",
            "pmtTyCd": "CASH",   # maps to the Payment Type created in setUp
            "remark": "Test Remark",
            "cfmDt": "20240101",
            "salesDt": "20240101",
            "stockRlsDt": "20240101",
            "totItemCnt": 1,
        }

        doc_name = create_purchase_from_search_details(sale)

        # Be flexible: assert that a document name was returned and saved
        self.assertTrue(bool(doc_name))

        purchases = frappe.get_all(
        "Navari eTims Registered Purchases",
        filters={"supplier_pin": "456", "supplier_invoice_number": "INV-002"},
        fields=["name"],
    )

        self.assertEqual(len(purchases), 1)
