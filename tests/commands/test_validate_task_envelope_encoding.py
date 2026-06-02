"""Regression: the task-envelope git-log subprocess must decode output as UTF-8.

WHY: ``_commit_trailer_channel_for_obpi`` and ``_commit_trailer_channel_map``
run ``git log --all --format=%B`` to harvest ``Task:`` trailers across history.
``git`` emits commit bodies as UTF-8, and gzkit's own commit subjects are
saturated with em-dashes (``—`` = UTF-8 ``E2 80 94``) and arrows. When the
``subprocess.run`` call omits ``encoding=``, Windows falls back to the locale
codec (cp1252); the ``_readerthread`` draining the pipe then raises
``UnicodeDecodeError`` on the first continuation byte (e.g. ``0x9d``), the
daemon thread dies, ``communicate()`` returns truncated/empty stdout, and the
audit silently under-counts TASK attributions. Pinning ``encoding="utf-8"``
makes the decode deterministic on every platform.

These assertions derive from ``.gzkit/rules/cross-platform.md`` § Subprocess
(UTF-8 must be explicit at every subprocess boundary), not from a run of the
code. The subprocess boundary is mocked per the Unit-tier contract in
``.gzkit/rules/tests.md``.
"""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands import validate_task_envelope as vte

# A git-log chunk whose body carries a multi-byte UTF-8 char before the trailer
# block — the exact shape that crashed the cp1252 reader thread.
_GIT_LOG_STDOUT = "feat(x): density dial — re-scope\n\nTask: TASK-0.0.1-01-01-01\n--EOC--\n"


def _fake_completed(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(
        args=["git"], returncode=0, stdout=_GIT_LOG_STDOUT, stderr=""
    )


class TaskEnvelopeGitLogEncodingTests(unittest.TestCase):
    """The git-log harvest must pass ``encoding='utf-8'`` and survive non-ASCII bodies."""

    def test_commit_trailer_for_obpi_pins_utf8_and_finds_trailer(self) -> None:
        with mock.patch.object(vte.subprocess, "run", side_effect=_fake_completed) as run:
            found = vte._commit_trailer_channel_for_obpi(Path("."), "OBPI-0.0.1-01")
        self.assertEqual(found, {"TASK-0.0.1-01-01-01"})
        self.assertEqual(
            run.call_args.kwargs.get("encoding"),
            "utf-8",
            "git-log subprocess must decode as UTF-8 (Windows cp1252 fallback drops commits)",
        )

    def test_commit_trailer_map_pins_utf8_and_groups_trailer(self) -> None:
        with mock.patch.object(vte.subprocess, "run", side_effect=_fake_completed) as run:
            grouped = vte._commit_trailer_channel_map(Path("."))
        self.assertEqual(grouped.get("OBPI-0.0.1-01"), {"TASK-0.0.1-01-01-01"})
        self.assertEqual(
            run.call_args.kwargs.get("encoding"),
            "utf-8",
            "git-log subprocess must decode as UTF-8 (Windows cp1252 fallback drops commits)",
        )


if __name__ == "__main__":
    unittest.main()
