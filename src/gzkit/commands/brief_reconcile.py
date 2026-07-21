"""``gz brief reconcile`` command (ADR-0.0.37, OBPI-0.0.37-06).

Operator-runnable wrapper around the OBPI-0.0.37-05 reconciliation engine. Emits
a ``brief_reconciled`` summary event on every run, an additional
``brief_reconcile_drift_detected`` event when any of the five dimensions drift,
and — under ``--apply --attestor`` — writes operator-attested amendments back
into the brief. The engine is consumed read-only; this module owns the CLI
surface, ledger emission, and the amendment-write path only.
"""

from __future__ import annotations

import json

from gzkit.commands.common import (
    GzCliError,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.commands.obpi_precomplete import _resolve_brief_path
from gzkit.governance.brief_reconcile import ReconcileResult, reconcile_brief
from gzkit.governance.events import (
    emit_brief_reconcile_drift_detected,
    emit_brief_reconciled,
)


def _compute_amendments(result: ReconcileResult, attestor: str) -> tuple[list[str], list[str]]:
    """Return (allowlist additions, tracked-defect notes) implied by the result.

    The CLI never silently rewrites verb references (operator-judgment call); it
    records them as tracked defects instead.
    """
    allowlist_adds = [
        f"`{path}` (added by brief reconcile, attestor {attestor})"
        for path in result.allowlist_delta.missing_in_brief
    ]
    defects = [
        f"Unresolved verb `gz {verb}` (brief reconcile, attestor {attestor})"
        for verb in result.verification_delta.unresolved_verbs
    ]
    if result.req_count_delta.delta != 0:
        defects.append(
            f"REQ-count drift: {result.req_count_delta.declared_reqs} declared vs "
            f"{result.req_count_delta.acceptance_criteria_count} acceptance criteria "
            f"(brief reconcile, attestor {attestor})"
        )
    return allowlist_adds, defects


def _append_under_heading(text: str, heading: str, bullets: list[str]) -> str:
    """Insert ``- bullet`` lines under ``heading`` (created at EOF if absent)."""
    block = "\n".join(f"- {bullet}" for bullet in bullets)
    if heading in text:
        idx = text.index(heading)
        line_end = text.index("\n", idx) + 1
        return f"{text[:line_end]}\n{block}\n{text[line_end:]}"
    return f"{text.rstrip()}\n\n{heading}\n\n{block}\n"


def _apply_amendments(brief_path, result: ReconcileResult, attestor: str) -> None:
    """Write operator-attested amendments back into the brief frontmatter/body."""
    allowlist_adds, defects = _compute_amendments(result, attestor)
    text = brief_path.read_text(encoding="utf-8")
    if allowlist_adds:
        text = _append_under_heading(text, "## Allowed Paths", allowlist_adds)
    if defects:
        text = _append_under_heading(text, "## Tracked Defects", defects)
    brief_path.write_text(text, encoding="utf-8")


def _delta_counts(result: ReconcileResult) -> dict[str, int]:
    return {
        "allowlist": (
            len(result.allowlist_delta.missing_in_brief)
            + len(result.allowlist_delta.missing_on_disk)
        ),
        "discovery": len(result.discovery_delta.unresolved_paths),
        "verification": len(result.verification_delta.unresolved_verbs),
        "req_count": result.req_count_delta.delta,
        "citation": len(result.citation_delta.stale_citations),
    }


def _render_report(result: ReconcileResult, *, do_write: bool, dry_run: bool) -> None:
    counts = _delta_counts(result)
    status = "[red]DRIFT[/red]" if result.has_drift else "[green]clean[/green]"
    console.print(f"[bold]Brief reconcile:[/bold] {result.brief_id} — {status}")
    console.print(
        "  deltas: "
        f"allowlist={counts['allowlist']} discovery={counts['discovery']} "
        f"verification={counts['verification']} req_count={counts['req_count']} "
        f"citation={counts['citation']}"
    )
    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no amendments written.")
    elif do_write:
        console.print("[green]Amendments applied to the brief.[/green]")


def brief_reconcile_cmd(
    obpi_id: str,
    dry_run: bool,
    apply: bool,
    attestor: str | None,
    as_json: bool,
) -> None:
    """Reconcile an OBPI brief against project state; optionally apply amendments."""
    ensure_initialized()
    root = get_project_root()

    brief_path = _resolve_brief_path(root, obpi_id)
    if brief_path is None:
        raise GzCliError(f"Brief not found for {obpi_id}")
    if apply and not attestor:
        raise GzCliError("--apply requires --attestor")

    result = reconcile_brief(brief_path, root)
    do_write = bool(apply and not dry_run)

    if do_write:
        _apply_amendments(brief_path, result, attestor or "")
        # Re-measure against the brief as amended. A repair verb that reports the
        # result it computed *before* its own mutation certifies the pre-mutation
        # world, so the Stage-1 gate blocks on drift the amendment already cleared
        # (GHI #677). The report, the receipt, and the exit code all read from this
        # second measurement.
        result = reconcile_brief(brief_path, root)

    if as_json:
        print(  # noqa: T201 — machine-consumption payload
            json.dumps(
                {
                    "brief_id": result.brief_id,
                    "has_drift": result.has_drift,
                    "deltas": _delta_counts(result),
                    "applied": do_write,
                    "dry_run": bool(dry_run),
                },
                indent=2,
            )
        )
    else:
        _render_report(result, do_write=do_write, dry_run=dry_run)

    if do_write:
        emit_brief_reconciled(root, result, applied=True, attestor=attestor)
    else:
        emit_brief_reconciled(root, result, applied=False)

    if result.has_drift:
        emit_brief_reconcile_drift_detected(root, result)
        # REQ-0.0.37-06-01 ("exits 0 on no-drift, 3 on drift") is unconditional:
        # --apply repairs the allowlist dimension only, so residual drift must
        # still fail closed rather than hand the operator a green exit over a
        # receipt the Stage-1 gate will reject (GHI #677).
        raise SystemExit(3)
