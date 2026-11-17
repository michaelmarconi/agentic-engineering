"""Logging set-up: every module gets its logger from get_logger()."""

import logging
import os
from pathlib import Path

import structlog

DEFAULT_LOG_FILE = "var/log/stockroom.jsonl"


def configure() -> None:
    log_file = Path(os.environ.get("STOCKROOM_LOG_FILE", DEFAULT_LOG_FILE))
    log_file.parent.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, os.environ.get("STOCKROOM_LOG_LEVEL", "INFO").upper(), logging.INFO)
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.WriteLoggerFactory(file=log_file.open("a", encoding="utf-8")),
    )


def get_logger(name: str):
    return structlog.get_logger(name)
