"""ARB step reporter — wraps arbitrary commands and emits a step receipt."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gzkit.arb.paths import receipts_root
from gzkit.arb.ruff_reporter import _git_context

SCHEMA_ID = "gzkit.arb.step_receipt.v1"
DEFAULT_MAX_OUTPUT_CHARS = 8000


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _tail(text: str, max_chars: int) -> tuple[str, bool]:
    if max_chars < 0:
        return text, False
    if len(text) <= max_chars:
        return text, False
    return text[-max_chars:], True


def _write_receipt(receipt: dict[str, object]) -> Path:
    out_dir = receipts_root()
    path = out_dir / f"{receipt['run_id']}.json"
    path.write_text(_canonical(receipt), encoding="utf-8")
    return path


def run_step_via_arb(
    *,
    name: str,
    cmd: list[str],
    quiet: bool = False,
    soft_fail: bool = False,
    max_output_chars: int = DEFAULT_MAX_OUTPUT_CHARS,
) -> tuple[int, Path]:
    """Run an arbitrary command and emit an ARB step receipt.

    Args:
        name: Logical step name (e.g., "ty", "unittest").
        cmd: Command argv to execute.
        quiet: Suppress non-essential stdout output.
        soft_fail: When true, emit a receipt but return exit status 0 to avoid
            blocking caller workflows.
        max_output_chars: Maximum characters stored per stdout/stderr tail.

    Returns:
        Tuple of (exit_status, receipt_path).

    Raises:
        ValueError: If name is empty or cmd is empty.
    """
    step_name = (name or "").strip()
    if not step_name:
        raise ValueError("ARB step name is required")
    if not cmd:
        raise ValueError("ARB step command is required")

    started = time.perf_counter()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        result = subprocess.CompletedProcess(cmd, 127, "", str(exc))
    duration_ms = int((time.perf_counter() - started) * 1000)

    stdout_tail, stdout_truncated = _tail(result.stdout or "", max_output_chars)
    stderr_tail, stderr_truncated = _tail(result.stderr or "", max_output_chars)

    exit_status = int(result.returncode)

    receipt: dict[str, object] = {
        "schema": SCHEMA_ID,
        "step": {
            "name": step_name,
            "command": list(cmd),
        },
        "run_id": f"arb-step-{step_name}-{uuid.uuid4().hex}",
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git": _git_context(),
        "exit_status": exit_status,
        "duration_ms": duration_ms,
        "stdout_tail": stdout_tail,
        "stderr_tail": stderr_tail,
        "stdout_truncated": stdout_truncated,
        "stderr_truncated": stderr_truncated,
    }

    path = _write_receipt(receipt)

    if not quiet:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        print(f"arb step name={step_name} exit_status={exit_status} receipt={path}")

    if soft_fail:
        return 0, path
    return exit_status, path


__all__ = ["SCHEMA_ID", "run_step_via_arb"]
