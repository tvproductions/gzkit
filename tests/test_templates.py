"""Tests for gzkit template system."""

import unittest
from pathlib import Path

from gzkit.templates import list_templates, load_template, render_template


class TestLoadTemplate(unittest.TestCase):
    """Tests for template loading."""

    def test_load_prd_template(self) -> None:
        """Can load PRD template."""
        content = load_template("prd")
        self.assertIn("{id}", content)
        self.assertIn("Problem Statement", content)

    def test_load_adr_template(self) -> None:
        """Can load ADR template."""
        content = load_template("adr")
        self.assertIn("{id}", content)
        self.assertIn("Intent", content)
        self.assertIn("Decision", content)
        self.assertIn("Decomposition Scorecard", content)

    def test_load_obpi_template(self) -> None:
        """Can load OBPI template."""
        content = load_template("obpi")
        self.assertIn("{id}", content)
        self.assertIn("Objective", content)
        self.assertIn("Requirements (FAIL-CLOSED)", content)
        self.assertIn("Discovery Checklist", content)

    def test_load_nonexistent_template(self) -> None:
        """Loading nonexistent template raises error."""
        with self.assertRaises(FileNotFoundError):
            load_template("nonexistent")


class TestRenderTemplate(unittest.TestCase):
    """Tests for template rendering."""

    def test_render_substitutes_values(self) -> None:
        """Render substitutes provided values."""
        content = render_template(
            "prd",
            id="PRD-TEST-1.0.0",
            title="Test PRD",
            semver="1.0.0",
        )
        self.assertIn("PRD-TEST-1.0.0", content)
        self.assertIn("Test PRD", content)

    def test_render_uses_defaults(self) -> None:
        """Render uses default values for missing keys."""
        content = render_template(
            "adr",
            id="ADR-0.1.0",
            title="Test ADR",
        )
        # date should be filled with today's date
        self.assertIn("ADR-0.1.0", content)
        # status should default to "Draft"
        self.assertIn("Draft", content)

    def test_render_preserves_unknown_placeholders(self) -> None:
        """Render preserves placeholders for unknown keys."""
        content = render_template(
            "obpi",
            id="OBPI-0.1.0-01-test",
            title="Test OBPI",
            # parent_adr not provided
        )
        # Unknown placeholders preserved
        self.assertIn("{parent_adr}", content)


class TestAgentsTemplateSemantic(unittest.TestCase):
    """Semantic content tests for the AGENTS template.

    Prevents sync from silently dropping governance rules.
    """

    def setUp(self) -> None:
        self.content = render_template(
            "agents",
            project_name="test-project",
            project_purpose="Test purpose",
            tech_stack="Python 3.13+",
            skills_canon_path=".gzkit/skills",
            skills_claude_path=".claude/skills",
            skills_codex_path=".agents/skills",
            skills_copilot_path=".github/skills",
            skills_catalog="(none)",
            sync_date="2026-01-01",
            local_content="",
        )

    def test_always_rules_present(self) -> None:
        """All 6 'Always' rules are present in rendered AGENTS template."""
        always_rules = [
            "Read AGENTS.md before starting work",
            "Follow the gate covenant for all changes",
            "Record governance events in the ledger",
            "Preserve human intent across context boundaries",
            "offload online research, codebase exploration, and log analysis to subagents",
            "always include a 'Why' parameter in the subagent system prompt",
        ]
        for rule in always_rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, self.content)

    def test_never_rules_present(self) -> None:
        """All 4 'Never' rules are present in rendered AGENTS template."""
        never_rules = [
            "Bypass Gate 5 (human attestation)",
            "Modify the ledger directly (use gzkit commands)",
            "Create governance artifacts without proper linkage",
            "Make changes that violate declared invariants",
        ]
        for rule in never_rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, self.content)

    def test_local_content_injection(self) -> None:
        """AGENTS template includes agents.local.md injection markers."""
        self.assertIn("<!-- BEGIN agents.local.md -->", self.content)
        self.assertIn("<!-- END agents.local.md -->", self.content)

    def test_pipeline_runtime_is_canonical(self) -> None:
        """Rendered AGENTS template names the CLI runtime as canonical."""
        self.assertIn("uv run gz obpi pipeline <OBPI-ID>", self.content)
        self.assertIn("gz-obpi-pipeline", self.content)
        self.assertIn("thin alias", self.content)


class TestAdapterTemplatesReferenceCanon(unittest.TestCase):
    """Adapter templates reference AGENTS.md instead of duplicating catalog."""

    def test_claude_adapter_references_agents_for_skills(self) -> None:
        content = render_template("claude", skills_catalog="- `test-skill`: Desc")
        self.assertNotIn("`test-skill`", content)
        self.assertIn("AGENTS.md", content)

    def test_copilot_adapter_references_agents_for_skills(self) -> None:
        content = render_template("copilot", skills_catalog="- `test-skill`: Desc")
        self.assertNotIn("`test-skill`", content)
        self.assertIn("AGENTS.md", content)
        self.assertIn("Available Skills", content)

    def test_agents_template_keeps_full_catalog(self) -> None:
        content = render_template("agents", skills_catalog="- `test-skill`: Desc")
        self.assertIn("`test-skill`", content)


class TestListTemplates(unittest.TestCase):
    """Tests for listing templates."""

    def test_lists_core_templates(self) -> None:
        """Lists all core templates."""
        templates = list_templates()
        names = {Path(template).stem for template in templates}
        self.assertIn("prd", names)
        self.assertIn("adr", names)
        self.assertIn("obpi", names)
        self.assertIn("constitution", names)
        self.assertIn("agents", names)


if __name__ == "__main__":
    unittest.main()
