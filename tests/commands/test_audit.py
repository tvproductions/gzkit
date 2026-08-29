import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.doc_coverage.manifest import manpage_path_for
from tests.commands.common import (
    CliRunner,
    start_init_subprocess_patches,
    stop_init_subprocess_patches,
)

_REAL_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Module-level cache: one ``gz init`` shared across tests via copytree
# (GHI #253).
_TEMPLATE_CTX: tempfile.TemporaryDirectory | None = None
_TEMPLATE_DIR: Path | None = None


def setUpModule() -> None:
    """Stub init subprocesses and build the shared init'd template."""
    global _TEMPLATE_CTX, _TEMPLATE_DIR
    start_init_subprocess_patches()
    _TEMPLATE_CTX = tempfile.TemporaryDirectory(prefix="gzkit-audit-tpl-")
    _TEMPLATE_DIR = Path(_TEMPLATE_CTX.name) / "project"
    _TEMPLATE_DIR.mkdir()
    orig = Path.cwd()
    os.chdir(_TEMPLATE_DIR)
    try:
        CliRunner().invoke(main, ["init"])
    finally:
        os.chdir(orig)


def tearDownModule() -> None:
    global _TEMPLATE_CTX, _TEMPLATE_DIR
    if _TEMPLATE_CTX is not None:
        _TEMPLATE_CTX.cleanup()
    _TEMPLATE_CTX = None
    _TEMPLATE_DIR = None
    stop_init_subprocess_patches()


class _InitFromTemplate:
    """Context manager: copytree cached init'd tree into a fresh tempdir."""

    def __enter__(self) -> None:
        assert _TEMPLATE_DIR is not None
        self._tmpctx = tempfile.TemporaryDirectory(prefix="gzkit-audit-test-")
        dest = Path(self._tmpctx.name) / "project"
        shutil.copytree(_TEMPLATE_DIR, dest)
        self._orig_cwd = Path.cwd()
        os.chdir(dest)

    def __exit__(self, *exc: object) -> None:
        os.chdir(self._orig_cwd)
        self._tmpctx.cleanup()


