"""
Structured logging setup using structlog for JSON event logs.
"""

from __future__ import annotations

import logging
import sys
from typing import Any, Dict

import structlog


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure stdlib logging + structlog processors.
    """
    timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        stream=sys.stdout,
        level=level,
        format="%(message)s",
    )


def get_logger(name: str, **context: Any) -> structlog.stdlib.BoundLogger:
    """
    Get a logger bound with optional static context.
    """
    logger = structlog.get_logger(name)
    if context:
        return logger.bind(**context)
    return logger

