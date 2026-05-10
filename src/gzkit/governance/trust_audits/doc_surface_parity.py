"""Doc-surface parity audit (GHI #418).

Fail-closed if any ``.md`` file exists under ``docs/user/commands/``.
That directory was decommissioned in favour of the canonical
``docs/user/manpages/`` surface (airlineops convention).
"""

from __future__ import annotations

from pathlib import Path

from gzkit.doc_coverage.manifest import MANPAGE_DIR
from gzkit.validate import ValidationError

_DECOMMISSIONED_DIR = Path("docs") / "user" / "commands"
_DECOMMISSIONED_POSIX = _DECOMMISSIONED_DIR.as_posix()
_PARITY_MESSAGE = (
    f"{_DECOMMISSIONED_POSIX}/ is decommissioned (GHI #418). Move to {MANPAGE_DIR.as_posix()}/."
)


def audit_doc_surface_parity(project_root: Path) -> list[ValidationError]:
    """Return errors for stale files under the decommissioned commands surface."""
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
            message=_PARITY_MESSAGE,
        )
        for path in stale
    ]
