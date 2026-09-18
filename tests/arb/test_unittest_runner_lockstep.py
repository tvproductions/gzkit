"""The unit-test invocation is one value, not three agreeing copies (GHI #856).

The accelerator (`unittest-parallel`, GHI #512) was adopted on the pre-commit
hook and on the `gz check` gate and never carried to the attestation surface, so
the command an agent runs *most* often -- the one proving "Tests pass" for
Gate 5 -- was the slow one. Measured 2026-08-27 at `2c81cb7d`, 10-core M-series,
same 8,912 tests, both exit 0: 144.23s serial against 41.34s parallel. 3.49x,
~103 seconds per attestation.

The repair aligns the two commands. This module pins that they cannot drift
apart again, which is a different and stronger claim: `quality.run_tests` used
to RE-SPELL the invocation, and a re-spelled copy is free to diverge the moment
either side is edited. `run_typecheck` has DERIVED from the canonical entry
since GHI #199 for exactly this reason, and
`tests/arb/test_typecheck_scope_lockstep.py` is this module's sibling -- the
same shape applied to the entry that had it first.

Each derivation test MUTATES the canonical entry and asserts the consumer
follows. A test that only compared the two current values would pass equally
well against two independently-spelled copies that happen to agree today, which
is the state that shipped this defect.

The pre-commit hook is the one copy that cannot derive (YAML read by another
tool before Python runs), so it is pinned by equality instead.
"""

from __future__ import annotations

import shlex
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

import yaml

from gzkit.arb.validator import CANONICAL_STEP_COMMANDS
from gzkit.cli.main import _build_parser
from gzkit.commands.obpi_stages import BASELINE_VERIFICATION
from gzkit.pipeline_dispatch import DispatchTask, TaskComplexity, compose_implementer_prompt
from gzkit.pipeline_verification import compose_verification_prompt
from gzkit.quality import run_tests

_SENTINEL_COMMAND = ["uv", "run", "sentinel-runner", "-s", "sentinel-tests"]

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _argv_of(observed: str | list[str]) -> list[str]:
    return shlex.split(observed) if isinstance(observed, str) else list(observed)


