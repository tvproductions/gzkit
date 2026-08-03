"""Document and frontmatter validation for governance artifacts."""

import re
from pathlib import Path
from typing import Any

from gzkit.core.validation_rules import (
    ValidationError,
    extract_headers,
    parse_frontmatter,
)
from gzkit.decomposition import active_checklist_items, parse_checklist_items, parse_scorecard
from gzkit.frontmatter import read_frontmatter
from gzkit.schemas import load_schema

# ADR lifecycle states that are grandfather-exempted from the
# ``required_headers`` and decomposition scorecard checks. Mirror of the
# lifecycle-aware precedent at
# ``src/gzkit/governance/trust_audits/briefs.py`` (``_BDD_GATED_BRIEF_STATUSES``)
# with inverted polarity: ``behave_req_tags`` fires only on Completed/
# Validated briefs; ``required_headers`` *skips* only on Completed/Validated
# ADRs, because post-Accepted artifacts had their shape locked at authoring
# and attestation time. Retroactively binding new section requirements is a
# trust-doctrine T1 violation -- the canonical schema does not bind the
# canonical provenance of what Validated artifacts actually carry. Narrow
# guard landed in OBPI-0.0.54-03 under GHI #480 as coupled-surface coherence
# under the schema-enum fix; full kind-aware schema split is the eventual
# disposition under ``ADR-pool.validate-documents-backfill`` (Alt #5).
_ADR_GRANDFATHERED_STATUSES = frozenset({"completed", "validated"})

# Filename-stem prefix identifying a pool ADR. Pool ADRs carry a structurally
# distinct shape contract (Intent / Target Scope / Non-Goals plus optional
# Decision / Alternatives / Promotion Criteria per AGENTS.md s Kinds; pool
# ADRs have no ``kind:`` or ``semver:`` frontmatter per
# ``src/gzkit/schemas/adr.json``). Applying the foundation/feature adr schema
# to them is the "validator scope mismatch" named in GHI #480 reopen comment.
# This narrow kind-aware skip is the minimum trust-doctrine repair to unblock
# OBPI-0.0.54-03 Stage 3 verify; full pool-shape validation is the pool ADR's
# eventual destination work.
_POOL_ADR_STEM_PREFIX = "ADR-pool."


def is_pool_adr_path(path: Path) -> bool:
    """Return True when ``path`` names a pool ADR artifact."""
    return path.stem.startswith(_POOL_ADR_STEM_PREFIX)


def is_canonical_adr_intent_path(path: Path) -> bool:
    """Return True when ``path`` is the intent document of a canonical ADR package.

    A canonical ADR package is a directory named for its ADR whose intent
    document carries the same stem: ``ADR-0.34.0-foundation-sunset/
    ADR-0.34.0-foundation-sunset.md``. Everything else the ``ADR-*.md`` glob
    reaches is a sidecar that legitimately carries no frontmatter -- closeout
    forms, briefs under ``obpis/``, audit and log files -- as are pool ADRs,
    which are flat files whose parent is the ``pool/`` tier directory.

    Stated as a property rather than as a list of sidecar names on purpose: an
    enumeration has to be revisited every time a package grows a subdirectory,
    and the omission is silent. Measured equivalent to the name-list form over
    all 357 ``ADR-*.md`` files on disk, selecting the same 86 (GHI #742).
    """
    return path.stem == path.parent.name


def is_adr_shape_grandfathered(frontmatter: dict[str, Any]) -> bool:
    """Return True when an ADR's lifecycle state freezes authoring-era shape."""
    return str(frontmatter.get("status", "")).lower() in _ADR_GRANDFATHERED_STATUSES


