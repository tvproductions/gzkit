"""Shared fixtures for governance-audit tests.

Mirrors the per-package helper convention of ``tests/commands/common.py``.
"""

from __future__ import annotations

import io
import subprocess
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from tests.commands.common import _isolated_git_env


class QuietAdvisoriesMixin(unittest.TestCase):
    """Capture the advisory stream so audit fixtures do not pollute the suite.

    Audits emit non-gating findings as a stream side effect — they have no other
    channel, since ``ValidationError`` carries no severity field and every
    returned entry changes the exit code. A test that exercises one of those
    audits therefore writes a *simulated* finding to the real stderr unless it
    captures it.

    That pollution used to be merely ugly (advisory prose interleaved with
    unittest's progress dots). It became load-bearing when ``gz check`` started
    surfacing advisory lines from passing steps (GHI #713): the Test step's
    captured stderr contains fixture findings, which are claims about temp
    directories, not about this project — so leaking them misattributes 32
    simulated findings to the real repository.

    ``self.advisory_output`` exposes what was captured, for tests that assert on
    the emitted prose.
    """

    def setUp(self) -> None:
        super().setUp()
        self.advisory_output = io.StringIO()
        capture = redirect_stderr(self.advisory_output)
        capture.__enter__()
        self.addCleanup(capture.__exit__, None, None, None)


def init_committed_repo(root: Path) -> Path:
    """Make *root* a git repository with every file in it committed; return *root*.

    The fidelity gate runs each assertion in a detached worktree at HEAD (GHI
    #1156), so a fixture that exercises it needs a project root with a commit.
    """
    env = _isolated_git_env()

    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=env)

    git("init", "-q")
    git("config", "user.email", "t@e.com")
    git("config", "user.name", "t")
    (root / ".gitkeep").touch()
    git("add", "-A")
    git("commit", "-q", "-m", "init")
    return root
