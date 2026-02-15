"""Tests for gzkit hooks module."""

import os
import tempfile
import unittest
from pathlib import Path

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
        if os.name == "nt":
            self.skipTest("Executable bit is not meaningful on Windows")
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = write_hook_script(project_root, "claude", ".claude/hooks")

            # Check executable bit
            import stat

            mode = script_path.stat().st_mode
            self.assertTrue(mode & stat.S_IXUSR)


if __name__ == "__main__":
    unittest.main()
