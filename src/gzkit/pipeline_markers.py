"""Pipeline marker I/O, discovery, receipt loading, and message builders.

Extracted from pipeline_runtime.py to keep module sizes under 600 lines.
All public symbols are re-exported from pipeline_runtime for backward compatibility.
"""

from __future__ import annotations

import json
import os
import re
import secrets
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast


def _claude_home() -> Path:
    """Return the Claude Code user home directory.

    Honors the ``GZKIT_CLAUDE_HOME`` environment variable so tests can point
    plan-discovery at an isolated fake home without monkey-patching the
    subprocess hook.
    """
    override = os.environ.get("GZKIT_CLAUDE_HOME")
    if override:
        return Path(override)
    return Path.home()


PIPELINE_RECEIPT_FILE = ".plan-audit-receipt.json"
PIPELINE_LEGACY_MARKER = ".pipeline-active.json"
# Operator ruling 2026-09-02: 4h was too short for the real cadence of this
# work. A marker's age is not evidence of abandonment — an OBPI checkpointed
# mid-flight, with its lock held and a `resume_point` recorded, is a LIVE
# session that a 4h TTL called stale within one working block. Measured
# instance: OBPI-0.35.0-04 checkpointed at 12:45Z and its two markers were
# reported stale by every `gz check` from 16:45Z onward, locally and in CI,
# regardless of what was being pushed. 24h matches the staleness threshold
# ADR-0.0.22 already set for security-scan receipts, so the repo now carries
# one number for "how old before we stop believing this", not two.
STALE_MARKER_HOURS = 24

_OBPI_SHORT_FORM_RE = re.compile(r"OBPI-\d+\.\d+\.\d+-\d+")


# A plan's declaration block names its subject structurally — an H1, or the
# ``**OBPI:**`` / ``**OBPI slug:**`` label the plan templates carry. Deliberately
# NOT a line-count window: the incidental mention this rule exists to reject sat
# at line 19 of the real conflicting plan, so a positional rule would have passed
# by accident of where one sentence landed.
_OBPI_LABEL_RE = re.compile(r"^\s*\**OBPI(?:\s+slug)?\**\s*:", re.IGNORECASE)


def _obpi_short_form(obpi_id: str) -> str:
    """Return the short form ``OBPI-X.Y.Z-NN`` from any OBPI identifier.

    plan_audit_cmd canonicalizes short-form input to the full slug before
    plan discovery (GHI #187). Plan files authored by Claude Code's plan
    mode (or by any agent that did not consult the ledger) typically only
    reference the short form. Matching on the short form ensures both
    callers — short-form and canonical-slug — agree on plan identity
    (GHI #313).
    """
    match = _OBPI_SHORT_FORM_RE.search(obpi_id)
    return match.group(0) if match else obpi_id


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
    """Return the project-local Claude plans directory.

    Receipts and markers always live here. Plan files (the markdown plans
    Claude Code's plan mode produces) may originate here OR in
    ``~/.claude/plans/``; use ``pipeline_plan_search_dirs`` and
    ``find_plan_for_obpi`` for plan discovery (#128).
    """
    return project_root / ".claude" / "plans"


def pipeline_plan_search_dirs(project_root: Path) -> list[Path]:
    """Return all directories to search when looking for a plan file (#128).

    Plan mode in Claude Code writes new plans to ``~/.claude/plans/`` (the
    global user directory), not the project-local ``.claude/plans/``. The
    historic project-local search missed every plan written by plan mode and
    produced a silent FAIL receipt that aborted the OBPI pipeline. Both
    locations must be searched.

    Project-local is listed first so a plan that exists in both wins from the
    project (its mtime is the more authoritative signal once a plan has been
    promoted into governance evidence).
    """
    project_local = project_root / ".claude" / "plans"
    global_local = _claude_home() / ".claude" / "plans"
    candidates: list[Path] = []
    seen: set[Path] = set()
    for candidate in (project_local, global_local):
        try:
            resolved = candidate.resolve()
        except (OSError, RuntimeError):
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if candidate.is_dir():
            candidates.append(candidate)
    return candidates


def _declared_obpi_ids(plan_path: Path) -> set[str]:
    """Return the short-form OBPI ids a plan DECLARES — filename plus its H1.

    Declaration is STRUCTURAL — the filename, an H1, or an ``**OBPI:**`` label —
    and stops at the first ``##``, below which everything is body prose.

    Measured over the live corpus 2026-09-06: of 306 plans, 304 name their OBPI
    in the H1 and only 217 in the filename, so filename-only ownership would
    orphan every auto-named plan. The two that declare neither own no OBPI (one
    is ADR-scoped, one is a superseded stub).
    """
    declared = set(_OBPI_SHORT_FORM_RE.findall(plan_path.name))
    try:
        lines = plan_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return declared
    for line in lines:
        if line.startswith("## "):
            break  # past the declaration block; everything below is body prose
        if line.startswith("# ") or _OBPI_LABEL_RE.match(line):
            declared.update(_OBPI_SHORT_FORM_RE.findall(line))
    return declared


