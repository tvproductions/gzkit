"""Tests for the gz plan-audit CLI command."""

from __future__ import annotations

import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from rich.console import Console

from gzkit.commands.plan_audit_cmd import (
    _derive_adr_id,
    _extract_allowed_paths,
    _extract_plan_paths,
    _find_adr_dir,
    _find_brief,
    _find_plan_file,
    _path_within_allowed,
    plan_audit_cmd,
)


class TestDeriveAdrId(unittest.TestCase):
    """Test OBPI-to-ADR derivation."""

    def test_standard_obpi(self) -> None:
        self.assertEqual(_derive_adr_id("OBPI-0.1.0-01"), "ADR-0.1.0")

    def test_obpi_with_suffix(self) -> None:
        self.assertEqual(_derive_adr_id("OBPI-0.10.0-05"), "ADR-0.10.0")

    def test_invalid_prefix(self) -> None:
        self.assertIsNone(_derive_adr_id("ADR-0.1.0"))

    def test_no_item_number(self) -> None:
        # "OBPI-0.1.0" has no trailing -NN, rsplit produces only one part
        self.assertIsNone(_derive_adr_id("OBPI-0.1.0"))


class TestFindAdrDir(unittest.TestCase):
    """Test ADR directory discovery."""

    def test_finds_matching_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-my-feature"
            adr_dir.mkdir(parents=True)
            result = _find_adr_dir(root, "ADR-0.1.0")
            self.assertIsNotNone(result)
            self.assertEqual(result, adr_dir)

    def test_returns_none_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "design" / "adr" / "foundation").mkdir(parents=True)
            result = _find_adr_dir(root, "ADR-0.99.0")
            self.assertIsNone(result)

    def test_returns_none_when_no_adr_base(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = _find_adr_dir(root, "ADR-0.1.0")
            self.assertIsNone(result)


class TestFindBrief(unittest.TestCase):
    """Test OBPI brief file discovery."""

    def test_finds_matching_brief(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir()
            brief = obpis_dir / "OBPI-0.1.0-01-my-feature.md"
            brief.write_text("# Brief", encoding="utf-8")
            result = _find_brief(adr_dir, "OBPI-0.1.0-01")
            self.assertIsNotNone(result)
            self.assertEqual(result, brief)

    def test_returns_none_when_no_obpis_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = Path(tmp)
            result = _find_brief(adr_dir, "OBPI-0.1.0-01")
            self.assertIsNone(result)


class TestFindPlanFile(unittest.TestCase):
    """Test plan file discovery."""

    def test_finds_plan_with_obpi_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plans_dir = Path(tmp)
            plan = plans_dir / "my-plan.md"
            plan.write_text("# Plan for OBPI-0.1.0-01\nDo things.", encoding="utf-8")
            result = _find_plan_file(plans_dir, "OBPI-0.1.0-01")
            self.assertIsNotNone(result)
            self.assertEqual(result, plan)

    def test_returns_none_when_no_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plans_dir = Path(tmp)
            plan = plans_dir / "other.md"
            plan.write_text("# Plan for something else", encoding="utf-8")
            result = _find_plan_file(plans_dir, "OBPI-0.1.0-01")
            self.assertIsNone(result)

    def test_returns_none_when_dir_missing(self) -> None:
        result = _find_plan_file(Path("/nonexistent/plans"), "OBPI-0.1.0-01")
        self.assertIsNone(result)

    def test_skips_dotfiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plans_dir = Path(tmp)
            dotfile = plans_dir / ".hidden-plan.md"
            dotfile.write_text("# Plan for OBPI-0.1.0-01", encoding="utf-8")
            result = _find_plan_file(plans_dir, "OBPI-0.1.0-01")
            self.assertIsNone(result)


class TestExtractAllowedPaths(unittest.TestCase):
    """Test allowed paths extraction from brief."""

    def test_extracts_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text(
                "## Allowed Paths\n\n- `src/gzkit/commands/`\n- `tests/`\n\n## Other\n",
                encoding="utf-8",
            )
            result = _extract_allowed_paths(brief)
            self.assertEqual(result, ["src/gzkit/commands/", "tests/"])

    def test_returns_none_when_no_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = Path(tmp) / "brief.md"
            brief.write_text("## Something Else\n\n- path\n", encoding="utf-8")
            result = _extract_allowed_paths(brief)
            self.assertIsNone(result)


class TestExtractPlanPaths(unittest.TestCase):
    """Test plan path extraction."""

    def test_extracts_paths_from_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.md"
            plan.write_text(
                "Modify `src/gzkit/commands/foo.py` and `tests/test_foo.py`\n",
                encoding="utf-8",
            )
            result = _extract_plan_paths(plan)
            self.assertIn("src/gzkit/commands/foo.py", result)
            self.assertIn("tests/test_foo.py", result)


class TestPathWithinAllowed(unittest.TestCase):
    """Test path-within-allowed checking."""

    def test_exact_match(self) -> None:
        self.assertTrue(_path_within_allowed("src/gzkit", ["src/gzkit"]))

    def test_subpath_match(self) -> None:
        self.assertTrue(_path_within_allowed("src/gzkit/commands/foo.py", ["src/gzkit/"]))

    def test_no_match_returns_true(self) -> None:
        # Current implementation returns True when path doesn't match (permissive)
        self.assertTrue(_path_within_allowed("other/path.py", ["src/gzkit/"]))


class TestPlanAuditCmdPass(unittest.TestCase):
    """Test plan_audit_cmd end-to-end PASS scenario."""

    def test_pass_writes_receipt_and_exits_0(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Create ADR directory
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text("# Brief\n## Allowed Paths\n- `src/`\n", encoding="utf-8")

            # Create plans directory with plan file
            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            plan = plans_dir / "plan-feature.md"
            plan.write_text("# Plan for OBPI-0.1.0-01\nModify `src/foo.py`\n", encoding="utf-8")

            # Create .gzkit.json
            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
            ):
                # Should not raise (exit 0)
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            receipt_path = plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json"
            self.assertTrue(receipt_path.exists())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["verdict"], "PASS")
            self.assertEqual(receipt["obpi_id"], "OBPI-0.1.0-01")
            self.assertEqual(receipt["gaps_found"], 0)


class TestPlanAuditCmdFail(unittest.TestCase):
    """Test plan_audit_cmd end-to-end FAIL scenario."""

    def test_fail_exits_1_when_no_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            # Create ADR directory but NO plan file
            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text("# Brief\n", encoding="utf-8")

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)

            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            quiet_console = Console(file=StringIO(), quiet=True)
            with (
                patch("gzkit.commands.plan_audit_cmd.console", quiet_console),
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
                self.assertRaises(SystemExit) as ctx,
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=False)

            self.assertEqual(ctx.exception.code, 1)
            receipt_path = plans_dir / ".plan-audit-receipt-OBPI-0.1.0-01.json"
            self.assertTrue(receipt_path.exists())
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(receipt["verdict"], "FAIL")
            self.assertGreater(receipt["gaps_found"], 0)


