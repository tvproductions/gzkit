"""Lock-handoff coupling validator (ADR-0.0.41 / OBPI-04).

Replays the ledger and fail-closes on any `obpi_lock_released` event whose
`handoff_path` payload is missing, references a nonexistent file, predates
the matching claim, or whose register entry violates Sub-Invariant 2's
minimum-information rule.

Implementation lands under OBPI-0.0.41-04; this stub satisfies the brief's
ground-truth Allowed Path check.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.core.validation_rules import ValidationError


def validate_lock_handoff_coupling(project_root: Path) -> list[ValidationError]:
    """Replay the ledger and fail-close on broken release/handoff couplings.

    Stub — full implementation lands in OBPI-0.0.41-04 per the brief at
    `docs/design/adr/foundation/ADR-0.0.41-token-block-lock-discipline/
    obpis/OBPI-0.0.41-04-lock-handoff-coupling-validator.md`.
    """
    del project_root
    return []
