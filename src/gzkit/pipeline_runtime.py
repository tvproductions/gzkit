"""Shared runtime helpers for the OBPI pipeline command and hook surfaces."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field

from gzkit.roles import (
    HandoffResult,
    HandoffStatus,
    ReviewFindingSeverity,
    ReviewResult,
    ReviewVerdict,
)

PIPELINE_RECEIPT_FILE = ".plan-audit-receipt.json"
PIPELINE_LEGACY_MARKER = ".pipeline-active.json"
STALE_MARKER_HOURS = 4


def pipeline_command(obpi_id: str, start_from: str | None = None) -> str:
    """Return the canonical runtime command for the target OBPI."""
    command = f"uv run gz obpi pipeline {obpi_id}"
    if start_from:
        return f"{command} --from={start_from}"
    return command


def pipeline_git_sync_command() -> str:
    """Return the guarded sync command used after ceremony."""
    return "uv run gz git-sync --apply --lint --test"


def pipeline_plans_dir(project_root: Path) -> Path:
    """Return the canonical Claude plans directory."""
    return project_root / ".claude" / "plans"


def load_pipeline_json(path: Path) -> dict[str, Any] | None:
    """Best-effort JSON loader for pipeline receipts and markers."""
    try:
        return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return None


def pipeline_marker_paths(plans_dir: Path, obpi_id: str) -> tuple[Path, Path]:
    """Return the per-OBPI and legacy marker paths."""
    return plans_dir / f".pipeline-active-{obpi_id}.json", plans_dir / PIPELINE_LEGACY_MARKER


def pipeline_stage_name(start_from: str | None) -> str:
    """Return the active stage label persisted in the marker payload."""
    if start_from == "verify":
        return "verify"
    if start_from == "ceremony":
        return "ceremony"
    if start_from == "sync":
        return "sync"
    return "implement"


def pipeline_stage_output(
    obpi_id: str,
    start_from: str | None,
    *,
    blockers: list[str] | None = None,
    requires_human_attestation: bool = False,
) -> dict[str, Any]:
    """Return structured stage-output fields for the active pipeline stage."""
    active_blockers = list(blockers or [])
    if start_from == "verify":
        if active_blockers:
            return {
                "blockers": active_blockers,
                "required_human_action": None,
                "next_command": None,
                "resume_point": "verify",
            }
        return {
            "blockers": [],
            "required_human_action": None,
            "next_command": pipeline_command(obpi_id, "ceremony"),
            "resume_point": "ceremony",
        }
    if start_from == "ceremony":
        return {
            "blockers": [],
            "required_human_action": (
                "Present evidence and obtain explicit human attestation before "
                "completion accounting."
                if requires_human_attestation
                else None
            ),
            "next_command": pipeline_command(obpi_id, "sync"),
            "resume_point": "sync",
        }
    if start_from == "sync":
        return {
            "blockers": [],
            "required_human_action": None,
            "next_command": pipeline_git_sync_command(),
            "resume_point": None,
        }
    return {
        "blockers": [],
        "required_human_action": None,
        "next_command": pipeline_command(obpi_id, "verify"),
        "resume_point": "verify",
    }


def pipeline_marker_payload(
    obpi_id: str,
    parent_adr: str,
    lane: str,
    start_from: str | None,
    receipt_state: str,
    *,
    execution_mode: str = "normal",
    requires_human_attestation: bool = False,
) -> dict[str, Any]:
    """Build the persisted active-state payload for pipeline markers."""
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload: dict[str, Any] = {
        "obpi_id": obpi_id,
        "parent_adr": parent_adr,
        "lane": lane,
        "entry": start_from or "full",
        "execution_mode": execution_mode,
        "current_stage": pipeline_stage_name(start_from),
        "started_at": timestamp,
        "updated_at": timestamp,
        "receipt_state": receipt_state,
    }
    payload.update(
        pipeline_stage_output(
            obpi_id,
            start_from,
            requires_human_attestation=requires_human_attestation,
        )
    )
    return payload


def write_pipeline_markers(plans_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    """Create active pipeline markers for the target OBPI."""
    obpi_id = str(payload["obpi_id"])
    per_obpi_marker, legacy_marker = pipeline_marker_paths(plans_dir, obpi_id)
    plans_dir.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2) + "\n"
    per_obpi_marker.write_text(encoded, encoding="utf-8")
    legacy_marker.write_text(encoded, encoding="utf-8")
    return per_obpi_marker, legacy_marker


def refresh_pipeline_markers(plans_dir: Path, obpi_id: str, *, blockers: list[str]) -> None:
    """Refresh active marker stage-output fields for the target OBPI."""
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    per_obpi_marker, legacy_marker = pipeline_marker_paths(plans_dir, obpi_id)
    for marker_path in (per_obpi_marker, legacy_marker):
        marker = load_pipeline_json(marker_path)
        if marker is None or marker.get("obpi_id") != obpi_id:
            continue
        entry = str(marker.get("entry") or "full")
        start_from = None if entry == "full" else entry
        marker.update(pipeline_stage_output(obpi_id, start_from, blockers=blockers))
        marker["updated_at"] = timestamp
        marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")


def remove_pipeline_markers(plans_dir: Path, obpi_id: str) -> None:
    """Remove active markers only when they still point at the target OBPI."""
    per_obpi_marker, legacy_marker = pipeline_marker_paths(plans_dir, obpi_id)
    for marker_path in (per_obpi_marker, legacy_marker):
        marker = load_pipeline_json(marker_path)
        if marker is None or marker.get("obpi_id") != obpi_id:
            continue
        marker_path.unlink(missing_ok=True)


def pipeline_concurrency_blockers(plans_dir: Path, obpi_id: str) -> list[str]:
    """Detect active markers that would conflict with this pipeline launch."""
    blockers: list[str] = []
    legacy_marker = load_pipeline_json(plans_dir / PIPELINE_LEGACY_MARKER)
    if legacy_marker is not None:
        legacy_obpi = str(legacy_marker.get("obpi_id") or "")
        if legacy_obpi and legacy_obpi != obpi_id:
            blockers.append(f"another OBPI is already active in the legacy marker: {legacy_obpi}")

    for marker_path in sorted(plans_dir.glob(".pipeline-active-*.json")):
        marker = load_pipeline_json(marker_path)
        if marker is None:
            continue
        active_obpi = str(marker.get("obpi_id") or "")
        if active_obpi and active_obpi != obpi_id:
            blockers.append(f"another OBPI is already active: {active_obpi}")
    return blockers


def pipeline_receipt_path(plans_dir: Path, obpi_id: str) -> Path:
    """Return the per-OBPI receipt path."""
    return plans_dir / f".plan-audit-receipt-{obpi_id}.json"


def _resolve_receipt_path(plans_dir: Path, obpi_id: str) -> Path | None:
    """Find the best receipt file: per-OBPI first, then legacy, then discovery."""
    if obpi_id:
        per_obpi = pipeline_receipt_path(plans_dir, obpi_id)
        if per_obpi.exists():
            return per_obpi
    legacy = plans_dir / PIPELINE_RECEIPT_FILE
    if legacy.exists():
        return legacy
    if not obpi_id:
        candidates = sorted(
            plans_dir.glob(".plan-audit-receipt-*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if candidates:
            return candidates[0]
    return None


def load_plan_audit_receipt(
    plans_dir: Path,
    obpi_id: str,
) -> tuple[str, list[str], dict[str, Any] | None]:
    """Return receipt state plus non-fatal warnings."""
    receipt_path = _resolve_receipt_path(plans_dir, obpi_id)
    if receipt_path is None:
        return (
            "missing",
            ["plan-audit receipt is missing; proceeding with an explicit gap"],
            None,
        )

    receipt = load_pipeline_json(receipt_path)
    if receipt is None:
        return (
            "invalid",
            ["plan-audit receipt is unreadable; proceeding with an explicit gap"],
            None,
        )

    receipt_obpi = str(receipt.get("obpi_id") or "")
    if obpi_id and receipt_obpi and receipt_obpi != obpi_id:
        return (
            "other_obpi",
            [f"plan-audit receipt currently targets another OBPI: {receipt_obpi}"],
            receipt,
        )

    verdict = str(receipt.get("verdict") or "")
    if verdict == "FAIL":
        return "fail", [], receipt
    if verdict == "PASS":
        return "pass", [], receipt
    return (
        "unknown",
        [f"plan-audit receipt verdict is not recognized: {verdict or '(missing)'}"],
        receipt,
    )


def pipeline_stage_labels(start_from: str | None) -> list[str]:
    """Return ordered stage labels for the selected entrypoint."""
    if start_from == "verify":
        return ["1. Load Context", "3. Verify", "4. Present Evidence", "5. Sync And Account"]
    if start_from == "ceremony":
        return ["1. Load Context", "4. Present Evidence", "5. Sync And Account"]
    if start_from == "sync":
        return ["1. Load Context", "5. Sync And Account"]
    return [
        "1. Load Context",
        "2. Implement",
        "3. Verify",
        "4. Present Evidence",
        "5. Sync And Account",
    ]


def marker_matches(marker_path: Path, obpi_id: str) -> bool:
    """Return whether a marker exists and matches the target OBPI."""
    if not marker_path.exists():
        return False
    marker = load_pipeline_json(marker_path)
    return bool(marker and marker.get("obpi_id") == obpi_id)


def find_active_pipeline_marker(plans_dir: Path) -> dict[str, Any] | None:
    """Return the first readable active pipeline marker payload."""
    marker_paths = sorted(plans_dir.glob(".pipeline-active-*.json"))
    marker_paths.append(plans_dir / PIPELINE_LEGACY_MARKER)
    for marker_path in marker_paths:
        if not marker_path.exists():
            continue
        marker = load_pipeline_json(marker_path)
        if marker is not None:
            return marker
        continue  # skip corrupted marker, check remaining
    return None


def find_obpi_brief(docs_root: Path, obpi_id: str) -> Path | None:
    """Find the OBPI brief that corresponds to the active marker."""
    if not docs_root.is_dir():
        return None
    matches = sorted(docs_root.rglob(f"{obpi_id}*.md"))
    return matches[0] if matches else None


def extract_brief_status(brief_path: Path) -> str | None:
    """Extract the brief status from a brief file."""
    try:
        lines = brief_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("status:"):
            return stripped.split(":", 1)[1].strip()
        if stripped.startswith("**Status:**"):
            return stripped.split("**Status:**", 1)[1].strip()
        if stripped.startswith("**Brief Status:**"):
            return stripped.split("**Brief Status:**", 1)[1].strip()
    return None


def pipeline_resume_command(marker: dict[str, Any]) -> str | None:
    """Return the canonical next command for an active marker when possible."""
    next_command = str(marker.get("next_command") or "").strip()
    if next_command:
        return next_command

    obpi_id = str(marker.get("obpi_id") or "").strip()
    if not obpi_id:
        return None

    resume_point = str(marker.get("resume_point") or "").strip()
    if resume_point in {"verify", "ceremony", "sync"}:
        return pipeline_command(obpi_id, resume_point)
    if str(marker.get("current_stage") or "").strip() == "implement":
        return pipeline_command(obpi_id, "verify")
    return None


def pipeline_router_message(obpi_id: str) -> str:
    """Render the standard router output after plan approval."""
    return (
        f"OBPI plan approved: {obpi_id}\n"
        "\n"
        "REQUIRED: Execute the approved plan via the governance runtime:\n"
        f"  {pipeline_command(obpi_id)}\n"
        "\n"
        "Do NOT implement directly; the runtime preserves the required\n"
        "verification, acceptance ceremony, and sync stages.\n"
        "\n"
        "If implementation is already done, use --from=verify or --from=ceremony."
    )


def pipeline_gate_message(obpi_id: str) -> str:
    """Render the standard write-gate blocker output."""
    return (
        f"BLOCKED: Pipeline not invoked for {obpi_id}.\n"
        "\n"
        "A plan-audit receipt exists but the governance pipeline has not\n"
        "been started. Implementation writes to src/ and tests/ are gated\n"
        "until the pipeline is invoked.\n"
        "\n"
        "REQUIRED: Invoke the pipeline:\n"
        f"  {pipeline_command(obpi_id)}\n"
        "\n"
        "If implementation is already complete, use:\n"
        f"  {pipeline_command(obpi_id, 'verify')}\n"
    )


def stale_pipeline_marker_message(obpi_id: str) -> str:
    """Render the stale-marker note for completed briefs."""
    return (
        "STALE PIPELINE MARKER\n"
        "\n"
        f"Active marker still references {obpi_id}, but the brief is already\n"
        "Completed. The pipeline marker is runtime-managed; re-enter the\n"
        "runtime only if more governance stages remain.\n"
    )


def pipeline_completion_reminder_message(
    marker: dict[str, Any],
    *,
    brief_status: str | None,
) -> str | None:
    """Render the advisory reminder for an incomplete active pipeline."""
    obpi_id = str(marker.get("obpi_id") or "").strip()
    if not obpi_id:
        return None

    if brief_status == "Completed":
        return stale_pipeline_marker_message(obpi_id)

    current_stage = str(marker.get("current_stage") or "implement")
    next_command = pipeline_resume_command(marker)
    blockers = [
        str(item).strip()
        for item in cast(list[Any], marker.get("blockers") or [])
        if str(item).strip()
    ]
    required_human_action = str(marker.get("required_human_action") or "").strip()

    lines = [
        "PIPELINE COMPLETION REMINDER",
        "",
        f"Active OBPI pipeline: {obpi_id}",
        f"Brief status: {brief_status or 'Unknown'}",
        f"Current stage: {current_stage}",
    ]
    receipt_state = str(marker.get("receipt_state") or "").strip()
    if receipt_state:
        lines.append(f"Receipt state: {receipt_state}")
    lines.append("")
    lines.append("You are about to commit or push while the governance pipeline still")
    lines.append("appears incomplete. Finish the runtime-managed closeout path first:")
    lines.append("")

    if blockers:
        lines.append("Active blockers:")
        lines.extend(f"  - {blocker}" for blocker in blockers)
        lines.append("")

    if required_human_action:
        lines.append("Required human action:")
        lines.append(f"  - {required_human_action}")
        lines.append("")

    if next_command:
        lines.append("Next canonical command:")
        lines.append(f"  {next_command}")
    else:
        lines.append("Next canonical command:")
        lines.append(f"  {pipeline_command(obpi_id, 'verify')}")
    lines.append("")
    lines.append("Do not clear the pipeline marker by hand; the runtime owns it.")
    return "\n".join(lines)


def completion_receipt_missing_message(obpi_id: str) -> str:
    """Render the validator message for a missing completion receipt."""
    return (
        f"\n⛔ BLOCKED: Cannot mark {obpi_id} as Completed.\n"
        "\n"
        "No completion receipt found in .gzkit/ledger.jsonl\n"
        "\n"
        "REQUIRED: finish the canonical pipeline path so completion accounting is recorded:\n"
        f"  {pipeline_command(obpi_id, 'verify')}\n"
        "\n"
        "If verification already passed, continue with:\n"
        f"  {pipeline_command(obpi_id, 'ceremony')}\n"
    )


def find_stale_pipeline_markers(
    plans_dir: Path, *, max_age_hours: int = STALE_MARKER_HOURS
) -> list[tuple[Path, dict[str, Any]]]:
    """Return marker paths and payloads whose updated_at exceeds the TTL."""
    now = datetime.now(UTC)
    stale: list[tuple[Path, dict[str, Any]]] = []
    candidates = sorted(plans_dir.glob(".pipeline-active-*.json"))
    candidates.append(plans_dir / PIPELINE_LEGACY_MARKER)
    for marker_path in candidates:
        if not marker_path.exists():
            continue
        marker = load_pipeline_json(marker_path)
        if marker is None:
            stale.append((marker_path, {}))
            continue
        updated_at = str(marker.get("updated_at") or "")
        if not updated_at:
            stale.append((marker_path, marker))
            continue
        try:
            marker_time = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
        except ValueError:
            stale.append((marker_path, marker))
            continue
        age_hours = (now - marker_time).total_seconds() / 3600
        if age_hours > max_age_hours:
            stale.append((marker_path, marker))
    return stale


def clear_stale_pipeline_markers(
    plans_dir: Path, *, max_age_hours: int = STALE_MARKER_HOURS
) -> list[tuple[Path, str]]:
    """Remove stale markers and return removed paths with their OBPI IDs."""
    removed: list[tuple[Path, str]] = []
    for marker_path, marker in find_stale_pipeline_markers(plans_dir, max_age_hours=max_age_hours):
        obpi_id = str(marker.get("obpi_id") or "unknown")
        marker_path.unlink(missing_ok=True)
        removed.append((marker_path, obpi_id))
    return removed


# ---------------------------------------------------------------------------
# Subagent dispatch: data models and orchestration (OBPI-0.18.0-02)
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
        done = {TaskStatus.DONE, TaskStatus.DONE_WITH_CONCERNS}
        return sum(1 for r in self.records if r.status in done)

    @property
    def blocked_count(self) -> int:
        return sum(1 for r in self.records if r.status == TaskStatus.BLOCKED)

    @property
    def is_finished(self) -> bool:
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
    extra_context: str = "",
) -> str:
    """Build the scoped prompt for an implementer subagent dispatch."""
    lines = [
        f"## Task {task.task_id}: {task.description}",
        "",
        "### Allowed Files",
        "",
    ]
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
            "2. Write tests before or alongside implementation (TDD).",
            "3. Run `uv run ruff check . --fix && uv run ruff format .` after code changes.",
            "4. Run `uv run -m unittest -q` to verify tests pass.",
            "5. Return a JSON result block with status, files_changed, tests_added, concerns.",
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

    Reviews always require judgment — never route to haiku.
    SIMPLE and STANDARD use sonnet; COMPLEX uses opus.
    """
    return REVIEW_MODEL_MAP[complexity]


