"""Pydantic frontmatter models for governance and control-surface content types.

Extracted from gzkit.models.frontmatter. Each model mirrors a corresponding
JSON schema. Pure domain logic — no I/O operations.
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
# Control-surface frontmatter models
# ---------------------------------------------------------------------------


class SkillFrontmatter(BaseModel):
    """Skill SKILL.md frontmatter — mirrors ``.gzkit/schemas/skill.schema.json``."""

    model_config = ConfigDict(frozen=True, extra="allow", populate_by_name=True)

    description: str
    name: str | None = Field(None, pattern=r"^[a-z0-9-]+$")
    category: (
        Literal[
            "adr-lifecycle",
            "adr-operations",
            "adr-audit",
            "obpi-pipeline",
            "governance-infrastructure",
            "agent-operations",
            "code-quality",
            "cross-repository",
        ]
        | None
    ) = None
    lifecycle_state: Literal["active", "deprecated", "draft", "retired"] | None = None
    owner: str | None = None
    last_reviewed: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    user_invocable: bool | None = Field(None, alias="user-invocable")
    disable_model_invocation: bool | None = Field(None, alias="disable-model-invocation")
    argument_hint: str | None = Field(None, alias="argument-hint")
    allowed_tools: str | None = Field(None, alias="allowed-tools")
    skill_model: str | None = Field(None, alias="model")
    context: Literal["fork"] | None = None
    agent: str | None = None


class InstructionFrontmatter(BaseModel):
    """Instruction frontmatter — mirrors ``.gzkit/schemas/rule.schema.json``."""

    model_config = ConfigDict(frozen=True, extra="allow", populate_by_name=True)

    apply_to: str = Field(..., alias="applyTo")
    name: str | None = None
    description: str | None = None
    category: str | None = None
    exclude_agent: Literal["code-review", "coding-agent", "all"] | None = Field(
        None, alias="excludeAgent"
    )


# ---------------------------------------------------------------------------
# Identity surface models (ADR-0.0.10, OBPI-0.0.10-02)
# ---------------------------------------------------------------------------


class AdrId(BaseModel):
    """Portable ADR identity surface.

    Pattern: ``ADR-X.Y.Z``  Example: ``ADR-0.0.10``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(..., description="Canonical ADR identifier", pattern=r"^ADR-\d+\.\d+\.\d+$")

    @classmethod
    def parse(cls, value: str) -> AdrId:
        """Parse and validate an ADR identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


class ObpiId(BaseModel):
    """Portable OBPI identity surface.

    Pattern: ``OBPI-X.Y.Z-NN``  Example: ``OBPI-0.0.10-01``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(
        ..., description="Canonical OBPI identifier", pattern=r"^OBPI-\d+\.\d+\.\d+-\d+$"
    )

    @classmethod
    def parse(cls, value: str) -> ObpiId:
        """Parse and validate an OBPI identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


class ReqId(BaseModel):
    """Portable REQ identity surface.

    Pattern: ``REQ-X.Y.Z-NN-MM``  Example: ``REQ-0.0.10-01-01``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(
        ..., description="Canonical REQ identifier", pattern=r"^REQ-\d+\.\d+\.\d+-\d+-\d+$"
    )

    @classmethod
    def parse(cls, value: str) -> ReqId:
        """Parse and validate a REQ identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


class TaskId(BaseModel):
    """Portable TASK identity surface.

    Pattern: ``TASK-X.Y.Z-NN-MM-SS``  Example: ``TASK-0.20.0-01-01-01``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(
        ..., description="Canonical TASK identifier", pattern=r"^TASK-\d+\.\d+\.\d+-\d+-\d+-\d+$"
    )

    @classmethod
    def parse(cls, value: str) -> TaskId:
        """Parse and validate a TASK identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


class EvidenceId(BaseModel):
    """Portable Evidence identity surface.

    Pattern: ``EV-X.Y.Z-NN-SSS``  Example: ``EV-0.0.10-01-001``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(
        ..., description="Canonical Evidence identifier", pattern=r"^EV-\d+\.\d+\.\d+-\d+-\d+$"
    )

    @classmethod
    def parse(cls, value: str) -> EvidenceId:
        """Parse and validate an Evidence identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


IDENTITY_MODELS: dict[str, type[BaseModel]] = {
    "ADR": AdrId,
    "OBPI": ObpiId,
    "REQ": ReqId,
    "TASK": TaskId,
    "EV": EvidenceId,
}


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
