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

    def test_includes_active_pipeline_enforcement_registration(self) -> None:
        """Generated settings wire the active OBPI-06 enforcement chain."""
        config = GzkitConfig(project_name="gzkit-test")

        settings = generate_claude_settings(config)

        pretool_hooks = settings["hooks"]["PreToolUse"]
        posttool_hooks = settings["hooks"]["PostToolUse"]

        self.assertFalse(settings["enabledPlugins"]["superpowers@claude-plugins-official"])

        self.assertEqual(
            pretool_hooks,
            [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "uv run python .claude/hooks/plan-audit-gate.py",
                        }
                    ],
                },
                {
                    "matcher": "Write|Edit",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "uv run python .claude/hooks/session-staleness-check.py",
                        },
                        {
                            "type": "command",
                            "command": "uv run python .claude/hooks/pipeline-gate.py",
                        },
                        {
                            "type": "command",
                            "command": ("uv run python .claude/hooks/obpi-completion-validator.py"),
                        },
                        {
                            "type": "command",
                            "command": "uv run python .claude/hooks/instruction-router.py",
                        },
                    ],
                },
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": (
                                "uv run python .claude/hooks/pipeline-completion-reminder.py"
                            ),
                        }
                    ],
                },
            ],
        )
        self.assertEqual(
            posttool_hooks,
            [
                {
                    "matcher": "ExitPlanMode",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "uv run python .claude/hooks/pipeline-router.py",
                        }
                    ],
                },
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "command",
                            "command": "uv run python .claude/hooks/post-edit-ruff.py",
                        },
                        {
                            "type": "command",
                            "command": "uv run python .claude/hooks/ledger-writer.py",
                        },
                    ],
                },
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
            pipeline_gate = hooks_dir / "pipeline-gate.py"
            pipeline_completion_reminder = hooks_dir / "pipeline-completion-reminder.py"
            session_staleness_check = hooks_dir / "session-staleness-check.py"
            obpi_completion_validator = hooks_dir / "obpi-completion-validator.py"
            ledger_writer = hooks_dir / "ledger-writer.py"
            readme = hooks_dir / "README.md"
            settings_path = project_root / ".claude" / "settings.json"

            for path in (
                instruction_router,
                post_edit_ruff,
                plan_audit_gate,
                pipeline_router,
                pipeline_gate,
                pipeline_completion_reminder,
                session_staleness_check,
                obpi_completion_validator,
                ledger_writer,
                readme,
                settings_path,
            ):
                self.assertTrue(path.exists(), path)

            self.assertIn(".claude/hooks/instruction-router.py", created)
            self.assertIn(".claude/hooks/post-edit-ruff.py", created)
            self.assertIn(".claude/hooks/plan-audit-gate.py", created)
            self.assertIn(".claude/hooks/pipeline-router.py", created)
            self.assertIn(".claude/hooks/pipeline-gate.py", created)
            self.assertIn(".claude/hooks/pipeline-completion-reminder.py", created)
            self.assertIn(".claude/hooks/session-staleness-check.py", created)
            self.assertIn(".claude/hooks/obpi-completion-validator.py", created)
            self.assertIn(".claude/hooks/ledger-writer.py", created)
            self.assertIn(".claude/hooks/README.md", created)
            self.assertIn(".claude/settings.json", created)

            settings = json.loads(settings_path.read_text(encoding="utf-8"))
            self.assertFalse(settings["enabledPlugins"]["superpowers@claude-plugins-official"])
            self.assertEqual(
                settings["hooks"]["PreToolUse"],
                [
                    {
                        "matcher": "ExitPlanMode",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "uv run python .claude/hooks/plan-audit-gate.py",
                            }
                        ],
                    },
                    {
                        "matcher": "Write|Edit",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "uv run python .claude/hooks/session-staleness-check.py",
                            },
                            {
                                "type": "command",
                                "command": "uv run python .claude/hooks/pipeline-gate.py",
                            },
                            {
                                "type": "command",
                                "command": (
                                    "uv run python .claude/hooks/obpi-completion-validator.py"
                                ),
                            },
                            {
                                "type": "command",
                                "command": "uv run python .claude/hooks/instruction-router.py",
                            },
                        ],
                    },
                    {
                        "matcher": "Bash",
                        "hooks": [
                            {
                                "type": "command",
                                "command": (
                                    "uv run python .claude/hooks/pipeline-completion-reminder.py"
                                ),
                            }
                        ],
                    },
                ],
            )
            self.assertEqual(
                settings["hooks"]["PostToolUse"],
                [
                    {
                        "matcher": "ExitPlanMode",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "uv run python .claude/hooks/pipeline-router.py",
                            }
                        ],
                    },
                    {
                        "matcher": "Edit|Write",
                        "hooks": [
                            {
                                "type": "command",
                                "command": "uv run python .claude/hooks/post-edit-ruff.py",
                            },
                            {
                                "type": "command",
                                "command": "uv run python .claude/hooks/ledger-writer.py",
                            },
                        ],
                    },
                ],
            )

            readme_text = readme.read_text(encoding="utf-8")
            self.assertIn("Current hook surface in gzkit:", readme_text)
            self.assertIn("hook that auto-surfaces", readme_text)
            self.assertIn("plan-audit-gate.py", readme_text)
            self.assertIn("pipeline-router.py", readme_text)
            self.assertIn("pipeline-gate.py", readme_text)
            self.assertIn("pipeline-completion-reminder.py", readme_text)
            self.assertIn("session-staleness-check.py", readme_text)
            self.assertIn("obpi-completion-validator.py", readme_text)
            self.assertIn("src/gzkit/pipeline_runtime.py", readme_text)
            self.assertIn("Registration Order", readme_text)
            self.assertNotIn("not yet active in", readme_text)
            self.assertNotIn("historical", readme_text)
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
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-03", result.stdout)
            self.assertEqual(result.stderr, "")


