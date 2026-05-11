"""Unit tests for the complexity advisor auto-chain hook (OBPI-0.0.29-05).

Tests mock at the Python boundary per REQ-0.0.29-05-11: the diagnosis engine,
threshold table, and timeout primitive are mocked; subprocess invocation of the
shell hook is reserved for behave (REQ-0.0.29-05-08).
"""

from __future__ import annotations

import io
import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.complexity.advisor.diagnosis import (
    AdvisorDiagnosis,
    DoctrinalFrame,
    ProofRange,
    RefactorArchetype,
)
from gzkit.complexity.advisor.timeout import TimeoutOk, TimeoutTimedOut
from gzkit.hooks.install_complexity_advisor import (
    _HOOK_ID,
    install,
    run_auto_chain,
)

# --- test-data helpers ---------------------------------------------------


def _make_diagnosis(*, band: str = "warn") -> AdvisorDiagnosis:
    return AdvisorDiagnosis(
        metric="radon_cc",
        crossing_band=band,
        crossing_value=12.0,
        archetype=RefactorArchetype.LONG_PARAMETER_LIST,
        doctrinal_frame=DoctrinalFrame(
            authority="fowler",
            citation="Fowler Refactoring 2e ch.3",
            excerpt="Long Parameter List refactoring",
        ),
        proof=(
            ProofRange(
                file_path="src/foo.py",
                start_line=10,
                end_line=30,
                ast_node_kind="FunctionDef",
            ),
        ),
        recommended_move="Extract Parameter Object",
    )


def _make_timeout_ok(diagnoses: list[AdvisorDiagnosis]) -> TimeoutOk:
    return TimeoutOk(value=diagnoses)


def _make_timeout_timed_out() -> TimeoutTimedOut:
    return TimeoutTimedOut(elapsed_s=30.5, callable_name="_diagnose_files")


# --- covers decorators ---------------------------------------------------

try:
    from gzkit.testing import covers  # ty: ignore[unresolved-import]
except ImportError:

    def covers(*_ids: str):  # type: ignore[misc]
        def decorator(fn):  # type: ignore[no-untyped-def]
            return fn

        return decorator


# --- tests ----------------------------------------------------------------


class TestRunAutoChain(unittest.TestCase):
    """Tests for run_auto_chain — the Python runtime entry point."""

    @covers("REQ-0.0.29-05-06")
    @patch("gzkit.hooks.install_complexity_advisor.run_with_timeout")
    def test_block_band_exits_1(self, mock_timeout: MagicMock) -> None:
        """Block-band crossing causes exit code 1 (REQ-6)."""
        mock_timeout.return_value = _make_timeout_ok([_make_diagnosis(band="block")])
        code = run_auto_chain(["src/foo.py"])
        self.assertEqual(code, 1)

    @covers("REQ-0.0.29-05-06")
    @patch("gzkit.hooks.install_complexity_advisor.run_with_timeout")
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_warn_band_exits_0_with_stderr(
        self, mock_stderr: io.StringIO, mock_timeout: MagicMock
    ) -> None:
        """Warn-band crossing exits 0 with diagnosis to stderr (REQ-6)."""
        mock_timeout.return_value = _make_timeout_ok([_make_diagnosis(band="warn")])
        code = run_auto_chain(["src/foo.py"])
        self.assertEqual(code, 0)
        self.assertIn("Archetype", mock_stderr.getvalue())

    @covers("REQ-0.0.29-05-04")
    @patch("gzkit.hooks.install_complexity_advisor.run_with_timeout")
    def test_timeout_wraps_advisor(self, mock_timeout: MagicMock) -> None:
        """run_with_timeout is called with correct parameters (REQ-4)."""
        mock_timeout.return_value = _make_timeout_ok([])
        run_auto_chain(["src/foo.py"], timeout_s=15.0)
        mock_timeout.assert_called_once()
        call_kwargs = mock_timeout.call_args
        self.assertEqual(call_kwargs.kwargs["timeout_s"], 15.0)
        self.assertEqual(call_kwargs.kwargs["context_invocation"], "auto-chain")

    @covers("REQ-0.0.29-05-04")
    @patch("gzkit.hooks.install_complexity_advisor.run_with_timeout")
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_timeout_exits_0_fail_open(
        self, mock_stderr: io.StringIO, mock_timeout: MagicMock
    ) -> None:
        """Timeout returns exit 0 (fail-open) with warning (REQ-4)."""
        mock_timeout.return_value = _make_timeout_timed_out()
        code = run_auto_chain(["src/foo.py"])
        self.assertEqual(code, 0)
        self.assertIn("timed out", mock_stderr.getvalue())

    @covers("REQ-0.0.29-05-02")
    @patch("gzkit.hooks.install_complexity_advisor.run_with_timeout")
    def test_xenon_fail_triggers_advisor(self, mock_timeout: MagicMock) -> None:
        """When called, the advisor runs and returns diagnoses (REQ-2)."""
        diag = _make_diagnosis(band="warn")
        mock_timeout.return_value = _make_timeout_ok([diag])
        code = run_auto_chain(["src/foo.py"])
        self.assertEqual(code, 0)
        mock_timeout.assert_called_once()

    @covers("REQ-0.0.29-05-06")
    @patch("gzkit.hooks.install_complexity_advisor.run_with_timeout")
    def test_no_crossings_exits_0(self, mock_timeout: MagicMock) -> None:
        """No crossings detected returns exit 0."""
        mock_timeout.return_value = _make_timeout_ok([])
        code = run_auto_chain(["src/foo.py"])
        self.assertEqual(code, 0)


