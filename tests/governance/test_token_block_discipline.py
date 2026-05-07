"""Tests for token-block discipline doctrine canon (OBPI-0.0.41-01)."""

import unittest
from pathlib import Path


class TestTokenBlockDisciplineCanon(unittest.TestCase):
    """Verify token-block discipline rule file exists and contains required sub-invariants."""

    def test_rule_file_exists(self):
        """OBPI-0.0.41-01: Rule file `.gzkit/rules/token-block-discipline.md` exists."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        self.assertTrue(rule_file.exists(), f"Rule file not found: {rule_file}")

    def test_rule_file_has_yaml_frontmatter(self):
        """OBPI-0.0.41-01: Rule file has YAML frontmatter."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("---\nid:", content, "Rule file missing YAML frontmatter")

    def test_rule_version_comment_present(self):
        """OBPI-0.0.41-01: Rule file has body-level rule-version comment."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("<!-- rule-version:", content, "Rule file missing rule-version comment")

    def test_binding_sub_invariant_1_abandon_categories(self):
        """OBPI-0.0.41-01-02: Binding Sub-Invariant 1 documented (auditable abandon categories)."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("Binding Sub-Invariant 1", content)
        self.assertIn("network_loss", content)
        self.assertIn("external_blocker", content)
        self.assertIn("wrong_obpi_claimed", content)
        self.assertIn("tool_failure", content)

    def test_binding_sub_invariant_2_minimum_information(self):
        """OBPI-0.0.41-01-03: Binding Sub-Invariant 2 documented (min-info requirements)."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("Binding Sub-Invariant 2", content)
        self.assertIn("Last lock-event timestamp", content)
        self.assertIn("Last commit SHA", content)
        self.assertIn("decision context", content)
        self.assertIn("branch state", content)

    def test_binding_sub_invariant_3_reaping(self):
        """OBPI-0.0.41-01-04: Binding Sub-Invariant 3 documented (reaping protocol)."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("Binding Sub-Invariant 3", content)
        self.assertIn("abandoned_by_reaper", content)

    def test_binding_sub_invariant_4_ttl_canon(self):
        """OBPI-0.0.41-01-05: Binding Sub-Invariant 4 documented (TTL + reaping)."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("Binding Sub-Invariant 4", content)
        self.assertIn("24 hours", content)
        self.assertIn("12 hours", content)

    def test_binding_sub_invariant_5_release_fail_closed(self):
        """OBPI-0.0.41-01-06: Binding Sub-Invariant 5 documented (fail-closed release)."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("Binding Sub-Invariant 5", content)
        self.assertIn("refuse to release", content)

    def test_vocabulary_section_present(self):
        """OBPI-0.0.41-01-06: Vocabulary section defined."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("## Vocabulary", content)
        self.assertIn("**Token**", content)
        self.assertIn("**Register entry**", content)
        self.assertIn("**Traversal**", content)
        self.assertIn("**Abandonment**", content)
        self.assertIn("**Reaping**", content)

    def test_cross_links_present(self):
        """OBPI-0.0.41-01-06: Cross-links to AGENTS.md and state-doctrine.md present."""
        rule_file = Path(".gzkit/rules/token-block-discipline.md")
        content = rule_file.read_text(encoding="utf-8")
        self.assertIn("AGENTS.md", content)
        self.assertIn("state-doctrine.md", content)
        self.assertIn("ADR-0.0.41", content)
