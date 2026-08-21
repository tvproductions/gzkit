#!/usr/bin/env python3
"""Pipeline Gate Hook.

PreToolUse hook on Write|Edit that blocks implementation file writes
under `src/` and `tests/` for a governed OBPI whose pipeline is not
active. The OBPI is identified by either a passing plan-audit
receipt (plan-mode path) or an OBPI lock held by the current agent
(GHI #606 — closes the never-entered-plan bypass). Blocking is
scoped to the OBPI's `## Allowed Paths`.

Exit codes:
  0 - Allow operation
  2 - Block operation (pipeline not invoked)
"""

import json
import os
import re
import sys
from pathlib import Path


def resolve_repo_path(cwd: str, file_path: str) -> str | None:
    """Resolve a tool file path into a repo-relative POSIX path."""
    if not cwd or not file_path:
        return None

    try:
        cwd_path = Path(cwd).resolve()
        target = Path(file_path)
        if not target.is_absolute():
            target = cwd_path / target
        rel_path = target.resolve().relative_to(cwd_path)
    except (OSError, TypeError, ValueError):
        return None

    return rel_path.as_posix()


def find_project_root(start: Path) -> Path:
    """Find the project root by looking for .gzkit or src/gzkit."""
    current = start
    while current != current.parent:
        if (current / ".gzkit").is_dir() or (current / "src" / "gzkit").is_dir():
            return current
        current = current.parent
    return start


def _is_path_within_scope(rel_path: str, allowed_paths: list[str]) -> bool:
    """Check if rel_path falls within any of the OBPI's allowed paths (#127)."""
    for allowed in allowed_paths:
        clean = allowed.rstrip("/").replace("/**", "")
        if rel_path == clean or rel_path.startswith(clean + "/"):
            return True
    return False


def _extract_allowed_paths_from_brief(brief_path: Path) -> list[str]:
    """Extract allowed paths from an OBPI brief file (#127)."""
    try:
        content = brief_path.read_text(encoding="utf-8")
    except OSError:
        return []
    match = re.search(
        r"^## Allowed Paths\s*$([\s\S]*?)(?:^## |\Z)",
        content,
        flags=re.MULTILINE,
    )
    if not match:
        return []
    paths: list[str] = []
    for line in match.group(1).splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        backticked = re.findall(r"`([^`]+)`", stripped)
        candidates = backticked or [re.sub(r"^-+\s*", "", stripped).split(" - ", 1)[0]]
        for candidate in candidates:
            normalized = candidate.strip().replace("\\", "/")
            if normalized and " " not in normalized:
                paths.append(normalized)
    return paths


# Stages in which AUTHORING production code is the declared work. Every other
# canonical stage is post-authoring: the pipeline has already left Stage 2, so a
# fresh `src/**` write there is freeform implementation wearing an active
# marker. `.claude/hooks/pipeline-gate.py` witnessed marker PRESENCE only until
# 2026-08-21, which is how OBPI-0.35.0-09 took ~350 lines of production edits at
# `current_stage: verify` with no implementer dispatch and no two-stage review —
# the Stage-2 gate that exists to catch hollow tests and subject-substituted REQ
# coverage never ran, and three tier-1 adversary rounds found it instead.
_AUTHORING_STAGES = frozenset({"implement"})


