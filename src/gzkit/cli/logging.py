"""Structured logging configuration — CLI adapter layer.

Configures structlog with:
- 4 verbosity levels tied to CLI flags (quiet, normal, verbose, debug)
- JSON file output for machine consumption
- Human-readable console output for interactive use
- Correlation IDs bound at command entry and propagated through the call stack

Core layer code uses structlog binding only (get_logger, bind, msg).
All processor/formatter configuration lives here in the CLI layer.
"""

from __future__ import annotations

import logging
import sys
import uuid
from pathlib import Path
from typing import Any, Literal, TextIO

import structlog

from gzkit.color_env import should_disable_color, should_force_terminal

Verbosity = Literal["quiet", "normal", "verbose", "debug"]

VERBOSITY_TO_LEVEL: dict[str, int] = {
    "quiet": logging.ERROR,
    "normal": logging.INFO,
    "verbose": logging.DEBUG,
    "debug": logging.DEBUG,
}


def _add_correlation_id(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Processor that ensures a correlation_id is present."""
    if "correlation_id" not in event_dict:
        event_dict["correlation_id"] = _current_correlation_id()
    return event_dict


_correlation_id: str = ""


def _current_correlation_id() -> str:
    """Return the active correlation ID, generating one if needed."""
    global _correlation_id  # noqa: PLW0603
    if not _correlation_id:
        _correlation_id = uuid.uuid4().hex[:12]
    return _correlation_id


def bind_correlation_id(correlation_id: str | None = None) -> str:
    """Bind a correlation ID for the current command invocation.

    Call this once at command entry. All subsequent log events will
    carry this ID.

    Returns:
        The correlation ID that was bound.

    """
    global _correlation_id  # noqa: PLW0603
    _correlation_id = correlation_id or uuid.uuid4().hex[:12]
    return _correlation_id


def _stream_wants_color(stream: TextIO | None) -> bool:
    """Return True when log output to *stream* should be coloured.

    *stream* is None when the process has no stderr (pythonw, a detached launch).
    """
    if stream is None or should_disable_color():
        return False
    return should_force_terminal() or stream.isatty()


def configure_logging(
    verbosity: Verbosity = "normal",
    log_file: Path | None = None,
    *,
    console_stream: TextIO | None = None,
) -> None:
    """Single configuration entry point for structured logging.

    Args:
        verbosity: One of quiet, normal, verbose, debug. Maps to log
            levels and controls what reaches the console.
        log_file: Optional path for JSON file output. When set, all log
            events are written as JSON lines regardless of verbosity.
        console_stream: Override for console output stream (default stderr).

    """
    level = VERBOSITY_TO_LEVEL.get(verbosity, logging.INFO)

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        _add_correlation_id,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if verbosity == "debug":
        shared_processors.append(structlog.processors.CallsiteParameterAdder())

    # Configure stdlib logging for structlog integration
    logging.basicConfig(
        format="%(message)s",
        stream=console_stream or sys.stderr,
        level=level,
        force=True,
    )

    handlers: list[logging.Handler] = []

    # JSON file handler — writes all events regardless of verbosity
    if log_file is not None:
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        handlers.append(file_handler)

    # Wire up structlog
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=False,
    )

    # Console formatter — human-readable. Colour only a terminal, honouring
    # NO_COLOR / FORCE_COLOR as the CLI console does, so captured stderr stays
    # plain. Where colour is wanted, take structlog's own default: forcing
    # colors=True raises SystemError on Windows without colorama, which is not a
    # runtime dependency (GHI #1010).
    renderer = (
        structlog.dev.ConsoleRenderer()
        if verbosity != "quiet" and _stream_wants_color(console_stream or sys.stderr)
        else structlog.dev.ConsoleRenderer(colors=False)
    )
    console_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    # JSON formatter — for file output
    json_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.processors.JSONRenderer(),
        ],
    )

    # Apply formatters to stdlib root logger
    root_logger = logging.getLogger()
    # Clear existing handlers to avoid duplication
    root_logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(console_stream or sys.stderr)
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler with JSON
    for handler in handlers:
        handler.setFormatter(json_formatter)
        root_logger.addHandler(handler)

    root_logger.setLevel(logging.DEBUG if log_file else level)
