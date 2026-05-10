"""Fail-closed gate: require gz-justify artifact when evaluation scores trigger.

Gate fires when the most recent ``adr-evaluation`` ledger event for the given
artifact has at least one dimension score below ``low_score_threshold`` OR at
least ``red_team_count_threshold`` red-team challenges fired, and no qualifying
``gz-justify`` artifact exists under ``artifacts/justify/``.

Thresholds are loaded from ``data/eval_feedback_thresholds.json`` — never
hardcoded (REQ-0.0.26-02-05).
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.core.validation_rules import ValidationError


def validate_evaluation_justify_binding(
    artifact_id: str,
    project_root: Path,
    *,
    ledger_path: Path | None = None,
) -> list[ValidationError]:
    """Return ValidationError if low evaluation scores have no gz-justify artifact.

    Returns:
        Empty list if gate passes (no trigger, or trigger + artifact present).
        Non-empty list if gate fires (trigger + no artifact).

    """
    # Load thresholds from config
    thresholds = _load_thresholds(project_root)
    low_score_threshold = thresholds.get("low_score_threshold", 3.0)
    red_team_count_threshold = thresholds.get("red_team_count_threshold", 3)

    # Find most recent adr-evaluation event for this artifact
    lp = ledger_path or (project_root / ".gzkit" / "ledger.jsonl")
    event = _latest_evaluation_event(lp, artifact_id)
    if event is None:
        return []  # No evaluation has run — no gate requirement

    # Check trigger conditions
    dimensions: dict[str, float] = event.get("dimensions", {})
    red_team: list = event.get("red_team_challenges_fired", [])
    failing_dims = [dim for dim, score in dimensions.items() if score < low_score_threshold]
    red_team_triggered = len(red_team) >= red_team_count_threshold

    if not failing_dims and not red_team_triggered:
        return []  # No trigger

    # Gate fired — check for qualifying justify artifact
    justify_dir = project_root / "artifacts" / "justify"
    if _has_justify_artifact(justify_dir, artifact_id):
        return []  # Artifact present — gate passes

    # Gate fired and no artifact — return error
    artifact_slug = artifact_id.replace(".", "-").lower()
    missing_path = (justify_dir / f"{artifact_slug}-<timestamp>.md").as_posix()
    reasons = []
    if failing_dims:
        reasons.append(f"dimension score(s) below threshold: {', '.join(failing_dims)}")
    if red_team_triggered:
        reasons.append(f"{len(red_team)} red-team challenge(s) fired")
    return [
        ValidationError(
            type="evaluation-justify-binding",
            artifact=artifact_id,
            message=(
                f"gz-justify artifact required for {artifact_id}: "
                f"{'; '.join(reasons)}. "
                f"Expected at: {missing_path}"
            ),
        )
    ]


def _load_thresholds(project_root: Path) -> dict:
    """Load eval feedback thresholds from ``data/eval_feedback_thresholds.json``."""
    config_path = project_root / "data" / "eval_feedback_thresholds.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def _latest_evaluation_event(ledger_path: Path, artifact_id: str) -> dict | None:
    """Return the most recent ``adr-evaluation`` event for ``artifact_id``, or None."""
    if not ledger_path.exists():
        return None
    events = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") == "adr-evaluation" and ev.get("id") == artifact_id:
            events.append(ev)
    return events[-1] if events else None


def _has_justify_artifact(justify_dir: Path, artifact_id: str) -> bool:
    """Return True if any file under ``justify_dir`` matches ``artifact_id``."""
    if not justify_dir.is_dir():
        return False
    artifact_slug = artifact_id.replace(".", "-").lower()
    for f in justify_dir.iterdir():
        name = f.name.lower()
        if name.startswith(artifact_slug) or artifact_id.lower() in name:
            return True
    return False
