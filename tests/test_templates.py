"""Tests for gzkit template system.

@covers ADR-0.17.0  OBPI-0.17.0-03 slim-claudemd-template
"""

import unittest
from pathlib import Path

from gzkit.templates import list_templates, load_template, render_template
from gzkit.traceability import covers

_PROJECT_ROOT = Path(__file__).resolve().parents[1]


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

    @covers("REQ-0.0.32-11-05")
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
            "Offload online research, codebase exploration, and log analysis to "
            "subagents when work splits across independent items",
            "always include a 'Why' parameter in the subagent system prompt",
        ]
        for rule in always_rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, self.content)
        self.assertNotIn("Aggressively offload", self.content)

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

    @covers("REQ-0.17.0-03-05")
    def test_local_content_injection(self) -> None:
        """AGENTS template includes agents.local.md injection markers."""
        self.assertIn("<!-- BEGIN agents.local.md -->", self.content)
        self.assertIn("<!-- END agents.local.md -->", self.content)

    @covers("REQ-0.17.0-03-07")
    def test_pipeline_runtime_is_canonical(self) -> None:
        """Rendered AGENTS template names the CLI runtime as canonical."""
        self.assertIn("uv run gz obpi pipeline <OBPI-ID>", self.content)
        self.assertIn("gz-obpi-pipeline", self.content)
        self.assertIn("thin alias", self.content)


class TestAdapterTemplatesReferenceCanon(unittest.TestCase):
    """Adapter templates reference AGENTS.md instead of duplicating catalog.

    @covers REQ-0.17.0-03-02
    @covers REQ-0.17.0-03-03
    @covers REQ-0.17.0-03-04
    """

    @covers("REQ-0.17.0-03-04")
    @covers("REQ-0.17.0-03-02")
    def test_claude_adapter_references_agents_for_skills(self) -> None:
        content = render_template("claude", skills_catalog="- `test-skill`: Desc")
        self.assertNotIn("`test-skill`", content)
        self.assertIn("AGENTS.md", content)

    @covers("REQ-0.17.0-03-03")
    def test_copilot_adapter_references_agents_for_skills(self) -> None:
        content = render_template("copilot", skills_catalog="- `test-skill`: Desc")
        self.assertNotIn("`test-skill`", content)
        self.assertIn("AGENTS.md", content)
        self.assertIn("Available Skills", content)

    def test_agents_template_keeps_full_catalog(self) -> None:
        content = render_template("agents", skills_catalog="- `test-skill`: Desc")
        self.assertIn("`test-skill`", content)


