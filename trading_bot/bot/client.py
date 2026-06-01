"""
client.py
---------
Low-level wrapper around the Binance Futures Testnet REST API.
Responsibilities:
  - Build and sign every request with HMAC-SHA256
  - Send the HTTP request via 'requests'
  - Log the raw request + response
  - Raise a clear BinanceAPIError on any API-level failure
"""

import hashlib
import hmac
import time
from typing import Any, Dict, Optional
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logging

# ------------------------------------------------------------------ #
# Constants
# ------------------------------------------------------------------ #
BASE_URL = "https://testnet.binancefuture.com"
RECV_WINDOW = 5000  # milliseconds Binance allows for request age

logger = setup_logging()


# ------------------------------------------------------------------ #
# Custom exception
# ------------------------------------------------------------------ #
class BinanceAPIError(Exception):
    """Raised when the Binance API returns an error response."""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(f"Binance API Error {code}: {message}")


# ------------------------------------------------------------------ #
# BinanceClient
# ------------------------------------------------------------------ #
class BinanceClient:
    """
    Wraps Binance Futures Testnet REST endpoints.
    Only the methods needed for this bot are implemented.
    """

    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            raise ValueError(
                "API key and secret must not be empty. "
                "Check your .env file."
            )
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        # Every request carries the API key header
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})
        logger.debug("BinanceClient initialised (testnet)")

    # -------------------------------------------------------------- #
    # Internal helpers
    # -------------------------------------------------------------- #

    def _timestamp(self) -> int:
        """Current UTC time in milliseconds."""
        return int(time.time() * 1000)

    def _sign(self, params: dict) -> str:
        """
        Create an HMAC-SHA256 signature from the query-string representation
        of params using the API secret as the key.
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return signature

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> dict:
        """
        Core request dispatcher.

        Args:
            method:   'GET' or 'POST'
            endpoint: e.g. '/fapi/v1/order'
            params:   query/body parameters
            signed:   if True, adds timestamp + signature (required for
                      account/order endpoints)

        Returns:
            Parsed JSON response as a dict.

        Raises:
            BinanceAPIError: API returned a non-2xx code or error body.
            requests.exceptions.RequestException: network-level failure.
        """
        params = params or {}

        if signed:
            server_time = self._request("GET", "/fapi/v1/time")["serverTime"]
            params["timestamp"] = server_time
            params["recvWindow"] = RECV_WINDOW
            params["signature"] = self._sign(params)

        url = BASE_URL + endpoint

        logger.debug(
            f"→ {method} {endpoint} | params: { {k: v for k, v in params.items() if k != 'signature'} }"
        )

        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method == "POST":
                response = self.session.post(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.ConnectionError:
            logger.error("Network error — cannot reach Binance Testnet. Check your internet connection.")
            raise
        except requests.exceptions.Timeout:
            logger.error("Request timed out after 10 seconds.")
            raise

        logger.debug(f"← HTTP {response.status_code} | body: {response.text[:500]}")

        # Parse JSON
        try:
            data = response.json()
        except Exception:
            logger.error(f"Could not parse API response as JSON: {response.text[:200]}")
            raise BinanceAPIError(-1, f"Non-JSON response: {response.text[:200]}")

        # Binance sends errors as {"code": <negative int>, "msg": "..."}
        if isinstance(data, dict) and "code" in data and data["code"] != 200:
            code = data["code"]
            msg = data.get("msg", "Unknown error")
            logger.error(f"Binance API error — code {code}: {msg}")
            raise BinanceAPIError(code, msg)

        return data

    # Public API methods

    def get_server_time(self) -> dict:
        """Ping the server and get server time (unsigned, no auth needed)."""
        return self._request("GET", "/fapi/v1/time")

    def get_exchange_info(self) -> dict:
        """Get trading rules and symbol information."""
        return self._request("GET", "/fapi/v1/exchangeInfo")

    def get_account(self) -> dict:
        """Get account information including balances (requires signing)."""
        return self._request("GET", "/fapi/v2/account", signed=True)

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> dict:
        """
        Place a new futures order.

        Args:
            symbol:        e.g. 'BTCUSDT'
            side:          'BUY' or 'SELL'
            order_type:    'MARKET', 'LIMIT', or 'STOP_MARKET'
            quantity:      amount to trade
            price:         required for LIMIT orders
            stop_price:    required for STOP_MARKET orders
            time_in_force: 'GTC' (Good Till Cancel) by default for LIMIT

        Returns:
            Raw order response dict from Binance.
        """
        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price is required for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        elif order_type == "STOP_MARKET":
            if stop_price is None:
                raise ValueError("stopPrice is required for STOP_MARKET orders.")
            params["stopPrice"] = stop_price

        logger.info(
            f"Placing {order_type} {side} order | "
            f"Symbol: {symbol} | Qty: {quantity}"
            + (f" | Price: {price}" if price else "")
            + (f" | StopPrice: {stop_price}" if stop_price else "")
        )

        response = self._request("POST", "/fapi/v1/order", params=params, signed=True)
        logger.info(f"Order placed successfully | orderId: {response.get('orderId')}")
        return response
