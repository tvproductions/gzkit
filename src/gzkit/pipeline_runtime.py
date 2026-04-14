"""Shared runtime helpers for the OBPI pipeline command and hook surfaces.

Subagent dispatch tracking and integration live here. Pipeline marker I/O,
task dispatch models, and verification dispatch are in dedicated modules;
all public symbols are re-exported below for backward compatibility.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.models.persona import load_persona

# ---------------------------------------------------------------------------
# Re-exports: pipeline_dispatch (task models, classification, review)
# ---------------------------------------------------------------------------
from gzkit.pipeline_dispatch import (
    DISPATCH_MODEL_MAP,
    MAX_BLOCKED_FIX_ATTEMPTS,
    MAX_NEEDS_CONTEXT_RETRIES,
    MAX_REVIEW_FIX_CYCLES,
    REVIEW_MODEL_MAP,
    DispatchRecord,
    DispatchState,
    DispatchTask,
    TaskComplexity,
    TaskStatus,
    advance_dispatch,
    classify_task_complexity,
    compose_implementer_prompt,
    compose_quality_review_prompt,
    compose_spec_review_prompt,
    create_dispatch_state,
    extract_plan_tasks,
    handle_review_cycle,
    handle_task_result,
    parse_handoff_result,
    parse_review_result,
    review_blocks_advancement,
    review_has_critical_findings,
    select_dispatch_model,
    select_review_model,
    should_dispatch_review,
)

# ---------------------------------------------------------------------------
# Re-exports: pipeline_markers (marker I/O, receipt loading, messages)
# ---------------------------------------------------------------------------
from gzkit.pipeline_markers import (
    PIPELINE_LEGACY_MARKER,
    PIPELINE_RECEIPT_FILE,
    STALE_MARKER_HOURS,
    check_adr_evaluation_verdict,
    clear_stale_pipeline_markers,
    completion_receipt_missing_message,
    extract_brief_status,
    find_active_pipeline_marker,
    find_obpi_brief,
    find_plan_for_obpi,
    find_stale_pipeline_markers,
    load_pipeline_json,
    load_plan_audit_receipt,
    marker_matches,
    pipeline_command,
    pipeline_completion_reminder_message,
    pipeline_concurrency_blockers,
    pipeline_gate_message,
    pipeline_git_sync_command,
    pipeline_marker_paths,
    pipeline_marker_payload,
    pipeline_plan_search_dirs,
    pipeline_plans_dir,
    pipeline_receipt_path,
    pipeline_resume_command,
    pipeline_router_message,
    pipeline_stage_labels,
    pipeline_stage_name,
    pipeline_stage_output,
    refresh_pipeline_markers,
    remove_pipeline_artifacts,
    remove_pipeline_markers,
    stale_pipeline_marker_message,
    validate_brief_for_pipeline,
    write_pipeline_markers,
)

# ---------------------------------------------------------------------------
# Re-exports: pipeline_verification (verification models, orchestration)
# ---------------------------------------------------------------------------
from gzkit.pipeline_verification import (
    MAX_VERIFICATION_FIX_CYCLES,
    VerificationOutcome,
    VerificationPlan,
    VerificationResult,
    VerificationScope,
    VerificationTimingMetrics,
    aggregate_verification_results,
    build_verification_plan,
    compose_verification_prompt,
    compute_path_overlap,
    compute_verification_timing,
    create_verification_dispatch_records,
    extract_verification_scopes,
    parse_verification_results,
    partition_independent_groups,
    prepare_stage3_verification,
    should_fallback_to_sequential,
)

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

ROLE_PERSONA_MAP: dict[str, str] = {
    "Implementer": "implementer",
    "Reviewer": "spec-reviewer",
    "QualityReviewer": "quality-reviewer",
    "Narrator": "narrator",
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
    persona_loaded: str | None = Field(None, description="Persona file stem loaded for dispatch")


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


def load_persona_for_dispatch(project_root: Path, role: str) -> str | None:
    """Load persona body text for a dispatch role.

    Maps the dispatch role name (e.g. ``"Implementer"``) to the persona file
    stem (e.g. ``"implementer"``) via :data:`ROLE_PERSONA_MAP` and delegates
    to :func:`gzkit.models.persona.load_persona`.

    Returns ``None`` when the role has no persona mapping or the persona file
    does not exist.  Raises ``ValueError`` when the persona file exists but
    has malformed YAML frontmatter — parse errors are defects, not graceful
    degradation cases.
    """
    persona_name = ROLE_PERSONA_MAP.get(role)
    if persona_name is None:
        return None
    return load_persona(project_root, persona_name)


def prepend_persona_to_prompt(persona_text: str | None, prompt: str) -> str:
    """Prepend a persona frame to a dispatch prompt.

    Returns *prompt* unchanged when *persona_text* is ``None`` or empty.
    When persona text is provided, it is placed before the task prompt with
    a horizontal-rule separator so the model receives the identity frame
    before the task instructions.
    """
    if not persona_text:
        return prompt
    return f"{persona_text}\n\n---\n\n{prompt}"


def create_subagent_dispatch_record(
    task_id: int,
    role: str,
    model: str,
    *,
    isolation: str = "inline",
    background: bool = False,
    persona_loaded: str | None = None,
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
        persona_loaded=persona_loaded,
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
    from typing import cast  # noqa: PLC0415

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


# ---------------------------------------------------------------------------
# Ensure __all__ covers every re-exported symbol for static analysis
# ---------------------------------------------------------------------------

__all__ = [
    # pipeline_markers
    "PIPELINE_LEGACY_MARKER",
    "PIPELINE_RECEIPT_FILE",
    "STALE_MARKER_HOURS",
    "check_adr_evaluation_verdict",
    "clear_stale_pipeline_markers",
    "completion_receipt_missing_message",
    "extract_brief_status",
    "find_active_pipeline_marker",
    "find_obpi_brief",
    "find_plan_for_obpi",
    "find_stale_pipeline_markers",
    "load_pipeline_json",
    "load_plan_audit_receipt",
    "marker_matches",
    "pipeline_command",
    "pipeline_completion_reminder_message",
    "pipeline_concurrency_blockers",
    "pipeline_gate_message",
    "pipeline_git_sync_command",
    "pipeline_marker_paths",
    "pipeline_marker_payload",
    "pipeline_plan_search_dirs",
    "pipeline_plans_dir",
    "pipeline_receipt_path",
    "pipeline_resume_command",
    "pipeline_router_message",
    "pipeline_stage_labels",
    "pipeline_stage_name",
    "pipeline_stage_output",
    "refresh_pipeline_markers",
    "remove_pipeline_artifacts",
    "remove_pipeline_markers",
    "stale_pipeline_marker_message",
    "validate_brief_for_pipeline",
    "write_pipeline_markers",
    # pipeline_dispatch
    "DISPATCH_MODEL_MAP",
    "MAX_BLOCKED_FIX_ATTEMPTS",
    "MAX_NEEDS_CONTEXT_RETRIES",
    "MAX_REVIEW_FIX_CYCLES",
    "REVIEW_MODEL_MAP",
    "DispatchRecord",
    "DispatchState",
    "DispatchTask",
    "TaskComplexity",
    "TaskStatus",
    "advance_dispatch",
    "classify_task_complexity",
    "compose_implementer_prompt",
    "compose_quality_review_prompt",
    "compose_spec_review_prompt",
    "create_dispatch_state",
    "extract_plan_tasks",
    "handle_review_cycle",
    "handle_task_result",
    "parse_handoff_result",
    "parse_review_result",
    "review_blocks_advancement",
    "review_has_critical_findings",
    "select_dispatch_model",
    "select_review_model",
    "should_dispatch_review",
    # pipeline_verification
    "MAX_VERIFICATION_FIX_CYCLES",
    "VerificationOutcome",
    "VerificationPlan",
    "VerificationResult",
    "VerificationScope",
    "VerificationTimingMetrics",
    "aggregate_verification_results",
    "build_verification_plan",
    "compose_verification_prompt",
    "compute_path_overlap",
    "compute_verification_timing",
    "create_verification_dispatch_records",
    "extract_verification_scopes",
    "parse_verification_results",
    "partition_independent_groups",
    "prepare_stage3_verification",
    "should_fallback_to_sequential",
    # local (subagent orchestration)
    "AGENT_FILE_MAP",
    "DISPATCH_SUMMARY_PREFIX",
    "DispatchAggregation",
    "ModelRoutingConfig",
    "PIPELINE_CONFIG_FILE",
    "ROLE_PERSONA_MAP",
    "SubagentDispatchRecord",
    "aggregate_dispatch_results",
    "complete_subagent_dispatch_record",
    "create_subagent_dispatch_record",
    "get_agent_file_for_role",
    "load_dispatch_state",
    "load_dispatch_summary",
    "load_model_routing_config",
    "load_persona_for_dispatch",
    "persist_dispatch_state",
    "persist_dispatch_summary",
    "prepend_persona_to_prompt",
    "validate_agent_files",
]
