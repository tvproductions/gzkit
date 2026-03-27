"""Tests for the gzkit.doc_coverage package.

Covers AST discovery, surface verification, orphan detection, models,
manifest loading, runner gap detection, and end-to-end integration.
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import TypeVar

from pydantic import ValidationError

from gzkit.doc_coverage.manifest import (
    CommandEntry,
    DocCoverageManifest,
    SurfaceRequirements,
    find_undeclared_commands,
    load_manifest,
)
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

_T = TypeVar("_T")


def covers(target: str):  # noqa: D401 — traceability decorator, not a docstring
    """Traceability decorator linking test classes/functions to ADR/OBPI/REQ targets."""

    def _identity(obj: _T) -> _T:
        return obj

    return _identity


# ---------------------------------------------------------------------------
# 1. AST Discovery Tests
# ---------------------------------------------------------------------------


@covers("ADR-0.0.6-documentation-cross-coverage-enforcement")
@covers("OBPI-0.0.6-01-ast-scanner")
@covers("REQ-0.0.6-01-01")
@covers("REQ-0.0.6-01-02")
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
        self.assertGreaterEqual(
            len(self.commands),
            50,
            f"Discovered only {len(self.commands)} commands — expected at least 50",
        )


# ---------------------------------------------------------------------------
# 2. Surface Verification Tests (synthetic fixtures)
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.6-01-ast-scanner")
@covers("REQ-0.0.6-01-03")
@covers("REQ-0.0.6-01-04")
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


@covers("OBPI-0.0.6-01-ast-scanner")
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


# ---------------------------------------------------------------------------
# 6. Manifest Model Tests
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.6-02-documentation-manifest")
@covers("REQ-0.0.6-02-01")
@covers("REQ-0.0.6-02-02")
class TestManifestModels(unittest.TestCase):
    """Test Pydantic models for the documentation coverage manifest."""

    def _make_surfaces(self, **overrides: bool) -> SurfaceRequirements:
        defaults = {
            "manpage": True,
            "index_entry": True,
            "operator_runbook": True,
            "governance_runbook": False,
            "docstring": True,
            "command_docs_mapping": True,
        }
        defaults.update(overrides)
        return SurfaceRequirements(**defaults)

    def _make_entry(self, governance_relevant: bool = False) -> CommandEntry:
        return CommandEntry(
            surfaces=self._make_surfaces(governance_runbook=governance_relevant),
            governance_relevant=governance_relevant,
        )

    def test_surface_requirements_frozen(self) -> None:
        surfaces = self._make_surfaces()
        with self.assertRaises((TypeError, ValidationError)):
            surfaces.manpage = False  # type: ignore[misc]

    def test_surface_requirements_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            SurfaceRequirements(
                manpage=True,
                index_entry=True,
                operator_runbook=True,
                governance_runbook=False,
                docstring=True,
                command_docs_mapping=True,
                extra_field=True,  # type: ignore[call-arg]
            )

    def test_command_entry_frozen(self) -> None:
        entry = self._make_entry()
        with self.assertRaises((TypeError, ValidationError)):
            entry.governance_relevant = True  # type: ignore[misc]

    def test_command_entry_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            CommandEntry(
                surfaces=self._make_surfaces(),
                governance_relevant=False,
                unknown=True,  # type: ignore[call-arg]
            )

    def test_manifest_frozen(self) -> None:
        manifest = DocCoverageManifest(
            version="1.0.0",
            description="Test",
            commands={"init": self._make_entry()},
        )
        with self.assertRaises((TypeError, ValidationError)):
            manifest.version = "2.0.0"  # type: ignore[misc]

    def test_manifest_extra_forbid(self) -> None:
        with self.assertRaises(ValidationError):
            DocCoverageManifest(
                version="1.0.0",
                description="Test",
                commands={"init": self._make_entry()},
                extra_field="forbidden",  # type: ignore[call-arg]
            )

    def test_governance_relevant_entry(self) -> None:
        entry = self._make_entry(governance_relevant=True)
        self.assertTrue(entry.governance_relevant)
        self.assertTrue(entry.surfaces.governance_runbook)

    def test_non_governance_entry(self) -> None:
        entry = self._make_entry(governance_relevant=False)
        self.assertFalse(entry.governance_relevant)
        self.assertFalse(entry.surfaces.governance_runbook)


# ---------------------------------------------------------------------------
# 7. Manifest Loader Tests
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.6-02-documentation-manifest")
@covers("REQ-0.0.6-02-03")
class TestLoadManifest(unittest.TestCase):
    """Test manifest loading from JSON files."""

    def _write_manifest(self, root: Path, data: dict) -> None:
        config_dir = root / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        (config_dir / "doc-coverage.json").write_text(json.dumps(data), encoding="utf-8")

    def _valid_manifest_data(self) -> dict:
        return {
            "version": "1.0.0",
            "description": "Test manifest",
            "commands": {
                "init": {
                    "surfaces": {
                        "manpage": True,
                        "index_entry": True,
                        "operator_runbook": True,
                        "governance_runbook": True,
                        "docstring": True,
                        "command_docs_mapping": True,
                    },
                    "governance_relevant": True,
                },
                "lint": {
                    "surfaces": {
                        "manpage": True,
                        "index_entry": True,
                        "operator_runbook": True,
                        "governance_runbook": False,
                        "docstring": True,
                        "command_docs_mapping": True,
                    },
                    "governance_relevant": False,
                },
            },
        }

    def test_load_valid_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root, self._valid_manifest_data())
            manifest = load_manifest(root)
            self.assertIsInstance(manifest, DocCoverageManifest)
            self.assertEqual(manifest.version, "1.0.0")
            self.assertEqual(len(manifest.commands), 2)
            self.assertIn("init", manifest.commands)
            self.assertIn("lint", manifest.commands)

    def test_load_manifest_governance_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root, self._valid_manifest_data())
            manifest = load_manifest(root)
            self.assertTrue(manifest.commands["init"].governance_relevant)
            self.assertFalse(manifest.commands["lint"].governance_relevant)

    def test_load_manifest_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaises(FileNotFoundError):
                load_manifest(root)

    def test_load_manifest_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "config"
            config_dir.mkdir(parents=True)
            (config_dir / "doc-coverage.json").write_text("not valid json", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                load_manifest(root)

    def test_load_manifest_missing_required_surface(self) -> None:
        data = self._valid_manifest_data()
        del data["commands"]["init"]["surfaces"]["docstring"]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root, data)
            with self.assertRaises(ValidationError):
                load_manifest(root)

    def test_load_manifest_extra_field_rejected(self) -> None:
        data = self._valid_manifest_data()
        data["commands"]["init"]["extra"] = True
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root, data)
            with self.assertRaises(ValidationError):
                load_manifest(root)


# ---------------------------------------------------------------------------
# 8. Undeclared Command Detection Tests
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.6-02-documentation-manifest")
@covers("REQ-0.0.6-02-04")
class TestFindUndeclaredCommands(unittest.TestCase):
    """Test detection of commands missing from the manifest."""

    def _make_manifest(self, command_names: list[str]) -> DocCoverageManifest:
        commands = {}
        for name in command_names:
            commands[name] = CommandEntry(
                surfaces=SurfaceRequirements(
                    manpage=True,
                    index_entry=True,
                    operator_runbook=True,
                    governance_runbook=False,
                    docstring=True,
                    command_docs_mapping=True,
                ),
                governance_relevant=False,
            )
        return DocCoverageManifest(
            version="1.0.0",
            description="Test",
            commands=commands,
        )

    def test_no_undeclared_when_all_present(self) -> None:
        manifest = self._make_manifest(["init", "lint", "test"])
        undeclared = find_undeclared_commands(manifest, {"init", "lint", "test"})
        self.assertEqual(undeclared, [])

    def test_undeclared_commands_detected(self) -> None:
        manifest = self._make_manifest(["init"])
        undeclared = find_undeclared_commands(manifest, {"init", "lint", "format"})
        self.assertEqual(undeclared, ["format", "lint"])

    def test_undeclared_returns_sorted(self) -> None:
        manifest = self._make_manifest([])
        undeclared = find_undeclared_commands(manifest, {"z-cmd", "a-cmd", "m-cmd"})
        self.assertEqual(undeclared, ["a-cmd", "m-cmd", "z-cmd"])

    def test_manifest_extras_ignored(self) -> None:
        manifest = self._make_manifest(["init", "lint", "extra"])
        undeclared = find_undeclared_commands(manifest, {"init", "lint"})
        self.assertEqual(undeclared, [])


# ---------------------------------------------------------------------------
# 9. Manifest Integration Tests
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.6-02-documentation-manifest")
class TestManifestIntegration(unittest.TestCase):
    """Test the real manifest against the real project."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parent.parent

    def test_real_manifest_loads(self) -> None:
        manifest = load_manifest(self.project_root)
        self.assertIsInstance(manifest, DocCoverageManifest)
        self.assertGreater(len(manifest.commands), 0)

    def test_real_manifest_covers_all_discovered_commands(self) -> None:
        manifest = load_manifest(self.project_root)
        discovered = scan_cli_commands(self.project_root)
        discovered_names = {c.name for c in discovered}
        undeclared = find_undeclared_commands(manifest, discovered_names)
        self.assertEqual(
            undeclared,
            [],
            f"Commands discovered by AST but missing from manifest: {undeclared}",
        )

    def test_real_manifest_governance_flag_matches_runbook_surface(self) -> None:
        manifest = load_manifest(self.project_root)
        for name, entry in manifest.commands.items():
            if entry.governance_relevant:
                self.assertTrue(
                    entry.surfaces.governance_runbook,
                    f"'{name}' is governance_relevant but governance_runbook is False",
                )

    def test_real_manifest_validates_against_schema(self) -> None:
        schema_path = self.project_root / "data" / "schemas" / "doc_coverage_manifest.schema.json"
        self.assertTrue(schema_path.exists(), "Schema file must exist")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "Documentation Coverage Manifest")
        self.assertIn("commands", schema["properties"])


