"""CLI adapter for the frontmatter-ledger reconciliation chore (ADR-0.0.16 OBPI-03).

Thin wrapper around ``gzkit.governance.frontmatter_coherence.reconcile_frontmatter``
that enforces the standard 4-code CLI doctrine exit policy and supports ``--json``
for machine-readable receipt output.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.cli.helpers.exit_codes import (
    EXIT_POLICY_BREACH,
    EXIT_SUCCESS,
    EXIT_SYSTEM_ERROR,
    EXIT_USER_ERROR,
)
from gzkit.commands.common import console, get_project_root
from gzkit.governance.frontmatter_coherence import (
    UnmappedStatusBlocker,
    reconcile_frontmatter,
)


def frontmatter_reconcile_cmd(*, dry_run: bool = False, as_json: bool = False) -> int:
    """Handler for ``gz frontmatter reconcile``.

    Exit codes (per .claude/rules/cli.md):
      0 = success
      1 = user/config error (not a gzkit project)
      2 = system/IO error (ledger unreadable, write failure)
      3 = policy breach (UnmappedStatusBlocker)

    Non-zero exit codes are propagated via ``SystemExit`` so ``gzkit.cli.main``
    terminates the process with the correct code — its else-branch swallows
    handler return values otherwise.
    """
    project_root = _resolve_project_root()
    if project_root is None:
        console.print("[red]Not inside a gzkit project (no .gzkit.json found).[/red]")
        raise SystemExit(EXIT_USER_ERROR)

    try:
        receipt = reconcile_frontmatter(project_root, dry_run=dry_run)
    except UnmappedStatusBlocker as blocker:
        console.print(f"[red]{blocker}[/red]")
        raise SystemExit(EXIT_POLICY_BREACH) from blocker
    except (OSError, ValueError) as exc:
        console.print(f"[red]reconcile_frontmatter failed: {exc}[/red]")
        raise SystemExit(EXIT_SYSTEM_ERROR) from exc

    if as_json:
        print(json.dumps(receipt.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        _render_human_receipt(receipt, dry_run=dry_run)
    return EXIT_SUCCESS


def _resolve_project_root() -> Path | None:
    """Return the project root via ``get_project_root`` or None when outside a project."""
    try:
        root = get_project_root()
    except (OSError, ValueError):
        return None
    if not (root / ".gzkit.json").is_file():
        return None
    return root


def _render_human_receipt(receipt: object, *, dry_run: bool) -> None:
    """Human-readable summary of a reconciliation receipt."""
    from gzkit.governance.frontmatter_coherence import (  # noqa: PLC0415
        ReconciliationReceipt,
    )

    if not isinstance(receipt, ReconciliationReceipt):
        return
    label = "[yellow]DRY-RUN[/yellow]" if dry_run else "[green]applied[/green]"
    console.print(f"Frontmatter-ledger reconciliation {label}")
    console.print(f"  ledger cursor:     {receipt.ledger_cursor}")
    console.print(f"  started / ended:   {receipt.run_started_at} / {receipt.run_completed_at}")
    console.print(f"  files rewritten:   {len(receipt.files_rewritten)}")
    console.print(f"  pool ADRs skipped: {len(receipt.skipped)}")
    if not receipt.files_rewritten:
        console.print("  [dim]no drift detected[/dim]")
        return
    for rewrite in receipt.files_rewritten:
        console.print(f"    {rewrite.path}")
        for diff in rewrite.diffs:
            console.print(f"      {diff.field}: {diff.before!r} -> {diff.after!r}")


__all__ = ["frontmatter_reconcile_cmd"]
