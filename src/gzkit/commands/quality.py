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
        location = rec.source.location
        if location is None:
            continue
        rel_path = pathlib.Path(location).relative_to(project_root)
        module = ".".join(rel_path.with_suffix("").parts)
        names.add(f"{module}.{rec.source.identifier}")

    return sorted(names)


def _resolve_obpi_behave_tags(project_root, obpi: str) -> list[str]:
    """Return behave scenario tags (``@REQ-...``) covering this OBPI's REQs.

    Scans ``features/**/*.feature`` for scenario tag lines (``@REQ-X.Y.Z-NN-MM``
    at scenario or feature level). Returns only tags whose REQ ID belongs to
    this OBPI — the filter list passed to ``behave --tags=``.
    """
    import re  # noqa: PLC0415

    req_ids = _resolve_obpi_req_ids(project_root, obpi)
    if not req_ids:
        return []

    req_tag_pattern = re.compile(r"@REQ-\d+\.\d+\.\d+-\d+-\d+")
    features_root = project_root / "features"
    if not features_root.is_dir():
        return []

    tags: set[str] = set()
    for feature_file in features_root.rglob("*.feature"):
        try:
            content = feature_file.read_text(encoding="utf-8")
        except OSError:
            continue
        for match in req_tag_pattern.finditer(content):
            tag = match.group(0)
            req_id = tag.removeprefix("@")
            if req_id in req_ids:
                tags.add(tag)
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
    tags = _resolve_obpi_behave_tags(project_root, obpi)
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
