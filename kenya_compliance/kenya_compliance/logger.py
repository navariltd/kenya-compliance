"""eTims Logger initialisation"""

import frappe
from frappe.utils import logger

logger.set_log_level("DEBUG")
etims_logger = frappe.logger("etims", allow_site=True, file_count=50)
