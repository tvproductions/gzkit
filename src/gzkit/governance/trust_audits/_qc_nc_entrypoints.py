"""Production-callable entrypoints for the qc negative controls (OBPI-0.0.74-16).

Each ``_ep_<claim>`` is the PRODUCTION enforcement path the meta-validator runner
invokes against the violation built by the paired ``_build_<claim>`` fixture in
``_qc_negative_controls.py``. The runner (``enforcement._run_single_claim``) calls
``entrypoint(fixture())`` and decides catch/no-catch from the ONE uniform signal
``bool(result)`` — a non-empty ``list[ValidationError]`` or a non-zero exit-style int
means the violation was caught (PASS); a falsy result means the entrypoint did NOT
catch it (FACADE).

These are direct, named module-level callables resolving into ``src/gzkit/**`` — never
``lambda`` or ``functools.partial`` pre-binding a forcing kwarg (ADR-0.0.74 Boundary
Invariant #7). Each runs the real validator against whatever the fixture built; a clean
fixture would make the entrypoint pass, surfacing the claim as a FACADE.

Split out of ``_qc_negative_controls.py`` for module-size discipline (<=600 lines,
`.claude/rules/pythonic.md`).
"""

from __future__ import annotations

from pathlib import Path

from gzkit.core.validation_rules import ValidationError


def _command_fails(command: str, root: Path) -> int:
    """Exit-style signal: 1 if the command fails in ``root`` (caught), else 0."""
    from gzkit.quality import run_command  # noqa: PLC0415

    return 1 if not run_command(command, cwd=root).success else 0


# --- subprocess-backed entrypoints -----------------------------------------


def _ep_lint(root: Path) -> int:
    return _command_fails("uv run ruff check .", root)


def _ep_format(root: Path) -> int:
    return _command_fails("uv run ruff format --check .", root)


def _ep_typecheck(root: Path) -> int:
    return _command_fails("uv run ty check .", root)


def _ep_test(root: Path) -> int:
    return _command_fails("uv run -m unittest discover tests", root)


def _ep_behave(root: Path) -> int:
    return _command_fails("uv run -m behave", root)


def _ep_skill_audit(root: Path) -> int:
    return _command_fails("uv run gz skill audit", root)


def _ep_parity_check(root: Path) -> int:
    return _command_fails("uv run gz parity check", root)


def _ep_readiness_audit(root: Path) -> int:
    return _command_fails("uv run gz readiness audit", root)


def _ep_cli_audit(root: Path) -> int:
    return _command_fails("uv run gz cli audit", root)


def _ep_preflight(root: Path) -> int:
    return _command_fails("uv run gz preflight", root)


# --- validator-backed entrypoints ------------------------------------------


def _ep_unscoped_rules(root: Path) -> int:
    from gzkit.validators.unscoped_rules import run_unscoped_rules  # noqa: PLC0415

    return 1 if run_unscoped_rules(root).exit_code == 3 else 0


def _ep_adr_status_freshness(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.taxonomy import audit_adr_status_fresh  # noqa: PLC0415

    return audit_adr_status_fresh(root)


def _ep_rendition_freshness(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.rendition_freshness import (  # noqa: PLC0415
        validate_rendition_freshness,
    )

    return validate_rendition_freshness(root)


def _ep_rendition_floor_coherence(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.rendition_floor_coherence import (  # noqa: PLC0415
        validate_rendition_floor_coherence,
    )

    return validate_rendition_floor_coherence(root)


def _ep_invariant_coherence(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.invariant_coherence import (  # noqa: PLC0415
        validate_invariant_coherence,
    )

    return validate_invariant_coherence(root)


def _ep_session_green_gate(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.session_green_gate import (  # noqa: PLC0415
        audit_session_green_gate,
    )

    return audit_session_green_gate(root)


def _ep_closeout_proof(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.closeout_proof import (  # noqa: PLC0415
        validate_closeout_proof,
    )

    return validate_closeout_proof(root, adr_id="ADR-0.0.99")


def _ep_kind_invariance(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.kind_invariance import audit_kind_invariance  # noqa: PLC0415

    return audit_kind_invariance(root)


def _ep_interview_transcripts(root: Path) -> list[ValidationError]:
    from gzkit.commands.validate_briefs import _validate_interviews  # noqa: PLC0415

    return _validate_interviews(root)


def _ep_receipt_shape(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.receipt_shape import audit_receipt_shape  # noqa: PLC0415

    return audit_receipt_shape(root)


def _ep_orientation_freshness(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.orientation import (  # noqa: PLC0415
        audit_orientation_freshness,
    )

    return audit_orientation_freshness(root)


def _ep_insights_shape(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.insights import audit_insights_shape  # noqa: PLC0415

    return audit_insights_shape(root)


def _ep_instructions_files_budget(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.instructions_files_budget import (  # noqa: PLC0415
        audit_instructions_files_budget,
    )

    return audit_instructions_files_budget(root)


def _ep_agents_md_map_conformance(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.agents_md_map_conformance import (  # noqa: PLC0415
        audit_agents_md_map_conformance,
    )

    return audit_agents_md_map_conformance(root)


def _ep_complexity_doctrine_links(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.complexity_doctrine_links import (  # noqa: PLC0415
        validate_complexity_doctrine_links,
    )

    return validate_complexity_doctrine_links(root)


def _ep_complexity_thresholds(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.complexity_thresholds import (  # noqa: PLC0415
        validate_complexity_thresholds,
    )

    return validate_complexity_thresholds(root)


def _ep_req_kind_discipline(root: Path) -> list[ValidationError]:
    from gzkit.commands.validate_req_kind import _validate_req_kind_discipline  # noqa: PLC0415

    return _validate_req_kind_discipline(root)


def _ep_tautological_test_audit(root: Path) -> list[ValidationError]:
    from gzkit.tautological_tests import audit_drift  # noqa: PLC0415

    return audit_drift(root)


def _ep_task_envelope_coherence(root: Path) -> list[ValidationError]:
    from gzkit.commands.validate_task_envelope import (  # noqa: PLC0415
        _validate_task_envelope_coherence,
    )

    return _validate_task_envelope_coherence(root)


def _ep_lock_handoff_coupling(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.lock_handoff_coupling import (  # noqa: PLC0415
        validate_lock_handoff_coupling,
    )

    return validate_lock_handoff_coupling(root)


def _ep_handoff_documents(root: Path) -> int:
    from gzkit.quality import run_handoff_document_audit  # noqa: PLC0415

    return 1 if not run_handoff_document_audit(root).success else 0


def _ep_surface_fidelity(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits import validate_surface_fidelity  # noqa: PLC0415

    return validate_surface_fidelity(root)


def _ep_line_endings(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.cross_platform import audit_line_endings  # noqa: PLC0415

    return audit_line_endings(root)


def _ep_dispatch_attestation(root: Path) -> int:
    from gzkit.quality import run_dispatch_attestation_audit  # noqa: PLC0415

    return 1 if not run_dispatch_attestation_audit(root).success else 0


def _ep_fidelity_presence(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.fidelity_presence import (  # noqa: PLC0415
        audit_fidelity_presence,
    )

    return audit_fidelity_presence(root, grandfather=frozenset())


def _ep_waiver_ratchet(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.waiver_ratchet import audit_waiver_ratchet  # noqa: PLC0415

    return audit_waiver_ratchet(root)