def compose_spec_review_prompt(
    task: DispatchTask,
    brief_requirements: list[str],
    files_changed: list[str],
) -> str:
    """Build the prompt for the spec compliance reviewer subagent.

    The reviewer must independently verify all requirements.
    Output must be a JSON code block in ReviewResult format.
    """
    lines = [
        "## Spec Compliance Review",
        "",
        "The implementer may be optimistic. Verify everything independently.",
        "",
        f"### Task {task.task_id}: {task.description}",
        "",
        "### Files Changed",
        "",
    ]
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
            "the implementation satisfies it. Do not take the implementer's word for anything —",
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
) -> str:
    """Build the prompt for the code quality reviewer subagent.

    Reviewer checks SOLID principles, size limits, test coverage, error handling,
    cross-platform compliance, and Pydantic conventions.
    Output must be a JSON code block in ReviewResult format.
    """
    lines = [
        "## Code Quality Review",
        "",
        "### Files to Review",
        "",
    ]
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
            "1. **SOLID principles** — single responsibility, open/closed, dependency inversion",
            "2. **Size limits** — functions <=50 lines, modules <=600 lines, classes <=300 lines",
            "3. **Test coverage** — tests exist and cover the implementation surfaces",
            "4. **Error handling** — no bare `except:` / `except Exception:`, typed errors",
            "5. **Cross-platform compliance** — pathlib.Path for all paths, UTF-8 encoding,",
            "   context managers for temp files, no shell=True",
            "6. **Pydantic conventions** — BaseModel (not dataclasses), ConfigDict with",
            "   extra='forbid', Field(...) for required fields",
            "",
            "### Instructions",
            "",
            "Read each file listed above. Flag any violations of the quality criteria.",
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


