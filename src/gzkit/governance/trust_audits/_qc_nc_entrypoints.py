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


#: Child-environment pins making captured NC output machine-comparable (GHI #793).
#:
#: ``expect_output`` compares a literal against captured stdout, and Rich's
#: highlighter rewrites that text — its number rule wrapped SGR codes INSIDE an
#: identifier (``OBPI-\x1b[1;36m0.0\x1b[0m.…``), so the literal no longer occurred
#: and the control reported FACADE against a check that had caught its violation.
#:
#: ``capture_output=True`` means the child never owns a TTY, so Rich's own
#: is-a-terminal test would normally disable colour by itself. ``FORCE_COLOR``
#: overrides exactly that test, which is why inheriting the parent environment is
#: not safe: the verdict becomes a function of the operator's terminal, green in
#: CI and red on a developer machine. Both pins are needed and neither is
#: redundant — ``FORCE_COLOR`` is honoured for ANY value including the empty
#: string, so it must be UNSET rather than blanked, and ``NO_COLOR`` then states
#: the intent positively for other renderers.
_NC_PRESENTATION_PINS = {"FORCE_COLOR": None, "NO_COLOR": "1"}


def _command_fails_argv(
    argv: list[str],
    root: Path,
    *,
    expected_exit: int,
    expect_output: str | None = None,
) -> int:
    """Sequence-form companion to ``_command_fails`` (same discrimination contract).

    The child runs with colour pinned OFF (``_NC_PRESENTATION_PINS``) so the
    ``expect_output`` channel compares against the text the CLI emits, not
    against a presentation-decorated rendering of it. Pinned here rather than at
    each fixture because the exposure belongs to the channel: only one of the six
    ``expect_output`` controls carries a digit-bearing substring today, and the
    other five survive by phrasing rather than by construction (GHI #793).
    """
    from gzkit.quality import run_command  # noqa: PLC0415

    result = run_command(argv, cwd=root, env_overrides=_NC_PRESENTATION_PINS)
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


def _ep_module_size(root: Path) -> int:
    """Run the production module-size gate script against the fixture root.

    The script resolves its own project root as ``Path.cwd()``, so pointing the
    subprocess cwd at the fixture is what aims it at the planted violation while
    the script itself stays the real one — never a copy. Resolution goes through
    ``_resolve_chore_dir`` (project-first, package-fallback) rather than a
    literal path, so the control follows the chore wherever it resolves.

    ``expect_output`` is required here for the same reason it is on gz verbs: the
    script exits 3 for a policy breach, but a missing thresholds table also
    raises ``SystemExit`` with a message, and exit code alone cannot tell the
    verdict from the bail-out.
    """
    import sys  # noqa: PLC0415

    from gzkit.commands.chores import _resolve_chore_dir  # noqa: PLC0415

    script = _resolve_chore_dir("module-sloc-cap-radon").path / "check_module_size.py"
    return _command_fails_argv(
        [sys.executable, str(script)],
        root,
        expected_exit=3,
        expect_output="not grandfathered",
    )


def _ep_test(root: Path) -> int:
    return _command_fails("uv run -m unittest discover tests", root, expected_exit=1)


def _ep_docs_build(root: Path) -> int:
    """Drive the production ``run_mkdocs`` path and require the RIGHT failure.

    A bare exit-1 check would be satisfied by mkdocs failing to launch at all,
    which is the mis-scoring GHI #699 named on the behave control. Both markers
    are asserted instead: mkdocs must name the unresolvable nav target (proving
    it parsed the config and walked the nav) AND report the strict-mode abort
    (proving ``--strict`` is what promoted the warning to a failure). Drop
    ``--strict`` from the command and this control goes red, which is the point.
    """
    from gzkit.quality import run_mkdocs  # noqa: PLC0415 — production path under test

    result = run_mkdocs(root)
    if result.success or result.returncode != 1:
        return 0
    output = f"{result.stdout}\n{result.stderr}"
    return int("absent-page.md" in output and "strict mode" in output)


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


def _ep_python_version_pins(root: Path) -> list[ValidationError]:
    """Run the production interpreter-pin audit against the planted tree."""
    from gzkit.governance.trust_audits.python_version_pins import (  # noqa: PLC0415
        audit_python_version_pins,
    )

    return audit_python_version_pins(root)


def _ep_wheel_path_literals(root: Path) -> list[ValidationError]:
    """Return findings for the WHEEL-SHIPPED doc only.

    The fixture plants the same literal in an unshipped ``docs/`` file. An
    unfiltered control would pass on a scan that ignored the include block
    entirely, which is the one property this control exists to witness.
    """
    from gzkit.governance.trust_audits.wheel_path_literals import (  # noqa: PLC0415
        audit_wheel_path_literals,
    )

    return [e for e in audit_wheel_path_literals(root) if "SKILL.md" in e.artifact]


def _ep_validate_default_scopes(root: Path) -> list[ValidationError]:
    """Run the whole default `gz validate` tier, as the bare invocation does."""
    from gzkit.commands.validate_cmd import _collect_errors  # noqa: PLC0415

    return _collect_errors(root, {})


def _ep_status_writer_coverage(root: Path) -> list[ValidationError]:
    """Return ONLY the planted-bypass findings, never the register's own noise.

    The audit also reports inert register entries, and in a synthetic tree
    EVERY real entry is inert — so an unfiltered control would go green on
    findings that have nothing to do with the bypass it plants. A control that
    can pass on the wrong evidence is not a control.
    """
    from gzkit.governance.trust_audits.status_writer_coverage import (  # noqa: PLC0415
        audit_status_writer_coverage,
    )

    return [e for e in audit_status_writer_coverage(root) if "rogue_writer.py" in e.artifact]


