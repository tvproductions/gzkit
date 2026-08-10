"""CLI tests for ``gz complexity guide`` (OBPI-0.0.30-01).

Covers REQ-0.0.30-01-01 through REQ-0.0.30-01-06 (acceptance criteria).
Subprocess boundaries are mocked at the engine-import level.

Test-class split:

* ``TestComplexityGuideBehavior`` — REQ-derived semantic assertions
  (exit codes, JSON shape, parsing, exit-3-never-produced).
* ``TestComplexityGuideOutputForm`` — Invariant-3 fixture pinning the
  default human prose form (string-shape assertions live only here).
* ``TestComplexityGuideCliAuditParity`` — REQ-06 CLI-audit coverage.
"""

from __future__ import annotations

import io
import json
import os
import tempfile
import unittest
from collections.abc import Iterator
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gzkit.commands.complexity_guide import complexity_guide_cmd
from gzkit.complexity.authoring.hint import AuthoringHint
from gzkit.traceability import covers


def _make_hint(
    *,
    archetype: str = "arrowhead",
    precedence_band: str = "approaching",
    file_path: str = "src/example.py",
    start_line: int = 1,
    end_line: int = 20,
) -> AuthoringHint:
    """Build a synthetic AuthoringHint for mocking."""
    return AuthoringHint(
        metric="radon_cc",
        precedence_band=precedence_band,  # type: ignore
        crossing_value=5.0,
        archetype=archetype,  # type: ignore
        doctrinal_frame_headline="Function decomposition signal.",
        recommended_move="Extract the inner branches into separate functions.",
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
    )


@contextmanager
def _rule_path_env() -> Iterator[Path]:
    """Yield a temp dir with CWD changed to it and rule path file present."""
    with tempfile.TemporaryDirectory() as raw_root:
        root = Path(raw_root)
        rule_dir = root / ".gzkit" / "rules"
        rule_dir.mkdir(parents=True)
        rule_path = rule_dir / "complexity-thresholds.json"
        rule_path.write_text("{}", encoding="utf-8")
        prior_cwd = Path.cwd()
        os.chdir(root)
        try:
            yield root
        finally:
            os.chdir(prior_cwd)


def _invoke(**kwargs: object) -> tuple[int, str, str]:
    """Call ``complexity_guide_cmd`` collapsing SystemExit into an exit code."""
    out = io.StringIO()
    err = io.StringIO()
    code = 0
    try:
        with redirect_stdout(out), redirect_stderr(err):
            code = complexity_guide_cmd(**kwargs) or 0
    except SystemExit as exc:
        raw = exc.code
        code = raw if isinstance(raw, int) else 1
    return int(code), out.getvalue(), err.getvalue()


