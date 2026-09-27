"""Hashes of every canonical-surface file version gzkit has shipped (GHI #1122).

``gz init --update`` and ``gz upgrade`` read this history to tell an unedited
project copy from an operator edit: a copy whose bytes match a version gzkit
shipped is safe to refresh, and any other difference is the operator's. This is
the content-hash mechanism of OBPI-0.0.32-05 requirement 4(b), chosen by
operator ruling on GHI #1122 in place of a body marker no scaffolder wrote.

``sync_pkg_surfaces`` appends the hash of every file it ships, so the history
stays complete by construction, and entries are never removed: an adopter may
hold any version ever released. The first entries were backfilled from the
release tags on 2026-09-27.
"""

import hashlib
import importlib.resources
import json
from pathlib import Path

from gzkit.skills import delivered_skill_body, delivered_skill_slugs
from gzkit.surface_write import effective_bytes, effective_files, write_if_changed

HISTORY_FILE = "canonical_history.json"
CANONICAL_SURFACES = ("skills", "rules", "chores", "personas", "templates")
_SCHEMA = "gzkit.canonical_history.v1"
_DESCRIPTION = (
    "sha256 of every canonical-surface file version gzkit has shipped, keyed by "
    "<surface>/<path>. Appended by `gz agent sync control-surfaces`; read by "
    "`gz init --update` and `gz upgrade` to tell an unedited copy from an edit "
    "(GHI #1122). Never hand-edited; entries are never removed."
)


def content_hash(payload: bytes) -> str:
    """Return the history's hash of ``payload``."""
    return hashlib.sha256(payload).hexdigest()


def load_canonical_history() -> dict[str, frozenset[str]]:
    """Return the installed wheel's history: ``<surface>/<path>`` to shipped hashes."""
    resource = importlib.resources.files("gzkit").joinpath(HISTORY_FILE)
    if not resource.is_file():
        return {}
    data = json.loads(resource.read_text(encoding="utf-8"))
    return {key: frozenset(hashes) for key, hashes in data.get("files", {}).items()}


def _shipped_files(pkg_root: Path) -> dict[str, bytes]:
    """Map each file the refresh walk would deliver to its (post-sync) bytes.

    Mirrors ``_walk_traversable``: any path part starting with ``_`` is package
    infrastructure (``__init__.py``, ``__pycache__``), never delivered content.
    """
    shipped: dict[str, bytes] = {}
    for surface in CANONICAL_SURFACES:
        surface_root = pkg_root / surface
        for path in effective_files(surface_root):
            rel = path.relative_to(surface_root.resolve())
            if any(part.startswith("_") for part in rel.parts):
                continue
            payload = effective_bytes(path)
            if payload is not None:
                shipped[f"{surface}/{rel.as_posix()}"] = payload
    return shipped


def delivered_variants(shipped: dict[str, bytes]) -> dict[str, set[bytes]]:
    """Map each shipped file to every form delivery can write for it.

    A file is delivered as its wheel bytes, except a skill router, whose rows
    are scoped to the skills that delivery lands (GHI #915): a freshly scaffolded
    adopter holds that scoped form, so the history must recognize it too.
    """
    bodies = {slug: shipped[key] for key in shipped if (slug := skill_body_slug(key))}
    delivered = delivered_skill_slugs(bodies)
    return {
        key: {payload, delivered_skill_body(payload, delivered)}
        if skill_body_slug(key)
        else {payload}
        for key, payload in shipped.items()
    }


def skill_body_slug(key: str) -> str | None:
    """Return the slug when ``key`` is a skill's ``SKILL.md`` (``skills/<slug>/SKILL.md``)."""
    parts = key.split("/")
    if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md":
        return parts[1]
    return None


def record_canonical_history(pkg_root: Path, project_root: Path, updated: list[str]) -> None:
    """Append the hash of every form ``pkg_root`` delivers; record the write in ``updated``."""
    history_path = pkg_root / HISTORY_FILE
    raw = effective_bytes(history_path)
    recorded = json.loads(raw).get("files", {}) if raw else {}
    files = {key: set(hashes) for key, hashes in recorded.items()}
    for key, forms in delivered_variants(_shipped_files(pkg_root)).items():
        files.setdefault(key, set()).update(content_hash(form) for form in forms)
    rendered = {
        "schema": _SCHEMA,
        "description": _DESCRIPTION,
        "files": {key: sorted(hashes) for key, hashes in sorted(files.items())},
    }
    if write_if_changed(history_path, (json.dumps(rendered, indent=2) + "\n").encode("utf-8")):
        updated.append(history_path.relative_to(project_root).as_posix())
