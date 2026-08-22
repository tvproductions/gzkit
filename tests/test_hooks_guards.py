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

    def test_prose_sentence_ending_in_pytest_not_flagged(self) -> None:
        """A doctrine string ending a sentence with 'pytest.' is prose, not usage (GHI #621).

        The detector targets module-attribute access (pytest.<identifier>); a
        sentence-ending 'pytest. ' in a quoted policy reference is not a pytest
        usage and must not trip the guard.
        """
        content = '_DOCTRINE = "Testing: unittest over pytest. Enforced by forbid-pytest hook."\n'
        self.assertEqual(self._scan(content), [])

    def test_pytest_attribute_access_still_flagged(self) -> None:
        """The class fix must not weaken real detection: pytest.<attr> still flags."""
        self.assertEqual(len(self._scan("value = pytest.raises(ValueError)\n")), 1)

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


class TestMxCheckpointSeam(unittest.TestCase):
    """The pre-commit enforcement surface resolves every guard through the shared checkpoint.

    Backs the GHI #843 direct fix. ADR-0.0.74 Boundary Invariant #2 states that
    *every* fail-closed funnel resolves its effective level through the shared MX
    checkpoint, and that "a guard that decides its own severity OR its own
    disposition without the checkpoint is the named coverage defect". The
    pre-commit guards did exactly that, so the hangar had no authority over one of
    the two enforcement surfaces governance uses.

    Semantics asserted (not strings): non-floor guards stop blocking inside the
    hangar, gate5_invariants members keep blocking there, nothing demotes outside
    it, an unreadable checkpoint fails closed, and the inventory cannot be
    forgotten by the next guard author.
    """

    @staticmethod
    def _hangar(td: str) -> Path:
        """Return a project root carrying an active MX marker."""
        root = Path(td)
        (root / ".gzkit").mkdir(parents=True, exist_ok=True)
        (root / ".gzkit" / "mx.json").write_text('{"session_id": "test-session"}', encoding="utf-8")
        return root

    def _sweep(self, root: Path, failing: str) -> tuple[int, str]:
        """Run the guard sweep with exactly *failing* returning 1 and the rest 0."""
        with contextlib.ExitStack() as stack:
            for _, attr, _ in guards._GUARD_META:
                stack.enter_context(
                    mock.patch.object(guards, attr, return_value=1 if attr == failing else 0)
                )
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                code = guards.run_guards(root)
        return code, buf.getvalue()

    def test_non_floor_guard_demotes_inside_the_hangar(self) -> None:
        """A non-floor guard's violation stops blocking once the hangar is open."""
        with tempfile.TemporaryDirectory() as td:
            code, _ = self._sweep(self._hangar(td), "forbid_pytest")
        self.assertEqual(code, 0, "a non-floor pre-commit guard must demote under the marker")

    def test_demotion_is_announced_rather_than_silent(self) -> None:
        """A demoted guard stays visible — advisory means non-grounding, never discarded.

        The failure this pins is the one recorded on GHI #843 itself: findings
        collected and then dropped with nothing said, so an operator cannot tell a
        clean run from a demoted one.
        """
        with tempfile.TemporaryDirectory() as td:
            _, out = self._sweep(self._hangar(td), "forbid_pytest")
        self.assertIn("forbid-pytest", out)
        self.assertIn("advisory", out.lower())

    def test_ledger_guard_pins_inside_the_hangar(self) -> None:
        """`ledger` is a gate5_invariants member — the hangar can never demote it."""
        with tempfile.TemporaryDirectory() as td:
            code, _ = self._sweep(self._hangar(td), "forbid_manual_ledger_edits")
        self.assertEqual(code, 1, "the ledger floor member must keep blocking in the hangar")

    def test_gate5_attestation_guard_pins_inside_the_hangar(self) -> None:
        """An unattested OBPI completion is faked Gate-5 — never advisory (AGENTS.md Never #1)."""
        with tempfile.TemporaryDirectory() as td:
            code, _ = self._sweep(self._hangar(td), "forbid_unattested_obpi_completion_commits")
        self.assertEqual(code, 1, "the gate5-attestation floor member must keep blocking")

    def test_guards_that_must_never_demote_still_block(self) -> None:
        """The four guards doctrine forbids demoting keep blocking inside the hangar.

        The names are listed HERE, derived from doctrine, and never read back out
        of `_GUARD_META`. A first draft derived them from the table under test
        (`[attr for ... if level == CRITICAL]`) and a mutant that downgraded the
        Stage-2 fence to ERROR SURVIVED — the guard simply left the list the
        assertion was built from. That is the tautological-test shape
        `.gzkit/rules/tests.md` forbids: it could not fail when the behaviour
        changed, because it re-derived its expectation from the change.
        """
        must_never_demote = {
            # gate5_invariants members — pin by NAME (ADR-0.0.74 BI#3)
            "forbid_manual_ledger_edits": "`ledger` — ledger integrity",
            "forbid_unattested_obpi_completion_commits": "`gate5-attestation`",
            # pinned by emitted CRITICAL — the quality.py precedent (GHI #651)
            "_run_enforcement_floor": "the §5 enforcement-claim meta-validator",
            "forbid_post_authoring_src_commits": "the Stage-2 fence (GHI #844)",
        }
        registered = {attr for _, attr, _ in guards._GUARD_META}
        self.assertEqual(
            set(must_never_demote) - registered,
            set(),
            "a guard doctrine forbids demoting is no longer registered at all",
        )
        with tempfile.TemporaryDirectory() as td:
            root = self._hangar(td)
            for attr, why in must_never_demote.items():
                with self.subTest(guard=attr):
                    code, _ = self._sweep(root, attr)
                    self.assertEqual(code, 1, f"{attr} must never demote — {why}")

    def test_nothing_demotes_outside_the_hangar(self) -> None:
        """Outside the marker every registered guard still blocks — demotion cannot leak."""
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".gzkit").mkdir(parents=True, exist_ok=True)
            for _, attr, _ in guards._GUARD_META:
                with self.subTest(guard=attr):
                    code, _ = self._sweep(root, attr)
                    self.assertEqual(code, 1, f"{attr} must block with no marker present")

    def test_unreadable_checkpoint_fails_closed(self) -> None:
        """If the checkpoint cannot be resolved the guard blocks — never silently demotes."""
        from gzkit.mx import checkpoint

        with tempfile.TemporaryDirectory() as td:
            root = self._hangar(td)
            with mock.patch.object(checkpoint, "resolve", side_effect=RuntimeError("boom")):
                code, _ = self._sweep(root, "forbid_pytest")
        self.assertEqual(code, 1, "an unresolvable checkpoint must fail closed, not demote")

    def test_every_forbid_guard_is_registered_in_the_inventory(self) -> None:
        """The funnel inventory cannot be forgotten — this is the fence GHI #843 lacked.

        ADR-0.0.74 Negative #6 named the cost up front: "every fail-closed funnel
        must consult the checkpoint; a funnel that forgets it silently stays hard".
        The inventory fence that shipped enumerated `validate_cmd` only, so the
        pre-commit surface was never in scope of any check.
        """
        forbid_fns = {
            name
            for name in dir(guards)
            if name.startswith("forbid_") and callable(getattr(guards, name))
        }
        registered = {attr for _, attr, _ in guards._GUARD_META}
        self.assertEqual(
            forbid_fns - registered,
            set(),
            "every forbid_* guard must be registered in _GUARD_META with an MX guard name",
        )

    def test_run_guards_holds_exactly_one_seam(self) -> None:
        """No guard is invoked directly — the loop over the inventory is the only call site.

        REQ-0.0.74-20-01's shape: ONE seam, not N inline substitutions. A direct
        call inside `run_guards` would bypass the checkpoint the same way the
        pre-checkpoint `main()` did.
        """
        import ast

        source = Path(guards.__file__).read_text(encoding="utf-8")
        fn = next(
            node
            for node in ast.walk(ast.parse(source))
            if isinstance(node, ast.FunctionDef) and node.name == "run_guards"
        )
        direct = [
            node.func.id
            for node in ast.walk(fn)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id.startswith("forbid_")
        ]
        self.assertEqual(
            direct, [], "guards must be reached through _GUARD_META, not called directly"
        )