def _ep_transcribed_adr_counts(root: Path) -> list[ValidationError]:
    """Return findings for the planted LIVE count only.

    Filtered to the Queue line so the control cannot pass on the historical
    line it also plants — the whole point of planting both is that flagging the
    archive is a failure, not a success.

    Keyed on the planted line's CONTENT (`Draft`, which only the live claim
    carries), never its line number: an offset filter silently empties the
    moment the fixture gains a line, and an empty filter is a control that
    always passes.
    """
    from gzkit.governance.trust_audits.transcribed_counts import (  # noqa: PLC0415
        audit_transcribed_counts,
    )

    return [e for e in audit_transcribed_counts(root) if "Draft" in e.message]


def _ep_adr_status_freshness(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.taxonomy import audit_adr_status_fresh  # noqa: PLC0415

    return audit_adr_status_fresh(root)


def _ep_pool_interview_schema(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.taxonomy import (  # noqa: PLC0415
        audit_pool_interview_schema,
    )

    return audit_pool_interview_schema(root)


def _ep_advisory_scorecard(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.release import audit_advisory_scorecard  # noqa: PLC0415

    return audit_advisory_scorecard(root)


def _ep_adr_taxonomy(root: Path) -> list[ValidationError]:
    from gzkit.governance import trust_audits  # noqa: PLC0415
    from gzkit.governance.trust_audits.taxonomy import (  # noqa: PLC0415
        audit_foundation_closure,
    )

    return trust_audits.audit_adr_taxonomy(root) + audit_foundation_closure(root)


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


def _ep_producer_field_parity(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.events import audit_producer_fields  # noqa: PLC0415

    return audit_producer_fields(root)


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


def _ep_corpus_retirement_witness(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.corpus_retirement_witness import (  # noqa: PLC0415
        validate_corpus_retirement_witness,
    )

    return validate_corpus_retirement_witness(root)


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


def _ep_persona_witness(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.persona_witness import (  # noqa: PLC0415
        audit_persona_witness,
    )

    return audit_persona_witness(root)


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
    """Run the scope exactly as `gz validate --instructions-files-budget` composes it.

    Both arms, summed, mirroring ``validate_cmd``. The char-budget arm is
    advisory until 1.0 (operator ruling 2026-08-17) and contributes no findings;
    the delivery witness still fail-closes on survival-declaration drift. Calling
    only the budget arm would have made this control structurally unable to fail.
    """
    from gzkit.governance.trust_audits.instructions_files_budget import (  # noqa: PLC0415
        audit_instructions_files_budget,
    )
    from gzkit.governance.trust_audits.surface_delivery_witness import (  # noqa: PLC0415
        audit_surface_delivery_witness,
    )

    return audit_instructions_files_budget(root) + audit_surface_delivery_witness(root)


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


def _ep_lock_exchange_coupling(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.lock_exchange_coupling import (  # noqa: PLC0415
        validate_lock_exchange_coupling,
    )

    return validate_lock_exchange_coupling(root)


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


def _ep_smoke_tier(root: Path) -> int:
    import io  # noqa: PLC0415
    from contextlib import redirect_stdout  # noqa: PLC0415

    from gzkit.commands.smoke_cmd import smoke_gate  # noqa: PLC0415

    # Swallow the gate's recovery prose: this control EXPECTS the failure, and a
    # passing `gz validate --qc-binding` that prints failure-shaped text is the
    # exact confusion GHI #726 closed one tier over.
    with redirect_stdout(io.StringIO()):
        return smoke_gate(root)


def _ep_authorship_policy(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.authorship import audit_authorship  # noqa: PLC0415

    return audit_authorship(root)


def _ep_dispatch_absorption_marker(root: Path) -> int:
    from gzkit.quality import run_dispatch_absorption_marker_audit  # noqa: PLC0415

    return 1 if not run_dispatch_absorption_marker_audit(root).success else 0


def _ep_fidelity_presence(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.fidelity_presence import (  # noqa: PLC0415
        audit_fidelity_presence,
    )

    return audit_fidelity_presence(root, grandfather=frozenset())


def _ep_config_registry(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.config_registry import (  # noqa: PLC0415
        audit_config_registry,
    )

    return audit_config_registry(root)


def _ep_waiver_ratchet(root: Path) -> list[ValidationError]:
    from gzkit.governance.trust_audits.waiver_ratchet import audit_waiver_ratchet  # noqa: PLC0415

    return audit_waiver_ratchet(root)


def _ep_exemption_controls(root: Path) -> list[ValidationError]:
    """Drive the production exemption-control audit against the fixture root.

    ``declarations`` injects a one-claim population so the control fails for
    THIS claim's own reason -- an undeclared claim absent from the disclosed
    list -- rather than incidentally tripping on the live registry's 75
    claims being absent from a bare fixture. The audit function itself is the
    real one, never a copy.
    """
    from gzkit.governance.trust_audits.exemption_controls import (  # noqa: PLC0415
        audit_exemption_controls,
    )

    return audit_exemption_controls(root, declarations={"nc-undeclared-claim": None})


def _ep_gate_callers(root: Path) -> list[ValidationError]:
    """Drive the production uncalled-gate audit against the fixture root.

    ``explicit_scopes=[]`` isolates the chore population the fixture plants; the
    audit function itself is the real one, never a copy.
    """
    from gzkit.governance.trust_audits.gate_callers import audit_gate_callers  # noqa: PLC0415

    return audit_gate_callers(root, gz_check_uncalled_scopes=[])


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
