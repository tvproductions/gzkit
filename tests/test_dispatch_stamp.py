"""The verb refusal of RP-12 ruling 17, read from the stamp a hook puts on a subagent's call.

The stamp is two environment variables (ruling 34 has the hook set them on a
subagent's ``gz`` command). A call carrying the root variable is a subagent's; a
call without it is the main session's and is never refused (#1296's case 3). The
real root is the directory the verb runs in, ``get_project_root``'s answer.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.dispatch_stamp import STAMP_ID_ENV, STAMP_ROOT_ENV, stamp_refusal


class StampRefusal(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.base = Path(directory.name)
        self.project = self.base / "project"
        self.scratch = self.base / "scratch"
        self.project.mkdir()
        self.scratch.mkdir()

    def _stamp(self, root: str) -> dict[str, str]:
        return {STAMP_ROOT_ENV: root, STAMP_ID_ENV: "D-0123456789abcdef"}

    def test_an_unstamped_call_is_the_main_sessions_and_proceeds(self) -> None:
        self.assertIsNone(stamp_refusal({}, self.project))

    def test_a_stamp_naming_the_real_root_proceeds(self) -> None:
        self.assertIsNone(stamp_refusal(self._stamp(self.project.as_posix()), self.project))

    def test_a_stamp_naming_another_root_is_refused(self) -> None:
        refusal = stamp_refusal(self._stamp(self.scratch.as_posix()), self.project)
        self.assertIsNotNone(refusal)
        self.assertIn("D-0123456789abcdef", str(refusal))

    def test_a_stamp_naming_no_root_is_refused(self) -> None:
        """Ruling 17: a subagent with no dispatch record is stamped with no root."""
        for empty in ("", "  "):
            with self.subTest(root=empty):
                self.assertIsNotNone(stamp_refusal(self._stamp(empty), self.project))

    def test_a_relative_stamp_root_is_refused(self) -> None:
        self.assertIsNotNone(stamp_refusal(self._stamp("project"), self.base))

    def test_a_subdirectory_of_the_intended_root_is_another_root(self) -> None:
        """A verb's root is its directory, so a subdirectory books into another project."""
        inner = self.project / "inner"
        inner.mkdir()
        self.assertIsNotNone(stamp_refusal(self._stamp(self.project.as_posix()), inner))

    def test_both_sides_are_resolved_before_comparing(self) -> None:
        """A link to the intended root is the intended root, and a link elsewhere is not."""
        link = self.base / "link"
        try:
            link.symlink_to(self.project, target_is_directory=True)
        except OSError as exc:  # Windows without the symlink privilege
            self.skipTest(f"no symlink here: {exc}")
        self.assertIsNone(stamp_refusal(self._stamp(link.as_posix()), self.project))
        self.assertIsNone(stamp_refusal(self._stamp(self.project.as_posix()), link))
        self.assertIsNotNone(stamp_refusal(self._stamp(link.as_posix()), self.scratch))


if __name__ == "__main__":
    unittest.main()