class TestRootSurfaceSlimming(unittest.TestCase):
    """Regression tests for OBPI-0.14.0-03 root surface slimming.

    Ensures workflow prose stays relocated to skills and docs,
    not re-introduced into root templates.

    @covers REQ-0.17.0-03-06
    """

    def setUp(self) -> None:
        self.agents = render_template(
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
        self.copilot = render_template(
            "copilot",
            project_name="test-project",
            project_purpose="Test purpose",
            tech_stack="Python 3.13+",
            coding_conventions="Ruff defaults",
            skills_canon_path=".gzkit/skills",
            skills_claude_path=".claude/skills",
            skills_codex_path=".agents/skills",
            skills_copilot_path=".github/skills",
            build_commands="uv sync",
            local_content="",
        )

    @covers("REQ-0.17.0-03-06")
    def test_agents_template_no_ceremony_steps(self) -> None:
        """Ceremony steps relocated to gz-obpi-pipeline skill."""
        self.assertNotIn("Present value narrative", self.agents)
        self.assertIn("gz-obpi-pipeline", self.agents)

    @covers("REQ-0.17.0-03-06")
    def test_agents_template_decomposition_references_doc(self) -> None:
        """Decomposition methodology replaced with doc reference."""
        self.assertIn("obpi-decomposition-matrix.md", self.agents)
        self.assertNotIn("Step 1: Baseline Structural Template", self.agents)

    @covers("REQ-0.17.0-03-06")
    def test_agents_template_execution_rules_condensed(self) -> None:
        """Execution rules condensed to essentials with gz --help reference."""
        self.assertIn("gz --help", self.agents)
        self.assertIn("gz check", self.agents)
        self.assertNotIn("gz prd", self.agents)
        self.assertNotIn("gz constitute", self.agents)

    @covers("REQ-0.17.0-03-06")
    def test_copilot_no_inline_ceremony(self) -> None:
        """Copilot template defers OBPI ceremony to AGENTS.md."""
        self.assertNotIn("Provide value narrative", self.copilot)
        self.assertIn("AGENTS.md", self.copilot)


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


class TestObpiDiscoveryChecklistOrder(unittest.TestCase):
    """Discovery Checklist pins parent-ADR § Decision read first.

    Closes GHI #321. Anthropic Prompt Engineering 101 'order matters'
    discipline applied to OBPI authoring: the agent must read the
    structured input (parent ADR § Decision) before the unstructured one
    (allowed paths, prerequisites). Without this pin agents grep
    backward from keywords rather than tracing forward from the parent
    ADR's Decision (Opus 4.7 § 2.3.6.2 failure pattern).
    """

    def setUp(self) -> None:
        self.content = load_template("obpi")
        self.checklist = self._extract_section(self.content, "## Discovery Checklist")

    @staticmethod
    def _extract_section(content: str, heading: str) -> str:
        start = content.find(heading)
        if start < 0:
            raise AssertionError(f"Heading {heading!r} not found in template")
        next_h2 = content.find("\n## ", start + len(heading))
        end = next_h2 if next_h2 > 0 else len(content)
        return content[start:end]

    def test_parent_adr_decision_pin_appears_before_governance_block(self) -> None:
        """Parent ADR § Decision read precedes the Governance read block."""
        decision_pin = self.checklist.find("Parent ADR § Decision")
        governance_marker = self.checklist.find("Governance")
        self.assertGreaterEqual(
            decision_pin,
            0,
            "Discovery Checklist must pin Parent ADR § Decision read",
        )
        self.assertGreaterEqual(governance_marker, 0)
        self.assertLess(
            decision_pin,
            governance_marker,
            "Parent ADR § Decision pin must appear before the Governance block",
        )

    def test_parent_adr_intent_frames_decision_read(self) -> None:
        """Parent ADR § Intent appears as the why-frame for the Decision read."""
        decision_pin = self.checklist.find("Parent ADR § Decision")
        intent_pin = self.checklist.find("Parent ADR § Intent")
        self.assertGreaterEqual(
            intent_pin,
            0,
            "Discovery Checklist must reference Parent ADR § Intent",
        )
        self.assertLess(
            decision_pin,
            intent_pin,
            "Decision pin (item #1) precedes the Intent frame (item #2)",
        )

    def test_decision_pin_includes_quote_instruction(self) -> None:
        """The Decision pin instructs the agent to quote the implementing line."""
        decision_idx = self.checklist.find("Parent ADR § Decision")
        window = self.checklist[decision_idx : decision_idx + 300]
        self.assertIn(
            "quote",
            window.lower(),
            "Decision pin must instruct the agent to quote the implementing line",
        )

    def test_stop_guard_below_decision_pin_references_decision(self) -> None:
        """A STOP guard below the Decision pin closes the unquoted-Decision failure mode."""
        decision_idx = self.checklist.find("Parent ADR § Decision")
        stop_after = self.checklist.find("STOP", decision_idx + 1)
        self.assertGreater(
            stop_after,
            decision_idx,
            "A STOP guard must follow the Decision pin",
        )
        stop_window = self.checklist[stop_after : stop_after + 250]
        self.assertIn(
            "Decision",
            stop_window,
            "STOP guard must reference the Decision item it pins",
        )


class TestObpiTemplateDemoSection(unittest.TestCase):
    """GHI #427 — OBPI scaffold template prompts authors to write product demos.

    The closeout ceremony walkthrough harvests `## Demo` (and `## Examples`)
    from briefs to showcase the *yielded product*. When the template lacks a
    Demo prompt, brief authors populate only `## Verification` (construction
    housekeeping), and the walkthrough falls through to weakest-form `--help`
    invocations. The template prompt is the upstream class fix.
    """

    def setUp(self) -> None:
        self.content = load_template("obpi")

    def test_template_includes_demo_section_heading(self) -> None:
        self.assertIn("\n## Demo\n", self.content)

    def test_template_separates_demo_from_verification(self) -> None:
        """Verification (housekeeping) appears before Demo (yielded product)."""
        verification_idx = self.content.find("\n## Verification\n")
        demo_idx = self.content.find("\n## Demo\n")
        self.assertGreater(verification_idx, 0)
        self.assertGreater(demo_idx, 0)
        self.assertLess(
            verification_idx,
            demo_idx,
            "Verification (housekeeping) must precede Demo (yielded product)",
        )

    def test_demo_section_names_yielded_product(self) -> None:
        """Demo guidance text frames the section as product, not housekeeping."""
        demo_idx = self.content.find("\n## Demo\n")
        next_h2 = self.content.find("\n## ", demo_idx + len("\n## Demo\n"))
        demo_body = self.content[demo_idx:next_h2]
        self.assertIn("YIELDED PRODUCT", demo_body)
        self.assertIn("not housekeeping", demo_body)


class TestTemplatesLayoutDualSurface(unittest.TestCase):
    """.gzkit/templates/<name>.md must be byte-identical to src/gzkit/templates/ copy.

    .gzkit/templates/ is the authored canonical source-of-truth (new home after
    reverse-migration from src/gzkit/templates/).
    src/gzkit/templates/ is the byte-equivalent package copy (ships in wheel).
    """

    @covers("REQ-0.0.32-11-01")
    def test_authored_canonical_surface_populated(self) -> None:
        """.gzkit/templates/ must exist and contain the migrated .md files."""
        authored_root = _PROJECT_ROOT / ".gzkit" / "templates"
        self.assertTrue(authored_root.is_dir(), ".gzkit/templates/ must exist post-migration")
        md_files = [f for f in authored_root.iterdir() if f.suffix == ".md"]
        self.assertGreaterEqual(
            len(md_files),
            11,
            f".gzkit/templates/ must contain all migrated .md files (found {len(md_files)})",
        )

    @covers("REQ-0.0.32-11-07")
    @covers("REQ-0.0.32-11-02")
    def test_dual_surface_byte_parity(self) -> None:
        """Authored .gzkit/templates/<name>.md must be byte-identical to src/gzkit copy."""
        authored_root = _PROJECT_ROOT / ".gzkit" / "templates"
        pkg_root = _PROJECT_ROOT / "src" / "gzkit" / "templates"
        self.assertTrue(authored_root.is_dir(), ".gzkit/templates/ must exist")
        md_files = [f for f in authored_root.iterdir() if f.suffix == ".md"]
        self.assertGreater(len(md_files), 0, ".gzkit/templates/ must contain at least one .md file")
        for authored in md_files:
            pkg_copy = pkg_root / authored.name
            self.assertTrue(
                pkg_copy.exists(),
                f"Package copy missing: {pkg_copy.relative_to(_PROJECT_ROOT)}",
            )
            self.assertEqual(
                authored.read_bytes(),
                pkg_copy.read_bytes(),
                f"Drift between .gzkit/templates/ and src/gzkit/templates/ for {authored.name}",
            )

    @covers("REQ-0.0.32-11-03")
    def test_init_py_api_preserved(self) -> None:
        """`src/gzkit/templates/__init__.py` must preserve the pre-migration public API."""
        from gzkit.templates import __all__ as templates_all

        expected = {"load_template", "render_template", "get_template_path", "list_templates"}
        self.assertEqual(
            set(templates_all),
            expected,
            "__all__ must be exactly the pre-OBPI symbol set — no CORE_TEMPLATES additions",
        )

    @covers("REQ-0.0.32-11-04")
    def test_skills_subdir_retained(self) -> None:
        """`src/gzkit/templates/skills/` subdir must remain at the package surface."""
        skills_subdir = _PROJECT_ROOT / "src" / "gzkit" / "templates" / "skills"
        self.assertTrue(
            skills_subdir.is_dir(),
            "src/gzkit/templates/skills/ must be retained at the package surface",
        )

    @covers("REQ-0.0.32-11-06")
    def test_no_scope_creep_in_init_py(self) -> None:
        """No CORE_TEMPLATES or scaffolder symbols added to __init__.py (OBPI-12 scope)."""
        init_py = _PROJECT_ROOT / "src" / "gzkit" / "templates" / "__init__.py"
        content = init_py.read_text(encoding="utf-8")
        forbidden_names = (
            "CORE_TEMPLATES",
            "scaffold_core_templates",
            "_iter_canonical_template_slugs",
        )
        for forbidden in forbidden_names:
            self.assertNotIn(
                forbidden,
                content,
                f"{forbidden} belongs to OBPI-12, must not appear in this OBPI's __init__.py",
            )

    @covers("REQ-0.0.32-11-08")
    def test_pyproject_no_new_template_includes(self) -> None:
        """pyproject.toml must not include src/gzkit/templates/**/*.md (OBPI-06 scope)."""
        pyproject = _PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")
        self.assertNotIn(
            "src/gzkit/templates/**/*.md",
            content,
            "templates wheel-include extension belongs to OBPI-06, not this OBPI",
        )

    @covers("REQ-0.0.32-11-09")
    def test_sync_surfaces_has_no_templates_byte_copy(self) -> None:
        """sync_surfaces.py must not sync .gzkit/templates to package surface (OBPI-08 scope)."""
        sync_module = _PROJECT_ROOT / "src" / "gzkit" / "sync_surfaces.py"
        content = sync_module.read_text(encoding="utf-8")
        self.assertNotIn(
            "src/gzkit/templates",
            content,
            "Dual-surface templates byte-copy step belongs to OBPI-08, not this OBPI",
        )

    @covers("REQ-0.0.32-11-10")
    def test_all_templates_loadable_post_migration(self) -> None:
        """`load_template` must succeed for all templates present in .gzkit/templates/."""
        authored_root = _PROJECT_ROOT / ".gzkit" / "templates"
        for md_file in sorted(authored_root.glob("*.md")):
            name = md_file.stem
            with self.subTest(template=name):
                content = load_template(name)
                self.assertGreater(len(content), 0, f"Template {name!r} must not be empty")


if __name__ == "__main__":
    unittest.main()
