"""Tests that `gz git-sync` keeps a refusing hook's diagnosis (GHI #816).

`_push_if_ahead` and `_commit_staged_changes` both bound `git_cmd`'s stdout to
an underscore-prefixed throwaway and appended only stderr to `blockers`. Hook
frameworks write their check report to stdout while git writes its terminal
summary to stderr, so a pre-push refusal surfaced as the bare line
`error: failed to push some refs to '<remote>'` — thirteen lines of `gz git-sync`
output carrying no failing check, no file, no line, and no recovery step, while
the same operation run as a plain `git push` returned ~150 lines naming all four.

Assertions derive from `.gzkit/rules/guardrail-feedback-prose.md` § Invariant --
a fail-closed surface emits "what failed, why it is forbidden, the governed next
step" -- not from the shape of the current output. A blocker that reports the
transport failed while discarding the gate's own recovery prose satisfies none of
the three parts, and it misdirects: `failed to push some refs` is git's
non-fast-forward phrasing, so it steers a reader toward `git pull --rebase` and
then toward `--no-verify`, which `AGENTS.md` Never #10 forbids outright.

Both call sites are exercised because both were blind; a fix applied only to the
push arm leaves a pre-commit refusal equally undiagnosable.
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.sync import _execute_git_sync

_HOOK_STDOUT = """gz check (pre-push gate).................................................Failed
- hook id: gz-check-pre-push
- exit code: 1

  ❌ Transcribed ADR counts

─── Transcribed ADR counts output ───
   →  .gzkit/handoffs/20260817T172834Z-example.md:59
   Remove the number and point at the command: `uv run gz adr status <ADR-ID>`.
"""

_GIT_STDERR = "error: failed to push some refs to 'https://github.com/tvproductions/gzkit.git'"

_COMMIT_HOOK_STDOUT = """ruff check (lint)..........................Failed
- hook id: ruff
- exit code: 1

src/gzkit/example.py:1:1: F401 [*] `os` imported but unused
"""

_COMMIT_GIT_STDERR = "error: pre-commit hook failed"


class _FakeGit:
    """Git stub whose commit and/or push fail the way a refusing hook does."""

    def __init__(
        self,
        *,
        push_stdout: str = "",
        push_stderr: str = "",
        push_rc: int = 0,
        commit_stdout: str = "",
        commit_stderr: str = "",
        commit_rc: int = 0,
        staged: str = ".gzkit/ledger.jsonl\n",
        ahead: int = 1,
    ) -> None:
        self.push_stdout = push_stdout
        self.push_stderr = push_stderr
        self.push_rc = push_rc
        self.commit_stdout = commit_stdout
        self.commit_stderr = commit_stderr
        self.commit_rc = commit_rc
        self.staged = staged
        self.ahead = ahead

    def __call__(self, _root: Path, *args: str) -> tuple[int, str, str]:
        if args[:3] == ("diff", "--cached", "--name-only"):
            return 0, self.staged, ""
        if args[0] == "commit":
            if self.commit_rc == 0:
                self.ahead += 1
            return self.commit_rc, self.commit_stdout, self.commit_stderr
        if args[0] == "push":
            return self.push_rc, self.push_stdout, self.push_stderr
        if args[:2] == ("rev-list", "--count"):
            spec = args[2]
            if spec == "origin/main..main":
                return 0, str(self.ahead), ""
            return 0, "0", ""
        if args[0] == "rev-parse":
            return 0, "deadbeef", ""
        return 0, "", ""


def _run(fake: _FakeGit, *, dirty: bool = False, allow_push: bool = True) -> list[str]:
    blockers: list[str] = []
    with (
        mock.patch("gzkit.commands.sync.git_cmd", side_effect=fake),
        mock.patch("gzkit.git_sync.git_cmd", side_effect=fake),
    ):
        _execute_git_sync(
            project_root=Path("/nonexistent"),
            dirty=dirty,
            auto_add=dirty,
            run_lint_gate=False,
            run_test_gate=False,
            allow_push=allow_push,
            remote="origin",
            target_branch="main",
            blockers=blockers,
            warnings=[],
        )
    return blockers


class TestRefusalKeepsItsDiagnosis(unittest.TestCase):
    """A hook's recovery prose must survive the wrapper that invoked it."""

    def test_push_blocker_names_the_failing_check(self) -> None:
        # The operator-visible question after a refusal is "which gate, and what
        # do I do" -- neither is answerable from git's stderr alone.
        blockers = _run(_FakeGit(push_rc=1, push_stdout=_HOOK_STDOUT, push_stderr=_GIT_STDERR))
        joined = "\n".join(blockers)

        self.assertIn("Transcribed ADR counts", joined, msg=f"blockers={blockers!r}")

    def test_push_blocker_carries_the_governed_next_step(self) -> None:
        # guardrail-feedback-prose part three. Without it the reader is left with
        # git's non-fast-forward phrasing, which points at the wrong remedy.
        blockers = _run(_FakeGit(push_rc=1, push_stdout=_HOOK_STDOUT, push_stderr=_GIT_STDERR))
        joined = "\n".join(blockers)

        self.assertIn("uv run gz adr status", joined, msg=f"blockers={blockers!r}")

    def test_push_blocker_still_carries_git_stderr(self) -> None:
        # Negative control on the fix's direction: capturing stdout must ADD to
        # the diagnosis, never replace the transport error. A fix that swapped
        # the streams would pass both tests above and lose the git summary.
        blockers = _run(_FakeGit(push_rc=1, push_stdout=_HOOK_STDOUT, push_stderr=_GIT_STDERR))
        joined = "\n".join(blockers)

        self.assertIn("failed to push some refs", joined, msg=f"blockers={blockers!r}")

    def test_commit_blocker_names_the_failing_hook(self) -> None:
        # The second blind call site. A push-only fix leaves this one dark, which
        # is the instance-not-class failure AGENTS.md DO IT RIGHT #1 names.
        blockers = _run(
            _FakeGit(
                commit_rc=1,
                commit_stdout=_COMMIT_HOOK_STDOUT,
                commit_stderr=_COMMIT_GIT_STDERR,
            ),
            dirty=True,
        )
        joined = "\n".join(blockers)

        self.assertIn("F401", joined, msg=f"blockers={blockers!r}")

    def test_stderr_only_failure_is_unchanged(self) -> None:
        # Negative control: a genuine non-hook git failure writes nothing to
        # stdout. The blocker must still report stderr rather than degrading to
        # the fallback string.
        blockers = _run(_FakeGit(push_rc=1, push_stdout="", push_stderr=_GIT_STDERR))

        self.assertEqual(blockers, [_GIT_STDERR], msg=f"blockers={blockers!r}")

    def test_silent_failure_falls_back(self) -> None:
        # Negative control: both streams empty must not yield an empty blocker,
        # which would render as a refusal with no text at all.
        blockers = _run(_FakeGit(push_rc=1, push_stdout="", push_stderr=""))

        self.assertEqual(blockers, ["Push failed."], msg=f"blockers={blockers!r}")


if __name__ == "__main__":
    unittest.main()
