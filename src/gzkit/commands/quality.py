"""Quality commands (lint, format, test, typecheck, check).

@covers ADR-0.20.0-spec-triangle-sync
@covers OBPI-0.20.0-05-advisory-gate-integration
"""

from __future__ import annotations

import pathlib
import subprocess
from collections.abc import Callable
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
    "ADR status freshness": ("adr-status-fresh", _mx_levels.ERROR),
    "Adversarial validation": ("adversarial-validation", _mx_levels.ERROR),
    "RED parity": ("red-parity", _mx_levels.ERROR),
    "Rendition freshness": ("rendition-freshness", _mx_levels.ERROR),
    "Rendition floor coherence": ("rendition-floor-coherence", _mx_levels.ERROR),
    "Invariant coherence": ("invariant-coherence", _mx_levels.ERROR),
    "Brief structure": ("brief-structure", _mx_levels.ERROR),
    "Session green gate": ("session-green-gate", _mx_levels.ERROR),
    "Closeout proof": ("closeout-proof", _mx_levels.ERROR),
    "Kind invariance": ("kind-invariance", _mx_levels.ERROR),
    "Interview transcripts": ("interviews", _mx_levels.ERROR),
    "Receipt shape": ("receipt-shape", _mx_levels.ERROR),
    "Orientation freshness": ("orientation-freshness", _mx_levels.ERROR),
    "Insights shape": ("insights-shape", _mx_levels.ERROR),
    "Instructions files budget": ("instructions-files-budget", _mx_levels.ERROR),
    "AGENTS.md map conformance": ("agents-md-map-conformance", _mx_levels.ERROR),
    "Complexity-doctrine links": ("complexity-doctrine-links", _mx_levels.ERROR),
    "Complexity-thresholds": ("complexity-thresholds", _mx_levels.ERROR),
    "REQ kind discipline": ("req-kind-discipline", _mx_levels.ERROR),
    "tautological test audit": ("tautological-test-audit", _mx_levels.ERROR),
    "Task envelope coherence": ("task-envelope-coherence", _mx_levels.ERROR),
    "Lock-handoff coupling": ("lock-handoff-coupling", _mx_levels.ERROR),
    "QC binding": ("qc-binding", _mx_levels.ERROR),
    "Fidelity presence": ("fidelity-presence", _mx_levels.ERROR),
    "Waiver ratchet": ("waiver-ratchet", _mx_levels.ERROR),
    "Handoff documents": ("handoff-documents", _mx_levels.ERROR),
    "Preflight": ("preflight", _mx_levels.ERROR),
    "Surface fidelity": ("surface-fidelity", _mx_levels.ERROR),
    "Line endings": ("line-endings", _mx_levels.ERROR),
    "Authorship policy": ("authorship", _mx_levels.ERROR),
    "Dispatch attestation": ("dispatch-attestation", _mx_levels.ERROR),
    # §5 enforcement-claim meta-validator — pinned CRITICAL so a FACADE never
    # demotes to advisory inside the hangar (ADR-0.0.74 BI#3 / §5; GHI #651).
    "Enforcement floor": ("enforcement-floor", _mx_levels.CRITICAL),
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
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

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
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

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
        console.print(behave_result.stdout)
    if behave_result.stderr:
        console.print(behave_result.stderr)
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
        console.print(unit.stdout)
    if unit.stderr:
        console.print(unit.stderr)
    if not unit.success:
        console.print("[red]Unit tests failed.[/red]")
        raise SystemExit(unit.returncode)
    console.print("[green]Unit tests passed.[/green]")

    if not bdd:
        return

    console.print("Running behave scenarios...")
    behave_result = run_behave(project_root)
    if behave_result.stdout:
        console.print(behave_result.stdout)
    if behave_result.stderr:
        console.print(behave_result.stderr)
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
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)

    if result.success:
        console.print("[green]Type check passed.[/green]")
    else:
        console.print("[red]Type check failed.[/red]")
        raise SystemExit(result.returncode)


