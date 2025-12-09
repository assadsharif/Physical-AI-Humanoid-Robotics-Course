"""
Structured logging configuration for the application.

Provides setup function for consistent logging across modules.
"""

import logging
import sys
from typing import Optional
from config import settings


def setup_logging(name: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        name: Logger name (typically __name__ from calling module)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name or __name__)

    # Only configure if not already configured
    if not logger.handlers:
        # Set level
        level = getattr(logging, settings.LOG_LEVEL, logging.INFO)
        logger.setLevel(level)

        # Create formatter
        formatter = logging.Formatter(
            "[%(asctime)s] %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


# Default root logger
logger = setup_logging("app")
