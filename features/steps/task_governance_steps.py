"""BDD steps for task lifecycle governance (ADR-0.22.0 / OBPI-0.22.0-04)."""

from __future__ import annotations

import io
import json
import shlex
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then

from gzkit.cli import main
from gzkit.ledger import Ledger, obpi_created_event


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


@given("an OBPI exists for ADR-0.1.0")
def step_create_obpi(context) -> None:  # type: ignore[no-untyped-def]
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(obpi_created_event("OBPI-0.1.0-01", "ADR-0.1.0"))


@given('I run the gz command "{command}"')
def step_given_run_command(context, command: str) -> None:  # type: ignore[no-untyped-def]
    args = shlex.split(command)
    context.exit_code, context.output = _invoke(args)


@given("a pending task {task_id} exists")
def step_create_pending_task(context, task_id: str) -> None:  # type: ignore[no-untyped-def]
    """No-op: pending is the default state (no ledger event needed)."""


@then("the output is valid JSON")
def step_output_is_valid_json(context) -> None:  # type: ignore[no-untyped-def]
    try:
        json.loads(context.output)
    except (json.JSONDecodeError, ValueError) as exc:
        raise AssertionError(f"Output is not valid JSON: {exc}\n{context.output}") from exc
