"""Vendor-manifest trust audit (ADR-0.0.34 OBPI-08).

Enforces the coupled-surface coherence rule: ``data/vendor-manifest.json``
must validate against ``src/gzkit/schemas/vendor_manifest.json`` and must
declare ``content_type_routes`` for every content type the render pipeline
enumerates. Drift between the manifest and the render pipeline's vendor
routing is fail-closed under ``gz validate --vendor-manifest``.
"""

from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from gzkit.core.validation_rules import ValidationError
from gzkit.schemas import load_schema

_MANIFEST_REL = Path("data") / "vendor-manifest.json"


def validate_vendor_manifest(project_root: Path) -> list[ValidationError]:
    """Audit the vendor manifest for schema validity and content-type coverage.

    Steps:
      1. Load ``data/vendor-manifest.json`` (fail-closed if missing/malformed).
      2. Load the bundled ``vendor_manifest`` JSON Schema.
      3. Validate the manifest against the schema with ``jsonschema``.
      4. Ensure ``content_type_routes`` is declared and non-empty.

    Returns an empty list on a clean manifest; otherwise one
    :class:`ValidationError` per finding.
    """
    errors: list[ValidationError] = []
    manifest_path = project_root / _MANIFEST_REL
    artifact = _MANIFEST_REL.as_posix()

    if not manifest_path.is_file():
        errors.append(
            ValidationError(
                type="vendor_manifest",
                artifact=artifact,
                message=(
                    "data/vendor-manifest.json is missing; vendor-manifest "
                    "audit fails closed (ADR-0.0.34 OBPI-08). Restore the "
                    "manifest or check it in."
                ),
            )
        )
        return errors

    try:
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(
            ValidationError(
                type="vendor_manifest",
                artifact=artifact,
                message=(
                    f"data/vendor-manifest.json is not valid JSON: {exc.msg} (line {exc.lineno})."
                ),
            )
        )
        return errors

    schema = load_schema("vendor_manifest")
    validator = Draft202012Validator(schema)
    for schema_error in sorted(validator.iter_errors(manifest_data), key=lambda e: e.path):
        path = ".".join(str(p) for p in schema_error.path) or "<root>"
        errors.append(
            ValidationError(
                type="vendor_manifest",
                artifact=artifact,
                message=f"Schema violation at {path}: {schema_error.message}",
                field=path,
            )
        )

    # REQ-0.0.34-08-03: explicitly call out missing content_type_routes even
    # when schema validation already flagged it, so the operator sees the
    # canonical recovery hint rather than only the jsonschema rendering.
    if not isinstance(manifest_data, dict) or "content_type_routes" not in manifest_data:
        errors.append(
            ValidationError(
                type="vendor_manifest",
                artifact=artifact,
                message=(
                    "Manifest is missing required key 'content_type_routes'. "
                    "Add the key and declare at least one (content_type, vendor) "
                    "pair (ADR-0.0.34 OBPI-08)."
                ),
                field="content_type_routes",
            )
        )

    return errors
