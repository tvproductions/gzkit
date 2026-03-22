"""Ledger system for tracking governance events.

The ledger is an append-only JSONL file that records all governance events.
State is derived from the ledger, not stored separately.
"""

import json
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, ClassVar

from pydantic import BaseModel, ConfigDict, Field, model_serializer, model_validator

from gzkit.utils import list_changed_files_between, resolve_git_head_commit

LEDGER_SCHEMA = "gzkit.ledger.v1"


ATTESTATION_CANONICAL_TERMS: dict[str, str] = {
    "completed": "Completed",
    "partial": "Completed - Partial",
    "dropped": "Dropped",
}

OBPI_RUNTIME_STATES = {
    "pending",
    "in_progress",
    "completed",
    "attested_completed",
    "validated",
    "drift",
}
OBPI_COMPLETED_RUNTIME_STATES = {"completed", "attested_completed", "validated"}
OBPI_PROOF_STATES = {"missing", "partial", "recorded", "validated"}
OBPI_ATTESTATION_REQUIREMENTS = {"required", "optional"}
OBPI_ATTESTATION_STATES = {"not_required", "missing", "recorded"}
REQ_PROOF_INPUT_KINDS = {
    "command",
    "artifact",
    "brief_section",
    "attestation",
    "legacy_key_proof",
}
REQ_PROOF_INPUT_STATUSES = {"present", "missing"}


class LedgerEvent(BaseModel):
    """A governance event recorded in the ledger.

    All events have:
    - schema: Always "gzkit.ledger.v1"
    - event: Event type (e.g., "project_init", "adr_created")
    - id: Artifact identifier
    - ts: ISO 8601 UTC timestamp

    Event-specific fields are stored in extra and flattened during serialization.

    Use ``model_validate(data)`` to parse from a dict (replaces ``from_dict``).
    Use ``model_dump()`` to serialize (replaces ``to_dict``).
    """

    model_config = ConfigDict(extra="forbid")

    event: str
    id: str
    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    schema_: str = Field(default=LEDGER_SCHEMA)
    parent: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)

    _KNOWN_FIELDS: ClassVar[frozenset[str]] = frozenset({"schema", "event", "id", "ts", "parent"})

    @model_validator(mode="before")
    @classmethod
    def _collect_extra_fields(cls, data: Any) -> Any:
        """Map 'schema' key to 'schema_' and collect unknown keys into extra."""
        if not isinstance(data, dict):
            return data
        result = dict(data)
        # Map "schema" → "schema_" for Pydantic field name
        if "schema" in result and "schema_" not in result:
            result["schema_"] = result.pop("schema")
        # Collect unknown keys into extra
        extra_keys = set(result.keys()) - cls._KNOWN_FIELDS - {"schema_", "extra"}
        if extra_keys:
            existing_extra = result.get("extra", {})
            if not isinstance(existing_extra, dict):
                existing_extra = {}
            for key in extra_keys:
                existing_extra[key] = result.pop(key)
            result["extra"] = existing_extra
        return result

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        """Serialize with schema_→schema mapping and extra flattened into top level."""
        result: dict[str, Any] = {
            "schema": self.schema_,
            "event": self.event,
            "id": self.id,
            "ts": self.ts,
        }
        if self.parent:
            result["parent"] = self.parent
        if self.extra:
            result.update(self.extra)
        return result


# Event factory functions for type safety and documentation
def project_init_event(project_name: str, mode: str) -> LedgerEvent:
    """Create a project initialization event."""
    return LedgerEvent(
        event="project_init",
        id=project_name,
        extra={"mode": mode},
    )


def prd_created_event(prd_id: str) -> LedgerEvent:
    """Create a PRD created event."""
    return LedgerEvent(
        event="prd_created",
        id=prd_id,
    )


def constitution_created_event(constitution_id: str) -> LedgerEvent:
    """Create a constitution created event."""
    return LedgerEvent(
        event="constitution_created",
        id=constitution_id,
    )


def obpi_created_event(obpi_id: str, parent: str) -> LedgerEvent:
    """Create an OBPI created event."""
    return LedgerEvent(
        event="obpi_created",
        id=obpi_id,
        parent=parent,
    )


def adr_created_event(adr_id: str, parent: str, lane: str) -> LedgerEvent:
    """Create an ADR created event."""
    return LedgerEvent(
        event="adr_created",
        id=adr_id,
        parent=parent,
        extra={"lane": lane},
    )


def artifact_edited_event(path: str, session: str | None = None) -> LedgerEvent:
    """Create an artifact edited event (from hooks)."""
    extra: dict[str, Any] = {"path": path}
    if session:
        extra["session"] = session
    return LedgerEvent(
        event="artifact_edited",
        id=path,
        extra=extra,
    )


def attested_event(
    adr_id: str,
    status: str,
    by: str,
    reason: str | None = None,
) -> LedgerEvent:
    """Create an attestation event."""
    extra: dict[str, Any] = {"status": status, "by": by}
    if reason:
        extra["reason"] = reason
    return LedgerEvent(
        event="attested",
        id=adr_id,
        extra=extra,
    )