def validate_frontmatter(
    frontmatter: dict[str, Any],
    schema: dict[str, Any],
    artifact_path: str,
) -> list[ValidationError]:
    """Validate frontmatter against schema requirements.

    Uses Pydantic model instantiation for ADR, OBPI, and PRD content types.
    Falls back to schema-driven validation for unknown schemas.

    Args:
        frontmatter: Parsed frontmatter dictionary.
        schema: Schema with frontmatter requirements.
        artifact_path: Path to artifact for error messages.

    Returns:
        List of validation errors.

    """
    from gzkit.models.frontmatter import (
        validate_frontmatter_model,  # noqa: PLC0415 -- avoid circular import at module level
    )

    model_result = validate_frontmatter_model(frontmatter, schema, artifact_path)
    if model_result is not None:
        return [ValidationError(**err) for err in model_result]

    # Fallback: schema-driven validation for unregistered schema IDs
    errors: list[ValidationError] = []
    fm_schema = schema.get("properties", {}).get("frontmatter", {})
    required_fields = fm_schema.get("required", [])
    field_schemas = fm_schema.get("properties", {})

    for field in required_fields:
        if field not in frontmatter:
            errors.append(
                ValidationError(
                    type="frontmatter",
                    artifact=artifact_path,
                    message=f"Missing required frontmatter field: {field}",
                    field=field,
                )
            )

    for field, value in frontmatter.items():
        if field not in field_schemas:
            continue

        field_schema = field_schemas[field]

        if "pattern" in field_schema:
            pattern = field_schema["pattern"]
            if not re.match(pattern, str(value)):
                errors.append(
                    ValidationError(
                        type="frontmatter",
                        artifact=artifact_path,
                        message=f"Field '{field}' does not match pattern {pattern}",
                        field=field,
                    )
                )

        if "enum" in field_schema:
            allowed = field_schema["enum"]
            if value not in allowed:
                errors.append(
                    ValidationError(
                        type="frontmatter",
                        artifact=artifact_path,
                        message=f"Field '{field}' must be one of {allowed}, got '{value}'",
                        field=field,
                    )
                )

    return errors


def validate_headers(
    headers: list[str],
    schema: dict[str, Any],
    artifact_path: str,
) -> list[ValidationError]:
    """Validate headers against schema requirements.

    Args:
        headers: List of extracted headers.
        schema: Schema with required_headers list.
        artifact_path: Path to artifact for error messages.

    Returns:
        List of validation errors.

    """
    errors = []
    required_headers = schema.get("required_headers", [])

    for required in required_headers:
        if required not in headers:
            errors.append(
                ValidationError(
                    type="header",
                    artifact=artifact_path,
                    message=f"Missing required section: '{required}'",
                    field=required,
                )
            )

    return errors


def _validate_obpi_id_matches_stem(
    frontmatter: dict[str, Any], path: Path
) -> list[ValidationError]:
    """Validate that OBPI frontmatter ``id`` matches the filename stem.

    The slugified filename stem is the canonical OBPI identifier used in ledger
    events. A short-form ``id`` (e.g. ``OBPI-0.0.14-01``) creates phantom
    duplicates when the ledger registers the full stem
    (``OBPI-0.0.14-01-obpi-lock-command``).
    """
    fm_id = frontmatter.get("id", "")
    stem = path.stem
    if fm_id and fm_id != stem:
        return [
            ValidationError(
                type="frontmatter",
                artifact=str(path),
                message=(
                    f"Frontmatter id '{fm_id}' does not match filename stem '{stem}'. "
                    f"The slugified filename is the canonical identifier for ledger "
                    f"registration. Update the frontmatter id to '{stem}'."
                ),
                field="id",
            )
        ]
    return []


def _validate_adr_decomposition(body: str, artifact_path: str) -> list[ValidationError]:
    """Validate deterministic ADR decomposition scorecard semantics."""
    errors: list[ValidationError] = []
    checklist_items = parse_checklist_items(body)
    if not checklist_items:
        errors.append(
            ValidationError(
                type="decomposition",
                artifact=artifact_path,
                message="Checklist must contain at least one OBPI item.",
                field="Checklist",
            )
        )

    scorecard, scorecard_errors = parse_scorecard(body)
    for message in scorecard_errors:
        errors.append(
            ValidationError(
                type="decomposition",
                artifact=artifact_path,
                message=message,
                field="Decomposition Scorecard",
            )
        )

    if (
        scorecard is not None
        and checklist_items
        and (len(active_checklist_items(checklist_items)) != scorecard.final_target_obpi_count)
    ):
        live_count = len(active_checklist_items(checklist_items))
        errors.append(
            ValidationError(
                type="decomposition",
                artifact=artifact_path,
                message=(
                    "Checklist count must match scorecard final target "
                    "(does not match): "
                    f"active={live_count} "
                    f"total={len(checklist_items)} "
                    f"target={scorecard.final_target_obpi_count}."
                ),
                field="Checklist",
            )
        )
    return errors


