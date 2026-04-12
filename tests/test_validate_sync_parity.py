"""Sync parity validation for generated control surfaces (GHI #134)."""

import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.validate_pkg.sync_parity import check_sync_parity
from tests.commands.common import CliRunner


class SyncParityCleanTreeTest(unittest.TestCase):
    """A freshly initialized project has no sync parity drift."""

    def test_clean_init_reports_no_drift(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            errors = check_sync_parity(Path.cwd())
            self.assertEqual(
                [],
                [(e.artifact, e.message) for e in errors],
                f"expected clean parity; got {[(e.artifact, e.message) for e in errors]}",
            )


class SyncParityContentDriftTest(unittest.TestCase):
    """A hand-edited generated surface must surface as drift."""

    def test_hand_edited_agents_md_reports_drift(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            agents_md = Path("AGENTS.md")
            original = agents_md.read_text(encoding="utf-8")
            agents_md.write_text(
                original + "\n\n<!-- hand-edited drift marker -->\n",
                encoding="utf-8",
            )

            errors = check_sync_parity(Path.cwd())
            drift_artifacts = [e.artifact for e in errors]
            self.assertIn("AGENTS.md", drift_artifacts)

    def test_hand_edited_claude_hook_reports_drift(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            hook_file = next(Path(".claude/hooks").glob("*.py"), None)
            self.assertIsNotNone(hook_file, ".claude/hooks must be populated after init")
            assert hook_file is not None
            hook_file.write_text(
                hook_file.read_text(encoding="utf-8") + "\n# rogue hand-edit\n",
                encoding="utf-8",
            )

            errors = check_sync_parity(Path.cwd())
            drift_artifacts = [e.artifact for e in errors]
            self.assertTrue(
                any(".claude/hooks" in a for a in drift_artifacts),
                f"expected .claude/hooks drift; got {drift_artifacts}",
            )


class SyncParityRestoresSnapshotTest(unittest.TestCase):
    """The parity check must not mutate the tree after it finishes."""

    def test_hand_edited_surface_is_restored_after_check(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            agents_md = Path("AGENTS.md")
            drifted = agents_md.read_text(encoding="utf-8") + "\nextra\n"
            agents_md.write_text(drifted, encoding="utf-8")

            errors = check_sync_parity(Path.cwd())
            self.assertTrue(errors, "expected drift to be reported")

            self.assertEqual(
                drifted,
                agents_md.read_text(encoding="utf-8"),
                "check_sync_parity must restore the pre-check file state",
            )


class SyncParityDateNormalizationTest(unittest.TestCase):
    """Stale AGENTS.md sync_date must not be reported as drift."""

    def test_outdated_sync_date_does_not_trigger_drift(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            agents_md = Path("AGENTS.md")
            content = agents_md.read_text(encoding="utf-8")
            stale = content.replace("- **Updated**: 20", "- **Updated**: 19", 1)
            if stale == content:
                import re

                stale = re.sub(
                    r"- \*\*Updated\*\*: \d{4}-\d{2}-\d{2}",
                    "- **Updated**: 1999-01-01",
                    content,
                    count=1,
                )
            self.assertNotEqual(stale, content, "test fixture must actually change the date")
            agents_md.write_text(stale, encoding="utf-8")

            errors = check_sync_parity(Path.cwd())
            agents_errors = [e for e in errors if e.artifact == "AGENTS.md"]
            self.assertEqual(
                [],
                agents_errors,
                f"stale sync_date must not trigger drift; got {[e.message for e in agents_errors]}",
            )


if __name__ == "__main__":
    unittest.main()
