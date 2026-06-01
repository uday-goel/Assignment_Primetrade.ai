"""
logging_config.py
-----------------
Sets up structured logging for the trading bot.
- Writes detailed logs to logs/trading_bot.log
- Shows clean, color-coded output in the terminal
"""

import logging
import os
from datetime import datetime


def setup_logging() -> logging.Logger:
    """
    Configure and return the application logger.
    Creates a 'logs/' directory if it doesn't exist.
    """
    # Make sure the logs folder exists
    os.makedirs("logs", exist_ok=True)

    # Create a logger named 'trading_bot'
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)  # Capture everything DEBUG and above

    # FILE HANDLER — writes detailed logs to logs/trading_bot.log

    log_filename = os.path.join("logs", "trading_bot.log")
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # Log everything to the file
    file_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(module)-18s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_format)

    # CONSOLE HANDLER — shows INFO and above in the terminal
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        fmt="%(levelname)-8s | %(message)s"
    )
    console_handler.setFormatter(console_format)

    # Attach both handlers (avoid adding duplicates if called multiple times)
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    logger.info(f"Logging initialised — writing to '{log_filename}'")
    return logger
