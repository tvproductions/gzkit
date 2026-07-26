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


def _command_fails(command: str, root: Path, *, expected_exit: int) -> int:
    """Exit-style signal: 1 only if the command exits with ``expected_exit`` in ``root``.

    ``expected_exit`` is the exit code the tool documents for "I ran, and the
    subject violated the claim". Any OTHER non-zero exit means the tool did not
    reach that verdict — it failed to launch (``returncode -1``), bailed on
    configuration, or crashed. Scoring those as "caught" is what let a negative
    control stay green after its enforcement was deleted entirely: the claim's
    §5 clause (c) obligation is to assert the production path fails *for the
    reason the claim names*, and a bare ``not success`` cannot express that
    (GHI #699 generator #1).
    """
    from gzkit.quality import run_command  # noqa: PLC0415

    return 1 if run_command(command, cwd=root).returncode == expected_exit else 0


def _gz_command_fails(
    verb: tuple[str, ...],
    root: Path,
    *,
    expected_exit: int,
    expect_output: str | None = None,
) -> int:
    """``_command_fails`` for a gz-owned verb, pinned to the WORKING TREE.

    ``uv run gz <verb>`` resolves ``gz`` from PATH. Under a bare (non-``uv run``)
    invocation that is the installed wheel — observed at ``~/.local/bin/gz`` —
    so gutting ``src/gzkit/`` leaves every gz-backed negative control green. §5
    clause (b) requires the control run the real path in its **production**
    configuration, and the wheel is not the tree under test (GHI #699
    generator #5).

    ``sys.executable -m gzkit`` re-enters the interpreter that already imported
    this module, so the code under test is definitionally the working tree.
    Argv is passed as a sequence — never a shell string — per
    `.claude/rules/cross-platform.md`.

    ``expect_output`` is required wherever the CLI cannot express the difference in
    its exit code. ``GzCliError`` ("gzkit not initialized"), an uncaught exception,
    and a genuine audit finding ALL exit 1 (``core/exceptions.py`` default, mapped in
    ``cli/helpers/exit_codes.py``, plus the generic handler in ``cli/main.py``), so on
    a gz verb ``expected_exit`` alone cannot discriminate. The output substring is the
    only channel that can.
    """
    import sys  # noqa: PLC0415

    return _command_fails_argv(
        [sys.executable, "-m", "gzkit", *verb],
        root,
        expected_exit=expected_exit,
        expect_output=expect_output,
    )


def _command_fails_argv(
    argv: list[str],
    root: Path,
    *,
    expected_exit: int,
    expect_output: str | None = None,
) -> int:
    """Sequence-form companion to ``_command_fails`` (same discrimination contract)."""
    from gzkit.quality import run_command  # noqa: PLC0415

    result = run_command(argv, cwd=root)
    if result.returncode != expected_exit:
        return 0
    if expect_output is not None and expect_output not in (result.stdout + result.stderr):
        return 0
    return 1


# --- subprocess-backed entrypoints -----------------------------------------


def _ep_lint(root: Path) -> int:
    return _command_fails("uv run ruff check .", root, expected_exit=1)


def _ep_format(root: Path) -> int:
    return _command_fails("uv run ruff format --check .", root, expected_exit=1)


def _ep_typecheck(root: Path) -> int:
    return _command_fails("uv run ty check .", root, expected_exit=1)


def _ep_test(root: Path) -> int:
    return _command_fails("uv run -m unittest discover tests", root, expected_exit=1)


def _ep_behave(root: Path) -> int:
    """Run behave from THIS interpreter, so the installed behave is the one used.

    ``uv run -m behave`` in a scratch dir resolves an ephemeral environment with no
    behave at all, exiting 1 on ``ModuleNotFoundError`` — a launch failure scored
    as a caught violation (GHI #699).
    """
    import sys  # noqa: PLC0415

    return _command_fails_argv(
        [sys.executable, "-m", "behave"],
        root,
        expected_exit=1,
        expect_output="planted negative-control failure",
    )


def _ep_skill_audit(root: Path) -> int:
    return _gz_command_fails(
        ("skill", "audit"),
        root,
        expected_exit=1,
        expect_output="SKA-REQUIRED-FIELD-MISSING",
    )


def _ep_parity_check(root: Path) -> int:
    return _gz_command_fails(
        ("parity", "check"),
        root,
        expected_exit=1,
        expect_output="required parity surface missing",
    )


