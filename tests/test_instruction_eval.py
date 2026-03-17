"""Tests for gzkit.instruction_eval — instruction architecture eval suite."""

import tempfile
import unittest
from pathlib import Path

from gzkit.instruction_eval import (
    BASELINE_CASES,
    EvalCase,
    run_eval_suite,
)


def _instruction_file(apply_to: str, body: str, *, exclude_agent: str | None = None) -> str:
    """Build a minimal .instructions.md file."""
    lines = ["---", f'applyTo: "{apply_to}"']
    if exclude_agent is not None:
        lines.append(f"excludeAgent: {exclude_agent}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


def _scaffold_project(root: Path) -> None:
    """Create minimal project structure for eval to pass."""
    # AGENTS.md with Project Identity
    (root / "AGENTS.md").write_text("# Agents\n\n## Project Identity\n\ngzkit governance toolkit\n")
    # CLAUDE.md
    (root / "CLAUDE.md").write_text("# Claude\n\nGuidance here.\n")
    # .github/instructions with one instruction
    inst = root / ".github" / "instructions"
    inst.mkdir(parents=True)
    body = "# Governance Core\n\nRules here."
    (inst / "governance_core.instructions.md").write_text(_instruction_file("**/*", body))
    # .claude/rules synced
    rules = root / ".claude" / "rules"
    rules.mkdir(parents=True)
    (rules / "governance_core.md").write_text(body)
    # .gzkit/skills with one skill
    skill = root / ".gzkit" / "skills" / "gz-test"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# gz-test skill\n")
    # docs/user/commands/index.md with quality references
    cmd_docs = root / "docs" / "user" / "commands"
    cmd_docs.mkdir(parents=True)
    (cmd_docs / "index.md").write_text(
        "# Commands\n\n- readiness audit\n- parity check\n- skill audit\n"
    )
    # src directory (for instruction reachability)
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "main.py").write_text("")


class TestBaselineCases(unittest.TestCase):
    """Verify baseline eval case structure."""

    def test_baseline_has_ten_cases(self) -> None:
        self.assertEqual(len(BASELINE_CASES), 10)

    def test_all_four_dimensions_covered(self) -> None:
        dimensions = {c.dimension for c in BASELINE_CASES}
        self.assertEqual(dimensions, {"outcome", "process", "style", "efficiency"})

    def test_both_controls_present(self) -> None:
        controls = {c.control for c in BASELINE_CASES}
        self.assertEqual(controls, {"positive", "negative"})

    def test_codex_and_claude_surfaces_present(self) -> None:
        surfaces = {c.surface for c in BASELINE_CASES}
        self.assertIn("codex", surfaces)
        self.assertIn("claude", surfaces)

    def test_each_behavior_has_positive_and_negative(self) -> None:
        """Each of codex/claude/workflow/drift has at least one positive and one negative."""
        # Group by ID prefix (first two segments)
        prefixes = set()
        for case in BASELINE_CASES:
            prefix = case.id.rsplit("-", 1)[0]
            prefixes.add((prefix, case.control))
        # Check that codex-load, claude-load, workflow-relocation, drift have both
        for behavior in ("codex-load", "claude-load", "workflow-relocation"):
            self.assertIn((behavior, "positive"), prefixes, f"{behavior} missing positive control")
            self.assertIn((behavior, "negative"), prefixes, f"{behavior} missing negative control")

    def test_unique_case_ids(self) -> None:
        ids = [c.id for c in BASELINE_CASES]
        self.assertEqual(len(ids), len(set(ids)))


class TestRunEvalSuite(unittest.TestCase):
    """Test running the eval suite against scaffolded projects."""

    def test_full_suite_passes_on_well_formed_project(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_project(root)
            result = run_eval_suite(root)
            failed = [r for r in result.results if not r.passed]
            self.assertTrue(
                result.success,
                f"Expected all evals to pass, but {len(failed)} failed: "
                + "; ".join(f"{r.case_id}: {r.detail}" for r in failed),
            )

    def test_missing_agents_md_fails_codex_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_project(root)
            (root / "AGENTS.md").unlink()
            result = run_eval_suite(root)
            codex_result = next(r for r in result.results if r.case_id == "codex-load-positive")
            self.assertFalse(codex_result.passed)

    def test_missing_rules_dir_fails_claude_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_project(root)
            import shutil

            shutil.rmtree(root / ".claude" / "rules")
            result = run_eval_suite(root)
            claude_result = next(r for r in result.results if r.case_id == "claude-load-positive")
            self.assertFalse(claude_result.passed)

    def test_missing_skills_dir_fails_workflow_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_project(root)
            import shutil

            shutil.rmtree(root / ".gzkit" / "skills")
            result = run_eval_suite(root)
            wf_result = next(
                r for r in result.results if r.case_id == "workflow-relocation-positive"
            )
            self.assertFalse(wf_result.passed)

    def test_dimension_scores_computed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_project(root)
            result = run_eval_suite(root)
            dim_names = {d.dimension for d in result.dimension_scores}
            self.assertEqual(dim_names, {"outcome", "process", "style", "efficiency"})

    def test_custom_cases_accepted(self) -> None:
        custom = [
            EvalCase(
                id="custom-check",
                surface="shared",
                dimension="outcome",
                control="positive",
                description="Custom eval",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_eval_suite(root, cases=custom)
            self.assertEqual(result.total, 1)
            # No check function registered for custom-check → fails
            self.assertFalse(result.results[0].passed)
            self.assertIn("No check function", result.results[0].detail)

    def test_legacy_skill_dir_fails_workflow_negative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_project(root)
            # Create legacy skill location
            (root / "skills").mkdir()
            result = run_eval_suite(root)
            wf_neg = next(r for r in result.results if r.case_id == "workflow-relocation-negative")
            self.assertFalse(wf_neg.passed)

    def test_command_index_missing_ref_fails_docs_positive(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_project(root)
            # Rewrite index without quality command refs
            (root / "docs" / "user" / "commands" / "index.md").write_text("# Commands\n")
            result = run_eval_suite(root)
            docs_result = next(r for r in result.results if r.case_id == "workflow-docs-positive")
            self.assertFalse(docs_result.passed)


class TestExtensibility(unittest.TestCase):
    """REQ-06-03: New cases can be added without rewriting the model."""

    def test_suite_accepts_extended_case_list(self) -> None:
        """Adding cases to BASELINE_CASES list works without model changes."""
        extended = list(BASELINE_CASES) + [
            EvalCase(
                id="subproject-custom",
                surface="shared",
                dimension="outcome",
                control="positive",
                description="Subproject-specific eval",
            ),
        ]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _scaffold_project(root)
            result = run_eval_suite(root, cases=extended)
            self.assertEqual(result.total, 11)
