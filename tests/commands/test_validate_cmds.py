import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event, obpi_created_event
from gzkit.traceability import covers
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
""",
                encoding="utf-8",
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

    def test_validate_decomposition_skips_validated_legacy_adr_shape(self) -> None:
        """Validated ADRs keep authoring-era decomposition shape under GHI #480."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_dir = Path("docs/design/adr/foundation/ADR-0.0.98-legacy")
            adr_dir.mkdir(parents=True, exist_ok=True)
            adr_content = """---
id: ADR-0.0.98-legacy
status: Validated
semver: 0.0.98
lane: heavy
kind: foundation
parent: PRD-TEST-1.0.0
date: 2026-01-01
---

# ADR-0.0.98: Legacy

## Feature Checklist

- [x] OBPI-0.0.98-01: Historical item
"""
            (adr_dir / "ADR-0.0.98-legacy.md").write_text(adr_content, encoding="utf-8")

            result = runner.invoke(main, ["validate", "--decomposition"])

            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_validate_decomposition_draft_adr_still_requires_scorecard(self) -> None:
        """Draft ADRs remain fail-closed for missing decomposition scorecards."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            adr_dir = Path("docs/design/adr/foundation/ADR-0.0.98-draft")
            adr_dir.mkdir(parents=True, exist_ok=True)
            adr_content = """---
id: ADR-0.0.98-draft
status: Draft
semver: 0.0.98
lane: heavy
kind: foundation
parent: PRD-TEST-1.0.0
date: 2026-01-01
---

# ADR-0.0.98: Draft

## Feature Checklist

