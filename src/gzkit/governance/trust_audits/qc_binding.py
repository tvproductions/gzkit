"""QC-binding behavioral audit (ADR-0.0.73 / OBPI-0.0.73-02).

Detects theater in bound QC steps via two channels:
1. Six static theater-signature checks (calibrated on ADR-0.0.37 facade)
2. Negative-control execution: a step that passes its own NC is theater

Usage::

    from gzkit.governance.trust_audits.qc_binding import audit_qc_binding
    errors = audit_qc_binding(project_root)
    # Non-empty → exit 3; empty → exit 0
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.qc_binding import QCStep

# ---------------------------------------------------------------------------
# Six theater signatures calibrated on the ADR-0.0.37 facade
# ---------------------------------------------------------------------------

THEATER_SIGNATURES: tuple[str, ...] = (
    "mtime-where-name-says-content",
    "empty-input-passes",
    "copy-vs-self",
    "fixture-only",
    "skip-if-PASS",
    "prose-graded-by-nothing",
)

_THEATER_SIGNATURE_DESCRIPTIONS: dict[str, str] = {
    "mtime-where-name-says-content": (
        "Step checks file modification time instead of content "
        "(name implies content-checking but implementation uses mtime)"
    ),
    "empty-input-passes": (
        "Step always passes when given empty or absent input "
        "(no content → no violation is theater, not a clean check)"
    ),
    "copy-vs-self": (
        "Fixture compares content to itself — tautological assertion "
        "(fixture == expected is always true; the check can never fail)"
    ),
    "fixture-only": (
        "Step only runs against its own fixture, never the real project "
        "(a step that never sees real code cannot catch real violations)"
    ),
    "skip-if-PASS": (
        "Step short-circuits when a prior artifact is already in PASS state "
        "(skipping on PASS means the check never runs the second time)"
    ),
    "prose-graded-by-nothing": (
        "Step outputs prose that is never machine-verified "
        "(agent-written prose without a bound checker is theater)"
    ),
}

# ---------------------------------------------------------------------------
# Negative-control registry
# ---------------------------------------------------------------------------

# Module-level NC registry: step_id → callable returning int (exit code).
# A callable returning 0 means the step PASSED its NC → hollow → theater.
# A callable returning non-zero means the step FAILED its NC → bound → genuine.
# Populated by register_negative_control(); OBPI-06 fills in the real entries.
_NEGATIVE_CONTROLS: dict[str, Callable[[], int]] = {}


def register_negative_control(step_id: str, nc: Callable[[], int]) -> None:
    """Register a negative-control callable for a bound step.

    The callable must return an exit-code-like integer: 0 if the negative
    control passed (step is hollow/theater), non-zero if the step genuinely
    failed (step is bound). OBPI-06 registers entries for all existing steps.
    """
    _NEGATIVE_CONTROLS[step_id] = nc


# ---------------------------------------------------------------------------
# Error builder
# ---------------------------------------------------------------------------


def _err(step_name: str, message: str) -> ValidationError:
    return ValidationError(type="qc_binding", artifact=step_name, message=message)


# ---------------------------------------------------------------------------
# Theater-signature detection
# ---------------------------------------------------------------------------


def _check_theater_signatures(step: QCStep) -> list[ValidationError]:
    """Return one ValidationError per theater signature found in step.theater_flags.

    The six ADR-0.0.37 facade signatures are canonical; any flag from that set
    found in step.theater_flags produces an error. Unknown flags are noted but
    not treated as the canonical six.
    """
    errors: list[ValidationError] = []
    for flag in step.theater_flags:
        if flag in THEATER_SIGNATURES:
            description = _THEATER_SIGNATURE_DESCRIPTIONS.get(flag, "")
            errors.append(
                _err(
                    step.name,
                    f"Theater signature '{flag}': {description}. "
                    "Implement a genuine check that fails for the right reason.",
                )
            )
    return errors


# ---------------------------------------------------------------------------
# Negative-control execution
# ---------------------------------------------------------------------------


def _check_negative_control(
    step: QCStep,
    nc_registry: dict[str, Callable[[], int]] | None = None,
) -> list[ValidationError]:
    """Run the step's negative control; flag if it exits 0 (hollow step).

    When ``nc_registry`` is None, the module-level ``_NEGATIVE_CONTROLS``
    registry is used. Passing an explicit registry is the test-isolation path.

    A step with no registered NC is skipped — absence of an NC is not itself
    a finding (OBPI-06 adds NCs; OBPI-02 ships the infrastructure only).
    """
    registry = nc_registry if nc_registry is not None else _NEGATIVE_CONTROLS
    nc = registry.get(step.id)
    if nc is None:
        return []
    exit_code = nc()
    if exit_code == 0:
        return [
            _err(
                step.name,
                "Hollow step: passed its own negative-control fixture (exit 0 when "
                "non-zero expected). A genuinely bound check must fail on its "
                "negative control.",
            )
        ]
    return []


# ---------------------------------------------------------------------------
# Main audit entry point
# ---------------------------------------------------------------------------


def audit_qc_binding(
    project_root: Path,  # noqa: ARG001 — registry-protocol parity; OBPI-06 may use it
    *,
    nc_registry: dict[str, Callable[[], int]] | None = None,
) -> list[ValidationError]:
    """Behavioral QC-binding audit (ADR-0.0.73 / OBPI-0.0.73-02).

    For every QC step in the registry:
    - Runs theater-signature detection (via step.theater_flags)
    - For ``bound`` steps, runs the registered negative control (if any)

    Returns a list of ValidationErrors; non-empty → caller should exit 3.
    An unclassified step (``build_qc_registry`` KeyError) is surfaced as a
    single error on the "registry" artifact rather than crashing.
    """
    from gzkit.qc_binding import build_qc_registry  # noqa: PLC0415

    try:
        registry = build_qc_registry()
    except KeyError as exc:
        return [
            ValidationError(
                type="qc_binding",
                artifact="registry",
                message=f"QC registry build failed — unclassified step: {exc}",
            )
        ]

    errors: list[ValidationError] = []
    for step in registry:
        errors.extend(_check_theater_signatures(step))
        if step.binding == "bound":
            errors.extend(_check_negative_control(step, nc_registry))
    return errors
