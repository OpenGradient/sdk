"""
X402 Authentication handler for httpx streaming requests.

This module provides an httpx Auth class that handles x402 payment protocol
authentication for streaming responses.
"""

import logging
import typing

import httpx
from x402.clients.base import x402Client
from x402.types import PaymentRequirements, x402PaymentRequiredResponse


class X402Auth(httpx.Auth):
    """
    httpx Auth handler for x402 payment protocol.

    This class implements the httpx Auth interface to handle 402 Payment Required
    responses by automatically creating and attaching payment headers.
    """

    requires_response_body = True

    def __init__(
        self,
        account: typing.Any,
        max_value: typing.Optional[int] = None,
        payment_requirements_selector: typing.Optional[
            typing.Callable[
                [
                    list[PaymentRequirements],
                    typing.Optional[str],
                    typing.Optional[str],
                    typing.Optional[int],
                ],
                PaymentRequirements,
            ]
        ] = None,
        network_filter: typing.Optional[str] = None,
        scheme_filter: typing.Optional[str] = None,
    ):
        self.x402_client = x402Client(
            account,
            max_value=max_value,
            payment_requirements_selector=payment_requirements_selector,  # type: ignore
        )
        self.network_filter = network_filter
        self.scheme_filter = scheme_filter

    async def async_auth_flow(self, request: httpx.Request) -> typing.AsyncGenerator[httpx.Request, httpx.Response]:
        response = yield request

        if response.status_code == 402:
            try:
                await response.aread()
                data = response.json()

                payment_response = x402PaymentRequiredResponse(**data)

                selected_requirements = self.x402_client.select_payment_requirements(
                    payment_response.accepts,
                    self.network_filter,
                    self.scheme_filter,
                )

                payment_header = self.x402_client.create_payment_header(
                    selected_requirements, 
                    payment_response.x402_version
                )

                request.headers["X-Payment"] = payment_header
                request.headers["Access-Control-Expose-Headers"] = "X-Payment-Response"
                yield request

            except Exception as e:
                logging.error(f"X402Auth: Error handling payment: {e}")
                return