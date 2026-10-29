"""Structured logging configuration — CLI adapter layer, on stdlib ``logging``.

Configures:
- 4 verbosity levels tied to CLI flags (quiet, normal, verbose, debug)
- JSON file output for machine consumption
- Human-readable console output for interactive use
- Correlation IDs bound at command entry and carried by every record

Core layer code logs through stdlib ``logging`` only: ``logging.getLogger(name)``,
with an event name as the message and its fields in ``extra=``. All handler and
formatter configuration lives here in the CLI layer. structlog did this until RO-9
tranche 6 (operator, by selection: "Replace with stdlib (Rec.)").
"""

import json
import logging
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, TextIO

from gzkit.color_env import should_disable_color, should_force_terminal

Verbosity = Literal["quiet", "normal", "verbose", "debug"]

# docs/design/cli-standards-v3.md § Verbosity Levels (canonical per ADR-0.0.4).
VERBOSITY_TO_LEVEL: dict[Verbosity, int] = {
    "quiet": logging.ERROR,
    "normal": logging.WARNING,
    "verbose": logging.INFO,
    "debug": logging.DEBUG,
}

#: Every attribute a bare ``LogRecord`` carries; anything else on a record came in
#: through ``extra=`` and is one of the event's fields.
_RECORD_ATTRIBUTES = frozenset(
    vars(logging.LogRecord("", 0, "", 0, "", None, None)).keys() | {"message", "asctime"}
)
_CALLSITE = ("filename", "funcName", "lineno")
_LEVEL_STYLES = {
    logging.DEBUG: "\x1b[2m",
    logging.INFO: "\x1b[32m",
    logging.WARNING: "\x1b[33m",
    logging.ERROR: "\x1b[31m",
    logging.CRITICAL: "\x1b[1;31m",
}
_RESET = "\x1b[0m"

_correlation_id: str = ""


def _current_correlation_id() -> str:
    """Return the active correlation ID, generating one if needed."""
    global _correlation_id  # noqa: PLW0603
    if not _correlation_id:
        _correlation_id = uuid.uuid4().hex[:12]
    return _correlation_id


def bind_correlation_id(correlation_id: str | None = None) -> str:
    """Bind a correlation ID for the current command invocation.

    Call this once at command entry. All subsequent log records will
    carry this ID.

    Returns:
        The correlation ID that was bound.

    """
    global _correlation_id  # noqa: PLW0603
    _correlation_id = correlation_id or uuid.uuid4().hex[:12]
    return _correlation_id


def _stamp_correlation_id(record: logging.LogRecord) -> bool:
    """Stamp the active correlation ID on a record that does not carry one.

    Returns:
        Always True: the filter adds a field and never drops a record.

    """
    if not hasattr(record, "correlation_id"):
        record.correlation_id = _current_correlation_id()
    return True


def _fields(record: logging.LogRecord) -> dict[str, object]:
    """Return the record's event fields: what ``extra=`` added, the correlation ID included."""
    return {k: v for k, v in vars(record).items() if k not in _RECORD_ATTRIBUTES}


def _timestamp(record: logging.LogRecord) -> str:
    return datetime.fromtimestamp(record.created, tz=UTC).isoformat()


class _JsonFormatter(logging.Formatter):
    """One JSON object per record: event, level, timestamp, logger and the event's fields."""

    def __init__(self, *, callsite: bool) -> None:
        super().__init__()
        self._callsite = callsite

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "event": record.getMessage(),
            "level": record.levelname.lower(),
            "timestamp": _timestamp(record),
            "logger": record.name,
            **_fields(record),
        }
        if self._callsite:
            payload.update({key: getattr(record, key) for key in _CALLSITE})
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            payload["stack"] = self.formatStack(record.stack_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


class _ConsoleFormatter(logging.Formatter):
    """``<timestamp> [<level>] <event> key=value ...``, the level styled only on request."""

    def __init__(self, *, color: bool, callsite: bool) -> None:
        super().__init__()
        self._color = color
        self._callsite = callsite

    def format(self, record: logging.LogRecord) -> str:
        level = f"[{record.levelname.lower():<8}]"
        if self._color:
            level = f"{_LEVEL_STYLES.get(record.levelno, '')}{level}{_RESET}"
        fields = {k: v for k, v in _fields(record).items() if k != "correlation_id"}
        if self._callsite:
            fields.update({key: getattr(record, key) for key in _CALLSITE})
        pairs = " ".join(f"{key}={value}" for key, value in fields.items())
        line = " ".join(
            part for part in (_timestamp(record), level, record.getMessage(), pairs) if part
        )
        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)
        if record.stack_info:
            line += "\n" + self.formatStack(record.stack_info)
        return line


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
        log_file: Optional path for JSON file output. When set, every
            record is written as a JSON line regardless of verbosity.
        console_stream: Override for console output stream (default stderr).

    """
    level = VERBOSITY_TO_LEVEL.get(verbosity, logging.INFO)
    stream = console_stream or sys.stderr
    callsite = verbosity == "debug"
    correlation = _stamp_correlation_id

    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.close()
    root_logger.handlers.clear()

    # Colour only a terminal, honouring NO_COLOR / FORCE_COLOR as the CLI console
    # does, so captured stderr stays plain. The styling is plain ANSI, which needs
    # no colorama on Windows (GHI #1010).
    console_handler = logging.StreamHandler(stream)
    console_handler.setLevel(level)
    console_handler.addFilter(correlation)
    console_handler.setFormatter(
        _ConsoleFormatter(
            color=verbosity != "quiet" and _stream_wants_color(stream), callsite=callsite
        )
    )
    root_logger.addHandler(console_handler)

    # JSON file handler — writes every record regardless of verbosity.
    if log_file is not None:
        file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.addFilter(correlation)
        file_handler.setFormatter(_JsonFormatter(callsite=callsite))
        root_logger.addHandler(file_handler)

    root_logger.setLevel(logging.DEBUG if log_file else level)
