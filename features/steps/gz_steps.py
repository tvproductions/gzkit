"""BDD steps for heavy-lane governance behavior."""

from __future__ import annotations

import io
import json
import shlex
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when

from gzkit.cli import main
from gzkit.ledger import Ledger, gate_checked_event


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


@given("a heavy ADR exists")
def step_plan_heavy_adr(_context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke(["plan", "0.1.0", "--lane", "heavy"])
    assert code == 0, output


@given("gate 2 and gate 3 are marked pass for ADR-0.1.0")
def step_mark_gate23(_context) -> None:  # type: ignore[no-untyped-def]
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(gate_checked_event("ADR-0.1.0", 2, "pass", "test", 0))
    ledger.append(gate_checked_event("ADR-0.1.0", 3, "pass", "docs", 0))


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


@then('JSON path "{path}" equals "{expected}"')
def step_json_path_equals(context, path: str, expected: str) -> None:  # type: ignore[no-untyped-def]
    payload = json.loads(context.output)
    value = payload
    for segment in path.split("."):
        value = value[segment]
    assert str(value) == expected, context.output
