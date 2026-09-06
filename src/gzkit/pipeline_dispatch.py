"""Task dispatch models, complexity classification, and review protocol.

Extracted from pipeline_runtime.py to keep module sizes under 600 lines.
All public symbols are re-exported from pipeline_runtime for backward compatibility.
"""

from __future__ import annotations

import json
import re
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.complexity.thresholds import load_threshold_table
from gzkit.models.persona import load_persona
from gzkit.roles import (
    HandoffResult,
    HandoffStatus,
    ReviewFindingSeverity,
    ReviewResult,
    ReviewVerdict,
)

# Dispatch role -> persona file stem. Defined here rather than in
# pipeline_runtime because the composers below are the only readers and
# pipeline_runtime imports from this module (GHI #861).
ROLE_PERSONA_MAP: dict[str, str] = {
    "Implementer": "implementer",
    "Reviewer": "spec-reviewer",
    "QualityReviewer": "quality-reviewer",
    "Narrator": "narrator",
}

THRESHOLD_TABLE_PATH = ".gzkit/rules/complexity-thresholds.json"


def _persona_frame(project_root: Path, role: str) -> list[str]:
    """Return the persona identity frame for *role* as prompt lines.

    A dispatched subagent inherits none of this session's context, so the
    behavioral frame ADR-0.0.11 makes a first-class control surface reaches
    it only if the prompt carries it. Returns an empty list when the role
    has no mapping or the persona file is absent.
    """
    stem = ROLE_PERSONA_MAP.get(role)
    if stem is None:
        return []
    body = load_persona(project_root, stem)
    if not body:
        return []
    return ["### Persona", "", body.strip(), ""]


def _why_frame(why: str) -> list[str]:
    """Return the Why block required by AGENTS.md Behavior Rules - Always #6.

    The subagent cannot see why this task exists; without it, it cannot tell
    signal from noise in the surface it is handed.
    """
    return ["### Why", "", why.strip(), ""]


def _threshold_criterion(project_root: Path) -> str:
    """Render the size/complexity criterion from the declared authority.

    Per `.gzkit/rules/governance-core.md` Non-negotiable rules, thresholds are
    read from JSON, never restated in prose. The band values are rendered from
    the table so that editing the table moves the prompt.
    """
    cite = f"the block bands declared in `{THRESHOLD_TABLE_PATH}`"
    table_path = project_root / THRESHOLD_TABLE_PATH
    if not table_path.is_file():
        return (
            f"2. **Size and complexity** -- judge against {cite} "
            "(table not readable from this root)"
        )
    table = load_threshold_table(table_path)
    blocks = [b for b in table.bands if b.trigger_semantic == "block"]
    rendered = ", ".join(f"{b.metric} {b.absolute_number}" for b in blocks)
    return f"2. **Size and complexity** -- judge against {cite}: {rendered}"


# ---------------------------------------------------------------------------
# Subagent dispatch: data models (OBPI-0.18.0-02)
# ---------------------------------------------------------------------------

MAX_NEEDS_CONTEXT_RETRIES = 2
MAX_BLOCKED_FIX_ATTEMPTS = 2


class TaskComplexity(StrEnum):
    """Task complexity level for model-aware routing."""

    SIMPLE = "simple"
    STANDARD = "standard"
    COMPLEX = "complex"


DISPATCH_MODEL_MAP: dict[TaskComplexity, str] = {
    TaskComplexity.SIMPLE: "haiku",
    TaskComplexity.STANDARD: "sonnet",
    TaskComplexity.COMPLEX: "opus",
}


class TaskStatus(StrEnum):
    """Dispatch task lifecycle status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    DONE_WITH_CONCERNS = "done_with_concerns"
    BLOCKED = "blocked"


class DispatchTask(BaseModel):
    """A single plan task prepared for subagent dispatch."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: int = Field(..., description="1-based task index")
    description: str = Field(..., description="Task description from plan")
    allowed_paths: list[str] = Field(default_factory=list, description="Scoped file paths")
    test_expectations: list[str] = Field(default_factory=list, description="Expected tests")
    complexity: TaskComplexity = Field(..., description="Assessed complexity level")
    model: str = Field(..., description="Model tier for dispatch")