def gate_checked_event(
    adr_id: str,
    gate: int,
    status: str,
    command: str,
    returncode: int,
    evidence: str | None = None,
) -> LedgerEvent:
    """Create a gate checked event."""
    extra: dict[str, Any] = {
        "gate": gate,
        "status": status,
        "command": command,
        "returncode": returncode,
    }
    if evidence:
        extra["evidence"] = evidence
    return LedgerEvent(
        event="gate_checked",
        id=adr_id,
        extra=extra,
    )


def closeout_initiated_event(
    adr_id: str,
    by: str,
    mode: str,
    evidence: dict[str, Any] | None = None,
) -> LedgerEvent:
    """Create a closeout initiation event."""
    extra: dict[str, Any] = {"by": by, "mode": mode}
    if evidence is not None:
        extra["evidence"] = evidence
    return LedgerEvent(
        event="closeout_initiated",
        id=adr_id,
        extra=extra,
    )


def audit_generated_event(
    adr_id: str,
    audit_file: str,
    audit_plan_file: str,
    passed: bool,
) -> LedgerEvent:
    """Create an audit-generated event recording that audit artifacts were created."""
    return LedgerEvent(
        event="audit_generated",
        id=adr_id,
        extra={
            "audit_file": audit_file,
            "audit_plan_file": audit_plan_file,
            "passed": passed,
        },
    )


def audit_receipt_emitted_event(
    adr_id: str,
    receipt_event: str,
    attestor: str,
    evidence: dict[str, Any] | None = None,
    anchor: dict[str, str] | None = None,
) -> LedgerEvent:
    """Create an audit receipt event."""
    extra: dict[str, Any] = {"receipt_event": receipt_event, "attestor": attestor}
    if evidence is not None:
        extra["evidence"] = evidence
    if anchor is not None:
        extra["anchor"] = anchor
    return LedgerEvent(
        event="audit_receipt_emitted",
        id=adr_id,
        extra=extra,
    )


def obpi_receipt_emitted_event(
    obpi_id: str,
    receipt_event: str,
    attestor: str,
    evidence: dict[str, Any] | None = None,
    parent_adr: str | None = None,
    obpi_completion: str | None = None,
    anchor: dict[str, str] | None = None,
) -> LedgerEvent:
    """Create an OBPI receipt event."""
    extra: dict[str, Any] = {"receipt_event": receipt_event, "attestor": attestor}
    if evidence is not None:
        extra["evidence"] = evidence
    if obpi_completion is not None:
        extra["obpi_completion"] = obpi_completion
    if anchor is not None:
        extra["anchor"] = anchor
    return LedgerEvent(
        event="obpi_receipt_emitted",
        id=obpi_id,
        parent=parent_adr,
        extra=extra,
    )


def artifact_renamed_event(old_id: str, new_id: str, reason: str | None = None) -> LedgerEvent:
    """Create an artifact rename event used for ID migrations."""
    extra: dict[str, Any] = {"new_id": new_id}
    if reason:
        extra["reason"] = reason
    return LedgerEvent(
        event="artifact_renamed",
        id=old_id,
        extra=extra,
    )


def adr_eval_completed_event(
    adr_id: str,
    verdict: str,
    adr_weighted_total: float,
    obpi_count: int,
    action_item_count: int,
) -> LedgerEvent:
    """Create an ADR evaluation completed event."""
    return LedgerEvent(
        event="adr_eval_completed",
        id=adr_id,
        extra={
            "verdict": verdict,
            "adr_weighted_total": adr_weighted_total,
            "obpi_count": obpi_count,
            "action_item_count": action_item_count,
        },
    )


def lifecycle_transition_event(
    artifact_id: str,
    content_type: str,
    from_state: str,
    to_state: str,
) -> LedgerEvent:
    """Create a lifecycle state transition event."""
    return LedgerEvent(
        event="lifecycle_transition",
        id=artifact_id,
        extra={
            "content_type": content_type,
            "from_state": from_state,
            "to_state": to_state,
        },
    )


