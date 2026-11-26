"""What git-sync's flags do is stated once, and every runtime output agrees (GHI #1390).

The git-sync skill is the statement: `--lint` and `--test` default off, a
routine sync, an OBPI Stage 5 sync and an ADR closeout sync all run
`gz git-sync --apply`, and a release runs `gz check --full` before it. The
runtime prints that command at two moments and describes the flags in
`--help`; each must agree with the statement, not with the retired
"always pass --lint --test" ritual (operator, 2026-11-26: *"we need to be
explicit in all cases for all combinations"*; *"B"*, repair the pipeline
runtime here).
"""

import argparse
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from gzkit.cli.main import _build_parser
from gzkit.commands.ceremony_state import CeremonyState
from gzkit.commands.ceremony_steps import render_step_11_complete
from gzkit.commands.obpi_stages import _build_sync_stage_steps
from gzkit.commands.version_sync import write_in_flight_release_manifest
from gzkit.pipeline_markers import pipeline_stage_output

_SYNC = "uv run gz git-sync --apply"


def _git_sync_actions() -> dict[str, argparse.Action]:
    parser = _build_parser()
    commands = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
    git_sync = commands.choices["git-sync"]
    return {opt: action for action in git_sync._actions for opt in action.option_strings}


def _written_manifest() -> str:
    """Return the manifest text `gz closeout` files at bump time, written to a temp root."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        rel = write_in_flight_release_manifest(root, "9.9.0", "ADR-9.9.0")
        return (root / rel).read_text(encoding="utf-8")


class TestPipelineSyncIsTheSkillsRitual(unittest.TestCase):
    """OBPI Stage 5 syncs with bare `--apply` (`stage-5-sync-and-account.md` steps 6 and 9)."""

    def test_stage_5_runs_bare_apply(self) -> None:
        steps = _build_sync_stage_steps(
            obpi_id="OBPI-0.0.29-08",
            resolved_parent="ADR-0.0.29",
            attestor="g0",
            evidence_json='{"value_narrative":"x","key_proof":"y","attestation_text":"t"}',
        )
        sync_commands = [cmd for cmd, _ in steps if "git-sync" in cmd]
        self.assertEqual(sync_commands, [_SYNC])

    def test_the_sync_position_states_bare_apply(self) -> None:
        output = pipeline_stage_output("OBPI-0.0.29-08", "sync")
        self.assertEqual(output["next_command"], _SYNC)


class TestCloseoutCompletionNamesTheRitual(unittest.TestCase):
    """The closeout ceremony syncs with bare `--apply` (`gz-adr-closeout-ceremony` rule 10)."""

    def test_completion_prescribes_bare_apply(self) -> None:
        now = datetime.now(UTC).isoformat()
        state = CeremonyState(
            adr_id="ADR-0.1.0",
            current_step=11,
            is_foundation=False,
            started_at=now,
            updated_at=now,
        )
        text = render_step_11_complete(state)
        self.assertIn(f"`{_SYNC.removeprefix('uv run ')}`", text)
        self.assertNotIn("--lint", text)
        self.assertNotIn("--test", text)


class TestGitSyncHelpStatesWhatEachFlagRunsOutputContract(unittest.TestCase):
    """# output-contract: `--help` is where an operator reads what a flag runs."""

    def test_the_gates_default_off(self) -> None:
        actions = _git_sync_actions()
        self.assertFalse(actions["--lint"].default)
        self.assertFalse(actions["--test"].default)

    def test_test_help_names_the_full_suite_and_no_commit_hook(self) -> None:
        actions = _git_sync_actions()
        for flag in ("--test", "--no-test"):
            with self.subTest(flag=flag):
                help_text = actions[flag].help or ""
                self.assertIn("full unit suite", help_text)
                self.assertNotIn("pre-commit", help_text)

    def test_each_flag_says_what_sync_py_runs_for_it(self) -> None:
        """Each help line names the step `_execute_git_sync` runs or skips for that flag.

        This holds the help text to the statement; it does not exercise sync.py.
        """
        actions = _git_sync_actions()
        # _run_sync_prechecks and _run_post_sync_lint: whole-tree gz lint, before and after.
        lint = actions["--lint"].help or ""
        self.assertIn("whole-tree", lint)
        self.assertIn("at the end", lint)
        self.assertIn("whole-tree", actions["--no-lint"].help or "")
        # _execute_git_sync: `git add -A`, refused by the src/ and tests/ sweep guard.
        auto_add = actions["--auto-add"].help or ""
        self.assertIn("git add -A", auto_add)
        self.assertIn("src/", auto_add)
        # --no-auto-add skips the sweep guard too, so whatever is staged is committed.
        no_auto_add = actions["--no-auto-add"].help or ""
        self.assertIn("already staged", no_auto_add)
        self.assertIn("no src/ or tests/ refusal", no_auto_add)
        # _pull_if_needed takes no allow_push, so --no-push still rebases.
        self.assertIn("rebase", actions["--no-push"].help or "")

    def test_description_names_both_hook_stages_and_the_full_suite(self) -> None:
        parser = _build_parser()
        commands = next(a for a in parser._actions if isinstance(a, argparse._SubParsersAction))
        description = commands.choices["git-sync"].description or ""
        # _plan_git_sync fetches before _execute_git_sync stages or commits.
        self.assertTrue(description.startswith("Fetch, stage, commit, rebase and push"))
        self.assertIn("pre-commit", description)
        self.assertIn("pre-push", description)
        self.assertIn("full unit suite", description)


class TestReleaseManifestNamesTheReleaseSweep(unittest.TestCase):
    """The in-flight manifest keeps `gz check --full` runnable (gz-patch-release Step 4c)."""

    def test_manifest_names_the_full_sweep_not_the_sync_flags(self) -> None:
        text = _written_manifest()
        self.assertIn("`gz check --full`", text)
        self.assertNotIn("--lint --test", text)


if __name__ == "__main__":
    unittest.main()
