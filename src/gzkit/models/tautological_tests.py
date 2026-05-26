"""Pydantic models for the decommission-tautological-tests chore (OBPI-0.0.59-04).

All models use ConfigDict(frozen=True, extra="forbid") per .gzkit/rules/models.md.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class ProposedDisposition(StrEnum):
    """Four disposition categories for a tautological test operation."""

    convert = "convert"
    replace_with_ledger = "replace-with-ledger"
    fold_to_validator = "fold-to-validator"
    keep_as_fixture = "keep-as-fixture"


class TautologicalTestOperation(BaseModel):
    """One co-occurrence of a filesystem-shaped op and an assertion in a test function."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Relative path from project root (posix)")
    line_number: int = Field(..., description="Line number of the filesystem operation")
    operation_kind: str = Field(..., description="Kind of filesystem operation detected")
    function_name: str = Field(..., description="Name of the containing test function")
    assertion_kind: str = Field(..., description="Kind of assertion in the same function")
    context_hint: str | None = Field(None, description="Optional context from the source text")


class Waiver(BaseModel):
    """A single waived operation entry with rationale-key indirection."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file_path: str = Field(..., description="Relative path of the file being waived (posix)")
    rationale_key: str = Field(..., description="Key into the rationale catalogue")
    waived_count: int = Field(..., ge=1, description="Number of operations waived by this entry")


class Baseline(BaseModel):
    """Persistent baseline snapshot of tautological operations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    operations: list[TautologicalTestOperation] = Field(
        default_factory=list, description="Baselined operations"
    )
    generated_at: str = Field(..., description="ISO-8601 timestamp of baseline generation")
