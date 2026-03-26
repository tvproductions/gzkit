"""Pydantic models for the documentation cross-coverage scanner."""

from pydantic import BaseModel, ConfigDict, Field


class SurfaceResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(
        ...,
        description=(
            "Surface name (manpage, index_entry, operator_runbook, "
            "governance_runbook, docstring, command_docs_mapping)"
        ),
    )
    passed: bool = Field(..., description="Whether the surface check passed")
    detail: str = Field(..., description="Explanation of the check result")


class CommandCoverage(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    command: str = Field(..., description="CLI command name as discovered (e.g. 'adr status')")
    surfaces: list[SurfaceResult] = Field(
        ..., description="Results for all six documentation surfaces"
    )
    all_passed: bool = Field(..., description="True when all surfaces pass")


class OrphanedDoc(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    surface: str = Field(..., description="Which surface has the orphan")
    reference: str = Field(..., description="The orphaned reference (file path or key)")
    detail: str = Field(..., description="Explanation of why this is orphaned")


class CoverageReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    commands_discovered: int = Field(..., description="Total CLI commands found by AST scanning")
    commands_fully_covered: int = Field(..., description="Commands with all six surfaces passing")
    commands_with_gaps: int = Field(..., description="Commands missing at least one surface")
    coverage: list[CommandCoverage] = Field(..., description="Per-command coverage results")
    orphaned: list[OrphanedDoc] = Field(
        ..., description="Documentation referencing removed commands"
    )
    passed: bool = Field(..., description="True only when no gaps and no orphans")
