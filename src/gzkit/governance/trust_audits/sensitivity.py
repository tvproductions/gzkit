"""Sensitivity-binding trust audit (ADR-0.0.22).

Auto-detect floor: brief allowed paths are intersected against the
``data/security_surfaces.json`` registry; if the intersection is non-empty
the brief's declared sensitivity must be either absent (floor) or
``security`` (escalation). Anything else is an escape attempt and fails
closed.
"""

from __future__ import annotations

import json
import re
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

from gzkit.governance.trust_audits.taxonomy import _parse_adr_frontmatter
from gzkit.validate import ValidationError

if TYPE_CHECKING:
    from gzkit.models.security_surfaces import SecuritySurfaceEntry

_SENSITIVITY_REGISTRY_REL = Path("data") / "security_surfaces.json"
_FLOOR_GRANDFATHER_REL = Path("data") / "sensitivity_floor_grandfather.json"

_SENSITIVITY_ALLOWED_PATHS_RE = re.compile(
    r"^##\s+ALLOWED\s+PATHS\s*$", re.MULTILINE | re.IGNORECASE
)
_SENSITIVITY_BRIEF_SECTION_RE = re.compile(r"^## ", re.MULTILINE)
_SENSITIVITY_BULLET_PATH_RE = re.compile(r"-\s+`([^`]+)`")


