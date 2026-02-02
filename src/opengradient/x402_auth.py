"""
X402 Authentication handler for httpx streaming requests.

This module provides an httpx Auth class that handles x402 payment protocol
authentication for streaming responses.
"""

from typing import Generator, Optional

import httpx
from eth_account.account import LocalAccount
from x402.clients.base import x402Client
from x402.types import x402PaymentRequiredResponse


class X402Auth(httpx.Auth):
    """
    httpx Auth handler for x402 payment protocol.

    This class implements the httpx Auth interface to handle 402 Payment Required
    responses by automatically creating and attaching payment headers.

    Example:
        async with httpx.AsyncClient(auth=X402Auth(account=wallet_account)) as client:
            response = await client.get("https://api.example.com/paid-resource")
    """

    requires_response_body = True

    def __init__(
        self,
        account: LocalAccount,
        max_value: Optional[int] = None,
        network_filter: Optional[str] = None,
        scheme_filter: Optional[str] = None,
    ):
        """
        Initialize X402Auth with an Ethereum account for signing payments.

        Args:
            account: eth_account LocalAccount instance for signing payments
            max_value: Optional maximum allowed payment amount in base units
            network_filter: Optional network filter for selecting payment requirements
            scheme_filter: Optional scheme filter for selecting payment requirements
        """
        self._account = account
        self._max_value = max_value
        self._network_filter = network_filter
        self._scheme_filter = scheme_filter
        self._x402_client = x402Client(
            account,
            max_value=max_value,
            network_filter=network_filter,
            scheme_filter=scheme_filter,
        )

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """
        Implement the auth flow for x402 payment handling.

        This method yields the initial request, and if a 402 response is received,
        it creates a payment header and retries the request.

        Args:
            request: The initial httpx Request

        Yields:
            httpx.Request objects (initial and retry with payment header)
        """
        # Send the initial request
        response = yield request

        # If not a 402, we're done
        if response.status_code != 402:
            return

        # Handle 402 Payment Required
        try:
            data = response.json()
            payment_response = x402PaymentRequiredResponse(**data)

            # Select payment requirements
            selected_requirements = self._x402_client.select_payment_requirements(
                payment_response.accepts
            )

            # Create payment header
            payment_header = self._x402_client.create_payment_header(
                selected_requirements, payment_response.x402_version
            )

            # Add payment header and retry
            request.headers["X-Payment"] = payment_header
            request.headers["Access-Control-Expose-Headers"] = "X-Payment-Response"

            yield request

        except Exception:
            # If payment handling fails, just return the original 402 response
            return