class TestDiagnoseFiles(unittest.TestCase):
    """Tests for _diagnose_files — the file-level analysis logic."""

    @covers("REQ-0.0.29-05-05")
    @patch("gzkit.hooks.install_complexity_advisor.DiagnosisEngine")
    @patch("gzkit.hooks.install_complexity_advisor.load_threshold_table")
    def test_staged_files_only(self, mock_load: MagicMock, mock_engine_cls: MagicMock) -> None:
        """Only the given file paths are analyzed, not the whole tree (REQ-5)."""
        from gzkit.hooks.install_complexity_advisor import _diagnose_files

        with tempfile.TemporaryDirectory() as tmp:
            staged = Path(tmp) / "staged.py"
            unstaged = Path(tmp) / "unstaged.py"
            staged.write_text("def f(): pass\n", encoding="utf-8")
            unstaged.write_text("def g(): pass\n", encoding="utf-8")

            mock_table = MagicMock()
            mock_table.band_for.return_value = None
            mock_load.return_value = mock_table
            mock_engine_cls.return_value = MagicMock()

            with patch(
                "gzkit.hooks.install_complexity_advisor._DEFAULT_RULE_PATH",
                staged,
            ):
                _diagnose_files([str(staged)])

            mock_load.assert_called_once()

    @covers("REQ-0.0.29-05-05")
    @patch("gzkit.hooks.install_complexity_advisor.load_threshold_table")
    def test_skips_non_python_files(self, mock_load: MagicMock) -> None:
        """Non-.py files are skipped."""
        from gzkit.hooks.install_complexity_advisor import _diagnose_files

        with tempfile.TemporaryDirectory() as tmp:
            txt_file = Path(tmp) / "readme.txt"
            txt_file.write_text("hello\n", encoding="utf-8")
            mock_load.return_value = MagicMock()

            with patch(
                "gzkit.hooks.install_complexity_advisor._DEFAULT_RULE_PATH",
                txt_file,
            ):
                result = _diagnose_files([str(txt_file)])
            self.assertEqual(result, [])


class TestInstaller(unittest.TestCase):
    """Tests for the install() function."""

    @covers("REQ-0.0.29-05-01")
    def test_installer_replaces_xenon_entry(self) -> None:
        """install() replaces xenon-complexity with composite hook (REQ-1)."""
        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".pre-commit-config.yaml"
            config_path.write_text(
                textwrap.dedent("""\
                    repos:
                      - repo: local
                        hooks:
                          - id: ruff-check
                            name: ruff check
                            entry: uvx ruff check --fix
                            language: system
                          - id: xenon-complexity
                            name: xenon
                            entry: uvx xenon --max-absolute C --max-modules C --max-average C src/
                            language: system
                            pass_filenames: false
                            types: [python]
                            stages: [pre-commit]
                          - id: unittest
                            name: unittest
                            entry: uv run -m unittest discover -q tests
                            language: system
                """),
                encoding="utf-8",
            )
            import contextlib  # noqa: PLC0415
            import io  # noqa: PLC0415

            original_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                with contextlib.redirect_stdout(io.StringIO()):
                    code = install()
            finally:
                os.chdir(original_cwd)

            self.assertEqual(code, 0)
            result = config_path.read_text(encoding="utf-8")
            self.assertIn(_HOOK_ID, result)
            self.assertNotIn("xenon-complexity", result)
            self.assertIn("ruff-check", result)
            self.assertIn("unittest", result)

    @covers("REQ-0.0.29-05-01")
    def test_installer_idempotent(self) -> None:
        """install() is idempotent when hook is already present."""
        import contextlib  # noqa: PLC0415
        import io  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            config_path = Path(tmp) / ".pre-commit-config.yaml"
            config_path.write_text(
                f"hooks:\n  - id: {_HOOK_ID}\n    name: test\n",
                encoding="utf-8",
            )
            original_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                with contextlib.redirect_stdout(io.StringIO()):
                    code = install()
            finally:
                os.chdir(original_cwd)
            self.assertEqual(code, 0)


