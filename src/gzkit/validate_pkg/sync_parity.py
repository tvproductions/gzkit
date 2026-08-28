"""Sync parity validation for generated control surfaces.

Detects drift between files in the working tree and what ``sync_all()`` would
produce for the current canonical state. ``sync_all()`` runs inside
:func:`gzkit.surface_write.capture_surface_writes`, so it renders the canonical
bytes without touching the tree and the check is a pure byte comparison.

It was a snapshot-sync-compare protocol until 2026-08-27: hash every file, run
``sync_all()`` IN PLACE, report drift, restore. That made the validator write the
surface it claims to inspect -- on a clean tree after GHI #890, and on a drifted
tree always, because sync laid the canonical bytes down and the envelope put the
drift back. A validator that can write under ANY input cannot carry a static
``read_only`` classification: rarity is not the property a scheduler needs,
impossibility is (GHI #891). The restore also called ``os.utime``, so an mtime
probe could not see the writes it was masking -- ctime is the witness that works,
because it moves on write and cannot be set from userspace.

Any transient generated content (e.g. the ``- **Updated**: YYYY-MM-DD`` line in
``AGENTS.md``) is normalized before comparison so operational timestamps do not
surface as false drift.
"""

import contextlib
import re
from pathlib import Path

from gzkit.config import (
    CODEX_CONFIG_DEFAULT_PATH,
    GzkitConfig,
    resolve_codex_config_path,
)
from gzkit.core.validation_rules import ValidationError
from gzkit.rules import nested_agents_md_paths
from gzkit.surface_write import capture_surface_writes
from gzkit.sync_surfaces import is_managed_codex_config, render_codex_config, sync_all

#: Every root ``gz validate --surfaces`` compares against ``sync_all``'s output.
#:
#: A hand-maintained list cannot announce what it has fallen behind: a file
#: outside these roots drops out of BOTH sides of the comparison at once and
#: cancels, so the check reports clean on a domain it does not cover. That is
#: how 21 vendor persona mirrors and one copilot hook stayed unchecked while
#: ``sync_all`` rewrote them on every run (GHI #893) -- persona mirrors being
#: governance surfaces under ``AGENTS.md`` § Persona, where a hand-edit silently
#: changes agent behaviour.
#:
#: The witness is a census, not vigilance:
#: ``tests/test_validate_sync_parity.py::SyncParityDomainCoversEveryWriteTest``
#: asserts every path ``sync_all`` writes is declared here, under a nested
#: ``AGENTS.md`` path, or on that test's explicit out-of-domain list. Adding a
#: surface to the writer without adding it here now fails that test.
SURFACE_ROOTS: tuple[str, ...] = (
    ".gzkit/manifest.json",
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".github/discovery-index.json",
    ".github/instructions",
    ".claude/settings.json",
    ".claude/hooks",
    ".github/copilot/hooks",
    ".claude/rules",
    ".claude/skills",
    ".agents/skills",
    ".github/skills",
    ".agents/personas",
    ".claude/personas",
    ".github/personas",
    ".copilotignore",
)


def _nested_agents_md(project_root: Path) -> list[str]:
    """Every nested ``AGENTS.md`` a sync may write, derived from the writer itself.

    This was a hand-maintained 3-entry tuple, and that was the defect: ``sync_all``
    writes one nested ``AGENTS.md`` per shared-rule subtree — ~19 on this tree —
    so the old snapshot captured 3 and the restore could put back only those 3.
    A read-only ``gz validate --surfaces`` therefore left 16 files modified, and
    reported as drift the very bytes it had just written. The snapshot/restore
    envelope is gone (GHI #891), but the completeness requirement outlived it:
    this set is also what ``_render_expected`` carries at current bytes for the
    files sync never touches. Deriving it from
    :func:`gzkit.rules.nested_agents_md_paths` makes snapshot/restore complete by
    construction rather than by remembering to extend a literal.
    """
    return sorted(
        path.relative_to(project_root).as_posix() for path in nested_agents_md_paths(project_root)
    )


_SYNC_DATE_LINE = re.compile(rb"^- \*\*Updated\*\*: \d{4}-\d{2}-\d{2}", re.MULTILINE)
_PYTHON_RUNTIME_CACHE_SUFFIXES = frozenset({".pyc", ".pyo"})


def _is_python_runtime_cache(path: Path) -> bool:
    """Return True for ignored Python bytecode under generated surfaces."""
    return "__pycache__" in path.parts or path.suffix in _PYTHON_RUNTIME_CACHE_SUFFIXES


def _collect_files(project_root: Path, config: GzkitConfig | None = None) -> set[Path]:
    """Return every tracked generated file under the configured surface roots."""
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")
    collected: set[Path] = set()
    candidates: list[str] = [*SURFACE_ROOTS, *_nested_agents_md(project_root)]
    for rel in candidates:
        abs_path = project_root / rel
        if abs_path.is_file():
            collected.add(abs_path)
            continue
        if abs_path.is_dir():
            for path in abs_path.rglob("*"):
                if path.is_file() and not _is_python_runtime_cache(path):
                    collected.add(path)
    try:
        codex_config = resolve_codex_config_path(project_root, config.paths.codex_config)
    except ValueError:
        return collected
    if codex_config.is_file() and is_managed_codex_config(codex_config.read_bytes()):
        collected.add(codex_config)
    default_path = resolve_codex_config_path(project_root, CODEX_CONFIG_DEFAULT_PATH)
    if codex_config != default_path and default_path.is_file():
        collected.add(default_path)
    return collected


