"""Tests for Eval-feedback-source: trailer validation — OBPI-0.0.26-04.

@covers ADR-0.0.26-evaluation-feedback-loop-doctrine
@covers OBPI-0.0.26-04-commit-trailer-validator
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.cli import main
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


def _make_completed_process(stdout: str, returncode: int = 0) -> MagicMock:
    """Return a fake CompletedProcess-like object for subprocess.run mocking."""
    cp = MagicMock()
    cp.returncode = returncode
    cp.stdout = stdout
    cp.stderr = ""
    return cp


class TestEvalFeedbackTrailerValidation(unittest.TestCase):
    """Verify Eval-feedback-source: trailer recognition and enforcement."""

    @covers("REQ-0.0.26-04-05")
    def test_eval_feedback_source_alone_rejected_for_src_commit(self) -> None:
        """src/tests commit with only Eval-feedback-source: trailer is REJECTED under GHI #552.

        Pre-GHI-#552 OBPI-0.0.26-04 doctrine accepted Eval-feedback-source: alone
        as a substitute for Task: on src/tests scope. GHI #552 strict-mode
        supersedes: src/tests scope requires Task: trailer. Eval-feedback-source:
        remains valid on rule-edit (.gzkit/rules/) commits closing eval-feedback
        GHIs (see test_passes_rule_edit_closing_eval_feedback_ghi_with_trailer).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            project_root = Path.cwd()
            _init_git_repo(project_root)
            src_file = project_root / "src" / "mypkg" / "module.py"
            src_file.parent.mkdir(parents=True, exist_ok=True)
            src_file.write_text("x = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "src"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    "feat: update module\n\nEval-feedback-source: eval-2026-01-01T00-00-00-abc",
                ],
                cwd=project_root,
                check=True,
                capture_output=True,
            )
            result = runner.invoke(main, ["validate", "--commit-trailers"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Task:", result.output)

    @covers("REQ-0.0.26-04-04")
    def test_fails_rule_edit_closing_eval_feedback_ghi_without_trailer(self) -> None:
        """Commit touching .gzkit/rules/ + closes eval-feedback GHI, no trailer → error."""
        # Use _head_commit_message_and_files to inject a synthetic commit state so
        # real git is not needed for the eval-feedback branch, and patch gh only.
        eval_feedback_response = '{"labels":[{"name":"eval-feedback"}]}'
        fake_head = (
            "chore: update rule\n\nCloses #42",
            [".gzkit/rules/my-rule.md"],
        )
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with (
                patch(
                    "gzkit.commands.validate_cmd._head_commit_message_and_files",
                    return_value=fake_head,
                ),
                patch(
                    "gzkit.commands.validate_cmd.subprocess.run",
                    side_effect=lambda args, **kw: _make_completed_process(
                        eval_feedback_response if args[0] == "gh" else "abc1234"
                    ),
                ),
            ):
                result = runner.invoke(main, ["validate", "--commit-trailers"])

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("Eval-feedback-source", result.output)

    @covers("REQ-0.0.26-04-05")
    def test_passes_rule_edit_closing_eval_feedback_ghi_with_trailer(self) -> None:
        """Commit touching .gzkit/rules/ + closes eval-feedback GHI + trailer → clean."""
        eval_feedback_response = '{"labels":[{"name":"eval-feedback"}]}'
        fake_head = (
            (
                "chore: update rule\n\n"
                "Closes #42\n\n"
                "Eval-feedback-source: eval-2026-01-01T00-00-00-abc"
            ),
            [".gzkit/rules/my-rule.md"],
        )
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with (
                patch(
                    "gzkit.commands.validate_cmd._head_commit_message_and_files",
                    return_value=fake_head,
                ),
                patch(
                    "gzkit.commands.validate_cmd.subprocess.run",
                    side_effect=lambda args, **kw: _make_completed_process(
                        eval_feedback_response if args[0] == "gh" else "abc1234"
                    ),
                ),
            ):
                result = runner.invoke(main, ["validate", "--commit-trailers"])

        self.assertEqual(result.exit_code, 0)

    @covers("REQ-0.0.26-04-05")
    def test_eval_feedback_source_additive_with_task_passes_code_commit(self) -> None:
        """Eval-feedback-source: + Task: trailer on src commit passes (GHI #552 additive).

        Eval-feedback-source: is now an additive trailer on src/tests scope —
        it co-exists with the required Task: trailer rather than substituting
        for it. This test fences the additive composition.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            project_root = Path.cwd()
            _init_git_repo(project_root)
            src_file = project_root / "src" / "mypkg" / "module.py"
            src_file.parent.mkdir(parents=True, exist_ok=True)
            src_file.write_text("x = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "src"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    (
                        "fix: apply eval feedback\n\n"
                        "Task: TASK-eval-feedback-applied-#001\n"
                        "Eval-feedback-source: eval-2026-05-01T10-00-00-xyz"
                    ),
                ],
                cwd=project_root,
                check=True,
                capture_output=True,
            )
            result = runner.invoke(main, ["validate", "--commit-trailers"])
            self.assertEqual(result.exit_code, 0)


if __name__ == "__main__":
    unittest.main()