# ---------------------------------------------------------------------------
# REQ-level parallel verification dispatch (OBPI-0.18.0-04)
# ---------------------------------------------------------------------------

MAX_VERIFICATION_FIX_CYCLES = 1

_BRIEF_REQ_RE = re.compile(r"^\d+\.\s+REQUIREMENT:\s*(.*)", re.IGNORECASE)


class VerificationScope(BaseModel):
    """A single requirement scoped for verification dispatch."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_index: int = Field(..., description="1-based requirement index")
    requirement_text: str = Field(..., description="Full requirement text")
    test_paths: list[str] = Field(default_factory=list, description="Test files to run")
    verification_commands: list[str] = Field(
        default_factory=list, description="Commands for verification"
    )
    pass_criteria: str = Field("All tests pass", description="Expected pass criteria")


class VerificationOutcome(StrEnum):
    """Outcome of a single REQ verification."""

    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


class VerificationResult(BaseModel):
    """Result from a verification subagent for one or more REQs."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_index: int = Field(..., description="1-based requirement index")
    outcome: VerificationOutcome = Field(..., description="Verification outcome")
    detail: str = Field("", description="Human-readable detail")
    commands_run: list[str] = Field(default_factory=list, description="Commands executed")


class VerificationPlan(BaseModel):
    """Dispatch plan for Stage 3 REQ-level verification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    scopes: list[VerificationScope] = Field(
        default_factory=list, description="All verification scopes"
    )
    independent_groups: list[list[int]] = Field(
        default_factory=list,
        description="Groups of req_index values that can run in parallel",
    )
    strategy: str = Field("sequential", description="'parallel', 'sequential', or 'mixed'")


def extract_verification_scopes(
    brief_content: str,
    test_paths: list[str] | None = None,
) -> list[VerificationScope]:
    """Parse brief requirements into verification scopes.

    Each numbered ``REQUIREMENT:`` line becomes one scope. If explicit
    test_paths are provided, they are attached to every scope. Otherwise
    scopes have empty test_paths (caller must populate or fall back to
    sequential dispatch).
    """
    scopes: list[VerificationScope] = []
    req_index = 0
    for line in brief_content.splitlines():
        match = _BRIEF_REQ_RE.match(line.strip())
        if match:
            req_index += 1
            scopes.append(
                VerificationScope(
                    req_index=req_index,
                    requirement_text=match.group(1).strip(),
                    test_paths=list(test_paths or []),
                )
            )
    return scopes


def compute_path_overlap(scopes: list[VerificationScope]) -> dict[tuple[int, int], list[str]]:
    """Return overlapping test paths between each pair of scopes.

    Keys are ``(req_a, req_b)`` tuples (``a < b``). Values are the shared
    paths. An empty dict means no overlaps exist.
    """
    overlaps: dict[tuple[int, int], list[str]] = {}
    for i, scope_a in enumerate(scopes):
        set_a = set(scope_a.test_paths)
        for scope_b in scopes[i + 1 :]:
            shared = sorted(set_a & set(scope_b.test_paths))
            if shared:
                overlaps[(scope_a.req_index, scope_b.req_index)] = shared
    return overlaps


def partition_independent_groups(
    scopes: list[VerificationScope],
    overlaps: dict[tuple[int, int], list[str]],
) -> list[list[int]]:
    """Partition scopes into groups of non-overlapping requirements.

    Within each group, no two scopes share test paths — they can be
    dispatched to parallel worktree-isolated subagents. Scopes that
    overlap are placed in the same group and verified sequentially within
    a single subagent.

    Uses a simple union-find to merge overlapping scopes into connected
    components.
    """
    if not scopes:
        return []

    parent: dict[int, int] = {s.req_index: s.req_index for s in scopes}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for req_a, req_b in overlaps:
        union(req_a, req_b)

    groups: dict[int, list[int]] = {}
    for s in scopes:
        root = find(s.req_index)
        groups.setdefault(root, []).append(s.req_index)

    return [sorted(members) for members in sorted(groups.values())]


def build_verification_plan(
    scopes: list[VerificationScope],
) -> VerificationPlan:
    """Create a dispatch plan from extracted verification scopes.

    - Zero scopes → empty plan, sequential (baseline-only).
    - All scopes lack test_paths → sequential fallback.
    - Otherwise → compute overlaps and partition into groups.
    """
    if not scopes:
        return VerificationPlan(strategy="sequential")

    if all(len(s.test_paths) == 0 for s in scopes):
        return VerificationPlan(
            scopes=scopes,
            independent_groups=[[s.req_index for s in scopes]],
            strategy="sequential",
        )

    overlaps = compute_path_overlap(scopes)
    groups = partition_independent_groups(scopes, overlaps)

    if len(groups) <= 1:
        strategy = "sequential"
    elif all(len(g) == 1 for g in groups):
        strategy = "parallel"
    else:
        strategy = "mixed"

    return VerificationPlan(
        scopes=scopes,
        independent_groups=groups,
        strategy=strategy,
    )


def compose_verification_prompt(
    scopes: list[VerificationScope],
    *,
    group_label: str = "",
) -> str:
    """Build the prompt for a verification subagent.

    The subagent receives one or more REQs to verify, runs the specified
    test commands, and returns a JSON result block per REQ.
    """
    lines = [
        "## REQ Verification",
        "",
    ]
    if group_label:
        lines.append(f"**Group:** {group_label}")
        lines.append("")

    lines.append("### Requirements to Verify")
    lines.append("")
    for scope in scopes:
        lines.append(f"**REQ-{scope.req_index}:** {scope.requirement_text}")
        if scope.test_paths:
            lines.append(f"  Test files: {', '.join(f'`{p}`' for p in scope.test_paths)}")
        if scope.verification_commands:
            lines.append(f"  Commands: {', '.join(f'`{c}`' for c in scope.verification_commands)}")
        lines.append(f"  Pass criteria: {scope.pass_criteria}")
        lines.append("")

    lines.extend(
        [
            "### Instructions",
            "",
            "For each requirement above:",
            "1. Read the relevant source and test files.",
            "2. Run the specified test commands (or `uv run -m unittest -q` if none specified).",
            "3. Verify the implementation satisfies the requirement text.",
            "",
            "Return results as a JSON code block with this structure:",
            "",
            "```json",
            "[",
            "  {",
            '    "req_index": 1,',
            '    "outcome": "PASS|FAIL|ERROR",',
            '    "detail": "explanation",',
            '    "commands_run": ["uv run -m unittest ..."]',
            "  }",
            "]",
            "```",
            "",
            "You are read-only — do NOT modify any files. Only read and run tests.",
            "",
        ]
    )
    return "\n".join(lines)


_VERIFICATION_JSON_RE = re.compile(r"```json\s*(\[.*?\])\s*```", re.DOTALL)


def parse_verification_results(agent_output: str) -> list[VerificationResult]:
    """Extract VerificationResult list from verification subagent output.

    Looks for a JSON code block containing an array of result objects.
    Returns an empty list if no valid result block is found.
    """
    match = _VERIFICATION_JSON_RE.search(agent_output)
    if not match:
        return []
    try:
        data = json.loads(match.group(1))
        if not isinstance(data, list):
            return []
        return [VerificationResult(**item) for item in data]
    except (json.JSONDecodeError, ValueError, KeyError):
        return []


def aggregate_verification_results(
    results: list[VerificationResult],
    expected_req_indices: list[int],
) -> tuple[bool, list[VerificationResult]]:
    """Aggregate results across all REQs.

    Returns ``(all_passed, failures)`` where ``all_passed`` is True only
    when every expected REQ has a PASS outcome. Missing REQs are treated
    as FAIL.
    """
    result_map = {r.req_index: r for r in results}
    failures: list[VerificationResult] = []

    for req_idx in expected_req_indices:
        result = result_map.get(req_idx)
        if result is None:
            failures.append(
                VerificationResult(
                    req_index=req_idx,
                    outcome=VerificationOutcome.FAIL,
                    detail="No result received from verification subagent",
                )
            )
        elif result.outcome != VerificationOutcome.PASS:
            failures.append(result)

    return len(failures) == 0, failures


def should_fallback_to_sequential(plan: VerificationPlan) -> bool:
    """Return True if the plan requires sequential fallback.

    Sequential fallback is required when:
    - Strategy is explicitly "sequential"
    - No scopes have test paths
    - All scopes are in a single group (no parallelism benefit)
    """
    return plan.strategy == "sequential"


# ---------------------------------------------------------------------------
# Subagent dispatch tracking and integration (OBPI-0.18.0-05)
# ---------------------------------------------------------------------------

AGENT_FILE_MAP: dict[str, str] = {
    "Implementer": ".claude/agents/implementer.md",
    "Reviewer": ".claude/agents/spec-reviewer.md",
    "QualityReviewer": ".claude/agents/quality-reviewer.md",
    "Narrator": ".claude/agents/narrator.md",
    "Planner": "",
}

PIPELINE_CONFIG_FILE = ".gzkit/pipeline-config.json"
DISPATCH_SUMMARY_PREFIX = ".pipeline-dispatch-"


class SubagentDispatchRecord(BaseModel):
    """Per-dispatch tracking record persisted in the pipeline marker."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    task_id: int = Field(..., description="1-based task index")
    role: str = Field(..., description="Role name (Implementer, Reviewer, etc.)")
    agent_file: str = Field(..., description="Path to .claude/agents/ file")
    model: str = Field(..., description="Model tier used for dispatch")
    isolation: str = Field("inline", description="Isolation mode (inline or worktree)")
    background: bool = Field(False, description="Whether dispatched in background")
    dispatched_at: str = Field(..., description="ISO-8601 dispatch timestamp")
    completed_at: str | None = Field(None, description="ISO-8601 completion timestamp")
    status: str = Field("pending", description="Dispatch status")
    result: dict[str, Any] | None = Field(None, description="Serialized result payload")


