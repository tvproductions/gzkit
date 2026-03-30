"""Typed flag models for the feature flag system.

Defines FlagCategory (StrEnum), FlagSpec (flag metadata), FlagEvaluation
(resolved value with source attribution), and typed error hierarchy.
Implements ADR-0.0.8 Section 6.5 field requirements and category-specific
validation rules.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from gzkit.core.exceptions import GzkitError

# ---------------------------------------------------------------------------
# Error hierarchy
# ---------------------------------------------------------------------------


class FlagError(GzkitError):
    """Base exception for all flag-related errors."""

    @property
    def exit_code(self) -> int:
        """Return exit code 1 for flag errors."""
        return 1


class UnknownFlagError(FlagError):
    """Raised when evaluating a flag key not present in the registry."""


class InvalidFlagValueError(FlagError):
    """Raised when a flag value cannot be parsed as boolean."""


# ---------------------------------------------------------------------------
# FlagCategory enum
# ---------------------------------------------------------------------------


class FlagCategory(StrEnum):
    """Feature flag categories per ADR-0.0.8 Section 4."""

    release = "release"
    ops = "ops"
    migration = "migration"
    development = "development"


# ---------------------------------------------------------------------------
# FlagSpec model
# ---------------------------------------------------------------------------


class FlagSpec(BaseModel):
    """Metadata for a single feature flag.

    Enforces ADR-0.0.8 Section 6.5 field requirements and category-specific
    validation rules:
    - ``release`` and ``migration`` require ``remove_by``
    - ``ops`` requires ``review_by``
    - ``development`` requires ``remove_by`` and ``default=false``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str = Field(..., description="Dotted identifier: {category}.{name}")
    category: FlagCategory = Field(..., description="Flag category")
    default: bool = Field(..., description="Explicit default value")
    description: str = Field(..., description="Human-readable purpose sentence")
    owner: str = Field(..., description="Responsible party")
    introduced_on: date = Field(..., description="Date the flag was added to the registry")
    review_by: date | None = Field(None, description="Required for ops flags")
    remove_by: date | None = Field(None, description="Required for release, migration, development")
    linked_adr: str | None = Field(None, description="ADR that introduced this flag")
    linked_issue: str | None = Field(None, description="GitHub issue tracking this flag")

    @model_validator(mode="after")
    def _enforce_category_rules(self) -> FlagSpec:
        """Enforce category-specific metadata requirements."""
        if self.category == FlagCategory.release and self.remove_by is None:
            msg = "Release flags require remove_by"
            raise ValueError(msg)

        if self.category == FlagCategory.migration and self.remove_by is None:
            msg = "Migration flags require remove_by"
            raise ValueError(msg)

        if self.category == FlagCategory.ops and self.review_by is None:
            msg = "Ops flags require review_by"
            raise ValueError(msg)

        if self.category == FlagCategory.development:
            if self.remove_by is None:
                msg = "Development flags require remove_by"
                raise ValueError(msg)
            if self.default is not False:
                msg = "Development flags must default to false"
                raise ValueError(msg)

        return self


# ---------------------------------------------------------------------------
# FlagEvaluation model
# ---------------------------------------------------------------------------


class FlagEvaluation(BaseModel):
    """Result of resolving a flag value through the precedence chain.

    Captures what the resolved value is and which precedence layer provided it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    key: str = Field(..., description="Flag key that was evaluated")
    value: bool = Field(..., description="Resolved boolean value")
    source: str = Field(..., description="Precedence layer that provided the value")
