"""Tests for resolving an external tool before gzkit spawns it (RO-9 tranche 4, S607).

A bare ``"git"`` in an argv lets the operating system choose the binary, and on
Windows ``CreateProcess`` tries the current directory before ``PATH``, so a
``git.exe`` committed to a repository gzkit runs inside would be the one spawned.
``shutil.which`` keeps that search order, so the resolver reads absolute ``PATH``
entries only.
"""

import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.executables import find_executable, resolve_argv, resolve_executable

_NAME = "gzkit-probe-tool"


def _plant(directory: Path) -> Path:
    """Write an executable named ``_NAME`` into ``directory``.

    Returns:
        The planted file's path.
    """
    suffix = ".EXE" if sys.platform == "win32" else ""
    tool = directory / f"{_NAME}{suffix}"
    tool.write_text("", encoding="utf-8")
    tool.chmod(tool.stat().st_mode | stat.S_IXUSR)
    return tool


class TestResolveExecutable(unittest.TestCase):
    def test_returns_the_absolute_path_on_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tool = _plant(Path(tmp))
            with patch.dict(os.environ, {"PATH": tmp}):
                found = Path(resolve_executable(_NAME))
            self.assertTrue(found.is_absolute())
            self.assertTrue(found.samefile(tool))

    def test_never_resolves_from_the_current_directory(self) -> None:
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as bindir:
            _plant(Path(cwd))
            real = _plant(Path(bindir))
            previous = Path.cwd()
            os.chdir(cwd)
            try:
                with patch.dict(os.environ, {"PATH": bindir}):
                    found = Path(resolve_executable(_NAME))
            finally:
                os.chdir(previous)
            self.assertTrue(found.samefile(real))

    def test_skips_relative_path_entries(self) -> None:
        with tempfile.TemporaryDirectory() as cwd:
            (Path(cwd) / "bin").mkdir()
            _plant(Path(cwd) / "bin")
            previous = Path.cwd()
            os.chdir(cwd)
            try:
                with (
                    patch.dict(os.environ, {"PATH": os.pathsep.join(["bin", "."])}),
                    self.assertRaises(FileNotFoundError),
                ):
                    resolve_executable(_NAME)
            finally:
                os.chdir(previous)

    def test_missing_tool_raises_what_subprocess_would(self) -> None:
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.dict(os.environ, {"PATH": tmp}),
            self.assertRaises(FileNotFoundError) as raised,
        ):
            resolve_executable(_NAME)
        self.assertEqual(raised.exception.filename, _NAME)


class TestFindExecutable(unittest.TestCase):
    def test_missing_tool_is_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {"PATH": tmp}):
            self.assertIsNone(find_executable(_NAME))

    def test_never_finds_a_tool_in_the_current_directory_alone(self) -> None:
        with tempfile.TemporaryDirectory() as cwd, tempfile.TemporaryDirectory() as empty:
            _plant(Path(cwd))
            previous = Path.cwd()
            os.chdir(cwd)
            try:
                with patch.dict(os.environ, {"PATH": empty}):
                    self.assertIsNone(find_executable(_NAME))
            finally:
                os.chdir(previous)


class TestResolveArgv(unittest.TestCase):
    def test_resolves_a_bare_executable_and_keeps_the_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tool = _plant(Path(tmp))
            with patch.dict(os.environ, {"PATH": tmp}):
                head, *rest = resolve_argv([_NAME, "status", "--porcelain"])
            self.assertTrue(Path(head).samefile(tool))
            self.assertEqual(rest, ["status", "--porcelain"])

    def test_keeps_an_executable_named_with_a_directory(self) -> None:
        with patch.dict(os.environ, {"PATH": ""}):
            self.assertEqual(
                resolve_argv([sys.executable, "-c", "pass"]), [sys.executable, "-c", "pass"]
            )


if __name__ == "__main__":
    unittest.main()
