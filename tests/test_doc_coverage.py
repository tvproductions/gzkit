"""Tests for the gzkit.doc_coverage package.

Covers AST discovery, surface verification, orphan detection, models,
and end-to-end integration.
"""

import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.doc_coverage.models import (
    CommandCoverage,
    CoverageReport,
    OrphanedDoc,
    SurfaceResult,
)
from gzkit.doc_coverage.scanner import (
    DiscoveredCommand,
    check_surfaces,
    check_surfaces_report,
    discover_commands,
    find_orphaned_docs,
    scan_cli_commands,
)

# ---------------------------------------------------------------------------
# 1. AST Discovery Tests
# ---------------------------------------------------------------------------


class TestDiscoverCommands(unittest.TestCase):
    """Test AST-based command discovery against the real cli/main.py."""

    @classmethod
    def setUpClass(cls) -> None:
        main_path = Path(__file__).resolve().parent.parent / "src" / "gzkit" / "cli" / "main.py"
        cls.source = main_path.read_text(encoding="utf-8")
        cls.commands = discover_commands(cls.source)
        cls.command_names = {c.name for c in cls.commands}

    def test_discovers_top_level_commands(self) -> None:
        expected = {
            "init",
            "prd",
            "plan",
            "status",
            "closeout",
            "audit",
            "validate",
            "tidy",
            "interview",
            "roles",
            "implement",
            "gates",
            "attest",
            "git-sync",
            "migrate-semver",
            "register-adrs",
            "check-config-paths",
        }
        for cmd in expected:
            self.assertIn(cmd, self.command_names, f"Expected top-level command '{cmd}' not found")

    def test_discovers_nested_two_level_commands(self) -> None:
        expected = {
            "adr status",
            "adr report",
            "adr promote",
            "adr evaluate",
            "adr audit-check",
            "adr covers-check",
            "adr emit-receipt",
            "obpi emit-receipt",
            "obpi status",
            "obpi pipeline",
            "obpi reconcile",
            "obpi validate",
            "cli audit",
            "parity check",
            "readiness audit",
            "readiness evaluate",
            "chores list",
            "chores show",
            "chores plan",
            "chores advise",
            "chores run",
            "chores audit",
            "skill new",
            "skill list",
            "skill audit",
        }
        for cmd in expected:
            self.assertIn(cmd, self.command_names, f"Expected two-level command '{cmd}' not found")

    def test_discovers_three_level_command(self) -> None:
        self.assertIn(
            "agent sync control-surfaces",
            self.command_names,
            "Expected three-level command 'agent sync control-surfaces' not found",
        )

    def test_discovers_inline_chained_parsers(self) -> None:
        # These use add_parser(...).set_defaults(...) inline chaining
        expected = {"lint", "format", "test", "typecheck", "check"}
        for cmd in expected:
            self.assertIn(
                cmd,
                self.command_names,
                f"Expected inline-chained command '{cmd}' not found",
            )

    def test_excludes_group_parsers(self) -> None:
        # Group parsers (have add_subparsers called) must not be leaf commands
        groups = {
            "adr",
            "obpi",
            "cli",
            "chores",
            "skill",
            "parity",
            "readiness",
            "agent",
            "agent sync",
        }
        for group in groups:
            self.assertNotIn(
                group, self.command_names, f"Group parser '{group}' must not be a leaf"
            )

    def test_extracts_handler_names(self) -> None:
        handler_map = {c.name: c.handler_name for c in self.commands}

        self.assertEqual(
            handler_map.get("init"),
            "init",
            "Handler for 'init' should be 'init'",
        )
        self.assertEqual(
            handler_map.get("adr status"),
            "adr_status_cmd",
            "Handler for 'adr status' should be 'adr_status_cmd'",
        )
        self.assertEqual(
            handler_map.get("lint"),
            "lint",
            "Handler for 'lint' should be 'lint'",
        )
        self.assertEqual(
            handler_map.get("cli audit"),
            "cli_audit_cmd",
            "Handler for 'cli audit' should be 'cli_audit_cmd'",
        )

    def test_total_command_count(self) -> None:
        self.assertEqual(len(self.commands), 51, f"Expected 51 commands, got {len(self.commands)}")


# ---------------------------------------------------------------------------
# 2. Surface Verification Tests (synthetic fixtures)
# ---------------------------------------------------------------------------


