import frappe

from ..handlers import handle_errors


def on_error(
    response: dict | str,
    url: str | None = None,
    doctype: str | None = None,
    document_name: str | None = None,
    integration_request_name: str | None = None,
) -> None:
    """Base "on-error" callback.

    Args:
        response (dict | str): The remote response
        url (str | None, optional): The remote address. Defaults to None.
        doctype (str | None, optional): The doctype calling the remote address. Defaults to None.
        document_name (str | None, optional): The document calling the remote address. Defaults to None.
        integration_reqeust_name (str | None, optional): The created Integration Request document name. Defaults to None.
    """
    handle_errors(
        response,
        route=url,
        doctype=doctype,
        document_name=document_name,
        integration_request_name=integration_request_name,
    )


"""
Thes functions are required as serialising lambda expressions is a bit involving.
"""


def customer_search_on_success(
    response: dict,
    document_name: str,
) -> None:
    frappe.db.set_value(
        "Customer",
        document_name,
        {
            "custom_tax_payers_name": response["taxprNm"],
            "custom_tax_payers_status": response["taxprSttsCd"],
            "custom_county_name": response["prvncNm"],
            "custom_subcounty_name": response["dstrtNm"],
            "custom_tax_locality_name": response["sctrNm"],
            "custom_location_name": response["locDesc"],
            "custom_is_validated": 1,
        },
    )


def item_registration_on_success(response: dict, document_name: str) -> None:
    frappe.db.set_value("Item", document_name, {"custom_item_registered": 1})


def customer_insurance_details_submission_on_success(
    response: dict, document_name: str
) -> None:
    frappe.db.set_value(
        "Customer",
        document_name,
        {"custom_insurance_details_submitted_successfully": 1},
    )


def customer_branch_details_submission_on_success(
    response: dict, document_name: str
) -> None:
    frappe.db.set_value(
        "Customer",
        document_name,
        {"custom_details_submitted_successfully": 1},
    )


def employee_user_details_submission_on_success(
    response: dict, document_name: str
) -> None:
    frappe.db.set_value("Employee", document_name, {"custom_etims_received": 1})


def inventory_submission_on_success(response: dict, document_name: str) -> None:
    frappe.db.set_value("Item", document_name, {"custom_inventory_submitted": 1})


def imported_item_submission_on_success(response: dict, document_name: str) -> None:
    frappe.db.set_value("Item", document_name, {"custom_imported_item_submitted": 1})


def sales_information_submission_on_success(
    response: dict, invoice_type: str, document_name: str
) -> None:
    response_data = response["data"]

    frappe.db.set_value(
        invoice_type,
        document_name,
        {
            "custom_current_receipt_number": response_data["curRcptNo"],
            "custom_total_receipt_number": response_data["totRcptNo"],
            "custom_internal_data": response_data["intrlData"],
            "custom_receipt_signature": response_data["rcptSign"],
            "custom_control_unit_date_time": response_data["sdcDateTime"],
            "custom_successfully_submitted": 1,
        },
    )


def item_composition_submission_on_success(response: dict, document_name: str) -> None:
    frappe.db.set_value(
        "BOM", document_name, {"custom_item_composition_submitted_successfully": 1}
    )


def purchase_invoice_submission_on_success(response: dict, document_name: str) -> None:
    # Update Invoice fields from KRA's response
    frappe.db.set_value(
        "Purchase Invoice",
        document_name,
        {
            "custom_submitted_successfully": 1,
        },
    )


def stock_mvt_submission_on_success(response: dict, document_name: str) -> None:
    frappe.db.set_value(
        "Stock Ledger Entry", document_name, {"custom_submitted_successfully": 1}
    )
