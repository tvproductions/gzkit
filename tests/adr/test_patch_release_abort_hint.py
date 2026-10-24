"""The manual-finish hint of `gz patch release --full` publishes one version block.

`RELEASE_NOTES.md` is cumulative: handing the whole file to
`gh release create --notes-file` puts every historical version into the release
body (GHI #710). The hint shown when the operator declines the full ceremony
must therefore slice the newest block first.
"""

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.commands.patch_release import _abort_hint_lines

_CUMULATIVE_NOTES = (
    "# Release Notes\n\n"
    "## v1.2.3 (2026-10-11)\n\nNewest entry.\n\n---\n\n"
    "## v1.2.2 (2026-10-01)\n\nOlder entry.\n"
)


def _slice_line() -> str:
    return next(line for line in _abort_hint_lines("1.2.3") if "RELEASE_NOTES.md >" in line)


class TestAbortHintPublishesNewestBlockOnly(unittest.TestCase):
    """The hinted release command reads a sliced body, never the cumulative file."""

    def test_release_command_never_takes_the_cumulative_file(self) -> None:
        release = [line for line in _abort_hint_lines("1.2.3") if "gh release create" in line]
        self.assertEqual(len(release), 1)
        self.assertIn("v1.2.3", release[0])
        self.assertNotIn("--notes-file RELEASE_NOTES.md", release[0])

    def test_release_reads_the_file_the_slice_wrote(self) -> None:
        lines = _abort_hint_lines("1.2.3")
        slice_at = lines.index(_slice_line())
        release_at = next(i for i, line in enumerate(lines) if "gh release create" in line)
        self.assertLess(slice_at, release_at)
        sliced_to = lines[slice_at].rsplit(">", 1)[1].strip()
        self.assertIn(f"--notes-file {sliced_to}", lines[release_at])

    @unittest.skipUnless(
        shutil.which("sh") and shutil.which("awk"),
        "the hinted slice is POSIX shell text; it is exercised where sh and awk exist",
    )
    def test_hinted_slice_keeps_the_newest_block_and_drops_the_older_one(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "RELEASE_NOTES.md").write_text(_CUMULATIVE_NOTES, encoding="utf-8")
            body = root / "body.md"
            subprocess.run(  # noqa: S603 — argv this test builds, list form
                ["sh", "-c", _slice_line()],
                cwd=root,
                env={**os.environ, "BODY": str(body)},
                check=True,
            )
            sliced = body.read_text(encoding="utf-8")
        self.assertIn("## v1.2.3", sliced)
        self.assertIn("Newest entry.", sliced)
        self.assertNotIn("v1.2.2", sliced)
        self.assertNotIn("Older entry.", sliced)


if __name__ == "__main__":
    unittest.main()
