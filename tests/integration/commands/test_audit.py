import json
import shutil
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.cli import main
from gzkit.doc_coverage.manifest import manpage_path_for
from tests.commands.common import CliRunner

_REAL_PROJECT_ROOT = Path(__file__).resolve().parents[3]

_uv_sync_patcher = patch("gzkit.commands.init_cmd._run_uv_sync", return_value=None)


def setUpModule() -> None:
    """Stub subprocess calls to ``uv sync`` — each real invocation costs ~1s."""
    _uv_sync_patcher.start()


def tearDownModule() -> None:
    _uv_sync_patcher.stop()


class TestConfigAndCliAuditCommands(unittest.TestCase):
    """Tests for check-config-paths and cli audit commands."""

    @staticmethod
    def _prepare_docs_surface() -> None:
        # Copy the real manifest so load_manifest() works in the isolated fs.
        src = _REAL_PROJECT_ROOT / "config" / "doc-coverage.json"
        dst = Path("config") / "doc-coverage.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        from gzkit.doc_coverage.manifest import load_manifest

        index_path = Path("docs/user/commands/index.md")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = load_manifest(Path("."))
        links: list[str] = []
        for command_name, entry in manifest.commands.items():
            if not entry.surfaces.manpage:
                continue
            doc_rel = manpage_path_for(command_name)
            doc_path = Path(doc_rel)
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            doc_path.write_text(f"# gz {command_name}\n\nStub\n")
            links.append(f"- [`gz {command_name}`]({doc_path.name})")
        index_path.write_text("# Commands Index\n\n" + "\n".join(links) + "\n")
        Path("README.md").write_text(
            "\n".join(
                [
                    "# Example Project",
                    "",
                    "## Quick Start",
                    "",
                    "```bash",
                    "gz init",
                    'gz plan create feature --title "Feature description"',
                    "gz status",
                    "gz check",
                    "```",
                    "",
                ]
            )
        )

    @staticmethod
    def _prepare_parity_surface() -> None:
        Path(".github/discovery-index.json").parent.mkdir(parents=True, exist_ok=True)
        Path(".github/discovery-index.json").write_text(
            json.dumps(
                {
                    "version": "1.0.0",
                    "discovery_checklist": {},
                    "completion_checklist": {"lite": [], "heavy": []},
                },
                indent=2,
            )
            + "\n"
        )
        Path("docs/governance/parity-intake-rubric.md").parent.mkdir(parents=True, exist_ok=True)
        Path("docs/governance/parity-intake-rubric.md").write_text("# Rubric\n")
        Path("docs/proposals/REPORT-TEMPLATE-airlineops-parity.md").parent.mkdir(
            parents=True, exist_ok=True
        )
        Path("docs/proposals/REPORT-TEMPLATE-airlineops-parity.md").write_text(
            "\n".join(
                [
                    "# REPORT TEMPLATE",
                    "## Executive Summary",
                    "## Canonical Coverage Matrix",
                    "## Behavior / Procedure Source Matrix",
                    "## Habit Parity Matrix (Required)",
                    "## GovZero Mining Inventory",
                    "## Proof Surface Check",
                    "## Next Actions",
                    "",
                ]
            )
        )
        Path(".gzkit/skills/airlineops-parity-scan/SKILL.md").parent.mkdir(
            parents=True, exist_ok=True
        )
        Path(".gzkit/skills/airlineops-parity-scan/SKILL.md").write_text(
            "\n".join(
                [
                    "# SKILL.md",
                    "uv run gz cli audit",
                    "uv run gz check-config-paths",
                    "uv run gz adr audit-check ADR-<target>",
                    "uv run mkdocs build --strict",
                    "",
                ]
            )
        )
        Path("docs/proposals/REPORT-airlineops-parity-2026-03-01.md").write_text(
            "\n".join(
                [
                    "# REPORT",
                    "Overall parity status: Partial",
                    "## Next Actions",
                    "",
                ]
            )
        )

    @staticmethod
    def _prepare_readiness_surface() -> None:
        Path("README.md").write_text(
            "\n".join(
                [
                    "# Example Project",
                    "",
                    "This is a development covenant for agent execution.",
                    "",
                    "human attestation remains required for completion.",
                    "",
                ]
            )
        )
        Path("docs/governance/governance_runbook.md").parent.mkdir(parents=True, exist_ok=True)
        Path("docs/governance/governance_runbook.md").write_text("# Governance Runbook\n")
        Path("docs/user/concepts").mkdir(parents=True, exist_ok=True)
        Path("docs/user/concepts/lanes.md").write_text("# Lanes\n")
        Path("docs/governance/GovZero/audits").mkdir(parents=True, exist_ok=True)
        Path("docs/governance/GovZero/audits/AUDIT-TEMPLATE-agent-readiness.md").write_text(
            "# Agent Readiness Audit\n"
        )
        Path("docs/user/reference").mkdir(parents=True, exist_ok=True)
        Path("docs/user/reference/agent-input-disciplines.md").write_text(
            "# Agent Input Disciplines\n"
        )
        Path("src/gzkit/templates").mkdir(parents=True, exist_ok=True)
        Path("src/gzkit/templates/obpi.md").write_text(
            "\n".join(
                [
                    "parent:",
                    "item:",
                    "## Objective",
                    "## Allowed Paths",
                    "## Denied Paths",
                    "## Discovery Checklist",
                    "## Requirements (FAIL-CLOSED)",
                    "NEVER",
                    "ALWAYS",
                    "## Acceptance Criteria",
                    "## Completion Checklist",
                    "",
                ]
            )
        )
        Path(".gzkit/skills/gz-obpi-specify/assets").mkdir(parents=True, exist_ok=True)
        Path(".gzkit/skills/gz-obpi-specify/assets/OBPI_BRIEF-template.md").write_text(
            "\n".join(
                [
                    "## BLOCKERS",
                    "## Implementation Plan (Lite)",
                    "## OBPI Completion Evidence",
                    "## Work Breakdown Structure Context",
                    "Each brief targets exactly one OBPI entry",
                    "",
                ]
            )
        )
        Path("docs/design/prd").mkdir(parents=True, exist_ok=True)
        Path("docs/design/prd/PRD-GZKIT-1.0.0.md").write_text("# PRD\n")
        Path("tests").mkdir(parents=True, exist_ok=True)
        Path("tests/test_cli.py").write_text("import unittest\n")
        Path("tests/test_sync.py").write_text("import unittest\n")
        # Eval suite surfaces: synced instruction → rule pair
        Path(".github/instructions").mkdir(parents=True, exist_ok=True)
        body = "# Governance Core\n\nRules here."
        Path(".github/instructions/governance_core.instructions.md").write_text(
            '---\napplyTo: "**/*"\n---\n\n' + body
        )
        Path(".claude/rules").mkdir(parents=True, exist_ok=True)
        Path(".claude/rules/governance_core.md").write_text(body)

    def test_check_config_paths_passes_for_valid_layout(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            Path("src").mkdir(exist_ok=True)
            Path("tests").mkdir(exist_ok=True)
            Path("docs").mkdir(exist_ok=True)
            Path(".github/instructions").mkdir(parents=True, exist_ok=True)
            Path(".claude/rules").mkdir(parents=True, exist_ok=True)
            Path(".gzkit/rules").mkdir(parents=True, exist_ok=True)
            Path(".gzkit/schemas").mkdir(parents=True, exist_ok=True)
            Path(".gzkit/personas").mkdir(parents=True, exist_ok=True)
            result = runner.invoke(main, ["check-config-paths"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_check_config_paths_detects_missing_path(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            Path("src").mkdir(exist_ok=True)
            Path("tests").mkdir(exist_ok=True)
            Path("docs").mkdir(exist_ok=True)
            # Break a required path.
            skill_dir = Path(".github/skills")
            if skill_dir.exists():
                for path in sorted(skill_dir.glob("**/*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
                skill_dir.rmdir()
            result = runner.invoke(main, ["check-config-paths"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("failed", result.output.lower())

    def test_check_config_paths_rejects_legacy_global_obpi_path(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            config_path = Path(".gzkit.json")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["paths"]["obpis"] = "design/obpis"
            config_path.write_text(json.dumps(config, indent=2) + "\n")
            Path("design/obpis").mkdir(parents=True, exist_ok=True)

            result = runner.invoke(main, ["check-config-paths"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("deprecated global obpi path", result.output.lower())

    def test_check_config_paths_rejects_legacy_global_obpi_files(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            legacy_file = Path("design/obpis/OBPI-0.1.0-01-legacy.md")
            legacy_file.parent.mkdir(parents=True, exist_ok=True)
            legacy_file.write_text("# legacy\n")

            result = runner.invoke(main, ["check-config-paths"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("legacy global obpi directory contains obpi files", result.output.lower())

    def test_cli_audit_passes_with_synchronized_docs(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_docs_surface()
            result = runner.invoke(main, ["cli", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_cli_audit_detects_mismatch(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_docs_surface()
            # Corrupt one heading to trigger mismatch.
            doc_rel = manpage_path_for("closeout")
            Path(doc_rel).write_text("# wrong heading\n")
            result = runner.invoke(main, ["cli", "audit"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("failed", result.output.lower())

    def test_cli_audit_detects_invalid_readme_quickstart_command(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_docs_surface()
            Path("README.md").write_text(
                "\n".join(
                    [
                        "# Example Project",
                        "",
                        "## Quick Start",
                        "",
                        "```bash",
                        "gz init",
                        "gz verify",
                        "```",
                        "",
                    ]
                )
            )
            result = runner.invoke(main, ["cli", "audit"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("invalid quick start command", result.output.lower())

    def test_parity_check_passes_when_contract_surfaces_are_present(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_parity_surface()
            result = runner.invoke(main, ["parity", "check"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_parity_check_fails_when_discovery_index_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_parity_surface()
            Path(".github/discovery-index.json").unlink()
            result = runner.invoke(main, ["parity", "check"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("required parity surface missing", result.output.lower())

    def test_readiness_audit_passes_for_initialized_repository(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_docs_surface()
            self._prepare_parity_surface()
            self._prepare_readiness_surface()
            result = runner.invoke(main, ["readiness", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_readiness_audit_fails_when_required_surface_missing(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            runner.invoke(main, ["init"])
            self._prepare_docs_surface()
            self._prepare_parity_surface()
            self._prepare_readiness_surface()
            Path(".github/discovery-index.json").unlink()
            result = runner.invoke(main, ["readiness", "audit"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("required control surface", result.output.lower())
