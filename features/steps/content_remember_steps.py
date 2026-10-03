"""BDD steps for gz content remember — OBPI-0.0.37-19 and OBPI-0.35.0-08.

The CLI invocation, exit-code, file-existence, output, and ledger-event assertions reuse
the shared steps in ``gz_steps.py`` (``I run the gz command``, ``the command exits ...``,
``the file ... exists/does not exist``, ``the output contains ...``, ``ledger event ...
has field ...``). The landing project and its assertions come from
``content_land_steps.py`` (``a three-consumer landing project with an unchanged corpus``,
``every consumer sidecar carries attestation text ...``).

Local to this file are five steps: the three seeding givens (the minimal control
surface, a committed rendition on a stale corpus fingerprint, and the parseable
``LandSurface.md`` that ``remember`` requires of the landing project) and the two
advisory steps that carry the REQ-0.35.0-08-04 recovery path (keep the printed advisory,
then run the land command it printed with its placeholders filled).

@covers REQ-0.0.37-19-01
@covers REQ-0.0.37-19-02
@covers REQ-0.0.37-19-03
@covers REQ-0.0.37-19-04
@covers REQ-0.35.0-08-04
@covers REQ-0.35.0-08-05
"""

from __future__ import annotations

import io
import shlex
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when

from gzkit.cli.main import main
from gzkit.content.rendition_store import (
    RenditionProvenance,
    save_fingerprint,
    save_rendition,
)

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


@given('a committed "{consumer}" rendition of "{name}" on a stale corpus fingerprint')
def step_seed_stale_rendition(_context, consumer: str, name: str) -> None:
    """Commit a rendition whose sidecar fingerprint cannot match any real corpus digest."""
    root = Path()
    save_rendition(root, name, consumer, _SURFACE.encode("utf-8"))
    save_fingerprint(
        root,
        name,
        consumer,
        RenditionProvenance(
            corpus_fingerprint="0" * 64,
            corpus_entry_count=0,
            rendition_fingerprint=None,
            committed_ts="2026-07-22T00:00:00+00:00",
            attestor="g0",
            attestation_text="seeded for scenario",
        ),
    )


_LAND_SURFACE_FILE = """# Land Surface

## Owned Section

seed rule text.

## Unowned Section

carried forward text verbatim
"""


@given('the landing project\'s surface "{name}" is a parseable contract')
def step_seed_land_surface(_context, name: str) -> None:
    """Write the control-surface file ``remember`` requires; landing itself never reads it.

    The sections are the two the landing project's ownership declaration names
    (``owned-section`` and ``unowned-section``), so ``--section owned-section`` resolves.
    """
    Path(name).write_text(_LAND_SURFACE_FILE, encoding="utf-8")


def _printed_land_command(output: str) -> str:
    """Return the ``uv run gz content land ...`` command the advisory printed, joined.

    The advisory wraps the command with a trailing backslash; the continuation line
    carries the flags. Both are read from the captured output, never hard-coded.
    """
    lines = output.splitlines()
    for index, line in enumerate(lines):
        if line.strip().startswith("uv run gz content land"):
            command = line.strip()
            while command.endswith("\\"):
                index += 1
                command = command[:-1].rstrip() + " " + lines[index].strip()
            return command
    raise AssertionError(f"the output printed no land command:\n{output}")


@then("I keep the advisory the command printed")
def step_keep_advisory(context) -> None:
    """Hold the advisory text, since later commands overwrite ``context.output``."""
    context.advisory = context.output


@when(
    'I run the land command the advisory printed with attestor "{attestor}" '
    'and attestation text "{text}"'
)
def step_run_printed_land_command(context, attestor: str, text: str) -> None:
    command = _printed_land_command(context.advisory)
    assert "<handle>" in command and "<the operator's verbatim words>" in command, command
    command = command.replace("<handle>", attestor)
    command = command.replace("<the operator's verbatim words>", text)
    argv = shlex.split(command)
    assert argv[:3] == ["uv", "run", "gz"], argv
    context.printed_command = command
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(argv[3:])
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    context.exit_code = 0 if code is None else int(code)
    context.output = output.getvalue()
