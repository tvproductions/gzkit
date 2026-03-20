"""Shared runtime helpers for the OBPI pipeline command and hook surfaces."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any, cast

from pydantic import BaseModel, ConfigDict, Field

from gzkit.roles import HandoffResult, HandoffStatus

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
