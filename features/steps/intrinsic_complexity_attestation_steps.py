"""Behave step definitions for intrinsic-complexity attestation (OBPI-0.0.29-07).

Provides Given steps that:
- Build the same synthetic fixture as ``complexity_advise_steps.py``
- Pre-populate the in-process ``_REGISTRY`` (decorator path)
- Create the ``.gzkit`` ledger directory (commit-time path)
- Mock TTY gate + ATTEST input (REQ-0.0.29-07-04 happy path)

The ``When I run the gz command`` / ``Then the command exits with code N``
steps live in ``gz_steps.py`` and are shared.

@covers REQ-0.0.29-07-01
@covers REQ-0.0.29-07-03
@covers REQ-0.0.29-07-04
@covers REQ-0.0.29-07-05
"""

from __future__ import annotations

import io
import json
import shlex
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from behave import given, then, when

from gzkit.cli import main


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


@given('the function "{qualname}" in "{filename}" is registered as intrinsically attested')
def step_register_intrinsic(context, qualname: str, filename: str) -> None:
    from datetime import date

    from gzkit.complexity.advisor.intrinsic import _REGISTRY  # noqa: PLC2701

    file_path = str((Path.cwd() / filename).absolute())
    _REGISTRY[(file_path, qualname)] = (
        "irreducible branching for all observed states",
        "Jeffry",
        date.today().isoformat(),
    )
    context.add_cleanup(_REGISTRY.clear)


@given('the ledger directory exists at "{rel_path}"')
def step_ensure_ledger_dir(_context, rel_path: str) -> None:
    ledger_dir = Path.cwd() / rel_path
    ledger_dir.mkdir(parents=True, exist_ok=True)
    ledger_file = ledger_dir / "ledger.jsonl"
    if not ledger_file.exists():
        ledger_file.write_text("", encoding="utf-8")


@when('I run the gz command "{command}" with simulated TTY attestation')
def step_run_with_tty_attest(context, command: str) -> None:
    args = shlex.split(command)
    with (
        patch(
            "gzkit.commands.complexity_advise._is_attest_tty_available",
            return_value=True,
        ),
        patch(
            "gzkit.commands.complexity_advise._prompt_attest_confirmation",
            return_value="ATTEST",
        ),
    ):
        context.exit_code, context.output = _invoke(args)


@then('the ledger contains an "{event_type}" event for "{qualname}"')
def step_ledger_has_attestation_event(_context, event_type: str, qualname: str) -> None:
    ledger_path = Path.cwd() / ".gzkit" / "ledger.jsonl"
    assert ledger_path.exists(), f"Ledger not found at {ledger_path}"
    events = [
        json.loads(line)
        for line in ledger_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    matching = [e for e in events if e.get("event") == event_type and qualname in e.get("id", "")]
    assert matching, (
        f"No {event_type!r} event with qualname {qualname!r} in ledger.\n"
        f"All events: {[e.get('event') for e in events]}"
    )
