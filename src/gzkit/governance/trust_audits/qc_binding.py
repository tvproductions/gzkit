"""QC-binding behavioral audit (ADR-0.0.73 / OBPI-0.0.73-02).

Detects theater in bound QC steps via two channels:
1. Seven static theater-signature checks (calibrated on ADR-0.0.37 facade)
2. Negative-control execution via the shared meta-validator engine: a bound step
   whose enforcement claim does not fail its own un-forced negative control is theater.

ADR-0.0.74 (OBPI-0.0.74-16) lifted the run-NC-in-production engine into
``gzkit.enforcement`` so qc_binding and the meta-validator runner share ONE engine
(Boundary Invariant #6). The qc negative controls are registered through the single
``@enforces`` primitive in ``_qc_negative_controls``; ``audit_qc_binding`` discovers each
bound step's claim from the enforcement registry and runs it via ``_run_single_claim``.
There is no ``_NEGATIVE_CONTROL_DEBT`` escape (Boundary Invariant #8 — strict no-debt).

Usage::

    from gzkit.governance.trust_audits.qc_binding import audit_qc_binding
    errors = audit_qc_binding(project_root)
    # Non-empty → exit 3; empty → exit 0
"""

from __future__ import annotations

from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.enforcement import (
    EnforcementClaimRecord,
    _run_single_claim,
    create_fixture_tempdir,
    enforces,
    get_enforcement_registry,
)
from gzkit.qc_binding import QCStep

# Import the qc negative-control fixtures for their @enforces registration side effect
# (the 36 claims register at import time). noqa: F401 — imported for effect, not name.
from . import _qc_negative_controls  # noqa: F401

# ---------------------------------------------------------------------------
# Seven theater signatures calibrated on the ADR-0.0.37 facade
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
# Main audit entry point
# ---------------------------------------------------------------------------


