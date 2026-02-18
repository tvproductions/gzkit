"""Tests for gzkit sync module."""

import tempfile
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.sync import (
    detect_project_name,
    detect_project_structure,
    extract_artifact_id,
    generate_manifest,
    parse_artifact_metadata,
    scan_existing_artifacts,
    sync_all,
)


class TestDetectProjectStructure(unittest.TestCase):
    """Tests for project structure detection."""

    def test_detects_src_directory(self) -> None:
        """Detects src/ as source root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "src").mkdir()
            (project_root / "tests").mkdir()

            structure = detect_project_structure(project_root)
            self.assertEqual(structure["source_root"], "src")
            self.assertEqual(structure["tests_root"], "tests")

    def test_detects_test_directory(self) -> None:
        """Detects test/ as tests root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            (project_root / "test").mkdir()

            structure = detect_project_structure(project_root)
            self.assertEqual(structure["tests_root"], "test")

    def test_defaults_for_missing_directories(self) -> None:
        """Uses defaults when directories don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            structure = detect_project_structure(project_root)
            self.assertEqual(structure["source_root"], "src")
            self.assertEqual(structure["tests_root"], "tests")


class TestDetectProjectName(unittest.TestCase):
    """Tests for project name detection."""

    def test_from_pyproject_toml(self) -> None:
        """Detects name from pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            pyproject = project_root / "pyproject.toml"
            pyproject.write_text('[project]\nname = "my-project"\n')

            name = detect_project_name(project_root)
            self.assertEqual(name, "my-project")

    def test_fallback_to_directory_name(self) -> None:
        """Falls back to directory name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            name = detect_project_name(project_root)
            # Should be the temp directory name
            self.assertEqual(name, project_root.name)


class TestGenerateManifest(unittest.TestCase):
    """Tests for manifest generation."""

    def test_generates_valid_manifest(self) -> None:
        """Generates manifest with all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig()

            manifest = generate_manifest(project_root, config)

            self.assertEqual(manifest["schema"], "gzkit.manifest.v1")
            self.assertIn("structure", manifest)
            self.assertIn("artifacts", manifest)
            self.assertIn("control_surfaces", manifest)
            self.assertIn("verification", manifest)
            self.assertIn("gates", manifest)

    def test_manifest_has_correct_artifacts(self) -> None:
        """Manifest includes all artifact types."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig()

            manifest = generate_manifest(project_root, config)

            artifacts = manifest["artifacts"]
            self.assertIn("prd", artifacts)
            self.assertIn("constitution", artifacts)
            self.assertIn("obpi", artifacts)
            self.assertIn("adr", artifacts)

    def test_manifest_has_verification_commands(self) -> None:
        """Manifest includes verification commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig()

            manifest = generate_manifest(project_root, config)

            verification = manifest["verification"]
            self.assertIn("lint", verification)
            self.assertIn("format", verification)
            self.assertIn("typecheck", verification)
            self.assertIn("test", verification)


