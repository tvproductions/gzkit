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
        # The 2026-06-04 doctrine reword (8dc04a9a) scoped the pipeline mandate to
        # contract-bearing OBPIs and dropped the "thin alias" phrasing; the runtime is
        # still named canonical via "the runtime owns stage sequencing".
        self.assertIn("the runtime owns stage sequencing", self.content)


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

    def test_agents_template_points_to_live_catalog(self) -> None:
        content = render_template("agents", skills_catalog="- `test-skill`: Desc")
        self.assertNotIn("`test-skill`", content)
        self.assertIn("uv run gz skill list", content)


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
    @covers("REQ-0.0.32-15-10")  # audit-exempt: regression-invariant-overlay OBPI-11 byte parity
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
        """`src/gzkit/templates/__init__.py` must expose the full public API."""
        from gzkit.templates import __all__ as templates_all

        expected = {
            "CORE_TEMPLATES",
            "_classify_template_file",
            "_iter_canonical_template_slugs",
            "get_template_path",
            "list_templates",
            "load_template",
            "render_template",
            "scaffold_core_templates",
        }
        self.assertEqual(set(templates_all), expected)

    @covers("REQ-0.0.32-11-04")
    def test_skills_subdir_retained(self) -> None:
        """`src/gzkit/templates/skills/` subdir must remain at the package surface."""
        skills_subdir = _PROJECT_ROOT / "src" / "gzkit" / "templates" / "skills"
        self.assertTrue(
            skills_subdir.is_dir(),
            "src/gzkit/templates/skills/ must be retained at the package surface",
        )

    @covers("REQ-0.0.32-06-02")
    def test_pyproject_includes_template_markdown(self) -> None:
        """pyproject.toml must include src/gzkit/templates/**/*.md (OBPI-06 scope)."""
        pyproject = _PROJECT_ROOT / "pyproject.toml"
        content = pyproject.read_text(encoding="utf-8")
        self.assertIn(
            "src/gzkit/templates/**/*.md",
            content,
            "templates wheel-include extension is part of OBPI-06 canonical surfaces",
        )

    @covers("REQ-0.0.32-11-09")
    def test_sync_surfaces_has_templates_pkg_sync(self) -> None:
        """sync_pkg_surfaces propagates .gzkit/templates/ to src/gzkit/templates/ (OBPI-08)."""
        import tempfile  # noqa: PLC0415

        from gzkit.config import GzkitConfig  # noqa: PLC0415
        from gzkit.sync_surfaces import sync_pkg_surfaces  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pkg_init = root / "src" / "gzkit" / "templates" / "__init__.py"
            pkg_init.parent.mkdir(parents=True)
            pkg_init.write_text("", encoding="utf-8")
            canonical = root / ".gzkit" / "templates" / "test-template.md"
            canonical.parent.mkdir(parents=True)
            canonical.write_text("# Test Template\n", encoding="utf-8")

            sync_pkg_surfaces(root, GzkitConfig(project_name="test"))

            pkg_copy = root / "src" / "gzkit" / "templates" / "test-template.md"
            self.assertTrue(
                pkg_copy.exists(),
                "OBPI-08 must propagate .gzkit/templates -> src/gzkit/templates",
            )
            self.assertEqual(pkg_copy.read_bytes(), canonical.read_bytes())

    @covers("REQ-0.0.32-11-10")
    def test_all_templates_loadable_post_migration(self) -> None:
        """`load_template` must succeed for all templates present in .gzkit/templates/."""
        authored_root = _PROJECT_ROOT / ".gzkit" / "templates"
        for md_file in sorted(authored_root.glob("*.md")):
            name = md_file.stem
            with self.subTest(template=name):
                content = load_template(name)
                self.assertGreater(len(content), 0, f"Template {name!r} must not be empty")


class TestCoreTemplatesRegistry(unittest.TestCase):
    """REQ-0.0.32-12-01: CORE_TEMPLATES registry exists in src/gzkit/templates/__init__.py."""

    @covers("REQ-0.0.32-12-01")
    def test_core_templates_is_list_of_str(self) -> None:
        """CORE_TEMPLATES is a non-empty list of strings."""
        from gzkit.templates import CORE_TEMPLATES  # noqa: PLC0415

        self.assertIsInstance(CORE_TEMPLATES, list)
        self.assertGreater(len(CORE_TEMPLATES), 0)
        for item in CORE_TEMPLATES:
            self.assertIsInstance(item, str)

    @covers("REQ-0.0.32-12-01")
    def test_core_templates_enumerates_canonical_slugs(self) -> None:
        """CORE_TEMPLATES enumerates all 11+ canonical template slugs."""
        from gzkit.templates import CORE_TEMPLATES  # noqa: PLC0415

        self.assertGreaterEqual(len(CORE_TEMPLATES), 11)
        # Spot-check known slugs
        for slug in ("adr", "prd", "obpi", "constitution", "agents"):
            self.assertIn(slug, CORE_TEMPLATES)

    @covers("REQ-0.0.32-12-02")
    def test_iter_canonical_template_slugs_count_matches_registry(self) -> None:
        """_iter_canonical_template_slugs returns same count as CORE_TEMPLATES."""
        from gzkit.templates import CORE_TEMPLATES, _iter_canonical_template_slugs  # noqa: PLC0415

        count = sum(1 for _ in _iter_canonical_template_slugs())
        self.assertEqual(count, len(CORE_TEMPLATES))