class DispatchRecord(BaseModel):
    """Mutable tracking record for a dispatched task."""

    model_config = ConfigDict(extra="forbid")

    task: DispatchTask = Field(..., description="The task being dispatched")
    status: TaskStatus = Field(TaskStatus.PENDING, description="Current lifecycle status")
    dispatch_count: int = Field(0, description="Number of dispatch attempts")
    result: HandoffResult | None = Field(None, description="Subagent result if completed")
    concerns: list[str] = Field(default_factory=list, description="Accumulated concerns")
    review_fix_count: int = Field(0, description="Number of review fix cycles")


class DispatchState(BaseModel):
    """Full dispatch state for a Stage 2 controller loop."""

    model_config = ConfigDict(extra="forbid")

    obpi_id: str = Field(..., description="OBPI being implemented")
    parent_adr: str = Field(..., description="Parent ADR identifier")
    records: list[DispatchRecord] = Field(default_factory=list, description="Task dispatch records")
    all_concerns: list[str] = Field(default_factory=list, description="Aggregated concerns")

    @property
    def current_index(self) -> int:
        """Index of the first non-terminal task, or total count if all done."""
        terminal = {TaskStatus.DONE, TaskStatus.DONE_WITH_CONCERNS, TaskStatus.BLOCKED}
        for i, rec in enumerate(self.records):
            if rec.status not in terminal:
                return i
        return len(self.records)

    @property
    def completed_count(self) -> int:
        """Count of tasks with DONE or DONE_WITH_CONCERNS status."""
        done = {TaskStatus.DONE, TaskStatus.DONE_WITH_CONCERNS}
        return sum(1 for r in self.records if r.status in done)

    @property
    def blocked_count(self) -> int:
        """Count of tasks with BLOCKED status."""
        return sum(1 for r in self.records if r.status == TaskStatus.BLOCKED)

    @property
    def is_finished(self) -> bool:
        """True when all tasks have reached a terminal status."""
        terminal = {TaskStatus.DONE, TaskStatus.DONE_WITH_CONCERNS, TaskStatus.BLOCKED}
        return all(r.status in terminal for r in self.records)


# ---------------------------------------------------------------------------
# Task extraction and complexity classification
# ---------------------------------------------------------------------------

_PLAN_TASK_RE = re.compile(r"^#{1,3}\s+(?:Task|Step)\s+(\d+)[:\s]*(.*)", re.IGNORECASE)
_NUMBERED_ITEM_RE = re.compile(r"^\d+\.\s+(.*)")


def extract_plan_tasks(plan_content: str) -> list[dict[str, str]]:
    """Parse plan markdown into a list of task dicts with id and description.

    Recognises two patterns:
    - Headings: ``## Task 1: description``
    - Numbered items: ``1. description``
    """
    tasks: list[dict[str, str]] = []
    for line in plan_content.splitlines():
        stripped = line.strip()
        heading_match = _PLAN_TASK_RE.match(stripped)
        if heading_match:
            tasks.append(
                {"id": heading_match.group(1), "description": heading_match.group(2).strip()}
            )
            continue
        numbered_match = _NUMBERED_ITEM_RE.match(stripped)
        if numbered_match and not tasks or numbered_match and tasks:
            tasks.append(
                {"id": str(len(tasks) + 1), "description": numbered_match.group(1).strip()}
            )
    return tasks


def classify_task_complexity(description: str, allowed_paths: list[str]) -> TaskComplexity:
    """Classify a task as SIMPLE, STANDARD, or COMPLEX based on file scope."""
    file_count = len(allowed_paths)
    if file_count <= 2:
        return TaskComplexity.SIMPLE
    if file_count <= 5:
        return TaskComplexity.STANDARD
    return TaskComplexity.COMPLEX


def select_dispatch_model(complexity: TaskComplexity) -> str:
    """Map task complexity to the dispatch model tier."""
    return DISPATCH_MODEL_MAP[complexity]