def audit_qc_binding(
    project_root: Path,
    *,
    nc_registry: dict[str, EnforcementClaimRecord] | None = None,
) -> list[ValidationError]:
    """Behavioral QC-binding audit (ADR-0.0.73 / OBPI-0.0.73-02; engine lifted OBPI-0.0.74-16).

    Two channels (ADR-0.0.73):
    - Channel 1 (static, GHI #657): the per-step ``theater_flags`` renderer PLUS a
      live source scan of the trust_audits validator tree
      (``theater_signature_scan``) for the three structurally-decidable theater
      signatures. ``project_root`` anchors that scan.
    - Channel 2 (behavioral): for ``bound`` steps, looks up the step's enforcement
      claim in the shared ``@enforces`` registry and runs it via the shared
      ``_run_single_claim`` engine. A bound step whose claim is missing, or whose
      un-forced negative control does not fail (outcome != PASS), is theater.

    ``nc_registry`` overrides the discovered enforcement registry with an explicit
    ``claim_id -> EnforcementClaimRecord`` map (test-isolation path), preserving the
    parameter's prior purpose.

    Returns a list of ValidationErrors; non-empty → caller should exit 3.
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

    if nc_registry is not None:
        records = dict(nc_registry)
    else:
        _ensure_qc_claims_registered()
        records = {r.claim_id: r for r in get_enforcement_registry()}

    errors: list[ValidationError] = []
    for step in registry:
        errors.extend(_check_theater_signatures(step))
        if step.binding != "bound":
            continue
        record = records.get(step.id)
        if record is None:
            errors.append(
                _err(
                    step.name,
                    f"Green-by-emptiness: bound step '{step.id}' has no @enforces "
                    "registration. ADR-0.0.74 (Boundary Invariant #6/#8) forbids a bound QC "
                    "step that cannot fail its own un-forced negative control — it verifies "
                    f"nothing. Register one via @enforces('{step.id}', fixture, entrypoint) in "
                    "_qc_negative_controls; there is no _NEGATIVE_CONTROL_DEBT escape.",
                )
            )
            continue
        result = _run_single_claim(record)
        if result.outcome != "PASS":
            errors.append(
                _err(
                    step.name,
                    f"Hollow step '{step.id}': {result.message}",
                )
            )
    errors.extend(_scan_validator_source(project_root))
    return errors


def _scan_validator_source(project_root: Path) -> list[ValidationError]:
    """Channel 1 (live): scan the trust_audits validator tree for theater signatures.

    Fires the static analyzer (GHI #657) on real source — the part of channel 1 that
    the inert ``theater_flags`` self-declaration model never could. Each finding is
    rendered as three-part guardrail-feedback prose (what / why-forbidden / next step)
    per ``.claude/rules/guardrail-feedback-prose.md``.
    """
    from gzkit.governance.trust_audits.theater_signature_scan import (  # noqa: PLC0415
        scan_validator_tree,
    )

    audits_dir = project_root / "src" / "gzkit" / "governance" / "trust_audits"
    if not audits_dir.is_dir():
        return []
    findings = scan_validator_tree(project_root, audits_dir.rglob("*.py"))
    return [
        ValidationError(
            type="qc_binding",
            artifact=f"{finding.file_path}:{finding.line_number}",
            message=(
                f"Theater signature '{finding.signature}' in {finding.function_name!r}: "
                f"{finding.evidence}. ADR-0.0.73 forbids a QC validator that enacts a known "
                "facade shape. Replace it with a check that fails for the right reason; "
                "verify with `uv run gz validate --qc-binding`."
            ),
        )
        for finding in findings
    ]


# ---------------------------------------------------------------------------
# Negative control for the qc-binding step itself (the step this ADR owns)
# ---------------------------------------------------------------------------


def _build_qc_binding_violation() -> Path:
    """Plant a real ``copy-vs-self`` facade in the validator tree this audit scans.

    Previously this fixture returned a ``QCStep`` self-declaring
    ``theater_flags=["copy-vs-self"]`` and the entrypoint was
    ``_check_theater_signatures`` — which merely tests membership of that literal in
    ``THEATER_SIGNATURES``, two literals in this same module. Both of the audit's
    real channels (the behavioral NC-execution loop and the live source scan) could
    be deleted outright and the control stayed green, on the one claim that
    certifies the theater detector itself (GHI #699).

    ADR-0.0.73's own pre-mortem named this outcome — *"detection stayed
    declarative... Mitigation baked in: detection is behavioral, not static-shape
    matching."* The fixture now plants the facade in real source layout so the AST
    analyzer must actually catch it; the tautological assertion is exactly the
    ``copy-vs-self`` shape ``THEATER_SIGNATURES`` names, planted rather than
    declared.
    """
    root = create_fixture_tempdir(prefix="gzkit-qc-nc-qc-binding-")
    planted = root / "src" / "gzkit" / "governance" / "trust_audits" / "planted_facade.py"
    planted.parent.mkdir(parents=True, exist_ok=True)
    planted.write_text(
        "def check_rendition(candidate):\n"
        "    # Tautological: the assertion can never fail.\n"
        "    return candidate == candidate\n",
        encoding="utf-8",
    )
    return root


def _qc_binding_registration_marker() -> None:
    """Inert carrier for the qc-binding @enforces registration."""


def register_qc_binding_claim() -> None:
    """Register the qc-binding self-NC claim via @enforces (idempotent)."""
    if any(r.claim_id == "qc-binding" for r in get_enforcement_registry()):
        return
    enforces(
        "qc-binding",
        _build_qc_binding_violation,
        _scan_validator_source,
        "Theater signature 'copy-vs-self'",
    )(_qc_binding_registration_marker)


def _ensure_qc_claims_registered() -> None:
    """(Re)register every qc enforcement claim — robust against registry resets.

    Idempotent: re-callable after ``reset_enforcement_registry()`` so the production
    claims survive test resets. Registers every qc NC and the qc-binding self-NC.
    """
    _qc_negative_controls.register_qc_negative_controls()
    register_qc_binding_claim()


_ensure_qc_claims_registered()
