"""
cli.py
Command-Line Interface entry point for the Trading Bot.

Usage examples:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 30000
  python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 28000

Run  python cli.py --help  to see all options.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceClient, BinanceAPIError
from bot.logging_config import setup_logging
from bot.orders import place_order, format_order_response
from bot.validators import validate_all

# Bootstrap

# Load environment variables from .env file (if it exists)
load_dotenv()

logger = setup_logging()

# CLI argument parser

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet — Simple Trading Bot",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python cli.py --symbol BTCUSDT --side BUY  --type MARKET --quantity 0.001\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type LIMIT  --quantity 0.001 --price 30000\n"
            "  python cli.py --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 28000\n"
        ),
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol, e.g. BTCUSDT",
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        type=str.upper,
        help="Order side: BUY or SELL",
    )
    parser.add_argument(
        "--type",
        dest="order_type",
        required=True,
        choices=["MARKET", "LIMIT", "STOP_MARKET"],
        type=str.upper,
        help="Order type: MARKET, LIMIT, or STOP_MARKET",
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Quantity to trade, e.g. 0.001",
    )
    parser.add_argument(
        "--price",
        default=None,
        help="Limit price (required for LIMIT orders), e.g. 30000",
    )
    parser.add_argument(
        "--stop-price",
        dest="stop_price",
        default=None,
        help="Stop trigger price (required for STOP_MARKET orders), e.g. 28000",
    )

    return parser

# Pretty-print helpers

def print_order_summary(params: dict) -> None:
    """Print a box showing what we're about to send."""
    print()
    print("─" * 50)
    print("          ORDER REQUEST SUMMARY")
    print("─" * 50)
    print(f"  Symbol     : {params['symbol']}")
    print(f"  Side       : {params['side']}")
    print(f"  Type       : {params['order_type']}")
    print(f"  Quantity   : {params['quantity']}")
    if params.get("price"):
        print(f"  Price      : {params['price']}")
    if params.get("stop_price"):
        print(f"  Stop Price : {params['stop_price']}")
    print("─" * 50)
    print()


def print_success(order_data: dict) -> None:
    print()
    print(format_order_response(order_data))
    print()
    print("  ✅  Order placed SUCCESSFULLY!")
    print()


def print_failure(error_msg: str) -> None:
    print()
    print("─" * 50)
    print("  ❌  Order FAILED")
    print(f"  Error: {error_msg}")
    print("─" * 50)
    print()

# Main

def main():
    parser = build_parser()
    args = parser.parse_args()

    # Load API credentials from environment 
    api_key = os.getenv("BINANCE_TESTNET_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET", "").strip()

    if not api_key or not api_secret:
        print()
        print("ERROR: API credentials not found.")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET")
        print()
        logger.error("Missing API credentials — BINANCE_TESTNET_API_KEY / BINANCE_TESTNET_API_SECRET not set.")
        sys.exit(1)

    # Validate inputs 
    logger.info(
        f"Received CLI args | symbol={args.symbol} side={args.side} "
        f"type={args.order_type} qty={args.quantity} "
        f"price={args.price} stop_price={args.stop_price}"
    )

    try:
        validated = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
        )
    except ValueError as e:
        print()
        print(f"INPUT ERROR: {e}")
        print()
        logger.error(f"Input validation failed: {e}")
        sys.exit(1)

    # Show the user what we're about to do 
    print_order_summary(validated)

    # Create the Binance client 
    try:
        client = BinanceClient(api_key=api_key, api_secret=api_secret)
    except ValueError as e:
        print(f"CLIENT ERROR: {e}")
        logger.error(f"Failed to create BinanceClient: {e}")
        sys.exit(1)

    # Place the order
    result = place_order(
        client=client,
        symbol=validated["symbol"],
        side=validated["side"],
        order_type=validated["order_type"],
        quantity=validated["quantity"],
        price=validated["price"],
        stop_price=validated["stop_price"],
    )

    # Print outcome
    if result["success"]:
        print_success(result["data"])
        logger.info("CLI session completed successfully.")
        sys.exit(0)
    else:
        print_failure(result["error"])
        logger.error(f"CLI session ended with order failure: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
