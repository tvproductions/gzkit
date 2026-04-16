import subprocess
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event, obpi_created_event
from tests.commands.common import CliRunner, _init_git_repo, _quick_init


class TestValidateCommand(unittest.TestCase):
    """Tests for gz validate command."""

    def test_validate_after_init(self) -> None:
        """validate passes after init (with surface errors expected)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            # Create AGENTS.md with required sections
            Path("AGENTS.md").write_text(
                """# AGENTS.md

## Project Identity

Test project

## Behavior Rules

Rules here

## Pattern Discovery

Discovery here

## Gate Covenant

Covenant here

## Execution Rules

Rules here
"""
            )
            result = runner.invoke(main, ["validate"])
            # May have some validation issues but should not crash
            self.assertIn("validation", result.output.lower())

    def test_validate_ledger_flag_fails_on_invalid_ledger(self) -> None:
        """--ledger performs strict ledger JSONL validation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with Path(".gzkit/ledger.jsonl").open("a") as ledger_file:
                ledger_file.write("{not-json}\n")

            result = runner.invoke(main, ["validate", "--ledger"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid JSON", result.output)

    def test_validate_all_includes_ledger_checks(self) -> None:
        """Default validate mode includes ledger validation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            with Path(".gzkit/ledger.jsonl").open("a") as ledger_file:
                ledger_file.write("{not-json}\n")

            result = runner.invoke(main, ["validate"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Invalid JSON", result.output)

    def test_validate_decomposition_flag_accepted(self) -> None:
        """--decomposition flag is accepted and runs decomposition scope."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["validate", "--decomposition"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("decomposition", result.output.lower())

    def test_validate_decomposition_detects_count_mismatch(self) -> None:
        """Decomposition validation detects checklist-scorecard mismatch."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_dir = Path("docs/design/adr/foundation/ADR-0.0.99-test")
            adr_dir.mkdir(parents=True, exist_ok=True)
            adr_content = """# ADR-0.0.99 Test

## Feature Checklist

- [ ] First item
- [ ] Second item

## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 1
- Interface: 1
- Observability: 0
- Lineage: 0
- Dimension Total: 3
- Baseline Range: 1-2
- Baseline Selected: 1
- Split Single-Narrative: 0
- Split Testability Ceiling: 0
- Split State Anchor: 0
- Split Surface Boundary: 0
- Split Total: 0
- Final Target OBPI Count: 1
"""
            (adr_dir / "ADR-0.0.99-test.md").write_text(adr_content, encoding="utf-8")
            result = runner.invoke(main, ["validate", "--decomposition"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("does not match", result.output)

    def test_validate_requirements_flag_accepted(self) -> None:
        """--requirements flag runs the requirements scope without crashing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["validate", "--requirements"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("requirements", result.output.lower())

    def test_validate_requirements_detects_bare_requirements_section(self) -> None:
        """OBPI with REQUIREMENTS section but no REQ-IDs is flagged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpi_dir = Path("docs/design/adr/pre-release/ADR-0.0.99-test/obpis")
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (obpi_dir / "OBPI-0.0.99-01-thing.md").write_text(
                """---
id: OBPI-0.0.99-01-thing
parent: ADR-0.0.99-test
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.99-01 — Thing

## OBJECTIVE

Do the thing.

## REQUIREMENTS (FAIL-CLOSED)

1. The thing must happen
2. The thing must be documented
""",
                encoding="utf-8",
            )
            result = runner.invoke(main, ["validate", "--requirements"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("REQ", result.output)
            self.assertIn("OBPI-0.0.99-01-thing", result.output)

    def test_validate_requirements_passes_when_req_ids_present(self) -> None:
        """OBPI with REQUIREMENTS section and at least one REQ-ID passes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpi_dir = Path("docs/design/adr/pre-release/ADR-0.0.99-test/obpis")
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (obpi_dir / "OBPI-0.0.99-01-thing.md").write_text(
                """---
id: OBPI-0.0.99-01-thing
parent: ADR-0.0.99-test
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.99-01 — Thing

## OBJECTIVE

Do the thing.

## REQUIREMENTS (FAIL-CLOSED)

1. The thing must happen

## Acceptance Criteria

- [ ] REQ-0.0.99-01-01: The thing must happen.
""",
                encoding="utf-8",
            )
            result = runner.invoke(main, ["validate", "--requirements"])
            self.assertEqual(result.exit_code, 0)

    def test_validate_commit_trailers_flag_accepted(self) -> None:
        """--commit-trailers flag runs the scope without crashing."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _init_git_repo(Path.cwd())
            result = runner.invoke(main, ["validate", "--commit-trailers"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("commit", result.output.lower())

    def test_validate_commit_trailers_flags_src_change_without_task_trailer(self) -> None:
        """HEAD commit touching src/** without Task: trailer is flagged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            project_root = Path.cwd()
            _init_git_repo(project_root)
            src_file = project_root / "src" / "mypkg" / "module.py"
            src_file.parent.mkdir(parents=True, exist_ok=True)
            src_file.write_text("x = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "src"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "feat: add module"],
                cwd=project_root,
                check=True,
                capture_output=True,
            )
            result = runner.invoke(main, ["validate", "--commit-trailers"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Task:", result.output)

    def test_validate_commit_trailers_passes_with_trailer(self) -> None:
        """HEAD commit with Task: trailer passes the check."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            project_root = Path.cwd()
            _init_git_repo(project_root)
            src_file = project_root / "src" / "mypkg" / "module.py"
            src_file.parent.mkdir(parents=True, exist_ok=True)
            src_file.write_text("x = 1\n", encoding="utf-8")
            subprocess.run(["git", "add", "src"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "feat: add module\n\nTask: TASK-0.0.1-01-01-01"],
                cwd=project_root,
                check=True,
                capture_output=True,
            )
            result = runner.invoke(main, ["validate", "--commit-trailers"])
            self.assertEqual(result.exit_code, 0)

    def test_validate_commit_trailers_skips_non_code_commits(self) -> None:
        """HEAD commit touching only docs/ does not require a Task: trailer."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            project_root = Path.cwd()
            _init_git_repo(project_root)
            docs_file = project_root / "docs" / "note.md"
            docs_file.parent.mkdir(parents=True, exist_ok=True)
            docs_file.write_text("note\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "docs"], cwd=project_root, check=True, capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "docs: add note"],
                cwd=project_root,
                check=True,
                capture_output=True,
            )
            result = runner.invoke(main, ["validate", "--commit-trailers"])
            self.assertEqual(result.exit_code, 0)

    def test_validate_requirements_skips_briefs_without_requirements_section(self) -> None:
        """OBPI with no REQUIREMENTS section at all is not flagged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpi_dir = Path("docs/design/adr/pre-release/ADR-0.0.99-test/obpis")
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (obpi_dir / "OBPI-0.0.99-01-thing.md").write_text(
                """---
id: OBPI-0.0.99-01-thing
parent: ADR-0.0.99-test
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.99-01 — Thing

## OBJECTIVE

Do the thing.
""",
                encoding="utf-8",
            )
            result = runner.invoke(main, ["validate", "--requirements"])
            self.assertEqual(result.exit_code, 0)


class TestFrontmatterCoherence(unittest.TestCase):
    """Tests for gz validate --frontmatter (GHI-167)."""

    def _scaffold_adr(self, project_root: Path, adr_id: str, fm: str) -> None:
        """Create an ADR file with given frontmatter content."""
        config = GzkitConfig.load(project_root / ".gzkit.json")
        adr_dir = project_root / config.paths.design_root / "adr" / "pre-release"
        slug_dir = adr_dir / f"{adr_id}-test"
        slug_dir.mkdir(parents=True, exist_ok=True)
        (slug_dir / f"{adr_id}-test.md").write_text(fm, encoding="utf-8")

    def _scaffold_obpi(self, project_root: Path, adr_id: str, obpi_id: str, fm: str) -> None:
        """Create an OBPI file with given frontmatter content."""
        config = GzkitConfig.load(project_root / ".gzkit.json")
        adr_dir = project_root / config.paths.design_root / "adr" / "pre-release"
        obpi_dir = adr_dir / f"{adr_id}-test" / "obpis"
        obpi_dir.mkdir(parents=True, exist_ok=True)
        (obpi_dir / f"{obpi_id}-test.md").write_text(fm, encoding="utf-8")

    def test_frontmatter_coherent_passes(self) -> None:
        """No errors when frontmatter matches ledger."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            self._scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: lite\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertEqual(result.exit_code, 0)

    def test_lane_drift_detected(self) -> None:
        """Detects lane mismatch between frontmatter and ledger."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            self._scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("lane", result.output)
            self.assertIn("heavy", result.output)
            self.assertIn("lite", result.output)

    def test_parent_drift_detected(self) -> None:
        """Detects parent mismatch between frontmatter and ledger."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            self._scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: ADR-0.0.1\nlane: lite\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("parent", result.output)

    def test_id_drift_detected_for_obpi(self) -> None:
        """Detects id mismatch on OBPI file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            ledger.append(obpi_created_event("OBPI-0.1.0-01-test", "ADR-0.1.0"))
            self._scaffold_obpi(
                root,
                "ADR-0.1.0",
                "OBPI-0.1.0-01",
                "---\nid: OBPI-0.1.0-01-wrong\nparent: ADR-0.1.0\n---\n# OBPI\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("id", result.output)

    def test_json_output_includes_frontmatter_errors(self) -> None:
        """--json mode emits structured frontmatter errors."""
        import json

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            self._scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            result = runner.invoke(main, ["validate", "--frontmatter", "--json"])
            self.assertEqual(result.exit_code, 0)  # --json doesn't raise SystemExit
            payload = json.loads(result.output)
            self.assertFalse(payload["valid"])
            self.assertEqual(len(payload["errors"]), 1)
            self.assertEqual(payload["errors"][0]["type"], "frontmatter")
            self.assertEqual(payload["errors"][0]["field"], "lane")
