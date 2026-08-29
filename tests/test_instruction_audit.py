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


def _framework_tree(root: Path) -> Path:
    """Mark ``root`` as the gzkit repo itself rather than a project using it.

    ``_is_framework_tree`` keys on the package source being present, so a test
    that wants the strict every-pattern-must-match reading has to say so out
    loud. A bare temp directory is an ADOPTER tree; asserting framework
    semantics against one is how a reachability test goes green because the
    discriminator moved rather than because the behaviour holds (GHI #912).
    """
    package = root / "src" / "gzkit"
    package.mkdir(parents=True, exist_ok=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    return root


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
            (inst / "src.instructions.md").write_text(
                _instruction_file("src/**", "# Source rules"), encoding="utf-8"
            )
            src = root / "src"
            src.mkdir()
            (src / "main.py").write_text("print('hello')", encoding="utf-8")

            errors = audit_instruction_reachability(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.17.0-02-06")
    def test_framework_tree_flags_a_glob_matching_nothing(self) -> None:
        """On gzkit itself every pattern must match: this is where canon lives."""
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework_tree(Path(tmp))
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "missing.instructions.md").write_text(
                _instruction_file("nonexistent/**", "# Missing target"), encoding="utf-8"
            )

            errors = audit_instruction_reachability(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("nonexistent/**", errors[0].message)
            self.assertIn("zero files", errors[0].message)

    def test_framework_tree_flags_an_unpopulated_adopter_path(self) -> None:
        """Strictness survives at the source, which is what catches a typo.

        ``docs/design/adr/**`` is adopter-real, so an adopter tree stays silent
        about it. gzkit is where the corpus is authored, so a pattern naming a
        directory this repo does not have is a defect in canon and must fire
        before the rule ships (GHI #912).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework_tree(Path(tmp))
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "adr.instructions.md").write_text(
                _instruction_file("docs/design/adr/**", "# ADR rules"), encoding="utf-8"
            )

            errors = audit_instruction_reachability(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("docs/design/adr/**", errors[0].message)

    def test_adopter_tree_permits_an_unpopulated_subtree(self) -> None:
        """A rule scoped to work the project has not done yet is not a defect.

        The whole point of scoping a rule to ``docs/design/adr/**`` is that it
        arms the moment the operator authors an ADR. Reporting it on day one
        describes the project's youth, not its configuration (GHI #912).
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "adr.instructions.md").write_text(
                _instruction_file("docs/design/adr/**", "# ADR rules"), encoding="utf-8"
            )

            errors = audit_instruction_reachability(root)

            self.assertEqual(errors, [])

    def test_adopter_tree_permits_an_uncreated_literal_file(self) -> None:
        """A literal path is the same question as a glob, and gets the answer.

        ``CHANGELOG.md`` has no glob segment at all, so any predicate reasoning
        about directory prefixes abstains on it rather than deciding it. The
        tree discriminator answers it the same way it answers a subtree.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "changelog.instructions.md").write_text(
                _instruction_file("CHANGELOG.md", "# Changelog rules"), encoding="utf-8"
            )

            errors = audit_instruction_reachability(root)

            self.assertEqual(errors, [])

    def test_adopter_tree_flags_a_leaked_framework_path(self) -> None:
        """The leak backstop survives the relaxation, which is the whole bargain.

        An adopter can never have ``src/gzkit/``. GHI #911 stops these at the
        delivery boundary; this audit is the independent witness that fires when
        the classifier misses one or a mirror is hand-edited.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "mx.instructions.md").write_text(
                _instruction_file("src/gzkit/mx/**", "# MX rules"), encoding="utf-8"
            )

            errors = audit_instruction_reachability(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("src/gzkit/mx/**", errors[0].message)

    def test_global_pattern_always_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "global.instructions.md").write_text(
                _instruction_file("**/*", "# Global rule"), encoding="utf-8"
            )

            errors = audit_instruction_reachability(root)

            self.assertEqual(errors, [])

    def test_no_instructions_dir_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            errors = audit_instruction_reachability(root)

            self.assertEqual(errors, [])

    def test_multi_pattern_flags_only_unreachable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _framework_tree(Path(tmp))
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "multi.instructions.md").write_text(
                _instruction_file("src/**,missing/**", "# Multi"), encoding="utf-8"
            )
            src = root / "src"
            src.mkdir(exist_ok=True)
            (src / "app.py").write_text("", encoding="utf-8")

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
                _instruction_file("**/*", "# Clean gzkit rules\nNo foreign refs here."),
                encoding="utf-8",
            )

            errors = audit_foreign_references(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.14.0-04-02")
    def test_airlineops_detected_in_instruction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "bad.instructions.md").write_text(
                _instruction_file("**/*", "# Rules\nUse airlineops conventions."), encoding="utf-8"
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
                _instruction_file("**/*", "# Rules\nRun opsdev arb ruff."), encoding="utf-8"
            )

            errors = audit_foreign_references(root)

            self.assertTrue(len(errors) >= 1)
            self.assertIn("opsdev", errors[0].message)

    def test_foreign_ref_in_rule_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)
            (rules / "bad.md").write_text("# Rule\nReferences airlineops paths.", encoding="utf-8")

            errors = audit_foreign_references(root)

            self.assertTrue(len(errors) >= 1)
            self.assertIn(".claude/rules/bad.md", errors[0].artifact)

    def test_project_own_name_not_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "gzkit.instructions.md").write_text(
                _instruction_file("**/*", "# gzkit-specific rules only"), encoding="utf-8"
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
            (inst / "global.instructions.md").write_text(
                _instruction_file("**/*", body), encoding="utf-8"
            )
            # sync_claude_rules would produce body.lstrip("\n") for global
            (rules / "global.md").write_text(body, encoding="utf-8")

            errors = audit_generated_surface_drift(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.14.0-04-03")
    @covers("REQ-0.17.0-02-06")
    def test_missing_rule_file_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            (inst / "missing.instructions.md").write_text(
                _instruction_file("**/*", "# Missing rule"), encoding="utf-8"
            )
            # Don't create the rule file

            errors = audit_generated_surface_drift(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("missing", errors[0].message)

    @covers("REQ-0.17.0-02-06")
    def test_synced_content_with_generated_banner_passes(self) -> None:
        """Banner-stripping is consistent across source body and mirror.

        Both sides emerge from the same render path and carry the
        ``<!-- Generated by gz agent sync -->`` banner. Before the
        regression-fix, the audit's banner-stripping regex was
        line-start-anchored (no ``re.MULTILINE``), so it stripped the
        banner from the global mirror (banner at position 0) but not
        from the source body (banner appears after a leading newline)
        nor from the scoped mirror (banner appears after the closing
        ``---``). The asymmetry produced false drift on every synced
        pair where the source body retained the banner.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            banner = "<!-- Generated by gz agent sync — do not edit -->"
            global_source = f'---\napplyTo: "**/*"\n---\n{banner}\n\n# Global Rule\nContent.'
            (inst / "global.instructions.md").write_text(global_source, encoding="utf-8")
            (rules / "global.md").write_text(
                f"{banner}\n\n# Global Rule\nContent.", encoding="utf-8"
            )

            scoped_source = f'---\napplyTo: "docs/**"\n---\n{banner}\n\n# Scoped Rule\nContent.'
            (inst / "scoped.instructions.md").write_text(scoped_source, encoding="utf-8")
            (rules / "scoped.md").write_text(
                f'---\npaths:\n  - "docs/**"\n---\n{banner}\n\n# Scoped Rule\nContent.',
                encoding="utf-8",
            )

            errors = audit_generated_surface_drift(root)

            self.assertEqual(errors, [])

    @covers("REQ-0.17.0-02-06")
    def test_drifted_content_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)

            (inst / "drift.instructions.md").write_text(
                _instruction_file("**/*", "# Original content"), encoding="utf-8"
            )
            (rules / "drift.md").write_text("# Modified content", encoding="utf-8")

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
            (rules / "orphan.md").write_text("# Orphan rule", encoding="utf-8")

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
            (inst / "scoped.instructions.md").write_text(
                _instruction_file("src/**", body), encoding="utf-8"
            )
            # _extract_body_after_frontmatter returns "\n# Scoped Rule" (line after ---)
            # sync_claude_rules produces scoped format: ---\npaths\n---\n + extracted_body
            content = (inst / "scoped.instructions.md").read_text(encoding="utf-8")
            from gzkit.rules import _extract_body_after_frontmatter

            extracted = _extract_body_after_frontmatter(content)
            expected = '---\npaths:\n  - "src/**"\n---\n' + extracted
            (rules / "scoped.md").write_text(expected, encoding="utf-8")

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
                _instruction_file("**/*", "# Excluded", exclude_agent="coding-agent"),
                encoding="utf-8",
            )
            # No rule file should be expected for excluded instructions

            errors = audit_generated_surface_drift(root)

            self.assertEqual(errors, [])


class TestCodeContract(unittest.TestCase):
    """Test audit_code_contract_mismatches()."""

    @covers("REQ-0.14.0-04-04")
    def test_pydantic_only_codebase_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "models.instructions.md").write_text(
                _instruction_file("**/*", "# Models\nUse Pydantic BaseModel only."),
                encoding="utf-8",
            )
            # gzkit's OWN package root — the only tree this audit may read.
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "models.py").write_text(
                "from pydantic import BaseModel\n\nclass Foo(BaseModel):\n    pass\n",
                encoding="utf-8",
            )

            errors = audit_code_contract_mismatches(root)

            self.assertEqual(errors, [])

    def test_dataclass_usage_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "models.instructions.md").write_text(
                _instruction_file("**/*", "# Models\nUse Pydantic BaseModel only."),
                encoding="utf-8",
            )
            # Inside gzkit's own package, the detection REQ-0.14.0-04-04
            # attests to must still fire.
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "bad_model.py").write_text(
                "from dataclasses import dataclass\n\n@dataclass\nclass Bar:\n    x: int\n",
                encoding="utf-8",
            )

            errors = audit_code_contract_mismatches(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("dataclasses", errors[0].message)
            self.assertIn("bad_model.py", errors[0].message)

    def test_adopter_tree_without_gzkit_package_is_noop(self) -> None:
        """An adopter's own `src/` is not gzkit's constraint to enforce (GHI #607).

        STDLIB-FIRST is gzkit's principle and gzkit's constraint. `gz init`
        scaffolds `models.md` into an adopter's rules, sync renders it to
        `.github/instructions/models.instructions.md`, and this audit then read
        the adopter's ENTIRE `src/` tree -- so a project that took gzkit for the
        governance process had its pre-existing value objects fail `gz validate`.

        The scope predicate keeps the attested REQ-0.14.0-04-04 detection
        capability (the REQ is silent on scope) while making the audit
        structurally inert outside gzkit's own package.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (inst / "models.instructions.md").write_text(
                _instruction_file("**/*", "# Models\nUse Pydantic BaseModel only."),
                encoding="utf-8",
            )
            adopter_pkg = root / "src" / "their_app"
            adopter_pkg.mkdir(parents=True)
            (adopter_pkg / "value_objects.py").write_text(
                "from dataclasses import dataclass\n\n@dataclass\nclass Money:\n    cents: int\n",
                encoding="utf-8",
            )

            errors = audit_code_contract_mismatches(root)

            self.assertEqual(errors, [])

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
                _instruction_file("nowhere/**", "# Unreachable"), encoding="utf-8"
            )
            # Foreign reference error
            (inst / "foreign.instructions.md").write_text(
                _instruction_file("**/*", "# Uses airlineops paths"), encoding="utf-8"
            )
            # Orphan rule (drift error)
            (rules / "orphan.md").write_text("# Orphan", encoding="utf-8")

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
            (inst / "clean.instructions.md").write_text(
                _instruction_file("**/*", body), encoding="utf-8"
            )
            (rules / "clean.md").write_text(body, encoding="utf-8")

            errors = audit_instructions(root)

            self.assertEqual(errors, [])


class CanonicalRulesSupersedeInstructionSourceTest(unittest.TestCase):
    """Where `.gzkit/rules/` canon exists, `.github/instructions/` is not a source.

    The drift audit compared `.claude/rules/` against `.github/instructions/` --
    one derived view judged against another, which is what Architectural
    Boundary 6 forbids and what GHI #891 corrected in `_shared_subtree_rules`.
    Both are rendered FROM `.gzkit/rules/`, so with copilot disabled every
    Claude rule was reported an orphan "with no source instruction" while its
    actual source sat in canon, unchanged.

    The instruction path survives as the fallback for a legacy adopter who
    hand-authors `.github/instructions/` with no canon -- there those files ARE
    the source.
    """

    def test_claude_rules_are_not_orphans_when_canon_exists(self) -> None:
        """A canonical rule with no copilot mirror is not an orphan."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            canon = root / ".gzkit" / "rules"
            canon.mkdir(parents=True)
            (canon / "sample.md").write_text(
                '---\nid: sample\npaths:\n  - "**"\n---\n\n# Sample\n', encoding="utf-8"
            )
            rules = root / ".claude" / "rules"
            rules.mkdir(parents=True)
            (rules / "sample.md").write_text("# Sample\n", encoding="utf-8")

            errors = audit_generated_surface_drift(root)

            self.assertEqual(errors, [])

    def test_legacy_instruction_source_still_audited_without_canon(self) -> None:
        """With no canon, hand-authored instructions remain the source of truth.

        Guards against 'fixing' the orphan report by disabling the audit: a
        legacy tree must still catch a missing rule file.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            inst = root / ".github" / "instructions"
            inst.mkdir(parents=True)
            (root / ".claude" / "rules").mkdir(parents=True)

            (inst / "missing.instructions.md").write_text(
                _instruction_file("**/*", "# Missing rule"), encoding="utf-8"
            )

            errors = audit_generated_surface_drift(root)

            self.assertEqual(len(errors), 1)
            self.assertIn("missing", errors[0].message)
