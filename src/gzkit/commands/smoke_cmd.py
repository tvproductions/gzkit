"""`gz smoke` — run the smoke/BVT tier against its declared budget (GHI #724).

The tier's ceiling lived in `.gzkit/rules/tests.md` as prose with no enforcement
consumer, so a 4.5x breach was invisible to everything except whoever happened to
time a run. This is the consumer.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.commands.common import console
from gzkit.config import GzkitConfig
from gzkit.smoke import SMOKE_BUDGET_SECONDS, run_smoke, smoke_marked_files

_EXIT_OK = 0
_EXIT_TEST_FAILURE = 1
_EXIT_POLICY_BREACH = 3


def smoke_gate(project_root: Path | None = None, budget: float | None = None) -> int:
    """Run the smoke tier and return its exit code without exiting.

    Split from :func:`smoke_cmd` so the decision is exercisable in a unit test.
    Folding the two together would leave the gate's own branches provable only
    by catching `SystemExit`, which reads as "the command exited" rather than
    "the policy fired" — a distinction that matters when the policy has three
    outcomes and only one of them means broken code.

    Exit codes follow `.claude/rules/cli.md`: 1 for a test failure the author
    can fix in code, 3 for a policy breach — an empty tier or an over-budget run
    are both contract violations rather than broken code.
    """
    root = project_root or Path.cwd()
    budget = SMOKE_BUDGET_SECONDS if budget is None else budget

    if not smoke_marked_files(root):
        if not GzkitConfig.load(root / ".gzkit.json").smoke.required:
            console.print(
                "[yellow]Smoke tier is empty[/yellow] — no test under `tests/` carries "
                "`@smoke`, and this project has not declared `smoke.required`.\n"
                "Passing advisory: a freshly scaffolded project has no tier yet, and "
                "gzkit does not impose one on adopters.\n"
                "Next step (optional): mark a build-verification test with "
                '`from gzkit.smoke import smoke`, then set `"smoke": {"required": true}` '
                "in `.gzkit.json` to make the tier binding."
            )
            return _EXIT_OK
        console.print(
            "[red]Smoke tier is empty[/red] — no test under `tests/` carries `@smoke`, "
            "but this project declares `smoke.required`.\n"
            "An empty tier satisfies any budget trivially, which is the green-by-emptiness "
            "shape `gz validate --qc-binding` refuses (ADR-0.0.74 Boundary Invariant #6).\n"
            "Next step: mark at least one build-verification test with "
            "`from gzkit.smoke import smoke` and the `@smoke` decorator."
        )
        return _EXIT_POLICY_BREACH

    result, elapsed = run_smoke(root)
    ran = result.testsRun
    console.print(f"\nRan {ran} smoke test(s) in {elapsed:.2f}s (budget {budget:.0f}s)")

    if not result.wasSuccessful():
        console.print(
            f"[red]Smoke tier FAILED[/red]: {len(result.failures)} failure(s), "
            f"{len(result.errors)} error(s). The build does not verify.\n"
            "Next step: fix the reported test(s), then re-run `uv run gz smoke`."
        )
        return _EXIT_TEST_FAILURE

    if elapsed > budget:
        console.print(
            f"[red]Smoke budget breached[/red]: {elapsed:.2f}s over a {budget:.0f}s ceiling.\n"
            "`.gzkit/rules/tests.md` § General Rules binds this tier to the ceiling so the "
            "build-verification loop stays cheap enough to actually run. The full unit tier "
            "has its own, larger budget precisely so this one can stay small.\n"
            "Next step: move the slow member out of the smoke tier (drop its `@smoke`), or "
            "amend the ceiling in `.gzkit/rules/tests.md` with rationale."
        )
        return _EXIT_POLICY_BREACH

    console.print("[green]Smoke tier PASSED[/green] within budget.")
    return _EXIT_OK


def smoke_cmd(project_root: Path | None = None, budget: float | None = None) -> None:
    """CLI entrypoint: run the gate and surface its verdict as an exit code.

    `gzkit.cli.main` discards a handler's return value and reads `SystemExit`,
    so a gate that only *returned* 3 would report success — the failure this
    wrapper exists to prevent.
    """
    code = smoke_gate(project_root, budget)
    if code:
        raise SystemExit(code)
