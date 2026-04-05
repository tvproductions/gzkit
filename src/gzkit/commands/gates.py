"""Gate and implement command implementations."""

import json
from pathlib import Path
from typing import Any

from gzkit.commands.common import (
    GzCliError,
    _cli_main,
    console,
    resolve_adr_file,
)
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, gate_checked_event


def _record_gate_result(
    ledger: Ledger,
    adr_id: str,
    gate: int,
    status: str,
    command: str,
    returncode: int,
    evidence: str | None = None,
) -> None:
    ledger.append(
        gate_checked_event(
            adr_id=adr_id,
            gate=gate,
            status=status,
            command=command,
            returncode=returncode,
            evidence=evidence,
        )
    )


def _print_command_output(result: Any) -> None:
    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(result.stderr)


def _run_gate_1(project_root: Path, config: GzkitConfig, ledger: Ledger, adr_id: str) -> bool:
    try:
        adr_file, _ = resolve_adr_file(project_root, config, adr_id)
        evidence = str(adr_file.relative_to(project_root))
        _record_gate_result(ledger, adr_id, 1, "pass", "ADR exists", 0, evidence)
        console.print(f"  [green]✓[/green] Gate 1 (ADR): [green]PASS[/green] ({evidence})")
    except GzCliError as exc:
        _record_gate_result(ledger, adr_id, 1, "fail", "ADR exists", 1, str(exc))
        console.print(f"  [red]❌[/red] Gate 1 (ADR): [red]FAIL[/red] ({exc})")
        return False
    else:
        return True


def _run_gate_2(
    project_root: Path,
    ledger: Ledger,
    adr_id: str,
    command: str,
    label: str = "Gate 2 (TDD):",
) -> bool:
    _m = _cli_main()
    console.print(f"{label} {command}")
    result = _m.run_command(command, cwd=project_root)
    _print_command_output(result)
    status = "pass" if result.success else "fail"
    _record_gate_result(
        ledger,
        adr_id,
        2,
        status,
        command,
        result.returncode,
        "stdout/stderr captured",
    )
    if result.success:
        console.print("  [green]✓[/green] Gate 2 (TDD): [green]PASS[/green]")
        # REQ-1: include eval results when datasets exist
        return _run_eval_delta(project_root, ledger, adr_id)
    console.print("  [red]❌[/red] Gate 2 (TDD): [red]FAIL[/red]")
    return False


def _run_gate_3(project_root: Path, ledger: Ledger, adr_id: str, command: str) -> bool:
    _m = _cli_main()
    mkdocs_path = project_root / "mkdocs.yml"
    if not mkdocs_path.exists():
        _record_gate_result(ledger, adr_id, 3, "fail", command, 1, "mkdocs.yml not found")
        console.print("  [red]❌[/red] Gate 3 (Docs): [red]FAIL[/red] (mkdocs.yml not found)")
        return False

    console.print(f"  → Gate 3 (Docs): {command}")
    result = _m.run_command(command, cwd=project_root)
    _print_command_output(result)
    status = "pass" if result.success else "fail"
    _record_gate_result(
        ledger,
        adr_id,
        3,
        status,
        command,
        result.returncode,
        "stdout/stderr captured",
    )
    if not result.success:
        console.print("  [red]❌[/red] Gate 3 (Docs): [red]FAIL[/red]")
        return False

    console.print("  [green]✓[/green] Docs build: [green]PASS[/green]")
    skill_audit_ok = _run_gate_3_skill_audit(project_root, ledger, adr_id)
    if skill_audit_ok:
        console.print("  [green]✓[/green] Gate 3 (Docs): [green]PASS[/green]")
        return True
    console.print("  [red]❌[/red] Gate 3 (Docs): [red]FAIL[/red]")
    return False


def _run_gate_3_skill_audit(project_root: Path, ledger: Ledger, adr_id: str) -> bool:
    """Run skill audit as a Gate 3 sub-check."""
    from gzkit.skills_audit import audit_skills

    _m = _cli_main()
    config = _m.ensure_initialized()
    report = audit_skills(project_root, config)

    blocking = sum(1 for i in report.issues if i.blocking)
    warnings = sum(1 for i in report.issues if not i.blocking)

    for issue in report.issues:
        style = "red" if issue.blocking else "yellow"
        console.print(
            f"  [{style}]{issue.severity.upper()}[/{style}] [{issue.code}] {issue.message}"
        )

    evidence = f"skills={report.checked_skills} blocking={blocking} warnings={warnings}"
    if blocking == 0:
        console.print(f"  [green]✓[/green] Skill Audit: [green]PASS[/green] ({evidence})")
        _record_gate_result(ledger, adr_id, 3, "pass", "skill-audit", 0, evidence)
        return True

    console.print(f"  [red]❌[/red] Skill Audit: [red]FAIL[/red] ({evidence})")
    _record_gate_result(ledger, adr_id, 3, "fail", "skill-audit", 1, evidence)
    return False


