"""ARB Ruff reporter — wraps ruff and emits a lint receipt."""

from __future__ import annotations

import json
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from gzkit.arb.paths import receipts_root

SCHEMA_ID = "gzkit.arb.lint_receipt.v1"
DEFAULT_MAX_FINDINGS = 200


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
        )
    except OSError as exc:
        return subprocess.CompletedProcess(cmd, 127, "", str(exc))


def _ruff_version() -> str:
    result = _run_command(["ruff", "--version"])
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _git_context() -> dict[str, object]:
    commit: str | None = None
    branch: str | None = None
    dirty: bool | None = None

    result = _run_command(["git", "rev-parse", "HEAD"])
    if result.returncode == 0:
        commit = result.stdout.strip() or None

    result = _run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if result.returncode == 0:
        branch = result.stdout.strip() or None

    result = _run_command(["git", "status", "--porcelain"])
    if result.returncode == 0:
        dirty = bool(result.stdout.strip())

    payload: dict[str, object] = {"commit": commit}
    if branch is not None:
        payload["branch"] = branch
    if dirty is not None:
        payload["dirty"] = dirty
    return payload


def _fallback_findings(message: str) -> list[dict[str, object]]:
    text = message.strip() or "ruff output missing"
    return [
        {
            "rule": "ARB000",
            "path": "<ruff>",
            "line": 1,
            "message": text[:400],
        }
    ]


def _int_ge1(value: object, *, default: int = 1) -> int:
    if isinstance(value, int) and value >= 1:
        return value
    return default


def _location_dict(item: dict[str, Any]) -> dict[str, Any]:
    location = item.get("location")
    if isinstance(location, dict):
        return location
    return {}


def _finding_from_item(item: object) -> dict[str, object] | None:
    if not isinstance(item, dict):
        return None

    item_dict = cast("dict[str, Any]", item)

    rule = item_dict.get("code") or item_dict.get("rule") or "UNKNOWN"
    path = item_dict.get("filename") or item_dict.get("path") or "<unknown>"
    location = _location_dict(item_dict)
    line = _int_ge1(location.get("row") or item_dict.get("line"), default=1)
    message = item_dict.get("message") or ""

    entry: dict[str, object] = {
        "rule": str(rule),
        "path": str(path),
        "line": line,
        "message": str(message),
    }

    column_raw = location.get("column") or item_dict.get("column")
    if isinstance(column_raw, int) and column_raw >= 1:
        entry["column"] = column_raw

    return entry


def _parse_findings(raw: str, stderr: str) -> list[dict[str, object]]:
    if not raw.strip():
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return _fallback_findings(stderr or raw)
    if not isinstance(data, list):
        return _fallback_findings("ruff JSON output was not a list")

    findings: list[dict[str, object]] = []
    for item in data:
        finding = _finding_from_item(item)
        if finding is not None:
            findings.append(finding)
    return findings


def _write_receipt(receipt: dict[str, object]) -> Path:
    out_dir = receipts_root()
    path = out_dir / f"{receipt['run_id']}.json"
    text = _canonical(receipt)
    path.write_text(text, encoding="utf-8")
    return path


def run_ruff_via_arb(
    *,
    paths: list[str] | None = None,
    fix: bool = False,
    quiet: bool = False,
    max_findings: int = DEFAULT_MAX_FINDINGS,
    soft_fail: bool = False,
) -> tuple[int, Path]:
    """Run ruff and emit an ARB lint receipt.

    Args:
        paths: Paths to check. Defaults to `["."]`.
        fix: Apply ruff auto-fixes.
        quiet: Suppress non-essential stdout output.
        max_findings: Maximum number of findings stored in the receipt.
        soft_fail: When true, emit a receipt but return exit status 0 to avoid
            blocking caller workflows (measurement-only mode).

    Returns:
        Tuple of (exit_status, receipt_path).
    """
    targets = paths or ["."]
    cmd = ["ruff", "check", *targets, "--output-format", "json"]
    if fix:
        cmd.append("--fix")

    ruff_result = _run_command(cmd)
    exit_status = int(ruff_result.returncode)

    if exit_status == 2:
        findings = _fallback_findings(ruff_result.stderr or ruff_result.stdout)
    else:
        findings = _parse_findings(ruff_result.stdout, ruff_result.stderr)

    findings_total = len(findings)
    findings_truncated = False
    if max_findings >= 0 and len(findings) > max_findings:
        findings = findings[:max_findings]
        findings_truncated = True

    receipt: dict[str, object] = {
        "schema": SCHEMA_ID,
        "tool": {"name": "ruff", "version": _ruff_version()},
        "run_id": f"arb-ruff-{uuid.uuid4().hex}",
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git": _git_context(),
        "findings": findings,
        "findings_total": findings_total,
        "findings_truncated": findings_truncated,
        "exit_status": exit_status,
    }

    path = _write_receipt(receipt)
    if not quiet:
        print(f"arb ruff exit_status={exit_status} receipt={path}")

    if exit_status != 0 and not quiet:
        print("arb next: uv run gz arb advise", file=sys.stderr)

    if soft_fail:
        return 0, path
    return exit_status, path


__all__ = ["SCHEMA_ID", "run_ruff_via_arb"]
