"""ARB Ruff reporter — wraps ruff and emits a lint receipt.

Ruff selects ALL under ``data/ruff_baseline.json`` (RO-9 tranche 4), so the
receipt carries the baseline's verdict, the same one `gz lint` returns: only the
findings no row holds, and a row its findings no longer fill, are recorded and
fail the run. A tree with no baseline records every finding, as plain Ruff does.
"""

import json
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from gzkit import ruff_baseline
from gzkit.arb.paths import receipts_root
from gzkit.executables import resolve_argv

SCHEMA_ID = "gzkit.arb.lint_receipt.v1"
DEFAULT_MAX_FINDINGS = 200


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(  # noqa: S603 — the Ruff argv this module builds; executable resolved
            resolve_argv(cmd),
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            encoding="utf-8",
        )
    except OSError as exc:
        return subprocess.CompletedProcess(cmd, 127, "", str(exc))


def _ruff_version() -> str:
    result = _run_command(["uv", "run", "ruff", "--version"])
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


def _breach_findings(breach: ruff_baseline.Breach) -> list[dict[str, object]]:
    """Render one baseline breach as receipt findings.

    Returns:
        Each unheld finding, or one entry naming the row to lower.

    """
    if breach.kind == "unheld":
        return [
            {"rule": f.rule, "path": f.file, "line": max(f.line, 1), "message": f.message}
            for f in breach.findings
        ]
    return [
        {
            "rule": breach.rule,
            "path": breach.file,
            "line": 1,
            "message": (
                f"{ruff_baseline.BASELINE_RELPATH} holds {breach.held} {breach.rule} for this "
                f"file and {breach.found} remain; run `uv run gz lint --ratchet`"
            ),
        }
    ]


def _judge_against_baseline(
    stdout: str, project_root: Path, targets: list[str]
) -> tuple[int, list[dict[str, object]]]:
    """Judge Ruff's JSON report against ``data/ruff_baseline.json``.

    Returns:
        The exit status (0 clean, 1 a breach, 2 unreadable) and the breach findings.

    """
    try:
        findings = ruff_baseline.parse_ruff_json(stdout, project_root)
        baseline = ruff_baseline.load_baseline(project_root) or {}
    except (ruff_baseline.RuffRunError, ruff_baseline.BaselineError) as exc:
        return 2, _fallback_findings(str(exc))
    scope = None if targets == ["."] else [Path(t).as_posix().rstrip("/") for t in targets]
    breaches = ruff_baseline.compare(findings, baseline, scope)
    return (1 if breaches else 0), [f for b in breaches for f in _breach_findings(b)]


def _write_receipt(receipt: dict[str, object]) -> Path:
    out_dir = receipts_root()
    path = out_dir / f"{receipt['run_id']}.json"
    # Trailing newline keeps end-of-file-fixer from rewriting receipts on
    # every pre-commit run (would block git-sync and burn operator tokens).
    text = _canonical(receipt) + "\n"
    path.write_text(text, encoding="utf-8")
    return path


def run_ruff_via_arb(  # noqa: PLR0913 — one keyword-only option per `gz arb ruff` flag
    *,
    paths: list[str] | None = None,
    fix: bool = False,
    quiet: bool = False,
    max_findings: int = DEFAULT_MAX_FINDINGS,
    soft_fail: bool = False,
    project_root: Path | None = None,
) -> tuple[int, Path]:
    """Run ruff and emit an ARB lint receipt.

    Args:
        paths: Paths to check. Defaults to `["."]`.
        fix: Apply ruff auto-fixes.
        quiet: Suppress non-essential stdout output.
        max_findings: Maximum number of findings stored in the receipt.
        soft_fail: When true, emit a receipt but return exit status 0 to avoid
            blocking caller workflows (measurement-only mode).
        project_root: Root whose ``data/ruff_baseline.json`` judges the findings.
            Defaults to the working directory.

    Returns:
        Tuple of (exit_status, receipt_path).

    """
    targets = paths or ["."]
    cmd = ["uv", "run", "ruff", "check", *targets, "--output-format", "json"]
    if fix:
        cmd.append("--fix")

    ruff_result = _run_command(cmd)
    exit_status = int(ruff_result.returncode)

    if exit_status not in {0, 1}:
        findings = _fallback_findings(ruff_result.stderr or ruff_result.stdout)
    else:
        exit_status, findings = _judge_against_baseline(
            ruff_result.stdout, project_root or Path.cwd(), targets
        )

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