def _run_gate_4(project_root: Path, ledger: Ledger, adr_id: str, command: str) -> bool:
    _m = _cli_main()
    features_dir = project_root / "features"
    if not features_dir.exists():
        _record_gate_result(ledger, adr_id, 4, "fail", command, 1, "features/ not found")
        console.print("  [red]❌[/red] Gate 4 (BDD): [red]FAIL[/red] (features/ not found)")
        return False

    console.print(f"  → Gate 4 (BDD): {command}")
    result = _m.run_command(command, cwd=project_root)
    _print_command_output(result)
    status = "pass" if result.success else "fail"
    _record_gate_result(
        ledger,
        adr_id,
        4,
        status,
        command,
        result.returncode,
        "stdout/stderr captured",
    )
    if result.success:
        console.print("  [green]✓[/green] Gate 4 (BDD): [green]PASS[/green]")
        return True
    console.print("  [red]❌[/red] Gate 4 (BDD): [red]FAIL[/red]")
    return False


def _run_gate_5() -> bool:
    console.print("  [yellow]⚠[/yellow] Gate 5 (Human): [yellow]PENDING[/yellow] (manual)")
    return True


def _run_eval_delta(
    project_root: Path,
    ledger: Ledger,
    adr_id: str,
) -> bool:
    """Run eval delta check as part of Gate 2.

    Runs the eval suite, compares against stored baselines, and reports
    regressions. Gracefully skips when eval datasets are absent (REQ-2).
    Records results via gate_checked_event (REQ-6).
    """
    from gzkit.eval.delta import (
        check_regressions,
        format_regression_output,
        load_thresholds,
    )
    from gzkit.eval.runner import run_eval_suite

    data_dir = project_root / "data" / "eval"
    baselines_dir = data_dir / "baselines"

    # REQ-2: graceful skip when no eval datasets
    if not data_dir.exists() or not any(data_dir.glob("*.json")):
        console.print("  [dim]↳ Eval delta: skipped (no eval datasets)[/dim]")
        _record_gate_result(ledger, adr_id, 2, "pass", "eval-delta", 0, "skipped: no eval datasets")
        return True

    try:
        current = run_eval_suite(data_dir=data_dir)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        console.print(f"  [red]❌[/red] Eval delta: ERROR ({exc})")
        _record_gate_result(ledger, adr_id, 2, "fail", "eval-delta", 1, str(exc))
        return False

    # REQ-2: graceful skip when no baselines to compare against
    if not baselines_dir.exists() or not any(baselines_dir.glob("*.baseline.json")):
        console.print(
            f"  [dim]↳ Eval delta: skipped (no baselines) — "
            f"{current.surfaces_scored} surfaces scored, "
            f"overall {current.overall_score}/4.0[/dim]"
        )
        _record_gate_result(ledger, adr_id, 2, "pass", "eval-delta", 0, "skipped: no baselines")
        return True

    config = load_thresholds(project_root / "config" / "eval_thresholds.json")
    result = check_regressions(current, config=config, baselines_dir=baselines_dir)
    output = format_regression_output(result)

    # REQ-6: record via gate_checked_event
    status = "pass" if result.passed else "fail"
    evidence = output
    _record_gate_result(
        ledger, adr_id, 2, status, "eval-delta", 0 if result.passed else 1, evidence
    )

    if result.passed:
        console.print(f"  [green]✓[/green] {output}")
        return True

    # REQ-5: regression output includes surface, dimension, baseline, current
    for line in output.split("\n"):
        console.print(f"  [red]{line}[/red]")
    return False


def implement_cmd(adr: str | None) -> None:
    """Run Gate 2 (tests) and record results."""
    _m = _cli_main()
    config = _m.ensure_initialized()
    project_root = _m.get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    adr_id = _m.resolve_target_adr(project_root, config, ledger, adr)
    manifest = _m.load_manifest(project_root)

    test_command = manifest.get("verification", {}).get("test", "uv run gz test")
    if not _run_gate_2(
        project_root,
        ledger,
        adr_id,
        test_command,
        label="[bold]Gate 2 (TDD):[/bold]",
    ):
        raise SystemExit(1)


def gates_cmd(gate_number: int | None, adr: str | None) -> None:
    """Run applicable gates for the current lane and record results."""
    _m = _cli_main()
    import sys

    print(  # noqa: T201
        "⚠ Deprecated: `gz gates` will be removed in a future release. Use `gz closeout` instead.",
        file=sys.stderr,
    )
    config = _m.ensure_initialized()
    project_root = _m.get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    adr_id = _m.resolve_target_adr(project_root, config, ledger, adr)
    manifest = _m.load_manifest(project_root)

    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id, {})
    lane = _m.resolve_adr_lane(info, config.mode)

    gates_for_lane = manifest.get("gates", {}).get(lane, [1, 2])
    gate_list = [gate_number] if gate_number is not None else list(gates_for_lane)

    failures = 0

    gate_handlers = {
        1: lambda: _m._run_gate_1(project_root, config, ledger, adr_id),
        2: lambda: _m._run_gate_2(
            project_root,
            ledger,
            adr_id,
            manifest.get("verification", {}).get("test", "uv run gz test"),
        ),
        3: lambda: _m._run_gate_3(
            project_root,
            ledger,
            adr_id,
            manifest.get("verification", {}).get("docs", "uv run mkdocs build --strict"),
        ),
        4: lambda: _m._run_gate_4(
            project_root,
            ledger,
            adr_id,
            manifest.get("verification", {}).get("bdd", "uv run -m behave features/"),
        ),
        5: _run_gate_5,
    }

    for gate in gate_list:
        handler = gate_handlers.get(gate)
        if not handler:
            _m.console.print(f"Unknown gate: {gate}")
            failures += 1
            continue
        if not handler():
            failures += 1

    if failures:
        raise SystemExit(1)