class TestCheckSurfaces(unittest.TestCase):
    """Test each surface check using minimal temp-dir fixtures."""

    def _make_command(self, name: str = "init", handler: str | None = "init") -> DiscoveredCommand:
        return DiscoveredCommand(name=name, handler_name=handler, line=1)

    def _get_surface(self, coverages: list[CommandCoverage], surface_name: str) -> SurfaceResult:
        """Extract a specific surface result from the first command coverage."""
        for cov in coverages:
            for s in cov.surfaces:
                if s.surface == surface_name:
                    return s
        self.fail(f"Surface '{surface_name}' not found in coverage results")

    def test_manpage_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            (root / "docs" / "user" / "commands" / "init.md").write_text(
                "# gz init\n", encoding="utf-8"
            )
            coverages = check_surfaces(root, [self._make_command("init")], "")
            surface = self._get_surface(coverages, "manpage")
            self.assertTrue(surface.passed, "Manpage surface should pass when file exists")

    def test_manpage_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            # No init.md
            coverages = check_surfaces(root, [self._make_command("init")], "")
            surface = self._get_surface(coverages, "manpage")
            self.assertFalse(surface.passed, "Manpage surface should fail when file is missing")

    def test_index_entry_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            (root / "docs" / "user" / "commands" / "index.md").write_text(
                "- [init](init.md)\n", encoding="utf-8"
            )
            coverages = check_surfaces(root, [self._make_command("init")], "")
            surface = self._get_surface(coverages, "index_entry")
            self.assertTrue(surface.passed, "Index entry surface should pass when entry exists")

    def test_index_entry_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            (root / "docs" / "user" / "commands" / "index.md").write_text(
                "- [something-else](something-else.md)\n", encoding="utf-8"
            )
            coverages = check_surfaces(root, [self._make_command("init")], "")
            surface = self._get_surface(coverages, "index_entry")
            self.assertFalse(surface.passed, "Index entry surface should fail when entry is absent")

    def test_operator_runbook_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user").mkdir(parents=True)
            (root / "docs" / "user" / "runbook.md").write_text(
                "Run `gz init` to get started.\n", encoding="utf-8"
            )
            coverages = check_surfaces(root, [self._make_command("init")], "")
            surface = self._get_surface(coverages, "operator_runbook")
            self.assertTrue(
                surface.passed, "Operator runbook surface should pass when command is referenced"
            )

    def test_governance_runbook_reference(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "governance").mkdir(parents=True)
            (root / "docs" / "governance" / "governance_runbook.md").write_text(
                "Use `gz init` to initialize.\n", encoding="utf-8"
            )
            coverages = check_surfaces(root, [self._make_command("init")], "")
            surface = self._get_surface(coverages, "governance_runbook")
            self.assertTrue(
                surface.passed, "Governance runbook surface should pass when command is referenced"
            )

    def test_command_docs_mapping_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # "init" is in COMMAND_DOCS
            coverages = check_surfaces(root, [self._make_command("init")], "")
            surface = self._get_surface(coverages, "command_docs_mapping")
            self.assertTrue(
                surface.passed,
                "Command docs mapping surface should pass when command is in COMMAND_DOCS",
            )

    def test_command_docs_mapping_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # "nonexistent" is not in COMMAND_DOCS
            coverages = check_surfaces(root, [self._make_command("nonexistent")], "")
            surface = self._get_surface(coverages, "command_docs_mapping")
            self.assertFalse(
                surface.passed,
                "Command docs mapping surface should fail when command is absent from COMMAND_DOCS",
            )


# ---------------------------------------------------------------------------
# 3. Orphan Detection Tests
# ---------------------------------------------------------------------------


class TestFindOrphanedDocs(unittest.TestCase):
    """Test orphaned documentation detection."""

    def test_orphaned_manpage_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            # Create a manpage for a command not in the discovered set
            (root / "docs" / "user" / "commands" / "ghost-cmd.md").write_text(
                "# gz ghost-cmd\n", encoding="utf-8"
            )
            # Discovered set does NOT include "ghost cmd"
            orphans = find_orphaned_docs(root, discovered_names={"init", "status"})
            orphan_refs = {o.reference for o in orphans}
            # Should flag the ghost-cmd.md manpage
            self.assertTrue(
                any("ghost-cmd" in ref for ref in orphan_refs),
                f"Expected 'ghost-cmd' orphan in {orphan_refs}",
            )

    def test_no_orphans_when_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            (root / "docs" / "user" / "commands" / "init.md").write_text(
                "# gz init\n", encoding="utf-8"
            )
            # All manpage files correspond to discovered commands
            # Also provide all COMMAND_DOCS keys in discovered_names to avoid COMMAND_DOCS orphans
            from gzkit.commands.common import COMMAND_DOCS

            all_names = set(COMMAND_DOCS.keys()) | {"init"}
            orphans = find_orphaned_docs(root, discovered_names=all_names)
            manpage_orphans = [o for o in orphans if o.surface == "manpage"]
            self.assertEqual(
                manpage_orphans,
                [],
                f"Expected no manpage orphans, got {manpage_orphans}",
            )

    def test_index_excluded_from_orphan_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs" / "user" / "commands").mkdir(parents=True)
            (root / "docs" / "user" / "commands" / "index.md").write_text(
                "# Command Index\n", encoding="utf-8"
            )
            # Discovered set is empty — only index.md is present
            orphans = find_orphaned_docs(root, discovered_names=set())
            manpage_orphans = [o for o in orphans if o.surface == "manpage"]
            self.assertEqual(
                manpage_orphans,
                [],
                "index.md must never be flagged as an orphaned manpage",
            )


