"""Shared fixtures for governance-audit tests.

Mirrors the per-package helper convention of ``tests/commands/common.py``.
"""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr


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
