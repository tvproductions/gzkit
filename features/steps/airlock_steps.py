"""BDD steps for the gz airlock-IN membrane surface (ADR-0.33.0, OBPI-0.33.0-02).

The airlock-IN preflight resolves a target OBPI's brief from the real
``docs/design/adr`` tree, so the scenario runs against the actual repository
root rather than the per-scenario tempdir. This step seeds
``context.project_root`` to the original working tree captured by
``features/environment.py``; the subprocess ``When``/``Then`` steps are reused
verbatim from ``chores_distribution_steps.py``.

@covers REQ-0.33.0-02-06
"""

from __future__ import annotations

from behave import given


@given("the gzkit repository working tree")
def step_repo_working_tree(context) -> None:
    context.project_root = context._original_cwd
    context.subprocess_exit_code = None
    context.subprocess_output = ""