def _load_floor_grandfather(project_root: Path) -> frozenset[str]:
    """Return the set of grandfathered brief rel-paths (GHI #625 cutover).

    These briefs predate the tightening of the auto-detect floor to fail closed
    on an omitted declaration over a registered security overlap. A missing or
    malformed file means *nothing* is grandfathered (empty set) — absence must
    not silently widen the waiver, but it is not itself fail-closed (the floor
    enforcement does not depend on the grandfather file existing).
    """
    gf_path = project_root / _FLOOR_GRANDFATHER_REL
    if not gf_path.is_file():
        return frozenset()
    try:
        payload = json.loads(gf_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return frozenset()
    briefs = payload.get("grandfathered_briefs", []) if isinstance(payload, dict) else []
    return frozenset(p for p in briefs if isinstance(p, str))


def _load_sensitivity_registry(
    project_root: Path,
) -> tuple[tuple[SecuritySurfaceEntry, ...] | None, ValidationError | None]:
    """Load the security-surfaces registry; return (entries, error).

    Returns (registry, None) on success or (None, fail-closed-error) when the
    registry is missing, unparseable, or schema-invalid. The error is shaped
    so it composes with the rest of the audit's findings without raising.
    """
    from gzkit.models.security_surfaces import load_registry

    registry_path = project_root / _SENSITIVITY_REGISTRY_REL
    if not registry_path.is_file():
        return None, ValidationError(
            type="sensitivity-registry-missing",
            artifact=_SENSITIVITY_REGISTRY_REL.as_posix(),
            message=(
                "data/security_surfaces.json is missing; sensitivity audit "
                "fails closed (ADR-0.0.22). Restore the registry or check it in."
            ),
        )
    try:
        registry = load_registry(registry_path)
    except json.JSONDecodeError as exc:
        return None, ValidationError(
            type="sensitivity-registry-malformed",
            artifact=_SENSITIVITY_REGISTRY_REL.as_posix(),
            message=f"Registry JSON is unparseable: {exc.msg} (line {exc.lineno}).",
        )
    except (ValueError, TypeError) as exc:
        return None, ValidationError(
            type="sensitivity-registry-malformed",
            artifact=_SENSITIVITY_REGISTRY_REL.as_posix(),
            message=f"Registry rejects schema: {exc}",
        )
    return registry, None


def _extract_sensitivity_allowed_paths(brief_text: str) -> list[str]:
    """Pull the bullet-quoted paths out of the brief's ``## ALLOWED PATHS`` block."""
    match = _SENSITIVITY_ALLOWED_PATHS_RE.search(brief_text)
    if not match:
        return []
    rest = brief_text[match.end() :]
    next_section = _SENSITIVITY_BRIEF_SECTION_RE.search(rest)
    section_text = rest[: next_section.start()] if next_section else rest
    paths: list[str] = []
    for raw_line in section_text.splitlines():
        bullet = raw_line.strip()
        if not bullet.startswith("- "):
            continue
        path_match = _SENSITIVITY_BULLET_PATH_RE.match(bullet)
        if path_match:
            paths.append(path_match.group(1))
    return paths


def _iter_sensitivity_briefs(project_root: Path) -> list[Path]:
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    briefs: list[Path] = []
    for sub in ("obpis", "briefs"):
        for brief in adr_root.rglob(f"{sub}/*.md"):
            briefs.append(brief)
    return sorted(briefs)


_DECLARED_SENSITIVITY_NULL_TOKENS: frozenset[str] = frozenset({"None", "null", "~"})


def _normalize_declared_sensitivity(declared: object) -> str | None:
    """Reduce a declared sensitivity field to ``None`` or a non-empty string."""
    if not isinstance(declared, str):
        return None
    norm: str | None = declared.strip() or None
    if norm in _DECLARED_SENSITIVITY_NULL_TOKENS:
        return None
    return norm


def _classify_brief_sensitivity(
    brief_path: Path,
    brief_text: str,
    project_root: Path,
    registry: tuple[SecuritySurfaceEntry, ...],
    grandfather: frozenset[str] = frozenset(),
) -> ValidationError | None:
    """Return the single finding (if any) implied by one brief's sensitivity binding."""
    from gzkit.models.security_surfaces import match_globs

    rel = brief_path.relative_to(project_root).as_posix()
    frontmatter = _parse_adr_frontmatter(brief_path) or {}
    declared_norm = _normalize_declared_sensitivity(frontmatter.get("sensitivity"))

    allowed_paths = _extract_sensitivity_allowed_paths(brief_text)
    try:
        matching_categories = match_globs(allowed_paths, registry)
    except (ValueError, TypeError):
        return ValidationError(
            type="sensitivity-malformed-allowlist",
            artifact=rel,
            message=(
                "Allowed Paths contains an unparseable glob; sensitivity intersection skipped."
            ),
        )

    if not matching_categories:
        return None

    if declared_norm not in (None, "security"):
        return ValidationError(
            type="sensitivity-escape-attempt",
            artifact=rel,
            message=(
                f"Brief declares sensitivity={declared_norm!r} but allowed "
                f"paths intersect security-sensitive surfaces "
                f"(detected=security, categories={list(matching_categories)}, "
                f"intersecting_paths={allowed_paths}). Escalate-not-escape: "
                "remove the declaration or set sensitivity: security."
            ),
        )

    if declared_norm is None:
        # Omission over a registered security overlap is fail-closed
        # (.gzkit/rules/security-sensitivity.md §§ 1-2, GHI #625). Briefs in the
        # grandfather cutover set predate the enforcement and remain at the
        # informational floor; everything else fails closed.
        if rel in grandfather:
            return ValidationError(
                type="sensitivity-floor-info",
                artifact=rel,
                message=(
                    f"Auto-detect floor active (grandfathered, GHI #625): "
                    f"detected_sensitivity=security, declared_sensitivity=None, "
                    f"intersecting_paths={allowed_paths}, "
                    f"registry_categories={list(matching_categories)}."
                ),
            )
        return ValidationError(
            type="sensitivity-floor-violation",
            artifact=rel,
            message=(
                f"Brief omits sensitivity: while allowed paths intersect "
                f"registered security surfaces (detected=security, "
                f"categories={list(matching_categories)}, "
                f"intersecting_paths={allowed_paths}). "
                f".gzkit/rules/security-sensitivity.md §§ 1-2 (escalate-not-escape): "
                f"omission over a security overlap is fail-closed. Declare "
                f"'sensitivity: security'; or if the overlap is an incidental "
                f"false positive, narrow the Allowed Paths or discharge at "
                f"completion via 'gz obpi complete --accept-security-floor'."
            ),
        )
    return None


def audit_sensitivity_binding(project_root: Path) -> list[ValidationError]:
    """Enforce ADR-0.0.22 sensitivity-binding (auto-detect floor + escalate-not-escape).

    Reads ``data/security_surfaces.json`` and walks every OBPI brief under
    ``docs/design/adr/**/{obpis,briefs}/*.md``. For each brief it intersects the
    bullet-quoted ``## ALLOWED PATHS`` glob list against the registry to compute
    a ``detected_sensitivity``; ``declared_sensitivity`` is read from frontmatter.
    The decision matrix (ADR-0.0.22) lives in ``_classify_brief_sensitivity``.
    """
    briefs = _iter_sensitivity_briefs(project_root)
    if not briefs:
        return []

    registry, registry_error = _load_sensitivity_registry(project_root)
    if registry_error is not None:
        return [registry_error]
    assert registry is not None  # noqa: S101 — narrowed for ty

    grandfather = _load_floor_grandfather(project_root)
    errors: list[ValidationError] = []
    for brief_path in briefs:
        try:
            brief_text = brief_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        finding = _classify_brief_sensitivity(
            brief_path, brief_text, project_root, registry, grandfather
        )
        if finding is not None:
            errors.append(finding)
    return errors


def detect_brief_security_floor(
    brief_text: str,
    project_root: Path,
) -> str | None:
    """Return ``"security"`` when brief allowed paths intersect the registry, else ``None``.

    Mirrors the auto-detect floor from :func:`audit_sensitivity_binding` so the
    OBPI completion runtime enforces the same security floor that the audit
    reports (GHI #413). When the registry is missing or unparseable the
    function returns ``None`` — :func:`audit_sensitivity_binding` already
    fail-closes that case at validate time, and completion falls through to
    the brief's declared sensitivity rather than masking a registry-state
    defect with a synthetic floor.
    """
    from gzkit.models.security_surfaces import match_globs

    registry, registry_error = _load_sensitivity_registry(project_root)
    if registry_error is not None or registry is None:
        return None

    allowed_paths = _extract_sensitivity_allowed_paths(brief_text)
    if not allowed_paths:
        return None

    try:
        matching = match_globs(allowed_paths, registry)
    except (ValueError, TypeError):
        return None

    return "security" if matching else None


def explain_sensitivity_for_paths(
    candidate_globs: Sequence[str],
    project_root: Path,
) -> dict[str, object]:
    """Predict classification for an ad-hoc path list without disk side effects.

    Returns a JSON-serializable payload:
        {
            "detected_sensitivity": "security" | None,
            "matching_categories": tuple[str, ...],
            "input_globs": tuple[str, ...],
        }

    On registry missing/malformed, the ``error`` key is populated and
    ``detected_sensitivity`` is ``None`` — the explain CLI still exits 0 because
    prediction without a registry is informational, not fail-closed.
    """
    from gzkit.models.security_surfaces import match_globs

    registry, registry_error = _load_sensitivity_registry(project_root)
    if registry_error is not None:
        return {
            "detected_sensitivity": None,
            "matching_categories": (),
            "input_globs": tuple(candidate_globs),
            "error": registry_error.message,
        }
    assert registry is not None  # noqa: S101

    matching = match_globs(candidate_globs, registry)
    return {
        "detected_sensitivity": "security" if matching else None,
        "matching_categories": tuple(matching),
        "input_globs": tuple(candidate_globs),
    }
