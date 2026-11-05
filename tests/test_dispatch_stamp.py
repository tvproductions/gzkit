"""The verb refusal of RP-12 ruling 17, read from the stamp a hook puts on a subagent's call.

The stamp is two environment variables (ruling 34 has the hook set them on a
subagent's ``gz`` command). A call carrying the root variable is a subagent's; a
call without it is the main session's and is never refused (#1296's case 3). The
real root is the directory the verb runs in, ``get_project_root``'s answer, read
only for a stamped call.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.cli.main import _build_parser
from gzkit.dispatch_stamp import STAMP_ID_ENV, STAMP_ROOT_ENV, consume_stamp, stamp_refusal
from tests.commands.common import CliRunner, _quick_init

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

    def test_a_stamped_call_whose_real_root_cannot_be_read_is_refused(self) -> None:
        """Ruling 36's exit 3 holds where the directory was deleted under the shell."""
        stamp = {STAMP_ROOT_ENV: self.project.as_posix(), STAMP_ID_ENV: "D-0123456789abcdef"}
        refusal = stamp_refusal(stamp, _never)
        self.assertIsNotNone(refusal)
        self.assertIn("D-0123456789abcdef", str(refusal))

    def test_a_volume_with_no_real_inode_numbers_compares_by_path(self) -> None:
        """Where every directory reports inode 0, matching inodes say nothing."""
        real_stat = Path.stat

        def no_inode(path: Path, *args: object, **kwargs: object) -> os.stat_result:
            fields = list(real_stat(path, *args, **kwargs))  # ty: ignore[invalid-argument-type]
            fields[1], fields[2] = 0, 1  # st_ino, st_dev
            return os.stat_result(fields)

        with patch.object(Path, "stat", no_inode):
            self.assertIsNotNone(self._refusal(self.scratch.as_posix(), self.project))
            self.assertIsNone(self._refusal(self.project.as_posix(), self.project))

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


class RefusalOutOfService(unittest.TestCase):
    """Ruling 28: the verb refusal is on at every level, out of service included."""

    def test_the_refusal_holds_with_the_alarms_off(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            here = Path(directory).resolve()
            stamp = {STAMP_ROOT_ENV: (here / "elsewhere").as_posix(), STAMP_ID_ENV: "D-x"}
            with patch("gzkit.mx.alarms.alarms_off", return_value=True):
                self.assertIsNotNone(stamp_refusal(stamp, lambda: here))


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
        stamped.pop("PYTHONSAFEPATH", None)  # the probe imports ``tests`` from its cwd
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
            timeout=60,
        )
        self.assertEqual(result.stdout.strip(), "absent")


def _leaf_parsers(parser: argparse.ArgumentParser) -> list[argparse.ArgumentParser]:
    found = [parser]
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for child in action.choices.values():
                found.extend(_leaf_parsers(child))
    return found


class StampForwarded(unittest.TestCase):
    """A verb that runs a command its caller supplies passes the stamp on to it.

    Ruling 37 rests on a nested gz having its directory chosen by the verb's code;
    a forwarded command is the agent's, so it keeps the stamp (the review of
    ruling 42, which voided through `gz arb step -- gz wp dispatch --void`).
    """

    def test_every_parser_taking_a_trailing_command_forwards_the_stamp(self) -> None:
        for parser in _leaf_parsers(_build_parser()):
            trailing = any(action.nargs == argparse.REMAINDER for action in parser._actions)
            if trailing:
                with self.subTest(parser=parser.prog):
                    self.assertTrue(parser.get_default("forwards_command"))

    def test_a_forwarded_command_runs_with_the_stamp(self) -> None:

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd().resolve().as_posix()
            probe = f"import os; print('child:', os.environ.get({STAMP_ROOT_ENV!r}, 'absent'))"
            argv = ["arb", "step", "--name", "probe", "--", sys.executable, "-c", probe]
            with unittest.mock.patch.dict(os.environ, {STAMP_ROOT_ENV: root, STAMP_ID_ENV: ""}):
                result = runner.invoke(main, argv)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertIn(f"child: {root}", result.output)


if __name__ == "__main__":
    unittest.main()
