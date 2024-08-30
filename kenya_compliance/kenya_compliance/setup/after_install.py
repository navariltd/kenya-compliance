import frappe


def after_install() -> None:
    query = """
    ALTER TABLE `tabSales Invoice`
    ADD COLUMN `serial_number` INT AUTO_INCREMENT,
    ADD INDEX (`serial_number`)
    """

    frappe.db.sql_ddl(query)
