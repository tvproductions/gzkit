"""Behave step definitions for constitutional invariant composition renderer (OBPI-0.0.37-02).

@covers REQ-0.0.37-02-01
@covers REQ-0.0.37-02-02
@covers REQ-0.0.37-02-04
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from behave import given, then, when  # type: ignore[import-untyped]

from gzkit.cli import main


def _invoke_capture(*args: str) -> tuple[int, str]:
    """Invoke gz CLI, return (exit_code, combined_stdout_stderr)."""
    output = io.StringIO()
    with redirect_stdout(output), redirect_stderr(output):
        try:
            code = main(list(args))
        except SystemExit as exc:
            raw = exc.code
            code = raw if isinstance(raw, int) else 1
    return 0 if code is None else int(code), output.getvalue()


def _seed_registry(root: Path) -> None:
    """Write one minimal valid invariant JSON to the registry directory.

    Also copies the canonical agents.md template into the workspace so the
    drift validator's bootstrap-safe guard (template-present check) is
    satisfied (OBPI-0.0.37-03).
    """
    inv_dir = root / ".gzkit" / "invariants"
    inv_dir.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": "CIC-test-seed",
        "claim": "Seed invariant for BDD test.",
        "structural_witness": ["gz validate --test"],
        "composition_targets": ["AGENTS.md"],
    }
    (inv_dir / "CIC-test-seed.json").write_text(json.dumps(entry), encoding="utf-8")

    template_src = Path(__file__).parent.parent.parent / "src" / "gzkit" / "templates" / "agents.md"
    if template_src.exists():
        template_dst_dir = root / ".gzkit" / "templates"
        template_dst_dir.mkdir(parents=True, exist_ok=True)
        (template_dst_dir / "agents.md").write_bytes(template_src.read_bytes())


def _render_bytes(root: Path) -> bytes:
    """Render agents-md to bytes without writing file, patching project root."""

    from gzkit.governance.compose import render_agents_md
    from gzkit.governance.invariants import load_invariants

    template_root = Path(__file__).parent.parent.parent / "src" / "gzkit" / "templates"
    invariants = load_invariants(root)
    return render_agents_md(invariants, template_root, root)


@given("the constitutional invariant registry has at least one entry")
def step_seed_registry(context) -> None:  # type: ignore[no-untyped-def]
    _seed_registry(Path.cwd())


@given("AGENTS.md contains the current rendered output")
def step_agents_md_matches(context) -> None:  # type: ignore[no-untyped-def]
    rendered = _render_bytes(Path.cwd())
    (Path.cwd() / "AGENTS.md").write_bytes(rendered)


@given("AGENTS.md contains stale content")
def step_agents_md_stale(context) -> None:  # type: ignore[no-untyped-def]
    (Path.cwd() / "AGENTS.md").write_text(
        "stale content — does not match rendered output", encoding="utf-8"
    )


@when('I run "gz governance render --target agents-md --stdout" twice')
def step_run_stdout_twice(context) -> None:  # type: ignore[no-untyped-def]
    code1, out1 = _invoke_capture("governance", "render", "--target", "agents-md", "--stdout")
    code2, out2 = _invoke_capture("governance", "render", "--target", "agents-md", "--stdout")
    context.stdout_run1 = out1
    context.stdout_run2 = out2
    context.exit_code = code1


@when('I run "gz governance render --target agents-md --check"')
def step_run_check(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("governance", "render", "--target", "agents-md", "--check")
    context.exit_code = code
    context.output = output


@when('I run "gz governance render --target agents-md"')
def step_run_write(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("governance", "render", "--target", "agents-md")
    context.exit_code = code
    context.output = output


@when('I run "gz governance render --target skill-readme"')
def step_run_unsupported_target(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("governance", "render", "--target", "skill-readme")
    context.exit_code = code
    context.output = output


@when('I run "gz governance render --help"')
def step_run_help(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("governance", "render", "--help")
    context.exit_code = code
    context.output = output


@then("AGENTS.md exists in the workspace")
def step_agents_md_exists(context) -> None:  # type: ignore[no-untyped-def]
    assert (Path.cwd() / "AGENTS.md").exists(), "AGENTS.md was not written"


@then("the two outputs are byte-identical")
def step_outputs_byte_identical(context) -> None:  # type: ignore[no-untyped-def]
    assert context.stdout_run1 == context.stdout_run2, (
        f"Outputs are not byte-identical. Run 1 length={len(context.stdout_run1)}, "
        f"Run 2 length={len(context.stdout_run2)}"
    )


# Note: the following shared steps are defined in gz_steps.py and reused here:
# - @then("the command exits with code {expected:d}")
# - @then("the command exits non-zero") / @then("the command exits with a non-zero code")
# - @then('the output contains "{text}"')
# The constitutional invariant steps below are scenario-specific only.


# -- OBPI-0.0.37-03 — Composition drift validator steps --


@given("AGENTS.md matches the rendered registry output")
def step_agents_md_matches_registry(context) -> None:  # type: ignore[no-untyped-def]
    rendered = _render_bytes(Path.cwd())
    (Path.cwd() / "AGENTS.md").write_bytes(rendered)


@given("AGENTS.md differs from the rendered registry output")
def step_agents_md_differs_registry(context) -> None:  # type: ignore[no-untyped-def]
    (Path.cwd() / "AGENTS.md").write_text(
        "drifted content — does not match rendered output", encoding="utf-8"
    )


@when('I run "gz validate --invariant-coherence"')
def step_run_invariant_coherence(context) -> None:  # type: ignore[no-untyped-def]
    code, output = _invoke_capture("validate", "--invariant-coherence")
    context.exit_code = code
    context.output = output


@then('a "composition_rendered" event is appended to the ledger')
def step_composition_rendered_in_ledger(context) -> None:  # type: ignore[no-untyped-def]
    ledger_path = Path.cwd() / ".gzkit" / "ledger.jsonl"
    assert ledger_path.exists(), "ledger.jsonl does not exist"
    found = False
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event") == "composition_rendered":
            found = True
            break
    assert found, "no composition_rendered event found in ledger.jsonl"
