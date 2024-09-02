import frappe


def after_uninstall() -> None:
    query = """
    ALTER TABLE `tabSales Invoice`
    DROP COLUMN IF EXISTS etims_serial_number;
    """

    frappe.db.sql_ddl(query)
