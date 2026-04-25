"""BDD steps for chores distribution scenarios (OBPI-0.0.21-07).

Exercises the install -> scaffold -> list -> repair lifecycle against the
real installed gzkit package by invoking the CLI as a subprocess in the
per-scenario tempdir set up by ``features/environment.py``.

@covers REQ-0.0.21-07-01
@covers REQ-0.0.21-07-02
@covers REQ-0.0.21-07-03
@covers REQ-0.0.21-07-04
@covers REQ-0.0.21-07-05
@covers REQ-0.0.21-07-06
@covers REQ-0.0.21-07-07
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

from behave import given, then, when

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def _strip_ansi(text: str) -> str:
    return _ANSI_RE.sub("", text)


def _gz_subprocess(command: str, cwd: Path) -> tuple[int, str]:
    """Invoke ``gz <args>`` as a subprocess in ``cwd``, return (exit, output).

    Replaces a leading ``gz`` token with ``[sys.executable, "-m", "gzkit"]``
    so the editable install in the project's ``.venv`` is exercised. ANSI
    color codes are stripped from the captured output to keep substring
    assertions stable.
    """
    parts = shlex.split(command)
    if not parts or parts[0] != "gz":
        raise ValueError(f"Expected leading 'gz' token, got: {command!r}")
    args = [sys.executable, "-m", "gzkit", *parts[1:]]
    env = os.environ.copy()
    env.setdefault("NO_COLOR", "1")
    result = subprocess.run(
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=env,
        check=False,
    )
    output = _strip_ansi(result.stdout) + _strip_ansi(result.stderr)
    return result.returncode, output


@given("a fresh empty project directory")
def step_fresh_empty_dir(context) -> None:  # type: ignore[no-untyped-def]
    cwd = Path.cwd()
    assert not (cwd / ".gzkit").exists(), f"Tempdir {cwd} is not fresh"
    context.project_root = cwd
    context.subprocess_exit_code = None
    context.subprocess_output = ""


@given("the workspace has been initialized via gz init")
def step_init_via_gz_init(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _gz_subprocess("gz init --no-skeleton", context.project_root)
    assert code == 0, f"gz init failed (exit {code}):\n{output}"


@given('the operator edits "{relpath}" with marker "{marker}"')
def step_operator_edits_chore(context, relpath: str, marker: str) -> None:  # type: ignore[no-untyped-def]
    target = context.project_root / Path(relpath)
    assert target.exists(), f"Expected {target} to exist before operator edit"
    existing = target.read_text(encoding="utf-8")
    target.write_text(existing + f"\n<!-- {marker} -->\n", encoding="utf-8")


@given('the slug "{slug}" has been removed from "{relpath}"')
def step_remove_slug_from_registry(context, slug: str, relpath: str) -> None:  # type: ignore[no-untyped-def]
    registry_path = context.project_root / Path(relpath)
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    chores = payload.get("chores", [])
    filtered = [entry for entry in chores if entry.get("slug") != slug]
    assert len(filtered) < len(chores), (
        f"Slug {slug!r} not present in registry {relpath} before removal"
    )
    payload["chores"] = filtered
    registry_path.write_text(json.dumps(payload, indent=4) + "\n", encoding="utf-8")


@when('I run "{command}" as a subprocess')
def step_run_subprocess(context, command: str) -> None:  # type: ignore[no-untyped-def]
    code, output = _gz_subprocess(command, context.project_root)
    context.subprocess_exit_code = code
    context.subprocess_output = (context.subprocess_output or "") + output


@then("the subprocess exits with code {expected:d}")
def step_subprocess_exit_code(context, expected: int) -> None:  # type: ignore[no-untyped-def]
    assert context.subprocess_exit_code == expected, (
        f"Expected exit {expected}, got {context.subprocess_exit_code}\n"
        f"Output:\n{context.subprocess_output}"
    )


@then('the subprocess output contains "{text}"')
def step_subprocess_output_contains(context, text: str) -> None:  # type: ignore[no-untyped-def]
    assert text in context.subprocess_output, (
        f"Expected {text!r} in subprocess output:\n{context.subprocess_output}"
    )


@then('every chore row in the subprocess output reports "{source}" source')
def step_every_chore_row_reports_source(context, source: str) -> None:  # type: ignore[no-untyped-def]
    output = context.subprocess_output
    other_labels = {"project", "package", "missing"} - {source}
    found_target = False
    for line in output.splitlines():
        for other in other_labels:
            assert other not in line, (
                f"Found unexpected source label {other!r} in row:\n{line!r}\nFull output:\n{output}"
            )
        if source in line:
            found_target = True
    assert found_target, f"No row reported {source!r} source in output:\n{output}"


@then('the registry "{relpath}" contains slug "{slug}"')
def step_registry_contains_slug(context, relpath: str, slug: str) -> None:  # type: ignore[no-untyped-def]
    registry_path = context.project_root / Path(relpath)
    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    slugs = {entry.get("slug") for entry in payload.get("chores", [])}
    assert slug in slugs, (
        f"Slug {slug!r} not found in {relpath} after merge.\nAvailable slugs: {sorted(slugs)}"
    )
