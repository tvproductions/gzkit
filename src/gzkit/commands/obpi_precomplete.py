"""Stage 5 pre-flight checklist for OBPI completion (GHI #196).

Reactive triage at Stage 5 — discovering brief readiness gaps, frontmatter
drift, lock ownership mismatches, missing ARB receipts, or stale plan-audit
receipts after invoking ``gz obpi complete`` — wastes operator time. This
command runs the same checks mechanically, upfront, with a clear pass/fail
report and a named remediation per failure.

The intended invocation pattern is **before** ``gz obpi complete``:

    uv run gz obpi precomplete OBPI-0.0.16-04
    # If exit 0, proceed to:
    uv run gz obpi complete OBPI-0.0.16-04 --attestor ... --attestation-text ...

The ``gz-obpi-pipeline`` skill wires this in as Stage 5 Step 0.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from gzkit.cli.helpers.exit_codes import (
    EXIT_POLICY_BREACH,
    EXIT_SUCCESS,
    EXIT_USER_ERROR,
)
from gzkit.commands.common import console, get_project_root

if TYPE_CHECKING:
    from collections.abc import Iterable


_OBPI_SHORT_PATTERN = re.compile(r"OBPI-[\d.]+-\d+")


@dataclass(frozen=True)
class CheckResult:
    """One precondition check: name, pass/fail, evidence message, remediation."""

    name: str
    ok: bool
    message: str
    remediation: str | None = None


def obpi_precomplete_cmd(*, obpi_id: str, as_json: bool = False) -> int:
    """Handler for ``gz obpi precomplete``.

    Exit codes (per .claude/rules/cli.md):
      0 = all preconditions met (safe to invoke gz obpi complete)
      1 = user/config error (brief not found, OBPI id invalid, etc.)
      3 = policy breach (one or more preconditions failed)

    Non-zero exit codes are propagated via ``SystemExit`` so
    ``gzkit.cli.main`` terminates the process with the correct code — its
    else-branch swallows handler return values otherwise.
    """
    project_root = get_project_root()

    brief_path = _resolve_brief_path(project_root, obpi_id)
    if brief_path is None:
        console.print(f"[red]Brief not found for {obpi_id}[/red]")
        raise SystemExit(EXIT_USER_ERROR)

    checks = list(_run_all_checks(project_root, brief_path, obpi_id))

    if as_json:
        print(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "ready": all(c.ok for c in checks),
                    "checks": [asdict(c) for c in checks],
                },
                indent=2,
            )
        )
    else:
        _render_human_report(obpi_id, checks)

    if not all(c.ok for c in checks):
        raise SystemExit(EXIT_POLICY_BREACH)
    return EXIT_SUCCESS


def _resolve_brief_path(project_root: Path, obpi_id: str) -> Path | None:
    """Find the OBPI brief by id under either obpis/ or briefs/ layout.

    Honors ``config.paths.design_root`` so the lookup works regardless of
    project layout (``docs/design`` in production, ``design`` in test
    fixtures from ``_quick_init``).
    """
    from gzkit.config import GzkitConfig

    short_match = _OBPI_SHORT_PATTERN.match(obpi_id)
    short = short_match.group(0) if short_match else obpi_id
    try:
        config = GzkitConfig.load(project_root / ".gzkit.json")
        design_root = config.paths.design_root
    except (OSError, ValueError):
        design_root = "docs/design"
    candidates: list[Path] = []
    for layout in ("obpis", "briefs"):
        candidates.extend(project_root.glob(f"{design_root}/adr/**/{layout}/{short}*.md"))
        if obpi_id != short:
            candidates.extend(project_root.glob(f"{design_root}/adr/**/{layout}/{obpi_id}*.md"))
    return candidates[0] if candidates else None


def _run_all_checks(project_root: Path, brief_path: Path, obpi_id: str) -> Iterable[CheckResult]:
    """Run every Stage 5 precondition check; yield each CheckResult in order."""
    yield _check_brief_readiness(project_root, brief_path)
    yield _check_reconcile_idempotent(project_root)
    yield _check_lock_held(project_root, obpi_id)
    yield _check_arb_receipts_present(project_root)
    yield _check_plan_audit_receipt(project_root, obpi_id)


def _check_brief_readiness(project_root: Path, brief_path: Path) -> CheckResult:
    """Brief MUST pass `gz obpi validate --authored` before completion."""
    from gzkit.hooks.obpi import ObpiValidator

    validator = ObpiValidator(project_root)
    errors = validator.validate_file(brief_path, require_authored=True)
    if errors:
        first = errors[0] if errors else "(no detail)"
        return CheckResult(
            name="brief_readiness",
            ok=False,
            message=f"{len(errors)} validator error(s); first: {first}",
            remediation=(
                f"Run `uv run gz obpi validate --authored "
                f"{brief_path.relative_to(project_root)}` and address each error."
            ),
        )
    return CheckResult(
        name="brief_readiness",
        ok=True,
        message=f"passes --authored validation ({brief_path.name})",
    )


def _check_reconcile_idempotent(project_root: Path) -> CheckResult:
    """`gz frontmatter reconcile --dry-run` MUST produce empty rewrite list.

    Catches the GHI #193 class-of-failure (gz obpi complete writes
    `Completed` but canonical-ledger form is `in_progress`): if the brief
    was just `complete`d in a prior precomplete attempt, the dry-run will
    surface the drift and recommend a reconcile round-trip before completion.
    """
    from gzkit.governance.frontmatter_coherence import reconcile_frontmatter

    receipt = reconcile_frontmatter(project_root, dry_run=True)
    if receipt.files_rewritten:
        files = ", ".join(rw.path for rw in receipt.files_rewritten[:3])
        suffix = "..." if len(receipt.files_rewritten) > 3 else ""
        return CheckResult(
            name="reconcile_idempotent",
            ok=False,
            message=f"{len(receipt.files_rewritten)} file(s) would be rewritten: {files}{suffix}",
            remediation="Run `uv run gz frontmatter reconcile` to clear drift.",
        )
    return CheckResult(
        name="reconcile_idempotent",
        ok=True,
        message="no pending frontmatter rewrites",
    )


def _check_lock_held(project_root: Path, obpi_id: str) -> CheckResult:
    """OBPI lock MUST exist before `gz obpi complete` runs."""
    short_match = _OBPI_SHORT_PATTERN.match(obpi_id)
    short = short_match.group(0) if short_match else obpi_id
    locks_dir = project_root / ".gzkit" / "locks"
    if not locks_dir.is_dir():
        return CheckResult(
            name="lock_held",
            ok=False,
            message="No .gzkit/locks/ directory",
            remediation=f"Run `uv run gz obpi lock claim {obpi_id}`.",
        )
    candidates = sorted(locks_dir.glob(f"{short}*.json")) + sorted(
        locks_dir.glob(f"{obpi_id}*.json") if obpi_id != short else []
    )
    if not candidates:
        return CheckResult(
            name="lock_held",
            ok=False,
            message=f"No lock file matches {short}",
            remediation=f"Run `uv run gz obpi lock claim {obpi_id}`.",
        )
    return CheckResult(
        name="lock_held",
        ok=True,
        message=f"lock present at {candidates[0].relative_to(project_root)}",
    )


def _check_arb_receipts_present(project_root: Path) -> CheckResult:
    """ARB receipts (lint/typecheck/unittest) SHOULD be present for Heavy-lane attestation.

    Per .gzkit/rules/attestation-enrichment.md, Heavy-lane attestation
    without inline receipt IDs is rejected. This check surfaces missing
    receipts before the operator drafts attestation text.
    """
    receipts_dir = project_root / "artifacts" / "receipts"
    if not receipts_dir.is_dir():
        return CheckResult(
            name="arb_receipts",
            ok=False,
            message="No artifacts/receipts/ directory",
            remediation=(
                "Run `uv run gz arb ruff` and "
                "`uv run gz arb step --name unittest -- uv run -m unittest -q` "
                "before drafting attestation."
            ),
        )
    arb_receipts = sorted(receipts_dir.glob("arb-*.json"), key=lambda p: p.stat().st_mtime)
    if not arb_receipts:
        return CheckResult(
            name="arb_receipts",
            ok=False,
            message="No ARB receipts found in artifacts/receipts/",
            remediation=(
                "Run `uv run gz arb ruff`, "
                "`uv run gz arb step --name unittest -- uv run -m unittest -q`, "
                "and `uv run gz arb step --name typecheck -- uv run gz typecheck`."
            ),
        )
    return CheckResult(
        name="arb_receipts",
        ok=True,
        message=f"{len(arb_receipts)} ARB receipt(s) present (newest: {arb_receipts[-1].name})",
    )


def _check_plan_audit_receipt(project_root: Path, obpi_id: str) -> CheckResult:
    """Plan-audit receipt MUST exist with verdict PASS for the target OBPI."""
    short_match = _OBPI_SHORT_PATTERN.match(obpi_id)
    short = short_match.group(0) if short_match else obpi_id
    plans_dir = project_root / ".claude" / "plans"
    if not plans_dir.is_dir():
        return CheckResult(
            name="plan_audit_receipt",
            ok=False,
            message="No .claude/plans/ directory",
            remediation=f"Run `uv run gz plan audit {obpi_id}`.",
        )
    candidates = sorted(plans_dir.glob(f".plan-audit-receipt-{short}*.json"))
    if not candidates:
        return CheckResult(
            name="plan_audit_receipt",
            ok=False,
            message=f"No plan-audit receipt for {short}",
            remediation=f"Run `uv run gz plan audit {obpi_id}`.",
        )
    receipt_path = candidates[-1]
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return CheckResult(
            name="plan_audit_receipt",
            ok=False,
            message=f"Receipt unreadable: {exc}",
            remediation=f"Re-run `uv run gz plan audit {obpi_id}`.",
        )
    verdict = receipt.get("verdict", "")
    if verdict != "PASS":
        return CheckResult(
            name="plan_audit_receipt",
            ok=False,
            message=f"Receipt verdict is {verdict!r} at {receipt_path.name}",
            remediation=(f"Address audit gaps and re-run `uv run gz plan audit {obpi_id}`."),
        )
    return CheckResult(
        name="plan_audit_receipt",
        ok=True,
        message=f"PASS receipt at {receipt_path.name}",
    )


def _render_human_report(obpi_id: str, checks: list[CheckResult]) -> None:
    """Render checklist with ✓/✗ markers + remediation hints."""
    console.print(f"\n[bold]Stage 5 precomplete check: {obpi_id}[/bold]\n")
    for check in checks:
        marker = "[green]✓[/green]" if check.ok else "[red]✗[/red]"
        console.print(f"  {marker} {check.name}: {check.message}")
        if not check.ok and check.remediation:
            console.print(f"      [dim]→ {check.remediation}[/dim]")
    failed = [c for c in checks if not c.ok]
    console.print()
    if failed:
        console.print(
            f"[red]BLOCKED: {len(failed)} of {len(checks)} preconditions not met. "
            f"Address remediations above before invoking `gz obpi complete`.[/red]"
        )
    else:
        console.print(
            f"[green]READY: all {len(checks)} preconditions met. "
            f"Safe to invoke `gz obpi complete {obpi_id}`.[/green]"
        )


__all__ = ["CheckResult", "obpi_precomplete_cmd"]