class DispatchAggregation(BaseModel):
    """Result aggregation computed from completed dispatch records."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    total_tasks: int = Field(..., description="Total dispatch records")
    completed: int = Field(..., description="Records with done status")
    blocked: int = Field(..., description="Records with blocked status")
    fix_cycles: int = Field(..., description="Total re-dispatch attempts")
    review_findings_by_severity: dict[str, int] = Field(
        default_factory=dict, description="Finding counts keyed by severity"
    )
    model_usage_per_role: dict[str, dict[str, int]] = Field(
        default_factory=dict, description="Model usage counts per role"
    )


class ModelRoutingConfig(BaseModel):
    """Declarative model routing configuration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    implementer: dict[str, str] = Field(
        default_factory=lambda: {"simple": "haiku", "standard": "sonnet", "complex": "opus"},
    )
    reviewer: dict[str, str] = Field(
        default_factory=lambda: {"simple": "sonnet", "standard": "sonnet", "complex": "opus"},
    )
    verifier: dict[str, str] = Field(
        default_factory=lambda: {"simple": "sonnet", "standard": "sonnet", "complex": "opus"},
    )


def load_model_routing_config(project_root: Path) -> ModelRoutingConfig:
    """Load model routing config from project or return defaults."""
    config_path = project_root / PIPELINE_CONFIG_FILE
    if config_path.is_file():
        raw = json.loads(config_path.read_text(encoding="utf-8"))
        routing = raw.get("model_routing")
        if isinstance(routing, dict):
            return ModelRoutingConfig(**routing)
    return ModelRoutingConfig()