class TestScanExistingArtifacts(unittest.TestCase):
    """Tests for existing artifact scanning."""

    def test_scan_empty_directory__returns_empty_lists(self) -> None:
        """Returns empty lists when design directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(result["prds"], [])
            self.assertEqual(result["adrs"], [])
            self.assertEqual(result["obpis"], [])

    def test_scan_finds_prd_files(self) -> None:
        """Finds PRD files in design/prd directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            prd_dir = project_root / "design" / "prd"
            prd_dir.mkdir(parents=True)
            (prd_dir / "PRD-TEST-1.0.0.md").write_text("# PRD")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["prds"]), 1)
            self.assertTrue(result["prds"][0].name == "PRD-TEST-1.0.0.md")

    def test_scan_finds_adr_files(self) -> None:
        """Finds ADR files in design/adr directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            adr_dir = project_root / "design" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-0.1.0.md").write_text("# ADR")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["adrs"]), 1)
            self.assertTrue(result["adrs"][0].name == "ADR-0.1.0.md")

    def test_scan_finds_nested_adrs(self) -> None:
        """Finds ADR files in subdirectories (e.g., adr-0.1.x/)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            adr_subdir = project_root / "design" / "adr" / "adr-0.1.x"
            adr_subdir.mkdir(parents=True)
            (adr_subdir / "ADR-0.1.0-test.md").write_text("# ADR")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["adrs"]), 1)
            self.assertTrue(result["adrs"][0].name == "ADR-0.1.0-test.md")

    def test_scan_ignores_legacy_global_obpi_directory(self) -> None:
        """Does not discover OBPI files in legacy design/obpis directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            obpi_dir = project_root / "design" / "obpis"
            obpi_dir.mkdir(parents=True)
            (obpi_dir / "OBPI-0.1.0-01-demo.md").write_text("# OBPI")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(result["obpis"], [])

    def test_scan_finds_obpi_files_nested_under_adr(self) -> None:
        """Finds OBPI files nested under ADR directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            obpi_dir = project_root / "design" / "adr" / "adr-0.1.x" / "ADR-0.1.0-demo" / "obpis"
            obpi_dir.mkdir(parents=True)
            (obpi_dir / "OBPI-0.1.0-02-nested.md").write_text("# OBPI")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["obpis"]), 1)
            self.assertTrue(result["obpis"][0].name == "OBPI-0.1.0-02-nested.md")

    def test_scan_with_docs_design_root(self) -> None:
        """Works with docs/design as design root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            prd_dir = project_root / "docs" / "design" / "prd"
            prd_dir.mkdir(parents=True)
            (prd_dir / "PRD-MYAPP-1.0.0.md").write_text("# PRD")

            result = scan_existing_artifacts(project_root, "docs/design")

            self.assertEqual(len(result["prds"]), 1)

    def test_scan_ignores_non_matching_files(self) -> None:
        """Ignores files that don't match PRD-/ADR- patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            prd_dir = project_root / "design" / "prd"
            prd_dir.mkdir(parents=True)
            (prd_dir / "PRD-VALID.md").write_text("# PRD")
            (prd_dir / "README.md").write_text("# README")
            (prd_dir / "notes.txt").write_text("notes")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["prds"]), 1)
            self.assertEqual(result["prds"][0].name, "PRD-VALID.md")


class TestExtractArtifactId(unittest.TestCase):
    """Tests for artifact ID extraction."""

    def test_extract_prd_id(self) -> None:
        """Extracts PRD ID from filename."""
        path = Path("/some/path/PRD-GZKIT-1.0.0.md")
        result = extract_artifact_id(path)
        self.assertEqual(result, "PRD-GZKIT-1.0.0")

    def test_extract_adr_id(self) -> None:
        """Extracts ADR ID from filename."""
        path = Path("/design/adr/ADR-0.1.0.md")
        result = extract_artifact_id(path)
        self.assertEqual(result, "ADR-0.1.0")

    def test_extract_adr_id_with_suffix(self) -> None:
        """Extracts ADR ID from filename with descriptive suffix."""
        path = Path("/design/adr/adr-0.1.x/ADR-0.1.0-enforced-governance.md")
        result = extract_artifact_id(path)
        self.assertEqual(result, "ADR-0.1.0-enforced-governance")


