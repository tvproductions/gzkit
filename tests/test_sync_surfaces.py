"""Regression tests for sync-generated surfaces.

@covers ADR-0.0.11  OBPI-0.0.11-04 agents-md-persona-section
@covers ADR-0.0.12  OBPI-0.0.12-07 agents-md-persona-reference
@covers ADR-0.0.13  OBPI-0.0.13-03 manifest-schema-persona-sync
"""

import re
import tempfile
import unittest
from pathlib import Path

from gzkit.templates import load_template, render_template
from gzkit.traceability import covers


class TestAgentsPersonaSection(unittest.TestCase):
    """Verify the mandatory Persona section in generated AGENTS.md."""

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

    @covers("REQ-0.0.11-04-01")
    def test_agents_template_has_persona_section(self) -> None:
        """Rendered AGENTS template contains ## Persona heading."""
        self.assertIn("## Persona", self.content)

    @covers("REQ-0.0.11-04-01")
    def test_agents_persona_references_control_surface(self) -> None:
        """Persona section references .gzkit/personas/ control surface."""
        self.assertIn(".gzkit/personas/", self.content)

    @covers("REQ-0.0.11-04-03")
    def test_agents_persona_forbids_expertise_claims(self) -> None:
        """Persona section warns against generic expertise claims."""
        self.assertIn("You are an expert", self.content)
        self.assertIn("never generic", self.content.lower())

    @covers("REQ-0.0.11-04-03")
    def test_agents_persona_frames_behavioral_identity(self) -> None:
        """Persona section describes virtue-ethics behavioral identity."""
        self.assertIn("behavioral", self.content.lower())
        self.assertIn("craftsmanship", self.content.lower())

    @covers("REQ-0.0.11-04-01")
    def test_persona_discovery_command(self) -> None:
        """Persona section includes discovery command."""
        self.assertIn("uv run gz personas list", self.content)


