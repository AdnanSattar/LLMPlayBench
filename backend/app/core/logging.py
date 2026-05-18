"""
Logging configuration.

Author: Adnan Sattar
Email: adnansattar09@gmail.com
GitHub: https://github.com/AdnanSattar
LinkedIn: https://www.linkedin.com/in/adnansattar09/
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path

from loguru import logger as base_logger

from .config import settings


def setup_logging():
    """Configure Loguru logger with production-ready settings."""

    # Clear any existing handlers
    base_logger.remove()

    # Log format
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level> | "
        "{extra}"
    )

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure console logging
    log_level = settings.LOG_LEVEL or "INFO"
    base_logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    # Configure file logging with rotation, retention, and compression
    log_filepath = logs_dir / "llmplaybench_{time}.log"
    base_logger.add(
        str(log_filepath),
        rotation="10 MB",  # Rotate when file reaches 10 MB
        retention="1 week",  # Keep logs for 1 week
        compression="zip",  # Compress rotated logs
        format=log_format,
        level=log_level,
        backtrace=True,
        diagnose=True,
        enqueue=True,  # Thread-safe logging
    )

    # Add structured logging format for JSON output
    structured_log_filepath = logs_dir / "structured_{time}.json"
    base_logger.add(
        str(structured_log_filepath),
        rotation="10 MB",
        retention="1 week",
        compression="zip",
        format="{message}",
        level=log_level,
        serialize=True,  # Enable JSON serialization
        enqueue=True,
    )

    # Add request context to all logs
    contextual_logger = base_logger.bind(service="llmplaybench-api")

    # Log startup message
    contextual_logger.info("Logging initialized with level: {}", log_level)

    return contextual_logger


# Create and configure the application logger
app_logger = setup_logging()


def get_request_logger(request_id=None):
    """
    Get a contextualized logger for request handling.

    Args:
        request_id: Unique ID for the request

    Returns:
        A logger instance with request context
    """
    if request_id:
        return app_logger.bind(request_id=request_id)
    return app_logger