class TestScaffoldCoreTemplates(unittest.TestCase):
    """REQ-0.0.32-12-03, 07, 08: scaffold_core_templates scaffolder."""

    @covers("REQ-0.0.32-12-03")
    def test_scaffold_signature_matches_sibling_scaffolders(self) -> None:
        """scaffold_core_templates has exact sibling-scaffolder surface shape."""
        import inspect  # noqa: PLC0415

        from gzkit.templates import scaffold_core_templates  # noqa: PLC0415

        sig = inspect.signature(scaffold_core_templates)
        params = list(sig.parameters.keys())
        self.assertIn("project_root", params)
        self.assertIn("config", params)
        self.assertIn("skip_existing", params)
        # skip_existing must be keyword-only
        skip_param = sig.parameters["skip_existing"]
        self.assertEqual(skip_param.kind, inspect.Parameter.KEYWORD_ONLY)

    @covers("REQ-0.0.32-12-07")
    def test_scaffold_writes_all_canonical_templates(self) -> None:
        """Fresh scaffold writes all canonical templates to .gzkit/templates/."""
        import tempfile  # noqa: PLC0415

        from gzkit.templates import CORE_TEMPLATES, scaffold_core_templates  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            result = scaffold_core_templates(project_root)
            self.assertIsInstance(result, list)
            self.assertEqual(len(result), len(CORE_TEMPLATES))
            templates_dir = project_root / ".gzkit" / "templates"
            self.assertTrue(templates_dir.is_dir())
            for slug in CORE_TEMPLATES:
                self.assertTrue(
                    (templates_dir / f"{slug}.md").exists(),
                    f"Expected {slug}.md in .gzkit/templates/",
                )

    @covers("REQ-0.0.32-12-03")
    def test_scaffold_returns_list_of_paths(self) -> None:
        """scaffold_core_templates returns list[Path]."""
        import tempfile  # noqa: PLC0415

        from gzkit.templates import scaffold_core_templates  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            result = scaffold_core_templates(Path(tmp))
            self.assertIsInstance(result, list)
            for item in result:
                self.assertIsInstance(item, Path)

    @covers("REQ-0.0.32-12-03")
    def test_scaffold_content_byte_identical_to_package(self) -> None:
        """Scaffolded template content is byte-identical to package resource."""
        import importlib.resources  # noqa: PLC0415
        import tempfile  # noqa: PLC0415

        from gzkit.templates import scaffold_core_templates  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            scaffold_core_templates(project_root)
            templates_dir = project_root / ".gzkit" / "templates"
            pkg = importlib.resources.files("gzkit.templates")
            for target in sorted(templates_dir.glob("*.md")):
                pkg_file = pkg.joinpath(target.name)
                self.assertEqual(
                    target.read_bytes(),
                    pkg_file.read_bytes(),
                    f"Scaffolded {target.name} not byte-identical to package",
                )

    @covers("REQ-0.0.32-12-08")
    def test_skip_existing_preserves_operator_edits(self) -> None:
        """skip_existing=True preserves operator edits to .gzkit/templates/<name>.md."""
        import tempfile  # noqa: PLC0415

        from gzkit.templates import scaffold_core_templates  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            # Fresh scaffold
            scaffold_core_templates(project_root)
            # Operator edits a template
            edited = project_root / ".gzkit" / "templates" / "adr.md"
            edited.write_text("OPERATOR-EDIT", encoding="utf-8")
            # Re-scaffold with skip_existing=True
            scaffold_core_templates(project_root, skip_existing=True)
            self.assertEqual(edited.read_text(encoding="utf-8"), "OPERATOR-EDIT")

    @covers("REQ-0.0.32-12-08")
    def test_skip_existing_false_overwrites(self) -> None:
        """skip_existing=False (default) overwrites existing templates."""
        import tempfile  # noqa: PLC0415

        from gzkit.templates import scaffold_core_templates  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            scaffold_core_templates(project_root)
            edited = project_root / ".gzkit" / "templates" / "adr.md"
            edited.write_text("OPERATOR-EDIT", encoding="utf-8")
            # Re-scaffold with default skip_existing=False
            scaffold_core_templates(project_root, skip_existing=False)
            self.assertNotEqual(edited.read_text(encoding="utf-8"), "OPERATOR-EDIT")


