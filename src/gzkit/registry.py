"""Content type registry for governance artifacts.

Catalogs every governance artifact type with its Pydantic model, JSON schema,
lifecycle states, canonical path pattern, and vendor rendering rules. The
registry is the single lookup for "what content types exist and how are they
shaped."

Singleton: the global ``REGISTRY`` is populated at import time.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError


class ContentType(BaseModel):
    """Descriptor for a governance content type."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Human-readable content type name (e.g., 'ADR')")
    schema_name: str | None = Field(
        None, description="Schema key for load_schema() (e.g., 'adr'), or None if unschematized"
    )
    frontmatter_model: Any = Field(
        None, description="Pydantic BaseModel class for frontmatter validation, or None"
    )
    lifecycle_states: list[str] = Field(
        default_factory=list,
        description="Ordered list of allowed lifecycle states",
    )
    canonical_path_pattern: str = Field(
        ..., description="Glob pattern for canonical artifact locations"
    )
    vendor_rendering_rules: dict[str, Any] = Field(
        default_factory=dict,
        description="Vendor-specific rendering configuration",
    )


class ContentTypeRegistry:
    """Singleton registry of governance content types.

    Usage::

        from gzkit.registry import REGISTRY

        adr_type = REGISTRY.get("ADR")
        all_types = REGISTRY.list_all()
        errors = REGISTRY.validate_artifact("ADR", frontmatter, "path/to/file.md")
    """

    def __init__(self) -> None:
        """Initialize empty registry."""
        self._types: dict[str, ContentType] = {}

    def register(self, content_type: ContentType) -> None:
        """Register a content type. Raises ValueError on duplicate name."""
        if content_type.name in self._types:
            msg = f"Content type already registered: {content_type.name}"
            raise ValueError(msg)
        self._types[content_type.name] = content_type

    def get(self, name: str) -> ContentType:
        """Look up a content type by name. Raises KeyError if not found."""
        try:
            return self._types[name]
        except KeyError:
            msg = f"Unknown content type: {name}"
            raise KeyError(msg) from None

    def list_all(self) -> list[ContentType]:
        """Return all registered content types in registration order."""
        return list(self._types.values())

    def validate_artifact(
        self,
        type_name: str,
        frontmatter: dict[str, Any],
        artifact_path: str,
    ) -> list[dict[str, Any]]:
        """Validate artifact frontmatter using the registered Pydantic model.

        Returns a list of error dicts (empty list = valid). Each dict has keys:
        ``type``, ``artifact``, ``message``, ``field``.

        Raises KeyError if the content type is not registered.
        Raises TypeError if the content type has no frontmatter model.
        """
        ct = self.get(type_name)
        if ct.frontmatter_model is None:
            msg = f"Content type '{type_name}' has no frontmatter model"
            raise TypeError(msg)

        try:
            ct.frontmatter_model(**frontmatter)
        except PydanticValidationError as exc:
            return _translate_errors(exc, frontmatter, artifact_path)

        return []


def _translate_errors(
    exc: PydanticValidationError,
    frontmatter: dict[str, Any],
    artifact_path: str,
) -> list[dict[str, Any]]:
    """Convert Pydantic validation errors to gzkit error format."""
    results: list[dict[str, Any]] = []
    for err in exc.errors():
        field = str(err["loc"][0]) if err["loc"] else None
        results.append(
            {
                "type": "frontmatter",
                "artifact": artifact_path,
                "message": f"Field '{field}': {err['msg']}",
                "field": field,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Singleton instance — populated at import time
# ---------------------------------------------------------------------------

REGISTRY = ContentTypeRegistry()


def _bootstrap_registry() -> None:
    """Register all known governance content types."""
    from gzkit.models.frontmatter import AdrFrontmatter, ObpiFrontmatter, PrdFrontmatter
    from gzkit.rules import RuleFrontmatter  # noqa: PLC0415 — avoids circular import

    REGISTRY.register(
        ContentType(
            name="ADR",
            schema_name="adr",
            frontmatter_model=AdrFrontmatter,
            lifecycle_states=["Draft", "Proposed", "Accepted", "Superseded", "Deprecated"],
            canonical_path_pattern="docs/design/adr/**/ADR-*.md",
            vendor_rendering_rules={"summary_table": True},
        )
    )
    REGISTRY.register(
        ContentType(
            name="OBPI",
            schema_name="obpi",
            frontmatter_model=ObpiFrontmatter,
            lifecycle_states=[
                "Draft",
                "Active",
                "Completed",
                "Abandoned",
                "pending",
                "in_progress",
                "completed",
                "attested_completed",
                "validated",
                "drift",
                "withdrawn",
            ],
            canonical_path_pattern="docs/design/adr/**/briefs/OBPI-*.md",
            vendor_rendering_rules={"summary_table": True},
        )
    )
    REGISTRY.register(
        ContentType(
            name="PRD",
            schema_name="prd",
            frontmatter_model=PrdFrontmatter,
            lifecycle_states=["Draft", "Review", "Approved", "Superseded"],
            canonical_path_pattern="docs/design/prd/**/PRD-*.md",
            vendor_rendering_rules={"summary_table": True},
        )
    )
    REGISTRY.register(
        ContentType(
            name="Constitution",
            schema_name=None,
            frontmatter_model=None,
            lifecycle_states=["Draft", "Ratified", "Amended", "Superseded"],
            canonical_path_pattern="docs/governance/**/constitution*.md",
            vendor_rendering_rules={},
        )
    )
    REGISTRY.register(
        ContentType(
            name="Rule",
            schema_name="rule",
            frontmatter_model=RuleFrontmatter,
            lifecycle_states=["Active", "Deprecated"],
            canonical_path_pattern=".gzkit/rules/**/*.md",
            vendor_rendering_rules={"mirror_to": ["claude", "github"]},
        )
    )
    REGISTRY.register(
        ContentType(
            name="Skill",
            schema_name=None,
            frontmatter_model=None,
            lifecycle_states=["Active", "Deprecated"],
            canonical_path_pattern=".gzkit/skills/**/SKILL.md",
            vendor_rendering_rules={"mirror_to": ["claude"]},
        )
    )
    REGISTRY.register(
        ContentType(
            name="Attestation",
            schema_name=None,
            frontmatter_model=None,
            lifecycle_states=["Recorded"],
            canonical_path_pattern=".gzkit/ledger.jsonl",
            vendor_rendering_rules={},
        )
    )
    REGISTRY.register(
        ContentType(
            name="LedgerEvent",
            schema_name="ledger",
            frontmatter_model=None,
            lifecycle_states=["Recorded"],
            canonical_path_pattern=".gzkit/ledger.jsonl",
            vendor_rendering_rules={},
        )
    )


_bootstrap_registry()
