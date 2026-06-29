"""OKF bundle conformance audit (ADR-0.30.0 / OBPI-0.30.0-03).

`gz validate --okf-conformance` checks ONLY the GENERATED OKF bundle for
well-formedness. It is an orientation-layer guard, never an authority surface.

Two invariants from the parent ADR shape this scope:

* **Generated-bundle-only (Boundary Invariant 2).** The audit recognizes a
  bundle *structurally* — a directory under ``.gzkit/`` that contains a reserved
  ``index.md`` AND at least one type-bearing concept doc — NEVER by an
  ``okf/``-format folder name. Authored source documents (which live under
  ``docs/``, never scanned here) are therefore never flagged: a source doc with
  no OKF frontmatter is NOT a conformance failure.
* **Orientation, never authority (Boundary Invariant 1 — STRUCTURAL-FENCE).**
  This audit validates the bundle's OWN well-formedness and nothing else. It
  MUST NEVER be consumed — and MUST NEVER consume OKF ``type``/tag/link data —
  as enforcement evidence for any OTHER governance claim. Truth lives in canon
  (Layer-1) and the ledger (Layer-2); the bundle is a Layer-3 navigation aid.

Conformance rules for a detected bundle:

* Every non-reserved markdown file MUST have parseable YAML frontmatter and a
  non-empty ``type``.
* Reserved files (``index.md``/``log.md``) MUST have parseable frontmatter.

Failures emit ``ValidationError(type="okf_conformance", ...)`` naming the
offending file and field; a non-empty list maps to exit 3 in the orchestrator.
A clean bundle returns ``[]`` (exit 0).
"""

from __future__ import annotations

from pathlib import Path

import yaml

from gzkit.validate import ValidationError

__all__ = ["audit_okf_conformance"]

_GZKIT_ROOT = ".gzkit"
_RESERVED_FILES = frozenset({"index.md", "log.md"})
_INDEX_FILE = "index.md"


def _read_frontmatter(path: Path) -> tuple[dict | None, bool]:
    """Return ``(data, parse_ok)`` for a markdown file's YAML frontmatter.

    * ``parse_ok=False`` — a ``---``-delimited block is present but unparseable
      (or does not parse to a mapping).
    * ``parse_ok=True, data=None`` — no frontmatter block present.
    * ``parse_ok=True, data=dict`` — parsed mapping.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return (None, True)
    parts = text.split("---", 2)
    if len(parts) < 3:
        return (None, False)
    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return (None, False)
    if data is None:
        return (None, True)
    if not isinstance(data, dict):
        return (None, False)
    return (data, True)


def _has_nonempty_type(data: dict | None) -> bool:
    return bool(data) and isinstance(data.get("type"), str) and data["type"].strip() != ""


def _is_bundle_root(directory: Path) -> bool:
    """A directory is an OKF bundle root iff it has a reserved ``index.md`` AND
    a type-bearing OKF signal — either the reserved ``index.md`` itself carries a
    ``type``, or at least one type-bearing concept doc is present (Boundary
    Invariant 2 — structural recognition by reserved files + ``type``, never by an
    ``okf/`` folder name).

    Reading the reserved ``index.md``'s own ``type`` as a detection signal means a
    bundle whose concept docs were all stripped of frontmatter (e.g. a generator
    regression) is still recognized — and therefore flagged — rather than going
    invisible to the audit."""
    index = directory / _INDEX_FILE
    if not index.is_file():
        return False
    index_data, index_ok = _read_frontmatter(index)
    if index_ok and _has_nonempty_type(index_data):
        return True
    for md in directory.glob("*.md"):
        if md.name in _RESERVED_FILES:
            continue
        data, parse_ok = _read_frontmatter(md)
        if parse_ok and _has_nonempty_type(data):
            return True
    return False


def _validate_file(path: Path, project_root: Path) -> list[ValidationError]:
    """Validate one bundle markdown file; reserved files need only parseable
    frontmatter, concept docs additionally need a non-empty ``type``."""
    rel = path.relative_to(project_root).as_posix()
    data, parse_ok = _read_frontmatter(path)
    reserved = path.name in _RESERVED_FILES
    if not parse_ok:
        return [
            ValidationError(
                type="okf_conformance",
                artifact=rel,
                message=f"{rel}: unparseable OKF frontmatter (field: frontmatter)",
            )
        ]
    if data is None:
        return [
            ValidationError(
                type="okf_conformance",
                artifact=rel,
                message=f"{rel}: missing OKF frontmatter (field: frontmatter)",
            )
        ]
    if not reserved and not _has_nonempty_type(data):
        return [
            ValidationError(
                type="okf_conformance",
                artifact=rel,
                message=f"{rel}: missing or empty required field (field: type)",
            )
        ]
    return []


def audit_okf_conformance(project_root: Path) -> list[ValidationError]:
    """Audit every detected OKF bundle under ``.gzkit/`` for conformance.

    Generated-bundle-only (Boundary Invariant 2): authored source docs under
    ``docs/`` are never scanned, so they can never be flagged.
    """
    gzkit_dir = project_root / _GZKIT_ROOT
    if not gzkit_dir.is_dir():
        return []
    errors: list[ValidationError] = []
    directories = [gzkit_dir, *(d for d in gzkit_dir.rglob("*") if d.is_dir())]
    for directory in directories:
        if not _is_bundle_root(directory):
            continue
        for md in sorted(directory.glob("*.md")):
            errors.extend(_validate_file(md, project_root))
    return errors