# ---------------------------------------------------------------------------
# Prompt composition and result parsing
# ---------------------------------------------------------------------------


def compose_implementer_prompt(
    task: DispatchTask,
    brief_requirements: list[str],
    *,
    why: str,
    project_root: Path,
    extra_context: str = "",
) -> str:
    """Build the scoped prompt for an implementer subagent dispatch."""
    lines = _persona_frame(project_root, "Implementer")
    lines.extend(
        [
            f"## Task {task.task_id}: {task.description}",
            "",
        ]
    )
    lines.extend(_why_frame(why))
    lines.extend(
        [
            "### Allowed Files",
            "",
        ]
    )
    for path in task.allowed_paths:
        lines.append(f"- `{path}`")
    lines.append("")

    if task.test_expectations:
        lines.append("### Test Expectations")
        lines.append("")
        for expectation in task.test_expectations:
            lines.append(f"- {expectation}")
        lines.append("")

    if brief_requirements:
        lines.append("### Brief Requirements")
        lines.append("")
        for req in brief_requirements:
            lines.append(f"- {req}")
        lines.append("")

    if extra_context:
        lines.append("### Additional Context")
        lines.append("")
        lines.append(extra_context)
        lines.append("")

    lines.extend(
        [
            "### Rules",
            "",
            "1. Only modify files listed in Allowed Files.",
            "2. Follow Red-Green-Refactor per behavior increment. Red: write a failing",
            "   test derived from the brief requirement, run it, confirm it fails for the",
            "   right reason. Green: the simplest code that passes. Refactor: improve",
            "   structure with tests green. Repeat per behavior -- do not batch all tests",
            "   first.",
            "3. Witness the Red: run `uv run gz arb red --req <REQ-ID> --obpi <OBPI-ID>`.",
            "   A test authored after the code, passing on its first run, is",
            "   byte-indistinguishable from a Red-first test without this receipt.",
            "   Report the assertion-level failure message you observed, not merely",
            "   that you wrote tests.",
            "4. Run `uv run ruff check . --fix && uv run ruff format .` after code changes.",
            "5. Run `uv run -m unittest -q` to verify tests pass.",
            "6. Return a JSON result block with status, files_changed, tests_added, concerns.",
            "",
        ]
    )
    return "\n".join(lines)


_RESULT_JSON_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.DOTALL)


def parse_handoff_result(agent_output: str) -> HandoffResult | None:
    """Extract a structured HandoffResult from subagent output text.

    Looks for a JSON code block containing the result fields.
    Returns None if no valid result block is found.
    """
    match = _RESULT_JSON_RE.search(agent_output)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
        return HandoffResult(**data)
    except (json.JSONDecodeError, ValueError, KeyError):
        return None


# ---------------------------------------------------------------------------
# Dispatch state management
# ---------------------------------------------------------------------------


def create_dispatch_state(
    obpi_id: str,
    parent_adr: str,
    plan_tasks: list[dict[str, str]],
    allowed_paths: list[str],
    test_expectations: list[str] | None = None,
) -> DispatchState:
    """Build initial DispatchState from parsed plan tasks."""
    records: list[DispatchRecord] = []
    for i, task_dict in enumerate(plan_tasks, start=1):
        complexity = classify_task_complexity(task_dict.get("description", ""), allowed_paths)
        model = select_dispatch_model(complexity)
        dispatch_task = DispatchTask(
            task_id=i,
            description=task_dict.get("description", ""),
            allowed_paths=allowed_paths,
            test_expectations=test_expectations or [],
            complexity=complexity,
            model=model,
        )
        records.append(DispatchRecord(task=dispatch_task))
    return DispatchState(obpi_id=obpi_id, parent_adr=parent_adr, records=records)