def _normalize(content: bytes) -> bytes:
    """Strip volatile sync-timestamp lines so operational drift is not false drift."""
    return _SYNC_DATE_LINE.sub(b"- **Updated**: <DATE>", content)


def _read_bytes_map(files: set[Path]) -> dict[Path, bytes]:
    """Read current bytes for each file, skipping any that cannot be read."""
    contents: dict[Path, bytes] = {}
    for path in files:
        try:
            contents[path] = path.read_bytes()
        except OSError:
            continue
    return contents


def _render_expected(project_root: Path, config: GzkitConfig) -> dict[Path, bytes]:
    """Return the bytes ``sync_all()`` would leave on disk, without writing any.

    Three sources compose into one expected map:

    * files sync means to WRITE -- captured with their intended bytes, including
      the ones already matching, because an unchanged write still asserts "this
      file should exist with these content";
    * files sync means to DELETE -- excluded, so they fall out of the caller's
      diff as stale;
    * files sync never touches -- carried at their CURRENT bytes. Omitting them
      would report every unmanaged file under a surface root as stale, which is
      the one way a render-and-compare check can be wrong where a
      sync-and-restore check was right.
    """
    current = _collect_files(project_root, config)
    expected = _read_bytes_map(current)
    with capture_surface_writes() as sink:
        sync_all(project_root, config, emit_event=False)
    for path in sink.removed:
        expected.pop(path, None)
    tracked = _tracked_roots(project_root, config)
    expected.update(
        {
            path: payload
            for path, payload in sink.written.items()
            if path in current or _is_tracked(path, tracked)
        }
    )
    return expected


def _tracked_roots(project_root: Path, config: GzkitConfig) -> set[Path]:
    """Return the roots :func:`_collect_files` walks, resolved."""
    roots = {(project_root / rel).resolve() for rel in SURFACE_ROOTS}
    roots.update(path.resolve() for path in nested_agents_md_paths(project_root))
    with contextlib.suppress(ValueError):
        roots.add(resolve_codex_config_path(project_root, config.paths.codex_config).resolve())
    roots.add(resolve_codex_config_path(project_root, CODEX_CONFIG_DEFAULT_PATH).resolve())
    return roots


def _is_tracked(path: Path, tracked: set[Path]) -> bool:
    """Whether ``path`` falls inside the parity domain.

    ``sync_all`` writes surfaces this check does not track -- the vendor persona
    mirrors under ``.agents/personas/``, ``.claude/personas/`` and
    ``.github/personas/`` are generated on every run and appear in no entry of
    ``SURFACE_ROOTS``. The old shape could not notice: ``expected`` was built by
    re-walking ``_collect_files`` AFTER the sync, so anything outside the tracked
    roots fell out of both sides at once. Rendering into a sink makes the write
    set visible for the first time, and without this filter 22 always-present
    persona files report as "sync_all() would create it".

    The parity DOMAIN is deliberately unchanged here: this fix removes the write,
    and widening what parity covers is a separate question with its own drift to
    triage. That the persona mirrors are generated-but-unchecked is disclosed as
    a follow-on, not quietly fixed under this one.
    """
    return path in tracked or any(path.is_relative_to(root) for root in tracked)