def validate_document(path: Path, schema_name: str) -> list[ValidationError]:
    """Validate a governance document against its schema.

    Args:
        path: Path to the Markdown document.
        schema_name: Name of schema to validate against (e.g., 'prd', 'adr', 'obpi').

    Returns:
        List of validation errors (empty if valid).

    """
    errors = []

    # Check file exists
    if not path.exists():
        return [
            ValidationError(
                type="schema",
                artifact=str(path),
                message="File does not exist",
            )
        ]

    # Load content
    try:
        content = path.read_text(encoding="utf-8")
    except OSError as e:
        return [
            ValidationError(
                type="schema",
                artifact=str(path),
                message=f"Failed to read file: {e}",
            )
        ]

    # Load schema
    try:
        schema = load_schema(schema_name)
    except FileNotFoundError:
        return [
            ValidationError(
                type="schema",
                artifact=str(path),
                message=f"Unknown schema: {schema_name}",
            )
        ]

    # Parse and validate
    frontmatter, body = parse_frontmatter(content)

    if not frontmatter:
        # For sidecars (closeout forms, briefs, audit/log files) and pool ADRs,
        # absence of frontmatter really is absence of the obligation. For the
        # intent document of a canonical ADR package it is the loudest possible
        # finding: no field can be checked at all, so a frontmatter-keyed reader
        # reports green over an artifact it never inspected (GHI #742). Keying
        # the exemption on directory placement rather than a frontmatter field
        # is the GHI #483 precedent generalized instead of re-instantiated.
        if not is_canonical_adr_intent_path(path):
            return []
        read = read_frontmatter(content)
        detail = (
            f"malformed and cannot be read: {read.reason}"
            if read.state == "malformed"
            else (
                "absent; a canonical ADR intent document must declare "
                "id, status, semver, lane, kind, parent, and date"
            )
        )
        return [
            ValidationError(
                type="frontmatter",
                artifact=str(path),
                message=f"Frontmatter is {detail}",
            )
        ]

    # Kind-aware pool ADR skip (GHI #480). Pool ADRs are structurally distinct
    # from foundation/feature ADRs and the current adr schema does not encode
    # their shape contract; full disposition is the pool ADR's Alt #5 work.
    if schema_name == "adr" and is_pool_adr_path(path):
        return []

    headers = extract_headers(body)

    # Lifecycle-aware grandfather skip (GHI #480). Validated/Completed ADRs
    # had their shape locked at authoring/attestation time; do not retroactively
    # bind them to required_headers, decomposition, or missing-required-field
    # checks added after their closeout. Pattern/enum/type checks on present
    # fields continue to fire (those are mechanical invariants, not authoring-
    # era shape requirements).
    is_grandfathered_adr = schema_name == "adr" and is_adr_shape_grandfathered(frontmatter)

    frontmatter_errors = validate_frontmatter(frontmatter, schema, str(path))
    if is_grandfathered_adr:
        frontmatter_errors = [
            err
            for err in frontmatter_errors
            if not err.message.startswith("Missing required frontmatter field")
        ]
    errors.extend(frontmatter_errors)

    if not is_grandfathered_adr:
        errors.extend(validate_headers(headers, schema, str(path)))
        if schema_name == "adr":
            errors.extend(_validate_adr_decomposition(body, str(path)))

    if schema_name == "obpi":
        errors.extend(_validate_obpi_id_matches_stem(frontmatter, path))

    return errors