def _pre_commit_entry(repo_root: Path, hook_id: str) -> str:
    """Return the ``entry:`` string of hook *hook_id*, or "" when absent."""
    config = yaml.safe_load((repo_root / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    for repo in config.get("repos", []):
        for hook in repo.get("hooks", []):
            if hook.get("id") == hook_id:
                return str(hook.get("entry", ""))
    return ""


class TestGateDerivesFromCanon(unittest.TestCase):
    """The `gz check` test tier READS the canonical entry rather than re-spelling it."""

    def _captured_argv(self) -> list[str]:
        with (
            tempfile.TemporaryDirectory() as tmpdir,
            mock.patch("gzkit.quality.run_command") as runner,
        ):
            run_tests(Path(tmpdir))
            runner.assert_called_once()
            return _argv_of(runner.call_args.args[0])

    def test_quality_gate_follows_a_changed_canonical_command(self) -> None:
        """Move the canonical value; the gate's argv must move with it."""
        with (
            mock.patch.dict(CANONICAL_STEP_COMMANDS, {"unittest": _SENTINEL_COMMAND}),
            mock.patch("gzkit.quality.run_command") as runner,
            tempfile.TemporaryDirectory() as tmpdir,
        ):
            run_tests(Path(tmpdir))
            observed = runner.call_args.args[0]

        self.assertEqual(
            _argv_of(observed),
            _SENTINEL_COMMAND,
            msg=(
                "run_tests did not follow the canonical command. It is re-spelling "
                "the invocation instead of reading it, which is what let the "
                "accelerator land on the gate and miss attestation (GHI #856)."
            ),
        )

    def test_gate_and_canon_agree_on_the_live_value(self) -> None:
        """For the command as shipped, the gate lands on the canonical argv."""
        self.assertEqual(self._captured_argv(), CANONICAL_STEP_COMMANDS["unittest"])


class TestCanonicalInvocationIsTheAccelerator(unittest.TestCase):
    """Assert the PROPERTIES that make the parallel runner fit to attest.

    A literal-equality test here would only restate the value this module
    already reads. These assert the three reasons the swap was allowed at all,
    so an edit that quietly drops one fails with the motivation attached.
    """

    def test_canonical_unittest_runs_the_parallel_accelerator(self) -> None:
        self.assertIn(
            "unittest-parallel",
            CANONICAL_STEP_COMMANDS["unittest"],
            msg=(
                "The canonical 'Tests pass' invocation fell back to the serial "
                "runner. Measured 2026-08-27: 144.23s serial vs 41.34s parallel "
                "over the same 8,912 tests -- ~103s per attestation (GHI #856)."
            ),
        )

    def test_canonical_unittest_buffers_passing_output(self) -> None:
        """`--buffer` keeps passing negative-path prose out of the log (GHI #723)."""
        self.assertIn("--buffer", CANONICAL_STEP_COMMANDS["unittest"])

    def test_canonical_unittest_does_not_fetch_its_runner_at_run_time(self) -> None:
        """The receipt's runner must be the PINNED one, never `--with`-resolved.

        This is the condition on which the swap was ruled (operator, 2026-08-27).
        An ARB receipt is durable EVIDENCE; `uv run --with unittest-parallel`
        resolves from the network at invocation time, so the version backing a
        receipt would be whatever `uv` picked that day. Asserted as the ABSENCE
        of `--with` rather than the presence of a version, because the pin lives
        in `pyproject.toml` and is proven by its own test below.
        """
        self.assertNotIn(
            "--with",
            CANONICAL_STEP_COMMANDS["unittest"],
            msg=(
                "The canonical attestation command fetches its test runner at run "
                "time. That is the dependency-provenance objection recorded at "
                "`canonical_steps.py` and re-ruled in GHI #856 by PINNING the "
                "runner -- not by accepting an unpinned one."
            ),
        )


class TestRunnerIsPinnedLikeEveryOtherVerifier(unittest.TestCase):
    """The accelerator is a declared dependency, not a run-time fetch.

    `.pre-commit-config.yaml` justified `--with` as "matching the un-pinned
    xenon/gitleaks precedent". That precedent does not exist: `xenon` is a
    pinned `dev` entry invoked as `uv run xenon`, and `gitleaks` is a native
    binary rather than a Python package. This test pins the convention the
    codebase actually follows, so the claim cannot be re-derived from memory.
    """

    def _dev_group(self) -> list[str]:
        data = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        return list(data["dependency-groups"]["dev"])

    def _names(self) -> set[str]:
        return {entry.split(">")[0].split("=")[0].strip() for entry in self._dev_group()}

    def test_unittest_parallel_is_a_declared_dev_dependency(self) -> None:
        self.assertIn(
            "unittest-parallel",
            self._names(),
            msg=(
                "The runner backing the canonical 'Tests pass' receipt is not a "
                "declared dependency, so its version is whatever the network "
                "served that day (GHI #856)."
            ),
        )

    def test_the_cited_xenon_precedent_is_pinned_too(self) -> None:
        """Negative control on the rationale, not on the value."""
        self.assertIn("xenon", self._names())
        self.assertEqual(
            shlex.split(_pre_commit_entry(_REPO_ROOT, "xenon-complexity"))[:3],
            ["uv", "run", "xenon"],
            msg="xenon is the precedent cited for `--with`; it does not use `--with`.",
        )


class TestAgentContractMatchesCanon(unittest.TestCase):
    """The `gz-arb` skill's invocation list is the surface agents actually read.

    Until 2026-09-17 that list was a table in `AGENTS.md` § Attestation; the
    operator ruled it out of the per-turn contract (GHI #921) and the contract now
    points at the skill, so the lockstep witness follows the list to its home.

    This is the cause that had NO test. `gz validate --cli-alignment` resolves
    the `gz` verbs in a documented command but not the argv after `--`, so the
    row could name a stale runner indefinitely: an agent following the contract
    verbatim would emit a receipt the provenance check then rejects, and the
    contract itself would be the thing lying.

    Compared as tokens rather than as a raw substring so table padding and
    formatting churn cannot make this pass or fail for the wrong reason.
    """

    def _attestation_row_command(self) -> list[str]:
        """Return the argv of the documented tests-pass invocation."""
        skill = _REPO_ROOT / ".gzkit" / "skills" / "gz-arb" / "SKILL.md"
        for line in skill.read_text(encoding="utf-8").splitlines():
            stripped = line.strip().lstrip("- ").strip()
            if stripped.startswith("`uv run gz arb step --name unittest --"):
                return shlex.split(stripped.split("`")[1])
        return []

    def test_attestation_table_row_equals_the_canonical_command(self) -> None:
        argv = self._attestation_row_command()
        self.assertNotEqual(argv, [], msg="No tests-pass invocation found in gz-arb/SKILL.md")

        prefix = ["uv", "run", "gz", "arb", "step", "--name", "unittest", "--"]
        self.assertEqual(
            argv,
            prefix + CANONICAL_STEP_COMMANDS["unittest"],
            msg=(
                "AGENTS.md § Attestation names a different 'Tests pass' invocation "
                "than CANONICAL_STEP_COMMANDS. An agent following the contract would "
                "emit a receipt that `gz arb validate` rejects as non-canonical "
                "provenance — the contract itself carrying the drift (GHI #856). "
                "AGENTS.md is played back from a committed rendition, so the repair "
                "is `gz content compose`/`commit` then `gz agent sync "
                "control-surfaces`, never a hand edit."
            ),
        )


class TestPreCommitHookMatchesCanon(unittest.TestCase):
    """The one copy that cannot derive is pinned by equality instead."""

    def test_pre_commit_unittest_entry_equals_the_canonical_command(self) -> None:
        entry = _pre_commit_entry(_REPO_ROOT, "unittest")

        self.assertNotEqual(entry, "", msg="No `unittest` hook found in .pre-commit-config.yaml")
        self.assertEqual(
            shlex.split(entry),
            CANONICAL_STEP_COMMANDS["unittest"],
            msg=(
                "The pre-commit `unittest` hook runs a different suite invocation "
                "than the attestation surface. That divergence is GHI #856 itself, "
                "relocated to the hook that runs most often."
            ),
        )


_SERIAL_FULL_SUITE = "-m unittest -q"


def _unittest_step_argv(commands: list[str]) -> list[str]:
    """Return the argv after ``--`` of the ``unittest``-labelled ARB step."""
    for command in commands:
        if command.startswith("uv run gz arb step --name unittest -- "):
            return shlex.split(command.split(" -- ", 1)[1])
    return []


class TestPipelineBaselineMatchesCanon(unittest.TestCase):
    """Stage 3 emits its `unittest` receipt through the canonical command.

    The 2026-08-27 close of GHI #856 called its enumeration exhaustive over
    receipt-bearing spellings and missed this one: the pipeline baseline kept the
    serial argv, which `arb/validator.py` retires at the swap boundary -- receipt
    `arb-step-unittest-7161a74d...` (2026-09-08) is that rejection, observed.
    """

    def test_stage3_unittest_step_runs_the_canonical_argv(self) -> None:
        self.assertEqual(
            _unittest_step_argv(BASELINE_VERIFICATION),
            CANONICAL_STEP_COMMANDS["unittest"],
            msg=(
                "The pipeline's Stage 3 baseline wraps a different suite invocation "
                "than the one `gz arb validate` accepts under the `unittest` label, "
                "so the governed pipeline emits a receipt its own validator refuses."
            ),
        )


class TestArbHelpShowsTheCanonicalStep(unittest.TestCase):
    """`gz arb` help examples under the `unittest` label are the accepted argv."""

    def _epilogs(self) -> list[str]:
        parser = _build_parser()
        arb = parser._subparsers._group_actions[0].choices["arb"]  # noqa: SLF001
        step = arb._subparsers._group_actions[0].choices["step"]  # noqa: SLF001
        return [arb.epilog or "", step.epilog or ""]

    def test_unittest_examples_carry_the_canonical_argv(self) -> None:
        canonical = shlex.join(CANONICAL_STEP_COMMANDS["unittest"])
        for epilog in self._epilogs():
            examples = [ln.strip() for ln in epilog.splitlines() if "--name unittest" in ln]
            self.assertTrue(examples, msg="No `--name unittest` example found in the epilog")
            for example in examples:
                self.assertEqual(example.split(" -- ", 1)[1], canonical)


class TestSubagentPromptsPrescribeTheParallelSuite(unittest.TestCase):
    """Dispatch prompts name `gz test`, never the serial full-suite spelling.

    Operator ruling 2026-09-18: "We want parallel everywhere unless you can give
    me a good reason why we can't." A scoped single-module run has nothing to
    parallelize and stays as it is; the FULL-suite fallback is what moves.
    """

    def test_implementer_prompt_verifies_with_gz_test(self) -> None:
        task = DispatchTask(
            task_id=1,
            description="Add feature X",
            allowed_paths=["src/gzkit/example.py"],
            test_expectations=["test_feature_x passes"],
            complexity=TaskComplexity.SIMPLE,
            model="haiku",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            prompt = compose_implementer_prompt(
                task, ["REQ text"], why="lockstep", project_root=Path(tmpdir)
            )
        self.assertNotIn(_SERIAL_FULL_SUITE, prompt)
        self.assertIn("`uv run gz test`", prompt)

    def test_verifier_prompt_falls_back_to_gz_test(self) -> None:
        prompt = compose_verification_prompt([])
        self.assertNotIn(_SERIAL_FULL_SUITE, prompt)
        self.assertIn("`uv run gz test`", prompt)


if __name__ == "__main__":
    unittest.main()