# ---------------------------------------------------------------------------
# 10. Gap Report Model Tests
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.6-03-chore-registration-and-enforcement")
@covers("REQ-0.0.6-03-01")
@covers("REQ-0.0.6-03-02")
class TestGapReportModels(unittest.TestCase):
    """Test Pydantic models for the gap report."""

    def test_gap_item_frozen(self) -> None:
        from gzkit.doc_coverage.models import GapItem

        gap = GapItem(command="lint", surface="manpage", detail="Missing lint.md")
        with self.assertRaises((TypeError, ValidationError)):
            gap.command = "format"  # type: ignore[misc]

    def test_gap_item_extra_forbid(self) -> None:
        from gzkit.doc_coverage.models import GapItem

        with self.assertRaises(ValidationError):
            GapItem(
                command="lint",
                surface="manpage",
                detail="Missing",
                extra="forbidden",  # type: ignore[call-arg]
            )

    def test_orphaned_doc_item_frozen(self) -> None:
        from gzkit.doc_coverage.models import OrphanedDocItem

        item = OrphanedDocItem(surface="manpage", reference="ghost.md", detail="No match")
        with self.assertRaises((TypeError, ValidationError)):
            item.surface = "index"  # type: ignore[misc]

    def test_gap_report_frozen(self) -> None:
        from gzkit.doc_coverage.models import DocCoverageGapReport

        report = DocCoverageGapReport(
            passed=True,
            commands_discovered=1,
            commands_checked=1,
            commands_with_gaps=0,
            gaps=[],
            undeclared_commands=[],
            orphaned_docs=[],
        )
        with self.assertRaises((TypeError, ValidationError)):
            report.passed = False  # type: ignore[misc]

    def test_gap_report_extra_forbid(self) -> None:
        from gzkit.doc_coverage.models import DocCoverageGapReport

        with self.assertRaises(ValidationError):
            DocCoverageGapReport(
                passed=True,
                commands_discovered=1,
                commands_checked=1,
                commands_with_gaps=0,
                gaps=[],
                undeclared_commands=[],
                orphaned_docs=[],
                extra="forbidden",  # type: ignore[call-arg]
            )

    def test_gap_report_serializes_to_json(self) -> None:
        from gzkit.doc_coverage.models import DocCoverageGapReport, GapItem

        gap = GapItem(command="lint", surface="manpage", detail="Missing lint.md")
        report = DocCoverageGapReport(
            passed=False,
            commands_discovered=52,
            commands_checked=52,
            commands_with_gaps=1,
            gaps=[gap],
            undeclared_commands=[],
            orphaned_docs=[],
        )
        data = report.model_dump()
        self.assertFalse(data["passed"])
        self.assertEqual(len(data["gaps"]), 1)
        self.assertEqual(data["gaps"][0]["command"], "lint")


