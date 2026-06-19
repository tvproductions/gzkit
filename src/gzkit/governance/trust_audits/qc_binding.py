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
from gzkit.governance.trust_audits._qc_negative_controls import _PRODUCTION_NEGATIVE_CONTROLS
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
    "shape-graded-not-substance",
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
    "shape-graded-not-substance": (
        "Step renders an authoritative truth-score from prose SHAPE or KEYWORD "
        "presence rather than decision substance (a score satisfiable by keyword "
        "or format presence alone grades shape, not truth — GHI #624)"
    ),
}

# ---------------------------------------------------------------------------
# Negative-control registry
# ---------------------------------------------------------------------------

# Module-level NC registry: step_id → callable returning int (exit code).
# A callable returning 0 means the step PASSED its NC → hollow → theater.
# A callable returning non-zero means the step FAILED its NC → bound → genuine.
# Populated by register_negative_control(); the qc-binding step (the step this
# ADR owns) is wired at the bottom of this module.
_NEGATIVE_CONTROLS: dict[str, Callable[[], int]] = {}

# Acknowledged negative-control coverage debt (ADR-0.0.73, OBPI-06).
# These bound steps have no negative control yet. OBPI-0.0.73-02's checklist
# promised "each step ships a fixture it must fail on"; its code deferred that
# wiring, leaving the behavioral channel inert. Rather than let the audit pass
# green-by-emptiness (an unwired bound step verifies nothing — the very
# 'empty-input-passes' theater signature), every unwired bound step is listed
# here EXPLICITLY so the gap is visible and tracked. The audit FAILS on every
# entry in this set: acknowledged debt is not green evidence. This keeps the
# project red until the owed negative controls are authored, while preserving a
# separate message for a NEW bound step that is neither wired nor acknowledged.
# Authoring honest NCs for these is tracked OBPI-02 correction work.
_NEGATIVE_CONTROL_DEBT: frozenset[str] = frozenset({})


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

    The canonical signatures are the six ADR-0.0.37 facade signatures plus the
    seventh ``shape-graded-not-substance`` (GHI #624, OBPI-0.0.73-07); any flag
    from ``THEATER_SIGNATURES`` found in step.theater_flags produces an error.
    Unknown flags are noted but not treated as canonical.
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

    active_nc = nc_registry if nc_registry is not None else _NEGATIVE_CONTROLS
    errors: list[ValidationError] = []
    for step in registry:
        errors.extend(_check_theater_signatures(step))
        if step.binding == "bound":
            if step.id in active_nc:
                errors.extend(_check_negative_control(step, active_nc))
            elif step.id in _NEGATIVE_CONTROL_DEBT:
                errors.append(
                    _err(
                        step.name,
                        f"Negative-control debt: bound step '{step.id}' has no registered "
                        "negative control. This debt is acknowledged, but acknowledged "
                        "debt is not passing evidence; author a genuine fixture via "
                        f"register_negative_control('{step.id}', ...) and remove the id "
                        "from _NEGATIVE_CONTROL_DEBT.",
                    )
                )
            else:
                errors.append(
                    _err(
                        step.name,
                        f"Green-by-emptiness: bound step '{step.id}' has no registered "
                        "negative control and is not in the acknowledged "
                        "_NEGATIVE_CONTROL_DEBT set. ADR-0.0.73 forbids a bound QC step "
                        "that cannot fail its own negative control — it verifies nothing "
                        "(the 'empty-input-passes' theater signature). Register one via "
                        f"register_negative_control('{step.id}', ...), or if its NC "
                        "authoring is tracked correction work, add it to "
                        "_NEGATIVE_CONTROL_DEBT.",
                    )
                )
    return errors


# ---------------------------------------------------------------------------
# Negative control for the qc-binding step itself (the step this ADR owns)
# ---------------------------------------------------------------------------


def _qc_binding_negative_control() -> int:
    """Genuine negative control for the ``qc-binding`` step.

    Feeds the theater detector a step that IS theater (it carries a canonical
    signature) and reports whether the detector fired, as an exit-style int:
    ``0`` means the detector MISSED the planted theater (hollow → the step would
    be flagged), non-zero means it caught it (genuinely bound). If
    ``_check_theater_signatures`` were ever gutted so it stopped flagging known
    signatures, this control returns 0 and the ``qc-binding`` step is itself
    flagged hollow — a check that cannot fail for the right reason fails here.
    """
    planted = QCStep(
        id="nc-planted-theater",
        name="NC Planted Theater",
        kind="audit",
        subject="src/",
        binding="bound",
        wired_into=["gz check"],
        theater_flags=["copy-vs-self"],
        enforcement_locus="python_function",
    )
    return 1 if _check_theater_signatures(planted) else 0


register_negative_control("qc-binding", _qc_binding_negative_control)

for _step_id, _negative_control in _PRODUCTION_NEGATIVE_CONTROLS.items():
    register_negative_control(_step_id, _negative_control)
