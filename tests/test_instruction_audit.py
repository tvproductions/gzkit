"""Tests for gzkit.instruction_audit — instruction audit and drift detection.

@covers ADR-0.17.0  OBPI-0.17.0-02 rules-mirroring
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.instruction_audit import (
    audit_code_contract_mismatches,
    audit_foreign_references,
    audit_generated_surface_drift,
    audit_instruction_reachability,
    audit_instructions,
)
from gzkit.traceability import covers


def _instruction_file(apply_to: str, body: str, *, exclude_agent: str | None = None) -> str:
    """Build a minimal .instructions.md file."""
    lines = ["---", f'applyTo: "{apply_to}"']
    if exclude_agent is not None:
        lines.append(f"excludeAgent: {exclude_agent}")
    lines.append("---")
    lines.append("")
    lines.append(body)
    return "\n".join(lines)


class TestReachability(unittest.TestCase):
    """Test audit_instruction_reachability().

    @covers REQ-0.17.0-02-06
    """

    @covers("REQ-0.17.0-02-06")
    def test_glob_matches_files_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "src.instructions.md").write_text(_instruction_file("src/**", "# Source rules"))
            src = root / "src"
            src.mkdir()
            (src / "main.py").write_text("print('hello')")

            errors = audit_instruction_reachability(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.17.0-02-06")
    def test_glob_matches_nothing_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "missing.instructions.md").write_text(
                _instruction_file("nonexistent/**", "# Missing target")
            )

            errors = audit_instruction_reachability(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("nonexistent/**", errors[0].message)
            self.assertIn("zero files", errors[0].message)

    def test_global_pattern_always_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "global.instructions.md").write_text(_instruction_file("**/*", "# Global rule"))

            errors = audit_instruction_reachability(root)

            self.assertEqual(errors, [])

    def test_no_instructions_dir_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            errors = audit_instruction_reachability(root)

            self.assertEqual(errors, [])

    def test_multi_pattern_flags_only_unreachable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "multi.instructions.md").write_text(
                _instruction_file("src/**,missing/**", "# Multi")
            )
            src = root / "src"
            src.mkdir()
            (src / "app.py").write_text("")

            errors = audit_instruction_reachability(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("missing/**", errors[0].message)


class TestForeignReferences(unittest.TestCase):
    """Test audit_foreign_references()."""

    def test_clean_body_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "clean.instructions.md").write_text(
                _instruction_file("**/*", "# Clean gzkit rules\nNo foreign refs here.")
            )

            errors = audit_foreign_references(root)

            self.assertEqual(errors, [])

    def test_airlineops_detected_in_instruction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "bad.instructions.md").write_text(
                _instruction_file("**/*", "# Rules\nUse airlineops conventions.")
            )

            errors = audit_foreign_references(root)

            self.assertTrue(len(errors) >= 1)
            self.assertIn("airlineops", errors[0].message)

    def test_opsdev_detected_in_instruction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "bad.instructions.md").write_text(
                _instruction_file("**/*", "# Rules\nRun opsdev arb ruff.")
            )

            errors = audit_foreign_references(root)

            self.assertTrue(len(errors) >= 1)
            self.assertIn("opsdev", errors[0].message)

    def test_foreign_ref_in_rule_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)
            (rules / "bad.md").write_text("# Rule\nReferences airlineops paths.")

            errors = audit_foreign_references(root)

            self.assertTrue(len(errors) >= 1)
            self.assertIn(".claude/rules/bad.md", errors[0].artifact)

    def test_project_own_name_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "gzkit.instructions.md").write_text(
                _instruction_file("**/*", "# gzkit-specific rules only")
            )

            errors = audit_foreign_references(root)

            self.assertEqual(errors, [])


class TestDrift(unittest.TestCase):
    """Test audit_generated_surface_drift().

    @covers REQ-0.17.0-02-06
    """

    @covers("REQ-0.17.0-02-06")
    def test_synced_content_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            body = "# Global Rule\nContent here."
            (inst / "global.instructions.md").write_text(_instruction_file("**/*", body))
            # sync_claude_rules would produce body.lstrip("\n") for global
            (rules / "global.md").write_text(body)

            errors = audit_generated_surface_drift(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.17.0-02-06")
    def test_missing_rule_file_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            (inst / "missing.instructions.md").write_text(
                _instruction_file("**/*", "# Missing rule")
            )
            # Don't create the rule file

            errors = audit_generated_surface_drift(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("missing", errors[0].message)

    @covers("REQ-0.17.0-02-06")
    def test_drifted_content_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            (inst / "drift.instructions.md").write_text(
                _instruction_file("**/*", "# Original content")
            )
            (rules / "drift.md").write_text("# Modified content")

            errors = audit_generated_surface_drift(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("drifted", errors[0].message)

    @covers("REQ-0.17.0-02-06")
    def test_orphan_rule_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            # Rule file with no source instruction
            (rules / "orphan.md").write_text("# Orphan rule")

            errors = audit_generated_surface_drift(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("Orphan", errors[0].message)

    def test_scoped_rule_content_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            body = "# Scoped Rule"
            (inst / "scoped.instructions.md").write_text(_instruction_file("src/**", body))
            # _extract_body_after_frontmatter returns "\n# Scoped Rule" (line after ---)
            # sync_claude_rules produces scoped format: ---\npaths\n---\n + extracted_body
            content = (inst / "scoped.instructions.md").read_text(encoding="utf-8")
            from gzkit.rules import _extract_body_after_frontmatter

            extracted = _extract_body_after_frontmatter(content)
            expected = '---\npaths:\n  - "src/**"\n---\n' + extracted
            (rules / "scoped.md").write_text(expected)

            errors = audit_generated_surface_drift(root)

            self.assertEqual(errors, [])

    def test_excluded_agent_not_expected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            (inst / "excluded.instructions.md").write_text(
                _instruction_file("**/*", "# Excluded", exclude_agent="coding-agent")
            )
            # No rule file should be expected for excluded instructions

            errors = audit_generated_surface_drift(root)

            self.assertEqual(errors, [])


class TestCodeContract(unittest.TestCase):
    """Test audit_code_contract_mismatches()."""

    def test_pydantic_only_codebase_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "models.instructions.md").write_text(
                _instruction_file("**/*", "# Models\nUse Pydantic BaseModel only.")
            )
            src = root / "src"
            src.mkdir()
            (src / "models.py").write_text(
                "from pydantic import BaseModel\n\nclass Foo(BaseModel):\n    pass\n"
            )

            errors = audit_code_contract_mismatches(root)

            self.assertEqual(errors, [])

    def test_dataclass_usage_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "models.instructions.md").write_text(
                _instruction_file("**/*", "# Models\nUse Pydantic BaseModel only.")
            )
            src = root / "src"
            src.mkdir()
            (src / "bad_model.py").write_text(
                "from dataclasses import dataclass\n\n@dataclass\nclass Bar:\n    x: int\n"
            )

            errors = audit_code_contract_mismatches(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("dataclasses", errors[0].message)
            self.assertIn("bad_model.py", errors[0].message)

    def test_missing_models_instruction_skips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            # No models.instructions.md

            errors = audit_code_contract_mismatches(root)

            self.assertEqual(errors, [])

    def test_no_instructions_dir_skips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            errors = audit_code_contract_mismatches(root)

            self.assertEqual(errors, [])


class TestOrchestrator(unittest.TestCase):
    """Test audit_instructions() aggregation."""

    def test_aggregates_errors_from_all_sub_audits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            # Reachability error: unreachable glob
            (inst / "unreachable.instructions.md").write_text(
                _instruction_file("nowhere/**", "# Unreachable")
            )
            # Foreign reference error
            (inst / "foreign.instructions.md").write_text(
                _instruction_file("**/*", "# Uses airlineops paths")
            )
            # Orphan rule (drift error)
            (rules / "orphan.md").write_text("# Orphan")

            errors = audit_instructions(root)

            types_found = {e.type for e in errors}
            self.assertIn("instruction", types_found)
            # Should have at least: 1 reachability + 1 foreign + orphan + missing rules
            self.assertGreaterEqual(len(errors), 3)

    def test_clean_project_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            body = "# Clean Rule"
            (inst / "clean.instructions.md").write_text(_instruction_file("**/*", body))
            (rules / "clean.md").write_text(body)

            errors = audit_instructions(root)

            self.assertEqual(errors, [])
