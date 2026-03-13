"""Tests for gzkit hooks module."""

import json
import os
import subprocess
import sys
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
            plan_audit_gate = hooks_dir / "plan-audit-gate.py"
            pipeline_router = hooks_dir / "pipeline-router.py"
            ledger_writer = hooks_dir / "ledger-writer.py"
            readme = hooks_dir / "README.md"
            settings_path = project_root / ".claude" / "settings.json"

            for path in (
                instruction_router,
                post_edit_ruff,
                plan_audit_gate,
                pipeline_router,
                ledger_writer,
                readme,
                settings_path,
            ):
                self.assertTrue(path.exists(), path)

            self.assertIn(".claude/hooks/instruction-router.py", created)
            self.assertIn(".claude/hooks/post-edit-ruff.py", created)
            self.assertIn(".claude/hooks/plan-audit-gate.py", created)
            self.assertIn(".claude/hooks/pipeline-router.py", created)
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
            self.assertIn("plan-audit-gate.py", readme_text)
            self.assertIn("pipeline-router.py", readme_text)
            self.assertIn("not yet active in", readme_text)
            self.assertIn("hook that runs `ruff check --fix`", readme_text)
            self.assertIn("hook that records governance", readme_text)


class TestPlanAuditGateHook(unittest.TestCase):
    """Tests for the generated plan-audit gate script."""

    def _create_hook(self, project_root: Path) -> Path:
        config = GzkitConfig(project_name="gzkit-test")
        setup_claude_hooks(project_root, config)
        return project_root / ".claude" / "hooks" / "plan-audit-gate.py"

    def _run_hook(self, script_path: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
        payload = {"cwd": str(cwd)}
        return subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def _write_plan(self, plans_dir: Path, name: str, content: str) -> Path:
        plans_dir.mkdir(parents=True, exist_ok=True)
        plan_path = plans_dir / name
        plan_path.write_text(content, encoding="utf-8")
        return plan_path

    def _write_receipt(self, plans_dir: Path, *, obpi_id: str, verdict: str) -> Path:
        receipt_path = plans_dir / ".plan-audit-receipt.json"
        receipt_path.write_text(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "timestamp": "2026-03-12T12:00:00Z",
                    "verdict": verdict,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return receipt_path

    def test_allows_when_plans_dir_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_allows_when_latest_plan_has_no_obpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            self._write_plan(plans_dir, "notes.md", "Plan for docs cleanup only\n")

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)

    def test_blocks_when_obpi_plan_has_no_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Cannot exit plan mode - plan audit required.", result.stderr)
            self.assertIn("/gz-plan-audit OBPI-0.12.0-02", result.stderr)

    def test_allows_when_matching_pass_receipt_is_newer_than_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="PASS")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)

    def test_allows_when_matching_fail_receipt_is_newer_than_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="FAIL")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)

    def test_blocks_when_receipt_is_older_than_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="PASS")
            os.utime(receipt_path, (1_700_000_000, 1_700_000_000))
            os.utime(plan_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Audit receipt is older than plan file", result.stderr)

    def test_blocks_when_receipt_obpi_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-07", verdict="PASS")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("Audit receipt is for OBPI-0.12.0-07", result.stderr)

    def test_blocks_when_receipt_verdict_is_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(plans_dir, "active.md", "Implement OBPI-0.12.0-02\n")
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="MAYBE")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid verdict", result.stderr)

    def test_emits_prior_art_warning_without_blocking_valid_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plan_path = self._write_plan(
                plans_dir,
                "active.md",
                "Create `src/new_module.py` for OBPI-0.12.0-02 without prior pattern notes\n",
            )
            receipt_path = self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-02", verdict="PASS")
            os.utime(plan_path, (1_700_000_000, 1_700_000_000))
            os.utime(receipt_path, (1_700_000_100, 1_700_000_100))

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertIn("PRIOR ART REMINDER", result.stderr)


class TestPipelineRouterHook(unittest.TestCase):
    """Tests for the generated pipeline router script."""

    def _create_hook(self, project_root: Path) -> Path:
        config = GzkitConfig(project_name="gzkit-test")
        setup_claude_hooks(project_root, config)
        return project_root / ".claude" / "hooks" / "pipeline-router.py"

    def _run_hook(self, script_path: Path, cwd: Path) -> subprocess.CompletedProcess[str]:
        payload = {"cwd": str(cwd)}
        return subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def _write_receipt(
        self,
        plans_dir: Path,
        *,
        obpi_id: str | None,
        verdict: str,
    ) -> Path:
        payload = {"timestamp": "2026-03-12T12:00:00Z", "verdict": verdict}
        if obpi_id is not None:
            payload["obpi_id"] = obpi_id

        receipt_path = plans_dir / ".plan-audit-receipt.json"
        plans_dir.mkdir(parents=True, exist_ok=True)
        receipt_path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        return receipt_path

    def test_allows_silently_when_receipt_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_receipt_is_corrupt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            plans_dir = project_root / ".claude" / "plans"
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".plan-audit-receipt.json").write_text("{oops\n", encoding="utf-8")

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_receipt_has_no_obpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(project_root / ".claude" / "plans", obpi_id=None, verdict="PASS")

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_receipt_verdict_is_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(
                project_root / ".claude" / "plans",
                obpi_id="OBPI-0.12.0-03",
                verdict="FAIL",
            )

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_routes_when_receipt_verdict_is_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(
                project_root / ".claude" / "plans",
                obpi_id="OBPI-0.12.0-03",
                verdict="PASS",
            )

            result = self._run_hook(script_path, project_root)

            self.assertEqual(result.returncode, 0)
            self.assertIn("OBPI plan approved: OBPI-0.12.0-03", result.stdout)
            self.assertIn("/gz-obpi-pipeline OBPI-0.12.0-03", result.stdout)
            self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