# ---------------------------------------------------------------------------
# 11. Runner Integration Tests
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.6-03-chore-registration-and-enforcement")
@covers("REQ-0.0.6-03-03")
class TestBuildGapReport(unittest.TestCase):
    """Test the runner gap report against the real project."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parent.parent

    def test_build_gap_report_returns_valid_report(self) -> None:
        from gzkit.doc_coverage.runner import build_gap_report

        report = build_gap_report(self.project_root)
        from gzkit.doc_coverage.models import DocCoverageGapReport

        self.assertIsInstance(report, DocCoverageGapReport)
        self.assertGreater(report.commands_discovered, 0)
        self.assertGreater(report.commands_checked, 0)

    def test_build_gap_report_no_undeclared_commands(self) -> None:
        from gzkit.doc_coverage.runner import build_gap_report

        report = build_gap_report(self.project_root)
        self.assertEqual(
            report.undeclared_commands,
            [],
            f"Undeclared commands: {report.undeclared_commands}",
        )

    def test_gap_report_json_conforms_to_schema(self) -> None:
        from gzkit.doc_coverage.runner import build_gap_report

        report = build_gap_report(self.project_root)
        data = report.model_dump()
        schema_path = self.project_root / "data" / "schemas" / "doc-coverage-report.schema.json"
        self.assertTrue(schema_path.exists(), "Gap report schema must exist")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        # Verify top-level required keys match schema
        for key in schema["required"]:
            self.assertIn(key, data, f"Missing required key: {key}")
        # Verify no extra keys
        for key in data:
            self.assertIn(key, schema["properties"], f"Unexpected key: {key}")


@covers("OBPI-0.0.6-03-chore-registration-and-enforcement")
class TestRunDocCoverage(unittest.TestCase):
    """Test the run_doc_coverage entry point."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parent.parent

    def test_run_returns_int(self) -> None:
        from gzkit.doc_coverage.runner import run_doc_coverage

        result = run_doc_coverage(self.project_root, json_output=False)
        self.assertIsInstance(result, int)
        self.assertIn(result, (0, 1))

    def test_run_json_mode_returns_int(self) -> None:
        from gzkit.doc_coverage.runner import run_doc_coverage

        result = run_doc_coverage(self.project_root, json_output=True)
        self.assertIsInstance(result, int)
        self.assertIn(result, (0, 1))


