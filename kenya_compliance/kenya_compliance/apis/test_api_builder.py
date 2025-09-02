import asyncio
from unittest.mock import AsyncMock, patch
import frappe
from frappe.tests.utils import FrappeTestCase
from .api_builder import EndpointsBuilder

class TestEndpointsBuilderDB(FrappeTestCase):

    @patch(
        "kenya_compliance.kenya_compliance.apis.api_builder.update_last_request_date",
        new_callable=lambda: lambda *args, **kwargs: None
    )
    @patch(
        "kenya_compliance.kenya_compliance.apis.api_builder.make_post_request",
        new_callable=AsyncMock
    )
    def test_make_post_request_success(self, mock_make_post_request, mock_update_request_date):
        # Arrange
        mock_response = {"resultCd": "000", "resultMsg": "Success", "resultDt": "20240101000000"}
        mock_make_post_request.return_value = mock_response

        e = EndpointsBuilder()
        e.url = "https://test.com/"
        e.payload = {"test_data": "Test Data"}
        e.headers = {"Content-Type": "application/json"}
        e.success_callback = lambda resp: setattr(e, "success_handled", True)
        e.error_callback = lambda resp, **kwargs: setattr(e, "error_handled", True)

        # Act
        e.make_remote_call()
        frappe.db.commit()

        # Assert
        record = frappe.get_all(
            "Integration Request",
            filters={"is_remote_request": 1, "url": e.url},
            fields=["*"]
        )
        self.assertTrue(hasattr(e, "success_handled"))
        self.assertFalse(hasattr(e, "error_handled"))
        self.assertGreater(len(record), 0)
        self.assertEqual(record[0]["output"], "Success")

    @patch(
        "kenya_compliance.kenya_compliance.apis.api_builder.update_last_request_date",
        new_callable=lambda: lambda *args, **kwargs: None
    )
    @patch(
        "kenya_compliance.kenya_compliance.apis.api_builder.make_post_request",
        new_callable=AsyncMock
    )
    def test_make_post_request_failed(self, mock_make_post_request, mock_update_request_date):
        # Arrange
        mock_response = {"resultCd": "001", "resultMsg": "Errored", "resultDt": "20240101000000"}
        mock_make_post_request.return_value = mock_response

        e = EndpointsBuilder()
        e.url = "https://test.com/"
        e.payload = {"test_data": "Test Data"}
        e.headers = {"Content-Type": "application/json"}
        e.success_callback = lambda resp: setattr(e, "success_handled", True)
        e.error_callback = lambda resp, **kwargs: setattr(e, "error_handled", True)

        # Act
        e.make_remote_call()
        frappe.db.commit()

        # Assert
        record = frappe.get_all(
            "Integration Request",
            filters={"is_remote_request": 1, "url": e.url},
            fields=["*"]
        )
        self.assertTrue(hasattr(e, "error_handled"))
        self.assertFalse(hasattr(e, "success_handled"))
        self.assertGreater(len(record), 0)
        self.assertEqual(record[0]["error"], "Errored")