def get_agent_file_for_role(role_name: str) -> str:
    """Map a role name to its agent file path."""
    return AGENT_FILE_MAP.get(role_name, "")


def create_subagent_dispatch_record(
    task_id: int,
    role: str,
    model: str,
    *,
    isolation: str = "inline",
    background: bool = False,
) -> SubagentDispatchRecord:
    """Create a new dispatch record with the current UTC timestamp."""
    return SubagentDispatchRecord(
        task_id=task_id,
        role=role,
        agent_file=get_agent_file_for_role(role),
        model=model,
        isolation=isolation,
        background=background,
        dispatched_at=datetime.now(UTC).isoformat(),
        status="in_progress",
    )


def complete_subagent_dispatch_record(
    record: SubagentDispatchRecord,
    status: str,
    result: dict[str, Any] | None = None,
) -> SubagentDispatchRecord:
    """Return a new record with completion timestamp and final status."""
    return record.model_copy(
        update={
            "completed_at": datetime.now(UTC).isoformat(),
            "status": status,
            "result": result,
        },
    )


def persist_dispatch_state(
    plans_dir: Path,
    obpi_id: str,
    records: list[SubagentDispatchRecord],
) -> None:
    """Persist dispatch records into the active pipeline marker."""
    marker_path = plans_dir / f".pipeline-active-{obpi_id}.json"
    if not marker_path.is_file():
        return
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    marker["dispatch_state"] = [r.model_dump() for r in records]
    marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")