class TestParseArtifactMetadata(unittest.TestCase):
    """Tests for artifact metadata parsing."""

    def test_parse_adr_with_header_and_parent(self) -> None:
        """Parses canonical ID from header and parent from frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_path = Path(tmpdir) / "ADR-0.1.0-test-description.md"
            adr_path.write_text(
                "# ADR-0.1.0: test description\n\n"
                "**Status:** Draft\n"
                "**Parent PRD:** [PRD-MYAPP-1.0.0](../prd/PRD-MYAPP-1.0.0.md)\n"
            )

            result = parse_artifact_metadata(adr_path)

            self.assertEqual(result["id"], "ADR-0.1.0")
            self.assertEqual(result["parent"], "PRD-MYAPP-1.0.0")

    def test_parse_adr_no_parent__uses_filename(self) -> None:
        """Falls back to filename when no parent found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_path = Path(tmpdir) / "ADR-0.2.0-orphan.md"
            adr_path.write_text("# ADR-0.2.0: orphan\n\n**Status:** Draft\n")

            result = parse_artifact_metadata(adr_path)

            self.assertEqual(result["id"], "ADR-0.2.0")
            self.assertNotIn("parent", result)

    def test_parse_prd_extracts_id_from_header(self) -> None:
        """Extracts PRD ID from header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prd_path = Path(tmpdir) / "PRD-MYAPP-1.0.0.md"
            prd_path.write_text("# PRD-MYAPP-1.0.0: My Application\n\n## Overview\n")

            result = parse_artifact_metadata(prd_path)

            self.assertEqual(result["id"], "PRD-MYAPP-1.0.0")

    def test_parse_nonexistent_file__returns_filename_stem(self) -> None:
        """Returns filename stem when file can't be read."""
        path = Path("/nonexistent/ADR-0.1.0-missing.md")

        result = parse_artifact_metadata(path)

        self.assertEqual(result["id"], "ADR-0.1.0-missing")

    def test_parse_parent_with_obpi(self) -> None:
        """Parses parent when it's an OBPI reference."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_path = Path(tmpdir) / "ADR-0.3.0.md"
            adr_path.write_text(
                "# ADR-0.3.0: feature\n\n**Parent:** [OBPI-core](../obpis/OBPI-core.md)\n"
            )

            result = parse_artifact_metadata(adr_path)

            self.assertEqual(result["parent"], "OBPI-core")

    def test_parse_frontmatter_id_parent_and_lane(self) -> None:
        """Uses frontmatter metadata when present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_path = Path(tmpdir) / "ADR-0.3.0-pool.sample.md"
            adr_path.write_text(
                "---\n"
                "id: ADR-0.3.0-pool.sample\n"
                "parent: PRD-GZKIT-1.0.0\n"
                "lane: Heavy\n"
                "---\n\n"
                "# ADR-0.3.0: pool.sample\n"
            )

            result = parse_artifact_metadata(adr_path)

            self.assertEqual(result["id"], "ADR-0.3.0-pool.sample")
            self.assertEqual(result["parent"], "PRD-GZKIT-1.0.0")
            self.assertEqual(result["lane"], "heavy")

    def test_frontmatter_id_takes_precedence_over_short_header(self) -> None:
        """Keeps full frontmatter ID even when header only has semver."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_path = Path(tmpdir) / "ADR-0.4.0-pool.heavy-lane.md"
            adr_path.write_text(
                "---\nid: ADR-0.4.0-pool.heavy-lane\n---\n\n# ADR-0.4.0: pool.heavy-lane\n"
            )

            result = parse_artifact_metadata(adr_path)

            self.assertEqual(result["id"], "ADR-0.4.0-pool.heavy-lane")


class TestSyncControlSurfaces(unittest.TestCase):
    """Tests for full control-surface synchronization."""

    def test_sync_includes_skills_in_generated_surfaces(self) -> None:
        """Generated AGENTS/CLAUDE/Copilot files include the skill catalog."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            skill_dir = project_root / config.paths.skills / "demo-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                "# SKILL.md\n\n## Demo Skill\n\nRun the demo command.\n"
            )

            sync_all(project_root, config)

            agents = (project_root / config.paths.agents_md).read_text()
            claude = (project_root / config.paths.claude_md).read_text()
            copilot = (project_root / config.paths.copilot_instructions).read_text()

            self.assertIn("`demo-skill`", agents)
            self.assertIn(".gzkit/skills/demo-skill/SKILL.md", agents)
            self.assertIn("`demo-skill`", claude)
            self.assertIn("`demo-skill`", copilot)

    def test_sync_mirrors_skills_into_all_tool_directories(self) -> None:
        """Canonical skills are mirrored into Claude, Codex, and Copilot paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            skill_dir = project_root / config.paths.skills / "audit-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            source_file = skill_dir / "SKILL.md"
            source_file.write_text("# SKILL.md\n\n## Audit Skill\n\nAudit behavior.\n")

            updated = sync_all(project_root, config)
            claude_mirror = project_root / config.paths.claude_skills / "audit-skill" / "SKILL.md"
            codex_mirror = project_root / config.paths.codex_skills / "audit-skill" / "SKILL.md"
            copilot_mirror = project_root / config.paths.copilot_skills / "audit-skill" / "SKILL.md"

            self.assertTrue(claude_mirror.exists())
            self.assertTrue(codex_mirror.exists())
            self.assertTrue(copilot_mirror.exists())
            self.assertEqual(claude_mirror.read_text(), source_file.read_text())
            self.assertEqual(codex_mirror.read_text(), source_file.read_text())
            self.assertEqual(copilot_mirror.read_text(), source_file.read_text())
            self.assertIn(".claude/skills/audit-skill/SKILL.md", updated)
            self.assertIn(".agents/skills/audit-skill/SKILL.md", updated)
            self.assertIn(".github/skills/audit-skill/SKILL.md", updated)

    def test_sync_bootstraps_canonical_from_legacy_copilot_mirror(self) -> None:
        """When canonical is empty, sync seeds it from legacy Copilot skills."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            legacy_skill = project_root / config.paths.copilot_skills / "legacy-skill"
            legacy_skill.mkdir(parents=True, exist_ok=True)
            (legacy_skill / "SKILL.md").write_text("# SKILL.md\n\n## Legacy Skill\n")

            sync_all(project_root, config)

            canonical_file = project_root / config.paths.skills / "legacy-skill" / "SKILL.md"
            self.assertTrue(canonical_file.exists())


if __name__ == "__main__":
    unittest.main()