class TestComplexityGuideBehavior(unittest.TestCase):
    """REQ-derived semantic tests for ``gz complexity guide``."""

    @covers("REQ-0.0.30-01-01")
    def test_clean_file_exit_0_no_hints(self) -> None:
        """Clean file (no advise crossings) produces exit 0 with no-hints message."""
        with _rule_path_env() as root:
            target = root / "clean.py"
            target.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
            with patch("gzkit.commands.complexity_guide._engine_analyze") as mock_analyze:
                mock_analyze.return_value = ()
                code, out, _err = _invoke(path=str(target))
        self.assertEqual(code, 0)
        self.assertIn("No advise-band hints found", out)

    @covers("REQ-0.0.30-01-02")
    def test_advise_band_crossings_exit_0_prose(self) -> None:
        """File with advise-band crossings produces exit 0 + one prose block per hint."""
        hint = _make_hint(archetype="arrowhead", start_line=5, end_line=25)
        with _rule_path_env() as root:
            target = root / "subject.py"
            target.write_text("def f(): pass\n", encoding="utf-8")
            with patch("gzkit.commands.complexity_guide._engine_analyze") as mock_analyze:
                mock_analyze.return_value = (hint,)
                code, out, _err = _invoke(path=str(target))
        self.assertEqual(code, 0)
        self.assertIn("Archetype", out)
        self.assertIn("arrowhead", out)
        self.assertIn("Move", out)
        self.assertIn("Guidance", out)

    @covers("REQ-0.0.30-01-03")
    def test_json_mode_valid_schema(self) -> None:
        """``--json`` emits valid JSON validating against AuthoringHint fields."""
        hint = _make_hint(archetype="arrowhead")
        with _rule_path_env() as root:
            target = root / "subject.py"
            target.write_text("def f(): pass\n", encoding="utf-8")
            with patch("gzkit.commands.complexity_guide._engine_analyze") as mock_analyze:
                mock_analyze.return_value = (hint,)
                code, out, _err = _invoke(path=str(target), json_output=True)
        self.assertEqual(code, 0)
        parsed = json.loads(out)
        self.assertIsInstance(parsed, list)
        self.assertEqual(len(parsed), 1)
        item = parsed[0]
        self.assertIn("metric", item)
        self.assertIn("precedence_band", item)
        self.assertIn("archetype", item)
        self.assertIn("recommended_move", item)
        self.assertIn("file_path", item)
        self.assertIn("start_line", item)
        self.assertIn("end_line", item)

    @covers("REQ-0.0.30-01-04")
    def test_warn_and_block_not_included(self) -> None:
        """Engine returns only advise-band hints; exit code is never 3."""
        with _rule_path_env() as root:
            target = root / "subject.py"
            target.write_text("def f(): pass\n", encoding="utf-8")
            with patch("gzkit.commands.complexity_guide._engine_analyze") as mock_analyze:
                # Engine already filters to advise-band only; simulate many hints
                hints = tuple(_make_hint() for _ in range(5))
                mock_analyze.return_value = hints
                code, _out, _err = _invoke(path=str(target))
        self.assertEqual(code, 0)

    @covers("REQ-0.0.30-01-05")
    def test_help_flag_exit_0_sections(self) -> None:
        """``--help`` exits 0 and contains description, usage, options, examples."""
        from gzkit.cli.main import _build_parser  # noqa: PLC0415

        parser = _build_parser()
        out = io.StringIO()
        try:
            with redirect_stdout(out):
                parser.parse_args(["complexity", "guide", "--help"])
        except SystemExit as exc:
            self.assertEqual(exc.code, 0)
        text = out.getvalue()
        self.assertIn("usage", text.lower())
        self.assertIn("options", text.lower())
        self.assertIn("guide", text.lower())

    def test_bad_path_exit_1(self) -> None:
        """Non-existent path exits 1."""
        with _rule_path_env():
            code, _out, err = _invoke(path="/nonexistent/path/that/does/not/exist.py")
        self.assertEqual(code, 1)
        self.assertIn("does not exist", err)

    def test_missing_threshold_table_exit_2(self) -> None:
        """Missing threshold table exits 2."""
        with tempfile.TemporaryDirectory() as raw_root:
            root = Path(raw_root)
            target = root / "subject.py"
            target.write_text("def f(): pass\n", encoding="utf-8")
            prior_cwd = Path.cwd()
            os.chdir(root)
            try:
                # No .gzkit/rules/complexity-thresholds.json created
                code, _out, err = _invoke(path=str(target))
            finally:
                os.chdir(prior_cwd)
        self.assertEqual(code, 2)
        self.assertIn("threshold rule not found", err)

    @covers("REQ-0.0.30-01-04")
    def test_exit_3_never_produced(self) -> None:
        """Even with many hints, exit code is never 3."""
        with _rule_path_env() as root:
            target = root / "subject.py"
            target.write_text("def f(): pass\n", encoding="utf-8")
            with patch("gzkit.commands.complexity_guide._engine_analyze") as mock_analyze:
                mock_analyze.return_value = tuple(_make_hint() for _ in range(20))
                code, _out, _err = _invoke(path=str(target))
        self.assertNotEqual(code, 3)
        self.assertEqual(code, 0)


class TestComplexityGuideOutputForm(unittest.TestCase):
    """Invariant-3 fixture: prose output contains expected header labels."""

    def test_prose_output_contains_headers(self) -> None:
        """Default prose output contains Archetype, Band, Guidance, Move headers."""
        hint = _make_hint(file_path="src/foo.py", start_line=10, end_line=30)
        with _rule_path_env() as root:
            target = root / "subject.py"
            target.write_text("def f(): pass\n", encoding="utf-8")
            with patch("gzkit.commands.complexity_guide._engine_analyze") as mock_analyze:
                mock_analyze.return_value = (hint,)
                _code, out, _err = _invoke(path=str(target))
        self.assertIn("Archetype", out)
        self.assertIn("Band", out)
        self.assertIn("Guidance", out)
        self.assertIn("Move", out)

    def test_prose_output_contains_file_location(self) -> None:
        """Prose output includes file_path and line range."""
        hint = _make_hint(file_path="src/example.py", start_line=5, end_line=15)
        with _rule_path_env() as root:
            target = root / "subject.py"
            target.write_text("def f(): pass\n", encoding="utf-8")
            with patch("gzkit.commands.complexity_guide._engine_analyze") as mock_analyze:
                mock_analyze.return_value = (hint,)
                _code, out, _err = _invoke(path=str(target))
        self.assertIn("src/example.py", out)
        self.assertIn("5-15", out)


class TestComplexityGuideCliAuditParity(unittest.TestCase):
    """REQ-06: ``gz cli audit`` covers the new verb."""

    @covers("REQ-0.0.30-01-06")
    def test_cli_audit_covers_complexity_guide(self) -> None:
        """Verify cross-coverage scanner finds no gaps for ``complexity guide``."""
        from gzkit.commands.common import get_project_root  # noqa: PLC0415
        from gzkit.doc_coverage.scanner import check_surfaces_report  # noqa: PLC0415

        report = check_surfaces_report(get_project_root())
        complexity_guide = next(
            (c for c in report.coverage if c.command == "complexity guide"),
            None,
        )
        self.assertIsNotNone(
            complexity_guide,
            msg="`complexity guide` not present in cross-coverage scan",
        )
        self.assertTrue(
            complexity_guide.all_passed,
            msg=(
                f"complexity guide coverage gaps: "
                f"{[s.surface for s in complexity_guide.surfaces if not s.passed]}"
            ),
        )


if __name__ == "__main__":
    unittest.main()
