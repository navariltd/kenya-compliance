import frappe


def after_install() -> None:
    query = """
    ALTER TABLE `tabSales Invoice`
    ADD COLUMN IF NOT EXISTS `etims_serial_number` INT AUTO_INCREMENT,
    ADD INDEX (`etims_serial_number`)
    """

    frappe.db.sql_ddl(query)
