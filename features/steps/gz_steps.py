"""BDD steps for heavy-lane governance behavior."""

from __future__ import annotations

import io
import json
import shlex
import subprocess
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, gate_checked_event, obpi_created_event, obpi_receipt_emitted_event


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


@given("the workspace is initialized in heavy mode")
def step_init_heavy(_context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke(["init", "--mode", "heavy"])
    assert code == 0, output


@given("the workspace is initialized")
def step_init_default(_context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke(["init"])
    assert code == 0, output


@given("a heavy ADR exists")
def step_plan_heavy_adr(_context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke(["plan", "create", "0.1.0", "--lane", "heavy"])
    assert code == 0, output


@given("ADR-0.1.0 exists")
def step_plan_default_adr(_context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke(["plan", "create", "0.1.0"])
    assert code == 0, output


@given("gate 2 and gate 3 are marked pass for ADR-0.1.0")
def step_mark_gate23(_context) -> None:  # type: ignore[no-untyped-def]
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
    ledger.append(gate_checked_event("ADR-0.1.0", 3, "pass", "docs", 0))


@given("a completed OBPI with anchor-tracked receipt exists for OBPI-0.1.0-01-demo")
def step_completed_anchor_obpi(context) -> None:  # type: ignore[no-untyped-def]
    config = GzkitConfig.load(Path(".gzkit.json"))
    obpi_path = Path(config.paths.adrs) / "obpis" / "OBPI-0.1.0-01-demo.md"
    obpi_path.parent.mkdir(parents=True, exist_ok=True)
    obpi_path.write_text(
        "\n".join(
            [
                "---",
                "id: OBPI-0.1.0-01-demo",
                "parent: ADR-0.1.0",
                "item: 1",
                "lane: Lite",
                "status: Completed",
                "---",
                "",
                "# OBPI-0.1.0-01-demo: Demo",
                "",
                "**Brief Status:** Completed",
                "",
                "## Evidence",
                "",
                "### Implementation Summary",
                "- Files created/modified: src/module.py",
                "- Validation commands run: uv run gz test",
                "- Date completed: 2026-03-12",
                "",
                "## Key Proof",
                "uv run gz obpi status OBPI-0.1.0-01-demo --json",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    module_path = Path("src/module.py")
    module_path.parent.mkdir(parents=True, exist_ok=True)
    module_path.write_text("value = 1\n", encoding="utf-8")

    subprocess.run(["git", "init", "-b", "main"], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "config", "user.name", "BDD User"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "bdd@example.com"],
        check=True,
        capture_output=True,
        text=True,
    )
    subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed"], check=True, capture_output=True, text=True)
    head = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(obpi_created_event("OBPI-0.1.0-01-demo", "ADR-0.1.0"))
    ledger.append(
        obpi_receipt_emitted_event(
            obpi_id="OBPI-0.1.0-01-demo",
            parent_adr="ADR-0.1.0",
            receipt_event="completed",
            attestor="human:bdd",
            obpi_completion="completed",
            evidence={
                "value_narrative": "Anchor-aware reconcile preserves completed lifecycle state.",
                "key_proof": "uv run gz obpi reconcile OBPI-0.1.0-01-demo --json",
                "scope_audit": {
                    "allowlist": ["src/module.py"],
                    "changed_files": ["src/module.py"],
                    "out_of_scope_files": [],
                },
                "git_sync_state": {
                    "dirty": False,
                    "ahead": 0,
                    "behind": 0,
                    "diverged": False,
                    "blockers": [],
                },
            },
            anchor={"commit": head, "semver": "0.1.0"},
        )
    )
    context.anchor_commit = head


@given("the tracked module changes after the completion anchor")
def step_anchor_drift(context) -> None:  # type: ignore[no-untyped-def]
    module_path = Path("src/module.py")
    module_path.write_text("value = 2\n", encoding="utf-8")
    subprocess.run(["git", "add", "src/module.py"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "drift"], check=True, capture_output=True, text=True)
    context.current_head = subprocess.run(
        ["git", "rev-parse", "--short=7", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


@when('I run the gz command "{command}"')
def step_run_command(context, command: str) -> None:  # type: ignore[no-untyped-def]
    args = shlex.split(command)
    context.exit_code, context.output = _invoke(args)


@then("the command exits non-zero")
def step_nonzero(context) -> None:  # type: ignore[no-untyped-def]
    assert context.exit_code != 0, context.output


@then("the command exits with code {expected:d}")
def step_exit_code(context, expected: int) -> None:  # type: ignore[no-untyped-def]
    assert context.exit_code == expected, context.output


@then('the output contains "{text}"')
def step_output_contains(context, text: str) -> None:  # type: ignore[no-untyped-def]
    assert text in context.output, context.output


@then('the file "{path}" exists')
def step_file_exists(_context, path: str) -> None:  # type: ignore[no-untyped-def]
    assert Path(path).exists(), f"Expected {path} to exist"


@then('the file "{path}" contains "{text}"')
def step_file_contains(_context, path: str, text: str) -> None:  # type: ignore[no-untyped-def]
    content = Path(path).read_text(encoding="utf-8")
    assert text in content, content


@then('JSON path "{path}" equals "{expected}"')
def step_json_path_equals(context, path: str, expected: str) -> None:  # type: ignore[no-untyped-def]
    payload = json.loads(context.output)
    value = payload
    for segment in path.split("."):
        value = value[segment]
    assert str(value) == expected, context.output
