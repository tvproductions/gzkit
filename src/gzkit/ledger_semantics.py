"""OBPI semantics derivation from ledger events.

This module computes the derived runtime state for each OBPI from
the raw ledger event stream: completion status, anchor analysis,
attestation requirements, drift detection, and issue collection.
"""

from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Any

from gzkit.ledger_proof import normalize_req_proof_inputs, summarize_req_proof_inputs
from gzkit.utils import list_changed_files_between, resolve_git_head_commit


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
    without invalidating it -- eventual consistency across the ADR.
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

    # Files changed since this OBPI's anchor -- expected when later siblings
    # or ADR closeout committed on top.  The anchor is superseded, not stale.
    return "superseded", [], anchor_drift_files


def _git_sync_anchor_notes(git_sync_state: Any) -> list[str]:
    """Record git-sync facts from receipt capture time (informational, not blocking).

    The git state at receipt time is metadata about the receipt, not a defect.
    A dirty worktree or ahead/behind state at OBPI completion is normal during
    incremental development -- the ADR closeout anchor seals the final state.
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


def _withdrawn_obpi_semantics() -> dict[str, Any]:
    """Return canonical semantics for a withdrawn OBPI."""
    return {
        "runtime_state": "withdrawn",
        "proof_state": "missing",
        "attestation_requirement": "optional",
        "attestation_state": "not_required",
        "req_proof_state": "missing",
        "req_proof_inputs": [],
        "req_proof_summary": {"state": "missing", "present": 0, "total": 0},
        "completed": False,
        "ledger_completed": False,
        "evidence_ok": False,
        "reflection_issues": [],
        "anchor_state": "none",
        "anchor_commit": None,
        "current_head": None,
        "anchor_issues": [],
        "anchor_drift_files": [],
        "issues": [],
    }


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
    if info.get("withdrawn"):
        return _withdrawn_obpi_semantics()
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
    # Anchor issues are informational at OBPI level -- each OBPI has its own
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