def plan_declares_obpi(plan_path: Path, obpi_id: str) -> bool:
    """Report whether this plan OWNS ``obpi_id`` rather than merely mentioning it.

    The single ownership rule for the plans directory. Two callers disagreed:
    discovery accepted any mention of the short form anywhere in the body, while
    orphan detection required the full slug. The same plan was therefore both
    "the plan for OBPI-05" and "no plan exists for OBPI-05", so a
    FAIL-because-no-plan-exists receipt orphaned itself by construction — the way
    a sibling plan mentions an unplanned OBPI IS the short-form exclusion
    sentence, and the more correctly a plan disclaims scope it does not carry,
    the more certainly the resulting receipt self-orphaned.

    Ownership is DECLARED (filename, H1, or ``**OBPI:**`` label), never
    incidental. Comparison is on the short form so the short-form and
    canonical-slug callers agree (GHI #313, GHI #967).
    """
    if not obpi_id:
        return False
    return _obpi_short_form(obpi_id) in _declared_obpi_ids(plan_path)


def find_plan_for_obpi(project_root: Path, obpi_id: str) -> Path | None:
    """Locate the most recent plan file referencing ``obpi_id`` across both dirs (#128).

    Searches every directory returned by :func:`pipeline_plan_search_dirs`,
    chooses the plan file with the most recent mtime that mentions the OBPI,
    and — if that file lives in the global user directory — copies it into
    the project-local plans directory so the plan, the receipt, and the
    pipeline marker stay co-located. Returns the project-local path the
    caller should treat as authoritative, or ``None`` if no plan was found.
    """
    if not obpi_id:
        return None

    short_form = _obpi_short_form(obpi_id)
    project_local = pipeline_plans_dir(project_root)
    candidates: list[tuple[float, Path]] = []
    for plans_dir in pipeline_plan_search_dirs(project_root):
        for plan_path in plans_dir.glob("*.md"):
            if plan_path.name.startswith("."):
                continue
            if short_form not in _declared_obpi_ids(plan_path):
                continue
            try:
                mtime = plan_path.stat().st_mtime
            except OSError:
                continue
            candidates.append((mtime, plan_path))

    if not candidates:
        return None

    _, source_path = max(candidates, key=lambda item: item[0])

    try:
        source_resolved = source_path.resolve()
        project_resolved = project_local.resolve() if project_local.exists() else project_local
    except (OSError, RuntimeError):
        return source_path

    if project_local in source_path.parents or source_resolved.parent == project_resolved:
        return source_path

    project_local.mkdir(parents=True, exist_ok=True)
    destination = project_local / source_path.name
    if not destination.exists() or destination.stat().st_mtime < source_path.stat().st_mtime:
        try:
            destination.write_text(source_path.read_text(encoding="utf-8"), encoding="utf-8")
        except OSError:
            return source_path
    return destination


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


def generate_pipeline_nonce() -> str:
    """Return a fresh 32-hex-character nonce for pipeline-launch authenticity (GHI #412)."""
    return secrets.token_hex(16)


def pipeline_marker_payload(
    obpi_id: str,
    parent_adr: str,
    lane: str,
    start_from: str | None,
    receipt_state: str,
    *,
    execution_mode: str = "normal",
    requires_human_attestation: bool = False,
    nonce: str | None = None,
) -> dict[str, Any]:
    """Build the persisted active-state payload for pipeline markers.

    GHI #412: a ``nonce`` field is now embedded so the agent-relayed
    attestation gate can cross-check the marker against a matching
    ``pipeline_launched`` ledger event. The caller may pass an explicit
    nonce (used by tests and replay paths); otherwise a fresh one is
    generated.
    """
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
        "nonce": nonce or generate_pipeline_nonce(),
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


def remove_pipeline_artifacts(plans_dir: Path, obpi_id: str) -> None:
    """Remove every plans-dir artifact belonging to this OBPI (GHI #139).

    Self-heals at pipeline completion so per-OBPI plan-audit receipts do not
    survive as future orphans. Removes:

    - the per-OBPI pipeline marker (``.pipeline-active-<obpi>.json``)
    - the legacy pipeline marker, only when it still points at this OBPI
    - the per-OBPI plan-audit receipt (``.plan-audit-receipt-<obpi>.json``)
    """
    remove_pipeline_markers(plans_dir, obpi_id)
    pipeline_receipt_path(plans_dir, obpi_id).unlink(missing_ok=True)


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


