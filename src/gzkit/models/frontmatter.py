"""Pydantic frontmatter models for ADR, OBPI, and PRD content types.

Each model mirrors the corresponding JSON schema in ``src/gzkit/schemas/``.
Pattern validators and Literal types enforce the same constraints that were
previously checked procedurally in ``validate.py``.
"""

from __future__ import annotations

from typing import Any, Literal, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError

# ---------------------------------------------------------------------------
# Frontmatter models
# ---------------------------------------------------------------------------


class AdrFrontmatter(BaseModel):
    """ADR frontmatter — mirrors ``src/gzkit/schemas/adr.json``."""

    model_config = ConfigDict(frozen=True, extra="allow")

    id: str = Field(..., pattern=r"^ADR-[0-9]+\.[0-9]+\.[0-9]+$")
    status: Literal["Draft", "Proposed", "Accepted", "Superseded", "Deprecated"]
    semver: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    lane: Literal["lite", "heavy"]
    parent: str
    date: str = Field(..., pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class ObpiFrontmatter(BaseModel):
    """OBPI frontmatter — mirrors ``src/gzkit/schemas/obpi.json``."""

    model_config = ConfigDict(frozen=True, extra="allow")

    id: str = Field(..., pattern=r"^OBPI-[0-9]+\.[0-9]+\.[0-9]+-[0-9]{2}(-[a-z0-9-]+)?$")
    parent: str
    item: str | int
    lane: Literal["lite", "heavy", "Lite", "Heavy"]
    status: Literal["Draft", "Active", "Completed", "Abandoned"]


class PrdFrontmatter(BaseModel):
    """PRD frontmatter — mirrors ``src/gzkit/schemas/prd.json``."""

    model_config = ConfigDict(frozen=True, extra="allow")

    id: str = Field(..., pattern=r"^PRD-[A-Z0-9]+-[0-9]+\.[0-9]+\.[0-9]+$")
    status: Literal["Draft", "Review", "Approved", "Superseded"]
    semver: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    date: str = Field(..., pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


# ---------------------------------------------------------------------------
# Schema-ID → model mapping
# ---------------------------------------------------------------------------

SCHEMA_TO_MODEL: dict[str, type[BaseModel]] = {
    "gzkit.adr.v1": AdrFrontmatter,
    "gzkit.obpi.v1": ObpiFrontmatter,
    "gzkit.prd.v1": PrdFrontmatter,
}


# ---------------------------------------------------------------------------
# Error translation — Pydantic → gzkit ValidationError list
# ---------------------------------------------------------------------------


def _literal_values(model_cls: type[BaseModel], field_name: str) -> list[str] | None:
    """Extract allowed Literal values for a model field."""
    field_info = model_cls.model_fields.get(field_name)
    if field_info is None:
        return None
    annotation = field_info.annotation
    # Unwrap unions (str | int doesn't have Literal)
    if get_origin(annotation) is Literal:
        return list(get_args(annotation))
    return None


def _translate_pydantic_errors(
    exc: PydanticValidationError,
    frontmatter: dict[str, Any],
    artifact_path: str,
    model_cls: type[BaseModel],
) -> list[dict[str, Any]]:
    """Convert Pydantic v2 errors to dicts matching gzkit error format.

    Returns a list of dicts with keys: type, artifact, message, field.
    """
    results: list[dict[str, Any]] = []
    for err in exc.errors():
        field = str(err["loc"][0]) if err["loc"] else None
        err_type = err["type"]

        if err_type == "missing":
            results.append(
                {
                    "type": "frontmatter",
                    "artifact": artifact_path,
                    "message": f"Missing required frontmatter field: {field}",
                    "field": field,
                }
            )
        elif err_type == "string_pattern_mismatch":
            pattern = err.get("ctx", {}).get("pattern", "")
            results.append(
                {
                    "type": "frontmatter",
                    "artifact": artifact_path,
                    "message": f"Field '{field}' does not match pattern {pattern}",
                    "field": field,
                }
            )
        elif err_type == "literal_error":
            allowed = _literal_values(model_cls, field) if field else None
            value = frontmatter.get(field, "") if field else ""
            results.append(
                {
                    "type": "frontmatter",
                    "artifact": artifact_path,
                    "message": f"Field '{field}' must be one of {allowed}, got '{value}'",
                    "field": field,
                }
            )
        else:
            # Catch-all for unexpected Pydantic error types
            results.append(
                {
                    "type": "frontmatter",
                    "artifact": artifact_path,
                    "message": f"Field '{field}': {err['msg']}",
                    "field": field,
                }
            )

    return results


def validate_frontmatter_model(
    frontmatter: dict[str, Any],
    schema: dict[str, Any],
    artifact_path: str,
) -> list[dict[str, Any]] | None:
    """Validate frontmatter using Pydantic model instantiation.

    Returns a list of error dicts if a model exists for the schema,
    or ``None`` if no model is registered (caller should fall back).

    Each dict has keys: type, artifact, message, field — matching the
    constructor kwargs of ``gzkit.validate.ValidationError``.
    """
    schema_id = schema.get("$id", "")
    model_cls = SCHEMA_TO_MODEL.get(schema_id)
    if model_cls is None:
        return None

    try:
        model_cls(**frontmatter)
    except PydanticValidationError as exc:
        return _translate_pydantic_errors(exc, frontmatter, artifact_path, model_cls)

    return []
