"""Agent role taxonomy and handoff protocols for pipeline execution.

Defines four universal agent roles — Planner, Implementer, Reviewer, Narrator —
with explicit boundaries, handoff artifacts, and conflict resolution rules.

Roles are project-level abstractions. Vendor assignment (which model fills which
role) is a session-level decision made by the pipeline orchestrator.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Handoff result contract
# ---------------------------------------------------------------------------


class HandoffStatus(StrEnum):
    """Structured result status for inter-role handoff."""

    DONE = "DONE"
    DONE_WITH_CONCERNS = "DONE_WITH_CONCERNS"
    NEEDS_CONTEXT = "NEEDS_CONTEXT"
    BLOCKED = "BLOCKED"


class ReviewVerdict(StrEnum):
    """Review outcome from Reviewer role."""

    PASS = "PASS"
    FAIL = "FAIL"
    CONCERNS = "CONCERNS"


class ReviewFindingSeverity(StrEnum):
    """Severity level for individual review findings."""

    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class ReviewFinding(BaseModel):
    """A single finding from a review."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    file: str = Field(..., description="File path where the finding was observed")
    line: int | None = Field(None, description="Line number if applicable")
    severity: ReviewFindingSeverity = Field(..., description="Finding severity level")
    message: str = Field(..., description="Description of the finding")


class HandoffResult(BaseModel):
    """Structured result from an implementer subagent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    status: HandoffStatus = Field(..., description="Overall task completion status")
    files_changed: list[str] = Field(default_factory=list, description="Files modified")
    tests_added: list[str] = Field(default_factory=list, description="Test files/methods added")
    concerns: list[str] = Field(default_factory=list, description="Issues or concerns to flag")


class ReviewResult(BaseModel):
    """Structured result from a reviewer subagent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    verdict: ReviewVerdict = Field(..., description="Overall review outcome")
    findings: list[ReviewFinding] = Field(
        default_factory=list, description="Specific review findings"
    )
    summary: str = Field("", description="Brief review summary")


# ---------------------------------------------------------------------------
# Artifact contracts
# ---------------------------------------------------------------------------


class ArtifactContract(BaseModel):
    """What a role produces and consumes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    produces: list[str] = Field(..., description="Artifact types this role outputs")
    consumes: list[str] = Field(..., description="Artifact types this role requires as input")


# ---------------------------------------------------------------------------
# Agent file specification
# ---------------------------------------------------------------------------


class AgentFileSpec(BaseModel):
    """Claude Code agent file frontmatter specification for a role."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tools: list[str] = Field(..., description="Tool allowlist enforcing role boundaries")
    model: str = Field("inherit", description="Model override or 'inherit' from parent")
    permission_mode: str = Field("default", description="Claude Code permission mode")
    max_turns: int = Field(..., description="Agent loop bound to prevent runaway execution")
    skills: list[str] = Field(default_factory=list, description="Skills injected into context")


# ---------------------------------------------------------------------------
# Role definitions
# ---------------------------------------------------------------------------


RoleName = Literal["Planner", "Implementer", "Reviewer", "Narrator"]

ROLE_NAMES: list[RoleName] = ["Planner", "Implementer", "Reviewer", "Narrator"]