def purge_orphaned_active_markers(
    plans_dir: Path,
    artifact_graph: Mapping[str, Mapping[str, Any]],
) -> list[tuple[Path, str, str]]:
    """Remove ``.pipeline-active-*`` markers whose OBPI is already attested_completed (GHI #399).

    The pipeline runtime writes a marker in Stage 1 and is contracted to remove
    it in Stage 5 step 4. When Stage 5 doesn't fire (session interruption, hook
    abort, harness restart) the marker becomes a stale orphan that fail-closes
    every future ``gz obpi pipeline`` invocation. This helper, called from the
    launcher before the concurrency check, scans the marker set and removes any
    marker whose OBPI's ledger state is ``attested_completed`` — provably
    orphaned and safe to clear.

    The caller emits a ``pipeline_marker_purged`` ledger event for each entry
    in the returned list so the cleanup is auditable and not a silent unlink.
    The function itself does not import the ledger; it consumes the
    pre-computed artifact-graph mapping the caller already loaded.
    """
    purged: list[tuple[Path, str, str]] = []

    candidates: list[Path] = sorted(plans_dir.glob(".pipeline-active-*.json"))
    legacy_path = plans_dir / PIPELINE_LEGACY_MARKER
    if legacy_path.exists():
        candidates.append(legacy_path)

    for marker_path in candidates:
        marker = load_pipeline_json(marker_path)
        if marker is None:
            continue
        marker_obpi = str(marker.get("obpi_id") or "")
        if not marker_obpi:
            continue
        info = artifact_graph.get(marker_obpi)
        if info is None or info.get("type") != "obpi":
            continue
        if info.get("obpi_completion") != "attested_completed":
            continue
        marker_path.unlink(missing_ok=True)
        parent_adr = str(info.get("parent") or "")
        purged.append((marker_path, marker_obpi, parent_adr))

    return purged


def pipeline_receipt_path(plans_dir: Path, obpi_id: str) -> Path:
    """Return the per-OBPI receipt path."""
    return plans_dir / f".plan-audit-receipt-{obpi_id}.json"


def _resolve_receipt_path(plans_dir: Path, obpi_id: str) -> Path | None:
    """Find the best receipt file: per-OBPI first, then legacy.

    When ``obpi_id`` is provided, prefer the exact per-OBPI receipt and fall
    back to the legacy path. When ``obpi_id`` is empty, the caller is asking
    "what receipt should drive this hook?" — pick the most recently modified
    receipt across per-OBPI and legacy so a stale legacy file cannot mask a
    fresh per-OBPI receipt (gzkit#140).
    """
    if obpi_id:
        per_obpi = pipeline_receipt_path(plans_dir, obpi_id)
        if per_obpi.exists():
            return per_obpi
        legacy = plans_dir / PIPELINE_RECEIPT_FILE
        return legacy if legacy.exists() else None

    candidates = list(plans_dir.glob(".plan-audit-receipt-*.json"))
    legacy = plans_dir / PIPELINE_RECEIPT_FILE
    if legacy.exists():
        candidates.append(legacy)
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


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


def validate_brief_for_pipeline(project_root: Path, brief_path: Path) -> list[str]:
    """Run authored-readiness validation on a brief before pipeline execution.

    Returns a list of blocking errors.  An empty list means the brief
    is safe to execute against.
    """
    from gzkit.hooks.obpi import ObpiValidator  # noqa: PLC0415

    validator = ObpiValidator(project_root)
    return validator.validate_file(brief_path, require_authored=True)


def check_adr_evaluation_verdict(adr_dir: Path) -> list[str]:
    """Check for a NO GO evaluation verdict in the ADR directory.

    Reads the judge-authored ``EVALUATION_SUBSTANCE.md`` first, falling back to
    ``EVALUATION_SCORECARD.md``. Returns a list of blocking errors if a NO GO
    verdict is found; an empty list if neither file exists (advisory, not
    required) or if the verdict is GO or CONDITIONAL GO.

    Precedence is load-bearing (GHI #769). The verdict marker matched below is
    emitted only by the judge's template — ``render_scorecard_markdown`` renders
    checkbox lines and no ``**Verdict:**`` — while ``gz adr evaluate`` rewrites
    the scorecard wholesale on every run. Reading the machine-owned file first
    therefore let a regenerated structural scorecard erase a recorded NO GO, so
    the gate reported clean precisely when it had most to say.

    The scorecard fallback is retained because 46 of the 55 scorecards on disk
    at the cutover carried judge verdicts; dropping it would disarm the gate for
    every one of them, which is the same defect arriving from the other side.
    """
    for filename in ("EVALUATION_SUBSTANCE.md", "EVALUATION_SCORECARD.md"):
        verdict_path = adr_dir / filename
        if not verdict_path.exists():
            continue

        try:
            content = verdict_path.read_text(encoding="utf-8")
        except OSError:
            continue

        verdict_match = re.search(
            r"\*\*(?:Overall\s+)?Verdict[:\s]*\*\*\s*(\S+(?:\s+\S+)*)", content
        )
        if not verdict_match:
            continue

        verdict = verdict_match.group(1).strip().upper()
        if "NO GO" in verdict or "NO_GO" in verdict or "NOGO" in verdict:
            return [
                f"ADR evaluation verdict is NO GO ({verdict_path.name}). "
                "Revise the ADR or OBPIs and re-run: uv run gz adr evaluate <ADR-ID>"
            ]
        return []
    return []


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
