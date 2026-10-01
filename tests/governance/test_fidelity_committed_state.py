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

from __future__ import annotations

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
    return subprocess.run(
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