def _marker_stage(marker_path: Path) -> str | None:
    """Return the marker's ``current_stage``, or ``None`` when unreadable/absent.

    ``None`` permits the write: a marker with no stage predates this check, and
    refusing on a parse error would block repair of the very marker at fault.
    """
    try:
        payload = json.loads(marker_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    stage = payload.get("current_stage")
    return str(stage) if isinstance(stage, str) and stage else None


def _post_authoring_message(obpi_id: str, stage: str, rel_path: str) -> str:
    """Explain why a production write is refused after Stage 2, and how to proceed."""
    return (
        f"BLOCKED: `{rel_path}` is a production write, but the pipeline marker for "
        f"{obpi_id} is at `current_stage: {stage}` — past Stage 2.\n\n"
        "WHY: an active marker is not evidence that the skill's Stage 2 ran. Stage 2 "
        "dispatches an implementer and then a two-stage spec-reviewer + quality-reviewer "
        "pass; that review is what catches hollow tests and REQ coverage bound to the "
        "wrong subject. Authoring production code at a post-authoring stage skips it "
        "while every marker-presence check still reads green.\n\n"
        "NEXT STEP: if this is genuine implementation work, re-enter Stage 2 so the "
        "review fires -- `uv run gz obpi pipeline "
        f"{obpi_id}` -- and let the skill dispatch it. If it is the bounded in-flight "
        "repair Stage 3 allows after a failed check, move the marker back to "
        "`implement` through the runtime so the re-entry is recorded, then repair. "
        "Do NOT hand-edit the marker to satisfy this gate (AGENTS.md Never #6).\n\n"
        "`tests/**` writes stay permitted at every stage: Phase 1b @covers parity and "
        "the Phase 1c RED witness are verify-stage work by design."
    )


def main() -> None:
    """Gate implementation writes until the pipeline is active."""
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_input = input_data.get("tool_input", {})
    rel_path = resolve_repo_path(
        input_data.get("cwd", os.getcwd()),
        tool_input.get("file_path", ""),
    )
    if rel_path is None or not rel_path.startswith(("src/", "tests/")):
        sys.exit(0)

    project_root = find_project_root(Path(input_data.get("cwd", os.getcwd())).resolve())
    sys.path.insert(0, str(project_root / "src"))

    try:
        from gzkit.pipeline_runtime import (
            agent_held_obpi_ids,
            extract_brief_status,
            find_obpi_brief,
            load_plan_audit_receipt,
            marker_matches,
            pipeline_gate_message,
            pipeline_marker_paths,
            pipeline_plans_dir,
        )
    except Exception:
        sys.exit(0)

    plans_dir = pipeline_plans_dir(project_root)
    docs_root = project_root / "docs"

    # Collect governing OBPI ids from both arming paths.
    candidates: list[str] = []

    # Arm A (GHI-127): a passing plan-audit receipt names the OBPI.
    if plans_dir.is_dir():
        receipt_state, _warnings, receipt = load_plan_audit_receipt(plans_dir, "")
        if receipt is not None and receipt_state == "pass":
            receipt_obpi = str(receipt.get("obpi_id") or "")
            if receipt_obpi:
                candidates.append(receipt_obpi)

    # Arm B (GHI #606): an OBPI lock held by THIS agent, whether or
    # not plan mode was ever entered — closes the never-entered-plan
    # bypass the receipt-keyed arm cannot see.
    for locked_obpi in agent_held_obpi_ids(project_root):
        if locked_obpi and locked_obpi not in candidates:
            candidates.append(locked_obpi)

    for obpi_id in candidates:
        brief_path = find_obpi_brief(docs_root, obpi_id)
        if brief_path is not None:
            brief_status = extract_brief_status(brief_path)
            if brief_status and brief_status.lower() == "completed":
                continue

            # Scope enforcement to the OBPI's allowed paths.
            allowed_paths = _extract_allowed_paths_from_brief(brief_path)
            if allowed_paths and not _is_path_within_scope(rel_path, allowed_paths):
                continue

        obpi_marker, legacy_marker = pipeline_marker_paths(plans_dir, obpi_id)
        active_marker: Path | None = None
        if marker_matches(obpi_marker, obpi_id):
            active_marker = obpi_marker
        elif marker_matches(legacy_marker, obpi_id):
            active_marker = legacy_marker

        if active_marker is not None:
            # An active marker arms the pipeline; it does NOT attest that Stage 2
            # ran. Production authoring is refused once the marker has moved past
            # the authoring stage. Tests stay open — verify-stage work needs them.
            stage = _marker_stage(active_marker)
            if rel_path.startswith("src/") and stage is not None and stage not in _AUTHORING_STAGES:
                print(_post_authoring_message(obpi_id, stage, rel_path), file=sys.stderr)
                sys.exit(2)
            continue

        # In scope, not completed, no active marker: freeform
        # implementation of a governed OBPI. Block with recovery prose.
        print(pipeline_gate_message(obpi_id), file=sys.stderr)
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
