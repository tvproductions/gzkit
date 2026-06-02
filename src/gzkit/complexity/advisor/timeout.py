"""Pre-commit timeout / fallback / failure-logging primitive (OBPI-0.0.29-09).

Wraps a callable with a configurable timeout. Returns a discriminated
``TimeoutResult`` union — callers decide policy (fail-open or fail-closed)
based on the result variant. On timeout, emits a JSONL entry to the
specified log path.

Cross-platform: ``signal.SIGALRM`` on POSIX, ``threading.Timer`` on Windows.
"""

from __future__ import annotations

import json
import os
import signal
import threading
import time
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

_DEFAULT_TIMEOUT_S = 30.0


class TimeoutOk(BaseModel):
    """Successful completion within the timeout window."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["ok"] = "ok"
    value: Any = Field(..., description="Return value of the callable")


class TimeoutTimedOut(BaseModel):
    """Callable exceeded the timeout window."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: Literal["timed_out"] = "timed_out"
    elapsed_s: float = Field(..., description="Elapsed seconds before timeout fired")
    callable_name: str = Field(..., description="Name of the timed-out callable")


TimeoutResult = TimeoutOk | TimeoutTimedOut


class _TimeoutError(Exception):
    pass


def run_with_timeout[T](
    callable_: Callable[[], T],
    *,
    timeout_s: float = _DEFAULT_TIMEOUT_S,
    log_path: Path,
    context_file_paths: list[str] | None = None,
    context_invocation: Literal["auto-chain", "ad-hoc"] = "auto-chain",
) -> TimeoutResult:
    """Run *callable_* with a hard timeout; log on timeout.

    Returns ``TimeoutOk`` on success, ``TimeoutTimedOut`` on timeout.
    The caller decides policy (fail-open or closed) based on the result.
    """
    start = time.monotonic()
    callable_name = getattr(callable_, "__name__", repr(callable_))

    if os.name == "nt":
        result = _run_with_timer(callable_, timeout_s)
    else:
        result = _run_with_signal(callable_, timeout_s)

    if result is _SENTINEL_TIMED_OUT:
        elapsed = time.monotonic() - start
        _emit_failure_log(
            log_path=log_path,
            callable_name=callable_name,
            timeout_s=timeout_s,
            elapsed_s=elapsed,
            file_paths=context_file_paths or [],
            invocation=context_invocation,
        )
        return TimeoutTimedOut(elapsed_s=elapsed, callable_name=callable_name)

    return TimeoutOk(value=result)


_SENTINEL_TIMED_OUT = object()


def _run_with_signal[T](callable_: Callable[[], T], timeout_s: float) -> T | object:
    """POSIX path: use SIGALRM for timeout."""

    def _handler(signum: int, frame: Any) -> None:  # noqa: ARG001
        raise _TimeoutError

    # POSIX-only signal attributes; this function is guarded at call site.
    old_handler = signal.signal(signal.SIGALRM, _handler)
    signal.setitimer(signal.ITIMER_REAL, timeout_s)
    try:
        result = callable_()
    except _TimeoutError:
        return _SENTINEL_TIMED_OUT
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old_handler)
    return result


def _run_with_timer[T](callable_: Callable[[], T], timeout_s: float) -> T | object:
    """Windows path: use threading.Timer for timeout."""
    result_holder: list[Any] = []
    exc_holder: list[BaseException] = []
    timed_out = threading.Event()

    def _target() -> None:
        try:
            result_holder.append(callable_())
        except BaseException as e:
            exc_holder.append(e)

    thread = threading.Thread(target=_target, daemon=True)
    timer = threading.Timer(timeout_s, lambda: timed_out.set())
    timer.start()
    thread.start()
    thread.join(timeout=timeout_s + 0.1)
    timer.cancel()

    if timed_out.is_set() or not result_holder:
        return _SENTINEL_TIMED_OUT
    if exc_holder:
        raise exc_holder[0]
    return result_holder[0]


def _emit_failure_log(
    *,
    log_path: Path,
    callable_name: str,
    timeout_s: float,
    elapsed_s: float,
    file_paths: list[str],
    invocation: str,
) -> None:
    """Append a JSONL entry to the failure log."""
    entry = {
        "timestamp": datetime.now(UTC).isoformat(),
        "callable_name": callable_name,
        "timeout_s": timeout_s,
        "elapsed_s": round(elapsed_s, 3),
        "context": {
            "file_paths": file_paths,
            "invocation": invocation,
        },
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
