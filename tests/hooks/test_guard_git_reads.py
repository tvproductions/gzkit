"""A guard that could not read git has not checked the commit (GHI #1339).

The pre-commit guards read the staged change through git. An empty answer used
to mean two things: git answered "nothing staged", or git never answered at
all. The second read as the first, so the ledger guard -- a ``GATE5_INVARIANTS``
member -- passed a staged ledger deletion whenever git failed. It also parsed the
raw patch, which a user's ``color.diff=always`` or ``diff.external`` reshapes
until no removed line is recognisable.

These tests drive real git in a temporary repository, never a stubbed read: the
defect lived in how git's own output and exit status were read.
"""

import io
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

from gzkit.hooks import guards
from tests.commands.common import _isolated_git_env
from tests.hooks.test_obpi_completion_commit_guard import _BRIEF_REL, _COMPLETED_NO_EVIDENCE

_LEDGER = ".gzkit/ledger.jsonl"


def _git(args: list[str], cwd: Path) -> None:
    subprocess.run(  # noqa: S603 — git argv this test builds
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_isolated_git_env(),
    )


def _repo(tmp: str) -> Path:
    """Return a repository whose committed ledger holds two rows."""
    root = Path(tmp)
    _git(["init", "-q", "-b", "main"], root)
    _git(["config", "user.email", "g0@users.noreply.github.com"], root)
    _git(["config", "user.name", "g0"], root)
    ledger = root / _LEDGER
    ledger.parent.mkdir(parents=True)
    ledger.write_text('{"a":1}\n{"b":2}\n', encoding="utf-8")
    _git(["add", "-A"], root)
    _git(["commit", "-qm", "base"], root)
    return root


def _stage_ledger(root: Path, text: str) -> None:
    (root / _LEDGER).write_text(text, encoding="utf-8")
    _git(["add", _LEDGER], root)


def _ledger_guard(root: Path) -> int:
    with redirect_stdout(io.StringIO()):
        return guards.forbid_manual_ledger_edits(root)


class TestTheLedgerGuardReadsTheStagedDiff(unittest.TestCase):
    """A staged ledger deletion is refused however the user's git renders diffs."""

    def test_a_staged_append_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            _stage_ledger(root, '{"a":1}\n{"b":2}\n{"c":3}\n')
            self.assertEqual(_ledger_guard(root), 0)

    def test_a_staged_deletion_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            _stage_ledger(root, '{"b":2}\n')
            self.assertEqual(_ledger_guard(root), 1)

    def test_a_staged_deletion_is_refused_when_diffs_are_always_colored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            _git(["config", "color.diff", "always"], root)
            _stage_ledger(root, '{"b":2}\n')
            self.assertEqual(_ledger_guard(root), 1)

    def test_a_staged_deletion_is_refused_under_an_external_diff_tool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            # `true` prints nothing: the patch the guard reads would be empty.
            _git(["config", "diff.external", "true"], root)
            _stage_ledger(root, '{"b":2}\n')
            self.assertEqual(_ledger_guard(root), 1)

    def test_a_staged_deletion_is_refused_under_a_textconv_driver(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            # A driver that prints nothing leaves no removed line to see.
            (root / ".git" / "info" / "attributes").write_text(
                "*.jsonl diff=blank\n", encoding="utf-8"
            )
            _git(["config", "diff.blank.textconv", "true"], root)
            _stage_ledger(root, '{"b":2}\n')
            self.assertEqual(_ledger_guard(root), 1)


class TestAReadThatMayMissIsNotAFailedRead(unittest.TestCase):
    """A brief new in this commit has no HEAD blob; that absence is an answer."""

    def test_a_new_brief_staged_completed_without_evidence_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            brief = root / _BRIEF_REL
            brief.parent.mkdir(parents=True)
            brief.write_text(_COMPLETED_NO_EVIDENCE, encoding="utf-8")
            _git(["add", "-A"], root)
            try:
                with redirect_stdout(io.StringIO()):
                    rc = guards.forbid_unattested_obpi_completion_commits(root)
            except guards.GitReadError as exc:
                self.fail(f"a brief absent from HEAD was read as a failed git read: {exc}")
        self.assertEqual(rc, 1)


class TestAGitReadThatFailsIsNotACleanRead(unittest.TestCase):
    """When git cannot answer, no guard reads the silence as "nothing staged"."""

    def test_every_git_reading_guard_raises_when_git_cannot_answer(self) -> None:
        readers = (
            guards.forbid_manual_ledger_edits,
            guards.forbid_skill_sync_drift,
            guards.forbid_post_authoring_src_commits,
            guards.forbid_unattested_obpi_completion_commits,
        )
        with tempfile.TemporaryDirectory() as tmp:
            not_a_repo = Path(tmp)
            for reader in readers:
                with self.subTest(guard=reader.__name__), self.assertRaises(guards.GitReadError):
                    reader(not_a_repo)

    def test_the_guard_sweep_refuses_the_commit_when_git_cannot_answer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            try:
                with redirect_stdout(out):
                    rc = guards.run_guards(Path(tmp))
            except guards.GitReadError as exc:
                self.fail(f"the sweep let a failed git read escape instead of refusing: {exc}")
        self.assertEqual(rc, 1)
        # output-contract: the refusal carries recovery prose (guardrail-feedback-prose.md).
        message = out.getvalue()
        self.assertIn("git diff --cached", message)
        self.assertIn("GHI #1339", message)

    def test_the_guard_sweep_refuses_the_commit_when_git_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _repo(tmp)
            _stage_ledger(root, '{"b":2}\n')
            out = io.StringIO()
            try:
                with mock.patch.dict(os.environ, {"PATH": ""}), redirect_stdout(out):
                    rc = guards.run_guards(root)
            except OSError as exc:
                self.fail(f"an absent git escaped the sweep instead of refusing: {exc!r}")
        self.assertEqual(rc, 1)
        # output-contract: the refusal names the cause (guardrail-feedback-prose.md).
        self.assertIn("could not run", out.getvalue())
        self.assertIn("GHI #1339", out.getvalue())


if __name__ == "__main__":
    unittest.main()