def parse_frontmatter_value(content: str, key: str) -> str | None:
    """Extract a single value from YAML frontmatter."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        raw_key, _, raw_value = line.partition(":")
        if raw_key.strip() != key:
            continue
        return raw_value.strip().strip("\"'")
    return None


def resolve_adr_lane(info: dict[str, Any], default_mode: str) -> str:
    """Resolve lane from ADR metadata with mode fallback."""
    lane = str(info.get("lane") or default_mode).lower()
    return lane if lane in {"lite", "heavy"} else default_mode


def _normalize_req_proof_input_item(item: Any) -> dict[str, str] | None:
    """Validate and normalize one REQ-proof input row."""
    if not isinstance(item, dict):
        return None

    name = item.get("name")
    kind = item.get("kind")
    source = item.get("source")
    status = item.get("status", "present")
    if not isinstance(name, str) or not name.strip():
        return None
    if not isinstance(kind, str) or kind not in REQ_PROOF_INPUT_KINDS:
        return None
    if not isinstance(source, str) or not source.strip():
        return None
    if not isinstance(status, str) or status not in REQ_PROOF_INPUT_STATUSES:
        return None

    entry = {
        "name": name.strip(),
        "kind": kind,
        "source": source.strip(),
        "status": status,
    }
    for optional_field in ("scope", "gap_reason"):
        optional_value = item.get(optional_field)
        if isinstance(optional_value, str) and optional_value.strip():
            entry[optional_field] = optional_value.strip()
    return entry


def _fallback_req_proof_inputs(
    fallback_key_proof: str | None,
    human_attestation: dict[str, Any] | None,
) -> list[dict[str, str]]:
    """Build compatibility proof inputs when structured evidence is absent."""
    normalized: list[dict[str, str]] = []
    if isinstance(fallback_key_proof, str) and fallback_key_proof.strip():
        normalized.append(
            {
                "name": "key_proof",
                "kind": "legacy_key_proof",
                "source": fallback_key_proof.strip(),
                "status": "present",
            }
        )
    if human_attestation and human_attestation.get("valid"):
        attestor = human_attestation.get("attestor", "human")
        attestation_date = human_attestation.get("date", "unknown-date")
        normalized.append(
            {
                "name": "human_attestation",
                "kind": "attestation",
                "source": f"{attestor} @ {attestation_date}",
                "status": "present",
            }
        )
    return normalized


def normalize_req_proof_inputs(
    raw_inputs: Any,
    *,
    fallback_key_proof: str | None = None,
    human_attestation: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    """Normalize REQ-proof inputs into a stable machine-readable list."""
    if isinstance(raw_inputs, list):
        normalized = [
            entry
            for item in raw_inputs
            if (entry := _normalize_req_proof_input_item(item)) is not None
        ]
        if normalized:
            return normalized

    return _fallback_req_proof_inputs(fallback_key_proof, human_attestation)


def summarize_req_proof_inputs(inputs: list[dict[str, str]]) -> dict[str, int | str]:
    """Summarize normalized REQ-proof input state."""
    total = len(inputs)
    present = sum(1 for item in inputs if item.get("status") == "present")
    missing = total - present

    if total == 0:
        state = "missing"
    elif missing == 0:
        state = "recorded"
    elif present == 0:
        state = "missing"
    else:
        state = "partial"

    return {
        "total": total,
        "present": present,
        "missing": missing,
        "state": state,
    }


def _resolve_attestation_requirement(evidence: dict[str, Any], obpi_completion: Any) -> str:
    """Resolve whether explicit human attestation evidence is required."""
    requirement = evidence.get("attestation_requirement")
    if isinstance(requirement, str):
        return requirement
    return "required" if obpi_completion == "attested_completed" else "optional"


def _has_substantive_evidence_text(value: Any) -> bool:
    """Return whether receipt evidence contains a substantive text payload."""
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower()
    return normalized not in {"", "-", "...", "tbd", "(none)", "n/a", "paste test output here"}


def _human_attestation_is_valid(evidence: dict[str, Any]) -> bool:
    """Return True when receipt evidence includes usable human attestation proof."""
    if evidence.get("human_attestation") is not True:
        return False
    attestation_text = evidence.get("attestation_text")
    attestation_date = evidence.get("attestation_date")
    return (
        isinstance(attestation_text, str)
        and bool(attestation_text.strip())
        and isinstance(attestation_date, str)
        and bool(attestation_date.strip())
    )


def _normalize_anchor(anchor: Any) -> dict[str, str] | None:
    """Normalize a stored anchor payload to a string-only mapping."""
    if not isinstance(anchor, dict):
        return None

    normalized: dict[str, str] = {}
    for key in ("commit", "semver", "tag"):
        value = anchor.get(key)
        if isinstance(value, str) and value.strip():
            normalized[key] = value.strip()
    return normalized or None


def _normalize_scope_audit(evidence: dict[str, Any]) -> dict[str, list[str]]:
    """Normalize optional scope-audit evidence into stable string lists."""
    scope_audit = evidence.get("scope_audit")
    if not isinstance(scope_audit, dict):
        return {"allowlist": [], "changed_files": [], "out_of_scope_files": []}

    normalized: dict[str, list[str]] = {}
    for key in ("allowlist", "changed_files", "out_of_scope_files"):
        value = scope_audit.get(key)
        if isinstance(value, list):
            normalized[key] = [
                str(item).replace("\\", "/").strip()
                for item in value
                if isinstance(item, str) and item.strip()
            ]
        else:
            normalized[key] = []
    return normalized


def _path_matches_scope_allowlist(path: str, allowlist: list[str]) -> bool:
    """Return True when a changed path intersects the recorded allowlist."""
    normalized_path = path.replace("\\", "/").strip()
    if not normalized_path:
        return False

    path_obj = PurePosixPath(normalized_path)
    for raw_pattern in allowlist:
        pattern = raw_pattern.replace("\\", "/").strip()
        if not pattern:
            continue
        if any(token in pattern for token in ("*", "?", "[")) and path_obj.match(pattern):
            return True
        if normalized_path == pattern or normalized_path.startswith(f"{pattern.rstrip('/')}/"):
            return True
    return False


def _is_transient_anchor_state_path(path: str) -> bool:
    """Return True when a path is runtime state, not durable governed scope."""
    normalized_path = path.replace("\\", "/").strip()
    return normalized_path == ".claude/hooks/.instruction-state.json"


def _relevant_anchor_drift_files(
    files_since_anchor: list[str] | None,
    scope_audit: dict[str, list[str]],
) -> list[str]:
    """Filter changed files since anchor down to the OBPI-recorded scope."""
    if not files_since_anchor:
        return []

    changed_files = set(scope_audit["changed_files"])
    allowlist = scope_audit["allowlist"]
    relevant = [
        path
        for path in files_since_anchor
        if not _is_transient_anchor_state_path(path)
        and (path in changed_files or _path_matches_scope_allowlist(path, allowlist))
    ]
    return sorted(set(relevant))


def _parse_event_timestamp(value: Any) -> datetime | None:
    """Parse an event timestamp into a comparable UTC-aware datetime."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _anchor_result(
    *,
    anchor_state: str,
    anchor_commit: str | None,
    current_head: str | None,
    anchor_issues: list[str] | None = None,
    anchor_drift_files: list[str] | None = None,
) -> dict[str, Any]:
    """Build a stable anchor-analysis payload."""
    return {
        "anchor_state": anchor_state,
        "anchor_commit": anchor_commit,
        "current_head": current_head,
        "anchor_issues": list(anchor_issues or []),
        "anchor_drift_files": list(anchor_drift_files or []),
    }