class TestRenderTemplateProjectFirst(unittest.TestCase):
    """REQ-0.0.32-12-06: render_template() project-first -> package-fallback."""

    @covers("REQ-0.0.32-12-06")
    def test_project_first_uses_project_copy_when_present(self) -> None:
        """render_template uses .gzkit/templates/<name>.md when present in CWD tree."""
        import os  # noqa: PLC0415
        import tempfile  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            project_root = Path(tmp)
            templates_dir = project_root / ".gzkit" / "templates"
            templates_dir.mkdir(parents=True)
            (templates_dir / "adr.md").write_text("PROJECT-EDIT-{id}", encoding="utf-8")
            orig_cwd = os.getcwd()
            try:
                os.chdir(project_root)
                result = render_template("adr", id="TEST-ID")
                self.assertIn("PROJECT-EDIT-TEST-ID", result)
            finally:
                os.chdir(orig_cwd)

    @covers("REQ-0.0.32-12-06")
    def test_package_fallback_when_no_project_copy(self) -> None:
        """render_template falls back to package surface when no project copy exists."""
        import os  # noqa: PLC0415
        import tempfile  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmp:
            orig_cwd = os.getcwd()
            try:
                os.chdir(tmp)
                # No .gzkit/templates/ directory
                result = render_template("prd", id="PRD-TEST-1.0.0", title="T")
                self.assertIn("PRD-TEST-1.0.0", result)
            finally:
                os.chdir(orig_cwd)


class TestTemplatesDocsCoverage(unittest.TestCase):
    """REQ-0.0.32-12-09, 10: docs and gz check gate coverage."""

    @covers("REQ-0.0.32-12-09")
    def test_init_manpage_has_templates_scaffolding_section(self) -> None:
        """docs/user/manpages/init.md must document Templates Scaffolding."""
        manpage = _PROJECT_ROOT / "docs" / "user" / "manpages" / "init.md"
        self.assertTrue(manpage.exists(), "init.md manpage must exist")
        content = manpage.read_text(encoding="utf-8")
        self.assertIn("Templates Scaffolding", content)
        self.assertIn("OBPI-0.0.32-12", content)
        self.assertIn(".gzkit/templates/", content)

    @covers("REQ-0.0.32-12-09")
    def test_runbook_has_templates_section(self) -> None:
        """docs/user/runbook.md must document templates commands."""
        runbook = _PROJECT_ROOT / "docs" / "user" / "runbook.md"
        self.assertTrue(runbook.exists(), "runbook.md must exist")
        content = runbook.read_text(encoding="utf-8")
        self.assertIn(".gzkit/templates", content)

    @covers("REQ-0.0.32-12-10")
    def test_scaffold_core_templates_importable(self) -> None:
        """scaffold_core_templates is importable — proxy for gz check exit 0 gate."""
        from gzkit.templates import (  # noqa: PLC0415
            CORE_TEMPLATES,
            scaffold_core_templates,
        )

        self.assertIsNotNone(scaffold_core_templates)
        self.assertIsInstance(CORE_TEMPLATES, list)


class TestClassifyTemplateFile(unittest.TestCase):
    """Per-surface classifier for the templates canonical surface (REQ-0.0.32-15-04).

    Signature-compatible with ``gzkit.chores._classify_chore_file``: returns
    one of ``"canonical"``, ``"package_only"``, or ``"runtime_state"``.
    """

    @covers("REQ-0.0.32-15-04")
    def test_importable(self) -> None:
        """``_classify_template_file`` is importable from ``gzkit.templates``."""
        try:
            from gzkit.templates import _classify_template_file  # noqa: PLC0415, F401
        except ImportError as e:  # pragma: no cover - failure surfaces in assertion
            self.fail(
                "_classify_template_file must be importable from gzkit.templates; "
                f"got ImportError: {e}"
            )

    @covers("REQ-0.0.32-15-04")
    def test_package_only_init_py(self) -> None:
        """``__init__.py`` files classify as ``package_only``."""
        from gzkit.templates import _classify_template_file  # noqa: PLC0415

        result = _classify_template_file(Path("src/gzkit/templates/__init__.py"))
        self.assertEqual(result, "package_only")

    @covers("REQ-0.0.32-15-04")
    def test_canonical_md(self) -> None:
        """A template ``*.md`` classifies as ``canonical``."""
        from gzkit.templates import _classify_template_file  # noqa: PLC0415

        result = _classify_template_file(Path("src/gzkit/templates/AGENTS.md"))
        self.assertEqual(result, "canonical")

    @covers("REQ-0.0.32-15-04")
    def test_package_only_pycache(self) -> None:
        """Anything under ``__pycache__`` classifies as ``package_only``."""
        from gzkit.templates import _classify_template_file  # noqa: PLC0415

        result = _classify_template_file(
            Path("src/gzkit/templates/__pycache__/something.cpython-313.pyc")
        )
        self.assertEqual(result, "package_only")


if __name__ == "__main__":
    unittest.main()
