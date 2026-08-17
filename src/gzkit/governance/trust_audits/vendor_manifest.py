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

# The agent contract is the ROOT contract: one rendition at root AGENTS.md,
# serving every harness. Doctrine home is
# docs/governance/agent-control-surface-rendering-substrate.md § Worked example
# ("gz content render agent_contract --vendor=root"), carried as an
# invariant-tier corpus entry from 2026-08-17.
_ROOT_CONTRACT_TYPE = "AgentContract"

_ROOT_CONTRACT_RECOVERY = (
    "AGENTS.md is the root contract and the agent-harness default: ONE rendition "
    "serves every harness, because it must fit the smallest vendor delivery cap. "
    "Declare exactly one route and one temperature for "
    f"{_ROOT_CONTRACT_TYPE!r}. Vendor-specific material belongs in that vendor's "
    "own surface (.claude/rules/**), never in a second AGENTS.md. Delivery CAPS "
    "are exempt and stay per-vendor — a cap is an observed fact about someone "
    "else's product, not a control gzkit chooses."
)


def _singleton_error(artifact: str, key: str, declared: list[str]) -> ValidationError:
    """Return the fail-closed finding for a multi-vendor root-contract declaration."""
    return ValidationError(
        type="vendor_manifest",
        artifact=artifact,
        message=(
            f"{key}.{_ROOT_CONTRACT_TYPE} declares {len(declared)} vendors "
            f"({', '.join(sorted(declared))}), but there is exactly one root contract. "
            + _ROOT_CONTRACT_RECOVERY
        ),
        field=f"{key}.{_ROOT_CONTRACT_TYPE}",
    )


def _root_contract_errors(
    manifest_data: dict, artifact: str, *, project_root: Path
) -> list[ValidationError]:
    """Fence the root contract against per-vendor routing, and witness the second copy.

    Two findings, both fail-closed:

    * ``AgentContract`` declaring more than one route or more than one temperature.
      Those are controls gzkit chooses, so a second one asserts two root contracts.
    * ``data/vendor-manifest.json`` disagreeing with
      :data:`gzkit.content.vendors._FALLBACK_ROUTES`. The fallback table is a second
      copy of the routing authority kept in agreement by a comment; that is the same
      two-copies-one-binds shape that let the root doctrine drift for three artifacts,
      so it is witnessed rather than trusted.
    """
    from gzkit.content.vendors import _FALLBACK_ROUTES

    errors: list[ValidationError] = []

    routes = manifest_data.get("content_type_routes")
    if isinstance(routes, dict):
        declared = routes.get(_ROOT_CONTRACT_TYPE)
        if isinstance(declared, list) and len(declared) > 1:
            errors.append(_singleton_error(artifact, "content_type_routes", declared))

    temperatures = manifest_data.get("content_type_temperatures")
    if isinstance(temperatures, dict):
        vendor_map = temperatures.get(_ROOT_CONTRACT_TYPE)
        if isinstance(vendor_map, dict) and len(vendor_map) > 1:
            errors.append(_singleton_error(artifact, "content_type_temperatures", list(vendor_map)))

    # The agreement check is a property of a gzkit SOURCE TREE, not of any manifest:
    # only a root that ships `vendors.py` owns the second copy this compares against.
    # A fixture root under tempfile has no such obligation, and asserting one there
    # would fail every partial fixture in the suite for a divergence that cannot exist.
    owns_fallback = (project_root / "src" / "gzkit" / "content" / "vendors.py").is_file()
    diverged = isinstance(routes, dict) and routes and dict(routes) != dict(_FALLBACK_ROUTES)
    if owns_fallback and diverged:
        errors.append(
            ValidationError(
                type="vendor_manifest",
                artifact=artifact,
                message=(
                    "content_type_routes disagrees with _FALLBACK_ROUTES in "
                    "src/gzkit/content/vendors.py. The fallback table is the routing "
                    "authority's second copy, resolved whenever no project root is "
                    "supplied, so a divergence means two callers of the same question "
                    "get different answers. Update both surfaces together."
                ),
                field="content_type_routes",
            )
        )

    return errors


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

    if isinstance(manifest_data, dict):
        errors.extend(_root_contract_errors(manifest_data, artifact, project_root=project_root))

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