def _completion_anchor_required(
    completion_evidence: dict[str, Any],
    scope_audit: dict[str, list[str]],
    git_sync_state: Any,
) -> bool:
    """Return True when completion receipts should participate in anchor reconciliation."""
    return bool(
        scope_audit["allowlist"]
        or scope_audit["changed_files"]
        or isinstance(git_sync_state, dict)
        or any(key in completion_evidence for key in ("recorder_source", "recorder_warnings"))
    )


def _resolve_current_head(project_root: Path | None, current_head: str | None) -> str | None:
    """Resolve current HEAD lazily when needed."""
    if current_head is not None or project_root is None:
        return current_head
    return resolve_git_head_commit(project_root)


def _derive_scope_anchor_state(
    *,
    project_root: Path | None,
    current_head: str,
    anchor_commit: str,
    scope_audit: dict[str, list[str]],
    files_since_anchor: list[str] | None,
) -> tuple[str, list[str], list[str]]:
    """Evaluate OBPI completion anchor against current HEAD.

    Each OBPI's anchor commit seals that increment's delivery proof.
    Later commits (sibling OBPIs, ADR closeout) supersede the anchor
    without invalidating it — eventual consistency across the ADR.
    """
    if current_head == anchor_commit:
        return "current", [], []

    if files_since_anchor is None and project_root is not None:
        files_since_anchor = list_changed_files_between(project_root, anchor_commit)
    if files_since_anchor is None:
        return "degraded", ["changes since the completion anchor could not be inspected"], []

    anchor_drift_files = _relevant_anchor_drift_files(files_since_anchor, scope_audit)
    if not anchor_drift_files:
        return "scope_clean", [], []

    # Files changed since this OBPI's anchor — expected when later siblings
    # or ADR closeout committed on top.  The anchor is superseded, not stale.
    return "superseded", [], anchor_drift_files


def _git_sync_anchor_notes(git_sync_state: Any) -> list[str]:
    """Record git-sync facts from receipt capture time (informational, not blocking).

    The git state at receipt time is metadata about the receipt, not a defect.
    A dirty worktree or ahead/behind state at OBPI completion is normal during
    incremental development — the ADR closeout anchor seals the final state.
    """
    if not isinstance(git_sync_state, dict):
        return []

    notes: list[str] = []
    blockers = [
        str(item).strip()
        for item in git_sync_state.get("blockers", [])
        if isinstance(item, str) and item.strip()
    ]
    if blockers:
        notes.append("completion git-sync evidence recorded blockers: " + "; ".join(blockers))

    if git_sync_state.get("dirty") is True:
        notes.append("completion receipt was captured from a dirty worktree")
    if git_sync_state.get("diverged") is True:
        notes.append("completion receipt was captured while git state was diverged")
    elif int(git_sync_state.get("ahead", 0) or 0) > 0:
        notes.append("completion receipt was captured while branch was ahead of remote")
    elif int(git_sync_state.get("behind", 0) or 0) > 0:
        notes.append("completion receipt was captured while branch was behind remote")
    return notes


def _derive_anchor_analysis(
    info: dict[str, Any],
    *,
    obpi_id: str | None,
    artifact_graph: dict[str, dict[str, Any]] | None,
    ledger_completed: bool,
    project_root: Path | None,
    current_head: str | None,
    files_since_anchor: list[str] | None,
) -> dict[str, Any]:
    """Derive anchor-aware drift state from completed-receipt evidence."""
    completion_evidence = info.get("latest_completion_evidence")
    if not isinstance(completion_evidence, dict):
        completion_evidence = {}

    scope_audit = _normalize_scope_audit(completion_evidence)
    git_sync_state = completion_evidence.get("git_sync_state")
    anchor_required = _completion_anchor_required(completion_evidence, scope_audit, git_sync_state)

    normalized_anchor = _normalize_anchor(info.get("latest_completion_anchor"))
    anchor_commit = normalized_anchor.get("commit") if normalized_anchor else None
    current_head = _resolve_current_head(project_root, current_head)

    if not ledger_completed:
        return _anchor_result(
            anchor_state="not_applicable",
            anchor_commit=anchor_commit,
            current_head=current_head,
        )

    if not anchor_required:
        return _anchor_result(
            anchor_state="not_tracked",
            anchor_commit=anchor_commit,
            current_head=current_head,
        )

    if not normalized_anchor or not anchor_commit:
        return _anchor_result(
            anchor_state="missing",
            anchor_commit=None,
            current_head=current_head,
            anchor_issues=["completion anchor evidence is missing"],
        )

    if current_head is None:
        return _anchor_result(
            anchor_state="degraded",
            anchor_commit=anchor_commit,
            current_head=None,
            anchor_issues=["current HEAD could not be resolved for anchor reconciliation"],
        )

    anchor_state, anchor_issues, anchor_drift_files = _derive_scope_anchor_state(
        project_root=project_root,
        current_head=current_head,
        anchor_commit=anchor_commit,
        scope_audit=scope_audit,
        files_since_anchor=files_since_anchor,
    )
    git_sync_notes = _git_sync_anchor_notes(git_sync_state)
    return _anchor_result(
        anchor_state=anchor_state,
        anchor_commit=anchor_commit,
        current_head=current_head,
        anchor_issues=[*anchor_issues, *git_sync_notes],
        anchor_drift_files=anchor_drift_files,
    )


