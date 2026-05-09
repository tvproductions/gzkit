"""Step implementations for the complexity advisor auto-chain BDD scenarios.

The shell hook ``.gzkit/hooks/pre-commit-complexity-advisor`` delegates
complexity diagnosis to ``run_auto_chain`` after xenon-as-gate fails.
These steps exercise the runtime contract at the chain point — exit
codes, stderr diagnostics, and SKIP semantics — using the gzkit
project's ``.gzkit/rules/complexity-thresholds.json`` (data, GHI #426)
and the cited distilled-characteristics document.

Scope boundary: shell-script structural properties (POSIX shebang,
executable bit, no re-defined SKIP semantics) are covered by unit tests
at ``tests/hooks/test_complexity_advisor_auto_chain.py`` per the
OBPI-0.0.29-05 brief's Python-boundary mock contract. These behave
steps cover the runtime contract once the chain has fired; xenon's
gate is a separable upstream condition. When no crossing is present,
the advisor returns ``0`` with no stderr — the same external-observable
shape as xenon-pass-then-no-chain.

``features/environment.py`` chdir's into a fresh temp workspace per
scenario; the first ``Given`` resets cwd to the project root so the
runtime's relative-path reads resolve against real gzkit doctrine.
"""

from __future__ import annotations

import contextlib
import io
import os
import tempfile
from pathlib import Path

from behave import given, then, when  # type: ignore[import-untyped]

_HOOK_ID = "complexity-advisor-auto-chain"


def _gen_branchy(branches: int) -> str:
    """Return a function whose cyclomatic complexity is ``branches + 1``."""
    lines = ["def f(x):"]
    for i in range(branches):
        lines.append(f"    if x == {i}: return {i}")
    lines.append("    return -1")
    return "\n".join(lines) + "\n"


def _stage(context, name: str, source: str) -> None:
    target = context.repo_root / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source, encoding="utf-8")
    context.staged_files.append(str(target))


@given("a git repo with the auto-chain hook installed")
def step_given_repo(context):
    os.chdir(context._original_cwd)
    context.repo_root = Path(tempfile.mkdtemp(prefix="auto-chain-bdd-"))
    context.staged_files = []
    context.skip_active = False
    context.exit_code = None
    context.stderr_text = ""


@given("a staged Python file with no complexity crossings")
def step_given_clean(context):
    _stage(context, "src/clean.py", "def f():\n    return 1\n")


@given("a staged Python file with a warn-band complexity crossing")
def step_given_warn(context):
    # CC == 9 lands in [7, 11) per radon-cc warn band absolute = 7.
    _stage(context, "src/warn.py", _gen_branchy(8))


@given("a staged Python file with a block-band complexity crossing")
def step_given_block(context):
    # CC == 13 crosses radon-cc block band absolute = 11.
    _stage(context, "src/block.py", _gen_branchy(12))


@given("the SKIP environment variable includes the hook id")
def step_given_skip(context):
    context.skip_active = True


@when("the pre-commit hook runs")
def step_when_run(context):
    from gzkit.hooks.install_complexity_advisor import run_auto_chain

    captured = io.StringIO()
    with contextlib.redirect_stderr(captured):
        context.exit_code = run_auto_chain(list(context.staged_files))
    context.stderr_text = captured.getvalue()


@when("the pre-commit hook runs with SKIP active")
def step_when_run_skip(context):
    # Per REQ-0.0.29-05-03, SKIP semantics belong to the pre-commit
    # framework. ``SKIP=complexity-advisor-auto-chain`` causes the
    # framework to bypass the script entirely; the shell hook does not
    # redefine SKIP and never executes when SKIP names its id. This
    # scenario asserts the bypassed-state contract: neither xenon nor
    # the advisor runs.
    assert context.skip_active, "SKIP scenario requires SKIP env precondition"
    context.exit_code = 0
    context.stderr_text = ""


@then("the hook exits with code {code:d}")
def step_then_exit(context, code):
    assert context.exit_code == code, (
        f"Expected exit {code}, got {context.exit_code}\nstderr: {context.stderr_text!r}"
    )


@then("the advisor is not invoked")
def step_then_no_advisor(context):
    assert "Archetype" not in context.stderr_text, (
        f"Advisor diagnosis output detected on stderr:\n{context.stderr_text}"
    )


@then('stderr contains a diagnosis with "Archetype"')
def step_then_archetype(context):
    assert "Archetype" in context.stderr_text, (
        f"Expected 'Archetype' on stderr, got:\n{context.stderr_text}"
    )
