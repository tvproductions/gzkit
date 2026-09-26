"""The fail-closed canonical preflight every mirror-propagating command runs (GHI #1100).

``gz agent sync control-surfaces`` refused to propagate corrupted canon, while
``gz tidy --fix`` and ``gz init`` (repair and ``--force``) reached the same
``sync_all`` through their own call sites and copied the corruption into every
vendor mirror. A guard one command holds and its siblings bypass guards
nothing, so the refusal lives here and every propagating caller routes
through it.
"""

from pathlib import Path

from rich.markup import escape

from gzkit.commands.common import console
from gzkit.config import GzkitConfig
from gzkit.sync import collect_canonical_sync_blockers


def report_sync_blockers(blockers: list[str]) -> None:
    """Print the preflight refusal and exit 1. Call only with a non-empty list."""
    console.print("[red]Sync preflight failed: canonical skills state is corrupted.[/red]")
    for blocker in blockers:
        console.print(f"  - {escape(blocker)}")
    console.print("\nRecovery:")
    console.print("  1. Fix canonical skills under .gzkit/skills")
    console.print("  2. Run: uv run gz skill audit --json")
    console.print("  3. Re-run the command")
    raise SystemExit(1)


def refuse_on_sync_blockers(project_root: Path, config: GzkitConfig) -> None:
    """Exit 1 before any mirror propagation while canonical skills fail preflight."""
    blockers = collect_canonical_sync_blockers(project_root, config)
    if blockers:
        report_sync_blockers(blockers)
