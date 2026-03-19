import json
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.quality import CheckResult, QualityResult
from tests.commands.common import CliRunner


class TestSkillCommands(unittest.TestCase):
    """Tests for skill subcommands."""

    @staticmethod
    def _write_stale_mirror_skill() -> None:
        stale = Path(".claude/skills/stale-skill")
        stale.mkdir(parents=True, exist_ok=True)
        (stale / "SKILL.md").write_text(
            "\n".join(
                [
                    "---",
                    "name: stale-skill",
                    "description: stale mirror skill",
                    "lifecycle_state: active",
                    "owner: gzkit-governance",
                    "last_reviewed: 2026-03-01",
                    "---",
                    "",
                    "# SKILL.md",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    @staticmethod
    def _set_skill_last_reviewed_all_roots(skill_name: str, last_reviewed: str) -> None:
        roots = [".gzkit/skills", ".agents/skills", ".claude/skills", ".github/skills"]
        for root in roots:
            skill_file = Path(root) / skill_name / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            updated = []
            for line in content.splitlines():
                if line.startswith("last_reviewed:"):
                    updated.append(f"last_reviewed: {last_reviewed}")
                else:
                    updated.append(line)
            skill_file.write_text("\n".join(updated) + "\n", encoding="utf-8")

    def test_skill_list(self) -> None:
        """skill list shows scaffolded skills."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["skill", "list"])
            self.assertEqual(result.exit_code, 0)
            # Should show core skills from init
            self.assertIn("lint", result.output)
            self.assertIn("gz-adr-create", result.output)
            self.assertNotIn("gz-adr-manager", result.output)

    def test_skill_new(self) -> None:
        """skill new creates skill."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["skill", "new", "my-skill"])
            self.assertEqual(result.exit_code, 0)
            skill_file = Path(".gzkit/skills/my-skill/SKILL.md")
            self.assertTrue(skill_file.exists())
            content = skill_file.read_text(encoding="utf-8")
            self.assertIn("compatibility:", content)
            self.assertIn("invocation:", content)
            self.assertIn("gz_command:", content)
            self.assertIn("metadata:", content)

    def test_init_scaffolds_adr_create_and_removes_adr_manager(self) -> None:
        """core skill scaffolding uses gz-adr-create hard cutover."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self.assertTrue(Path(".gzkit/skills/gz-adr-create/SKILL.md").exists())
            self.assertFalse(Path(".gzkit/skills/gz-adr-manager").exists())

    def test_skill_audit_passes_after_init(self) -> None:
        """skill audit passes for freshly initialized project."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["skill", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_skill_audit_warning_is_non_blocking_without_strict(self) -> None:
        """Stale mirror-only skills emit non-blocking warnings by default."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._write_stale_mirror_skill()
            result = runner.invoke(main, ["skill", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("non-blocking", result.output.lower())
            self.assertIn("blocking: 0", result.output.lower())
            self.assertIn("non-blocking: 1", result.output.lower())

    def test_skill_audit_strict_fails_on_non_blocking_warnings(self) -> None:
        """Strict mode escalates warnings to failure."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._write_stale_mirror_skill()
            result = runner.invoke(main, ["skill", "audit", "--strict"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("non-blocking warnings", result.output.lower())
            self.assertIn("ska-mirror-dir-unexpected", result.output.lower())

    def test_skill_audit_json_includes_issue_codes_and_blocking_counts(self) -> None:
        """JSON payload includes additive policy fields for machine consumers."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._write_stale_mirror_skill()
            result = runner.invoke(main, ["skill", "audit", "--json"])
            self.assertEqual(result.exit_code, 0)
            payload = json.loads(result.output)
            self.assertIn("blocking_error_count", payload)
            self.assertIn("non_blocking_warning_count", payload)
            self.assertIn("max_review_age_days", payload)
            self.assertIn("stale_review_count", payload)
            self.assertEqual(payload["blocking_error_count"], 0)
            self.assertEqual(payload["non_blocking_warning_count"], 1)
            self.assertEqual(payload["max_review_age_days"], 90)
            self.assertEqual(payload["stale_review_count"], 0)
            self.assertTrue(payload["issues"])
            issue = payload["issues"][0]
            self.assertIn("code", issue)
            self.assertIn("blocking", issue)
            self.assertFalse(issue["blocking"])
            self.assertEqual(issue["code"], "SKA-MIRROR-DIR-UNEXPECTED")

    def test_skill_audit_rejects_non_positive_max_review_age_days(self) -> None:
        """Non-positive max review age is rejected as invalid input."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["skill", "audit", "--max-review-age-days", "0"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("positive integer", result.output.lower())

    def test_skill_audit_max_review_age_override_relaxes_stale_failure(self) -> None:
        """Override can relax stale-review blocking checks when policy allows."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            stale_date = (date.today() - timedelta(days=120)).isoformat()
            self._set_skill_last_reviewed_all_roots("lint", stale_date)

            default_result = runner.invoke(main, ["skill", "audit"])
            self.assertNotEqual(default_result.exit_code, 0)
            self.assertIn("ska-last-reviewed-stale", default_result.output.lower())

            relaxed_result = runner.invoke(main, ["skill", "audit", "--max-review-age-days", "365"])
            self.assertEqual(relaxed_result.exit_code, 0)

    def test_check_command_passes_with_non_blocking_skill_audit_warning(self) -> None:
        """Aggregate check remains pass when skill audit warning is non-blocking."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            ok = QualityResult(success=True, command="cmd", stdout="", stderr="", returncode=0)
            warning_skill_audit = QualityResult(
                success=True,
                command="uv run gz skill audit",
                stdout="Warnings: SKA-MIRROR-DIR-UNEXPECTED",
                stderr="",
                returncode=0,
            )
            fake = CheckResult(
                success=True,
                lint=ok,
                format=ok,
                typecheck=ok,
                test=ok,
                skill_audit=warning_skill_audit,
                parity_check=ok,
                readiness_audit=ok,
            )
            with patch("gzkit.cli.run_all_checks", return_value=fake):
                result = runner.invoke(main, ["check"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("all checks passed", result.output.lower())