def handle_task_result(
    state: DispatchState,
    task_index: int,
    result: HandoffResult,
) -> str:
    """Process a subagent result and return the next action.

    Returns one of: "advance", "redispatch", "fix", "handoff", "complete".
    """
    if task_index < 0 or task_index >= len(state.records):
        return "handoff"

    record = state.records[task_index]
    record.result = result

    if result.status == HandoffStatus.DONE:
        record.status = TaskStatus.DONE
        if state.is_finished:
            return "complete"
        return "advance"

    if result.status == HandoffStatus.DONE_WITH_CONCERNS:
        record.status = TaskStatus.DONE_WITH_CONCERNS
        record.concerns.extend(result.concerns)
        state.all_concerns.extend(result.concerns)
        if state.is_finished:
            return "complete"
        return "advance"

    if result.status == HandoffStatus.NEEDS_CONTEXT:
        if record.dispatch_count >= MAX_NEEDS_CONTEXT_RETRIES:
            record.status = TaskStatus.BLOCKED
            record.concerns.append("circuit breaker: exceeded NEEDS_CONTEXT retry limit")
            return "handoff"
        return "redispatch"

    if result.status == HandoffStatus.BLOCKED:
        if record.dispatch_count < MAX_BLOCKED_FIX_ATTEMPTS:
            return "fix"
        record.status = TaskStatus.BLOCKED
        record.concerns.extend(result.concerns)
        return "handoff"

    record.status = TaskStatus.BLOCKED
    return "handoff"


def advance_dispatch(state: DispatchState, task_index: int) -> int | None:
    """Mark a task as in-progress for dispatch. Returns task index or None."""
    if task_index < 0 or task_index >= len(state.records):
        return None
    record = state.records[task_index]
    record.status = TaskStatus.IN_PROGRESS
    record.dispatch_count += 1
    return task_index


# ---------------------------------------------------------------------------
# Two-stage review protocol (OBPI-0.18.0-03)
# ---------------------------------------------------------------------------

MAX_REVIEW_FIX_CYCLES = 2

REVIEW_MODEL_MAP: dict[TaskComplexity, str] = {
    TaskComplexity.SIMPLE: "sonnet",
    TaskComplexity.STANDARD: "sonnet",
    TaskComplexity.COMPLEX: "opus",
}


def should_dispatch_review(status: HandoffStatus) -> bool:
    """Return True only for terminal-success statuses that warrant review.

    DONE and DONE_WITH_CONCERNS trigger review. BLOCKED and NEEDS_CONTEXT do not.
    """
    return status in {HandoffStatus.DONE, HandoffStatus.DONE_WITH_CONCERNS}


def select_review_model(complexity: TaskComplexity) -> str:
    """Map task complexity to the review model tier.

    Reviews always require judgment -- never route to haiku.
    SIMPLE and STANDARD use sonnet; COMPLEX uses opus.
    """
    return REVIEW_MODEL_MAP[complexity]


class ReviewerCapability(BaseModel):
    """What a reviewer persona can actually do, read from its agent definition."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    agent: str = Field(..., description="Agent definition name")
    tools: list[str] = Field(default_factory=list, description="Declared tool grant")
    can_execute: bool = Field(False, description="True if the grant includes a shell")


_EXECUTION_TOOLS: frozenset[str] = frozenset({"Bash", "BashOutput"})


def reviewer_capability(project_root: Path, agent: str) -> ReviewerCapability:
    """Read a reviewer persona's declared tool grant (GHI #941).

    The grant is READ, never asserted in prose. A composer that hardcoded
    "read-only" would contradict the agent definition the moment the grant
    changed — and granting reviewers execution is exactly the open question this
    issue leaves to the operator, so the disclosure has to track the file.

    Fails safe toward the restrictive claim: an unreadable or absent definition
    reports no execution, because promising a capability the reviewer may not
    have is the direction that produces the unrunnable ask.
    """
    definition = project_root / ".claude" / "agents" / f"{agent}.md"
    try:
        lines = definition.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ReviewerCapability(agent=agent)
    for line in lines:
        if line.lower().startswith("tools:"):
            tools = [t.strip() for t in line.split(":", 1)[1].split(",") if t.strip()]
            return ReviewerCapability(
                agent=agent,
                tools=tools,
                can_execute=bool(_EXECUTION_TOOLS & set(tools)),
            )
    return ReviewerCapability(agent=agent)


def _capability_frame(project_root: Path, agent: str) -> list[str]:
    """Disclose the reviewer's own reach, and route its gaps out of the verdict."""
    capability = reviewer_capability(project_root, agent)
    lines = ["### Your Capability", ""]
    if capability.tools:
        lines.append(f"Your tool grant is: {', '.join(capability.tools)}.")
    else:
        lines.append("Your tool grant could not be resolved; assume reading only.")
    if not capability.can_execute:
        lines.extend(
            [
                "You **cannot execute** commands. Verify by reading the code, never by",
                "running it. If a check in this prompt requires execution, do not attempt",
                "it and do not treat it as a defect.",
            ]
        )
    lines.extend(
        [
            "",
            "Anything you could not verify goes in `verification_gaps` — never in",
            "`findings`, and never in the verdict. `findings` and the verdict describe",
            "the CODE under review; a limit of your own is not a defect in it.",
            "",
        ]
    )
    return lines


