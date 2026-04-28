"""Tests for CLI audit command with cross-coverage integration."""

import json
import textwrap
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli.main import main
from tests.commands.common import CliRunner


class TestCliAuditCrossCoverage(unittest.TestCase):
    """Verify cross-coverage data appears in cli audit output."""

    _json_data: dict
    _human_output: str

    @classmethod
    def setUpClass(cls) -> None:
        # ``gz cli audit`` runs the full cross-coverage scanner every time
        # and is ~1.5s per invocation. Share the expensive scanner call
        # across both JSON and human renderings so setUp pays the scan
        # once instead of twice (GHI #253).
        runner = CliRunner()
        from gzkit.doc_coverage.scanner import check_surfaces_report  # noqa: PLC0415

        original = check_surfaces_report

        cached_report: dict[str, object] = {}

        def _cached_scanner(project_root, *args, **kwargs):
            if "report" not in cached_report:
                cached_report["report"] = original(project_root, *args, **kwargs)
            return cached_report["report"]

        with patch(
            "gzkit.doc_coverage.scanner.check_surfaces_report",
            side_effect=_cached_scanner,
        ):
            json_result = runner.invoke(main, ["cli", "audit", "--json"])
            cls._json_data = json.loads(json_result.output)
            human_result = runner.invoke(main, ["cli", "audit"])
            cls._human_output = human_result.output

    def test_cli_audit_json_includes_cross_coverage(self) -> None:
        """JSON output must include a cross_coverage key with CoverageReport shape."""
        data = self._json_data
        self.assertIn("cross_coverage", data)
        cc = data["cross_coverage"]
        self.assertIn("commands_discovered", cc)
        self.assertIn("commands_fully_covered", cc)
        self.assertIn("commands_with_gaps", cc)
        self.assertIn("coverage", cc)
        self.assertIn("orphaned", cc)
        self.assertIn("passed", cc)
        self.assertGreater(cc["commands_discovered"], 0)

    def test_cli_audit_json_coverage_list_structure(self) -> None:
        """Each entry in cross_coverage.coverage must have expected fields."""
        cc = self._json_data["cross_coverage"]
        self.assertIsInstance(cc["coverage"], list)
        # At least one command should be present in the real project
        self.assertGreater(len(cc["coverage"]), 0)
        first = cc["coverage"][0]
        self.assertIn("command", first)
        self.assertIn("surfaces", first)
        self.assertIn("all_passed", first)
        self.assertIsInstance(first["surfaces"], list)
        self.assertGreater(len(first["surfaces"]), 0)
        surface = first["surfaces"][0]
        self.assertIn("surface", surface)
        self.assertIn("passed", surface)
        self.assertIn("detail", surface)

    def test_cli_audit_json_counts_consistent(self) -> None:
        """commands_fully_covered + commands_with_gaps must equal commands_discovered."""
        cc = self._json_data["cross_coverage"]
        self.assertEqual(
            cc["commands_fully_covered"] + cc["commands_with_gaps"],
            cc["commands_discovered"],
        )

    def test_cli_audit_human_shows_cross_coverage(self) -> None:
        """Human-readable output must include a Cross-coverage: section."""
        self.assertIn("Cross-coverage:", self._human_output)

    def test_cli_audit_json_result_has_valid_key(self) -> None:
        """JSON output must retain the existing 'valid' and 'issues' keys alongside cross_coverage.

        Ensures backward-compatible output contract is preserved.
        """
        data = self._json_data
        self.assertIn("valid", data)
        self.assertIn("issues", data)
        self.assertIn("cross_coverage", data)
        self.assertIsInstance(data["valid"], bool)
        self.assertIsInstance(data["issues"], list)


