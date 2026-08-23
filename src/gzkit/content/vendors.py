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
    "AgentContract": ["root"],
    "Bullet": ["claude"],
    "Chore": ["claude"],
    "Handoff": ["claude"],
    "Persona": ["claude"],
    "Rule": ["claude"],
    "Scenario": ["claude"],
    "Skill": ["claude"],
}

# Which content type owns each rendered control surface — the INVERSE of
# _FALLBACK_ROUTES, and the authority that makes "is this consumer on-route for
# THIS surface" answerable. Without it a route test can only ask whether a
# consumer is routed for *something*, which grades a retained `claude.md` under
# `AGENTS.md/` because `claude` routes Rule, Skill, Persona and four others
# (GHI #840). Update both surfaces together, as with _FALLBACK_ROUTES.
_FALLBACK_SURFACE_CONTENT_TYPES: dict[str, str] = {
    "AGENTS.md": "AgentContract",
}

_MANIFEST_REL = Path("data") / "vendor-manifest.json"

# Legal compression-setpoint tokens. Mirrors the enum in
# src/gzkit/schemas/vendor_manifest.json
# (content_type_temperatures.additionalProperties.additionalProperties.enum);
# kept here as the in-code source the setpoint-coherence validator reads
# (OBPI-0.0.37-20). Schema validation owns shape; this owns the runtime token
# legality check used by gz validate --setpoint-coherence.
SETPOINT_TOKENS: frozenset[str] = frozenset({"lite", "medium", "heavy"})

# NB: temperature has no in-code fallback table by design (operator directive
# 2026-06-03). Unlike vendor routes, temperature is a general control whose
# values are configuration, never an in-code vendor-identity rule — so a
# (content_type, vendor) pair with no manifest declaration fails closed rather
# than resolving to a baked-in default. See temperature_for below.


def _read_manifest_key(project_root: Path, key: str) -> dict[str, object]:
    """Read one top-level mapping from ``data/vendor-manifest.json``.

    Returns an empty dict if the file is missing, unparseable, or the key is
    absent or not a mapping — callers handle fallback. Schema validation is the
    responsibility of ``gz validate --vendor-manifest`` (see
    ``gzkit.governance.trust_audits.vendor_manifest``).
    """
    manifest_path = project_root / _MANIFEST_REL
    if not manifest_path.is_file():
        return {}
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    # A top-level non-object parses cleanly and then has no `.get` — `[]`, `"x"`,
    # `null`, `3` all reach here as valid JSON. Without this guard the docstring
    # above is false for "unparseable", and the AttributeError escapes into every
    # caller. That matters most at the corpus-mutation seam
    # (`commands/content/_drift.warn_on_rendition_drift`), whose handler catches
    # only `(OSError, ValueError)` under a stated contract that "no fault here may
    # cost the operator their words or their exit code" — an AttributeError there
    # costs the exit code after the corpus row is already durable, and reports it
    # as a bare `Unexpected error: 'list' object has no attribute 'get'`.
    if not isinstance(data, dict):
        return {}
    section = data.get(key, {})
    return section if isinstance(section, dict) else {}


def _load_manifest(project_root: Path) -> dict[str, list[str]]:
    """Load ``content_type_routes``, dropping anything that does not conform."""
    routes = _read_manifest_key(project_root, "content_type_routes")
    # Normalize to dict[str, list[str]] — drop anything that does not conform.
    typed: dict[str, list[str]] = {}
    for key, value in routes.items():
        if isinstance(key, str) and isinstance(value, list):
            typed[key] = [v for v in value if isinstance(v, str)]
    return typed


def _load_temperatures(project_root: Path) -> dict[str, dict[str, str]]:
    """Load ``content_type_temperatures``, dropping anything that does not conform."""
    temps = _read_manifest_key(project_root, "content_type_temperatures")
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


def content_type_for_surface(surface: str, *, project_root: Path | None = None) -> str | None:
    """Return the content type that owns *surface*, or ``None`` when unmapped.

    ``None`` means "this project declares no owner for that surface" and is a
    real answer, not an error: callers decide what an unmapped surface means for
    them rather than having a guess imposed here.
    """
    if project_root is not None:
        declared = _read_manifest_key(project_root, "surface_content_types")
        if declared:
            owner = declared.get(surface)
            return owner if isinstance(owner, str) else None
    return _FALLBACK_SURFACE_CONTENT_TYPES.get(surface)


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


def delivery_cap_for(
    content_type: str, vendor: str, *, project_root: Path | None = None
) -> int | None:
    """Return the vendor's hard delivery limit in bytes, or ``None`` if unknown.

    A delivery cap is an *observed fact about someone else's product* — Codex
    silently truncates root ``AGENTS.md`` past ``project_doc_max_bytes``
    (openai/codex#7138). That is why this resolver fails **open** where
    :func:`temperature_for` fails closed: temperature is a control gzkit
    chooses, so an undeclared value is an authoring omission worth blocking on,
    whereas an undeclared cap means gzkit knows of no limit for that vendor.
    Fail-closing here would force an agent to invent a byte cap for every
    vendor, fabricating adapter constraints to satisfy a gate (GHI #712).
    """
    caps = _read_manifest_key(project_root, "content_type_delivery_caps") if project_root else {}
    vendor_map = caps.get(content_type)
    if not isinstance(vendor_map, dict):
        return None
    cap = vendor_map.get(vendor)
    return cap if isinstance(cap, int) and not isinstance(cap, bool) else None


def binding_delivery_cap(
    content_type: str, *, project_root: Path | None = None
) -> tuple[int, str] | None:
    """Return the ``(cap, vendor)`` a single delivered surface must satisfy.

    A content type routed to ONE surface serving every harness must fit the
    **smallest** cap any harness declares — the strictest constraint binds,
    because one file cannot be short for Codex and long for everyone else.

    This exists because per-route lookup stops working the moment routing
    collapses: ``AgentContract`` routes to ``root``, no vendor named ``root``
    publishes a ``project_doc_max_bytes``, and a per-route resolver therefore
    finds no cap and falls silent — losing the truncation witness precisely when
    a single shared surface makes it matter most.

    Returns ``None`` when no cap is declared. Fails **open** for the reason
    :func:`delivery_cap_for` does: an undeclared cap means gzkit knows of no
    limit, and fail-closing would force an agent to invent byte caps.
    """
    caps = _read_manifest_key(project_root, "content_type_delivery_caps") if project_root else {}
    vendor_map = caps.get(content_type)
    if not isinstance(vendor_map, dict):
        return None
    declared = [
        (value, vendor)
        for vendor, value in vendor_map.items()
        if isinstance(vendor, str) and isinstance(value, int) and not isinstance(value, bool)
    ]
    if not declared:
        return None
    cap, vendor = min(declared)
    return cap, vendor
