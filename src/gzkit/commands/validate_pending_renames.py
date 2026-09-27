"""Pending bare-to-slug rename validator (GHI #1118).

``gz migrate-semver`` finds ledger events under a bare ``ADR-X.Y.Z`` or
``OBPI-X.Y.Z-NN`` whose artifact's on-disk id is its slug and appends the
rename. Until it runs, those events are orphaned from their artifact. This scope
runs the same detector in the default tier, so the drift fails the gate instead
of waiting for an operator to remember the migration (AGENTS.md § Architectural
Boundaries 4).
"""

from pathlib import Path

from gzkit.commands.register import pending_semver_renames
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.validate import ValidationError


def _validate_pending_renames(project_root: Path) -> list[ValidationError]:
    """Report every rename ``gz migrate-semver`` would append; empty when none are pending."""
    config = GzkitConfig.load(project_root / ".gzkit.json")
    ledger = Ledger(project_root / config.paths.ledger)
    try:
        pending = pending_semver_renames(project_root, config.paths.design_root, ledger)
    except (OSError, ValueError):
        # An unreadable ledger is the `ledger` scope's finding to report; raising
        # here would replace its diagnosis with a crash in the same run.
        return []
    if not pending:
        return []
    pairs = "; ".join(f"{old} -> {new}" for old, new in pending)
    return [
        ValidationError(
            type="pending_renames",
            artifact=".gzkit/ledger.jsonl",
            message=(
                f"{len(pending)} artifact rename(s) pending: {pairs}. "
                "Why: events under a bare id are orphaned from their artifact until the "
                "ledger records the rename; reconciliation may not wait on a manual "
                "chore (AGENTS.md § Architectural Boundaries 4, GHI #1118). "
                "Next: review with `uv run gz migrate-semver --dry-run`, then append "
                "with `uv run gz migrate-semver`."
            ),
        )
    ]
