"""The verb refusal of RP-12 ruling 17, read from the stamp a hook puts on a subagent's call.

The stamp is two environment variables (ruling 34 has the hook set them on a
subagent's ``gz`` command). A call carrying the root variable is a subagent's; a
call without it is the main session's and is never refused (#1296's case 3). The
real root is the directory the verb runs in, ``get_project_root``'s answer, read
only for a stamped call.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.dispatch_stamp import STAMP_ID_ENV, STAMP_ROOT_ENV, consume_stamp, stamp_refusal

_REPO = Path(__file__).resolve().parents[1]


def _never() -> Path:
    """Stand in for a root that cannot be read, as from a deleted directory.

    Raises:
        FileNotFoundError: always.

    """
    raise FileNotFoundError


class StampRefusal(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(directory.name)
        self.project = self.base / "project"
        self.scratch = self.base / "scratch"
        self.project.mkdir()
        self.scratch.mkdir()

    def _refusal(self, root: str, real: Path) -> str | None:
        stamp = {STAMP_ROOT_ENV: root, STAMP_ID_ENV: "D-0123456789abcdef"}
        return stamp_refusal(stamp, lambda: real)

    def test_an_unstamped_call_is_the_main_sessions_and_proceeds(self) -> None:
        """Case 3, the root never read: an unreadable one is the verb's own failure."""
        self.assertIsNone(stamp_refusal({}, _never))

    def test_a_stamp_naming_the_real_root_proceeds(self) -> None:
        self.assertIsNone(self._refusal(self.project.as_posix(), self.project))

    def test_a_stamp_naming_another_root_is_refused(self) -> None:
        refusal = self._refusal(self.scratch.as_posix(), self.project)
        self.assertIsNotNone(refusal)
        self.assertIn("D-0123456789abcdef", str(refusal))

    def test_a_stamp_naming_no_root_is_refused(self) -> None:
        """Ruling 17: a subagent with no dispatch record is stamped with no root."""
        for empty in ("", "  "):
            with self.subTest(root=empty):
                self.assertIsNotNone(self._refusal(empty, self.project))

    def test_a_relative_stamp_root_is_refused(self) -> None:
        self.assertIsNotNone(self._refusal("project", self.base))

    def test_a_stamped_root_that_does_not_exist_is_refused(self) -> None:
        self.assertIsNotNone(self._refusal((self.base / "gone").as_posix(), self.project))

    def test_a_subdirectory_of_the_intended_root_is_another_root(self) -> None:
        """A verb's root is its directory, so a subdirectory books into another project."""
        inner = self.project / "inner"
        inner.mkdir()
        self.assertIsNotNone(self._refusal(self.project.as_posix(), inner))

    def test_both_sides_are_resolved_before_comparing(self) -> None:
        """A link to the intended root is the intended root, and a link elsewhere is not."""
        link = self.base / "link"
        try:
            link.symlink_to(self.project, target_is_directory=True)
        except OSError as exc:  # Windows without the symlink privilege
            self.skipTest(f"no symlink here: {exc}")
        self.assertIsNone(self._refusal(link.as_posix(), self.project))
        self.assertIsNone(self._refusal(self.project.as_posix(), link))
        self.assertIsNotNone(self._refusal(link.as_posix(), self.scratch))

    def test_a_root_spelled_in_another_case_is_the_same_directory_where_case_folds(
        self,
    ) -> None:
        """A case-insensitive volume keeps the case typed, so the spelling is not the root."""
        respelled = self.base / "PROJECT"
        if not respelled.is_dir():
            self.skipTest("this volume is case-sensitive")
        self.assertIsNone(self._refusal(respelled.as_posix(), self.project))


class StampConsumed(unittest.TestCase):
    """Ruling 37: a call that passes takes the stamp out of what it runs."""

    def test_consuming_removes_the_stamp_and_nothing_else(self) -> None:
        environ = {STAMP_ROOT_ENV: "/r", STAMP_ID_ENV: "D-0123456789abcdef", "HOME": "/h"}
        consume_stamp(environ)
        self.assertEqual(environ, {"HOME": "/h"})

    def test_an_unstamped_environment_is_left_as_it_was(self) -> None:
        environ = {"HOME": "/h"}
        consume_stamp(environ)
        self.assertEqual(environ, {"HOME": "/h"})

    def test_the_test_harness_drops_an_inherited_stamp(self) -> None:
        """A stamped agent's own test run reaches its fixtures as the main session's would."""
        stamped = {**os.environ, STAMP_ROOT_ENV: _REPO.as_posix(), STAMP_ID_ENV: "D-x"}
        probe = f"import os, tests; print(os.environ.get({STAMP_ROOT_ENV!r}, 'absent'))"
        result = subprocess.run(  # noqa: S603 -- the running interpreter, a literal argv
            [sys.executable, "-c", probe],
            cwd=_REPO,
            env=stamped,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=True,
        )
        self.assertEqual(result.stdout.strip(), "absent")


if __name__ == "__main__":
    unittest.main()