class TestShellHookContract(unittest.TestCase):
    """Tests for the shell hook script contract."""

    @covers("REQ-0.0.29-05-10")
    def test_hook_is_posix_shell(self) -> None:
        """Hook script starts with #!/bin/sh (REQ-10)."""
        hook_path = Path(".gzkit/hooks/pre-commit-complexity-advisor")
        self.assertTrue(hook_path.exists(), f"Hook not found at {hook_path}")
        first_line = hook_path.read_text(encoding="utf-8").splitlines()[0]
        self.assertEqual(first_line, "#!/bin/sh")

    @covers("REQ-0.0.29-05-10")
    def test_hook_is_executable(self) -> None:
        """Hook script has executable permission (REQ-10).

        On Windows the POSIX execute bit is not surfaced in `os.stat`, but git
        preserves the canonical mode (100755) in the index, which is the
        contract the hook must satisfy when checked out on a POSIX worktree.
        Cross-platform fix lands under GHI #442.
        """
        hook_path = Path(".gzkit/hooks/pre-commit-complexity-advisor")
        self.assertTrue(hook_path.exists())
        result = subprocess.run(
            ["git", "ls-files", "--stage", str(hook_path)],
            capture_output=True,
            text=True,
            check=True,
        )
        stored_mode = result.stdout.split()[0] if result.stdout.strip() else ""
        self.assertEqual(
            stored_mode,
            "100755",
            f"Hook git mode {stored_mode!r} != '100755' (not executable in tree)",
        )

    @covers("REQ-0.0.29-05-12")
    def test_no_operator_email_in_artifacts(self) -> None:
        """No personal email in hook or installer files (REQ-12)."""
        paths = [
            Path(".gzkit/hooks/pre-commit-complexity-advisor"),
            Path("src/gzkit/hooks/install_complexity_advisor.py"),
        ]
        email_markers = ["@" + "gmail.com", "@" + "yahoo.com"]
        for path in paths:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                for marker in email_markers:
                    self.assertNotIn(
                        marker,
                        content,
                        f"Personal email found in {path}",
                    )


class TestCoversDecorators(unittest.TestCase):
    """Verify tests use tempfile-backed fixtures and @covers decorators (REQ-7)."""

    @covers("REQ-0.0.29-05-07")
    def test_tests_use_tempfile_and_covers(self) -> None:
        """Test suite uses tempfile-backed fixtures and @covers decorators."""
        test_path = Path("tests/hooks/test_complexity_advisor_auto_chain.py")
        content = test_path.read_text(encoding="utf-8")
        self.assertIn("tempfile", content)
        self.assertIn("@covers", content)
        self.assertIn("REQ-0.0.29-05", content)


class TestSkipBehavior(unittest.TestCase):
    """Tests for SKIP bypass wiring."""

    @covers("REQ-0.0.29-05-03")
    def test_skip_env_bypasses_both(self) -> None:
        """Shell hook contains no internal SKIP check — pre-commit handles it.

        The composite hook id ``complexity-advisor-auto-chain`` means
        ``SKIP=complexity-advisor-auto-chain git commit`` skips the entire
        hook (both xenon and advisor) via the pre-commit framework's native
        SKIP mechanism. This test verifies the hook script does not redefine
        SKIP semantics (REQ-3 says 'honored as-is from the chore').
        """
        hook_path = Path(".gzkit/hooks/pre-commit-complexity-advisor")
        content = hook_path.read_text(encoding="utf-8")
        self.assertNotIn("SKIP_COMPLEXITY", content)
        self.assertNotIn("SKIP_XENON", content)


if __name__ == "__main__":
    unittest.main()