def load_dispatch_state(
    plans_dir: Path,
    obpi_id: str,
) -> list[SubagentDispatchRecord]:
    """Load dispatch records from the active pipeline marker."""
    marker_path = plans_dir / f".pipeline-active-{obpi_id}.json"
    if not marker_path.is_file():
        return []
    marker = json.loads(marker_path.read_text(encoding="utf-8"))
    raw_records = marker.get("dispatch_state", [])
    if not isinstance(raw_records, list):
        return []
    return [SubagentDispatchRecord(**r) for r in raw_records]


def aggregate_dispatch_results(
    records: list[SubagentDispatchRecord],
) -> DispatchAggregation:
    """Compute aggregation from a list of dispatch records."""
    done_statuses = {"done", "done_with_concerns"}
    completed = sum(1 for r in records if r.status in done_statuses)
    blocked = sum(1 for r in records if r.status == "blocked")

    # Count re-dispatches by looking for duplicate task_ids
    task_dispatch_counts: dict[int, int] = {}
    for r in records:
        task_dispatch_counts[r.task_id] = task_dispatch_counts.get(r.task_id, 0) + 1
    fix_cycles = sum(max(0, c - 1) for c in task_dispatch_counts.values())

    # Aggregate review findings by severity from result payloads
    severity_counts: dict[str, int] = {}
    for r in records:
        if r.result and "findings" in r.result:
            for finding in r.result["findings"]:
                sev = str(finding.get("severity", "info")).lower()
                severity_counts[sev] = severity_counts.get(sev, 0) + 1

    # Model usage per role
    model_usage: dict[str, dict[str, int]] = {}
    for r in records:
        role_usage = model_usage.setdefault(r.role, {})
        role_usage[r.model] = role_usage.get(r.model, 0) + 1

    return DispatchAggregation(
        total_tasks=len(records),
        completed=completed,
        blocked=blocked,
        fix_cycles=fix_cycles,
        review_findings_by_severity=severity_counts,
        model_usage_per_role=model_usage,
    )


