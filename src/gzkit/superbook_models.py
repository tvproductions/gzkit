"""Pydantic data models for gz superbook pipeline.

These are the first Pydantic models in gzkit (per ADR-0.15.0 migration).
They are internal to the superbook pipeline and do not replace existing
dataclasses used by ledger, decomposition, or config.
"""

from pydantic import BaseModel, ConfigDict, Field


class SpecData(BaseModel):
    """Parsed superpowers spec document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    title: str = Field(..., description="Spec title from first H1 heading")
    goal: str = Field(..., description="Goal statement from spec")
    architecture: str = Field("", description="Architecture summary")
    decisions: list[str] = Field(default_factory=list, description="Design decisions")
    file_scope: list[str] = Field(default_factory=list, description="Files in scope")


class TaskData(BaseModel):
    """A single task within a plan chunk."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Task heading text")
    file_paths: list[str] = Field(default_factory=list, description="Files touched")
    steps: list[str] = Field(default_factory=list, description="Step descriptions")


class ChunkData(BaseModel):
    """A plan chunk containing tasks."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str = Field(..., description="Chunk heading text")
    tasks: list[TaskData] = Field(default_factory=list, description="Tasks in chunk")
    file_paths: list[str] = Field(default_factory=list, description="Union of task file paths")
    criteria: list[str] = Field(default_factory=list, description="Verifiable outcomes")


class PlanData(BaseModel):
    """Parsed superpowers plan document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    goal: str = Field(..., description="Plan goal statement")
    tech_stack: str = Field("", description="Tech stack line")
    chunks: list[ChunkData] = Field(default_factory=list, description="Plan chunks")


class CommitData(BaseModel):
    """A git commit extracted for retroactive evidence."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sha: str = Field(..., description="Short commit SHA")
    message: str = Field(..., description="Commit message first line")
    files: list[str] = Field(default_factory=list, description="Changed file paths")
    date: str = Field(..., description="ISO date string")


class LaneClassification(BaseModel):
    """Result of rules-based lane classification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    lane: str = Field(..., description="lite or heavy")
    signals: list[str] = Field(default_factory=list, description="Triggering file patterns")
    confidence: str = Field("auto", description="auto or override")


class REQData(BaseModel):
    """A single requirement identifier with description."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="REQ-X.Y.Z-NN-CC format")
    description: str = Field(..., description="What the requirement verifies")


class OBPIDraft(BaseModel):
    """Draft OBPI brief for generation."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="OBPI-X.Y.Z-NN-slug")
    objective: str = Field(..., description="Single-narrative objective")
    parent: str = Field(..., description="Parent ADR ID")
    item: int = Field(..., description="Checklist item number (1-based)")
    lane: str = Field(..., description="lite or heavy")
    status: str = Field("Draft", description="Draft or Pending-Attestation")
    allowed_paths: list[str] = Field(default_factory=list)
    reqs: list[REQData] = Field(default_factory=list)
    work_breakdown: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)


class ADRDraft(BaseModel):
    """Draft ADR for generation."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="ADR-X.Y.Z")
    title: str = Field(...)
    semver: str = Field(...)
    lane: str = Field(...)
    status: str = Field("Draft")
    intent: str = Field(...)
    decision: str = Field(...)
    checklist: list[str] = Field(default_factory=list)
    scorecard: dict[str, int] = Field(default_factory=dict)
    obpis: list[OBPIDraft] = Field(default_factory=list)
