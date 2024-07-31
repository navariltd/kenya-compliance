from __future__ import annotations

import asyncio
from typing import Callable, Literal
from urllib import parse

import aiohttp

import frappe
from frappe.integrations.utils import create_request_log
from frappe.model.document import Document

from ..logger import etims_logger
from ..utils import make_post_request, update_last_request_date


class BaseEndpointsBuilder:
    """Abstract Endpoints Builder class"""

    def __init__(self) -> None:
        self.integration_request: str | Document | None = None
        self.error: str | Exception | None = None
        self._observers: list[ErrorObserver] = []
        self.doctype: str | Document | None = None
        self.document_name: str | None = None

    def attach(self, observer: ErrorObserver) -> None:
        """Attach an observer

        Args:
            observer (AbstractObserver): The observer to attach
        """
        self._observers.append(observer)

    def notify(self) -> None:
        """Notify all attached observers."""
        for observer in self._observers:
            observer.update(self)


class ErrorObserver:
    """Error observer class."""

    def update(self, notifier: BaseEndpointsBuilder) -> None:
        """Reacts to event from notifier

        Args:
            notifier (AbstractEndpointsBuilder): The event notifier object
        """
        if notifier.error:
            # TODO: Check why integration log is never updated
            update_integration_request(
                notifier.integration_request.name,
                status="Failed",
                output=None,
                error=notifier.error,
            )
            etims_logger.exception(notifier.error, exc_info=True)
            frappe.log_error(
                title="Fatal Error",
                message=notifier.error,
                reference_doctype=notifier.doctype,
                reference_name=notifier.document_name,
            )
            frappe.throw(
                """A Fatal Error was Encountered.
                Please check the Error Log for more details""",
                notifier.error,
                title="Fatal Error",
            )


# TODO: Does this class need to be singleton?
class EndpointsBuilder(BaseEndpointsBuilder):
    """
    Base Endpoints Builder class.
    This class harbours common functionalities when communicating with etims servers
    """

    def __init__(self) -> None:
        super().__init__()

        self._url: str | None = None
        self._payload: dict | None = None
        self._headers: dict | None = None
        self._success_callback_handler: Callable | None = None
        self._error_callback_handler: Callable | None = None

        self.attach(ErrorObserver())

    @property
    def url(self) -> str | None:
        """The remote address

        Returns:
            str | None: The remote address
        """
        return self._url

    @url.setter
    def url(self, new_url: str) -> None:
        self._url = new_url

    @property
    def payload(self) -> dict | None:
        """The request data

        Returns:
            dict | None: The request data
        """
        return self._payload

    @payload.setter
    def payload(self, new_payload: dict) -> None:
        self._payload = new_payload

    @property
    def headers(self) -> dict | None:
        """The request headers

        Returns:
            dict | None: The request headers
        """
        return self._headers

    @headers.setter
    def headers(self, new_headers: dict) -> None:
        self._headers = new_headers

    @property
    def success_callback(self) -> Callable | None:
        """Function that handles success responses.
        The function must have at least one argument which will be the response received.

        Returns:
            Callable | None: The function that handles success responses
        """
        return self._success_callback_handler

    @success_callback.setter
    def success_callback(self, callback: Callable) -> None:
        self._success_callback_handler = callback

    @property
    def error_callback(self) -> Callable | None:
        """The function that handles error responses

        Returns:
            Callable | None: The function that handles error responses
        """
        return self._error_callback_handler

    @error_callback.setter
    def error_callback(
        self,
        callback: Callable[[dict[str, str | int | None] | str, str, str, str], None],
    ) -> None:
        self._error_callback_handler = callback

    def make_remote_call(
        self, doctype: Document | str | None = None, document_name: str | None = None
    ) -> None:
        """The function that handles the communication to the remote servers.

        Args:
            doctype (Document | str | None, optional): The doctype calling this object. Defaults to None.
            document_name (str | None, optional): The name of the doctype calling this object. Defaults to None.

        Returns:
            Any: The response received.
        """
        if (
            self._url is None
            or self._headers is None
            or self._success_callback_handler is None
            or self._error_callback_handler is None
        ):
            frappe.throw(
                """Please check that all required request parameters are supplied. These include the headers, and success and error callbacks""",
                frappe.MandatoryError,
                title="Setup Error",
                is_minimizable=True,
            )

        self.doctype, self.document_name = doctype, document_name
        parsed_url = parse.urlparse(self._url)
        route_path = f"/{parsed_url.path.split('/')[-1]}"

        self.integration_request = create_request_log(
            data=self._payload,
            is_remote_request=True,
            service_name="etims",
            request_headers=self._headers,
            url=self._url,
            reference_docname=document_name,
            reference_doctype=doctype,
        )

        try:
            response = asyncio.run(
                make_post_request(self._url, self._payload, self._headers)
            )

            if response["resultCd"] == "000":
                # Success callback handler here
                self._success_callback_handler(response)

                update_last_request_date(response["resultDt"], route_path)
                update_integration_request(
                    self.integration_request.name,
                    status="Completed",
                    output=response["resultMsg"],
                    error=None,
                )

            else:
                update_integration_request(
                    self.integration_request.name,
                    status="Failed",
                    output=None,
                    error=response["resultMsg"],
                )
                # Error callback handler here
                self._error_callback_handler(
                    response,
                    url=route_path,
                    doctype=doctype,
                    document_name=document_name,
                )

        except (
            aiohttp.client_exceptions.ClientConnectorError,
            aiohttp.client_exceptions.ClientOSError,
            asyncio.exceptions.TimeoutError,
        ) as error:
            self.error = error
            self.notify()


def update_integration_request(
    integration_request: str,
    status: Literal["Completed", "Failed"],
    output: str | None = None,
    error: str | None = None,
) -> None:
    """Updates the given integration request record

    Args:
        integration_request (str): The provided integration request
        status (Literal[&quot;Completed&quot;, &quot;Failed&quot;]): The new status of the request
        output (str | None, optional): The response message, if any. Defaults to None.
        error (str | None, optional): The error message, if any. Defaults to None.
    """
    doc = frappe.get_doc("Integration Request", integration_request, for_update=True)
    doc.status = status
    doc.error = error
    doc.output = output

    doc.save(ignore_permissions=True)