def compose_spec_review_prompt(
    task: DispatchTask,
    brief_requirements: list[str],
    files_changed: list[str],
    *,
    why: str,
    project_root: Path,
) -> str:
    """Build the prompt for the spec compliance reviewer subagent.

    The reviewer must independently verify all requirements.
    Output must be a JSON code block in ReviewResult format.
    """
    lines = _persona_frame(project_root, "Reviewer")
    lines.extend(
        [
            "## Spec Compliance Review",
            "",
            "The implementer may be optimistic. Verify everything independently.",
            "",
        ]
    )
    lines.extend(_capability_frame(project_root, "spec-reviewer"))
    lines.extend(_why_frame(why))
    lines.extend(
        [
            f"### Task {task.task_id}: {task.description}",
            "",
            "### Files Changed",
            "",
        ]
    )
    for f in files_changed:
        lines.append(f"- `{f}`")
    lines.append("")

    if brief_requirements:
        lines.append("### Brief Requirements to Verify")
        lines.append("")
        for req in brief_requirements:
            lines.append(f"- {req}")
        lines.append("")

    lines.extend(
        [
            "### Instructions",
            "",
            "Read each changed file independently. For every requirement above, confirm whether",
            "the implementation satisfies it. Do not take the implementer's word for anything --",
            "check the code directly.",
            "",
            "Return your verdict as a JSON code block with this exact structure:",
            "",
            "```json",
            "{",
            '  "verdict": "PASS|FAIL|CONCERNS",',
            '  "findings": [',
            '    {"file": "...", "line": null, "severity": "critical|major|minor|info",',
            '     "message": "..."}',
            "  ],",
            '  "verification_gaps": ["checks you could not perform, if any"],',
            '  "summary": "Brief explanation of overall verdict"',
            "}",
            "```",
            "",
            "Severity guide:",
            "- critical: requirement not met, blocks advancement",
            "- major: significant gap, should be addressed",
            "- minor: small issue, noted but non-blocking",
            "- info: observation only",
            "",
        ]
    )
    return "\n".join(lines)


