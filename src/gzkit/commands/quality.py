"""Quality commands (lint, format, test, typecheck, check).

@covers ADR-0.20.0-spec-triangle-sync
@covers OBPI-0.20.0-05-advisory-gate-integration
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from rich.markup import escape

from gzkit.commands.common import console, get_project_root
from gzkit.quality import (
    DriftAdvisoryResult,
    QualityResult,
    run_behave,
    run_format,
    run_lint,
    run_tests,
    run_typecheck,
)

CheckStepRunner = Callable[[pathlib.Path], Any]

# Guard metadata for the MX checkpoint seam (ADR-0.0.74 item 20, OBPI-0.0.74-20).
# Maps each step's display name to (guard_name, emitted_level).  One central
# dict — not per-runner decoration — so the seam in check() is the single
# firing point (REQ-0.0.74-20-01, REQUIREMENT: ONE seam only).
#
# Most steps emit ERROR (grounding band): they block on a real violation and
# demote to advisory under an active marker.  The "Enforcement floor" step is
# the exception — it is the §5 enforcement-claim meta-validator (the floor's
# own teeth), so it emits CRITICAL to pin it: a FACADE must ground in or out of
# the hangar (ADR-0.0.74 BI#3, "never relaxes either engine"; GHI #651).  It is
# pinned by emitted level, not GATE5_INVARIANTS membership — that frozenset is a
# fixed five-member integrity-class set (REQ-0.0.74-03-01) the meta-validator
# runner is not itself a member of.
#
# Fallback: if a step name is absent (future step not yet registered), check()
# derives a kebab-case guard_name from the display name and uses ERROR level.
# THE FALLBACK DOES NOT MAKE AN ENTRY OPTIONAL (GHI #787).  The validator
# reachability ratchet regexes THIS DICT to decide whether a scope is gated, and
# it cannot see a derived name, so a step missing here is filed as reachable from
# nothing while it runs on every commit.  Every step belongs in this dict; see
# _build_check_steps' family-A item 7 and tests/governance/
# test_check_registry_coherence.py, which fails closed on the disagreement.
from gzkit.mx import levels as _mx_levels  # noqa: E402 — after type alias

_STEP_GUARD_META: dict[str, tuple[str, int]] = {
    "Lint": ("lint", _mx_levels.ERROR),
    "Format": ("format", _mx_levels.ERROR),
    "Typecheck": ("typecheck", _mx_levels.ERROR),
    "Test": ("test", _mx_levels.ERROR),
    "Behave": ("behave", _mx_levels.ERROR),
    "Skill audit": ("skill-audit", _mx_levels.ERROR),
    "Parity check": ("parity-check", _mx_levels.ERROR),
    "Readiness audit": ("readiness-audit", _mx_levels.ERROR),
    "CLI audit": ("cli-audit", _mx_levels.ERROR),
    "Unscoped rules": ("unscoped-rules", _mx_levels.ERROR),
    "Python version pins": ("python-version-pins", _mx_levels.ERROR),
    "ADR status freshness": ("adr-status-fresh", _mx_levels.ERROR),
    "Advisory scorecard coverage": ("advisory-scorecard", _mx_levels.ERROR),
    "Adversarial validation": ("adversarial-validation", _mx_levels.ERROR),
    "RED parity": ("red-parity", _mx_levels.ERROR),
    "Producer field parity": ("producer-fields", _mx_levels.ERROR),
    "Rendition freshness": ("rendition-freshness", _mx_levels.ERROR),
    "Rendition floor coherence": ("rendition-floor-coherence", _mx_levels.ERROR),
    "Invariant coherence": ("invariant-coherence", _mx_levels.ERROR),
    "Corpus retirement witness": ("corpus-retirement-witness", _mx_levels.ERROR),
    "Wheel path literals": ("wheel-path-literals", _mx_levels.ERROR),
    "Brief structure": ("brief-structure", _mx_levels.ERROR),
    "OBPI lifecycle coherence": ("obpi-lifecycle-coherence", _mx_levels.ERROR),
    "Session green gate": ("session-green-gate", _mx_levels.ERROR),
    "Closeout proof": ("closeout-proof", _mx_levels.ERROR),
    "Kind invariance": ("kind-invariance", _mx_levels.ERROR),
    "Persona witness": ("persona-witness", _mx_levels.ERROR),
    "Interview transcripts": ("interviews", _mx_levels.ERROR),
    "Pool interview schema": ("pool-interview", _mx_levels.ERROR),
    "Receipt shape": ("receipt-shape", _mx_levels.ERROR),
    "Orientation freshness": ("orientation-freshness", _mx_levels.ERROR),
    "Insights shape": ("insights-shape", _mx_levels.ERROR),
    "Instructions files budget": ("instructions-files-budget", _mx_levels.ERROR),
    "AGENTS.md map conformance": ("agents-md-map-conformance", _mx_levels.ERROR),
    "Complexity-doctrine links": ("complexity-doctrine-links", _mx_levels.ERROR),
    "Complexity-thresholds": ("complexity-thresholds", _mx_levels.ERROR),
    "REQ kind discipline": ("req-kind-discipline", _mx_levels.ERROR),
    "Status writer coverage": ("status-writer-coverage", _mx_levels.ERROR),
    "Transcribed ADR counts": ("transcribed-adr-counts", _mx_levels.ERROR),
    "tautological test audit": ("tautological-test-audit", _mx_levels.ERROR),
    "Task envelope coherence": ("task-envelope-coherence", _mx_levels.ERROR),
    "Lock-exchange coupling": ("lock-exchange-coupling", _mx_levels.ERROR),
    "QC binding": ("qc-binding", _mx_levels.ERROR),
    "Fidelity presence": ("fidelity-presence", _mx_levels.ERROR),
    "Waiver ratchet": ("waiver-ratchet", _mx_levels.ERROR),
    "Config registry": ("config-registry", _mx_levels.ERROR),
    "Gate callers": ("gate-callers", _mx_levels.ERROR),
    "Exemption controls": ("exemption-controls", _mx_levels.ERROR),
    "Handoff documents": ("handoff-documents", _mx_levels.ERROR),
    "Preflight": ("preflight", _mx_levels.ERROR),
    "Surface fidelity": ("surface-fidelity", _mx_levels.ERROR),
    "Line endings": ("line-endings", _mx_levels.ERROR),
    # CRITICAL, not ERROR: enforces `operator-pii` (a GATE5_INVARIANTS member)
    # under a non-floor name, so the floor's string match never sees it. Pinned
    # by LEVEL for the same reason as the validate scope — an email-suffix check
    # is a narrower proxy for the operator-PII prohibition and may not be bound
    # to the floor member (ADR-0.0.74 § Consequences/Negative #7). GHI #852.
    "Authorship policy": ("authorship", _mx_levels.CRITICAL),
    "Smoke tier": ("smoke-tier", _mx_levels.ERROR),
    "Dispatch absorption marker": ("dispatch-absorption-marker", _mx_levels.ERROR),
    # §5 enforcement-claim meta-validator — pinned CRITICAL so a FACADE never
    # demotes to advisory inside the hangar (ADR-0.0.74 BI#3 / §5; GHI #651).
    "Enforcement floor": ("enforcement-floor", _mx_levels.CRITICAL),
    "ADR taxonomy": ("taxonomy", _mx_levels.ERROR),
}


def _apply_mx_seam(
    result: QualityResult,
    guard_name: str,
    emitted_level: int,
    project_root: pathlib.Path,
) -> QualityResult:
    """Apply the MX checkpoint to one step result — the ONE seam for all steps.

    If the step returned returncode=3 (policy breach) and the checkpoint resolves
    its route to advisory (non-grounding), demote: return a passing result so the
    aggregator does not block.  gate5_invariants members always resolve to a
    grounding route regardless of marker state (checkpoint.resolve pins them to
    CRITICAL), so they are never demoted.

    Steps that passed (returncode != 3) pass through unchanged.
    """
    if getattr(result, "returncode", 0) != 3:
        return result
    from gzkit.mx import checkpoint, disposition  # noqa: PLC0415 — lazy: avoids circular risk

    route = checkpoint.resolve(guard_name, emitted_level, project_root)
    if disposition.grounds(route):
        return result
    return QualityResult(
        success=True,
        command=result.command,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=0,
    )


def lint() -> None:
    """Run code linting (ruff + pymarkdown)."""
    project_root = get_project_root()

    console.print("Running linters...")
    result = run_lint(project_root)

    if result.stdout:
        console.print(result.stdout, markup=False)
    if result.stderr:
        console.print(result.stderr, markup=False)

    if result.success:
        console.print("[green]Lint passed.[/green]")
    else:
        console.print("[red]Lint failed.[/red]")
        raise SystemExit(result.returncode)


def format_cmd() -> None:
    """Auto-format code with ruff."""
    project_root = get_project_root()

    console.print("Formatting code...")
    result = run_format(project_root)

    if result.stdout:
        console.print(result.stdout, markup=False)
    if result.stderr:
        console.print(result.stderr, markup=False)

    if result.success:
        console.print("[green]Format complete.[/green]")
    else:
        console.print("[red]Format failed.[/red]")
        raise SystemExit(result.returncode)


def _resolve_obpi_req_ids(project_root, obpi: str) -> set[str]:
    """Return the set of REQ IDs belonging to the given OBPI."""
    from gzkit.triangle import scan_briefs  # noqa: PLC0415

    short = obpi.upper().removeprefix("OBPI-")
    if "-" not in short:
        raise ValueError(f"Expected OBPI-<semver>-<item> form, got {obpi!r}")
    semver, item = short.split("-", 1)
    item = item.split("-", 1)[0]

    briefs = scan_briefs(project_root / "docs" / "design" / "adr")
    return {
        str(b.entity.id)
        for b in briefs
        if b.entity.id.semver == semver and b.entity.id.obpi_item == item
    }


def _test_name_from_record(record, project_root: pathlib.Path) -> str | None:
    """Return a unittest-runnable name for a ``@covers`` linkage record.

    Decorator-form records carry a qualified function name in
    ``source.identifier`` (e.g. ``TestFoo.test_bar``); we return
    ``<module>.<qualname>``. Comment- and docstring-form records carry the
    file path itself as ``source.identifier`` (no function context is
    available from a free-floating ``@covers`` reference), so we return the
    dotted module path alone — unittest will run every test in the module.

    Returns ``None`` when the record has no source location to anchor a
    test name against.
    """
    location = record.source.location
    if location is None:
        return None
    rel_path = pathlib.Path(location).relative_to(project_root)
    module = ".".join(rel_path.with_suffix("").parts)
    if record.source.identifier == location:
        return module
    return f"{module}.{record.source.identifier}"


def _resolve_obpi_test_names(project_root, obpi: str) -> list[str]:
    """Return unittest-runnable names for tests covering this OBPI's REQs.

    Uses the canonical traceability API (``@covers`` scanner + brief REQ
    extraction) to identify which tests cover REQs belonging to the target
    OBPI. Returns unittest-addressable identifiers like
    ``tests.commands.test_validate_frontmatter.TestClass.test_method``.
    """
    from gzkit.traceability import EdgeType, scan_test_tree  # noqa: PLC0415
    from gzkit.triangle import ReqId  # noqa: PLC0415

    req_ids = _resolve_obpi_req_ids(project_root, obpi)
    if not req_ids:
        return []

    records = scan_test_tree(project_root / "tests")

    names: set[str] = set()
    for rec in records:
        if rec.edge_type != EdgeType.COVERS:
            continue
        try:
            target_req = ReqId.parse(rec.target.identifier)
        except ValueError:
            continue
        if str(target_req) not in req_ids:
            continue
        name = _test_name_from_record(rec, project_root)
        if name is not None:
            names.add(name)

    return sorted(names)


def resolve_obpi_behave_tags(project_root, obpi: str) -> list[str]:
    """Return behave scenario tags (``@REQ-...``) covering this OBPI's REQs.

    Delegates feature-file parsing to ``scan_feature_tree`` — the canonical
    scanner used by ``gz covers`` (GHI #185) — so the tag list this
    function emits is always consistent with the coverage graph.

    Public surface (GHI #420): consumed by ``obpi_stages._run_pipeline_verify_stage``
    to scope the Stage 3 behave invocation to this OBPI's REQ tags so
    cross-OBPI rot in unrelated feature files cannot block new OBPIs.
    """
    from gzkit.traceability import EdgeType, scan_feature_tree  # noqa: PLC0415
    from gzkit.triangle import ReqId  # noqa: PLC0415

    req_ids = _resolve_obpi_req_ids(project_root, obpi)
    if not req_ids:
        return []

    records = scan_feature_tree(project_root / "features")
    tags: set[str] = set()
    for rec in records:
        if rec.edge_type != EdgeType.COVERS:
            continue
        try:
            target_req = ReqId.parse(rec.target.identifier)
        except ValueError:
            continue
        if str(target_req) not in req_ids:
            continue
        tags.add(f"@{target_req}")
    return sorted(tags)


def _run_obpi_scoped_unit(project_root, obpi: str) -> None:
    """Run unit tests covering this OBPI's REQs (exit on failure)."""
    names = _resolve_obpi_test_names(project_root, obpi)
    if not names:
        console.print(f"[yellow]No @covers unit tests found for {obpi}.[/yellow]")
        return
    console.print(f"Running {len(names)} unit test(s) scoped to {obpi}...")
    result = subprocess.run(
        ["uv", "run", "-m", "unittest", "-v", *names],
        cwd=project_root,
        check=False,
        encoding="utf-8",
    )
    if result.returncode != 0:
        console.print("[red]OBPI-scoped unit tests failed.[/red]")
        raise SystemExit(result.returncode)
    console.print(f"[green]OBPI-scoped unit tests passed ({len(names)} tests).[/green]")


def _run_obpi_scoped_behave(project_root, obpi: str) -> None:
    """Run behave scenarios tagged with this OBPI's REQs (exit on failure)."""
    tags = resolve_obpi_behave_tags(project_root, obpi)
    if not tags:
        console.print(
            f"[yellow]No @REQ-tagged behave scenarios found for {obpi}. "
            "Tag scenarios with @REQ-X.Y.Z-NN-MM to opt in (GHI #185).[/yellow]"
        )
        return
    console.print(f"Running behave scenarios for {len(tags)} REQ tag(s) of {obpi}...")
    behave_result = run_behave(project_root, tags=tags)
    if behave_result.stdout:
        console.print(behave_result.stdout, markup=False)
    if behave_result.stderr:
        console.print(behave_result.stderr, markup=False)
    if not behave_result.success:
        console.print("[red]OBPI-scoped behave scenarios failed.[/red]")
        raise SystemExit(behave_result.returncode)
    console.print("[green]OBPI-scoped behave scenarios passed.[/green]")


def test(bdd: bool = False, obpi: str | None = None) -> None:
    """Run the test suite; optionally scoped to one OBPI and/or with BDD.

    Scope selection:

    * ``--obpi OBPI-X.Y.Z-NN`` — run unit tests decorated with ``@covers``
      for REQs belonging to that OBPI (~1s typical). Combine with ``--bdd``
      to additionally run behave scenarios tagged with those REQs.
      OBPI pipeline Stage 3 uses this.
    * ``--bdd`` (no ``--obpi``) — full unittest suite + full behave run
      (ADR closeout / Heavy-lane ceremony).
    * default — full unittest suite only (ad-hoc / CI / pre-commit baseline).

    See ``.gzkit/rules/tests.md`` and GHI #185 for the scenario-tag convention.
    """
    project_root = get_project_root()

    if obpi:
        _run_obpi_scoped_unit(project_root, obpi)
        if bdd:
            _run_obpi_scoped_behave(project_root, obpi)
        return

    console.print("Running unit tests...")
    unit = run_tests(project_root)
    if unit.stdout:
        console.print(unit.stdout, markup=False)
    if unit.stderr:
        console.print(unit.stderr, markup=False)
    if not unit.success:
        console.print("[red]Unit tests failed.[/red]")
        raise SystemExit(unit.returncode)
    console.print("[green]Unit tests passed.[/green]")

    if not bdd:
        return

    console.print("Running behave scenarios...")
    behave_result = run_behave(project_root)
    if behave_result.stdout:
        console.print(behave_result.stdout, markup=False)
    if behave_result.stderr:
        console.print(behave_result.stderr, markup=False)
    if behave_result.success:
        console.print("[green]Behave scenarios passed.[/green]")
    else:
        console.print("[red]Behave scenarios failed.[/red]")
        raise SystemExit(behave_result.returncode)


def typecheck() -> None:
    """Run type checking with ty."""
    project_root = get_project_root()

    console.print("Running type checker...")
    result = run_typecheck(project_root)

    if result.stdout:
        console.print(result.stdout, markup=False)
    if result.stderr:
        console.print(result.stderr, markup=False)

    if result.success:
        console.print("[green]Type check passed.[/green]")
    else:
        console.print("[red]Type check failed.[/red]")
        raise SystemExit(result.returncode)


def _build_check_steps() -> list[tuple[str, CheckStepRunner]]:
    """Build the canonical `gz check` steps list.

    Module-scope-importable so tests and external callers can introspect the
    aggregator without invoking the full check pipeline (REQ-0.0.27-07-06).

    ADDING A STEP HERE IS NOT ONE EDIT. The obligations fall in TWO families, and
    conflating them is what let the earlier version of this list read as complete
    while naming only the first (GHI #787).

    A. STEP obligations — a new entry in the returned list. This list is the
       derived source for the ADR-0.0.73 QC registry, so a new entry obliges:

       1. ``_STEP_CLASSIFICATION`` in ``gzkit.qc_binding`` — ``build_qc_registry()``
          raises ``KeyError`` on an unclassified step and every QC test fails at
          once. That is the design working: no step ships unaccounted.
       2. If classified ``bound``, an ``@enforces`` negative control — there is no
          debt escape (ADR-0.0.74 Boundary Invariants #6/#8).
       3. An ``_ep_<claim>`` entrypoint in ``_qc_nc_entrypoints``.
       4. A ``_build_<claim>`` fixture in ``_qc_negative_controls``, which must fail
          for the claim's OWN reason — a fixture that trips a neighbouring check
          proves nothing about this one.

       5. ``QC_CLAIM_EXEMPTS`` in ``_qc_claim_exemptions`` — an ``@enforces``
          control registers with ``exempts=None`` (UNDECLARED) until the claim is
          declared here, and ``gz validate --exemption-controls`` discloses it.
          Declare ``EXEMPTS_NONE`` when the gate carries no project-controllable
          admit path; NEVER silence it via ``exemption_control_grandfather.json``,
          the laundering ADR-0.0.74 Boundary Invariant #8 forbids.
       6. ``data/check_step_concurrency.json`` — every step declares ``read_only``
          or ``writes``; ``tests/governance/test_check_step_concurrency.py`` fails
          closed on an undeclared step. MEASURE it (run the step alone, see what
          it wrote) — never guess, and never default to ``read_only``.
       7. ``_STEP_GUARD_META`` above. REQUIRED, and this list called it optional
          until GHI #787 was reopened — the correction, not a restatement. The
          reachability ratchet
          (``.gzkit/chores/control-surface-validator-reachability``) decides
          whether a scope is gated by regexing THIS DICT out of this module, so a
          step absent from it is filed as reachable from nothing however loudly it
          runs. ``_seam``'s kebab-case fallback keeps the MX seam correct and is
          invisible to that regex, which is exactly why the dict read as a
          refinement. Measured when the correction landed: ``OBPI lifecycle
          coherence`` had run as a step while ``--obpi-lifecycle-coherence`` sat in
          the ungated grandfather as protecting nothing.

    B. SCOPE obligations — when the step wraps a NEW ``gz validate`` scope, which
       is the overwhelmingly common case and the reason family A alone reads as
       the whole duty. Registering the scope additionally obliges:

       8. ``data/check_scope_membership.json`` — add the stem to ``in_check`` AND
          bump ``_counts.registry_scopes`` / ``_counts.in_check``
          (``tests/governance/test_check_scope_parity.py``).
       9. The post-snapshot admission list in
          ``tests/cli/test_validate_registry_parity.py``, WHICH ONE DEPENDS ON THE
          SCOPE'S TIER — this is the only genuinely tier-dependent obligation in
          either family, and having no branch here is what let GHI #787's own fix
          read as complete for default-tier work. DEFAULT tier goes in
          ``_POST_SNAPSHOT_DEFAULT_ADDITIONS``, a TUPLE whose order must match
          registry order; EXPLICIT tier goes in
          ``_POST_SNAPSHOT_EXPLICIT_ADDITIONS``, a frozenset. Add
          ``_POST_SNAPSHOT_OTHER_SCOPES_EXCLUDED`` if the scope owns a solo
          early-return lifecycle. The goldens beside them are measured evidence of
          the pre-collapse truth; a new scope is DECLARED alongside, never appended
          to them.
      10. ``SOLO_ONLY_KWARGS`` and ``_DISPATCH_DEFAULTS`` in
          ``tests/cli/test_validate_solo_scope_refusal.py``, for a solo scope —
          ``_dispatch_early_return_scopes`` takes keyword-only args, so a new one
          breaks every case in that suite until declared.
      11. A per-flag section in ``docs/user/manpages/validate.md``
          (``uv run gz cli audit``, exit 1).

    Promoting a scope to DEFAULT tier also changes its INPUT contract: the QC
    negative controls exercise default scopes against synthetic project roots that
    ship no wheel, so an audit that hard-exits on a missing repository artifact is
    wrong there. Absence is "nothing delivered"; only an UNPARSEABLE artifact stays
    fatal.

    THIS LIST IS A MAP, NOT THE ENFORCEMENT — with one measured exception, below.
    Every surface above carries its own fail-closed witness, and they work: landing
    the ``Gate callers`` step (GHI #785) against the four-item version produced 14
    loud test failures plus a ``cli audit`` refusal, each naming its own remedy.
    The cost of an incomplete map is normally a wasted round-trip, never a false
    green. Nothing grades this docstring for the same reason it has never been
    graded: asserting prose mentions each consumer would grep content rather than
    exercise behavior, the shape ``gz validate --tautological-test-audit`` rejects
    and ``.claude/rules/guardrail-feedback-prose.md`` § Enforcement posture refuses
    on the stated ground that an inferential prose-grader is weaker than a real
    enforcement consumer.

    THE EXCEPTION IS ITEM 7, and it is why that refusal does not settle this whole
    surface. Its witness fires only at pre-commit, i.e. AFTER ``gz check`` has
    returned 0 and the work is believed finished, so for that one item the map was
    load-bearing and it was wrong. ``tests/governance/test_check_registry_coherence.py``
    now asserts that the ratchet's derived gated-set and the live step list agree,
    in both directions. That is NOT prose-grading — both sides are produced by
    executing real code — which is why it is built where the docstring grader was
    refused. Keep the rest of the map accurate by hand; that territory is guarded.

    Enumerated in GHI #744's close ("worth recording for the next person") and
    restated here because that record lived only in a closed issue: wiring the
    module-size step (GHI-less, ``59931cb07``) re-derived the whole list by
    breaking 23 tests. Family B was added under GHI #787, after the next person
    re-derived it again by breaking 14. That fix was itself incomplete and the
    issue reopened 19 days later, when landing one scope (GHI #900, ``22ad1659``)
    cost 8 full ``gz check`` runs at roughly one further registration each; items
    5-7 and the tier branch in item 9 are that correction, and 5-8 renumbered to
    8-11 to seat them. The recurrence at the next count up — 4, then 8, then 11 —
    is the finding, not the specific items. Point of use is the only placement
    that binds.
    """
    from gzkit.quality import (
        run_adr_status_fresh_audit,
        run_adversarial_validation_audit,
        run_advisory_scorecard_audit,
        run_agents_md_map_conformance_audit,
        run_authorship_audit,
        run_brief_structure_audit,
        run_cli_audit,
        run_closeout_proof_audit,
        run_complexity_doctrine_links_audit,
        run_complexity_thresholds_audit,
        run_config_registry_audit,
        run_corpus_retirement_witness_audit,
        run_dispatch_absorption_marker_audit,
        run_enforcement_floor_audit,
        run_exemption_controls_audit,
        run_fidelity_presence_audit,
        run_format_check,
        run_gate_callers_audit,
        run_handoff_document_audit,
        run_insights_shape_audit,
        run_instructions_files_budget_audit,
        run_interviews_audit,
        run_invariant_coherence_audit,
        run_kind_invariance_audit,
        run_line_endings_audit,
        run_lock_exchange_coupling_audit,
        run_mkdocs,
        run_module_size_audit,
        run_obpi_lifecycle_coherence_audit,
        run_orientation_freshness_audit,
        run_parity_check,
        run_persona_witness_audit,
        run_pool_interview_audit,
        run_preflight,
        run_producer_fields_audit,
        run_python_version_pins_audit,
        run_qc_binding_audit,
        run_readiness_audit,
        run_receipt_shape_audit,
        run_red_parity_audit,
        run_rendition_floor_coherence_audit,
        run_rendition_freshness_audit,
        run_req_kind_discipline_audit,
        run_session_green_gate_audit,
        run_skill_audit,
        run_smoke_tier,
        run_status_writer_coverage_audit,
        run_surface_fidelity_audit,
        run_task_envelope_coherence_audit,
        run_tautological_test_audit,
        run_taxonomy_audit,
        run_transcribed_adr_counts_audit,
        run_unscoped_rules_audit,
        run_validate_default_scopes,
        run_waiver_ratchet_audit,
        run_wheel_path_literals_audit,
    )

    return [
        ("Lint", run_lint),
        ("Format", run_format_check),
        ("Typecheck", run_typecheck),
        ("Module size", run_module_size_audit),
        ("Test", run_tests),
        ("Behave", run_behave),
        ("Docs build", run_mkdocs),
        ("Validate default scopes", run_validate_default_scopes),
        ("Skill audit", run_skill_audit),
        ("Parity check", run_parity_check),
        ("Readiness audit", run_readiness_audit),
        ("CLI audit", run_cli_audit),
        ("Unscoped rules", run_unscoped_rules_audit),
        ("Python version pins", run_python_version_pins_audit),
        ("ADR status freshness", run_adr_status_fresh_audit),
        ("Advisory scorecard coverage", run_advisory_scorecard_audit),
        ("OBPI lifecycle coherence", run_obpi_lifecycle_coherence_audit),
        ("Adversarial validation", run_adversarial_validation_audit),
        ("RED parity", run_red_parity_audit),
        ("Producer field parity", run_producer_fields_audit),
        ("Rendition freshness", run_rendition_freshness_audit),
        ("Rendition floor coherence", run_rendition_floor_coherence_audit),
        ("Invariant coherence", run_invariant_coherence_audit),
        ("Corpus retirement witness", run_corpus_retirement_witness_audit),
        ("Wheel path literals", run_wheel_path_literals_audit),
        ("Brief structure", run_brief_structure_audit),
        ("Session green gate", run_session_green_gate_audit),
        ("Closeout proof", run_closeout_proof_audit),
        ("Kind invariance", run_kind_invariance_audit),
        ("Persona witness", run_persona_witness_audit),
        ("Interview transcripts", run_interviews_audit),
        ("Pool interview schema", run_pool_interview_audit),
        ("Receipt shape", run_receipt_shape_audit),
        ("Orientation freshness", run_orientation_freshness_audit),
        ("Insights shape", run_insights_shape_audit),
        ("Instructions files budget", run_instructions_files_budget_audit),
        ("AGENTS.md map conformance", run_agents_md_map_conformance_audit),
        ("Complexity-doctrine links", run_complexity_doctrine_links_audit),
        ("Complexity-thresholds", run_complexity_thresholds_audit),
        ("REQ kind discipline", run_req_kind_discipline_audit),
        ("Status writer coverage", run_status_writer_coverage_audit),
        ("Transcribed ADR counts", run_transcribed_adr_counts_audit),
        ("tautological test audit", run_tautological_test_audit),
        ("Task envelope coherence", run_task_envelope_coherence_audit),
        ("Lock-exchange coupling", run_lock_exchange_coupling_audit),
        ("QC binding", run_qc_binding_audit),
        ("Fidelity presence", run_fidelity_presence_audit),
        ("Waiver ratchet", run_waiver_ratchet_audit),
        ("Config registry", run_config_registry_audit),
        ("Gate callers", run_gate_callers_audit),
        ("Exemption controls", run_exemption_controls_audit),
        ("Handoff documents", run_handoff_document_audit),
        ("Preflight", run_preflight),
        ("Surface fidelity", run_surface_fidelity_audit),
        ("Line endings", run_line_endings_audit),
        ("Authorship policy", run_authorship_audit),
        ("Smoke tier", run_smoke_tier),
        ("Dispatch absorption marker", run_dispatch_absorption_marker_audit),
        ("Enforcement floor", run_enforcement_floor_audit),
        # Foundation Sunset closure gate — LAST by design (ADR-0.34.0 OBPI-05):
        # wiring equals a terminal tree, so it lands green on first run.
        ("ADR taxonomy", run_taxonomy_audit),
    ]


def _load_check_step_scopes() -> dict[str, dict[str, Any]]:
    """Return the per-scope step policy from ``data/check_step_scopes.json``.

    Deliberately NOT cached, for the same reason as
    :func:`_load_check_step_classes`: caching against ``get_project_root()`` is
    the import-time-capture shape that makes a value outlive the cwd it resolved
    under (GHI #857). A missing or unreadable file returns ``{}``, and every
    consumer below treats that as "no skips" — the conservative direction.
    """
    path = get_project_root() / "data" / "check_step_scopes.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    scopes = data.get("scopes")
    return scopes if isinstance(scopes, dict) else {}


def _scope_skips(scope: str) -> frozenset[str]:
    """Return the step names *scope* drops, empty for an undeclared scope.

    Polarity is deliberate: a scope names what it DROPS, so a newly registered
    step runs everywhere until someone excludes it, and an unknown scope name
    (a typo, a missing file) drops nothing rather than silently emptying the
    gate.
    """
    entry = _load_check_step_scopes().get(scope) or {}
    skips = entry.get("skips")
    return frozenset(skips) if isinstance(skips, list) else frozenset()


def _scope_records_verified(scope: str) -> bool:
    """Whether *scope* may record the fingerprint the pre-push gate reuses.

    Only the full sweep may. A scope that drops any step is a PARTIAL
    verification, and a partial verification that can satisfy a gate is the
    presence-check failure ``AGENTS.md`` names. ``record_verified`` already
    admits only ``scope="full"``; this reads the declaration so the claim lives
    beside the skip list it depends on rather than being implied by a caller.
    """
    if scope == "full":
        return True
    entry = _load_check_step_scopes().get(scope) or {}
    return entry.get("records_verified") is True


def _select_check_steps(*, fast: bool, prepush: bool = False) -> list[tuple[str, CheckStepRunner]]:
    """Return the step list for this scope, substituting scoped tests when fast."""
    steps = _build_check_steps()
    if fast:
        skipped = _scope_skips("fast")
        kept = [(name, runner) for name, runner in steps if name not in skipped]
        kept.append(("Test (changed)", _run_changed_tests))
        return kept
    if prepush:
        skipped = _scope_skips("prepush")
        return [(name, runner) for name, runner in steps if name not in skipped]
    return steps


# Concurrency ceiling for the read-only phase.  Deliberately below the core
# count: the "Test" step internally runs `unittest-parallel` across every core
# (GHI #512), so an unbounded pool would have one step saturating the machine
# while fifty others queue behind it for the same cores.
_MAX_CONCURRENT_STEPS = 8


def _step_concurrency_classes() -> dict[str, str]:
    """Return {step name: "read_only" | "writes"} from the measured declaration.

    Returns ``{}`` when the declaration is absent, which makes every step serial
    — today's behaviour exactly.  That is the case in ADOPTER projects: the
    declaration describes gzkit's own step set and is project-local here, on the
    same footing as ``data/module_size_grandfather.json``, whose reader also
    returns empty when the file is missing.  So this speedup is gzkit's own and
    adopters are unaffected rather than broken; shipping it to them would mean
    inventing a package-data surface, which is scope this fix does not carry.

    Deliberately NOT cached.  Caching this against ``get_project_root()`` is the
    import-time-capture shape that makes a value outlive the cwd it was resolved
    under (GHI #857); the file is small and read once per ``check()`` run, so the
    cache would buy nothing and reintroduce a defect this repo is already
    tracking.
    """
    path = get_project_root() / "data" / "check_step_concurrency.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {name: entry["class"] for name, entry in data["steps"].items()}


def _steps_overlapping_writers() -> set[str]:
    """Return the read-only steps MEASURED not to read anything a writer produces.

    These may run while the serial writer phase is still going. Everything else
    waits for it, which is what the runner did for every reader until GHI #904.

    **Opt-in, never inferred.** A step overlaps only by carrying
    ``overlaps_writers: true`` in the declaration; absence means "wait", so the
    conservative behaviour is what you get by saying nothing. That is the same
    polarity :func:`_partition_steps_by_concurrency` already uses for ``class``,
    and it is load-bearing rather than stylistic: inverting it would make an
    unmeasured step overlap by default, which is precisely the flaky gate GHI
    #835 refused -- *"A parallel runner over steps with an undeclared dependency
    is a flaky gate, which is strictly worse than a slow one."*

    The bar for the flag is a measurement on BOTH sides, not an absence of known
    conflict. For ``Test``, measured 2026-08-28 with the same marker protocol
    that produced ``class``: ``Behave`` writes exactly one path
    (``dist/py_gzkit-*.whl``) and ``Docs build`` writes only under ``site/``,
    while ``Test`` is declared ``read_only`` (it writes nothing) and every
    reference to ``dist/`` or ``site/`` under ``tests/`` is an EXCLUSION -- those
    trees are named there as "not live state".
    """
    path = get_project_root() / "data" / "check_step_concurrency.json"
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        name
        for name, entry in data["steps"].items()
        if entry.get("overlaps_writers") is True and entry.get("class") == "read_only"
    }


def _partition_steps_by_concurrency(
    steps: list[tuple[str, CheckStepRunner]],
) -> tuple[list[tuple[str, CheckStepRunner]], list[tuple[str, CheckStepRunner]]]:
    """Split steps into (serial writers, concurrent read-only), preserving order.

    Writers keep their relative list order as a CONSERVATIVE DEFAULT, not to
    preserve a named edge.  Until 2026-08-28 this paragraph read that one
    measured producer→consumer edge depended on it — ``Behave`` builds
    ``dist/*.whl`` and ``gz validate --distribution`` reads that wheel.  Nothing
    in the gate reads it (GHI #905): ``--distribution`` is the static T0 audit
    and walks the SOURCE tree, and T0's wheel-reading arm is
    ``tests/test_packaging.py``, which builds its own wheel hermetically.  List
    order is kept because keeping it is free and reordering is unmeasured.

    An UNDECLARED step runs SERIALLY.  Serial is the conservative class — always
    correct, merely slower — so defaulting there can never introduce the race
    GHI #835 warns about ("A parallel runner over steps with an undeclared
    dependency is a flaky gate, which is strictly worse than a slow one"), while
    defaulting to read-only could.  The "no step ships unaccounted" guarantee is
    not weakened by this, it is relocated to where it can fail closed without
    making the runtime brittle for callers that compose their own step lists:
    ``tests/governance/test_check_step_concurrency.py`` fails the commit when a
    real step is missing from the declaration.
    """
    classes = _step_concurrency_classes()
    serial: list[tuple[str, CheckStepRunner]] = []
    concurrent: list[tuple[str, CheckStepRunner]] = []
    for name, runner in steps:
        target = concurrent if classes.get(name) == "read_only" else serial
        target.append((name, runner))
    return serial, concurrent


def _seam(name: str, result: QualityResult, project_root: pathlib.Path) -> QualityResult:
    """Apply the ONE MX checkpoint seam to a step result."""
    guard_name, emitted_level = _STEP_GUARD_META.get(
        name, (name.lower().replace(" ", "-"), _mx_levels.ERROR)
    )
    return _apply_mx_seam(result, guard_name, emitted_level, project_root)


def _run_check_steps(
    steps: list[tuple[str, CheckStepRunner]],
    project_root: pathlib.Path,
    progress: Any,
) -> list[tuple[str, QualityResult]]:
    """Run every step and return results in the declared list order.

    Two phases, per the declaration's stated protocol: writers serially first,
    then every read-only step concurrently.  The boundary is a conservative
    default against UNDECLARED dependencies — no measured edge crosses it (GHI
    #905) — so it holds without needing a general dependency graph.

    **One reader is allowed to overlap the writer phase (GHI #904.)** The phase
    boundary charges every reader for a dependency none of them turned out to
    have. ``Test`` is the extreme
    case: 31.99s of work idle behind 33.01s of writers it has no edge to, on the
    command a session runs most. A step joins the overlap lane only by carrying
    ``overlaps_writers`` in the declaration — see
    :func:`_steps_overlapping_writers` for the measurement that admits ``Test``
    and for why the flag is opt-in rather than inferred.

    Writers still run SERIALLY AMONG THEMSELVES, in list order, because no
    WRITER-side safety argument has been made — ``overlaps_writers`` is a
    reader-side measurement and does not carry one. They are submitted as ONE
    task for exactly that reason: a lane, not a fan-out.

    Threads (not processes) are correct because every runner shells out through
    ``run_command``: the work happens in subprocesses, so the GIL is not in the
    path.  The MX seam and the progress tick both stay on this thread, which
    keeps the single-firing-point requirement (REQ-0.0.74-20-01) intact — every
    ``_seam`` call below happens after a ``.result()``, never inside a worker.
    """
    serial, concurrent = _partition_steps_by_concurrency(steps)
    # No writers means no lane to overlap, so every reader belongs in ONE pool.
    # Splitting them anyway would halve the pool and reorder progress to buy
    # nothing -- caught by `tests/unit/test_progress_indication.py`, whose step
    # list is two readers and no writer.
    overlapping = _steps_overlapping_writers() if serial else set()
    early = [(n, r) for n, r in concurrent if n in overlapping]
    gated = [(n, r) for n, r in concurrent if n not in overlapping]
    collected: dict[str, QualityResult] = {}

    def _run_writer_lane() -> list[tuple[str, QualityResult]]:
        """Run every writer in list order. One task, so the order is preserved."""
        return [(name, runner(project_root)) for name, runner in serial]

    if early:
        workers = min(_MAX_CONCURRENT_STEPS, len(early) + 1, (os.cpu_count() or 4))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            lane = pool.submit(_run_writer_lane)
            pending = {pool.submit(runner, project_root): name for name, runner in early}
            for future in as_completed(pending):
                name = pending[future]
                progress.advance(name)
                collected[name] = _seam(name, future.result(), project_root)
            for name, result in lane.result():
                progress.advance(name)
                collected[name] = _seam(name, result, project_root)
    else:
        for name, runner in serial:
            progress.advance(name)
            collected[name] = _seam(name, runner(project_root), project_root)

    if gated:
        workers = min(_MAX_CONCURRENT_STEPS, len(gated), (os.cpu_count() or 4))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            pending = {pool.submit(runner, project_root): name for name, runner in gated}
            for future in as_completed(pending):
                name = pending[future]
                progress.advance(name)
                collected[name] = _seam(name, future.result(), project_root)

    return [(name, collected[name]) for name, _ in steps]


def _render_step_failures(results: list[tuple[str, QualityResult]]) -> None:
    """Print each failing step's captured output.

    Without this the aggregator swallows *why* a step failed — a gate that hides
    its own failure reason is undiagnosable from a CI log (the cause of 28
    consecutive unreadable red CI runs).
    """
    for name, result in results:
        if result.success:
            continue
        console.print(f"\n[red]─── {name} output ───[/red]")
        if result.stdout:
            console.print(result.stdout.rstrip("\n"), markup=False)
        if result.stderr:
            console.print(result.stderr.rstrip("\n"), markup=False)


def _record_full_pass(project_root: pathlib.Path) -> None:
    """Record that the FULL gate passed over this tree's content (GHI #835).

    Recorded only when nothing is unstaged or untracked. The fingerprint names the
    INDEX tree — the object that survives ``pre-commit``'s stash and that a commit
    will carry — while the gate ran against the WORKING tree, and those are the
    same object only when the tree is fully staged. Recording otherwise would
    attest a tree that was never the one tested.
    """
    from gzkit.check_fingerprint import (  # noqa: PLC0415
        record_verified,
        staged_fingerprint,
        tree_is_fully_staged,
    )

    if not tree_is_fully_staged(project_root):
        console.print(
            "[dim]  (not recorded as verified: the tree has unstaged or untracked "
            "changes, so the gate ran against content no commit will carry. "
            "`git add -A` before `gz check` to let the pre-push gate reuse it.)[/dim]"
        )
        return
    record_verified(project_root, staged_fingerprint(project_root), scope="full")


def _report_reuse_skip(project_root: pathlib.Path, *, as_json: bool) -> bool:
    """Announce and return True when this exact tree already passed a full check."""
    import json  # noqa: PLC0415
    import sys  # noqa: PLC0415

    from gzkit.check_fingerprint import already_verified  # noqa: PLC0415

    verified = already_verified(project_root)
    if verified is None:
        return False
    if as_json:
        sys.stdout.write(
            json.dumps({"success": True, "skipped": "already-verified"}, indent=2) + "\n"
        )
    else:
        console.print(
            f"[green]✓[/green] gz check: skipped — this exact tree ({verified[:12]}) "
            "already passed a full check. Content-addressed: any edit re-runs it."
        )
    return True


def _record_and_announce_pass(
    project_root: pathlib.Path, *, fast: bool, prepush: bool = False
) -> None:
    """Announce a passing run, recording the fingerprint only for a FULL one.

    A ``--fast`` pass is deliberately never recorded: it skipped the expensive
    steps by design, and letting a partial verification satisfy the gate is the
    presence-check failure ``AGENTS.md`` names.

    A ``prepush`` pass is not recorded either, and for exactly the same reason
    (GHI #950): it drops ``Behave``. Recording it would mint a fingerprint
    asserting a full sweep passed over content no full sweep ever ran on, and the
    next push would reuse that assertion.
    """
    if prepush and not _scope_records_verified("prepush"):
        console.print(
            "\n[green]✓ Pre-push checks passed.[/green] "
            f"[yellow](scoped — {', '.join(sorted(_scope_skips('prepush')))} not run; "
            "CI runs the full sweep on this commit)[/yellow]"
        )
        return
    if fast:
        console.print(
            "\n[green]✓ Fast checks passed.[/green] "
            f"[yellow](scoped — {', '.join(sorted(_scope_skips('fast')))} not run; "
            "this does NOT satisfy the pre-push gate)[/yellow]"
        )
        return
    _record_full_pass(project_root)
    console.print("\n[green]✓ All checks passed.[/green]")


def _changed_paths(project_root: pathlib.Path) -> list[str]:
    """Return repo-relative paths differing from HEAD, plus untracked files."""
    paths: set[str] = set()
    for args in (
        ["diff", "--name-only", "HEAD"],
        ["ls-files", "--others", "--exclude-standard"],
    ):
        try:
            out = subprocess.run(
                ["git", *args],
                cwd=project_root,
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if out.returncode == 0:
            paths.update(line.strip() for line in out.stdout.splitlines() if line.strip())
    return sorted(paths)


def _select_changed_tests(project_root: pathlib.Path, changed: list[str]) -> list[str]:
    """Return unittest-addressable module names for the tests a change touches.

    Two arms, and the second is a HEURISTIC stated as one: a changed test module
    is selected exactly, and a changed production module selects test modules whose
    filename contains its stem. Name matching is not a dependency graph — it will
    miss a test that exercises a module it is not named after. That is why a
    ``--fast`` pass is never recorded as verified: the selection is a convenience
    for the inner loop, never a claim of coverage.
    """
    selected: set[str] = set()
    stems: set[str] = set()
    for rel in changed:
        posix = rel.replace("\\", "/")
        if not posix.endswith(".py"):
            continue
        if posix.startswith("tests/"):
            selected.add(posix[: -len(".py")].replace("/", "."))
        elif posix.startswith("src/"):
            stem = pathlib.Path(posix).stem
            if stem not in ("__init__", "__main__"):
                stems.add(stem)
    if stems:
        for test_file in (project_root / "tests").rglob("test_*.py"):
            if any(stem in test_file.stem for stem in stems):
                rel_test = test_file.relative_to(project_root).as_posix()
                selected.add(rel_test[: -len(".py")].replace("/", "."))
    return sorted(selected)


def _run_changed_tests(project_root: pathlib.Path) -> QualityResult:
    """Run only the test modules the working tree touches (``gz check --fast``)."""
    from gzkit.quality import run_command  # noqa: PLC0415

    modules = _select_changed_tests(project_root, _changed_paths(project_root))
    if not modules:
        return QualityResult(
            success=True,
            command="(no changed tests selected)",
            stdout=(
                "No test module matched the working tree's changes. This is a SELECTION "
                "result, never a pass: run `uv run gz check` for the full suite."
            ),
            stderr="",
            returncode=0,
        )
    return run_command(["uv", "run", "-m", "unittest", "-q", *modules], cwd=project_root)


#: Steps a ``--fast`` run drops. Measured 2026-08-22 on a 10-core host against a
#: 148s full run: Test 44s, Behave 33s, Docs build 4s. Everything else — lint,
#: format, typecheck, and every governance validator — stays, because the whole
#: remainder is cheaper than any one of these three and it is where the
#: governance value lives.
def check(as_json: bool = False, fast: bool = False, reuse_verified: bool = False) -> None:
    """Run all quality checks (lint + format + typecheck + test + governance audits).

    ``fast`` drops the three expensive steps and runs only the tests the working
    tree touches. It is an INNER-LOOP scope and never records a verified
    fingerprint, so it cannot stand in for the gate — a partial verification that
    could satisfy a gate is the presence-check failure ``AGENTS.md`` names.

    ``reuse_verified`` skips the run when this exact tree CONTENT already passed a
    full check (GHI #835). A fix used to pay the full ~148s twice: once when the
    agent verified, then again at ``git push`` over a tree that had not changed.
    The second run cannot reach a different verdict.

    ``reuse_verified`` also SELECTS the ``prepush`` scope (GHI #950): it is set by
    exactly one caller, the ``gz-check-pre-push`` hook, so it is the marker for
    "this is the push gate". That scope drops ``Behave`` per
    ``data/check_step_scopes.json`` — 30.61s measured, the largest step in the
    sweep, already ruled Heavy-lane/closeout-scope by ``sync.py``, and re-run in
    full by CI on the same commit. Like ``fast``, a prepush run never records a
    verified fingerprint: it is a partial sweep, and a partial verification that
    could satisfy a gate is the presence-check failure ``AGENTS.md`` names.
    """
    import json
    import sys

    from gzkit.cli.formatters import OutputFormatter
    from gzkit.quality import run_drift_advisory

    project_root = get_project_root()
    fmt = OutputFormatter()

    if reuse_verified and not fast and _report_reuse_skip(project_root, as_json=as_json):
        return

    steps = _select_check_steps(fast=fast, prepush=reuse_verified)

    with fmt.progress_context(len(steps), "Running quality checks") as progress:
        results = _run_check_steps(steps, project_root, progress)

    drift: DriftAdvisoryResult = run_drift_advisory(project_root)

    # Flag health (advisory — warnings only, does not block)
    from gzkit.flags.diagnostics import FlagHealthSummary, get_flag_health
    from gzkit.flags.registry import load_registry

    flag_health: FlagHealthSummary | None = None
    try:
        registry = load_registry()
        flag_health = get_flag_health(registry)
    except Exception:  # noqa: BLE001 — flag health is advisory
        pass

    if as_json:
        payload: dict[str, object] = {
            "success": all(r.success for _, r in results),
            "scope": "fast" if fast else "full",
            "checks": {name: r.success for name, r in results},
            "drift": drift.to_dict(),
        }
        # `prepush` is excluded on the same ground as `fast` (GHI #950): both are
        # partial sweeps, and only a full one may mint the reuse fingerprint.
        if all(r.success for _, r in results) and not fast and not reuse_verified:
            _record_full_pass(project_root)
        if flag_health is not None:
            payload["flag_health"] = flag_health.model_dump()
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        if not all(r.success for _, r in results):
            raise SystemExit(1)
        return

    def _sym(ok: bool) -> str:
        return "[green]✓[/green]" if ok else "[red]❌[/red]"

    for name, result in results:
        console.print(f"  {_sym(result.success)} [bold]{name}[/bold]")

    _render_step_advisories(results)

    all_passed = all(r.success for _, r in results)
    if all_passed:
        _record_and_announce_pass(project_root, fast=fast, prepush=reuse_verified)
    else:
        console.print("\n[red]❌ Some checks failed.[/red]")
        _render_step_failures(results)

    _render_drift_advisory(drift)
    _render_flag_health(flag_health)

    if not all_passed:
        raise SystemExit(1)


def _bears_advisories(result: QualityResult) -> bool:
    """Whether a step's captured output can carry findings about THIS project.

    An advisory is a claim a validator makes about the repository. The test step
    also emits advisory-marked lines — its fixtures exercise the very audits that
    emit them — but those are claims about temp directories, so surfacing them
    would misattribute simulated findings to the real tree. The discriminator is
    the command the step actually ran, recorded on the result, rather than a
    hand-kept list of step names that would drift as steps are added.
    """
    return "gz validate" in result.command


def _render_step_advisories(results: list[tuple[str, QualityResult]]) -> None:
    """Surface advisory lines emitted by validator steps that PASSED (GHI #713).

    The failure branch already dumps a failing step's whole output, so drawing
    from passing steps only both closes the hole and avoids double-printing.
    Without this, a finding that must not change the exit code — the vendor
    delivery-cap distance, a staged-warn rendition check, an orphan bullet — is
    reachable only by running its scope directly, which is not the surface
    operators run.
    """
    from gzkit.advisory import ADVISORY_MARKER, advisory_lines  # noqa: PLC0415 — import cycle

    found = [
        (name, line.removeprefix(ADVISORY_MARKER).strip())
        for name, result in results
        if result.success and _bears_advisories(result)
        for line in advisory_lines(result.stdout, result.stderr)
    ]
    if not found:
        return
    console.print("\n[yellow]⚠ Advisory (does not affect exit code):[/yellow]")
    for name, prose in found:
        # escape=True: advisory prose is audit-authored text, not markup. The
        # marker itself looks like a Rich tag, and so can arbitrary quoted
        # content inside a finding — rendering it as markup would drop or
        # corrupt the prose the operator is meant to read.
        console.print(f"  [dim]{name}[/dim] {escape(prose)}")


def _render_drift_advisory(drift: DriftAdvisoryResult) -> None:
    """Render an advisory drift *summary* after blocking checks.

    Emits per-category counts only — never the full per-finding list, which
    routinely exceeds 1,000 lines and buries the exit-code-relevant gate
    results under advisory bulk (the recovery-plan triage principle: blockers
    before advisory bulk). The full per-finding listing is available via
    ``gz drift`` (and ``gz drift --json`` / ``--plain``).
    """
    if not drift.has_drift:
        return

    console.print("\n[yellow]⚠ Advisory: spec-test-code drift detected[/yellow]")

    categories = (
        ("Unlinked specs (REQs with no test)", len(drift.unlinked_specs)),
        ("Orphan tests (covering absent REQs)", len(drift.orphan_tests)),
        ("Unjustified code changes", len(drift.unjustified_code_changes)),
    )
    for label, count in categories:
        if count:
            console.print(f"  [yellow]advisory[/yellow]  {label}: {count}")

    console.print(
        f"  Total: {drift.total_drift_count} finding(s) "
        f"[dim](advisory — does not affect exit code)[/dim]"
    )
    console.print("  [dim]Run `gz drift` for the full per-finding list.[/dim]")


def _render_flag_health(health: object | None) -> None:
    """Render flag health warnings after quality checks."""
    from gzkit.flags.diagnostics import FlagHealthSummary

    if not isinstance(health, FlagHealthSummary):
        return
    if health.stale_count == 0 and health.approaching_count == 0:
        return

    console.print("\n[yellow]⚠ Flag health warnings[/yellow]")

    if health.stale_keys:
        console.print("  Stale flags (past deadline):")
        for key in health.stale_keys:
            console.print(f"    [red]stale[/red]  {key}")

    if health.approaching_keys:
        console.print("  Approaching deadline (within 14 days):")
        for key in health.approaching_keys:
            console.print(f"    [yellow]warning[/yellow]  {key}")

    console.print(
        f"  Total: {health.stale_count} stale, "
        f"{health.approaching_count} approaching "
        f"[dim](advisory — does not affect exit code)[/dim]"
    )


# Module-scope alias exposing `gz check` aggregator for test introspection.
# Tests assert that `gz_check_cmd.steps` includes specific runner tuples
# (e.g. REQ-0.0.27-07-06 — complexity-doctrine-links must fire as part of
# the `gz check` aggregate). The function attribute is populated lazily on
# first access via property-like getter to avoid circular imports at module
# load.
gz_check_cmd = check


def _gz_check_cmd_steps() -> list[tuple[str, CheckStepRunner]]:
    return _build_check_steps()


# Attach steps as a function attribute so tests can introspect the aggregator
# without invoking it. Computed once at module import time.
gz_check_cmd.steps = _build_check_steps()  # type: ignore
