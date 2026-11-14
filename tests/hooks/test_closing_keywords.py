"""No pushed commit message carries a GitHub closing keyword (GHI #1327).

A GHI closes only after a reviewer that did not do the fix confirms it on the
issue (AGENTS.md § Defect-fix routing). GitHub closes an issue when a pushed
commit says ``fix: #N``; ``d0a9b2ffe`` closed three issues that way on
2026-11-13.
"""

import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from gzkit.executables import resolve_executable
from gzkit.hooks.closing_keywords import closing_references, main
from tests.commands.common import _isolated_git_env

_REFUSED = (
    "- direct fix: #1318, #1321, #1324",
    "Closes #12",
    "closed #12",
    "FIXED #3",
    "fixes tvproductions/gzkit#7",
    "resolve #4",
    "resolved tvproductions/gzkit#7",
    "Resolves: #5",
    "fixes https://github.com/tvproductions/gzkit/issues/9",
)

_ACCEPTED = (
    "fix(validate): honour the checkpoint (GHI #1318)",
    "fixed in #12",
    "the fix for #12 landed",
    "closing the loop on #4",
    "prefix #3 suffix",
    "Resolved by: 83ce5165c",
    "fixes the reader, see GHI #1321",
)


class TestClosingReferences(unittest.TestCase):
    def test_every_closing_shape_is_found(self) -> None:
        missed = [text for text in _REFUSED if not closing_references(text)]
        self.assertEqual(missed, [])

    def test_house_shapes_and_prose_are_not_closing(self) -> None:
        flagged = [text for text in _ACCEPTED if closing_references(text)]
        self.assertEqual(flagged, [])

    def test_the_finding_names_the_keyword_and_its_reference(self) -> None:
        self.assertEqual(closing_references("body\n\nCloses #12\n"), ["Closes #12"])


class TestPrePushRange(unittest.TestCase):
    """The hook reads the commits being pushed, as pre-commit hands them over."""

    def _git(self, repo: Path, *args: str) -> str:
        return subprocess.run(  # noqa: S603 — git in a temp repository
            [resolve_executable("git"), *args],
            cwd=repo,
            env=_isolated_git_env(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        ).stdout.strip()

    def _repo(self, root: Path, messages: list[str]) -> list[str]:
        self._git(root, "init", "-q")
        self._git(root, "config", "user.name", "g0")
        self._git(root, "config", "user.email", "g0@users.noreply.github.com")
        shas = []
        for index, message in enumerate(messages):
            (root / f"f{index}.txt").write_text(str(index), encoding="utf-8")
            self._git(root, "add", ".")
            self._git(root, "commit", "-q", "-m", message)
            shas.append(self._git(root, "rev-parse", "HEAD"))
        return shas

    def _run(self, repo: Path, from_ref: str, to_ref: str) -> int:
        env = {"PRE_COMMIT_FROM_REF": from_ref, "PRE_COMMIT_TO_REF": to_ref}
        prior = {key: os.environ.get(key) for key in env}
        os.environ.update(env)
        try:
            return main(repo)
        finally:
            for key, value in prior.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_a_closing_keyword_in_a_pushed_commit_refuses_the_push(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base, bad = self._repo(repo, ["base", "docs: route\n\n- direct fix: #1318"])
            err = io.StringIO()
            with redirect_stderr(err):
                code = self._run(repo, base, bad)
        self.assertEqual(code, 1)
        prose = err.getvalue()
        # what failed, why it is forbidden, the governed next step (guardrail-feedback-prose.md)
        self.assertIn(f"{bad[:12]}: 'fix: #1318'", prose)
        self.assertIn("AGENTS.md § Defect-fix routing", prose)
        self.assertIn("git commit --amend", prose)

    def test_a_clean_range_passes_and_history_before_it_is_not_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            _, old, new = self._repo(repo, ["Closes #1 long ago", "base", "fix(x): y (GHI #2)"])
            self.assertEqual(self._run(repo, old, new), 0)

    def test_with_no_starting_ref_only_commits_on_no_remote_are_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as remote:
            repo = Path(tmp)
            self._repo(repo, ["Closes #1 pushed long ago"])
            self._git(Path(remote), "init", "-q", "--bare")
            self._git(repo, "remote", "add", "origin", remote)
            self._git(repo, "push", "-q", "origin", "HEAD:refs/heads/main")
            self.assertEqual(self._run(repo, "0" * 40, "HEAD"), 0)
            (repo / "new.txt").write_text("x", encoding="utf-8")
            self._git(repo, "add", ".")
            self._git(repo, "commit", "-q", "-m", "resolve #2 unreviewed")
            err = io.StringIO()
            with redirect_stderr(err):
                code = self._run(repo, "0" * 40, "HEAD")
        self.assertEqual(code, 1)
        self.assertIn("'resolve #2'", err.getvalue())
        self.assertNotIn("Closes #1", err.getvalue())

    def test_the_module_runs_as_the_hook_entry(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            base, bad = self._repo(repo, ["base", "fixes #3"])
            env = _isolated_git_env()
            codes = []
            for to_ref in (base, bad):
                env.update(PRE_COMMIT_FROM_REF=base if to_ref == bad else "0" * 40)
                env["PRE_COMMIT_TO_REF"] = to_ref
                done = subprocess.run(
                    [sys.executable, "-m", "gzkit.hooks.closing_keywords"],
                    cwd=repo,
                    env=env,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    check=False,
                )
                codes.append(done.returncode)
        self.assertEqual(codes, [0, 1])


if __name__ == "__main__":
    unittest.main()
