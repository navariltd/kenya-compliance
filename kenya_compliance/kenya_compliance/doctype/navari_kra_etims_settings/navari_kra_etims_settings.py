# Copyright (c) 2024, Navari Ltd and contributors
# For license information, please see license.txt

import asyncio

import aiohttp
import frappe
from frappe.integrations.utils import create_request_log
from frappe.model.document import Document

from ...apis.api_builder import update_integration_request
from ...background_tasks.tasks import send_sales_invoices_information
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
            task_name = send_sales_invoices_information.__name__

            task: Document = frappe.get_doc(
                "Scheduled Job Type",
                {"method": ["like", f"%{task_name}%"]},
                ["name", "method", "frequency"],
                for_update=True,
            )

            task.frequency = self.sales_information_submission
            task.save()

        if self.stock_information_submission:
            pass

        if self.purchase_information_submission:
            pass

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
                etims_logger.exception(error, exc_info=True)
                frappe.log_error(
                    title="Connection failed during initialisation",
                    message=error,
                    reference_doctype=SETTINGS_DOCTYPE_NAME,
                )
                frappe.throw(
                    "Connection failed",
                    error,
                    title="Connection Error",
                )

            except aiohttp.client_exceptions.ClientOSError as error:
                etims_logger.exception(error, exc_info=True)
                frappe.log_error(
                    title="Connection reset by peer",
                    message=error,
                    reference_doctype=SETTINGS_DOCTYPE_NAME,
                )
                frappe.throw(
                    "Connection reset by peer",
                    error,
                    title="Connection Error",
                )

            except asyncio.exceptions.TimeoutError as error:
                etims_logger.exception(error, exc_info=True)
                frappe.log_error(
                    title="Timeout Error",
                    message=error,
                    reference_doctype=SETTINGS_DOCTYPE_NAME,
                )
                frappe.throw("Timeout Encountered", error, title="Timeout Error")

            finally:
                update_integration_request(
                    integration_request.name,
                    "Failed",
                    output=None,
                    error="Exception Encountered",
                )