def _build_check_steps() -> list[tuple[str, CheckStepRunner]]:
    """Build the canonical `gz check` steps list.

    Module-scope-importable so tests and external callers can introspect the
    aggregator without invoking the full check pipeline (REQ-0.0.27-07-06).
    """
    from gzkit.quality import (
        run_adr_status_fresh_audit,
        run_adversarial_validation_audit,
        run_agents_md_map_conformance_audit,
        run_authorship_audit,
        run_brief_structure_audit,
        run_cli_audit,
        run_closeout_proof_audit,
        run_complexity_doctrine_links_audit,
        run_complexity_thresholds_audit,
        run_dispatch_attestation_audit,
        run_enforcement_floor_audit,
        run_fidelity_presence_audit,
        run_format_check,
        run_handoff_document_audit,
        run_insights_shape_audit,
        run_instructions_files_budget_audit,
        run_interviews_audit,
        run_invariant_coherence_audit,
        run_kind_invariance_audit,
        run_line_endings_audit,
        run_lock_handoff_coupling_audit,
        run_mkdocs,
        run_obpi_lifecycle_coherence_audit,
        run_orientation_freshness_audit,
        run_parity_check,
        run_preflight,
        run_qc_binding_audit,
        run_readiness_audit,
        run_receipt_shape_audit,
        run_red_parity_audit,
        run_rendition_floor_coherence_audit,
        run_rendition_freshness_audit,
        run_req_kind_discipline_audit,
        run_session_green_gate_audit,
        run_skill_audit,
        run_surface_fidelity_audit,
        run_task_envelope_coherence_audit,
        run_tautological_test_audit,
        run_unscoped_rules_audit,
        run_waiver_ratchet_audit,
    )

    return [
        ("Lint", run_lint),
        ("Format", run_format_check),
        ("Typecheck", run_typecheck),
        ("Test", run_tests),
        ("Behave", run_behave),
        ("Docs build", run_mkdocs),
        ("Skill audit", run_skill_audit),
        ("Parity check", run_parity_check),
        ("Readiness audit", run_readiness_audit),
        ("CLI audit", run_cli_audit),
        ("Unscoped rules", run_unscoped_rules_audit),
        ("ADR status freshness", run_adr_status_fresh_audit),
        ("OBPI lifecycle coherence", run_obpi_lifecycle_coherence_audit),
        ("Adversarial validation", run_adversarial_validation_audit),
        ("RED parity", run_red_parity_audit),
        ("Rendition freshness", run_rendition_freshness_audit),
        ("Rendition floor coherence", run_rendition_floor_coherence_audit),
        ("Invariant coherence", run_invariant_coherence_audit),
        ("Brief structure", run_brief_structure_audit),
        ("Session green gate", run_session_green_gate_audit),
        ("Closeout proof", run_closeout_proof_audit),
        ("Kind invariance", run_kind_invariance_audit),
        ("Interview transcripts", run_interviews_audit),
        ("Receipt shape", run_receipt_shape_audit),
        ("Orientation freshness", run_orientation_freshness_audit),
        ("Insights shape", run_insights_shape_audit),
        ("Instructions files budget", run_instructions_files_budget_audit),
        ("AGENTS.md map conformance", run_agents_md_map_conformance_audit),
        ("Complexity-doctrine links", run_complexity_doctrine_links_audit),
        ("Complexity-thresholds", run_complexity_thresholds_audit),
        ("REQ kind discipline", run_req_kind_discipline_audit),
        ("tautological test audit", run_tautological_test_audit),
        ("Task envelope coherence", run_task_envelope_coherence_audit),
        ("Lock-handoff coupling", run_lock_handoff_coupling_audit),
        ("QC binding", run_qc_binding_audit),
        ("Fidelity presence", run_fidelity_presence_audit),
        ("Waiver ratchet", run_waiver_ratchet_audit),
        ("Handoff documents", run_handoff_document_audit),
        ("Preflight", run_preflight),
        ("Surface fidelity", run_surface_fidelity_audit),
        ("Line endings", run_line_endings_audit),
        ("Authorship policy", run_authorship_audit),
        ("Dispatch attestation", run_dispatch_attestation_audit),
        ("Enforcement floor", run_enforcement_floor_audit),
    ]


def check(as_json: bool = False) -> None:
    """Run all quality checks (lint + format + typecheck + test + governance audits)."""
    import json
    import sys

    from gzkit.cli.formatters import OutputFormatter
    from gzkit.quality import run_drift_advisory

    project_root = get_project_root()
    fmt = OutputFormatter()

    steps = _build_check_steps()

    results: list[tuple[str, QualityResult]] = []
    with fmt.progress_context(len(steps), "Running quality checks") as progress:
        for name, runner in steps:
            progress.advance(name)
            result = runner(project_root)
            guard_name, emitted_level = _STEP_GUARD_META.get(
                name, (name.lower().replace(" ", "-"), _mx_levels.ERROR)
            )
            result = _apply_mx_seam(result, guard_name, emitted_level, project_root)
            results.append((name, result))

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
            "checks": {name: r.success for name, r in results},
            "drift": drift.to_dict(),
        }
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
        console.print("\n[green]✓ All checks passed.[/green]")
    else:
        console.print("\n[red]❌ Some checks failed.[/red]")
        # Surface each failing step's captured output. Without this the
        # aggregator swallows *why* a step failed — a gate that hides its own
        # failure reason is undiagnosable from a CI log (the cause of 28
        # consecutive unreadable red CI runs).
        for name, result in results:
            if result.success:
                continue
            console.print(f"\n[red]─── {name} output ───[/red]")
            if result.stdout:
                console.print(result.stdout.rstrip("\n"))
            if result.stderr:
                console.print(result.stderr.rstrip("\n"))

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