def persist_dispatch_summary(
    plans_dir: Path,
    obpi_id: str,
    aggregation: DispatchAggregation,
    records: list[SubagentDispatchRecord],
) -> Path:
    """Write dispatch summary for historical queries after marker cleanup."""
    summary_path = plans_dir / f"{DISPATCH_SUMMARY_PREFIX}{obpi_id}.json"
    payload = {
        "obpi_id": obpi_id,
        "aggregation": aggregation.model_dump(),
        "records": [r.model_dump() for r in records],
    }
    summary_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return summary_path


def load_dispatch_summary(plans_dir: Path, obpi_id: str) -> dict[str, Any] | None:
    """Load persisted dispatch summary for historical queries."""
    summary_path = plans_dir / f"{DISPATCH_SUMMARY_PREFIX}{obpi_id}.json"
    if not summary_path.is_file():
        return None
    return cast(dict[str, Any], json.loads(summary_path.read_text(encoding="utf-8")))


def validate_agent_files(project_root: Path) -> list[str]:
    """Validate that all pipeline agent files exist with required frontmatter.

    Returns a list of validation error messages (empty = all valid).
    """
    errors: list[str] = []
    required_keys = {"name", "tools"}
    for role_name, rel_path in AGENT_FILE_MAP.items():
        if not rel_path:
            continue
        agent_path = project_root / rel_path
        if not agent_path.is_file():
            errors.append(f"{rel_path}: file not found (role: {role_name})")
            continue
        content = agent_path.read_text(encoding="utf-8")
        if not content.startswith("---"):
            errors.append(f"{rel_path}: missing YAML frontmatter (role: {role_name})")
            continue
        parts = content.split("---", 2)
        if len(parts) < 3:
            errors.append(f"{rel_path}: malformed frontmatter (role: {role_name})")
            continue
        frontmatter = parts[1]
        found_keys = set()
        for line in frontmatter.strip().splitlines():
            if ":" in line:
                key = line.split(":", 1)[0].strip()
                found_keys.add(key)
        missing = required_keys - found_keys
        if missing:
            errors.append(
                f"{rel_path}: missing frontmatter keys {sorted(missing)} (role: {role_name})"
            )
    return errors
