"""Tests for gzkit hooks module."""

import json
import os
import tempfile
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.hooks.claude import generate_claude_settings, setup_claude_hooks
from gzkit.hooks.core import (
    generate_hook_script,
    is_governance_artifact,
    write_hook_script,
)


class TestIsGovernanceArtifact(unittest.TestCase):
    """Tests for governance artifact detection."""

    def test_design_prd(self) -> None:
        """Detects PRD in design directory."""
        self.assertTrue(is_governance_artifact("design/prd/PRD-TEST.md"))

    def test_design_adr(self) -> None:
        """Detects ADR in design directory."""
        self.assertTrue(is_governance_artifact("design/adr/ADR-0.1.0.md"))

    def test_design_obpis(self) -> None:
        """Detects OBPI in design directory."""
        self.assertTrue(is_governance_artifact("design/obpis/OBPI-core.md"))

    def test_docs_adr(self) -> None:
        """Detects ADR in docs directory."""
        self.assertTrue(is_governance_artifact("docs/adr/ADR-0.1.0.md"))

    def test_agents_md(self) -> None:
        """Detects AGENTS.md."""
        self.assertTrue(is_governance_artifact("AGENTS.md"))

    def test_claude_md(self) -> None:
        """Detects CLAUDE.md."""
        self.assertTrue(is_governance_artifact("CLAUDE.md"))

    def test_source_code(self) -> None:
        """Source code is not a governance artifact."""
        self.assertFalse(is_governance_artifact("src/gzkit/cli.py"))

    def test_test_file(self) -> None:
        """Test file is not a governance artifact."""
        self.assertFalse(is_governance_artifact("tests/test_cli.py"))


class TestGenerateHookScript(unittest.TestCase):
    """Tests for hook script generation."""

    def test_generates_python_script(self) -> None:
        """Generates valid Python script."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script = generate_hook_script("claude", project_root)

            self.assertIn("#!/usr/bin/env python3", script)
            self.assertIn("def main()", script)
            self.assertIn("json.load(sys.stdin)", script)

    def test_includes_hook_type(self) -> None:
        """Script includes hook type in docstring."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script = generate_hook_script("claude", project_root)
            self.assertIn("claude", script)


class TestWriteHookScript(unittest.TestCase):
    """Tests for writing hook scripts."""

    def test_creates_hook_file(self) -> None:
        """Creates hook script file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = write_hook_script(project_root, "claude", ".claude/hooks")

            self.assertTrue(script_path.exists())
            self.assertEqual(script_path.name, "ledger-writer.py")

    def test_makes_executable(self) -> None:
        """Hook script is executable."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = write_hook_script(project_root, "claude", ".claude/hooks")

            if os.name == "nt":
                self.assertTrue(script_path.exists())
                self.assertEqual(script_path.suffix, ".py")
                return

            # Check executable bit on Unix-like systems.
            import stat

            mode = script_path.stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR)


class TestGenerateClaudeSettings(unittest.TestCase):
    """Tests for Claude settings generation."""

    def test_includes_instruction_router_post_edit_and_ledger_writer(self) -> None:
        """Generated settings wire the full OBPI-01 hook tranche."""
        config = GzkitConfig(project_name="gzkit-test")

        settings = generate_claude_settings(config)

        pretool_hooks = settings["hooks"]["PreToolUse"][0]["hooks"]
        posttool_hooks = settings["hooks"]["PostToolUse"][0]["hooks"]
        pretool_commands = [hook["command"] for hook in pretool_hooks]
        posttool_commands = [hook["command"] for hook in posttool_hooks]

        self.assertEqual(
            pretool_commands,
            ["uv run python .claude/hooks/instruction-router.py"],
        )
        self.assertEqual(
            posttool_commands,
            [
                "uv run python .claude/hooks/post-edit-ruff.py",
                "uv run python .claude/hooks/ledger-writer.py",
            ],
        )


class TestSetupClaudeHooks(unittest.TestCase):
    """Tests for Claude hook setup."""

    def test_creates_full_hook_tranche_and_settings(self) -> None:
        """Setup writes the tranche files referenced by settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            created = setup_claude_hooks(project_root, config)
            created = [path.replace("\\", "/") for path in created]

            hooks_dir = project_root / ".claude" / "hooks"
            instruction_router = hooks_dir / "instruction-router.py"
            post_edit_ruff = hooks_dir / "post-edit-ruff.py"
            ledger_writer = hooks_dir / "ledger-writer.py"
            readme = hooks_dir / "README.md"
            settings_path = project_root / ".claude" / "settings.json"

            for path in (
                instruction_router,
                post_edit_ruff,
                ledger_writer,
                readme,
                settings_path,
            ):
                self.assertTrue(path.exists(), path)

            self.assertIn(".claude/hooks/instruction-router.py", created)
            self.assertIn(".claude/hooks/post-edit-ruff.py", created)
            self.assertIn(".claude/hooks/ledger-writer.py", created)
            self.assertIn(".claude/hooks/README.md", created)
            self.assertIn(".claude/settings.json", created)

            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            self.assertEqual(
                settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"],
                "uv run python .claude/hooks/instruction-router.py",
            )
            self.assertEqual(
                [hook["command"] for hook in settings["hooks"]["PostToolUse"][0]["hooks"]],
                [
                    "uv run python .claude/hooks/post-edit-ruff.py",
                    "uv run python .claude/hooks/ledger-writer.py",
                ],
            )

            readme_text = readme.read_text(encoding="utf-8")
            self.assertIn("Current hook surface in gzkit:", readme_text)
            self.assertIn("hook that auto-surfaces", readme_text)
            self.assertIn("hook that runs `ruff check --fix`", readme_text)
            self.assertIn("hook that records governance", readme_text)


if __name__ == "__main__":
    unittest.main()
