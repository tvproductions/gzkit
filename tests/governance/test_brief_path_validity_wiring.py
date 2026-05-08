"""Integration tests for GHI #419 wirings.

Proves that ``gz obpi validate`` and ``gz adr promote`` invoke the shared
brief-path-validity primitives and surface drift as command-level errors.
"""

import tempfile
import unittest
from pathlib import Path
from typing import Any

from gzkit.commands.adr_promote import _check_scaffold_obpis
from gzkit.commands.obpi_cmd import _validate_brief_path_existence


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestObpiValidateBriefPathExistence(unittest.TestCase):
    """``gz obpi validate --authored`` invokes path-validity check.

    The check is gated on ``--authored`` so early Draft briefs can iterate
    on placeholder paths without false-failing structural validation;
    authoring-time strictness is the explicit gate that fires path-validity.
    """

    def test_drifted_path_surfaces_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "obpis" / "OBPI-test.md"
            _write(brief, "## Allowed Paths\n\n- `src/drifted.py`\n")
            errors = _validate_brief_path_existence(root, brief)
            self.assertEqual(len(errors), 1)
            self.assertIn("src/drifted.py", errors[0])
            self.assertIn("does not exist", errors[0])

    def test_vendor_mirror_path_surfaces_error(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "obpis" / "OBPI-test.md"
            _write(root / ".claude" / "rules" / "tests.md", "doc\n")
            _write(brief, "## Allowed Paths\n\n- `.claude/rules/tests.md`\n")
            errors = _validate_brief_path_existence(root, brief)
            self.assertEqual(len(errors), 1)
            self.assertIn("vendor mirror", errors[0])

    def test_brief_creates_marker_exempts_net_new_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "obpis" / "OBPI-test.md"
            _write(
                brief,
                "## Allowed Paths\n\n"
                "- `src/net_new.py`\n\n"
                "## Creates these files\n\n"
                "- `src/net_new.py`\n",
            )
            self.assertEqual(_validate_brief_path_existence(root, brief), [])

    def test_fresh_scaffold_without_paths_surfaces_no_errors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "obpis" / "OBPI-test.md"
            _write(brief, "# Title\n\nNo allowed paths section.\n")
            self.assertEqual(_validate_brief_path_existence(root, brief), [])

    def test_existing_path_surfaces_no_errors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            _write(root / "src" / "foo.py", "x = 1\n")
            brief = root / "obpis" / "OBPI-test.md"
            _write(brief, "## Allowed Paths\n\n- `src/foo.py`\n")
            self.assertEqual(_validate_brief_path_existence(root, brief), [])


class TestAdrPromoteCheckScaffoldObpisPathValidity(unittest.TestCase):
    """``gz adr promote`` _check_scaffold_obpis surfaces brief-path drift."""

    def _build_promotion_plan(self, brief_path: Path) -> dict[str, Any]:
        return {"obpi_plans": [{"obpi_file": brief_path}]}

    def test_drifted_brief_path_surfaces_in_structure_errors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "OBPI-test.md"
            _write(
                brief,
                "---\n"
                "id: OBPI-0.1.0-01\n"
                "title: Test brief\n"
                "kind: feature\n"
                "lane: lite\n"
                "status: Authored\n"
                "---\n\n"
                "## Allowed Paths\n\n"
                "- `src/drifted_module.py`\n",
            )
            plan = self._build_promotion_plan(brief)
            scaffold_count, structure_errors = _check_scaffold_obpis(root, plan)
            self.assertTrue(
                any("src/drifted_module.py" in err for err in structure_errors),
                f"Expected drift error in {structure_errors}",
            )

    def test_brief_creates_marker_exempts_net_new_in_promotion(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            brief = root / "OBPI-test.md"
            _write(
                brief,
                "---\n"
                "id: OBPI-0.1.0-01\n"
                "title: Test brief\n"
                "kind: feature\n"
                "lane: lite\n"
                "status: Authored\n"
                "---\n\n"
                "## Allowed Paths\n\n"
                "- `src/net_new_promote.py`\n\n"
                "## Creates these files\n\n"
                "- `src/net_new_promote.py`\n",
            )
            plan = self._build_promotion_plan(brief)
            _scaffold_count, structure_errors = _check_scaffold_obpis(root, plan)
            offenders = [
                err
                for err in structure_errors
                if "net_new_promote" in err and "does not exist" in err
            ]
            self.assertFalse(
                offenders,
                f"Net-new path should be exempt; got {structure_errors}",
            )


if __name__ == "__main__":
    unittest.main()
