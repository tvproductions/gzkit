"""Quality commands (lint, format, test, typecheck, check).

@covers ADR-0.20.0-spec-triangle-sync
@covers OBPI-0.20.0-05-advisory-gate-integration
"""

from __future__ import annotations

import pathlib
import subprocess

from gzkit.commands.common import console, get_project_root
from gzkit.quality import (
    DriftAdvisoryResult,
    run_behave,
    run_format,
    run_lint,
    run_tests,
    run_typecheck,
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


def _resolve_obpi_test_names(project_root, obpi: str) -> list[str]:
    """Return unittest-runnable names for tests covering this OBPI's REQs.

    Uses the canonical traceability API (``@covers`` scanner + brief REQ
    extraction) to identify which tests cover REQs belonging to the target
    OBPI. Returns unittest-addressable identifiers like
    ``tests.commands.test_validate_frontmatter.TestClass.test_method``.
    """
    from gzkit.traceability import EdgeType, scan_test_tree  # noqa: PLC0415
    from gzkit.triangle import ReqId, scan_briefs  # noqa: PLC0415

    short = obpi.upper().removeprefix("OBPI-")
    if "-" not in short:
        raise ValueError(f"Expected OBPI-<semver>-<item> form, got {obpi!r}")
    semver, item = short.split("-", 1)
    item = item.split("-", 1)[0]  # Drop any trailing slug

    brief_root = project_root / "docs" / "design" / "adr"
    briefs = scan_briefs(brief_root)
    req_ids = {
        str(b.entity.id)
        for b in briefs
        if b.entity.id.semver == semver and b.entity.id.obpi_item == item
    }
    if not req_ids:
        return []

    test_root = project_root / "tests"
    records = scan_test_tree(test_root)

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
        location = rec.source.location
        if location is None:
            continue
        rel_path = pathlib.Path(location).relative_to(project_root)
        module = ".".join(rel_path.with_suffix("").parts)
        names.add(f"{module}.{rec.source.identifier}")

    return sorted(names)


def test(bdd: bool = False, obpi: str | None = None) -> None:
    """Run the unit-test suite; optionally scoped to one OBPI or with BDD.

    Scope selection:

    * ``--obpi OBPI-X.Y.Z-NN`` — run only tests decorated with
      ``@covers`` for REQs belonging to that OBPI (fastest;
      OBPI-scoped pipeline stage 3). Incompatible with ``--bdd``.
    * ``--bdd`` — run the full unittest suite plus behave scenarios
      (Heavy-lane / ADR closeout / pre-release ceremony).
    * default — run the full unittest suite (ad-hoc, CI-safe). Pre-commit
      hooks already enforce this on every commit, so operators rarely
      need to invoke it manually for OBPI-scoped work.

    See ``.gzkit/rules/tests.md`` for policy.
    """
    project_root = get_project_root()

    if obpi and bdd:
        console.print(
            "[red]--obpi and --bdd are mutually exclusive. "
            "OBPI-scoped runs are unit-only; BDD belongs to ADR closeout.[/red]"
        )
        raise SystemExit(1)

    if obpi:
        names = _resolve_obpi_test_names(project_root, obpi)
        if not names:
            console.print(
                f"[yellow]No @covers tests found for {obpi}. "
                "Either no REQs have test coverage yet, or the OBPI has no "
                "testable REQs (docs-only).[/yellow]"
            )
            return
        console.print(f"Running {len(names)} test(s) scoped to {obpi}...")
        result = subprocess.run(
            ["uv", "run", "-m", "unittest", "-v", *names],
            cwd=project_root,
            check=False,
            encoding="utf-8",
        )
        if result.returncode != 0:
            console.print("[red]OBPI-scoped tests failed.[/red]")
            raise SystemExit(result.returncode)
        console.print(f"[green]OBPI-scoped tests passed ({len(names)} tests).[/green]")
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


def check(as_json: bool = False) -> None:
    """Run all quality checks (lint + format + typecheck + test + governance audits)."""
    import json
    import sys

    from gzkit.cli.formatters import OutputFormatter
    from gzkit.quality import (
        run_cli_audit,
        run_drift_advisory,
        run_format_check,
        run_parity_check,
        run_preflight,
        run_readiness_audit,
        run_skill_audit,
    )

    project_root = get_project_root()
    fmt = OutputFormatter()

    steps = [
        ("Lint", run_lint),
        ("Format", run_format_check),
        ("Typecheck", run_typecheck),
        ("Test", run_tests),
        ("Behave", run_behave),
        ("Skill audit", run_skill_audit),
        ("Parity check", run_parity_check),
        ("Readiness audit", run_readiness_audit),
        ("CLI audit", run_cli_audit),
        ("Preflight", run_preflight),
    ]

    results: list[tuple[str, bool]] = []
    with fmt.progress_context(len(steps), "Running quality checks") as progress:
        for name, runner in steps:
            progress.advance(name)
            result = runner(project_root)
            results.append((name, result.success))

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
            "success": all(s for _, s in results),
            "checks": dict(results),
            "drift": drift.to_dict(),
        }
        if flag_health is not None:
            payload["flag_health"] = flag_health.model_dump()
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        if not all(s for _, s in results):
            raise SystemExit(1)
        return

    def _sym(ok: bool) -> str:
        return "[green]✓[/green]" if ok else "[red]❌[/red]"

    for name, success in results:
        console.print(f"  {_sym(success)} [bold]{name}[/bold]")

    all_passed = all(s for _, s in results)
    if all_passed:
        console.print("\n[green]✓ All checks passed.[/green]")
    else:
        console.print("\n[red]❌ Some checks failed.[/red]")

    _render_drift_advisory(drift)
    _render_flag_health(flag_health)

    if not all_passed:
        raise SystemExit(1)


def _render_drift_advisory(drift: DriftAdvisoryResult) -> None:
    """Render advisory drift findings after blocking checks."""
    if not drift.has_drift:
        return

    console.print("\n[yellow]⚠ Advisory: spec-test-code drift detected[/yellow]")

    if drift.unlinked_specs:
        console.print("  Unlinked specs (REQs with no test):")
        for req_id in drift.unlinked_specs:
            console.print(f"    [yellow]advisory[/yellow]  {req_id}")

    if drift.orphan_tests:
        console.print("  Orphan tests (covering absent REQs):")
        for req_id in drift.orphan_tests:
            console.print(f"    [yellow]advisory[/yellow]  {req_id}")

    if drift.unjustified_code_changes:
        console.print("  Unjustified code changes:")
        for code_id in drift.unjustified_code_changes:
            console.print(f"    [yellow]advisory[/yellow]  {code_id}")

    console.print(
        f"  Total: {drift.total_drift_count} finding(s) "
        f"[dim](advisory — does not affect exit code)[/dim]"
    )


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
