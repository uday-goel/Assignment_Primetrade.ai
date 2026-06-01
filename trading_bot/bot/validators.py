"""
validators.py
-------------
Validates all user inputs BEFORE any API call is made.
Raises ValueError with a clear message if something is wrong.
This keeps the client and CLI layers clean.
"""

from typing import Optional


# Allowed values — easy to extend later
VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    """
    Symbol must be a non-empty string of letters/digits (e.g. BTCUSDT).
    Returns the symbol uppercased.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty. Example: BTCUSDT")
    if not symbol.isalnum():
        raise ValueError(
            f"Symbol '{symbol}' contains invalid characters. "
            "Use only letters and digits (e.g. BTCUSDT)."
        )
    return symbol


def validate_side(side: str) -> str:
    """Side must be BUY or SELL (case-insensitive)."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(
            f"Side '{side}' is not valid. Choose from: {', '.join(VALID_SIDES)}"
        )
    return side


def validate_order_type(order_type: str) -> str:
    """Order type must be one of the allowed types (case-insensitive)."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Order type '{order_type}' is not valid. "
            f"Choose from: {', '.join(VALID_ORDER_TYPES)}"
        )
    return order_type


def validate_quantity(quantity: str) -> float:
    """
    Quantity must be a positive number.
    Accepts both int and float strings (e.g. '0.001', '5').
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(
            f"Quantity '{quantity}' is not a valid number. Example: 0.001"
        )
    if qty <= 0:
        raise ValueError(
            f"Quantity must be greater than 0. Got: {qty}"
        )
    return qty


def validate_price(price: Optional[str], order_type: str) -> Optional[float]:
    """
    Price is required for LIMIT and STOP_MARKET orders.
    For MARKET orders it is ignored (returns None).
    """
    if order_type == "MARKET":
        if price is not None:
            # Not an error — just silently ignore it for MARKET
            pass
        return None  # MARKET orders don't use a price

    # LIMIT / STOP_MARKET — price is required
    if price is None or str(price).strip() == "":
        raise ValueError(
            f"Price is required for {order_type} orders. "
            "Provide it with --price."
        )
    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValueError(
            f"Price '{price}' is not a valid number. Example: 30000.50"
        )
    if p <= 0:
        raise ValueError(f"Price must be greater than 0. Got: {p}")
    return p


def validate_stop_price(stop_price: Optional[str], order_type: str) -> Optional[float]:
    """Stop price is required for STOP_MARKET orders."""
    if order_type != "STOP_MARKET":
        return None
    if stop_price is None or str(stop_price).strip() == "":
        raise ValueError(
            "Stop price (--stop-price) is required for STOP_MARKET orders."
        )
    try:
        sp = float(stop_price)
    except (ValueError, TypeError):
        raise ValueError(
            f"Stop price '{stop_price}' is not a valid number. Example: 29000.00"
        )
    if sp <= 0:
        raise ValueError(f"Stop price must be greater than 0. Got: {sp}")
    return sp


def validate_all(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: Optional[str] = None,
    stop_price: Optional[str] = None,
) -> dict:
    """
    Run all validators and return a clean dict of validated values.
    Raises ValueError on the first problem found.
    """
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_order_type = validate_order_type(order_type)
    validated_quantity = validate_quantity(quantity)
    validated_price = validate_price(price, validated_order_type)
    validated_stop_price = validate_stop_price(stop_price, validated_order_type)

    return {
        "symbol": validated_symbol,
        "side": validated_side,
        "order_type": validated_order_type,
        "quantity": validated_quantity,
        "price": validated_price,
        "stop_price": validated_stop_price,
    }