def _derive_obpi_issues(
    *,
    ledger_completed: bool,
    latest_receipt_event: Any,
    implementation_evidence_ok: bool,
    key_proof_ok: bool,
    attestation_requirement: str,
    human_attestation_ok: bool,
) -> list[str]:
    """Collect canonical fail-closed OBPI runtime issues from ledger truth."""
    issues: list[str] = []
    if not ledger_completed:
        issues.append("ledger proof of completion is missing")
    if latest_receipt_event == "validated" and not ledger_completed:
        issues.append("validated receipt exists without completed proof state")
    if ledger_completed and not implementation_evidence_ok:
        issues.append("completed receipt evidence is missing value narrative")
    if ledger_completed and not key_proof_ok:
        issues.append("completed receipt evidence is missing key proof")
    if attestation_requirement == "required" and ledger_completed and not human_attestation_ok:
        issues.append("required human attestation evidence is missing")
    return issues


def _derive_obpi_reflection_issues(
    *,
    ledger_completed: bool,
    file_completed: bool,
    found_file: bool,
    latest_receipt_event: Any,
    file_implementation_evidence_ok: bool,
    file_key_proof_ok: bool,
    attestation_requirement: str,
    file_human_attestation_ok: bool,
) -> list[str]:
    """Collect markdown-reflection drift that should not redefine ledger truth."""
    issues: list[str] = []
    if latest_receipt_event and not found_file:
        issues.append("OBPI brief file is missing; markdown reflection is out of sync with ledger")
    if not ledger_completed and file_completed:
        issues.append("brief reflection says Completed without ledger completion proof")
    if ledger_completed and found_file and not file_completed:
        issues.append("brief reflection is not marked Completed")
    if ledger_completed and found_file and not file_implementation_evidence_ok:
        issues.append("brief implementation summary is missing or placeholder")
    if ledger_completed and found_file and not file_key_proof_ok:
        issues.append("brief key proof is missing or placeholder")
    if (
        attestation_requirement == "required"
        and ledger_completed
        and found_file
        and not file_human_attestation_ok
    ):
        issues.append("brief human attestation section is missing or incomplete")
    return issues


def _derive_attestation_state(
    attestation_requirement: str,
    human_attestation_ok: bool,
) -> str:
    """Resolve the derived attestation state label."""
    if attestation_requirement == "required":
        return "recorded" if human_attestation_ok else "missing"
    return "not_required"


def _derive_obpi_runtime_state(
    *,
    issues: list[str],
    anchor_issues: list[str],
    ledger_completed: bool,
    validated: bool,
    evidence_ok: bool,
    attestation_state: str,
    obpi_completion: Any,
    latest_receipt_event: Any,
    implementation_evidence_ok: bool,
    key_proof_ok: bool,
    req_proof_present: int,
) -> str:
    """Resolve the OBPI runtime state from normalized evidence."""
    non_anchor_issues = list(issues)
    for anchor_issue in anchor_issues:
        try:
            non_anchor_issues.remove(anchor_issue)
        except ValueError:
            continue

    if non_anchor_issues and ledger_completed:
        return "drift"
    if validated and ledger_completed and evidence_ok and attestation_state != "missing":
        return "validated"
    if obpi_completion == "attested_completed" and evidence_ok and attestation_state == "recorded":
        return "attested_completed"
    if obpi_completion == "completed" and evidence_ok:
        return "completed"
    if any([latest_receipt_event, implementation_evidence_ok, key_proof_ok, req_proof_present]):
        return "in_progress"
    return "pending"


