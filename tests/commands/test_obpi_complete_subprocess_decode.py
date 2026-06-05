"""Decode-robustness tests for the OBPI-completion REQ-coverage subprocesses.

GHI #534: on Windows the covering-test subprocess reader crashed with
``UnicodeDecodeError`` (``invalid start byte 0xa7``) when a grandchild
emitted bytes outside UTF-8, aborting ``gz obpi complete``. The completion
helpers must decode tolerantly so an undecodable byte in a sub-process's
stdout cannot escape the reader path.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from gzkit.commands.obpi_complete import _run_captured


class TestObpiCompleteSubprocessDecode(unittest.TestCase):
    def test_run_captured_tolerates_non_utf8_grandchild_stdout(self) -> None:
        # Grandchild writes 0xA7 — an invalid UTF-8 start byte (the exact byte
        # in the GHI #534 trace). Without errors="replace" the reader raises
        # UnicodeDecodeError (a ValueError), which is NOT caught by the callers'
        # (OSError, SubprocessError) guards and crashes completion.
        cmd = [
            sys.executable,
            "-c",
            r"import sys; sys.stdout.buffer.write(b'before\xa7after'); sys.exit(0)",
        ]

        result = _run_captured(cmd, cwd=str(Path.cwd()))

        # The semantic: completion observes the sub-process's real exit code
        # instead of dying on a decode error, and the surrounding text survives.
        self.assertEqual(result.returncode, 0)
        self.assertIn("before", result.stdout)
        self.assertIn("after", result.stdout)

    def test_run_captured_preserves_nonzero_exit(self) -> None:
        # A failing covering test must still read as a failure (returncode != 0)
        # even when its output carries non-UTF-8 bytes.
        cmd = [
            sys.executable,
            "-c",
            r"import sys; sys.stdout.buffer.write(b'fail\xa7'); sys.exit(1)",
        ]

        result = _run_captured(cmd, cwd=str(Path.cwd()))

        self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