class TestAgentsPersonaReference(unittest.TestCase):
    """Verify persona reference integration in AGENTS.md (ADR-0.0.12-07)."""

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

    @covers("REQ-0.0.12-07-01")
    def test_persona_section_references_main_session_grounding(self) -> None:
        """Persona section references the main-session persona grounding."""
        self.assertIn("main-session", self.content)
        self.assertIn("craftsperson", self.content)
        self.assertIn("governance not as overhead", self.content)

    @covers("REQ-0.0.12-07-01")
    def test_persona_section_lists_role_mapping(self) -> None:
        """Persona section contains role-mapping table with all personas."""
        for persona in [
            "main-session",
            "implementer",
            "narrator",
            "pipeline-orchestrator",
            "quality-reviewer",
            "spec-reviewer",
        ]:
            with self.subTest(persona=persona):
                self.assertIn(f"`{persona}`", self.content)

    @covers("REQ-0.0.12-07-01")
    def test_persona_section_does_not_inline_full_content(self) -> None:
        """Persona section references but does not inline full persona files."""
        # The full grounding is ~4 sentences; the reference is condensed.
        # Check that the full behavioral anchors section is NOT inlined.
        # Anchor on newline so we match H2 headings only, not H3 subsections
        # (e.g. "### Anti-patterns" under § Attestation contains the H2 substring).
        self.assertNotIn("\n## Behavioral Anchors", self.content)
        self.assertNotIn("\n## Anti-patterns", self.content)

    @covers("REQ-0.0.12-07-02")
    def test_persona_references_survive_regeneration(self) -> None:
        """Template round-trip produces identical persona section."""
        content_a = render_template(
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
        content_b = render_template(
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
        # Extract persona section from both renders
        persona_a = content_a.split("## Persona")[1].split("## Prime Directive")[0]
        persona_b = content_b.split("## Persona")[1].split("## Prime Directive")[0]
        self.assertEqual(persona_a, persona_b)

    @covers("REQ-0.0.12-07-01")
    def test_persona_section_references_adr_0_0_12(self) -> None:
        """Persona reference section cites ADR-0.0.12."""
        self.assertIn("ADR-0.0.12", self.content)


class TestAdrPersonaSection(unittest.TestCase):
    """Verify the Persona placeholder in the ADR template."""

    @covers("REQ-0.0.11-04-02")
    def test_adr_template_has_persona_section(self) -> None:
        """ADR template contains ## Persona heading."""
        content = load_template("adr")
        self.assertIn("## Persona", content)

    @covers("REQ-0.0.11-04-02")
    def test_adr_persona_precedes_intent(self) -> None:
        """Persona section appears before Intent in ADR template."""
        content = load_template("adr")
        persona_pos = content.index("## Persona")
        intent_pos = content.index("## Intent")
        self.assertLess(persona_pos, intent_pos)


class TestPersonaSyncMirrors(unittest.TestCase):
    """Verify persona files are mirrored to vendor surfaces (OBPI-0.0.13-03).

    @covers ADR-0.0.13  OBPI-0.0.13-03 manifest-schema-persona-sync
    """

    _PERSONA_CONTENT = (
        "---\nname: implementer\ntraits:\n  - methodical\n"
        "anti-traits:\n  - scope-creep\ngrounding: I implement with care.\n---\n\n"
        "# Implementer\n"
    )

    def test_persona_sync_mirrors_to_claude(self) -> None:
        """REQ-0.0.13-03-02: Sync mirrors .gzkit/personas/ to .claude/personas/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            (personas_dir / "implementer.md").write_text(self._PERSONA_CONTENT, encoding="utf-8")

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            updated = sync_persona_mirrors(root, config)

            mirror = root / ".claude" / "personas" / "implementer.md"
            self.assertTrue(mirror.exists(), f"Expected {mirror} to exist")
            content = mirror.read_text(encoding="utf-8")
            self.assertIn("I implement with care", content)
            self.assertTrue(len(updated) > 0)

    def test_persona_sync_respects_vendor_enablement(self) -> None:
        """REQ-0.0.13-03-03: Disabled vendor gets no persona mirror."""
        _persona = (
            "---\nname: main-session\ntraits:\n  - methodical\n"
            "anti-traits:\n  - scope-creep\ngrounding: I stay on task.\n---\n\n"
            "# Main\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            (personas_dir / "main-session.md").write_text(_persona, encoding="utf-8")

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            sync_persona_mirrors(root, config, vendor_aware=True)

            # Copilot is disabled by default
            copilot_mirror = root / ".github" / "personas" / "main-session.md"
            self.assertFalse(copilot_mirror.exists(), "Disabled vendor should not get mirror")

            # Claude is enabled by default
            claude_mirror = root / ".claude" / "personas" / "main-session.md"
            self.assertTrue(claude_mirror.exists(), "Enabled vendor should get mirror")

    def test_persona_sync_skips_when_no_personas_dir(self) -> None:
        """Sync returns empty list when .gzkit/personas/ does not exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            updated = sync_persona_mirrors(root, config)
            self.assertEqual(updated, [])

    def test_persona_sync_updates_stale_mirror(self) -> None:
        """REQ-0.0.13-03-06: Re-running sync updates changed persona files."""
        _v1 = (
            "---\nname: implementer\ntraits:\n  - methodical\n"
            "anti-traits:\n  - scope-creep\ngrounding: Version one.\n---\n\n"
            "# V1\n"
        )
        _v2 = (
            "---\nname: implementer\ntraits:\n  - methodical\n"
            "anti-traits:\n  - scope-creep\ngrounding: Version two.\n---\n\n"
            "# V2\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            (personas_dir / "implementer.md").write_text(_v1, encoding="utf-8")

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            sync_persona_mirrors(root, config)

            # Update canonical file
            (personas_dir / "implementer.md").write_text(_v2, encoding="utf-8")
            updated = sync_persona_mirrors(root, config)

            mirror = root / ".claude" / "personas" / "implementer.md"
            content = mirror.read_text(encoding="utf-8")
            self.assertIn("Version two", content)
            self.assertTrue(len(updated) > 0)

    def test_persona_sync_does_not_modify_canonical(self) -> None:
        """REQ-0.0.13-03-06: Sync is one-directional — canonical files unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            personas_dir = root / ".gzkit" / "personas"
            personas_dir.mkdir(parents=True)
            canonical = personas_dir / "implementer.md"
            canonical.write_text(self._PERSONA_CONTENT, encoding="utf-8")

            from gzkit.config import GzkitConfig
            from gzkit.sync_surfaces import sync_persona_mirrors

            config = GzkitConfig()
            sync_persona_mirrors(root, config)

            self.assertEqual(canonical.read_text(encoding="utf-8"), self._PERSONA_CONTENT)


class TestLoadLocalContentPath(unittest.TestCase):
    """GHI #339: agents.local.md must live under .gzkit/ to avoid Claude Code double-load.

    Co-locating the generator-input file with rendered AGENTS.md at project root
    causes Claude Code's memory system to load the local content twice: once
    embedded in AGENTS.md (via {local_content} substitution) and once directly
    from the project-root sibling file. Moving the source under .gzkit/
    keeps the input out of the consumer's auto-discovery path.
    """

    def test_load_local_content_reads_from_gzkit_subdir(self) -> None:
        """load_local_content reads from .gzkit/agents.local.md, not project root."""
        from gzkit.sync_surfaces import load_local_content

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            gzkit_dir = root / ".gzkit"
            gzkit_dir.mkdir()
            (gzkit_dir / "agents.local.md").write_text(
                "# Project-local addendum\n", encoding="utf-8"
            )

            self.assertEqual(load_local_content(root), "# Project-local addendum\n")

    def test_load_local_content_ignores_project_root_path(self) -> None:
        """A stray agents.local.md at project root must NOT be loaded (GHI #339).

        If the legacy path is still honored, the double-load defect persists:
        Claude Code loads the project-root file directly AND through the
        AGENTS.md {local_content} substitution.
        """
        from gzkit.sync_surfaces import load_local_content

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "agents.local.md").write_text("LEGACY\n", encoding="utf-8")

            self.assertEqual(load_local_content(root), "")

    def test_load_local_content_empty_when_absent(self) -> None:
        """load_local_content returns empty string when .gzkit/agents.local.md is absent."""
        from gzkit.sync_surfaces import load_local_content

        with tempfile.TemporaryDirectory() as tmpdir:
            self.assertEqual(load_local_content(Path(tmpdir)), "")


class TestSyncPkgSurfaces(unittest.TestCase):
    """OBPI-0.0.32-08: sync_pkg_surfaces propagates .gzkit/<surface>/ to src/gzkit/<surface>/.

    @covers REQ-0.0.32-08-01
    @covers REQ-0.0.32-08-02
    @covers REQ-0.0.32-08-04
    @covers REQ-0.0.32-08-05
    """

    _VALID_SKILL_MD = (
        "---\n"
        "name: test-skill\n"
        "description: Test skill for OBPI-0.0.32-08\n"
        "lifecycle_state: active\n"
        "owner: test\n"
        "last_reviewed: 2026-01-01\n"
        "---\n\n# Test Skill\n"
    )

    @staticmethod
    def _make_pkg_surface(root: Path, surface: str) -> None:
        _make_pkg_surface(root, surface)

    @covers("REQ-0.0.32-08-01")
    def test_sync_pkg_surfaces_skills_resolves_canonical_from_gzkit(self) -> None:
        """sync_pkg_surfaces reads from .gzkit/skills/ and writes to src/gzkit/skills/."""
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_pkg_surfaces

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_pkg_surface(root, "skills")
            canonical_skill = root / ".gzkit" / "skills" / "test-skill" / "SKILL.md"
            canonical_skill.parent.mkdir(parents=True)
            canonical_skill.write_text(self._VALID_SKILL_MD, encoding="utf-8")

            config = GzkitConfig(project_name="test")
            result = sync_pkg_surfaces(root, config)

            pkg_skill = root / "src" / "gzkit" / "skills" / "test-skill" / "SKILL.md"
            self.assertTrue(pkg_skill.exists(), "pkg SKILL.md must be created by sync")
            self.assertEqual(pkg_skill.read_bytes(), canonical_skill.read_bytes())
            self.assertEqual(canonical_skill.read_bytes(), self._VALID_SKILL_MD.encode())
            self.assertIn("src/gzkit/skills/test-skill/SKILL.md", result)

    @covers("REQ-0.0.32-08-01")
    def test_sync_pkg_surfaces_rules_resolves_canonical_from_gzkit(self) -> None:
        """sync_pkg_surfaces reads from .gzkit/rules/ and writes to src/gzkit/rules/."""
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_pkg_surfaces

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_pkg_surface(root, "rules")
            canonical_rule = root / ".gzkit" / "rules" / "test-rule.md"
            canonical_rule.parent.mkdir(parents=True)
            canonical_rule.write_text("# Test Rule\n\nContent.\n", encoding="utf-8")

            config = GzkitConfig(project_name="test")
            result = sync_pkg_surfaces(root, config)

            pkg_rule = root / "src" / "gzkit" / "rules" / "test-rule.md"
            self.assertTrue(pkg_rule.exists(), "pkg rule must be created by sync")
            self.assertEqual(pkg_rule.read_bytes(), canonical_rule.read_bytes())
            self.assertIn("src/gzkit/rules/test-rule.md", result)

    @covers("REQ-0.0.32-08-02")
    def test_sync_pkg_surfaces_dual_direction_single_call(self) -> None:
        """One sync_pkg_surfaces call writes to both src/gzkit/skills/ and src/gzkit/rules/."""
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_pkg_surfaces

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_pkg_surface(root, "skills")
            self._make_pkg_surface(root, "rules")
            skill_dir = root / ".gzkit" / "skills" / "gz-prd"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(self._VALID_SKILL_MD, encoding="utf-8")
            rules_dir = root / ".gzkit" / "rules"
            rules_dir.mkdir(parents=True)
            (rules_dir / "adr-audit.md").write_text("# ADR Audit\n", encoding="utf-8")

            config = GzkitConfig(project_name="test")
            result = sync_pkg_surfaces(root, config)

            self.assertTrue((root / "src" / "gzkit" / "skills" / "gz-prd" / "SKILL.md").exists())
            self.assertTrue((root / "src" / "gzkit" / "rules" / "adr-audit.md").exists())
            skill_paths = [p for p in result if "skills" in p]
            rule_paths = [p for p in result if "rules" in p]
            self.assertTrue(len(skill_paths) >= 1, f"Expected skill paths in result: {result}")
            self.assertTrue(len(rule_paths) >= 1, f"Expected rule paths in result: {result}")

    @covers("REQ-0.0.32-08-04")
    def test_sync_pkg_surfaces_idempotent(self) -> None:
        """Second sync_pkg_surfaces call on freshly-synced state produces no writes."""
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_pkg_surfaces

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_pkg_surface(root, "skills")
            canonical_skill = root / ".gzkit" / "skills" / "gz-prd" / "SKILL.md"
            canonical_skill.parent.mkdir(parents=True)
            canonical_skill.write_text(self._VALID_SKILL_MD, encoding="utf-8")

            config = GzkitConfig(project_name="test")
            first = sync_pkg_surfaces(root, config)
            second = sync_pkg_surfaces(root, config)

            self.assertTrue(len(first) >= 1, "First sync must write at least one file")
            self.assertEqual(second, [], f"Second sync must produce no writes; got: {second}")

    @covers("REQ-0.0.32-08-05")
    def test_sync_pkg_surfaces_chores_skips_runtime_state(self) -> None:
        """Chores runtime-state files (CHORE-LOG.md, proofs/) are never written to pkg."""
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_pkg_surfaces

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Establish chores pkg surface
            pkg_chores_dir = root / "src" / "gzkit" / "chores"
            pkg_chores_dir.mkdir(parents=True)
            chore_dir = root / ".gzkit" / "chores" / "test-chore"
            chore_dir.mkdir(parents=True)
            (chore_dir / "CHORE.md").write_text("# Test Chore\n", encoding="utf-8")
            (chore_dir / "CHORE-LOG.md").write_text("log\n", encoding="utf-8")
            proofs = chore_dir / "proofs"
            proofs.mkdir()
            (proofs / "receipt.json").write_text("{}", encoding="utf-8")

            config = GzkitConfig(project_name="test")
            sync_pkg_surfaces(root, config)

            pkg_chore = pkg_chores_dir / "test-chore"
            self.assertTrue((pkg_chore / "CHORE.md").exists(), "CHORE.md must be synced to pkg")
            self.assertFalse(
                (pkg_chore / "CHORE-LOG.md").exists(),
                "CHORE-LOG.md is runtime_state; must NOT be synced",
            )
            self.assertFalse(
                (pkg_chore / "proofs" / "receipt.json").exists(),
                "proofs/ contents are runtime_state; must NOT be synced",
            )

    @covers("REQ-0.0.32-08-02")
    def test_sync_all_calls_pkg_surface_sync(self) -> None:
        """sync_all() propagates .gzkit/skills/ to src/gzkit/skills/ when pkg is established."""
        from gzkit.config import GzkitConfig
        from gzkit.sync_surfaces import sync_all

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / ".gzkit").mkdir()
            self._make_pkg_surface(root, "skills")
            skill_dir = root / ".gzkit" / "skills" / "gz-prd"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(self._VALID_SKILL_MD, encoding="utf-8")

            config = GzkitConfig(project_name="test")
            result = sync_all(root, config, emit_event=False)

            pkg_skill = root / "src" / "gzkit" / "skills" / "gz-prd" / "SKILL.md"
            self.assertTrue(
                pkg_skill.exists(),
                "sync_all must propagate .gzkit/skills/ to src/gzkit/skills/ (REQ-0.0.32-08-02)",
            )
            self.assertIn("src/gzkit/skills/gz-prd/SKILL.md", result)


def _make_pkg_surface(root: Path, surface: str) -> None:
    """Create src/gzkit/<surface>/__init__.py to establish the dual-surface guard."""
    init = root / "src" / "gzkit" / surface / "__init__.py"
    init.parent.mkdir(parents=True, exist_ok=True)
    init.write_text("", encoding="utf-8")


class TestSyncPkgSurfacesManifestAndDocs(unittest.TestCase):
    """OBPI-0.0.32-08 REQ coverage for manifest, rule re-affirm, and check-gate REQs."""

    _REPO_ROOT = Path(__file__).resolve().parent.parent

    @covers("REQ-0.0.32-08-07")
    def test_manifest_records_skills_control_surface(self) -> None:
        """Manifest is updated by sync and contains control_surfaces with skills path."""
        manifest = self._REPO_ROOT / ".gzkit" / "manifest.json"
        self.assertTrue(manifest.exists(), "manifest.json must exist")
        import json  # noqa: PLC0415

        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertIn("control_surfaces", data, "manifest.json must have control_surfaces")
        self.assertIn(
            "skills",
            data["control_surfaces"],
            "control_surfaces must include 'skills' path (.gzkit/skills)",
        )

    @covers("REQ-0.0.32-08-09")
    def test_sync_does_not_introduce_new_pkg_skills_beyond_canonical(self) -> None:
        """OBPI-08 sync does not introduce src/gzkit/skills/ files absent from .gzkit/skills/.

        REQ-09: this OBPI must not add on-disk-not-baseline drift. sync_pkg_surfaces
        is SKILL.md-only and only writes slugs that exist canonically.
        """
        from gzkit.config import GzkitConfig  # noqa: PLC0415
        from gzkit.sync_surfaces import sync_pkg_surfaces  # noqa: PLC0415

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _make_pkg_surface(root, "skills")
            canonical_skill = root / ".gzkit" / "skills" / "gz-prd" / "SKILL.md"
            canonical_skill.parent.mkdir(parents=True)
            canonical_skill.write_text(
                "---\nname: gz-prd\ndescription: X\n"
                "lifecycle_state: active\nowner: t\nlast_reviewed: 2026-01-01\n---\n",
                encoding="utf-8",
            )
            config = GzkitConfig(project_name="test")
            sync_pkg_surfaces(root, config)

            pkg_skills = root / "src" / "gzkit" / "skills"
            synced_slugs = {
                d.name for d in pkg_skills.iterdir() if d.is_dir() and not d.name.startswith("__")
            }
            canonical_slugs = {d.name for d in (root / ".gzkit" / "skills").iterdir() if d.is_dir()}
            extra = synced_slugs - canonical_slugs - {"__pycache__"}
            self.assertEqual(
                extra,
                set(),
                f"sync_pkg_surfaces wrote skill slugs absent from canonical: {extra}",
            )

    @covers("REQ-0.0.32-08-10")
    def test_agent_sync_feature_has_req_tagged_scenario(self) -> None:
        """features/agent_sync.feature exists with @REQ-0.0.32-08-01 scenario tag."""
        feature = self._REPO_ROOT / "features" / "agent_sync.feature"
        self.assertTrue(feature.exists(), "features/agent_sync.feature must exist")
        content = feature.read_text(encoding="utf-8")
        self.assertIn(
            "@REQ-0.0.32-08-01",
            content,
            "feature file must have @REQ-0.0.32-08-01 scenario tag",
        )

    @covers("REQ-0.0.32-08-11")
    def test_skill_surface_sync_rule_documents_broadened_sync(self) -> None:
        """skill-surface-sync.md re-affirms Edit .gzkit/ first and documents broadened sync."""
        rule = self._REPO_ROOT / ".gzkit" / "rules" / "skill-surface-sync.md"
        content = rule.read_text(encoding="utf-8")
        match = re.search(r"<!--\s*rule-version:\s*(\d+)\.(\d+)\.(\d+)\s*-->", content)
        self.assertIsNotNone(match, "rule must carry a body-level rule-version marker")
        assert match is not None
        major, minor, patch = (int(match.group(i)) for i in (1, 2, 3))
        self.assertGreaterEqual(
            (major, minor, patch),
            (0, 5, 0),
            f"rule must be at or above the OBPI-08 baseline 0.5.0; found {major}.{minor}.{patch}",
        )
        self.assertIn(
            "src/gzkit/<surface>/",
            content,
            "rule must document wheel-shipping pkg copy surface",
        )
        self.assertIn(
            "Edit `.gzkit/` first",
            content,
            "rule must re-affirm 'Edit .gzkit/ first' canon",
        )

    @covers("REQ-0.0.32-08-12")
    def test_sync_surfaces_module_imports_cleanly(self) -> None:
        """sync_surfaces.py imports successfully (baseline for gz check gate)."""
        import importlib  # noqa: PLC0415

        mod = importlib.import_module("gzkit.sync_surfaces")
        self.assertTrue(
            hasattr(mod, "sync_pkg_surfaces"),
            "sync_surfaces must export sync_pkg_surfaces",
        )
        self.assertTrue(
            hasattr(mod, "sync_all"),
            "sync_surfaces must export sync_all",
        )


if __name__ == "__main__":
    unittest.main()
