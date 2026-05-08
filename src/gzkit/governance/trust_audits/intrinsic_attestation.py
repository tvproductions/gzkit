"""Fail-closed audit: intrinsic-complexity-attestation ledger event shape (OBPI-0.0.29-07).

Validates that every ``intrinsic-complexity-attestation`` event in the ledger
carries all required fields with correct types. Malformed events fail the
``gz validate --intrinsic-attestation`` scope with a structured
:class:`~gzkit.core.validation_rules.ValidationError`.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

_REQUIRED_STR_FIELDS = frozenset(
    {
        "file_path",
        "qualname",
        "reason",
        "attestor",
        "attestation_date",
        "metric",
        "crossing_band",
    }
)
_VALID_CROSSING_BANDS = frozenset({"block", "warn", "advise"})


def validate_intrinsic_attestation(project_root: Path) -> list[ValidationError]:
    """Return ValidationErrors for malformed intrinsic-complexity-attestation events.

    Reads ``.gzkit/ledger.jsonl`` from ``project_root`` and checks every
    ``intrinsic-complexity-attestation`` event for required-field presence,
    non-empty string values, a valid ``crossing_band`` enum, and a numeric
    ``crossing_value``.
    """
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []

    errors: list[ValidationError] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") != "intrinsic-complexity-attestation":
            continue
        artifact = ev.get("id", "<unknown>")
        for field in _REQUIRED_STR_FIELDS:
            val = ev.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(
                    ValidationError(
                        type="intrinsic_attestation",
                        artifact=artifact,
                        message=(
                            f"intrinsic-complexity-attestation event {artifact!r}: "
                            f"required field {field!r} is missing or empty."
                        ),
                    )
                )
        band = ev.get("crossing_band")
        if isinstance(band, str) and band not in _VALID_CROSSING_BANDS:
            errors.append(
                ValidationError(
                    type="intrinsic_attestation",
                    artifact=artifact,
                    message=(
                        f"intrinsic-complexity-attestation event {artifact!r}: "
                        f"crossing_band {band!r} not in {sorted(_VALID_CROSSING_BANDS)}."
                    ),
                )
            )
        crossing_value = ev.get("crossing_value")
        if not isinstance(crossing_value, (int, float)):
            errors.append(
                ValidationError(
                    type="intrinsic_attestation",
                    artifact=artifact,
                    message=(
                        f"intrinsic-complexity-attestation event {artifact!r}: "
                        f"crossing_value must be a number, got {type(crossing_value).__name__!r}."
                    ),
                )
            )
    return errors
