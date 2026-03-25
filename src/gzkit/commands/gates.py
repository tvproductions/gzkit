"""Gate and implement command implementations."""

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
        return True
    except GzCliError as exc:
        _record_gate_result(ledger, adr_id, 1, "fail", "ADR exists", 1, str(exc))
        console.print(f"  [red]❌[/red] Gate 1 (ADR): [red]FAIL[/red] ({exc})")
        return False


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
        return True
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
    if result.success:
        console.print("  [green]✓[/green] Gate 3 (Docs): [green]PASS[/green]")
        return True
    console.print("  [red]❌[/red] Gate 3 (Docs): [red]FAIL[/red]")
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

    print(
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
