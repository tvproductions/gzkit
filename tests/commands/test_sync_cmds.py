import os
import subprocess
import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner


class TestGitSyncCommand(unittest.TestCase):
    """Tests for git sync ritual commands."""

    def test_git_sync_skill_flag_prints_skill_path(self) -> None:
        """git-sync --skill prints paired skill path without repo checks."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["git-sync", "--skill"])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output.strip(), ".gzkit/skills/git-sync/SKILL.md")

    def test_sync_repo_alias_is_removed(self) -> None:
        """sync-repo alias is no longer accepted after hard cutover."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["sync-repo", "--skill"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("invalid choice", result.output.lower())

    def test_git_sync_fails_outside_git_repo(self) -> None:
        """git-sync returns error when cwd is not a git repo."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["git-sync"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("not a git repository", result.output.lower())

    def test_git_sync_dry_run_in_git_repo(self) -> None:
        """git-sync dry-run works in a local git repo."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            subprocess.run(["git", "init"], check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(["git", "add", "-A"], check=True, capture_output=True, text=True)
            subprocess.run(
                ["git", "commit", "-m", "chore: initial"],
                check=True,
                capture_output=True,
                text=True,
            )

            result = runner.invoke(main, ["git-sync"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Git sync plan", result.output)

            alias_result = runner.invoke(main, ["sync-repo"])
            self.assertNotEqual(alias_result.exit_code, 0)
            self.assertIn("invalid choice", alias_result.output.lower())

    def test_git_sync_rejects_skip_that_disables_xenon(self) -> None:
        """git-sync blocks SKIP values that can bypass xenon complexity checks."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            original_skip = os.environ.get("SKIP")
            os.environ["SKIP"] = "xenon-complexity"
            try:
                result = runner.invoke(main, ["git-sync"])
            finally:
                if original_skip is None:
                    os.environ.pop("SKIP", None)
                else:
                    os.environ["SKIP"] = original_skip

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Refusing git-sync with SKIP", result.output)


class TestSyncCommand(unittest.TestCase):
    """Tests for control-surface sync commands."""

    def test_agent_sync_control_surfaces_updates_surfaces(self) -> None:
        """agent sync control-surfaces is the canonical command."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("Sync complete", result.output)

    def test_agent_sync_dry_run_reports_complete_write_set(self) -> None:
        """Dry-run output must list every path that sync_all() would touch."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            apply_result = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            self.assertEqual(apply_result.exit_code, 0)
            applied = {
                line.strip().removeprefix("Updated ")
                for line in apply_result.output.splitlines()
                if line.strip().startswith("Updated ")
            }
            self.assertTrue(applied, "apply-mode must report at least one updated path")

            dry_result = runner.invoke(main, ["agent", "sync", "control-surfaces", "--dry-run"])
            self.assertEqual(dry_result.exit_code, 0)
            for path in applied:
                self.assertIn(
                    path,
                    dry_result.output,
                    f"dry-run must list {path} from apply-mode write set",
                )

    def test_agent_sync_dry_run_does_not_mutate_disk(self) -> None:
        """Dry-run must not modify any file on disk."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            before: dict[str, bytes] = {}
            for surface_root in (
                "AGENTS.md",
                "CLAUDE.md",
                ".github/copilot-instructions.md",
                ".claude/hooks",
                ".claude/skills",
            ):
                p = Path(surface_root)
                if p.is_file():
                    before[str(p)] = p.read_bytes()
                elif p.is_dir():
                    for f in p.rglob("*"):
                        if f.is_file():
                            before[str(f)] = f.read_bytes()

            dry_result = runner.invoke(main, ["agent", "sync", "control-surfaces", "--dry-run"])
            self.assertEqual(dry_result.exit_code, 0)

            for path, original in before.items():
                self.assertEqual(
                    original,
                    Path(path).read_bytes(),
                    f"dry-run mutated {path}",
                )

    def test_sync_alias_is_removed(self) -> None:
        """sync top-level alias is no longer accepted after hard cutover."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["sync"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("invalid choice", result.output.lower())

    def test_agent_control_sync_alias_is_removed(self) -> None:
        """agent-control-sync alias is no longer accepted after hard cutover."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            result = runner.invoke(main, ["agent-control-sync"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("invalid choice", result.output.lower())

    def test_agent_sync_fails_closed_on_canonical_skill_corruption(self) -> None:
        """Sync blocks mirror propagation when canonical SKILL metadata is invalid."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            Path(".gzkit/skills/lint/SKILL.md").write_text("# SKILL.md\n\nbroken\n")

            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("preflight failed", result.output.lower())
            self.assertIn(".gzkit/skills/lint/SKILL.md", result.output)

    def test_agent_sync_reports_stale_mirror_recovery_non_destructively(self) -> None:
        """Sync warns on stale mirror-only paths and preserves them for manual cleanup."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            stale_skill = Path(".claude/skills/stale-skill")
            stale_skill.mkdir(parents=True, exist_ok=True)
            (stale_skill / "SKILL.md").write_text(
                "---\n"
                "name: stale-skill\n"
                "description: stale\n"
                "lifecycle_state: active\n"
                "owner: gzkit-governance\n"
                "last_reviewed: 2026-02-21\n"
                "---\n\n"
                "# SKILL.md\n"
            )

            result = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertEqual(result.exit_code, 0)
            self.assertIn("Recovery required", result.output)
            self.assertIn(".claude/skills/stale-skill", result.output)
            self.assertTrue(stale_skill.exists())

    def test_agent_sync_output_is_deterministic_across_repeated_runs(self) -> None:
        """Repeated sync command output is stable for unchanged inputs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])

            first = runner.invoke(main, ["agent", "sync", "control-surfaces"])
            second = runner.invoke(main, ["agent", "sync", "control-surfaces"])

            self.assertEqual(first.exit_code, 0)
            self.assertEqual(second.exit_code, 0)
            self.assertEqual(first.output, second.output)