# ---------------------------------------------------------------------------
# 12. Chore Registration Test
# ---------------------------------------------------------------------------


@covers("OBPI-0.0.6-03-chore-registration-and-enforcement")
@covers("REQ-0.0.6-03-04")
class TestChoreRegistration(unittest.TestCase):
    """Verify the doc-coverage chore is properly registered."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parent.parent

    def test_doc_coverage_in_chore_registry(self) -> None:
        registry_path = self.project_root / "config" / "gzkit.chores.json"
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        slugs = [c["slug"] for c in data["chores"]]
        self.assertIn("doc-coverage", slugs, "doc-coverage chore must be registered")

    def test_doc_coverage_chore_frequency(self) -> None:
        registry_path = self.project_root / "config" / "gzkit.chores.json"
        data = json.loads(registry_path.read_text(encoding="utf-8"))
        entry = next(c for c in data["chores"] if c["slug"] == "doc-coverage")
        self.assertEqual(entry.get("frequency"), "per-release")

    def test_doc_coverage_chore_dir_exists(self) -> None:
        chore_dir = self.project_root / "ops" / "chores" / "doc-coverage"
        self.assertTrue(chore_dir.is_dir(), "Chore directory must exist")
        self.assertTrue((chore_dir / "CHORE.md").exists(), "CHORE.md must exist")
        self.assertTrue((chore_dir / "acceptance.json").exists(), "acceptance.json must exist")
        self.assertTrue((chore_dir / "README.md").exists(), "README.md must exist")

    def test_doc_coverage_schema_exists(self) -> None:
        schema_path = self.project_root / "data" / "schemas" / "doc-coverage-report.schema.json"
        self.assertTrue(schema_path.exists(), "Gap report schema must exist")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema["title"], "Documentation Coverage Gap Report")


if __name__ == "__main__":
    unittest.main()
