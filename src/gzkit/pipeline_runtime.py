"""Shared runtime helpers for the OBPI pipeline command and hook surfaces."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

PIPELINE_RECEIPT_FILE = ".plan-audit-receipt.json"
PIPELINE_LEGACY_MARKER = ".pipeline-active.json"


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


def load_plan_audit_receipt(
    plans_dir: Path,
    obpi_id: str,
) -> tuple[str, list[str], dict[str, Any] | None]:
    """Return receipt state plus non-fatal warnings."""
    receipt_path = plans_dir / PIPELINE_RECEIPT_FILE
    if not receipt_path.exists():
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
        return None
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
    if resume_point in {"verify", "ceremony"}:
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
