"""Chores-layout drift trust audit (ADR-0.0.21 Decision #9)."""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.validate import ValidationError

_CHORES_LAYOUT_FILES: frozenset[str] = frozenset({"CHORE.md", "acceptance.json"})

_CHORES_LAYOUT_EXCLUDED_SEGMENTS: frozenset[str] = frozenset(
    {"__pycache__", ".venv", "dist", "build", "node_modules"}
)


def _is_excluded_chore_path(rel_parts: tuple[str, ...]) -> bool:
    """Skip dotfile-hidden ancestors and excluded build/venv segments."""
    if any(seg.startswith(".") for seg in rel_parts[:-1]):
        return True
    return any(seg in _CHORES_LAYOUT_EXCLUDED_SEGMENTS for seg in rel_parts)


def _is_canonical_chore_path(rel_posix: str, canonical_roots: tuple[str, ...]) -> bool:
    return any(rel_posix.startswith(f"{root}/") for root in canonical_roots)


def audit_chores_layout(project_root: Path) -> list[ValidationError]:
    """Flag ``CHORE.md`` / ``acceptance.json`` outside canonical chores roots.

    ADR-0.0.21 Decision #9: chores live under exactly two roots —
    ``src/gzkit/chores/`` (canonical, shipped in the wheel) and the
    project-scoped ``paths.chores`` (default ``.gzkit/chores/``). Two vectors
    fail closed: (1) any ``CHORE.md`` or ``acceptance.json`` discovered
    outside both roots is layout drift; (2) ANY file under the forbidden
    legacy ``ops/chores/`` root is drift regardless of filename — bare proof
    debris (no ``CHORE.md`` beside it) re-creates the tree the migration
    erased and slipped past the filename-only check for a month (GHI #605).

    Walking semantics mirror the ``audit_utf8_prefix`` pattern: skip
    dotfile-hidden segments, ``__pycache__``/``.venv``/``dist``/``build``/
    ``node_modules``. Waiver entries in
    ``data/chores_layout_waivers.json`` (a JSON list of POSIX path strings)
    exempt explicitly-listed paths per trust-doctrine T2.
    """
    from gzkit.config import GzkitConfig  # noqa: PLC0415

    config = GzkitConfig.load(project_root / ".gzkit.json")
    project_chores_root = config.paths.chores.strip("/")
    canonical_roots = ("src/gzkit/chores", project_chores_root)

    waivers = _load_chores_layout_waivers(project_root)

    errors: list[ValidationError] = []
    for path in sorted(project_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(project_root)
        if _is_excluded_chore_path(rel.parts):
            continue
        rel_posix = rel.as_posix()
        if rel_posix in waivers or _is_canonical_chore_path(rel_posix, canonical_roots):
            continue
        if rel_posix.startswith("ops/chores/"):
            errors.append(
                ValidationError(
                    type="chores_layout",
                    artifact=rel_posix,
                    message=(
                        f"file under forbidden legacy `ops/chores/` root: {rel_posix}. "
                        "ADR-0.0.21 Decision #9 forbids the `ops/chores/` layout "
                        "entirely (the migration vector this audit closes), regardless "
                        "of filename — bare proof debris re-creates the tree (GHI #605). "
                        "Recovery: delete the file and rewrite the chore's proof-write "
                        f"path to `{project_chores_root}/<slug>/proofs/`."
                    ),
                )
            )
            continue
        if path.name not in _CHORES_LAYOUT_FILES:
            continue
        errors.append(
            ValidationError(
                type="chores_layout",
                artifact=rel_posix,
                message=(
                    f"stray {path.name} outside canonical chores roots "
                    f"(`src/gzkit/chores/`, `{project_chores_root}/`). "
                    "ADR-0.0.21 Decision #9 forbids ad-hoc chore layouts."
                ),
            )
        )
    return errors


def _load_chores_layout_waivers(project_root: Path) -> frozenset[str]:
    """Load waiver paths from ``data/chores_layout_waivers.json``.

    Returns an empty frozenset if the file is absent, empty, or
    malformed — the audit fails open on waiver IO so a missing file does
    not silently become a strict-mode escape hatch in either direction.
    """
    waiver_file = project_root / "data" / "chores_layout_waivers.json"
    if not waiver_file.is_file():
        return frozenset()
    try:
        payload = json.loads(waiver_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return frozenset()
    if not isinstance(payload, list):
        return frozenset()
    return frozenset(str(entry) for entry in payload if isinstance(entry, str))
