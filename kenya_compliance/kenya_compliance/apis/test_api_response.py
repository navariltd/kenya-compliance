import asyncio
from unittest.mock import MagicMock, patch
from typing import Any

import frappe
from frappe.tests.utils import FrappeTestCase

from .remote_response_status_handlers import (
    check_duplicate_registered_purchase,
    create_purchase_from_search_details,
)


def setUp(self):
    super().setUp()

    # In-memory stores
    self.error_logs = []
    self.integration_requests = []
    self.purchases = []

    # Patch frappe.db.exists
    def fake_exists(doctype, filters_or_name=None):
        if doctype == "Navari eTims Registered Purchases":
            if isinstance(filters_or_name, dict):
                for p in self.purchases:
                    if all(getattr(p, k, None) == v for k, v in filters_or_name.items()):
                        return f"{p.spplrTin}-{p.spplrInvcNo}"
            elif isinstance(filters_or_name, str):
                for p in self.purchases:
                    if f"{p.spplrTin}-{p.spplrInvcNo}" == filters_or_name:
                        return filters_or_name
        return None

    self.exists_patcher = patch("frappe.db.exists", side_effect=fake_exists)
    self.exists_patcher.start()

    # Patch frappe.get_doc correctly
    def fake_get_doc(doc, *args, **kwargs):
        if isinstance(doc, dict):
            doctype = doc.get("doctype")
            store = {
                "Navari eTims Registered Purchases": self.purchases,
                "Integration Request": self.integration_requests,
                "Error Log": self.error_logs,
            }.get(doctype, [])

            fake_doc = MagicMock()
            fake_doc.name = f"{doctype[:3].upper()}-{len(store)+1}"

            # Properly assign all fields
            for k, v in doc.items():
                setattr(fake_doc, k, v)

            def insert(*a, **k):
                store.append(fake_doc)
                return fake_doc

            fake_doc.insert = insert
            fake_doc.save = lambda *a, **k: fake_doc
            return fake_doc

        else:  # string doctype
            fake_doc = MagicMock()
            fake_doc.name = doc
            fake_doc.insert = lambda *a, **k: fake_doc
            fake_doc.save = lambda *a, **k: fake_doc
            return fake_doc

    # THIS MUST BE INSIDE setUp
    self.get_doc_patcher = patch("frappe.get_doc", side_effect=fake_get_doc)
    self.get_doc_patcher.start()

    # Patch frappe.get_all
    def fake_get_all(doctype, *args, filters=None, fields=None, limit=None, **kwargs):
        store_map = {
            "Error Log": self.error_logs,
            "Integration Request": self.integration_requests,
            "Navari eTims Registered Purchases": self.purchases,
        }
        store = store_map.get(doctype, [])
        results = []
        for item in store:
            match = True
            if filters:
                for k, v in filters.items():
                    if getattr(item, k, None) != v:
                        match = False
                        break
            if match:
                results.append({**item.__dict__})
        return results[:limit] if limit else results

    self.get_all_patcher = patch("frappe.get_all", side_effect=fake_get_all)
    self.get_all_patcher.start()


    def tearDown(self):
        super().tearDown()
        self.exists_patcher.stop()
        self.get_doc_patcher.stop()
        self.get_all_patcher.stop()

    # ------------------------
    # Test Methods
    # ------------------------

    def test_check_duplicate_registered_purchase_logs_error(self):
        sale = {"spplrTin": "123", "spplrInvcNo": "INV-001"}

        # First call should not find duplicate
        self.assertIsNone(check_duplicate_registered_purchase(sale))

        # Add a fake purchase to trigger duplicate
        fake_purchase = MagicMock()
        fake_purchase.spplrTin = "123"
        fake_purchase.spplrInvcNo = "INV-001"
        self.purchases.append(fake_purchase)

        duplicate_id = check_duplicate_registered_purchase(sale)
        self.assertEqual(duplicate_id, "123-INV-001")
        self.assertGreater(len(self.error_logs), 0)

    def test_create_purchase_from_search_details_creates_purchase(self):
        sale = {
            "spplrNm": "Vendor",
            "spplrTin": "456",
            "spplrBhfId": "001",
            "spplrInvcNo": "INV-002",
            "rcptTyCd": "A",
            "pmtTyCd": "CASH",
            "remark": "Test Remark",
            "cfmDt": "20240101",
            "salesDt": "20240101",
            "stockRlsDt": "20240101",
            "totItemCnt": 1,
        }

        doc_name = create_purchase_from_search_details(sale)
        self.assertTrue(doc_name.startswith("PUR-"))
        self.assertGreater(len(self.purchases), 0)