class TestPerFlagDocCoverage(unittest.TestCase):
    """Per-flag doc coverage: every registered argparse long flag must be documented (GHI #350)."""

    def test_discover_command_flags_extracts_long_flags_per_subcommand(self) -> None:
        """discover_command_flags returns {command: [flag, ...]} from add_argument calls."""
        from gzkit.doc_coverage.flag_scanner import discover_command_flags  # noqa: PLC0415

        source = textwrap.dedent(
            """
            def _build_parser():
                parser = StableArgumentParser()
                sub = parser.add_subparsers()
                p_validate = sub.add_parser("validate")
                p_validate.add_argument("--documents", action="store_true")
                p_validate.add_argument("--chores-layout", action="store_true")
                p_validate.set_defaults(func=lambda a: validate())
            """
        )
        flags = discover_command_flags(source)
        self.assertIn("validate", flags)
        self.assertIn("--documents", flags["validate"])
        self.assertIn("--chores-layout", flags["validate"])

    def test_discover_command_flags_handles_short_and_long_pair(self) -> None:
        """When add_argument has both -x and --xxx, only the long form is captured."""
        from gzkit.doc_coverage.flag_scanner import discover_command_flags  # noqa: PLC0415

        source = textwrap.dedent(
            """
            def _build_parser():
                parser = StableArgumentParser()
                sub = parser.add_subparsers()
                p_status = sub.add_parser("status")
                p_status.add_argument("-q", "--quiet", action="store_true")
                p_status.set_defaults(func=lambda a: status())
            """
        )
        flags = discover_command_flags(source)
        self.assertEqual(flags["status"], ["--quiet"])

    def test_check_flag_doc_coverage_flags_undocumented_flag(self) -> None:
        """check_flag_doc_coverage emits an issue when a flag has no doc mention (GHI #350).

        Closes the class of failure: a flag added to an existing command without
        any mention in the per-command doc previously survived every mechanical
        check (cli_audit reported 87/87 clean during the chores-layout gap).
        """
        import tempfile  # noqa: PLC0415

        from gzkit.doc_coverage.flag_scanner import check_flag_doc_coverage  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            commands_dir = Path(tmp)
            (commands_dir / "validate.md").write_text(
                "# gz validate\n\n## Examples\n\n### `--documents`\n\nDoc for documents.\n",
                encoding="utf-8",
            )
            flags_by_command = {"validate": ["--documents", "--undocumented-flag"]}
            issues = check_flag_doc_coverage(commands_dir, flags_by_command, waivers={})
            issue_text = " ".join(item["issue"] for item in issues)
            paths = {item["path"] for item in issues}
            self.assertEqual(len(issues), 1)
            self.assertIn("docs/user/commands/validate.md", paths)
            self.assertIn("--undocumented-flag", issue_text)
            self.assertNotIn("--documents", issue_text)

    def test_per_flag_doc_waivers_match_real_project_drift(self) -> None:
        """Real-project per-flag drift must exactly equal the waiver snapshot (GHI #350).

        New flags added without docs => a fresh issue not in the waiver => fail.
        Stale waivers (flag waived but doc now exists, or flag removed from
        argparse) => over-waiver => fail.

        Drained when the GHI #353 doc-backlog work moves a waiver entry into
        an actual doc section.
        """
        from gzkit.commands.common import get_project_root  # noqa: PLC0415
        from gzkit.doc_coverage.flag_scanner import (  # noqa: PLC0415
            _PER_FLAG_DOC_WAIVERS,
            check_flag_doc_coverage,
            scan_command_flags,
        )

        project_root = get_project_root()
        flags_by_command = scan_command_flags(project_root)
        commands_dir = project_root / "docs" / "user" / "commands"

        # 1. Audit with the live waiver: must surface zero drift.
        issues = check_flag_doc_coverage(commands_dir, flags_by_command)
        self.assertEqual(issues, [], f"New per-flag doc gaps surfaced: {issues}")

        # 2. Audit with empty waivers: every waivered flag must still be a real
        # gap in the live docs. A waiver entry whose flag is now documented
        # (or whose flag has been removed from argparse) is stale.
        no_waiver_issues = check_flag_doc_coverage(commands_dir, flags_by_command, waivers={})
        actual_gaps: dict[str, set[str]] = {}
        for issue in no_waiver_issues:
            slug = issue["path"].rsplit("/", 1)[-1].removesuffix(".md")
            command_name = slug.replace("-", " ", 1) if " " not in slug else slug
            flag = issue["issue"].split("`")[1]
            actual_gaps.setdefault(slug, set()).add(flag)

        for command_name, waived_flags in _PER_FLAG_DOC_WAIVERS.items():
            slug = command_name.replace(" ", "-")
            actual_for_command = actual_gaps.get(slug, set())
            stale = waived_flags - actual_for_command
            self.assertFalse(
                stale,
                f"Stale waivers for {command_name}: {sorted(stale)} — flags are now "
                f"documented (or removed); drop them from _PER_FLAG_DOC_WAIVERS.",
            )
