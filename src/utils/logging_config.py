"""Centralized logging configuration for the application."""

import logging
import structlog

from src.utils.config import settings


def configure_logging() -> None:
    """Configure structlog for the entire application.

    This must be called before any logger is created to ensure
    consistent logging behavior across all modules.
    """
    # Configure stdlib logging first
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(message)s"
    )

    # Configure structlog with processors that handle keyword arguments
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Configure logging immediately on import
configure_logging()

# Create a default logger for use in modules
logger = structlog.get_logger()
