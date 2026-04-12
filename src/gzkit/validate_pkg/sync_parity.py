"""Sync parity validation for generated control surfaces.

Detects drift between files in the working tree and what ``sync_all()`` would
produce for the current canonical state. The check uses a snapshot-sync-compare
protocol: every file under a tracked surface root is hashed, ``sync_all()`` runs
in place, drift is reported, and the snapshot is restored so the validator is
non-mutating from the caller's perspective.

Any transient generated content (e.g. the ``- **Updated**: YYYY-MM-DD`` line in
``AGENTS.md``) is normalized before comparison so operational timestamps do not
surface as false drift.
"""

import re
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.core.validation_rules import ValidationError
from gzkit.sync_surfaces import sync_all

SURFACE_ROOTS: tuple[str, ...] = (
    ".gzkit/manifest.json",
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".github/discovery-index.json",
    ".github/instructions",
    ".claude/settings.json",
    ".claude/hooks",
    ".claude/rules",
    ".claude/skills",
    ".agents/skills",
    ".github/skills",
    ".copilotignore",
)

_NESTED_AGENTS_MD: tuple[str, ...] = (
    "src/gzkit/AGENTS.md",
    "src/gzkit/commands/AGENTS.md",
    "tests/AGENTS.md",
)

_SYNC_DATE_LINE = re.compile(rb"^- \*\*Updated\*\*: \d{4}-\d{2}-\d{2}", re.MULTILINE)


def _collect_files(project_root: Path) -> set[Path]:
    """Return every tracked generated file under the configured surface roots."""
    collected: set[Path] = set()
    candidates: list[str] = [*SURFACE_ROOTS, *_NESTED_AGENTS_MD]
    for rel in candidates:
        abs_path = project_root / rel
        if abs_path.is_file():
            collected.add(abs_path)
            continue
        if abs_path.is_dir():
            for path in abs_path.rglob("*"):
                if path.is_file():
                    collected.add(path)
    return collected


def _normalize(content: bytes) -> bytes:
    """Strip volatile sync-timestamp lines so operational drift is not false drift."""
    return _SYNC_DATE_LINE.sub(b"- **Updated**: <DATE>", content)


def _snapshot(files: set[Path]) -> dict[Path, bytes]:
    """Read current bytes for each file into an in-memory snapshot."""
    snapshot: dict[Path, bytes] = {}
    for path in files:
        try:
            snapshot[path] = path.read_bytes()
        except OSError:
            continue
    return snapshot


def _restore(project_root: Path, snapshot: dict[Path, bytes], created: set[Path]) -> None:
    """Write snapshot content back to disk and remove files sync_all created."""
    for path, content in snapshot.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    for path in created:
        try:
            path.unlink()
        except FileNotFoundError:
            continue


def plan_sync_all(project_root: Path, config: GzkitConfig | None = None) -> list[str]:
    """Return the exact list of paths ``sync_all()`` would write, without mutating disk.

    Runs the real ``sync_all()`` orchestrator inside a snapshot-restore envelope
    so the complete write set is derived from the same code path as apply mode.
    Used by ``gz agent sync control-surfaces --dry-run`` to preview an exact
    deterministic plan instead of a hand-maintained subset.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    pre_files = _collect_files(project_root)
    snapshot = _snapshot(pre_files)

    created: set[Path] = set()
    planned: list[str] = []
    try:
        raw_planned = list(sync_all(project_root, config))
        for entry in raw_planned:
            candidate = Path(entry)
            if candidate.is_absolute():
                try:
                    planned.append(candidate.relative_to(project_root).as_posix())
                except ValueError:
                    planned.append(candidate.as_posix())
            else:
                planned.append(candidate.as_posix())
        post_files = _collect_files(project_root)
        created = post_files - pre_files
    finally:
        _restore(project_root, snapshot, created)

    return sorted(set(planned))


def check_sync_parity(
    project_root: Path, config: GzkitConfig | None = None
) -> list[ValidationError]:
    """Detect drift between generated surfaces and the output of ``sync_all()``.

    The check runs ``sync_all()`` against ``project_root`` in place and compares
    pre/post content for every tracked surface file. After comparison, the
    pre-sync snapshot is restored so the caller sees no net file mutation.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    pre_files = _collect_files(project_root)
    snapshot = _snapshot(pre_files)

    errors: list[ValidationError] = []
    created: set[Path] = set()
    try:
        sync_all(project_root, config)
        post_files = _collect_files(project_root)
        created = post_files - pre_files
        removed = pre_files - post_files
        shared = pre_files & post_files

        for path in sorted(shared):
            old = _normalize(snapshot.get(path, b""))
            try:
                new = _normalize(path.read_bytes())
            except OSError as exc:
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(path.relative_to(project_root)),
                        message=f"Failed to re-read surface after sync: {exc}",
                    )
                )
                continue
            if old != new:
                errors.append(
                    ValidationError(
                        type="surface",
                        artifact=str(path.relative_to(project_root)),
                        message=(
                            "Generated surface is out of sync with canonical state. "
                            "Run `uv run gz agent sync control-surfaces` to repair."
                        ),
                    )
                )

        for path in sorted(created):
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=str(path.relative_to(project_root)),
                    message=(
                        "Generated surface missing — sync_all() would create it. "
                        "Run `uv run gz agent sync control-surfaces` to repair."
                    ),
                )
            )

        for path in sorted(removed):
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=str(path.relative_to(project_root)),
                    message=(
                        "Stale surface — sync_all() would remove it. "
                        "Run `uv run gz agent sync control-surfaces` to repair."
                    ),
                )
            )
    finally:
        _restore(project_root, snapshot, created)

    return errors
