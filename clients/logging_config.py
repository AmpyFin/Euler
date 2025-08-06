"""
Logging configuration for Euler system.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging() -> logging.Logger:
    """
    Set up consolidated logging to system.log.

    Returns:
        Root logger configured for system-wide logging
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Remove any existing handlers
    root_logger.handlers.clear()

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    # Create file handler for system.log
    log_path = os.path.join("logs", "system.log")
    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)

    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    return root_logger


# Initialize logging system
logger = setup_logging()

# Create component loggers that will inherit from root logger
fetch_logger = logging.getLogger("FetchClient")
process_logger = logging.getLogger("ProcessingClient")
inference_logger = logging.getLogger("InferenceClient")
system_logger = logging.getLogger("SystemClient")
