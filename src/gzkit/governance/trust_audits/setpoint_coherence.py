"""Setpoint-coherence trust audit (ADR-0.0.37 OBPI-0.0.37-20).

Enforces the setpoint-thermostat coherence rule: every ``(content_type, vendor)``
pair declared in ``data/vendor-manifest.json`` ``content_type_routes`` MUST carry
a legal declared setpoint in ``content_type_temperatures``. The setpoint is the
compression target the authoring-time composer drives toward (parent ADR
§ Decision Re-Alignment, re-aimed mechanism part 2); this gate asserts the
declaration surface is coherent before the composer that consumes it is built.

Drift is fail-closed under ``gz validate --setpoint-coherence``:

* a routed pair with no declared setpoint (REQ-0.0.37-20-01),
* a declared setpoint token outside the legal set (REQ-0.0.37-20-02).

A coherent manifest yields no errors (REQ-0.0.37-20-03). A missing or malformed
manifest fails closed rather than resolving silently.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.content.vendors import SETPOINT_TOKENS
from gzkit.core.validation_rules import ValidationError

_MANIFEST_REL = Path("data") / "vendor-manifest.json"
_ROUTES_KEY = "content_type_routes"
_TEMPS_KEY = "content_type_temperatures"


def validate_setpoint_coherence(project_root: Path) -> list[ValidationError]:
    """Audit setpoint declaration coherence against the vendor manifest.

    Steps:
      1. Load ``data/vendor-manifest.json`` (fail-closed if missing/malformed).
      2. Flag any declared setpoint token outside ``SETPOINT_TOKENS`` (REQ-02).
      3. Flag any ``content_type_routes`` pair with no declared setpoint in
         ``content_type_temperatures`` (REQ-01).

    Returns an empty list on a coherent manifest (REQ-03); otherwise one
    :class:`ValidationError` per finding.
    """
    errors: list[ValidationError] = []
    manifest_path = project_root / _MANIFEST_REL
    artifact = _MANIFEST_REL.as_posix()

    if not manifest_path.is_file():
        errors.append(
            ValidationError(
                type="setpoint_coherence",
                artifact=artifact,
                message=(
                    "data/vendor-manifest.json is missing; setpoint-coherence "
                    "audit fails closed (OBPI-0.0.37-20). Restore the manifest "
                    "or check it in."
                ),
            )
        )
        return errors

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(
            ValidationError(
                type="setpoint_coherence",
                artifact=artifact,
                message=(
                    f"data/vendor-manifest.json is not valid JSON: {exc.msg} (line {exc.lineno})."
                ),
            )
        )
        return errors

    routes = manifest.get(_ROUTES_KEY, {}) if isinstance(manifest, dict) else {}
    temps = manifest.get(_TEMPS_KEY, {}) if isinstance(manifest, dict) else {}

    # REQ-0.0.37-20-02: illegal setpoint tokens.
    for content_type, vendor_map in temps.items():
        for vendor, token in vendor_map.items():
            if token not in SETPOINT_TOKENS:
                errors.append(
                    ValidationError(
                        type="setpoint_coherence",
                        artifact=artifact,
                        message=(
                            f"Illegal setpoint token {token!r} for "
                            f"({content_type}, {vendor}); legal tokens are "
                            f"{sorted(SETPOINT_TOKENS)}."
                        ),
                        field=f"{_TEMPS_KEY}.{content_type}.{vendor}",
                    )
                )

    # REQ-0.0.37-20-01: every routed pair must carry a declared setpoint.
    for content_type, vendors in routes.items():
        declared = temps.get(content_type, {})
        for vendor in vendors:
            if vendor not in declared:
                errors.append(
                    ValidationError(
                        type="setpoint_coherence",
                        artifact=artifact,
                        message=(
                            f"({content_type}, {vendor}) is routed in "
                            f"{_ROUTES_KEY} but has no declared setpoint in "
                            f"{_TEMPS_KEY}; declare a compression target "
                            f"({sorted(SETPOINT_TOKENS)}) for the pair "
                            "(OBPI-0.0.37-20)."
                        ),
                        field=f"{_TEMPS_KEY}.{content_type}.{vendor}",
                    )
                )

    return errors