def derive_obpi_semantics(
    info: dict[str, Any],
    *,
    obpi_id: str | None = None,
    artifact_graph: dict[str, dict[str, Any]] | None = None,
    found_file: bool,
    file_completed: bool,
    implementation_evidence_ok: bool,
    key_proof_ok: bool,
    fallback_key_proof: str | None = None,
    human_attestation: dict[str, Any] | None = None,
    project_root: Path | None = None,
    current_head: str | None = None,
    files_since_anchor: list[str] | None = None,
) -> dict[str, Any]:
    """Derive shared OBPI runtime semantics from ledger and brief evidence."""
    latest_receipt_event = info.get("latest_receipt_event")
    obpi_completion = info.get("obpi_completion")
    ledger_completed = bool(info.get("ledger_completed"))
    validated = bool(info.get("validated"))

    evidence = info.get("latest_evidence")
    if not isinstance(evidence, dict):
        evidence = {}

    attestation_requirement = _resolve_attestation_requirement(evidence, obpi_completion)

    req_proof_inputs = normalize_req_proof_inputs(
        evidence.get("req_proof_inputs"),
        fallback_key_proof=(
            evidence.get("key_proof")
            if _has_substantive_evidence_text(evidence.get("key_proof"))
            else None
        ),
    )
    req_proof_summary = summarize_req_proof_inputs(req_proof_inputs)
    req_proof_state = str(req_proof_summary["state"])

    file_human_attestation_ok = bool(human_attestation and human_attestation.get("valid"))
    human_attestation_ok = _human_attestation_is_valid(evidence)
    attestation_state = _derive_attestation_state(attestation_requirement, human_attestation_ok)

    canonical_implementation_evidence_ok = _has_substantive_evidence_text(
        evidence.get("value_narrative")
    )
    canonical_key_proof_ok = (
        _has_substantive_evidence_text(evidence.get("key_proof"))
        or int(req_proof_summary["present"]) > 0
    )
    evidence_ok = canonical_implementation_evidence_ok and canonical_key_proof_ok
    anchor_analysis = _derive_anchor_analysis(
        info,
        obpi_id=obpi_id,
        artifact_graph=artifact_graph,
        ledger_completed=ledger_completed,
        project_root=project_root,
        current_head=current_head,
        files_since_anchor=files_since_anchor,
    )

    issues = _derive_obpi_issues(
        ledger_completed=ledger_completed,
        latest_receipt_event=latest_receipt_event,
        implementation_evidence_ok=canonical_implementation_evidence_ok,
        key_proof_ok=canonical_key_proof_ok,
        attestation_requirement=attestation_requirement,
        human_attestation_ok=human_attestation_ok,
    )
    reflection_issues = _derive_obpi_reflection_issues(
        ledger_completed=ledger_completed,
        file_completed=file_completed,
        found_file=found_file,
        latest_receipt_event=latest_receipt_event,
        file_implementation_evidence_ok=implementation_evidence_ok,
        file_key_proof_ok=key_proof_ok,
        attestation_requirement=attestation_requirement,
        file_human_attestation_ok=file_human_attestation_ok,
    )

    runtime_state = _derive_obpi_runtime_state(
        issues=issues,
        anchor_issues=list(anchor_analysis["anchor_issues"]),
        ledger_completed=ledger_completed,
        validated=validated,
        evidence_ok=evidence_ok,
        attestation_state=attestation_state,
        obpi_completion=obpi_completion,
        latest_receipt_event=latest_receipt_event,
        implementation_evidence_ok=canonical_implementation_evidence_ok,
        key_proof_ok=canonical_key_proof_ok,
        req_proof_present=int(req_proof_summary["present"]),
    )

    proof_state = "validated" if runtime_state == "validated" else req_proof_state
    # Anchor issues are informational at OBPI level — each OBPI has its own
    # commit anchor and later sibling/ADR work will naturally drift it.
    # Blocking validation belongs at ADR closeout, not per-OBPI audit.
    reflection_issues = [*reflection_issues, *list(anchor_analysis["anchor_issues"])]

    completed = bool(ledger_completed and evidence_ok and attestation_state != "missing")
    return {
        "runtime_state": runtime_state,
        "proof_state": proof_state,
        "attestation_requirement": attestation_requirement,
        "attestation_state": attestation_state,
        "req_proof_state": req_proof_state,
        "req_proof_inputs": req_proof_inputs,
        "req_proof_summary": req_proof_summary,
        "completed": completed,
        "ledger_completed": ledger_completed,
        "evidence_ok": evidence_ok,
        "reflection_issues": reflection_issues,
        "anchor_state": anchor_analysis["anchor_state"],
        "anchor_commit": anchor_analysis["anchor_commit"],
        "current_head": anchor_analysis["current_head"],
        "anchor_issues": list(anchor_analysis["anchor_issues"]),
        "anchor_drift_files": list(anchor_analysis["anchor_drift_files"]),
        "issues": issues,
    }