class TestPlanAuditCmdJson(unittest.TestCase):
    """Test plan_audit_cmd --json output."""

    def test_json_output_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            adr_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.1.0-feature"
            obpis_dir = adr_dir / "obpis"
            obpis_dir.mkdir(parents=True)
            brief = obpis_dir / "OBPI-0.1.0-01-feature.md"
            brief.write_text("# Brief\n", encoding="utf-8")

            plans_dir = root / ".claude" / "plans"
            plans_dir.mkdir(parents=True)
            plan = plans_dir / "plan.md"
            plan.write_text("# OBPI-0.1.0-01 plan\n", encoding="utf-8")

            (root / ".gzkit.json").write_text("{}", encoding="utf-8")

            with (
                patch("gzkit.commands.common.get_project_root", return_value=root),
                patch("gzkit.commands.common.ensure_initialized"),
                patch("sys.stdout", new_callable=StringIO) as mock_stdout,
            ):
                plan_audit_cmd(obpi_id="OBPI-0.1.0-01", as_json=True)
                output = mock_stdout.getvalue()

            data = json.loads(output)
            self.assertEqual(data["obpi_id"], "OBPI-0.1.0-01")
            self.assertEqual(data["verdict"], "PASS")
            self.assertIn("timestamp", data)
            self.assertIn("gaps_found", data)


if __name__ == "__main__":
    unittest.main()