class RoleDefinition(BaseModel):
    """Complete definition of a pipeline agent role."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    name: RoleName = Field(..., description="Role name")
    description: str = Field(..., description="Role purpose and responsibility")
    pipeline_stages: list[str] = Field(..., description="Pipeline stages where this role operates")
    artifacts: ArtifactContract = Field(..., description="Artifact production/consumption contract")
    agent_spec: AgentFileSpec = Field(
        ..., description="Claude Code agent file specification for this role"
    )
    can_write: bool = Field(..., description="Whether the role has filesystem write access")


# ---------------------------------------------------------------------------
# Conflict resolution
# ---------------------------------------------------------------------------


# Precedence order: lower index = higher precedence when two roles touch the same file.
CONFLICT_PRECEDENCE: list[RoleName] = ["Planner", "Implementer", "Reviewer", "Narrator"]


def resolve_conflict(role_a: RoleName, role_b: RoleName) -> RoleName:
    """Determine which role takes precedence when two agents touch the same file.

    Returns the role with higher precedence (lower index in CONFLICT_PRECEDENCE).
    """
    idx_a = CONFLICT_PRECEDENCE.index(role_a)
    idx_b = CONFLICT_PRECEDENCE.index(role_b)
    return role_a if idx_a <= idx_b else role_b


# ---------------------------------------------------------------------------
# Canonical role taxonomy
# ---------------------------------------------------------------------------


PLANNER = RoleDefinition(
    name="Planner",
    description=(
        "Creates ADR documents, OBPI briefs, implementation plans, and dependency graphs. "
        "Operates in pre-pipeline (plan mode) and Stage 1 context loading."
    ),
    pipeline_stages=["pre-pipeline", "stage-1"],
    artifacts=ArtifactContract(
        produces=[
            "ADR documents",
            "OBPI briefs",
            "implementation plans",
            "dependency graphs",
        ],
        consumes=[
            "user intent",
            "codebase state",
            "governance constraints",
        ],
    ),
    agent_spec=AgentFileSpec(
        tools=["Read", "Glob", "Grep", "Bash", "Agent"],
        model="inherit",
        permission_mode="default",
        max_turns=20,
        skills=[],
    ),
    can_write=False,
)


IMPLEMENTER = RoleDefinition(
    name="Implementer",
    description=(
        "Implements plan tasks with TDD discipline. Dispatched per-task by the pipeline "
        "controller. Returns structured result status for orchestrator consumption."
    ),
    pipeline_stages=["stage-2"],
    artifacts=ArtifactContract(
        produces=[
            "code changes",
            "tests",
            "commit-ready file sets",
            "structured result status",
        ],
        consumes=[
            "plan task with scoped context",
            "allowed files",
            "test expectations",
            "brief requirements",
        ],
    ),
    agent_spec=AgentFileSpec(
        tools=["Read", "Edit", "Write", "Glob", "Grep", "Bash"],
        model="inherit",
        permission_mode="acceptEdits",
        max_turns=25,
        skills=[],
    ),
    can_write=True,
)


REVIEWER = RoleDefinition(
    name="Reviewer",
    description=(
        "Evaluates implementation quality via independent review. Two sub-roles: "
        "Spec Compliance Reviewer (requirements match) and Code Quality Reviewer "
        "(architecture, SOLID, maintainability). Read-only — structurally enforced."
    ),
    pipeline_stages=["stage-2", "stage-3"],
    artifacts=ArtifactContract(
        produces=[
            "review verdicts (PASS/FAIL/CONCERNS)",
            "specific findings with severity",
        ],
        consumes=[
            "code changes from implementer",
            "plan/brief requirements",
            "quality criteria",
        ],
    ),
    agent_spec=AgentFileSpec(
        tools=["Read", "Glob", "Grep"],
        model="inherit",
        permission_mode="default",
        max_turns=15,
        skills=[],
    ),
    can_write=False,
)


NARRATOR = RoleDefinition(
    name="Narrator",
    description=(
        "Presents evidence for ceremony and documentation sync. Reads implementation "
        "and verification outputs to compose attestation surfaces and documentation updates."
    ),
    pipeline_stages=["stage-4", "stage-5"],
    artifacts=ArtifactContract(
        produces=[
            "evidence presentations",
            "ceremony artifacts",
            "documentation updates",
        ],
        consumes=[
            "implementation results",
            "verification outputs",
            "attestation records",
        ],
    ),
    agent_spec=AgentFileSpec(
        tools=["Read", "Glob", "Grep", "Bash"],
        model="inherit",
        permission_mode="default",
        max_turns=10,
        skills=[],
    ),
    can_write=False,
)


ROLE_REGISTRY: dict[RoleName, RoleDefinition] = {
    "Planner": PLANNER,
    "Implementer": IMPLEMENTER,
    "Reviewer": REVIEWER,
    "Narrator": NARRATOR,
}


def get_role(name: RoleName) -> RoleDefinition:
    """Look up a role definition by name."""
    return ROLE_REGISTRY[name]


def get_roles_for_stage(stage: str) -> list[RoleDefinition]:
    """Return all roles that operate in a given pipeline stage."""
    return [role for role in ROLE_REGISTRY.values() if stage in role.pipeline_stages]


def validate_tool_boundaries(role: RoleDefinition) -> list[str]:
    """Check that a role's tool allowlist enforces its write access contract.

    Returns a list of violation messages (empty if valid).
    """
    write_tools = {"Edit", "Write"}
    has_write_tools = bool(write_tools & set(role.agent_spec.tools))
    violations: list[str] = []
    if role.can_write and not has_write_tools:
        violations.append(f"{role.name}: can_write=True but tools lack Edit/Write")
    if not role.can_write and has_write_tools:
        found = write_tools & set(role.agent_spec.tools)
        violations.append(f"{role.name}: can_write=False but tools include {found}")
    return violations
