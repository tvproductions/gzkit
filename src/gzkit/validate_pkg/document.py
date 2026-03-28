"""Document and frontmatter validation for governance artifacts."""

import re
from pathlib import Path
from typing import Any

from gzkit.core.validation_rules import (
    ValidationError,
    extract_headers,
    parse_frontmatter,
)
from gzkit.decomposition import parse_checklist_items, parse_scorecard
from gzkit.schemas import load_schema


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
        and (len(checklist_items) != scorecard.final_target_obpi_count)
    ):
        errors.append(
            ValidationError(
                type="decomposition",
                artifact=artifact_path,
                message=(
                    "Checklist count must match scorecard final target: "
                    f"checklist={len(checklist_items)} "
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

    # Skip files without frontmatter -- they are not governance documents
    if not frontmatter:
        return []

    headers = extract_headers(body)

    errors.extend(validate_frontmatter(frontmatter, schema, str(path)))
    errors.extend(validate_headers(headers, schema, str(path)))
    if schema_name == "adr":
        errors.extend(_validate_adr_decomposition(body, str(path)))

    return errors
