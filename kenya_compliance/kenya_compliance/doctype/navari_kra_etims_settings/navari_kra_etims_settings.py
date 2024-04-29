# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import asyncio

import aiohttp
import frappe
from frappe.integrations.utils import create_request_log
from frappe.model.document import Document

from ...apis.api_builder import update_integration_request
from ...background_tasks.tasks import (
    send_pos_invoices_information,
    send_purchase_information,
    send_sales_invoices_information,
    send_stock_information,
    send_item_inventory_information,
)
from ...handlers import handle_errors
from ...logger import etims_logger
from ...utils import (
    get_route_path,
    is_valid_kra_pin,
    is_valid_url,
    make_post_request,
    update_last_request_date,
)
from ..doctype_names_mapping import (
    PRODUCTION_SERVER_URL,
    SANDBOX_SERVER_URL,
    SETTINGS_DOCTYPE_NAME,
)


class NavariKRAeTimsSettings(Document):
    """ETims Integration Settings doctype"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error = None
        self.message = None
        self.error_title = None

    def validate(self) -> None:
        """Validation Hook"""
        self.error_title = "Validation Error"

        if self.sandbox:
            self.server_url = SANDBOX_SERVER_URL
            self.env = "Sandbox"
        else:
            self.server_url = PRODUCTION_SERVER_URL
            self.env = "Production"

        if self.server_url:
            if not is_valid_url(self.server_url):
                self.error = "The URL Provided is invalid"
                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title=self.error_title,
                )

        if self.bhfid:
            if len(self.bhfid) != 2:
                self.error = "Invalid Branch Id"

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title=self.error_title,
                )

        if self.dvcsrlno:
            if len(self.dvcsrlno) > 100:
                self.error = "Invalid Device Serial Number"

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title=self.error_title,
                )

        if not self.company:
            self.error = "Company is Mandatory"

            etims_logger.error(self.error)
            frappe.throw(self.error, frappe.ValidationError, title=self.error_title)

        if not self.tin:
            self.error = "PIN is mandatory to proceed!"

            etims_logger.error(self.error)
            frappe.throw(self.error, frappe.ValidationError, title=self.error_title)

        if self.tin:
            is_valid_pin = is_valid_kra_pin(self.tin)

            if not is_valid_pin:
                self.error = (
                    "The Tax Payer's PIN you entered does not resemble a valid PIN"
                )

                etims_logger.error(self.error)
                frappe.throw(
                    self.error,
                    frappe.ValidationError,
                    title=self.error_title,
                )

        if self.is_active:
            # Ensure mutual exclusivity of is_active field across settings records
            query = f"""
            UPDATE `tab{SETTINGS_DOCTYPE_NAME}`
            SET is_active = 0
            WHERE name != '{self.name}'
                AND company = '{self.company}'
                AND env = '{self.env}'
                AND bhfid = '{self.bhfid}';
            """
            frappe.db.sql(query)

    def on_update(self) -> None:
        """On Change Hook"""
        if not self.is_active:
            active_envs = frappe.get_all(
                SETTINGS_DOCTYPE_NAME,
                filters={
                    "is_active": 1,
                    "company": self.company,
                    "env": self.env,
                    "bhfid": self.bhfid,
                },
                fields=["name", "is_active"],
            )

            if not active_envs:
                frappe.db.set_value(SETTINGS_DOCTYPE_NAME, self.name, "is_active", 1)
                self.reload()

        if self.sales_information_submission:
            # frequency of submission for sales info.
            sales_invoices_task_name = send_sales_invoices_information.__name__

            sales_invoices_task: Document = frappe.get_doc(
                "Scheduled Job Type",
                {"method": ["like", f"%{sales_invoices_task_name}%"]},
                ["name", "method", "frequency"],
                for_update=True,
            )

            sales_invoices_task.frequency = self.sales_information_submission

            pos_invoices_task_name = send_pos_invoices_information.__name__

            pos_invoices_task: Document = frappe.get_doc(
                "Scheduled Job Type",
                {"method": ["like", f"%{pos_invoices_task_name}%"]},
                ["name", "method", "frequency"],
                for_update=True,
            )

            pos_invoices_task.frequency = self.sales_information_submission

            if self.sales_information_submission == "Cron":
                # Updates all sales related background tasks to use cron
                cron_format = self.sales_info_cron_format

                sales_invoices_task.cron_format = cron_format
                pos_invoices_task.cron_format = cron_format

            sales_invoices_task.save()
            pos_invoices_task.save()

        if self.stock_information_submission:
            stock_information_task_name = send_stock_information.__name__
            item_inventory_submission_task_name = (
                send_item_inventory_information.__name__
            )

            stock_information_task = frappe.get_doc(
                "Scheduled Job Type",
                {"method": ["like", f"%{stock_information_task_name}%"]},
                ["name", "method", "frequency"],
                for_update=True,
            )

            stock_information_task.frequency = self.stock_information_submission

            item_inventory_submission_task = frappe.get_doc(
                "Scheduled Job Type",
                {"method": ["like", f"%{item_inventory_submission_task_name}%"]},
                ["name", "method", "frequency"],
                for_update=True,
            )

            item_inventory_submission_task.frequency = self.stock_information_submission

            if self.stock_information_submission == "Cron":
                stock_information_task.cron_format = self.stock_info_cron_format
                item_inventory_submission_task.cron_format = self.stock_info_cron_format

            stock_information_task.save()
            item_inventory_submission_task.save()

        if self.purchase_information_submission:
            purchase_information_task_name = send_purchase_information.__name__

            purchase_information_task = frappe.get_doc(
                "Scheduled Job Type",
                {"method": ["like", f"%{purchase_information_task_name}%"]},
                ["name", "method", "frequency"],
                for_update=True,
            )

            purchase_information_task.frequency = self.purchase_information_submission

            if self.purchase_information_submission == "Cron":
                purchase_information_task.cron_format = self.purchase_info_cron_format

            purchase_information_task.save()

    def before_insert(self) -> None:
        """Before Insertion Hook"""
        route_path, last_request_date = get_route_path("DeviceVerificationReq")

        if route_path:
            url = f"{self.server_url}{route_path}"
            payload = {
                "tin": self.tin,
                "bhfId": self.bhfid,
                "dvcSrlNo": self.dvcsrlno,
            }

            integration_request = create_request_log(
                data=payload,
                service_name="etims",
                url=url,
                request_headers=None,
                is_remote_request=True,
            )

            try:
                response = asyncio.run(make_post_request(url, payload))

                if response["resultCd"] == "000":
                    self.communication_key = response["data"]["info"]["cmcKey"]

                    update_last_request_date(response["resultDt"], route_path)
                    update_integration_request(
                        integration_request.name,
                        "Completed",
                        output=f'{response["resultMsg"]}, {response["resultCd"]}',
                        error=None,
                    )

                else:
                    update_integration_request(
                        integration_request.name,
                        "Failed",
                        output=None,
                        error=f'{response["resultMsg"]}, {response["resultCd"]}',
                    )
                    handle_errors(
                        response, route_path, self.name, SETTINGS_DOCTYPE_NAME
                    )

            except aiohttp.client_exceptions.ClientConnectorError as error:
                self.error_title = "Connection failed during initialisation"

                etims_logger.exception(error, exc_info=True)
                frappe.log_error(
                    title=self.error_title,
                    message=error,
                    reference_doctype=SETTINGS_DOCTYPE_NAME,
                )
                update_integration_request(
                    integration_request.name,
                    "Failed",
                    output=None,
                    error=self.error_title,
                )
                frappe.throw(
                    "Connection failed",
                    error,
                    title=self.error_title,
                )

            except aiohttp.client_exceptions.ClientOSError as error:
                self.error_title = "Connection reset by peer"

                etims_logger.exception(error, exc_info=True)
                frappe.log_error(
                    title=self.error_title,
                    message=error,
                    reference_doctype=SETTINGS_DOCTYPE_NAME,
                )
                update_integration_request(
                    integration_request.name,
                    "Failed",
                    output=None,
                    error=self.error_title,
                )
                frappe.throw(
                    "Connection reset by peer",
                    error,
                    title=self.error_title,
                )

            except asyncio.exceptions.TimeoutError as error:
                self.error_title = "Timeout Error"

                etims_logger.exception(error, exc_info=True)
                frappe.log_error(
                    title=self.error_title,
                    message=error,
                    reference_doctype=SETTINGS_DOCTYPE_NAME,
                )
                update_integration_request(
                    integration_request.name,
                    "Failed",
                    output=None,
                    error=self.error_title,
                )
                frappe.throw("Timeout Encountered", error, title=self.error_title)