- [ ] OBPI-0.0.98-01: Planned item
"""
            (adr_dir / "ADR-0.0.98-draft.md").write_text(adr_content, encoding="utf-8")

            result = runner.invoke(main, ["validate", "--decomposition"])

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Missing required section: 'Decomposition Scorecard'", result.output)

    def test_validate_interviews_flag_accepted(self) -> None:
        """--interviews flag is accepted and runs the interviews scope."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["validate", "--interviews"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("interviews", result.output.lower())

    def test_validate_interviews_detects_missing_qa_transcript(self) -> None:
        """An ADR with OBPI briefs but no '## Q&A Transcript' section is flagged.

        The interviews scope verifies the design-conversation receipt lives in
        the ADR body as a ``## Q&A Transcript`` section (GHI #511 retarget).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpi_dir = Path("docs/design/adr/foundation/ADR-0.0.99-test/obpis")
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (obpi_dir / "OBPI-0.0.99-01-thing.md").write_text(
                "# OBPI-0.0.99-01\n", encoding="utf-8"
            )
            (obpi_dir.parent / "ADR-0.0.99-test.md").write_text(
                "# ADR-0.0.99 Test\n\n## Decision\n\nDo the thing.\n", encoding="utf-8"
            )
            result = runner.invoke(main, ["validate", "--interviews"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Q&A Transcript", result.output)

    def test_validate_interviews_passes_with_embedded_qa_transcript(self) -> None:
        """An ADR carrying a '## Q&A Transcript' section passes the scope."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpi_dir = Path("docs/design/adr/foundation/ADR-0.0.99-test/obpis")
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (obpi_dir / "OBPI-0.0.99-01-thing.md").write_text(
                "# OBPI-0.0.99-01\n", encoding="utf-8"
            )
            (obpi_dir.parent / "ADR-0.0.99-test.md").write_text(
                "# ADR-0.0.99 Test\n\n## Q&A Transcript\n\nQ: why? A: because.\n",
                encoding="utf-8",
            )
            result = runner.invoke(main, ["validate", "--interviews"])
            self.assertEqual(result.exit_code, 0)

    def test_validate_interviews_skips_waived_adr(self) -> None:
        """An ADR listed in interview_transcript_waivers.json is exempt.

        Pre-convention ADRs whose design conversation was never recorded are
        waived from the embedded ``## Q&A Transcript`` check (GHI #515): the
        validator skips any ADR ID present in the sidecar waiver registry
        rather than flagging a transcript that cannot be honestly produced.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpi_dir = Path("docs/design/adr/foundation/ADR-0.0.99-test/obpis")
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (obpi_dir / "OBPI-0.0.99-01-thing.md").write_text(
                "# OBPI-0.0.99-01\n", encoding="utf-8"
            )
            # ADR carries OBPI briefs but no '## Q&A Transcript' section.
            (obpi_dir.parent / "ADR-0.0.99-test.md").write_text(
                "# ADR-0.0.99 Test\n\n## Decision\n\nDo the thing.\n",
                encoding="utf-8",
            )
            Path("data").mkdir(exist_ok=True)
            Path("data/interview_transcript_waivers.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "default_rationale": {"pre-convention": "Predates the convention."},
                        "waivers": {"ADR-0.0.99": {"rationale": "pre-convention"}},
                    }
                ),
                encoding="utf-8",
            )
            result = runner.invoke(main, ["validate", "--interviews"])
            self.assertEqual(result.exit_code, 0)

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

    def test_validate_commit_trailers_rejects_ceremony_alone_for_src(self) -> None:
        """src/tests commits with only Ceremony: trailer are REJECTED (GHI #552 strict mode).

        Pre-GHI-#552 the OR-permissive rule allowed Ceremony: as a substitute for
        Task: on src/tests scope. That was the doctrinal escape valve that
        silently abandoned TASK discipline (3 Task: vs. 305+ Ceremony: in 30 days).
        Strict mode: src/tests requires Task:. Ceremony: stays valid for
        non-src/tests scope (docs/, .gzkit/, ledger reconciles).
        """
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
                [
                    "git",
                    "commit",
                    "-m",
                    "chore: update src/mypkg (gz git-sync)\n\nCeremony: gz-git-sync",
                ],
                cwd=project_root,
                check=True,
                capture_output=True,
            )
            result = runner.invoke(main, ["validate", "--commit-trailers"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Task:", result.output)

    def test_validate_commit_trailers_accepts_slug_form_task_trailer(self) -> None:
        """src/tests commits with slug-form ``Task: TASK-<slug>-#<ghi>`` pass (GHI #552).

        Direct-fix work outside OBPI scope cannot mint a formal
        TASK-X.Y.Z-NN-MM-PP id (no parent OBPI), so the slug form is the
        canonical convention (per GHI #160 Phase 7 backfill).
        """
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
                [
                    "git",
                    "commit",
                    "-m",
                    (
                        "fix(validator): tighten trailer rule\n\n"
                        "Task: TASK-task-spine-restoration-#552"
                    ),
                ],
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

    def test_validate_briefs_tolerates_legacy_noncompleted_brief_shape(self) -> None:
        """--briefs uses lifecycle-aware validation, not raw current schema on legacy drafts."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpi_dir = Path("docs/design/adr/pre-release/ADR-0.0.99-test/obpis")
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (obpi_dir / "OBPI-0.0.99-01-legacy.md").write_text(
                """---
id: OBPI-0.0.99-01
parent: ADR-0.0.99-test
status: Pending
lane: Lite
---

# OBPI-0.0.99-01 - Legacy

## Acceptance Criteria

- [ ] Legacy criterion written before the authored-brief schema.
""",
                encoding="utf-8",
            )

            result = runner.invoke(main, ["validate", "--briefs"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_validate_briefs_does_not_require_live_scope_for_completed_history(self) -> None:
        """--briefs is static corpus hygiene, not completion-readiness validation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            obpi_dir = Path("docs/design/adr/pre-release/ADR-0.0.99-test/obpis")
            obpi_dir.mkdir(parents=True, exist_ok=True)
            (obpi_dir / "OBPI-0.0.99-01-completed.md").write_text(
                """---
id: OBPI-0.0.99-01
parent: ADR-0.0.99-test
status: Completed
lane: Lite
---

# OBPI-0.0.99-01 - Completed History

## Implementation Summary

Historical completion evidence.

## Key Proof

Historical proof.
""",
                encoding="utf-8",
            )

            result = runner.invoke(main, ["validate", "--briefs"])
            self.assertEqual(result.exit_code, 0, msg=result.output)


class TestValidateScopeResolution(unittest.TestCase):
    """The rendered scope list must match the checks that actually ran."""

    def test_default_validate_scope_list_includes_frontmatter(self) -> None:
        from gzkit.commands.validate_cmd import _resolve_scopes

        self.assertIn("frontmatter", _resolve_scopes({}))

    def test_frontmatter_flag_resolves_to_frontmatter_only(self) -> None:
        from gzkit.commands.validate_cmd import _resolve_scopes

        self.assertEqual(["frontmatter"], _resolve_scopes({"frontmatter": True}))

    def test_distribution_flag_resolves_to_distribution_only(self) -> None:
        from gzkit.commands.validate_cmd import _resolve_scopes

        self.assertEqual(["distribution"], _resolve_scopes({"distribution": True}))

    def test_closeout_proof_flag_resolves_to_closeout_proof_only(self) -> None:
        # ADR-0.0.69: --closeout-proof is an opt-in scope. A closeout-proof-only
        # run must report exactly that scope in the summary — not silently fall
        # back to the default run_all set (which would misreport ten scopes that
        # never ran and never name the one that did).
        from gzkit.commands.validate_cmd import _resolve_scopes

        self.assertEqual(["closeout_proof"], _resolve_scopes({"closeout_proof": True}))


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


class TestValidateTaxonomyFlag(unittest.TestCase):
    """Dispatch tests for `gz validate --taxonomy` (REQ-0.0.17-04-08)."""

    def _write_adr(self, rel: str, frontmatter: dict[str, str]) -> None:
        path = Path(rel)
        path.parent.mkdir(parents=True, exist_ok=True)
        lines = ["---"]
        for key, value in frontmatter.items():
            lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")
        lines.append("# Stub")
        path.write_text("\n".join(lines), encoding="utf-8")

    @covers("REQ-0.0.17-04-08")
    @covers("REQ-0.0.17-05-07")
    def test_validate_taxonomy_flag_clean_on_empty_tree(self) -> None:
        """--taxonomy exits 0 when no non-pool ADRs are present.

        Also pins REQ-0.0.17-05-07 (post-backfill, `gz validate --taxonomy`
        exits 0 against the canonical tree) — the semantic is the same.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["validate", "--taxonomy"])
            self.assertEqual(result.exit_code, 0)
            self.assertIn("taxonomy", result.output.lower())

    @covers("REQ-0.0.17-04-08")
    def test_validate_taxonomy_detects_missing_kind(self) -> None:
        """--taxonomy flags a non-pool ADR without the kind field."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            self._write_adr(
                "docs/design/adr/foundation/ADR-0.0.99-example/ADR-0.0.99-example.md",
                {"id": "ADR-0.0.99", "semver": "0.0.99"},
            )
            result = runner.invoke(main, ["validate", "--taxonomy"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("taxonomy", result.output.lower())
            self.assertIn("missing `kind:`", result.output)

    @covers("REQ-0.0.17-04-08")
    def test_validate_taxonomy_detects_pool_kind_frontmatter(self) -> None:
        """--taxonomy flags a pool ADR that carries a kind field."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            self._write_adr(
                "docs/design/adr/pool/ADR-pool.example.md",
                {"id": "ADR-pool.example", "kind": "foundation"},
            )
            result = runner.invoke(main, ["validate", "--taxonomy"])
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs derive kind", result.output)


_MANIFEST_WITH_ADR_ARTIFACT = {
    "schema": "gzkit.manifest.v2",
    "structure": {
        "source_root": "src",
        "tests_root": "tests",
        "docs_root": "docs",
        "design_root": "docs/design",
    },
    "artifacts": {
        "adr": {"path": "docs/design/adr", "schema": "gzkit.adr.v1"},
    },
    "data": {},
    "ops": {},
    "thresholds": {},
    "control_surfaces": {},
    "verification": {},
    "gates": {},
    "rules": {},
}

_BARE_ID_ADR_FRONTMATTER = """\
---
id: ADR-0.0.43
status: Draft
kind: foundation
semver: 0.0.43
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-11
---
# ADR-0.0.43: DDD Domain Cascade
"""

_SLUG_ID_ADR_FRONTMATTER = """\
---
id: ADR-0.0.43-ddd-domain-cascade
status: Draft
kind: foundation
semver: 0.0.43
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-11
---
# ADR-0.0.43-ddd-domain-cascade: DDD Domain Cascade
"""


class TestValidateDocumentsNestedIteration(unittest.TestCase):
    """REQ-468-01: validate --documents must reach nested ADR packages.

    GHI #346 Reach Caveat: non-recursive glob skipped foundation/pre-release
    ADR packages. Bare-id frontmatter in a nested package must fail-close.
    """

    def _write_manifest(self, root: Path) -> None:
        gzkit_dir = root / ".gzkit"
        gzkit_dir.mkdir(parents=True, exist_ok=True)
        (gzkit_dir / "manifest.json").write_text(
            json.dumps(_MANIFEST_WITH_ADR_ARTIFACT), encoding="utf-8"
        )

    def _write_nested_adr(self, root: Path, content: str) -> Path:
        pkg_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.43-ddd-domain-cascade"
        pkg_dir.mkdir(parents=True)
        path = pkg_dir / "ADR-0.0.43-ddd-domain-cascade.md"
        path.write_text(content, encoding="utf-8")
        return path

    def test_bare_id_in_nested_package_fails_closed(self) -> None:
        """Bare-id frontmatter in a nested ADR package must produce a frontmatter id error."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            self._write_nested_adr(root, _BARE_ID_ADR_FRONTMATTER)
            errors = _validate_manifest_documents(root)
            id_errors = [e for e in errors if e.type == "frontmatter" and e.field == "id"]
            self.assertGreater(
                len(id_errors),
                0,
                msg=(
                    "Expected frontmatter id error for bare-id ADR in nested package;"
                    " got none (GHI #468)"
                ),
            )

    def test_slug_id_in_nested_package_produces_no_id_error(self) -> None:
        """Slug-suffixed ADR in nested package must not raise an id frontmatter error."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            self._write_nested_adr(root, _SLUG_ID_ADR_FRONTMATTER)
            errors = _validate_manifest_documents(root)
            id_errors = [e for e in errors if e.type == "frontmatter" and e.field == "id"]
            self.assertEqual(
                id_errors,
                [],
                msg=f"Expected no id errors for slug-id ADR; got {id_errors}",
            )


_MANIFEST_WITH_OBPI_AND_ADR = {
    "schema": "gzkit.manifest.v2",
    "structure": {
        "source_root": "src",
        "tests_root": "tests",
        "docs_root": "docs",
        "design_root": "docs/design",
    },
    "artifacts": {
        "obpi": {"path": "docs/design/adr", "schema": "gzkit.obpi.v1"},
        "adr": {"path": "docs/design/adr", "schema": "gzkit.adr.v1"},
    },
    "data": {},
    "ops": {},
    "thresholds": {},
    "control_surfaces": {},
    "verification": {},
    "gates": {},
    "rules": {},
}

_HISTORICAL_OBPI_BRIEF = """\
---
id: OBPI-0.0.99-01-historical-thing
parent: ADR-0.0.99
item: 1
lane: lite
status: Completed
---
# OBPI-0.0.99-01 — Historical Thing

This attested-completed brief predates the current authored-brief schema and
carries none of the required `## Lane` / `## Allowed Paths` / `## Denied Paths`
/ `## Requirements (FAIL-CLOSED)` / `## Quality Gates` sections.
"""


class TestValidateDocumentsSkipsObpiCorpus(unittest.TestCase):
    """REQ-500-01: documents scope must not raw-schema-validate OBPI briefs.

    GHI #500: the `documents` scope treated every OBPI brief as a
    newly-authored document and produced thousands of non-actionable
    schema-section failures against the historical corpus. OBPI corpus
    hygiene is owned by the version-aware `briefs` scope; strict authored
    checks by `gz obpi validate --authored`.
    """

    def _write_manifest(self, root: Path) -> None:
        gzkit_dir = root / ".gzkit"
        gzkit_dir.mkdir(parents=True, exist_ok=True)
        (gzkit_dir / "manifest.json").write_text(
            json.dumps(_MANIFEST_WITH_OBPI_AND_ADR), encoding="utf-8"
        )

    def test_historical_obpi_brief_produces_no_documents_errors(self) -> None:
        """A schema-incomplete historical OBPI brief must raise no documents-scope errors."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            obpi_dir = root / "docs" / "design" / "adr" / "pre-release" / "ADR-0.0.99-x" / "obpis"
            obpi_dir.mkdir(parents=True)
            (obpi_dir / "OBPI-0.0.99-01-historical-thing.md").write_text(
                _HISTORICAL_OBPI_BRIEF, encoding="utf-8"
            )
            errors = _validate_manifest_documents(root)
            obpi_errors = [e for e in errors if Path(e.artifact).name.startswith("OBPI-")]
            self.assertEqual(
                obpi_errors,
                [],
                msg=f"documents scope must skip OBPI briefs (GHI #500); got {obpi_errors}",
            )

    def test_adr_validation_still_fires(self) -> None:
        """Regression guard: removing OBPI from documents must not stop ADR validation."""
        from gzkit.commands.validate_cmd import _validate_manifest_documents

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root)
            pkg_dir = root / "docs" / "design" / "adr" / "foundation" / "ADR-0.0.43-ddd"
            pkg_dir.mkdir(parents=True)
            (pkg_dir / "ADR-0.0.43-ddd.md").write_text(_BARE_ID_ADR_FRONTMATTER, encoding="utf-8")
            errors = _validate_manifest_documents(root)
            id_errors = [e for e in errors if e.type == "frontmatter" and e.field == "id"]
            self.assertGreater(
                len(id_errors),
                0,
                msg="ADR frontmatter validation must still fire in the documents scope",
            )
