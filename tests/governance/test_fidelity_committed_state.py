"""The fidelity gate grades the committed tree, never the live checkout (GHI #1156).

Operator ruling 2026-10-01 (verbatim: "Committed state (Recommended)"): each
fidelity assertion runs in a detached worktree at HEAD, and the gate fails
closed when that worktree cannot be built. So:

(a) an assertion satisfiable only by an uncommitted file must FAIL;
(b) an assertion that writes a file leaves the live root byte-unchanged;
(c) with no buildable worktree, every assertion fails with the distinct
    ``WORKTREE_UNAVAILABLE`` sentinel and nothing runs at all.

Each test runs with the process cwd inside the live fixture root, because that
is where the closeout ceremony's caller sits — a gate that inherits cwd would
read and write the live tree, which is the defect.
"""

import os
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.fidelity import WORKTREE_UNAVAILABLE, FidelityAssertion, run_fidelity_gate
from tests.commands.common import _isolated_git_env
from tests.governance.common import init_committed_repo


def _py(code: str) -> str:
    """A portable ``python -c <code>`` command line (no shell, survives shlex.split)."""
    return f"{shlex.quote(sys.executable)} -c {shlex.quote(code)}"


def _exists(name: str) -> str:
    return _py(f"import os, sys; sys.exit(0 if os.path.isfile({name!r}) else 1)")


def _assertion(command: str, expected_exit: int = 0) -> FidelityAssertion:
    return FidelityAssertion(
        adr_id="ADR-test", claim="claim", command=command, expected_exit=expected_exit
    )


