"""Doc-surface parity audit (GHI #418).

Fail-closed if any ``.md`` file exists under ``docs/user/commands/``.
That directory was decommissioned in favour of the canonical
``docs/user/manpages/`` surface (airlineops convention).
"""

from __future__ import annotations

from pathlib import Path

from gzkit.validate import ValidationError

_DECOMMISSIONED_DIR = Path("docs") / "user" / "commands"


def audit_doc_surface_parity(project_root: Path) -> list[ValidationError]:
    target = project_root / _DECOMMISSIONED_DIR
    if not target.is_dir():
        return []
    stale = sorted(p.relative_to(project_root).as_posix() for p in target.rglob("*.md"))
    if not stale:
        return []
    return [
        ValidationError(
            type="doc_surface_parity",
            artifact=path,
            message=(
                "docs/user/commands/ is decommissioned (GHI #418). Move to docs/user/manpages/."
            ),
        )
        for path in stale
    ]
