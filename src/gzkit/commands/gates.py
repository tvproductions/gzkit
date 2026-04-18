"""Gate and implement command implementations."""

import json
from pathlib import Path
from typing import Any, Literal

from gzkit.cli.helpers.exit_codes import EXIT_POLICY_BREACH, EXIT_USER_ERROR
from gzkit.commands.common import (
    GzCliError,
    _cli_main,
    console,
    resolve_adr_file,
)
from gzkit.commands.validate_frontmatter import (
    _RECOVERY_COMMANDS,
    validate_frontmatter_coherence,
)
from gzkit.config import GzkitConfig
from gzkit.governance.status_vocab import canonicalize_status
from gzkit.ledger import Ledger, gate_checked_event
from gzkit.validate import ValidationError

Gate1Result = Literal["pass", "fail", "policy_breach"]


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


def _render_gate1_frontmatter_drift(errors: list[ValidationError]) -> None:
    """Render Gate 1 frontmatter drift listing (OBPI-0.0.16-02).

    Emits one block per drifted field with ledger-vs-frontmatter values, the
    recovery command from ``_RECOVERY_COMMANDS``, and — for ``status:`` drift —
    the canonical ledger term via ``STATUS_VOCAB_MAPPING`` (OBPI-0.0.16-05).
    Unmapped status terms surface on a distinct "unmapped" line rather than
    silently falling back, per REQ-0.0.16-05-06.

    Migration breadcrumb: when ``gz gates`` is removed in favor of
    ``gz closeout``, this renderer migrates to ``gz closeout`` Stage 1 (near
    ``closeout.py`` ADR-existence check) so the frontmatter guard stays
    mechanical at the operator's daily surface.
    """
    drift = [e for e in errors if e.type == "frontmatter"]
    if not drift:
        return
    console.print("  [red]❌[/red] Gate 1 (ADR): [red]FAIL[/red] (frontmatter drift)")
    for error in drift:
        field = error.field or "?"
        ledger_value = error.ledger_value or "?"
        fm_value = error.frontmatter_value or "?"
        console.print(
            f"    Field [bold]{field}[/bold] in {error.artifact}: "
            f"ledger='{ledger_value}' frontmatter='{fm_value}'"
        )
        if field == "status":
            canonical = canonicalize_status(fm_value)
            if canonical is None:
                console.print(
                    f"      [yellow]unmapped status term[/yellow] '{fm_value}' — "
                    "add it to STATUS_VOCAB_MAPPING"
                )
            else:
                console.print(f"      canonical ledger term: [cyan]{canonical}[/cyan]")
        command = _RECOVERY_COMMANDS.get(field, "gz chores run frontmatter-ledger-coherence")
        console.print(f"      → run: [cyan]{command}[/cyan]")


def _run_gate_1(
    project_root: Path, config: GzkitConfig, ledger: Ledger, adr_id: str
) -> Gate1Result:
    """Gate 1: ADR existence AND frontmatter-ledger coherence.

    Returns ``"policy_breach"`` on frontmatter drift so ``gates_cmd`` exits
    with ``EXIT_POLICY_BREACH`` (3). Returns ``"fail"`` on other Gate 1
    failures (e.g. ADR missing). Precedence rule: policy-breach exits shadow
    plain-failure exits within the same run; every gate still renders its
    output before the exit is raised, and the ledger records both events.
    """
    try:
        adr_file, _ = resolve_adr_file(project_root, config, adr_id)
    except GzCliError as exc:
        _record_gate_result(ledger, adr_id, 1, "fail", "ADR exists", 1, str(exc))
        console.print(f"  [red]❌[/red] Gate 1 (ADR): [red]FAIL[/red] ({exc})")
        return "fail"

    evidence = str(adr_file.relative_to(project_root))
    drift_errors = validate_frontmatter_coherence(project_root, adr_scope=adr_id)
    if drift_errors:
        _render_gate1_frontmatter_drift(drift_errors)
        drift_evidence = json.dumps(
            {
                "artifact": evidence,
                "drifted_fields": [
                    {
                        "field": e.field,
                        "ledger_value": e.ledger_value,
                        "frontmatter_value": e.frontmatter_value,
                        "artifact": e.artifact,
                    }
                    for e in drift_errors
                    if e.type == "frontmatter"
                ],
            }
        )
        _record_gate_result(ledger, adr_id, 1, "fail", "frontmatter-coherence", 3, drift_evidence)
        return "policy_breach"

    _record_gate_result(ledger, adr_id, 1, "pass", "ADR exists", 0, evidence)
    console.print(f"  [green]✓[/green] Gate 1 (ADR): [green]PASS[/green] ({evidence})")
    return "pass"


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


def _exit_for_gate_outcomes(policy_breaches: int, failures: int) -> None:
    """Route final exit code across mixed gate outcomes.

    Policy-breach exits (3) shadow plain-failure exits (1) within one run so
    ``gz gates`` surfaces the governance violation as the primary signal.
    Every gate still renders its output before this is raised; the ledger
    records both events. Only the final exit code is narrowed.
    """
    if policy_breaches:
        raise SystemExit(EXIT_POLICY_BREACH)
    if failures:
        raise SystemExit(EXIT_USER_ERROR)


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
    policy_breaches = 0

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
        outcome = handler()
        if outcome == "policy_breach":
            policy_breaches += 1
        elif not outcome:
            failures += 1

    _exit_for_gate_outcomes(policy_breaches, failures)