class Ledger:
    """Append-only ledger for governance events.

    The ledger is stored as JSONL (JSON Lines) format - one JSON object per line.
    This enables append-only writes and streaming reads.
    """

    def __init__(self, path: Path):
        """Initialize ledger at the given path.

        Args:
            path: Path to the ledger.jsonl file.

        """
        self.path = path

    def exists(self) -> bool:
        """Check if the ledger file exists."""
        return self.path.exists()

    def create(self) -> None:
        """Create an empty ledger file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.touch()

    def append(self, event: LedgerEvent) -> None:
        """Append an event to the ledger.

        Args:
            event: The event to append.

        """
        if not self.path.exists():
            self.create()

        with open(self.path, "a") as f:
            json.dump(event.model_dump(), f, separators=(",", ":"))
            f.write("\n")

    def read_all(self) -> list[LedgerEvent]:
        """Read all events from the ledger.

        Returns:
            List of all events in chronological order.

        """
        if not self.path.exists():
            return []

        events = []
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    events.append(LedgerEvent.model_validate(data))

        return events

    def query(
        self,
        event_type: str | None = None,
        artifact_id: str | None = None,
    ) -> list[LedgerEvent]:
        """Query events by type and/or artifact ID.

        Args:
            event_type: Filter by event type (e.g., "adr_created").
            artifact_id: Filter by artifact ID.

        Returns:
            Filtered list of events.

        """
        events = self.read_all()

        if event_type:
            events = [e for e in events if e.event == event_type]

        if artifact_id:
            events = [e for e in events if e.id == artifact_id]

        return events

    def latest_event(self, artifact_id: str) -> LedgerEvent | None:
        """Get the most recent event for an artifact.

        Args:
            artifact_id: The artifact ID to query.

        Returns:
            Most recent event or None if not found.

        """
        events = self.query(artifact_id=artifact_id)
        return events[-1] if events else None

    @staticmethod
    def _build_rename_map(events: list[LedgerEvent]) -> dict[str, str]:
        """Build old->new artifact ID mapping from rename events."""
        rename_map: dict[str, str] = {}
        for event in events:
            if event.event != "artifact_renamed":
                continue
            new_id = event.extra.get("new_id")
            if isinstance(new_id, str) and new_id and new_id != event.id:
                rename_map[event.id] = new_id
        return rename_map

    @staticmethod
    def _canonicalize_with_map(artifact_id: str, rename_map: dict[str, str]) -> str:
        """Resolve an artifact ID through any rename chain."""
        current = artifact_id
        seen: set[str] = set()
        while current in rename_map and current not in seen:
            seen.add(current)
            current = rename_map[current]
        return current

    def canonicalize_id(self, artifact_id: str) -> str:
        """Resolve an artifact ID to the latest canonical identifier."""
        events = self.read_all()
        rename_map = self._build_rename_map(events)
        return self._canonicalize_with_map(artifact_id, rename_map)

    def get_latest_gate_statuses(self, adr_id: str) -> dict[int, str]:
        """Get the latest recorded gate status for an ADR.

        For each gate number, the most recent `gate_checked` event wins.

        Args:
            adr_id: ADR identifier.

        Returns:
            Mapping of gate number to latest status ("pass"/"fail").

        """
        latest: dict[int, str] = {}
        events = self.read_all()
        rename_map = self._build_rename_map(events)
        target_id = self._canonicalize_with_map(adr_id, rename_map)

        for event in events:
            if event.event != "gate_checked":
                continue
            if self._canonicalize_with_map(event.id, rename_map) != target_id:
                continue

            gate_value = event.extra.get("gate")
            status = event.extra.get("status")

            gate: int | None = None
            if isinstance(gate_value, int):
                gate = gate_value
            elif isinstance(gate_value, str) and gate_value.isdigit():
                gate = int(gate_value)

            if gate is None or not isinstance(status, str):
                continue

            latest[gate] = status

        return latest

    @staticmethod
    def _artifact_creation_entry(
        event: LedgerEvent,
        canonical_parent: str | None,
    ) -> dict[str, Any]:
        """Create the initial graph entry for an artifact creation event."""
        entry: dict[str, Any] = {
            "type": event.event.replace("_created", ""),
            "created": event.ts,
            "parent": canonical_parent,
            "children": [],
            "attested": False,
        }
        if event.event == "obpi_created":
            entry["latest_receipt_event"] = None
            entry["latest_evidence"] = None
            entry["latest_completion_evidence"] = None
            entry["latest_completion_anchor"] = None
            entry["latest_completion_ts"] = None
            entry["validated"] = False
            entry["ledger_completed"] = False
        if event.event == "adr_created":
            entry["lane"] = event.extra.get("lane")
            entry["closeout_initiated"] = False
            entry["closeout_by"] = None
            entry["closeout_mode"] = None
            entry["closeout_evidence"] = None
            entry["latest_receipt_event"] = None
            entry["validated"] = False
        return entry

    @classmethod
    def _ensure_artifact_entry(
        cls,
        graph: dict[str, dict[str, Any]],
        event: LedgerEvent,
        canonical_id: str,
        canonical_parent: str | None,
    ) -> None:
        """Create graph node on first creation event for an artifact."""
        creation_events = {
            "prd_created",
            "constitution_created",
            "obpi_created",
            "adr_created",
        }
        if event.event not in creation_events or canonical_id in graph:
            return
        graph[canonical_id] = cls._artifact_creation_entry(event, canonical_parent)

    @staticmethod
    def _record_parent_child_relationship(
        graph: dict[str, dict[str, Any]],
        canonical_parent: str | None,
        canonical_id: str,
    ) -> None:
        """Attach child to parent node if both are represented in the graph."""
        if not canonical_parent or canonical_parent not in graph:
            return
        children = graph[canonical_parent]["children"]
        if canonical_id not in children:
            children.append(canonical_id)

    @staticmethod
    def _apply_adr_created_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "adr_created" or canonical_id not in graph:
            return
        graph[canonical_id]["lane"] = event.extra.get("lane", graph[canonical_id].get("lane"))

    @staticmethod
    def _apply_attestation_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "attested" or canonical_id not in graph:
            return
        graph[canonical_id]["attested"] = True
        graph[canonical_id]["attestation_status"] = event.extra.get("status")
        graph[canonical_id]["attestation_by"] = event.extra.get("by")

    @staticmethod
    def _apply_closeout_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "closeout_initiated" or canonical_id not in graph:
            return
        graph[canonical_id]["closeout_initiated"] = True
        graph[canonical_id]["closeout_by"] = event.extra.get("by")
        graph[canonical_id]["closeout_mode"] = event.extra.get("mode")
        graph[canonical_id]["closeout_evidence"] = event.extra.get("evidence")

    @staticmethod
    def _apply_audit_receipt_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "audit_receipt_emitted" or canonical_id not in graph:
            return
        receipt_event = event.extra.get("receipt_event")
        graph[canonical_id]["latest_receipt_event"] = receipt_event
        evidence = event.extra.get("evidence")
        adr_completion = evidence.get("adr_completion") if isinstance(evidence, dict) else None
        if receipt_event == "validated" and adr_completion != "not_completed":
            graph[canonical_id]["validated"] = True

    @staticmethod
    def _apply_obpi_receipt_metadata(
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        if event.event != "obpi_receipt_emitted" or canonical_id not in graph:
            return
        if graph[canonical_id].get("type") != "obpi":
            return
        receipt_event = event.extra.get("receipt_event")
        graph[canonical_id]["latest_receipt_event"] = receipt_event
        evidence = event.extra.get("evidence")
        if isinstance(evidence, dict):
            graph[canonical_id]["latest_evidence"] = dict(evidence)
        if receipt_event == "completed":
            graph[canonical_id]["latest_completion_evidence"] = dict(evidence or {})
            graph[canonical_id]["latest_completion_anchor"] = _normalize_anchor(
                event.extra.get("anchor")
            )
            graph[canonical_id]["latest_completion_ts"] = event.ts

        obpi_completion = event.extra.get("obpi_completion")
        if obpi_completion:
            graph[canonical_id]["obpi_completion"] = obpi_completion
            if obpi_completion in {"completed", "attested_completed"}:
                graph[canonical_id]["ledger_completed"] = True

        if receipt_event == "validated":
            graph[canonical_id]["validated"] = True

    @classmethod
    def _apply_graph_event_metadata(
        cls,
        graph: dict[str, dict[str, Any]],
        canonical_id: str,
        event: LedgerEvent,
    ) -> None:
        """Apply non-creation metadata for a ledger event."""
        cls._apply_adr_created_metadata(graph, canonical_id, event)
        cls._apply_attestation_metadata(graph, canonical_id, event)
        cls._apply_closeout_metadata(graph, canonical_id, event)
        cls._apply_audit_receipt_metadata(graph, canonical_id, event)
        cls._apply_obpi_receipt_metadata(graph, canonical_id, event)

    def get_artifact_graph(self) -> dict[str, dict[str, Any]]:
        """Build a graph of artifacts and their relationships.

        Returns:
            Dictionary mapping artifact IDs to their info and relationships.

        """
        graph: dict[str, dict[str, Any]] = {}
        events = self.read_all()
        rename_map = self._build_rename_map(events)

        for event in events:
            canonical_id = self._canonicalize_with_map(event.id, rename_map)
            canonical_parent = (
                self._canonicalize_with_map(event.parent, rename_map) if event.parent else None
            )

            self._ensure_artifact_entry(graph, event, canonical_id, canonical_parent)
            self._record_parent_child_relationship(graph, canonical_parent, canonical_id)
            self._apply_graph_event_metadata(graph, canonical_id, event)

        return graph

    def get_pending_attestations(self) -> list[str]:
        """Get artifact IDs that need attestation.

        Returns:
            List of artifact IDs without attestation events.

        """
        graph = self.get_artifact_graph()
        return [
            artifact_id
            for artifact_id, info in graph.items()
            if info["type"] == "adr" and not info["attested"]
        ]

    @staticmethod
    def canonical_attestation_term(status: str | None) -> str | None:
        """Map internal attestation token to canonical display term."""
        if status is None:
            return None
        return ATTESTATION_CANONICAL_TERMS.get(status, status)

    @classmethod
    def derive_adr_semantics(cls, info: dict[str, Any]) -> dict[str, Any]:
        """Derive canonical lifecycle and closeout-phase semantics for ADR status surfaces."""
        attestation_status = info.get("attestation_status")
        validated = bool(info.get("validated"))
        closeout_initiated = bool(info.get("closeout_initiated"))

        if validated:
            lifecycle_status = "Validated"
            closeout_phase = "validated"
        elif attestation_status == "dropped":
            lifecycle_status = "Abandoned"
            closeout_phase = "attested"
        elif attestation_status in {"completed", "partial"}:
            lifecycle_status = "Completed"
            closeout_phase = "attested"
        elif closeout_initiated:
            lifecycle_status = "Pending"
            closeout_phase = "closeout_initiated"
        else:
            lifecycle_status = "Pending"
            closeout_phase = "pre_closeout"

        return {
            "lifecycle_status": lifecycle_status,
            "closeout_phase": closeout_phase,
            "attestation_term": cls.canonical_attestation_term(
                attestation_status if isinstance(attestation_status, str) else None
            ),
        }
