"""Tests for gzkit.hooks.guards — pytest usage scanner.

@covers REQ-0.25.0-27-01
@covers REQ-0.25.0-27-02
@covers REQ-0.25.0-27-03
@covers REQ-0.25.0-27-04
@covers REQ-0.25.0-27-05
"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.hooks import guards


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestIterFiles(unittest.TestCase):
    """iter_files walks a root and filters by suffix, excluded dirs, and path snippets."""

    def test_yields_allowed_suffixes(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "a.py", "x = 1\n")
            _write(root / "pyproject.toml", "[project]\n")
            _write(root / "conf.ini", "[section]\n")
            _write(root / "setup.cfg", "[metadata]\n")
            _write(root / "data.yaml", "key: value\n")
            _write(root / "notes.yml", "a: 1\n")
            _write(root / "req.txt", "foo\n")
            _write(root / "README.md", "# ignored\n")
            _write(root / "pic.png", "\x89PNG\n")

            yielded = {p.name for p in guards.iter_files(root)}
            self.assertIn("a.py", yielded)
            self.assertIn("pyproject.toml", yielded)
            self.assertIn("conf.ini", yielded)
            self.assertIn("setup.cfg", yielded)
            self.assertIn("data.yaml", yielded)
            self.assertIn("notes.yml", yielded)
            self.assertIn("req.txt", yielded)
            self.assertNotIn("README.md", yielded)
            self.assertNotIn("pic.png", yielded)

    def test_excludes_top_level_excluded_dirs(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for excluded in (".git", ".venv", "venv", "env", "site", "build", "dist", "htmlcov"):
                _write(root / excluded / "hidden.py", "import pytest\n")
            _write(root / "keep.py", "ok = 1\n")

            yielded = list(guards.iter_files(root))
            names = {p.name for p in yielded}
            self.assertIn("keep.py", names)
            self.assertNotIn(
                "hidden.py",
                names,
                msg=f"Excluded dir contents leaked: {[str(p) for p in yielded]}",
            )

    def test_excludes_docs_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "docs" / "guide.py", "import pytest\n")
            _write(root / "pkg" / "docs" / "inner.py", "import pytest\n")
            _write(root / "keep.py", "ok = 1\n")

            names = {p.name for p in guards.iter_files(root)}
            self.assertIn("keep.py", names)
            self.assertNotIn("guide.py", names)
            self.assertNotIn("inner.py", names)

    def test_excludes_self_reference_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "gzkit" / "hooks" / "guards.py", "import pytest\n")
            _write(root / "other.py", "ok = 1\n")

            names = {p.name for p in guards.iter_files(root)}
            self.assertIn("other.py", names)
            paths = [p.as_posix() for p in guards.iter_files(root)]
            self.assertFalse(
                any("gzkit/hooks/guards.py" in p for p in paths),
                msg=f"Self-ref leaked: {paths}",
            )


class TestScanFileSourceLevel(unittest.TestCase):
    """scan_file detects pytest usage patterns line-by-line in source files."""

    def _scan(self, content: str, name: str = "mod.py") -> list[str]:
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td) / name, content)
            return guards.scan_file(p)

    def test_detects_import_pytest(self) -> None:
        result = self._scan("import pytest\n")
        self.assertEqual(len(result), 1)
        self.assertIn("L1:", result[0])

    def test_detects_from_pytest_import(self) -> None:
        result = self._scan("from pytest import fixture\n")
        self.assertEqual(len(result), 1)
        self.assertIn("L1:", result[0])

    def test_detects_pytest_dot_reference(self) -> None:
        result = self._scan("value = pytest.fixture\n")
        self.assertEqual(len(result), 1)

    def test_detects_pytest_decorator(self) -> None:
        result = self._scan("@pytest.mark.slow\ndef test():\n    pass\n")
        self.assertEqual(len(result), 1)
        self.assertIn("L1:", result[0])

    def test_detects_py_test_alias(self) -> None:
        result = self._scan("value = py.test\n")
        self.assertEqual(len(result), 1)

    def test_clean_file_returns_empty(self) -> None:
        result = self._scan(
            "import unittest\n\nclass T(unittest.TestCase):\n    def test_ok(self):\n        pass\n"
        )
        self.assertEqual(result, [])

    def test_multiple_violations_report_line_numbers(self) -> None:
        content = "import pytest\n# comment\nuse = pytest.fixture\n"
        result = self._scan(content)
        self.assertEqual(len(result), 2)
        self.assertTrue(any("L1:" in v for v in result))
        self.assertTrue(any("L3:" in v for v in result))


class TestScanFileSpecialCases(unittest.TestCase):
    """scan_file has special-case handling for conftest.py and dependency config files."""

    def test_conftest_short_circuits_even_if_clean(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td) / "conftest.py", "# totally innocent\n")
            result = guards.scan_file(p)
            self.assertEqual(result, ["contains pytest-specific conftest.py"])

    def test_pyproject_with_pytest_dependency_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = _write(
                Path(td) / "pyproject.toml",
                "[project]\nname = 'x'\ndependencies = ['pytest']\n",
            )
            self.assertEqual(guards.scan_file(p), ["declares pytest dependency"])

    def test_pyproject_without_pytest_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td) / "pyproject.toml", "[project]\nname = 'x'\n")
            self.assertEqual(guards.scan_file(p), [])

    def test_requirements_txt_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td) / "requirements.txt", "pytest==7.4\n")
            self.assertEqual(guards.scan_file(p), ["declares pytest dependency"])

    def test_requirements_dev_txt_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td) / "requirements-dev.txt", "Pytest>=8\n")
            self.assertEqual(guards.scan_file(p), ["declares pytest dependency"])

    def test_requirements_txt_case_insensitive(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td) / "requirements.txt", "PyTest==7.0\n")
            self.assertEqual(guards.scan_file(p), ["declares pytest dependency"])


class TestScanFileReadError(unittest.TestCase):
    """scan_file returns an 'unreadable file' message on OSError."""

    def test_unreadable_file_reports_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            p = _write(Path(td) / "broken.py", "import pytest\n")
            with mock.patch.object(Path, "read_text", side_effect=PermissionError("denied")):
                result = guards.scan_file(p)
            self.assertEqual(len(result), 1)
            self.assertTrue(result[0].startswith("unreadable file:"))
            self.assertIn("denied", result[0])


class TestForbidPytest(unittest.TestCase):
    """forbid_pytest integrates iter_files + scan_file and returns an exit code."""

    def test_clean_root_returns_zero(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "pkg" / "mod.py", "import unittest\n")
            _write(root / "pkg" / "tests" / "test_mod.py", "import unittest\n")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = guards.forbid_pytest(root)
            self.assertEqual(rc, 0)
            self.assertEqual(buf.getvalue(), "")

    def test_bad_py_file_returns_one_and_prints_findings(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "bad.py", "import pytest\n")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = guards.forbid_pytest(root)
            output = buf.getvalue()
            self.assertEqual(rc, 1)
            self.assertIn("pytest usage detected", output)
            self.assertIn("bad.py", output)
            self.assertIn("L1:", output)
            self.assertIn("Please remove pytest references", output)

    def test_conftest_under_root_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "pkg" / "conftest.py", "# empty\n")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = guards.forbid_pytest(root)
            self.assertEqual(rc, 1)
            self.assertIn("contains pytest-specific conftest.py", buf.getvalue())

    def test_pyproject_dependency_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "pyproject.toml", "[project]\ndependencies = ['pytest']\n")

            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = guards.forbid_pytest(root)
            self.assertEqual(rc, 1)
            self.assertIn("declares pytest dependency", buf.getvalue())


class TestSafePrint(unittest.TestCase):
    """_safe_print prints ASCII normally, falls back to backslash escape on encode errors."""

    def test_ascii_passes_through(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            guards._safe_print("plain ascii line")
        self.assertEqual(buf.getvalue(), "plain ascii line\n")

    def test_unicode_encode_error_triggers_fallback(self) -> None:
        captured: list[str] = []

        def fake_print(*args: object, **kwargs: object) -> None:
            text = str(args[0]) if args else ""
            if "\u2713" in text:
                raise UnicodeEncodeError("cp1252", text, 0, 1, "narrow terminal")
            captured.append(text)

        with mock.patch("gzkit.hooks.guards.print", side_effect=fake_print, create=True):
            guards._safe_print("pre \u2713 post")

        self.assertEqual(len(captured), 1)
        fallback = captured[0]
        self.assertIn("pre ", fallback)
        self.assertNotIn("\u2713", fallback)
        self.assertIn("\\u2713", fallback)

    def test_encodable_unicode_prints_directly(self) -> None:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            guards._safe_print("cafe")
        self.assertEqual(buf.getvalue(), "cafe\n")


class TestMain(unittest.TestCase):
    """main() delegates to forbid_pytest(Path.cwd())."""

    def test_main_returns_zero_on_clean_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "ok.py", "import unittest\n")
            with mock.patch.object(Path, "cwd", return_value=root):
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc = guards.main()
            self.assertEqual(rc, 0)


if __name__ == "__main__":
    unittest.main()
