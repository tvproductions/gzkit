"""BDD steps for heavy-lane governance behavior.

@covers REQ-0.25.0-33-05
"""

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
from gzkit.events import EventAnchor
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    gate_checked_event,
    obpi_created_event,
    obpi_receipt_emitted_event,
)


def _invoke(args: list[str]) -> tuple[int, str]:
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(args)
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


def _init_with_agent_surfaces(mode: str) -> None:
    """Extend _quick_init with agent-contract scaffolding.

    Scenarios that assert on AGENTS.md content or require the full agent
    control-surface tree (AGENTS.md, CLAUDE.md, hooks, skill mirrors) need
    what real ``gz init`` produces. ``_quick_init`` alone is too minimal;
    the full ``gz init`` CLI path is too slow (~2s per scenario).
    """
    from tests.commands.common import _quick_init  # noqa: PLC0415

    from gzkit.config import GzkitConfig
    from gzkit.skills import scaffold_core_skills
    from gzkit.sync_surfaces import sync_all

    _quick_init(mode=mode)
    config = GzkitConfig.load(Path(".gzkit.json"))
    scaffold_core_skills(Path.cwd(), config)
    sync_all(Path.cwd(), config)


@given("the workspace is initialized in heavy mode")
def step_init_heavy(_context) -> None:  # type: ignore[no-untyped-def]
    from tests.commands.common import _quick_init  # noqa: PLC0415

    _quick_init(mode="heavy")


@given("the workspace is initialized")
def step_init_default(_context) -> None:  # type: ignore[no-untyped-def]
    from tests.commands.common import _quick_init  # noqa: PLC0415

    _quick_init(mode="lite")


@given("the workspace is initialized with agent surfaces in heavy mode")
def step_init_heavy_with_surfaces(_context) -> None:  # type: ignore[no-untyped-def]
    _init_with_agent_surfaces(mode="heavy")


@given("the workspace is initialized with agent surfaces")
def step_init_default_with_surfaces(_context) -> None:  # type: ignore[no-untyped-def]
    _init_with_agent_surfaces(mode="lite")


@given("a heavy ADR exists")
def step_plan_heavy_adr(_context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke(["plan", "create", "0.1.0", "--lane", "heavy", "--kind", "feature"])
    assert code == 0, output


@given("ADR-0.1.0 exists")
def step_plan_default_adr(_context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke(["plan", "create", "0.1.0", "--kind", "feature"])
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
            anchor=EventAnchor(commit=head, semver="0.1.0"),
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


@then('the file "{path}" does not exist')
def step_file_not_exists(_context, path: str) -> None:  # type: ignore[no-untyped-def]
    assert not Path(path).exists(), f"Expected {path} to NOT exist"


@then('ledger event "{event}" has field "{key}" equal to "{value}"')
def step_ledger_event_field(_context, event: str, key: str, value: str) -> None:  # type: ignore[no-untyped-def]
    ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
    matches = [
        json.loads(line)
        for line in ledger_text.splitlines()
        if line.strip() and json.loads(line).get("event") == event
    ]
    assert matches, f"No ledger event named {event!r} in:\n{ledger_text}"
    last = matches[-1]
    actual = last.get(key)
    assert str(actual) == value, (
        f"Event {event!r} field {key!r}={actual!r}, expected {value!r}\nFull event: {last}"
    )


@given('a pool ADR "{adr_id}" with target scope exists')
def step_seed_pool_adr_with_scope(_context, adr_id: str) -> None:  # type: ignore[no-untyped-def]
    config = GzkitConfig.load(Path(".gzkit.json"))
    pool_dir = Path(config.paths.adrs) / "pool"
    pool_dir.mkdir(parents=True, exist_ok=True)
    pool_file = pool_dir / f"{adr_id}.md"
    pool_file.write_text(
        "---\n"
        f"id: {adr_id}\n"
        "status: Pool\n"
        "parent: PRD-GZKIT-1.0.0\n"
        "lane: heavy\n"
        "---\n\n"
        f"# {adr_id}: Sample Work\n\n"
        "## Status\n\nPool\n\n"
        "## Intent\n\nTurn sample pool work into executable tracked delivery.\n\n"
        "## Target Scope\n\n"
        "- Define runtime command contract\n"
        "- Persist machine-readable stage state\n"
        "- Expose structured stage outputs\n\n"
        "## Non-Goals\n\n- No external orchestrator\n",
        encoding="utf-8",
    )
    ledger = Ledger(Path(".gzkit/ledger.jsonl"))
    ledger.append(adr_created_event(adr_id, "", "heavy"))
