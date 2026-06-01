"""
orders.py
---------
Business-logic layer that sits between the CLI and the raw BinanceClient.
Responsibilities:
  - Accept validated inputs
  - Call the appropriate client method
  - Format and return a human-readable result summary
"""

from typing import Optional

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging

logger = setup_logging()


def place_order(
    client: BinanceClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None,
) -> dict:
    """
    Place an order using the provided client and return a structured result.

    Returns a dict with:
        success (bool)  — whether the order was accepted
        data    (dict)  — raw API response on success
        error   (str)   — error message on failure
    """
    logger.debug(
        f"orders.place_order called | {order_type} {side} {symbol} "
        f"qty={quantity} price={price} stop_price={stop_price}"
    )

    try:
        response = client.place_order(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
        )
        logger.debug(f"Raw API response: {response}")
        return {"success": True, "data": response, "error": None}

    except BinanceAPIError as e:
        logger.error(f"BinanceAPIError while placing order: {e}")
        return {"success": False, "data": None, "error": str(e)}

    except Exception as e:
        logger.error(f"Unexpected error while placing order: {e}", exc_info=True)
        return {"success": False, "data": None, "error": f"Unexpected error: {e}"}


def format_order_response(response_data: dict) -> str:
    """
    Convert a raw Binance order response dict into a readable multi-line string.
    Safe — handles missing fields gracefully.
    """
    lines = [
        "─" * 50,
        "          ORDER RESPONSE DETAILS",
        "─" * 50,
        f"  Order ID      : {response_data.get('orderId', 'N/A')}",
        f"  Client Ord ID : {response_data.get('clientOrderId', 'N/A')}",
        f"  Symbol        : {response_data.get('symbol', 'N/A')}",
        f"  Side          : {response_data.get('side', 'N/A')}",
        f"  Type          : {response_data.get('type', 'N/A')}",
        f"  Status        : {response_data.get('status', 'N/A')}",
        f"  Quantity      : {response_data.get('origQty', 'N/A')}",
        f"  Executed Qty  : {response_data.get('executedQty', 'N/A')}",
        f"  Avg Price     : {response_data.get('avgPrice', 'N/A')}",
        f"  Price         : {response_data.get('price', 'N/A')}",
        f"  Time in Force : {response_data.get('timeInForce', 'N/A')}",
        "─" * 50,
    ]
    return "\n".join(lines)