def _ep_readiness_audit(root: Path) -> int:
    """Require EXACTLY ONE required-surface failure, naming the planted omission.

    Every other gz-backed control can pin a distinctive message, but readiness
    fails every check identically on an empty project — the issue string for a
    missing file and for a file lacking its markers is the same literal. So a
    substring match cannot separate "one planted omission" from "nothing exists",
    and the discriminator has to be the COUNT (GHI #699).

    Reads `--json` rather than the rendered table: grading a control on table
    geometry would be the `shape-graded-not-substance` signature this tree's own
    theater scanner names.
    """
    import json  # noqa: PLC0415
    import sys  # noqa: PLC0415

    from gzkit.quality import run_command  # noqa: PLC0415

    result = run_command([sys.executable, "-m", "gzkit", "readiness", "audit", "--json"], cwd=root)
    if result.returncode != 1:
        return 0
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        return 0
    failures = report.get("required_failures") or []
    if len(failures) != 1:
        return 0
    return 1 if failures[0].get("path") == "CLAUDE.md" else 0


def _ep_cli_audit(root: Path) -> int:
    return _gz_command_fails(
        ("cli", "audit"),
        root,
        expected_exit=1,
        expect_output="expected heading `# gz demo`",
    )


def _ep_preflight(root: Path) -> int:
    return _gz_command_fails(
        ("preflight",),
        root,
        expected_exit=1,
        expect_output="OBPI-0.0.1-01-demo",
    )


# --- validator-backed entrypoints ------------------------------------------


def _ep_unscoped_rules(root: Path) -> int:
    from gzkit.validators.unscoped_rules import run_unscoped_rules  # noqa: PLC0415

    return 1 if run_unscoped_rules(root).exit_code == 3 else 0


def _ep_adr_status_freshness(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.taxonomy import audit_adr_status_fresh  # noqa: PLC0415

    return audit_adr_status_fresh(root)


def _ep_obpi_lifecycle_coherence(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.taxonomy import (  # noqa: PLC0415
        audit_obpi_lifecycle_coherence,
    )

    return audit_obpi_lifecycle_coherence(root)


def _ep_adversarial_validation(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.adversarial_validation import (  # noqa: PLC0415
        audit_adversarial_validation,
    )

    return audit_adversarial_validation(root)


def _ep_red_parity(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.red_parity import audit_red_parity  # noqa: PLC0415

    return audit_red_parity(root)


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


def _ep_brief_structure(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.brief_structure import (  # noqa: PLC0415
        validate_brief_structure,
    )

    return validate_brief_structure(root)


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


def _ep_handoff_documents_populated(root: Path) -> list[str]:
    """Production path for the present-but-empty handoff invariant (GHI #698).

    Returns the audit's blocking finding lines (not a bare ``int``) so the
    control can pin the specific ``Empty required section`` reason via
    ``expect`` — an ``int`` return collapses to ``bool`` and ``_render_findings``
    yields ``""``, which no ``expect`` can match.
    """
    from gzkit.quality import run_handoff_document_audit  # noqa: PLC0415

    result = run_handoff_document_audit(root)
    if result.success:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


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


def _ep_enforcement_floor(records: list) -> int:
    """NC entrypoint for enforcement-floor: meta-validator must detect FACADE claims.

    Returns facade_count + test_bug_count (non-zero = caught the FACADE = PASS for NC).
    If run_meta_validator is gutted to skip FACADE detection, returns 0 = FACADE for NC.
    """
    from gzkit.enforcement import run_meta_validator  # noqa: PLC0415

    result = run_meta_validator(registry=records, root=None)
    return result.facade_count + result.test_bug_count


def _ep_theater_signature_scan(root: Path) -> list:
    """NC entrypoint for theater-signature-scan: the analyzer must catch the planted facade.

    Runs the production static analyzer against the planted ``src/gzkit/planted.py``
    violation; a non-empty findings list = caught = PASS. If the detector is gutted, it
    returns [] = FACADE.
    """
    from gzkit.governance.trust_audits.theater_signature_scan import (  # noqa: PLC0415
        scan_source_for_signatures,
    )

    planted = root / "src" / "gzkit" / "planted.py"
    return scan_source_for_signatures(planted, rel="src/gzkit/planted.py")
