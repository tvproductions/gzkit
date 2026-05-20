"""Governance-layer event emission helpers (ADR-0.0.37, OBPI-0.0.37-03)."""

from __future__ import annotations

from pathlib import Path

from gzkit.ledger import Ledger
from gzkit.ledger_events import (
    composition_drift_detected_event,
    composition_rendered_event,
)


def emit_composition_rendered(
    root: Path,
    invariant_count: int,
    target: str,
    byte_count: int,
) -> None:
    """Append a composition_rendered event to the project ledger."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(
        composition_rendered_event(
            invariant_count=invariant_count,
            target=target,
            byte_count=byte_count,
        )
    )


def emit_composition_drift_detected(
    root: Path,
    target: str,
    diff_first_50_lines: str,
) -> None:
    """Append a composition_drift_detected event to the project ledger."""
    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    ledger.append(
        composition_drift_detected_event(
            target=target,
            diff_first_50_lines=diff_first_50_lines,
        )
    )