class TestConfigAndCliAuditCommands(unittest.TestCase):
    """Tests for check-config-paths and cli audit commands."""

    @staticmethod
    def _prepare_docs_surface() -> None:
        # Copy the real manifest so load_manifest() works in the isolated fs.
        src = _REAL_PROJECT_ROOT / "config" / "doc-coverage.json"
        dst = Path("config") / "doc-coverage.json"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

        from gzkit.doc_coverage.flag_scanner import scan_command_flags
        from gzkit.doc_coverage.manifest import load_manifest

        flags_by_command = scan_command_flags(_REAL_PROJECT_ROOT)
        index_path = Path("docs/user/manpages/index.md")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = load_manifest(Path("."))
        links: list[str] = []
        for command_name, entry in manifest.commands.items():
            if not entry.surfaces.manpage:
                continue
            doc_rel = manpage_path_for(command_name)
            doc_path = Path(doc_rel)
            doc_path.parent.mkdir(parents=True, exist_ok=True)
            flag_line = " ".join(flags_by_command.get(command_name, []))
            stub = f"# gz {command_name}\n\nStub\n"
            if flag_line:
                stub += f"\nFlags: {flag_line}\n"
            doc_path.write_text(stub, encoding="utf-8")
            links.append(f"- [`gz {command_name}`]({doc_path.name})")
        index_path.write_text("# Commands Index\n\n" + "\n".join(links) + "\n", encoding="utf-8")
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
            ),
            encoding="utf-8",
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
            + "\n",
            encoding="utf-8",
        )
        Path("docs/governance/parity-intake-rubric.md").parent.mkdir(parents=True, exist_ok=True)
        Path("docs/governance/parity-intake-rubric.md").write_text("# Rubric\n", encoding="utf-8")
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
            ),
            encoding="utf-8",
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
            ),
            encoding="utf-8",
        )
        Path("docs/proposals/REPORT-airlineops-parity-2026-03-01.md").write_text(
            "\n".join(
                [
                    "# REPORT",
                    "Overall parity status: Partial",
                    "## Next Actions",
                    "",
                ]
            ),
            encoding="utf-8",
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
            ),
            encoding="utf-8",
        )
        Path("docs/governance/governance_runbook.md").parent.mkdir(parents=True, exist_ok=True)
        Path("docs/governance/governance_runbook.md").write_text(
            "# Governance Runbook\n", encoding="utf-8"
        )
        Path("docs/user/concepts").mkdir(parents=True, exist_ok=True)
        Path("docs/user/concepts/lanes.md").write_text("# Lanes\n", encoding="utf-8")
        Path("docs/governance/GovZero/audits").mkdir(parents=True, exist_ok=True)
        Path("docs/governance/GovZero/audits/AUDIT-TEMPLATE-agent-readiness.md").write_text(
            "# Agent Readiness Audit\n", encoding="utf-8"
        )
        Path("docs/user/reference").mkdir(parents=True, exist_ok=True)
        Path("docs/user/reference/agent-input-disciplines.md").write_text(
            "# Agent Input Disciplines\n", encoding="utf-8"
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
            ),
            encoding="utf-8",
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
            ),
            encoding="utf-8",
        )
        Path("docs/design/prd").mkdir(parents=True, exist_ok=True)
        Path("docs/design/prd/PRD-GZKIT-1.0.0.md").write_text("# PRD\n", encoding="utf-8")
        Path("tests").mkdir(parents=True, exist_ok=True)
        Path("tests/test_cli.py").write_text("import unittest\n", encoding="utf-8")
        Path("tests/test_sync.py").write_text("import unittest\n", encoding="utf-8")
        # Eval suite surfaces: a synced instruction → rule pair. The name must
        # not collide with a rule gz init actually scaffolds -- this pair was
        # called governance_core until 2026-08-28, and once init began leaving a
        # synced tree (GHI #908) the real .claude/rules/governance-core.md landed
        # beside it. The drift audit accepts underscore and hyphen spellings as
        # the same rule, so the stub body was compared against the real one and
        # reported drift that neither file had.
        Path(".github/instructions").mkdir(parents=True, exist_ok=True)
        body = "# Fixture Sync Pair\n\nRules here."
        Path(".github/instructions/fixture_sync_pair.instructions.md").write_text(
            '---\napplyTo: "**/*"\n---\n\n' + body, encoding="utf-8"
        )
        Path(".claude/rules").mkdir(parents=True, exist_ok=True)
        Path(".claude/rules/fixture_sync_pair.md").write_text(body, encoding="utf-8")

        TestConfigAndCliAuditCommands._seed_rule_scope_paths()

    # Paths named by applyTo globs that a BRAND-NEW project has not populated
    # yet -- no ADRs authored, no changelog written, no handoff recorded. These
    # are adopter-real; they are empty, not unsatisfiable, and the reachability
    # audit does not distinguish the two.
    #
    # This list carried 16 more entries until GHI #911 landed the delivery-time
    # path classifier. Those named gzkit's OWN source tree (`src/gzkit/**`,
    # `scripts/`, `data/`), which an adopter can never have and which is why the
    # rules no longer deliver them. Their removal here is the end-to-end witness
    # that the classifier works: the fixture stops compensating for a leak.
    _RULE_SCOPE_PATHS = (
        "CHANGELOG.md",
        "RELEASE_NOTES.md",
        "docs/design/adr/ADR-0.0.0-fixture/obpis/OBPI-0.0.0-01-fixture.md",
        "docs/governance/complexity/fixture.md",
        ".claude/agents/fixture.md",
        ".gzkit/handoffs/fixture.md",
        ".gzkit/locks/exchange/fixture.md",
    )

    @staticmethod
    def _seed_rule_scope_paths() -> None:
        """Create one file per applyTo glob the scaffolded rules declare."""
        for relative in TestConfigAndCliAuditCommands._RULE_SCOPE_PATHS:
            target = Path(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text("", encoding="utf-8")

    def test_check_config_paths_passes_for_valid_layout(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
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
        with _InitFromTemplate():
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
        with _InitFromTemplate():
            config_path = Path(".gzkit.json")
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["paths"]["obpis"] = "design/obpis"
            config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
            Path("design/obpis").mkdir(parents=True, exist_ok=True)

            result = runner.invoke(main, ["check-config-paths"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("deprecated global obpi path", result.output.lower())

    def test_check_config_paths_rejects_legacy_global_obpi_files(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
            legacy_file = Path("design/obpis/OBPI-0.1.0-01-legacy.md")
            legacy_file.parent.mkdir(parents=True, exist_ok=True)
            legacy_file.write_text("# legacy\n", encoding="utf-8")

            result = runner.invoke(main, ["check-config-paths"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("legacy global obpi directory contains obpi files", result.output.lower())

    def test_cli_audit_passes_with_synchronized_docs(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
            self._prepare_docs_surface()
            result = runner.invoke(main, ["cli", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_cli_audit_detects_mismatch(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
            self._prepare_docs_surface()
            # Corrupt one heading to trigger mismatch.
            doc_rel = manpage_path_for("closeout")
            Path(doc_rel).write_text("# wrong heading\n", encoding="utf-8")
            result = runner.invoke(main, ["cli", "audit"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("failed", result.output.lower())

    def test_cli_audit_detects_invalid_readme_quickstart_command(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
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
                ),
                encoding="utf-8",
            )
            result = runner.invoke(main, ["cli", "audit"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("invalid quick start command", result.output.lower())

    def test_parity_check_passes_when_contract_surfaces_are_present(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
            self._prepare_parity_surface()
            result = runner.invoke(main, ["parity", "check"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_parity_check_fails_when_discovery_index_missing(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
            self._prepare_parity_surface()
            Path(".github/discovery-index.json").unlink()
            result = runner.invoke(main, ["parity", "check"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("required parity surface missing", result.output.lower())

    def test_readiness_audit_passes_for_initialized_repository(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
            self._prepare_docs_surface()
            self._prepare_parity_surface()
            self._prepare_readiness_surface()
            result = runner.invoke(main, ["readiness", "audit"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("passed", result.output.lower())

    def test_readiness_audit_fails_when_required_surface_missing(self) -> None:
        runner = CliRunner()
        with _InitFromTemplate():
            self._prepare_docs_surface()
            self._prepare_parity_surface()
            self._prepare_readiness_surface()
            Path(".github/discovery-index.json").unlink()
            result = runner.invoke(main, ["readiness", "audit"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("required control surface", result.output.lower())
