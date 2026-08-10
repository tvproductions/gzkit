"""BDD steps for gz content remember — OBPI-0.0.37-19.

The CLI invocation, exit-code, file-existence, and ledger-event assertions reuse the
shared steps in ``gz_steps.py`` (``I run the gz command``, ``the command exits ...``,
``the file ... exists/does not exist``, ``ledger event ... has field ...``). Only the
surface-seeding ``@given`` is local.

@covers REQ-0.0.37-19-01
@covers REQ-0.0.37-19-02
@covers REQ-0.0.37-19-03
@covers REQ-0.0.37-19-04
"""

from __future__ import annotations

from pathlib import Path

from behave import given

_SURFACE = """# Test Agent Contract

Purpose line.

## Behavior Rules

- Do the thing.

## Prime Directive

- Own it.
"""


@given('a control surface "{name}" with a "Behavior Rules" section')
def step_seed_surface(_context, name: str) -> None:
    """Write a minimal AgentContract-parseable surface (with a behavior-rules Pillar)."""
    Path(name).write_text(_SURFACE, encoding="utf-8")
