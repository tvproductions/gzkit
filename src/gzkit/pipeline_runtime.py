"""Shared helpers for the OBPI pipeline runtime contract."""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent
from typing import Any, cast

from gzkit.decomposition import extract_markdown_section

PIPELINE_RECEIPT_FILE = ".plan-audit-receipt.json"
PIPELINE_LEGACY_MARKER = ".pipeline-active.json"
PIPELINE_ALIAS = "/gz-obpi-pipeline"


def pipeline_runtime_command(obpi_id: str, *, start_from: str | None = None) -> str:
    """Return the canonical pipeline command for one OBPI."""
    command = f"uv run gz obpi pipeline {obpi_id}"
    if start_from:
        return f"{command} --from={start_from}"
    return command


def pipeline_skill_command(obpi_id: str, *, start_from: str | None = None) -> str:
    """Return the thin skill alias for the canonical pipeline command."""
    command = f"{PIPELINE_ALIAS} {obpi_id}"
    if start_from:
        return f"{command} --from={start_from}"
    return command


def pipeline_router_message(obpi_id: str) -> str:
    """Return the canonical plan-approved routing message."""
    return dedent(
        f"""\
        OBPI plan approved: {obpi_id}

        REQUIRED: Start the canonical governance runtime:
          {pipeline_runtime_command(obpi_id)}

        Thin alias available for agent UX:
          {pipeline_skill_command(obpi_id)}

        Do NOT implement directly; the runtime preserves verification, evidence,
        guarded sync, and completion-accounting order.

        If implementation is already done, resume with:
          {pipeline_runtime_command(obpi_id, start_from="verify")}
          {pipeline_runtime_command(obpi_id, start_from="ceremony")}
        """
    ).rstrip()


def pipeline_gate_block_message(obpi_id: str) -> str:
    """Return the canonical write-gate blocker message."""
    return dedent(
        f"""\
        BLOCKED: Pipeline not invoked for {obpi_id}.

        A plan-audit receipt exists but the governance pipeline has not been
        started. Implementation writes to src/ and tests/ are gated until the
        canonical runtime is active.

        REQUIRED: Start the canonical runtime:
          {pipeline_runtime_command(obpi_id)}

        Thin alias available:
          {pipeline_skill_command(obpi_id)}

        If implementation is already complete, resume with:
          {pipeline_runtime_command(obpi_id, start_from="verify")}
        """
    ).rstrip()


def pipeline_completion_reminder_message(
    obpi_id: str,
    *,
    status: str | None,
    next_command: str | None,
) -> str:
    """Return the non-blocking reminder shown before commit or push."""
    resume_command = next_command or pipeline_runtime_command(obpi_id, start_from="ceremony")
    return dedent(
        f"""\
        PIPELINE COMPLETION REMINDER

        Active OBPI pipeline: {obpi_id}
        Brief status: {status or "Unknown"}

        You are about to commit or push while the governance pipeline still
        appears incomplete. Re-enter through the canonical runtime and finish
        the remaining closeout path from there.

        Preferred re-entry point:
          {resume_command}

        Thin alias available:
          {pipeline_skill_command(obpi_id, start_from="ceremony")}
        """
    ).rstrip()


def pipeline_stale_marker_message(obpi_id: str) -> str:
    """Return the stale-marker advisory shown when the brief is completed."""
    return dedent(
        f"""\
        STALE PIPELINE MARKER

        Active marker still references {obpi_id}, but the brief is already
        Completed. Clean up the pipeline marker if the closeout is done.
        """
    ).rstrip()


def _pipeline_plans_dir(project_root: Path) -> Path:
    """Return the canonical Claude plans directory."""
    return project_root / ".claude" / "plans"


