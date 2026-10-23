"""`gz lint` and the surfaces that tell an agent how to lint (RO-9 tranche 4).

Ruff selects ALL under ``data/ruff_baseline.json``, so bare ``ruff check`` reports
every held finding and exits 1 on a tree the gate passes. The verb routes each
mode to the baseline's verdict, and every surface that prescribes a lint command
to an agent names ``gz lint``.
"""

import io
import tempfile
import unittest
from collections import Counter
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from rich.console import Console

from gzkit import ruff_baseline
from gzkit.arb.advisor import _recommendations_for_counts
from gzkit.arb.patterns import RULE_GUIDANCE
from gzkit.cli import parser_handler_manifest
from gzkit.cli.main import main
from gzkit.commands import quality as quality_cmd
from gzkit.governance.trust_audits import _qc_nc_entrypoints
from gzkit.governance.trust_audits._qc_claim_delegations import QC_CLAIM_DELEGATIONS
from gzkit.hooks.claude import _claude_hooks_readme
from gzkit.pipeline_dispatch import DispatchTask, TaskComplexity, compose_implementer_prompt
from gzkit.quality import QualityResult

_OK = QualityResult(success=True, command="x", stdout="", stderr="", returncode=0)
_BAD = QualityResult(success=False, command="x", stdout="", stderr="", returncode=1)
_BARE = "ruff check . --fix"


class LintVerbRoutingTest(unittest.TestCase):
    """Each mode of `gz lint` reaches the baseline's verdict."""

    def setUp(self) -> None:
        self.root = Path("/repo")
        patcher = mock.patch.object(quality_cmd, "get_project_root", return_value=self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _lint(self, *args: object, width: int = 200, **kwargs: object) -> str:
        out = io.StringIO()
        with mock.patch.object(quality_cmd, "console", Console(file=out, width=width)):
            quality_cmd.lint(*args, **kwargs)
        return out.getvalue()

    def test_no_paths_runs_the_whole_lint_step(self) -> None:
        with mock.patch.object(quality_cmd, "run_lint", return_value=_OK) as step:
            self._lint()
        step.assert_called_once_with(self.root)

    def test_named_paths_run_ruff_alone_on_them(self) -> None:
        with (
            mock.patch.object(quality_cmd, "run_ruff_against_baseline", return_value=_OK) as ruff,
            mock.patch.object(quality_cmd, "run_lint") as step,
        ):
            self._lint(["a.py"], fix=True)
        ruff.assert_called_once_with(self.root, ["a.py"], fix=True)
        step.assert_not_called()

    def test_fix_alone_fixes_the_whole_tree(self) -> None:
        with mock.patch.object(quality_cmd, "run_ruff_against_baseline", return_value=_OK) as ruff:
            self._lint(None, fix=True)
        ruff.assert_called_once_with(self.root, fix=True)

    def test_each_finding_prints_on_one_line_however_narrow_the_console(self) -> None:
        """`path:line:col RULE message` stays greppable: Rich does not wrap it."""
        found = "src/gzkit/example_module.py:12:5 PLC0415 `import` should be at the top-level"
        warned = "warning: Ruff could not read one optional configuration value here"
        result = QualityResult(success=True, command="x", stdout=found, stderr=warned, returncode=0)
        with mock.patch.object(quality_cmd, "run_lint", return_value=result):
            text = self._lint(width=40)
        self.assertIn(found, text.splitlines())
        self.assertIn(warned, text.splitlines())

    def test_a_failed_check_exits_with_its_status(self) -> None:
        with (
            mock.patch.object(quality_cmd, "run_lint", return_value=_BAD),
            self.assertRaises(SystemExit) as caught,
        ):
            self._lint()
        self.assertEqual(caught.exception.code, 1)

    def test_ratchet_lowers_the_baseline_and_runs_no_lint(self) -> None:
        with (
            mock.patch.object(ruff_baseline, "ratchet_baseline", return_value=3) as ratchet,
            mock.patch.object(quality_cmd, "run_lint") as step,
        ):
            text = self._lint(ratchet=True)
        ratchet.assert_called_once_with(self.root)
        step.assert_not_called()
        self.assertIn("removed 3 row(s)", text)

    def test_a_ratchet_that_cannot_run_exits_2(self) -> None:
        error = ruff_baseline.BaselineError("no data/ruff_baseline.json to ratchet")
        with (
            mock.patch.object(ruff_baseline, "ratchet_baseline", side_effect=error),
            self.assertRaises(SystemExit) as caught,
        ):
            self._lint(ratchet=True)
        self.assertEqual(caught.exception.code, 2)


class LintParserTest(unittest.TestCase):
    """The parser hands paths and both flags to the verb."""

    def test_paths_and_flags_reach_the_handler(self) -> None:
        handler = mock.Mock()
        with mock.patch.dict(parser_handler_manifest._HANDLER_CACHE, {"lint": handler}):
            main(["lint", "--fix", "a.py", "b.py"])
            main(["lint", "--ratchet"])
        self.assertEqual(
            handler.call_args_list,
            [
                mock.call(["a.py", "b.py"], fix=True, ratchet=False),
                mock.call([], fix=False, ratchet=True),
            ],
        )

    def test_both_lint_verbs_name_the_baseline_in_their_help(self) -> None:
        for argv in (["lint", "--help"], ["arb", "ruff", "--help"]):
            with self.subTest(argv=argv):
                out = io.StringIO()
                with redirect_stdout(out):
                    code = main(argv)
                self.assertEqual(code, 0)
                self.assertIn("data/ruff_baseline.json", out.getvalue())


class LintControlTest(unittest.TestCase):
    """NC:lint drives `gz lint`, the verb the Lint step's Ruff verdict comes from."""

    def test_the_control_runs_gz_lint_for_the_planted_finding(self) -> None:
        with mock.patch.object(_qc_nc_entrypoints, "_gz_command_fails", return_value=1) as run:
            self.assertEqual(_qc_nc_entrypoints._ep_lint(Path("/fixture")), 1)
        run.assert_called_once_with(
            ("lint",), Path("/fixture"), expected_exit=1, expect_output="bad.py:1:8 F401"
        )
        self.assertEqual(QC_CLAIM_DELEGATIONS["lint"], "python -m gzkit lint")


class LintPrescriptionsTest(unittest.TestCase):
    """Every surface that tells an agent how to lint names `gz lint`, never bare Ruff."""

    def test_the_implementer_prompt_lints_with_gz_lint(self) -> None:
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
                task, ["REQ"], why="lint", project_root=Path(tmpdir)
            )
        self.assertIn("`uv run gz lint --fix && uv run ruff format .`", prompt)
        self.assertNotIn(_BARE, prompt)

    def test_the_arb_advice_for_style_failures_lints_with_gz_lint(self) -> None:
        advice = _recommendations_for_counts(Counter({"E501": 5}))
        self.assertTrue(any("`uv run gz lint --fix" in line for line in advice), advice)

    def test_the_import_order_guidance_names_gz_lint(self) -> None:
        self.assertIn("`uv run gz lint --fix`", RULE_GUIDANCE["I001"][1])

    def test_the_hooks_readme_says_both_ruff_hooks_run_gz_lint(self) -> None:
        readme = _claude_hooks_readme()
        self.assertIn(
            "`post-edit-ruff.py`\n  PostToolUse (`Write|Edit`) hook that runs `gz lint`", readme
        )
        self.assertIn("`stop-turn-feedback.py`\n  Stop (`*`) hook that runs `gz lint`", readme)


if __name__ == "__main__":
    unittest.main()