def compose_quality_review_prompt(
    files_changed: list[str],
    test_files: list[str],
    *,
    why: str,
    project_root: Path,
) -> str:
    """Build the prompt for the code quality reviewer subagent.

    Reviewer checks SOLID principles, size limits, test coverage, error handling,
    cross-platform compliance, and Pydantic conventions.
    Output must be a JSON code block in ReviewResult format.
    """
    lines = _persona_frame(project_root, "QualityReviewer")
    lines.extend(
        [
            "## Code Quality Review",
            "",
        ]
    )
    lines.extend(_capability_frame(project_root, "quality-reviewer"))
    lines.extend(_why_frame(why))
    lines.extend(
        [
            "### Files to Review",
            "",
        ]
    )
    for f in files_changed:
        lines.append(f"- `{f}`")
    lines.append("")

    if test_files:
        lines.append("### Test Files to Review")
        lines.append("")
        for f in test_files:
            lines.append(f"- `{f}`")
        lines.append("")

    lines.extend(
        [
            "### Quality Criteria",
            "",
            "Evaluate each file against all of the following criteria:",
            "",
            "1. **SOLID principles** -- single responsibility, open/closed, dependency inversion",
            _threshold_criterion(project_root),
            "3. **Test coverage** -- tests exist and cover the implementation surfaces",
            "4. **Error handling** -- no bare `except:` / `except Exception:`, typed errors",
            "5. **Cross-platform compliance** -- pathlib.Path for all paths, UTF-8 encoding,",
            "   context managers for temp files, no shell=True",
            "6. **Pydantic conventions** -- BaseModel (not dataclasses), ConfigDict with",
            "   extra='forbid', Field(...) for required fields",
            "",
            "### Instructions",
            "",
            "Read each file listed above. Report only what affects correctness or a",
            "stated brief requirement as blocking; everything else is an observation.",
            "Style preferences and taste calls are non-blocking -- record them at",
            "`minor` or `info` severity and do not escalate. Do not manufacture",
            "findings: PASS with no findings is a valid and expected verdict.",
            "",
            "Return your verdict as a JSON code block with this exact structure:",
            "",
            "```json",
            "{",
            '  "verdict": "PASS|FAIL|CONCERNS",',
            '  "findings": [',
            '    {"file": "...", "line": null, "severity": "critical|major|minor|info",',
            '     "message": "..."}',
            "  ],",
            '  "verification_gaps": ["checks you could not perform, if any"],',
            '  "summary": "Brief explanation of overall verdict"',
            "}",
            "```",
            "",
            "Severity guide:",
            "- critical: serious violation that must be fixed before advancement",
            "- major: notable issue that should be addressed",
            "- minor: small improvement opportunity",
            "- info: observation only",
            "",
        ]
    )
    return "\n".join(lines)


def parse_review_result(reviewer_output: str) -> ReviewResult | None:
    """Extract a ReviewResult from reviewer subagent output text.

    Looks for a JSON code block containing the result fields.
    Returns None if no valid result block is found.
    """
    match = _RESULT_JSON_RE.search(reviewer_output)
    if not match:
        return None
    try:
        data = json.loads(match.group(1))
        return ReviewResult(**data)
    except (json.JSONDecodeError, ValueError, KeyError):
        return None


def review_has_critical_findings(result: ReviewResult) -> bool:
    """Return True if any finding in the result has critical severity."""
    return any(f.severity == ReviewFindingSeverity.CRITICAL for f in result.findings)


def review_blocks_advancement(result: ReviewResult) -> bool:
    """Return True if the review result should block task advancement.

    FAIL always blocks. CONCERNS with critical findings blocks.
    PASS never blocks. CONCERNS without critical findings does not block.
    """
    return result.verdict == ReviewVerdict.FAIL or (
        result.verdict == ReviewVerdict.CONCERNS and review_has_critical_findings(result)
    )


def handle_review_cycle(
    state: DispatchState,
    task_index: int,
    spec_result: ReviewResult,
    quality_result: ReviewResult | None,
) -> str:
    """Process review results for a task and determine the next action.

    Returns one of: "advance", "fix", "blocked".

    Logic:
    - If spec blocks advancement: increment review_fix_count, return "fix" or "blocked".
    - If spec passes: check quality result (if provided).
    - If quality blocks advancement: increment review_fix_count, return "fix" or "blocked".
    - If both pass: return "advance".
    """
    if task_index < 0 or task_index >= len(state.records):
        return "blocked"

    record = state.records[task_index]

    if review_blocks_advancement(spec_result):
        record.review_fix_count += 1
        if record.review_fix_count > MAX_REVIEW_FIX_CYCLES:
            return "blocked"
        return "fix"

    if quality_result is not None and review_blocks_advancement(quality_result):
        record.review_fix_count += 1
        if record.review_fix_count > MAX_REVIEW_FIX_CYCLES:
            return "blocked"
        return "fix"

    return "advance"
