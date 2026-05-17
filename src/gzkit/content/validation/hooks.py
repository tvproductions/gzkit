"""Validation hooks — ADR-0.0.34 § Decision item #6 (OBPI-0.0.34-06).

Wires the ADR-0.0.33 fidelity validator suite at two hook points:
  - validate_render: fired by render() after producing bytes, before returning
  - validate_save: fired by gz content edit save-path, after render, before write

Fail-closed: any ValidationError from the suite raises FidelityHookError.
No warn-and-continue path exists.
"""

from __future__ import annotations

from pathlib import Path

import gzkit.governance.trust_audits as _trust_audits
from gzkit.core.validation_rules import ValidationError


class FidelityHookError(Exception):
    """Raised when the fidelity validator suite detects a violation.

    Attributes:
        validator_id: The failing validator's type string (from ValidationError.type).
        violation: Human-readable description of the failure.
        errors: Full list of ValidationError from the validator suite.
    """

    def __init__(
        self,
        *,
        validator_id: str,
        violation: str,
        errors: list[ValidationError] | None = None,
    ) -> None:
        self.validator_id = validator_id
        self.violation = violation
        self.errors = errors or []
        super().__init__(f"Fidelity validation failed [{validator_id}]: {violation}")


def _run_validators(project_root: Path) -> None:
    """Run ADR-0.0.33 fidelity suite; raise FidelityHookError on first failure."""
    errors = _trust_audits.validate_surface_fidelity(project_root)
    if errors:
        first = errors[0]
        raise FidelityHookError(
            validator_id=first.type,
            violation=first.message,
            errors=errors,
        )


def validate_render(*, project_root: Path) -> None:
    """Invoke the ADR-0.0.33 fidelity suite at the render hook point.

    Called by render() after producing bytes, before returning.
    Raises FidelityHookError on any fidelity violation.

    Note: ADR-0.0.33 validators operate on project-root surfaces, not on the
    produced byte-string directly. A rendered bytes parameter was removed as it
    was unused and created a deceptive API. Byte-level validators can be added
    to the suite when required.
    """
    _run_validators(project_root)


def validate_save(*, project_root: Path) -> None:
    """Invoke the ADR-0.0.33 fidelity suite at the save hook point.

    Called by gz content edit save-path after render(), before write.
    Raises FidelityHookError on any fidelity violation.

    Note: ADR-0.0.33 validators operate on project-root surfaces, not on the
    produced byte-string directly. A rendered bytes parameter was removed as it
    was unused and created a deceptive API. Byte-level validators can be added
    to the suite when required.
    """
    _run_validators(project_root)