def _git(root: Path, *args: str) -> str:
    return subprocess.run(  # noqa: S603 — git argv this test builds
        ["git", "-C", str(root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=_isolated_git_env(),
    ).stdout


class _LiveRootCase(unittest.TestCase):
    """A temp git repo with one commit, entered as the process cwd."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="gzkit-fid-live-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        (self.root / "committed.txt").write_text("committed\n", encoding="utf-8")
        init_committed_repo(self.root)
        previous = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)


class TestFidelityGradesCommittedState(_LiveRootCase):
    def test_committed_file_is_visible(self) -> None:
        """Control: the worktree is HEAD, so a committed file satisfies the row."""
        [result] = run_fidelity_gate(
            [_assertion(_exists("committed.txt"))], adr_id="ADR-test", project_root=self.root
        )
        self.assertEqual(result.result, "pass", result)

    def test_uncommitted_file_cannot_satisfy_an_assertion(self) -> None:
        """(a) A row passing only because of an untracked live file must FAIL."""
        (self.root / "uncommitted.txt").write_text("local\n", encoding="utf-8")
        [result] = run_fidelity_gate(
            [_assertion(_exists("uncommitted.txt"))], adr_id="ADR-test", project_root=self.root
        )
        self.assertEqual(result.observed, 1)
        self.assertEqual(result.result, "fail")

    def test_writing_assertion_leaves_live_root_unchanged(self) -> None:
        """(b) An assertion that writes ``probe`` must not touch the live tree."""
        (self.root / "uncommitted.txt").write_text("local\n", encoding="utf-8")
        before = _git(self.root, "status", "--porcelain")
        [result] = run_fidelity_gate(
            [_assertion(_py("open('probe', 'w').write('x')"))],
            adr_id="ADR-test",
            project_root=self.root,
        )
        self.assertEqual(result.result, "pass", "the write itself must have run")
        self.assertFalse((self.root / "probe").exists())
        self.assertEqual(_git(self.root, "status", "--porcelain"), before)
        self.assertEqual(_git(self.root, "worktree", "list", "--porcelain").count("worktree "), 1)


_PRISTINE = _py(
    "import os, sys\n"
    "ok = (open('committed.txt', encoding='utf-8').read() == 'committed\\n'\n"
    "      and not os.path.exists('new.txt') and not os.path.exists('ignored.txt'))\n"
    "sys.exit(0 if ok else 1)"
)


class TestEachRowStartsFromHead(unittest.TestCase):
    """Every row sees exactly the committed tree, whatever an earlier row did (GHI #1156).

    The ruling's invariant is per assertion: "a fidelity assertion's verdict depends
    only on the committed tree at HEAD". A row that modifies, deletes, adds or writes
    an ignored file must not change what the next row sees.
    """

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="gzkit-fid-rows-")
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        (self.root / "committed.txt").write_text("committed\n", encoding="utf-8")
        (self.root / ".gitignore").write_text("ignored.txt\n", encoding="utf-8")
        init_committed_repo(self.root)
        previous = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)

    def _second_row_after(self, first: str) -> FidelityAssertion:
        first_result, second = run_fidelity_gate(
            [_assertion(first), _assertion(_PRISTINE)], adr_id="ADR-test", project_root=self.root
        )
        self.assertEqual(first_result.result, "pass", "the first row's write must have run")
        return second

    def test_a_modified_or_added_file_does_not_reach_the_next_row(self) -> None:
        second = self._second_row_after(
            _py(
                "open('committed.txt', 'w').write('changed')\n"
                "open('new.txt', 'w').write('x')\n"
                "open('ignored.txt', 'w').write('x')"
            )
        )
        self.assertEqual(second.result, "pass", "the second row saw the first row's writes")

    def test_a_deleted_file_is_back_for_the_next_row(self) -> None:
        second = self._second_row_after(_py("import os; os.remove('committed.txt')"))
        self.assertEqual(second.result, "pass", "the second row saw the first row's deletion")

    def test_the_run_builds_one_worktree_not_one_per_row(self) -> None:
        """One checkout per run, not per row.

        Seven rows built seven full checkouts: 190 s on windows-latest (profile run
        38984988910).
        """
        record_dir = tempfile.TemporaryDirectory(prefix="gzkit-fid-cwd-")
        self.addCleanup(record_dir.cleanup)
        record = Path(record_dir.name) / "cwds.txt"
        row = _assertion(_py(f"import os; open({str(record)!r}, 'a').write(os.getcwd() + '\\n')"))
        results = run_fidelity_gate([row, row, row], adr_id="ADR-test", project_root=self.root)
        self.assertEqual([r.result for r in results], ["pass"] * 3)
        cwds = record.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(cwds), 3)
        self.assertEqual(len(set(cwds)), 1, f"each row ran in its own worktree: {cwds}")
        self.assertNotEqual(Path(cwds[0]).resolve(), self.root, "a row ran in the live root")


class TestARowThatCannotRunOrBreaksTheWorktree(_LiveRootCase):
    """Failure paths of the shared worktree (GHI #1156 fail-closed, per row)."""

    def test_a_command_that_cannot_execute_reports_minus_one_and_the_next_row_runs(
        self,
    ) -> None:
        missing, control = run_fidelity_gate(
            [_assertion("gzkit-no-such-executable-xyz"), _assertion(_exists("committed.txt"))],
            adr_id="ADR-test",
            project_root=self.root,
        )
        self.assertEqual(missing.observed, -1)
        self.assertEqual(missing.result, "fail")
        self.assertEqual(control.result, "pass", "one unrunnable row must not sink the next")

    def test_a_worktree_that_cannot_be_restored_fails_later_rows_closed_without_running(
        self,
    ) -> None:
        """A row that breaks the worktree's git link: no later row may run on a dirty tree."""
        record_dir = tempfile.TemporaryDirectory(prefix="gzkit-fid-ran-")
        self.addCleanup(record_dir.cleanup)
        marker = Path(record_dir.name) / "ran"
        writer = _py(f"open({str(marker)!r}, 'a').write('x')")
        breaker, second, third = run_fidelity_gate(
            [
                _assertion(_py("import os; os.remove('.git')")),
                _assertion(writer),
                _assertion(writer),
            ],
            adr_id="ADR-test",
            project_root=self.root,
        )
        self.assertEqual(breaker.result, "pass", "the first row's removal must have run")
        self.assertEqual([second.observed, third.observed], [WORKTREE_UNAVAILABLE] * 2)
        self.assertEqual([second.result, third.result], ["fail", "fail"])
        self.assertFalse(marker.exists(), "a row ran on a worktree that was not restored")


class TestAFailedCheckoutFailsClosedEvenWhenCleanWorks(_LiveRootCase):
    """A stale ``index.lock`` makes ``checkout`` fail while ``clean`` succeeds.

    The tracked edit survives in that case, so a restore that trusted ``clean``
    alone would run the next row on a tree that is not HEAD.
    """

    def test_the_next_row_does_not_run_on_the_unrestored_tree(self) -> None:
        lock_and_edit = _py(
            "import os, subprocess\n"
            "d = subprocess.run(['git', 'rev-parse', '--absolute-git-dir'],"
            " capture_output=True, text=True, check=True).stdout.strip()\n"
            "open(os.path.join(d, 'index.lock'), 'w').close()\n"
            "open('committed.txt', 'w').write('changed')"
        )
        first, second = run_fidelity_gate(
            [_assertion(lock_and_edit), _assertion(_exists("committed.txt"))],
            adr_id="ADR-test",
            project_root=self.root,
        )
        self.assertEqual(first.result, "pass", "the first row's lock and edit must have run")
        self.assertEqual(second.observed, WORKTREE_UNAVAILABLE)


class TestFidelityFailsClosedWithoutWorktree(unittest.TestCase):
    def test_non_git_root_fails_every_assertion_and_runs_nothing(self) -> None:
        """(c) No buildable worktree: every row fails with the sentinel, none runs."""
        tmp = tempfile.TemporaryDirectory(prefix="gzkit-fid-nogit-")
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name).resolve()
        previous = Path.cwd()
        os.chdir(root)
        self.addCleanup(os.chdir, previous)
        marker = root / "ran"
        writer = _py(f"open({str(marker)!r}, 'w').write('x')")
        results = run_fidelity_gate(
            [_assertion(writer), _assertion(writer, expected_exit=1)],
            adr_id="ADR-test",
            project_root=root,
        )
        self.assertEqual([r.result for r in results], ["fail", "fail"])
        self.assertEqual([r.observed for r in results], [WORKTREE_UNAVAILABLE] * 2)
        self.assertFalse(marker.exists(), "an assertion ran despite no worktree")


if __name__ == "__main__":
    unittest.main()
