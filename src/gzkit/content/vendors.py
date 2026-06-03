"""Vendor routing helpers for the agent control surface render pipeline.

ADR-0.0.34 § Decision item #8: vendor-manifest-expansion. The canonical
declaration of which content types render to which vendor mirrors lives in
``data/vendor-manifest.json``. This module reads that file when a project
root is supplied; otherwise it falls back to an in-code table that mirrors
the same routes at initial release so callers without a project root (for
example, the render pipeline in isolation tests) still work.
"""

from __future__ import annotations

import json
from pathlib import Path

# Fallback routing table used when project_root is not supplied.
# Mirrors data/vendor-manifest.json at initial release. Update both surfaces
# together when extending vendor coverage.
_FALLBACK_ROUTES: dict[str, list[str]] = {
    "AgentContract": ["claude", "codex"],
    "Bullet": ["claude"],
    "Chore": ["claude"],
    "Handoff": ["claude"],
    "Persona": ["claude"],
    "Rule": ["claude"],
    "Scenario": ["claude"],
    "Skill": ["claude"],
}

_MANIFEST_REL = Path("data") / "vendor-manifest.json"

# NB: temperature has no in-code fallback table by design (operator directive
# 2026-06-03). Unlike vendor routes, temperature is a general control whose
# values are configuration, never an in-code vendor-identity rule — so a
# (content_type, vendor) pair with no manifest declaration fails closed rather
# than resolving to a baked-in default. See temperature_for below.


def _load_manifest(project_root: Path) -> dict[str, list[str]]:
    """Load ``content_type_routes`` from ``data/vendor-manifest.json``.

    Returns an empty dict if the file is missing or malformed — callers
    handle fallback. Schema validation is the responsibility of
    ``gz validate --vendor-manifest`` (see
    ``gzkit.governance.trust_audits.vendor_manifest``).
    """
    manifest_path = project_root / _MANIFEST_REL
    if not manifest_path.is_file():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    routes = data.get("content_type_routes", {})
    if not isinstance(routes, dict):
        return {}
    # Normalize to dict[str, list[str]] — drop anything that does not conform.
    typed: dict[str, list[str]] = {}
    for key, value in routes.items():
        if isinstance(key, str) and isinstance(value, list):
            typed[key] = [v for v in value if isinstance(v, str)]
    return typed


def _load_temperatures(project_root: Path) -> dict[str, dict[str, str]]:
    """Load ``content_type_temperatures`` from ``data/vendor-manifest.json``.

    Returns an empty dict if the file is missing, malformed, or has no temperatures key.
    """
    manifest_path = project_root / _MANIFEST_REL
    if not manifest_path.is_file():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    temps = data.get("content_type_temperatures", {})
    if not isinstance(temps, dict):
        return {}
    typed: dict[str, dict[str, str]] = {}
    for ct, vendor_map in temps.items():
        if isinstance(ct, str) and isinstance(vendor_map, dict):
            typed[ct] = {
                k: v for k, v in vendor_map.items() if isinstance(k, str) and isinstance(v, str)
            }
    return typed


def routes_for(content_type: str, *, project_root: Path | None = None) -> list[str]:
    """Return the vendor mirrors registered for *content_type*.

    When ``project_root`` is supplied, reads ``data/vendor-manifest.json`` and
    returns the manifest-declared mirrors. When ``project_root`` is ``None``,
    falls back to the in-code :data:`_FALLBACK_ROUTES` table.

    Returns an empty list when the content type is not registered — callers
    treat that as fail-closed.
    """
    if project_root is not None:
        routes = _load_manifest(project_root)
        if routes:
            return routes.get(content_type, [])
    return _FALLBACK_ROUTES.get(content_type, [])


def all_routes(*, project_root: Path | None = None) -> dict[str, list[str]]:
    """Return the full ``content_type -> vendors`` mapping.

    When ``project_root`` is supplied and the manifest is present and parseable,
    returns the manifest-declared map; otherwise returns the in-code fallback.
    """
    if project_root is not None:
        routes = _load_manifest(project_root)
        if routes:
            return routes
    return dict(_FALLBACK_ROUTES)


def temperature_for(content_type: str, vendor: str, *, project_root: Path | None = None) -> str:
    """Return the manifest-declared temperature for the (content_type, vendor) pair.

    Temperature is a general control resolved purely from
    ``data/vendor-manifest.json`` ``content_type_temperatures`` — there is no
    in-code default pairing. Any (content_type, vendor) that is not declared
    (including when ``project_root`` is absent, so no manifest is readable)
    fails closed with ``ValueError`` rather than resolving to a baked-in tier
    (REQ-0.0.37-15-02; operator directive 2026-06-03 — no vendor-locked rule).
    """
    temps = _load_temperatures(project_root) if project_root is not None else {}
    vendor_map = temps.get(content_type, {})
    if vendor in vendor_map:
        return vendor_map[vendor]
    raise ValueError(
        f"No temperature declared for ({content_type!r}, {vendor!r}) "
        f"in {_MANIFEST_REL}; declare it in content_type_temperatures "
        f"(REQ-0.0.37-15-02 fail-closed)."
    )