class TestPipelineGateHook(unittest.TestCase):
    """Tests for the generated pipeline gate script."""

    def _create_hook(self, project_root: Path) -> Path:
        config = GzkitConfig(project_name="gzkit-test")
        setup_claude_hooks(project_root, config)
        return project_root / ".claude" / "hooks" / "pipeline-gate.py"

    def _run_hook(
        self,
        script_path: Path,
        cwd: Path,
        *,
        file_path: str,
    ) -> subprocess.CompletedProcess[str]:
        payload = {"cwd": str(cwd), "tool_input": {"file_path": file_path}}
        return subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def _write_receipt(self, plans_dir: Path, *, obpi_id: str, verdict: str) -> None:
        plans_dir.mkdir(parents=True, exist_ok=True)
        (plans_dir / ".plan-audit-receipt.json").write_text(
            json.dumps(
                {
                    "obpi_id": obpi_id,
                    "timestamp": "2026-03-13T12:00:00Z",
                    "verdict": verdict,
                }
            )
            + "\n",
            encoding="utf-8",
        )

    def _write_marker(self, plans_dir: Path, name: str, *, obpi_id: str) -> None:
        plans_dir.mkdir(parents=True, exist_ok=True)
        (plans_dir / name).write_text(
            json.dumps({"obpi_id": obpi_id, "started_at": "2026-03-13T12:00:00Z"}) + "\n",
            encoding="utf-8",
        )

    def test_allows_non_implementation_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root, file_path="docs/readme.md")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_when_receipt_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_when_receipt_is_not_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(
                project_root / ".claude" / "plans",
                obpi_id="OBPI-0.12.0-04",
                verdict="FAIL",
            )

            result = self._run_hook(script_path, project_root, file_path="tests/test_demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_blocks_when_pass_receipt_exists_without_marker(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)
            self._write_receipt(
                project_root / ".claude" / "plans",
                obpi_id="OBPI-0.12.0-04",
                verdict="PASS",
            )

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Pipeline not invoked for OBPI-0.12.0-04.", result.stderr)
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-04", result.stderr)
            self.assertIn("--from=verify", result.stderr)

    def test_allows_when_per_obpi_marker_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-04.json",
                obpi_id="OBPI-0.12.0-04",
            )

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_allows_when_richer_per_obpi_marker_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-04.json",
                obpi_id="OBPI-0.12.0-04",
            )
            (plans_dir / ".pipeline-active-OBPI-0.12.0-04.json").write_text(
                json.dumps(
                    {
                        "obpi_id": "OBPI-0.12.0-04",
                        "parent_adr": "ADR-0.12.0-obpi-pipeline-enforcement-parity",
                        "lane": "heavy",
                        "entry": "verify",
                        "execution_mode": "normal",
                        "current_stage": "verify",
                        "started_at": "2026-03-13T12:00:00Z",
                        "updated_at": "2026-03-13T12:05:00Z",
                        "receipt_state": "pass",
                        "blockers": [],
                        "required_human_action": None,
                        "next_command": "uv run gz obpi pipeline OBPI-0.12.0-04 --from=ceremony",
                        "resume_point": "ceremony",
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_allows_when_legacy_marker_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            self._write_marker(plans_dir, ".pipeline-active.json", obpi_id="OBPI-0.12.0-04")

            result = self._run_hook(script_path, project_root, file_path="tests/test_demo.py")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_blocks_when_marker_is_corrupt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".pipeline-active.json").write_text("{oops\n", encoding="utf-8")

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Pipeline not invoked for OBPI-0.12.0-04.", result.stderr)

    def test_blocks_when_marker_obpi_does_not_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_receipt(plans_dir, obpi_id="OBPI-0.12.0-04", verdict="PASS")
            self._write_marker(plans_dir, ".pipeline-active.json", obpi_id="OBPI-0.12.0-03")

            result = self._run_hook(script_path, project_root, file_path="src/demo.py")

            self.assertEqual(result.returncode, 2)
            self.assertIn("BLOCKED: Pipeline not invoked for OBPI-0.12.0-04.", result.stderr)


class TestPipelineCompletionReminderHook(unittest.TestCase):
    """Tests for the generated pipeline completion reminder script."""

    def _create_hook(self, project_root: Path) -> Path:
        config = GzkitConfig(project_name="gzkit-test")
        setup_claude_hooks(project_root, config)
        return project_root / ".claude" / "hooks" / "pipeline-completion-reminder.py"

    def _run_hook(
        self,
        script_path: Path,
        cwd: Path,
        *,
        command: str,
    ) -> subprocess.CompletedProcess[str]:
        payload = {"cwd": str(cwd), "tool_input": {"command": command}}
        return subprocess.run(
            [sys.executable, str(script_path)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def _write_marker(self, plans_dir: Path, name: str, payload: dict[str, str]) -> None:
        plans_dir.mkdir(parents=True, exist_ok=True)
        (plans_dir / name).write_text(json.dumps(payload) + "\n", encoding="utf-8")

    def _write_brief(self, project_root: Path, *, status: str) -> Path:
        brief_path = (
            project_root
            / "docs"
            / "design"
            / "adr"
            / "pre-release"
            / "ADR-0.12.0-obpi-pipeline-enforcement-parity"
            / "obpis"
            / "OBPI-0.12.0-05-completion-reminder-surface.md"
        )
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(
            "\n".join(
                [
                    "---",
                    "id: OBPI-0.12.0-05-completion-reminder-surface",
                    f"status: {status}",
                    "---",
                    "",
                    "# OBPI-0.12.0-05",
                    "",
                    f"**Status:** {status}",
                    "",
                    f"**Brief Status:** {status}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return brief_path

    def test_allows_silently_when_command_is_not_commit_or_push(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root, command="git status")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_marker_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            script_path = self._create_hook(project_root)

            result = self._run_hook(script_path, project_root, command="git commit -m test")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_marker_is_corrupt(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            plans_dir.mkdir(parents=True, exist_ok=True)
            (plans_dir / ".pipeline-active.json").write_text("{oops\n", encoding="utf-8")

            result = self._run_hook(script_path, project_root, command="git push origin main")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_marker_has_no_obpi(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active.json",
                {"started_at": "2026-03-13T12:00:00Z"},
            )

            result = self._run_hook(script_path, project_root, command="git commit -m test")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_allows_silently_when_brief_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-05.json",
                {"obpi_id": "OBPI-0.12.0-05", "started_at": "2026-03-13T12:00:00Z"},
            )

            result = self._run_hook(script_path, project_root, command="git push origin main")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")

    def test_emits_stale_marker_note_when_brief_is_completed(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-05.json",
                {"obpi_id": "OBPI-0.12.0-05", "started_at": "2026-03-13T12:00:00Z"},
            )
            self._write_brief(project_root, status="Completed")

            result = self._run_hook(script_path, project_root, command="git commit -m test")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("STALE PIPELINE MARKER", result.stderr)
            self.assertIn("OBPI-0.12.0-05", result.stderr)
            self.assertIn("runtime-managed", result.stderr)

    def test_emits_reminder_when_brief_is_incomplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-05.json",
                {"obpi_id": "OBPI-0.12.0-05", "started_at": "2026-03-13T12:00:00Z"},
            )
            self._write_brief(project_root, status="Accepted")

            result = self._run_hook(script_path, project_root, command="git push origin main")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("PIPELINE COMPLETION REMINDER", result.stderr)
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-05 --from=verify", result.stderr)
            self.assertIn("Do not clear the pipeline marker by hand", result.stderr)

    def test_emits_reminder_with_richer_marker_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            plans_dir = project_root / ".claude" / "plans"
            script_path = self._create_hook(project_root)
            self._write_marker(
                plans_dir,
                ".pipeline-active-OBPI-0.12.0-05.json",
                {
                    "obpi_id": "OBPI-0.12.0-05",
                    "parent_adr": "ADR-0.12.0-obpi-pipeline-enforcement-parity",
                    "lane": "heavy",
                    "entry": "verify",
                    "execution_mode": "normal",
                    "current_stage": "verify",
                    "started_at": "2026-03-13T12:00:00Z",
                    "updated_at": "2026-03-13T12:05:00Z",
                    "receipt_state": "pass",
                    "blockers": [],
                    "required_human_action": None,
                    "next_command": "uv run gz obpi pipeline OBPI-0.12.0-05 --from=ceremony",
                    "resume_point": "ceremony",
                },
            )
            self._write_brief(project_root, status="Accepted")

            result = self._run_hook(script_path, project_root, command="git push origin main")

            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertIn("PIPELINE COMPLETION REMINDER", result.stderr)
            self.assertIn("Active OBPI pipeline: OBPI-0.12.0-05", result.stderr)
            self.assertIn("Current stage: verify", result.stderr)
            self.assertIn("uv run gz obpi pipeline OBPI-0.12.0-05 --from=ceremony", result.stderr)


if __name__ == "__main__":
    unittest.main()