def _load_pipeline_json(path: Path) -> dict[str, Any] | None:
    """Best-effort JSON loader for pipeline receipts and markers."""
    try:
        return cast(dict[str, Any], json.loads(path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return None


def _pipeline_marker_paths(plans_dir: Path, obpi_id: str) -> tuple[Path, Path]:
    """Return the per-OBPI and legacy marker paths."""
    return plans_dir / f".pipeline-active-{obpi_id}.json", plans_dir / PIPELINE_LEGACY_MARKER


def _pipeline_stage_name(start_from: str | None) -> str:
    """Return the active stage label persisted in the marker payload."""
    if start_from == "verify":
        return "verify"
    if start_from == "ceremony":
        return "ceremony"
    return "implement"


def _pipeline_stage_output(
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
            "next_command": pipeline_runtime_command(obpi_id, start_from="ceremony"),
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
            "next_command": "uv run gz git-sync --apply --lint --test",
            "resume_point": None,
        }
    return {
        "blockers": [],
        "required_human_action": None,
        "next_command": pipeline_runtime_command(obpi_id, start_from="verify"),
        "resume_point": "verify",
    }


def _pipeline_marker_payload(
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
        "current_stage": _pipeline_stage_name(start_from),
        "started_at": timestamp,
        "updated_at": timestamp,
        "receipt_state": receipt_state,
    }
    payload.update(
        _pipeline_stage_output(
            obpi_id,
            start_from,
            requires_human_attestation=requires_human_attestation,
        )
    )
    return payload


def _write_pipeline_markers(plans_dir: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    """Create active pipeline markers for the target OBPI."""
    obpi_id = payload["obpi_id"]
    per_obpi_marker, legacy_marker = _pipeline_marker_paths(plans_dir, obpi_id)
    plans_dir.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2) + "\n"
    per_obpi_marker.write_text(encoded, encoding="utf-8")
    legacy_marker.write_text(encoded, encoding="utf-8")
    return per_obpi_marker, legacy_marker


def _refresh_pipeline_markers(
    plans_dir: Path,
    obpi_id: str,
    *,
    blockers: list[str],
) -> None:
    """Refresh active marker stage-output fields for the target OBPI."""
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    per_obpi_marker, legacy_marker = _pipeline_marker_paths(plans_dir, obpi_id)
    for marker_path in (per_obpi_marker, legacy_marker):
        marker = _load_pipeline_json(marker_path)
        if marker is None or marker.get("obpi_id") != obpi_id:
            continue
        entry = str(marker.get("entry") or "full")
        start_from = None if entry == "full" else entry
        marker.update(_pipeline_stage_output(obpi_id, start_from, blockers=blockers))
        marker["updated_at"] = timestamp
        marker_path.write_text(json.dumps(marker, indent=2) + "\n", encoding="utf-8")


def _remove_pipeline_markers(plans_dir: Path, obpi_id: str) -> None:
    """Remove active markers only when they still point at the target OBPI."""
    per_obpi_marker, legacy_marker = _pipeline_marker_paths(plans_dir, obpi_id)
    for marker_path in (per_obpi_marker, legacy_marker):
        marker = _load_pipeline_json(marker_path)
        if marker is None or marker.get("obpi_id") != obpi_id:
            continue
        marker_path.unlink(missing_ok=True)


def _pipeline_concurrency_blockers(plans_dir: Path, obpi_id: str) -> list[str]:
    """Detect active markers that would conflict with this pipeline launch."""
    blockers: list[str] = []
    legacy_marker = _load_pipeline_json(plans_dir / PIPELINE_LEGACY_MARKER)
    if legacy_marker is not None:
        legacy_obpi = str(legacy_marker.get("obpi_id") or "")
        if legacy_obpi and legacy_obpi != obpi_id:
            blockers.append(f"another OBPI is already active in the legacy marker: {legacy_obpi}")

    for marker_path in sorted(plans_dir.glob(".pipeline-active-*.json")):
        marker = _load_pipeline_json(marker_path)
        if marker is None:
            continue
        active_obpi = str(marker.get("obpi_id") or "")
        if active_obpi and active_obpi != obpi_id:
            blockers.append(f"another OBPI is already active: {active_obpi}")
    return blockers


def _pipeline_receipt_state(
    plans_dir: Path, obpi_id: str
) -> tuple[str, list[str], dict[str, Any] | None]:
    """Return receipt state plus non-fatal warnings."""
    receipt_path = plans_dir / PIPELINE_RECEIPT_FILE
    if not receipt_path.exists():
        return (
            "missing",
            ["plan-audit receipt is missing; proceeding with an explicit gap"],
            None,
        )

    receipt = _load_pipeline_json(receipt_path)
    if receipt is None:
        return (
            "invalid",
            ["plan-audit receipt is unreadable; proceeding with an explicit gap"],
            None,
        )

    receipt_obpi = str(receipt.get("obpi_id") or "")
    if receipt_obpi and receipt_obpi != obpi_id:
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


def _pipeline_verification_commands(obpi_content: str, lane: str) -> list[str]:
    """Parse the Verification block into executable shell commands."""
    section = extract_markdown_section(obpi_content, "Verification") or ""
    matches = re.findall(r"```bash\n(.*?)```", section, flags=re.DOTALL)
    commands: list[str] = []
    for block in matches:
        for raw_line in block.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line == "command --to --verify":
                continue
            commands.append(line)
    if lane == "heavy":
        commands.extend(["uv run mkdocs build --strict", "uv run -m behave features/"])

    deduped: list[str] = []
    seen: set[str] = set()
    for command in commands:
        if command in seen:
            continue
        seen.add(command)
        deduped.append(command)
    return deduped


def _pipeline_stage_labels(start_from: str | None) -> list[str]:
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