def plan_sync_all(project_root: Path, config: GzkitConfig | None = None) -> list[str]:
    """Return the exact list of paths ``sync_all()`` would write, without mutating disk.

    Runs the real ``sync_all()`` orchestrator inside a snapshot-restore envelope
    so the complete write set is derived from the same code path as apply mode.
    Used by ``gz agent sync control-surfaces --dry-run`` to preview an exact
    deterministic plan instead of a hand-maintained subset.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    planned: list[str] = []
    with capture_surface_writes():
        raw_planned = list(sync_all(project_root, config, emit_event=False))
    for entry in raw_planned:
        candidate = Path(entry)
        if candidate.is_absolute():
            try:
                planned.append(candidate.relative_to(project_root).as_posix())
            except ValueError:
                planned.append(candidate.as_posix())
        else:
            planned.append(candidate.as_posix())
    return sorted(set(planned))


def snapshot_surfaces(project_root: Path, config: GzkitConfig | None = None) -> dict[Path, bytes]:
    """Capture current surface-file bytes without running ``sync_all()``.

    Useful when the caller already knows the tree is in a synced state
    (e.g. immediately after ``gz init`` or a successful sync) and wants
    to feed that snapshot to ``check_sync_parity(..., expected=...)``
    without paying a second ``sync_all`` pass.
    """
    return _read_bytes_map(_collect_files(project_root, config))


def compute_expected_surfaces(
    project_root: Path, config: GzkitConfig | None = None
) -> dict[Path, bytes]:
    """Run ``sync_all()`` and return the bytes it produces, keyed by absolute path.

    The caller's working tree is not mutated: the sync renders into a capture
    sink rather than onto disk (GHI #891). Intended for
    callers (tests, repeated audits) that will compare many tree states
    against the same canonical output and want to pay the sync cost once.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    return _render_expected(project_root, config)


def _diff_against_expected(
    project_root: Path,
    current_snapshot: dict[Path, bytes],
    current_files: set[Path],
    expected: dict[Path, bytes],
) -> list[ValidationError]:
    """Produce drift errors comparing ``current_snapshot`` against ``expected``."""
    # Normalize every path to resolved form so set intersections and relative_to
    # work across macOS /var ↔ /private/var symlink mismatches (expected may
    # have been snapshotted from an unresolved path by the caller).
    project_root = project_root.resolve()
    current_snapshot = {p.resolve(): b for p, b in current_snapshot.items()}
    current_files = {p.resolve() for p in current_files}
    expected = {p.resolve(): b for p, b in expected.items()}
    errors: list[ValidationError] = []
    expected_paths = set(expected)

    shared = current_files & expected_paths
    created = expected_paths - current_files
    removed = current_files - expected_paths

    for path in sorted(shared):
        old = _normalize(current_snapshot.get(path, b""))
        new = _normalize(expected[path])
        if old != new:
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=path.relative_to(project_root).as_posix(),
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
                artifact=path.relative_to(project_root).as_posix(),
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
                artifact=path.relative_to(project_root).as_posix(),
                message=(
                    "Stale surface — sync_all() would remove it. "
                    "Run `uv run gz agent sync control-surfaces` to repair."
                ),
            )
        )

    return errors


def _codex_config_parity_errors(project_root: Path, config: GzkitConfig) -> list[ValidationError]:
    """Report preserved Codex drift that sync intentionally will not overwrite."""
    errors: list[ValidationError] = []
    artifact = Path(config.paths.codex_config).as_posix()
    try:
        config_path = resolve_codex_config_path(project_root, artifact)
    except ValueError as exc:
        return [ValidationError(type="surface", artifact=artifact, message=str(exc))]
    if config_path.exists() and not config_path.is_file():
        return [
            ValidationError(
                type="surface",
                artifact=artifact,
                message="Configured Codex config path is not a regular file.",
            )
        ]
    if config_path.is_file():
        content = config_path.read_bytes()
        if is_managed_codex_config(content) and content != render_codex_config().encode():
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=artifact,
                    message="Managed Codex config drift is preserved for operator review.",
                )
            )
    default_path = resolve_codex_config_path(project_root, CODEX_CONFIG_DEFAULT_PATH)
    rendered = render_codex_config().encode()
    if config_path != default_path and default_path.is_file():
        default_content = default_path.read_bytes()
        if default_content in (b"", rendered):
            return errors
        errors.append(
            ValidationError(
                type="surface",
                artifact=CODEX_CONFIG_DEFAULT_PATH,
                message=f"Obsolete default Codex config conflicts with {artifact}.",
            )
        )
    return errors


def check_sync_parity(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    expected: dict[Path, bytes] | None = None,
) -> list[ValidationError]:
    """Detect drift between generated surfaces and the output of ``sync_all()``.

    By default the check renders what ``sync_all()`` would produce into a
    capture sink and byte-compares it against the tree. Nothing is written --
    not on a clean tree, and not on a drifted one (GHI #891).

    If ``expected`` is supplied (produced by ``compute_expected_surfaces``
    or by ``snapshot_surfaces`` when the caller already knows the tree is
    synced), the sync step is skipped and the current tree is compared
    directly against the pre-computed expected state. Intended for callers
    — tests, repeated audits — that drive many comparisons against the
    same canonical state and want to pay the sync cost once.
    """
    # Resolve to canonical form so Path.relative_to(project_root) works on
    # macOS where /var is a symlink to /private/var: _collect_files walks a
    # resolved tree while Path.cwd() can hand back the unresolved prefix.
    project_root = project_root.resolve()

    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    pre_files = _collect_files(project_root, config)
    snapshot_bytes = _read_bytes_map(pre_files)
    codex_errors = _codex_config_parity_errors(project_root, config)

    try:
        codex_config = resolve_codex_config_path(project_root, config.paths.codex_config)
    except ValueError:
        return codex_errors
    if codex_config.exists() and not codex_config.is_file():
        return codex_errors

    if expected is not None:
        if codex_config.is_file() and not is_managed_codex_config(codex_config.read_bytes()):
            expected = {
                path: content
                for path, content in expected.items()
                if path.resolve() != codex_config
            }
        return [
            *codex_errors,
            *_diff_against_expected(project_root, snapshot_bytes, pre_files, expected),
        ]

    return [
        *codex_errors,
        *_diff_against_expected(
            project_root,
            snapshot_bytes,
            pre_files,
            _render_expected(project_root, config),
        ),
    ]