# ---------------------------------------------------------------------------
# 4. Model Tests
# ---------------------------------------------------------------------------


class TestModels(unittest.TestCase):
    """Test Pydantic model contracts for doc_coverage models."""

    def _make_surface_result(self, passed: bool = True) -> SurfaceResult:
        return SurfaceResult(surface="manpage", passed=passed, detail="Test detail")

    def _make_command_coverage(self, all_passed: bool = True) -> CommandCoverage:
        return CommandCoverage(
            command="init",
            surfaces=[self._make_surface_result(all_passed)],
            all_passed=all_passed,
        )

    def _make_report(
        self,
        coverage: list[CommandCoverage] | None = None,
        orphaned: list[OrphanedDoc] | None = None,
        passed: bool = True,
    ) -> CoverageReport:
        coverage = coverage or []
        orphaned = orphaned or []
        return CoverageReport(
            commands_discovered=1,
            commands_fully_covered=1 if passed else 0,
            commands_with_gaps=0 if passed else 1,
            coverage=coverage,
            orphaned=orphaned,
            passed=passed,
        )

    def test_coverage_report_frozen(self) -> None:
        report = self._make_report()
        with self.assertRaises((TypeError, ValidationError)):
            report.commands_discovered = 99  # type: ignore[misc]

    def test_coverage_report_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            CoverageReport(
                commands_discovered=1,
                commands_fully_covered=1,
                commands_with_gaps=0,
                coverage=[],
                orphaned=[],
                passed=True,
                unknown_field="forbidden",  # type: ignore[call-arg]
            )

    def test_report_passed_when_fully_covered(self) -> None:
        report = self._make_report(passed=True)
        self.assertTrue(report.passed, "Report should pass when no gaps and no orphans")
        self.assertEqual(report.commands_with_gaps, 0)
        self.assertEqual(len(report.orphaned), 0)

    def test_report_failed_when_gaps_exist(self) -> None:
        gap_coverage = self._make_command_coverage(all_passed=False)
        report = CoverageReport(
            commands_discovered=1,
            commands_fully_covered=0,
            commands_with_gaps=1,
            coverage=[gap_coverage],
            orphaned=[],
            passed=False,
        )
        self.assertFalse(report.passed, "Report should fail when commands have gaps")
        self.assertGreater(report.commands_with_gaps, 0)

    def test_report_failed_when_orphans_exist(self) -> None:
        orphan = OrphanedDoc(
            surface="manpage",
            reference="docs/user/commands/ghost.md",
            detail="No matching command",
        )
        report = CoverageReport(
            commands_discovered=0,
            commands_fully_covered=0,
            commands_with_gaps=0,
            coverage=[],
            orphaned=[orphan],
            passed=False,
        )
        self.assertFalse(report.passed, "Report should fail when orphans exist")
        self.assertEqual(len(report.orphaned), 1)


# ---------------------------------------------------------------------------
# 5. Integration Tests
# ---------------------------------------------------------------------------


class TestIntegration(unittest.TestCase):
    """End-to-end integration tests using the actual project root."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parent.parent

    def test_scan_cli_commands_returns_commands(self) -> None:
        commands = scan_cli_commands(self.project_root)
        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 0, "scan_cli_commands must return at least one command")
        for cmd in commands:
            self.assertIsInstance(cmd, DiscoveredCommand)

    def test_check_surfaces_report_returns_valid_report(self) -> None:
        report = check_surfaces_report(self.project_root)
        self.assertIsInstance(report, CoverageReport)
        self.assertGreater(
            report.commands_discovered,
            0,
            "CoverageReport must discover at least one command",
        )
        self.assertEqual(
            report.commands_discovered,
            report.commands_fully_covered + report.commands_with_gaps,
            "commands_discovered must equal fully_covered + with_gaps",
        )


if __name__ == "__main__":
    unittest.main()
