"""Tests for gzkit sync module.

@covers ADR-0.17.0  OBPI-0.17.0-03 slim-claudemd-template
@covers ADR-0.17.0  OBPI-0.17.0-05 manifest-update-and-final-sync
"""

import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from jsonschema import Draft202012Validator

from gzkit.config import GzkitConfig
from gzkit.schemas import load_schema
from gzkit.sync import (
    collect_canonical_sync_blockers,
    collect_skills_catalog,
    detect_project_name,
    detect_project_structure,
    extract_artifact_id,
    find_stale_mirror_paths,
    generate_manifest,
    parse_artifact_metadata,
    scan_existing_artifacts,
    sync_all,
)


def _skill_markdown(
    name: str,
    *,
    description: str = "Demo skill",
    lifecycle_state: str = "active",
    last_reviewed: str | None = None,
    lifecycle_transition_from: str | None = None,
    lifecycle_transition_date: str | None = None,
    lifecycle_transition_reason: str | None = None,
    lifecycle_transition_evidence: str | None = None,
    compatibility: str | None = None,
    invocation: str | None = None,
    gz_command: str | None = None,
    deprecation_replaced_by: str | None = None,
    deprecation_migration: str | None = None,
    deprecation_communication: str | None = None,
    deprecation_announced_on: str | None = None,
    retired_on: str | None = None,
    metadata: dict[str, str] | None = None,
) -> str:
    lines = [
        "---",
        f"name: {name}",
        f"description: {description}",
        f"lifecycle_state: {lifecycle_state}",
        "owner: gzkit-governance",
        f"last_reviewed: {last_reviewed or date.today().isoformat()}",
    ]
    if compatibility is not None:
        lines.append(f"compatibility: {compatibility}")
    if invocation is not None:
        lines.append(f"invocation: {invocation}")
    if gz_command is not None:
        lines.append(f"gz_command: {gz_command}")
    if lifecycle_transition_from is not None:
        lines.append(f"lifecycle_transition_from: {lifecycle_transition_from}")
    if lifecycle_transition_date is not None:
        lines.append(f"lifecycle_transition_date: {lifecycle_transition_date}")
    if lifecycle_transition_reason is not None:
        lines.append(f"lifecycle_transition_reason: {lifecycle_transition_reason}")
    if lifecycle_transition_evidence is not None:
        lines.append(f"lifecycle_transition_evidence: {lifecycle_transition_evidence}")
    if deprecation_replaced_by is not None:
        lines.append(f"deprecation_replaced_by: {deprecation_replaced_by}")
    if deprecation_migration is not None:
        lines.append(f"deprecation_migration: {deprecation_migration}")
    if deprecation_communication is not None:
        lines.append(f"deprecation_communication: {deprecation_communication}")
    if deprecation_announced_on is not None:
        lines.append(f"deprecation_announced_on: {deprecation_announced_on}")
    if retired_on is not None:
        lines.append(f"retired_on: {retired_on}")
    if metadata is not None:
        lines.append("metadata:")
        for key, value in metadata.items():
            lines.append(f"  {key}: {value}")
    lines.extend(["---", "", "# SKILL.md", "", "Skill body.", ""])
    return "\n".join(lines)


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
            pyproject.write_text('[project]\nname = "my-project"\n', encoding="utf-8")

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

    def test_manifest_includes_default_codex_config_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = generate_manifest(Path(tmpdir), GzkitConfig())

            self.assertEqual(
                manifest["control_surfaces"].get("codex_config"),
                ".codex/config.toml",
            )

    def test_shared_schema_keeps_v1_codex_config_optional(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = generate_manifest(Path(tmpdir), GzkitConfig())
        manifest["schema"] = "gzkit.manifest.v1"
        for key in ("canonical_rules", "canonical_schemas", "claude_rules"):
            manifest["control_surfaces"].pop(key)
        for key in ("bdd", "docs"):
            manifest["verification"].pop(key)
        manifest["control_surfaces"].pop("codex_config")
        schema = load_schema("manifest")

        errors = list(Draft202012Validator(schema).iter_errors(manifest))

        self.assertEqual(errors, [], [error.message for error in errors])

    def test_generated_v2_manifest_matches_shared_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = generate_manifest(Path(tmpdir), GzkitConfig())
        schema = load_schema("manifest")

        errors = list(Draft202012Validator(schema).iter_errors(manifest))

        self.assertEqual(errors, [], [error.message for error in errors])

    def test_generates_valid_manifest(self) -> None:
        """Generates manifest with all required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig()

            manifest = generate_manifest(project_root, config)

            self.assertEqual(manifest["schema"], "gzkit.manifest.v2")
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

    def test_manifest_includes_canonical_rules_and_schemas(self) -> None:
        """Manifest control_surfaces includes canonical_rules and canonical_schemas."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig()

            manifest = generate_manifest(project_root, config)

            surfaces = manifest["control_surfaces"]
            self.assertIn("canonical_rules", surfaces)
            self.assertIn("canonical_schemas", surfaces)
            self.assertEqual(surfaces["canonical_rules"], ".gzkit/rules")
            self.assertEqual(surfaces["canonical_schemas"], ".gzkit/schemas")

    def test_manifest_control_surfaces_complete(self) -> None:
        """Manifest control_surfaces includes all expected keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig()

            manifest = generate_manifest(project_root, config)

            surfaces = manifest["control_surfaces"]
            expected_keys = {
                "agents_md",
                "claude_md",
                "hooks",
                "skills",
                "canonical_rules",
                "canonical_schemas",
                "claude_skills",
                "codex_config",
                "codex_skills",
                "claude_rules",
                "personas",
            }
            self.assertEqual(set(surfaces.keys()), expected_keys)


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
            (prd_dir / "PRD-TEST-1.0.0.md").write_text("# PRD", encoding="utf-8")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["prds"]), 1)
            self.assertTrue(result["prds"][0].name == "PRD-TEST-1.0.0.md")

    def test_scan_finds_adr_files(self) -> None:
        """Finds ADR files in design/adr directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            adr_dir = project_root / "design" / "adr"
            adr_dir.mkdir(parents=True)
            (adr_dir / "ADR-0.1.0.md").write_text("# ADR", encoding="utf-8")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["adrs"]), 1)
            self.assertTrue(result["adrs"][0].name == "ADR-0.1.0.md")

    def test_scan_finds_nested_adrs(self) -> None:
        """Finds ADR files in subdirectories (e.g., adr-0.1.x/)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            adr_subdir = project_root / "design" / "adr" / "adr-0.1.x"
            adr_subdir.mkdir(parents=True)
            (adr_subdir / "ADR-0.1.0-test.md").write_text("# ADR", encoding="utf-8")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["adrs"]), 1)
            self.assertTrue(result["adrs"][0].name == "ADR-0.1.0-test.md")

    def test_scan_ignores_legacy_global_obpi_directory(self) -> None:
        """Does not discover OBPI files in legacy design/obpis directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            obpi_dir = project_root / "design" / "obpis"
            obpi_dir.mkdir(parents=True)
            (obpi_dir / "OBPI-0.1.0-01-demo.md").write_text("# OBPI", encoding="utf-8")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(result["obpis"], [])

    def test_scan_finds_obpi_files_nested_under_adr(self) -> None:
        """Finds OBPI files nested under ADR directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            obpi_dir = project_root / "design" / "adr" / "adr-0.1.x" / "ADR-0.1.0-demo" / "obpis"
            obpi_dir.mkdir(parents=True)
            (obpi_dir / "OBPI-0.1.0-02-nested.md").write_text("# OBPI", encoding="utf-8")

            result = scan_existing_artifacts(project_root, "design")

            self.assertEqual(len(result["obpis"]), 1)
            self.assertTrue(result["obpis"][0].name == "OBPI-0.1.0-02-nested.md")

    def test_scan_with_docs_design_root(self) -> None:
        """Works with docs/design as design root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            prd_dir = project_root / "docs" / "design" / "prd"
            prd_dir.mkdir(parents=True)
            (prd_dir / "PRD-MYAPP-1.0.0.md").write_text("# PRD", encoding="utf-8")

            result = scan_existing_artifacts(project_root, "docs/design")

            self.assertEqual(len(result["prds"]), 1)

    def test_scan_ignores_non_matching_files(self) -> None:
        """Ignores files that don't match PRD-/ADR- patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            prd_dir = project_root / "design" / "prd"
            prd_dir.mkdir(parents=True)
            (prd_dir / "PRD-VALID.md").write_text("# PRD", encoding="utf-8")
            (prd_dir / "README.md").write_text("# README", encoding="utf-8")
            (prd_dir / "notes.txt").write_text("notes", encoding="utf-8")

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
                "**Parent PRD:** [PRD-MYAPP-1.0.0](../prd/PRD-MYAPP-1.0.0.md)\n",
                encoding="utf-8",
            )

            result = parse_artifact_metadata(adr_path)

            self.assertEqual(result["id"], "ADR-0.1.0")
            self.assertEqual(result["parent"], "PRD-MYAPP-1.0.0")

    def test_parse_adr_no_parent__uses_filename(self) -> None:
        """Falls back to filename when no parent found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_path = Path(tmpdir) / "ADR-0.2.0-orphan.md"
            adr_path.write_text("# ADR-0.2.0: orphan\n\n**Status:** Draft\n", encoding="utf-8")

            result = parse_artifact_metadata(adr_path)

            self.assertEqual(result["id"], "ADR-0.2.0")
            self.assertNotIn("parent", result)

    def test_parse_prd_extracts_id_from_header(self) -> None:
        """Extracts PRD ID from header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            prd_path = Path(tmpdir) / "PRD-MYAPP-1.0.0.md"
            prd_path.write_text(
                "# PRD-MYAPP-1.0.0: My Application\n\n## Overview\n", encoding="utf-8"
            )

            result = parse_artifact_metadata(prd_path)

            self.assertEqual(result["id"], "PRD-MYAPP-1.0.0")

    def test_parse_nonexistent_file__returns_filename_stem(self) -> None:
        """Returns filename stem when file can't be read."""
        path = Path("/nonexistent/ADR-0.1.0-missing.md")

        result = parse_artifact_metadata(path)

        self.assertEqual(result["id"], "ADR-0.1.0-missing")

    def test_malformed_frontmatter_yields_no_id_rather_than_a_stem_guess(self) -> None:
        """A malformed block must not resolve to an invented id (GHI #736 residual).

        The function already refused to *parse* a malformed block, but still
        returned the stem-derived id it had seeded before reading -- so it
        handed back exactly the guess its own comment said it refused. That
        left callers unable to distinguish "no frontmatter, id taken from the
        stem" from "frontmatter present but unreadable, id invented", which are
        different conditions with different repairs.

        Absence is asserted alongside as the negative control: a genuinely
        frontmatter-less file still resolves to its stem, so the refusal is
        scoped to damage rather than applied to every id-less artifact.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            malformed = Path(tmpdir) / "ADR-0.5.0-truncated.md"
            malformed.write_text(
                "---\nid: ADR-0.5.0-truncated\n\n# ADR-0.5.0: no closing marker\n",
                encoding="utf-8",
            )

            self.assertNotIn("id", parse_artifact_metadata(malformed))

    def test_absent_frontmatter_still_resolves_to_the_stem(self) -> None:
        """Negative control for the refusal above: absent is not malformed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plain = Path(tmpdir) / "ADR-0.5.0-plain.md"
            # No ADR-shaped H1 either, so the stem is the only id source left;
            # a header would otherwise supply one and mask the distinction.
            plain.write_text("Body prose with no heading.\n", encoding="utf-8")

            self.assertEqual(parse_artifact_metadata(plain)["id"], "ADR-0.5.0-plain")

    def test_parse_parent_with_obpi(self) -> None:
        """Parses parent when it's an OBPI reference."""
        with tempfile.TemporaryDirectory() as tmpdir:
            adr_path = Path(tmpdir) / "ADR-0.3.0.md"
            adr_path.write_text(
                "# ADR-0.3.0: feature\n\n**Parent:** [OBPI-core](../obpis/OBPI-core.md)\n",
                encoding="utf-8",
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
                "# ADR-0.3.0: pool.sample\n",
                encoding="utf-8",
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
                "---\nid: ADR-0.4.0-pool.heavy-lane\n---\n\n# ADR-0.4.0: pool.heavy-lane\n",
                encoding="utf-8",
            )

            result = parse_artifact_metadata(adr_path)

            self.assertEqual(result["id"], "ADR-0.4.0-pool.heavy-lane")


class TestSyncControlSurfaces(unittest.TestCase):
    """Tests for full control-surface synchronization."""

    def test_sync_generated_surfaces_include_guarded_git_sync_pipeline_contract(self) -> None:
        """Generated surfaces carry the guarded sync-before-accounting contract."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            sync_all(project_root, config)

            agents = (project_root / config.paths.agents_md).read_text(encoding="utf-8")
            claude = (project_root / config.paths.claude_md).read_text(encoding="utf-8")

            self.assertIn("guarded git sync -> completion", agents)
            self.assertIn("uv run gz obpi pipeline <OBPI-ID>", agents)
            self.assertIn("uv run gz git-sync --apply --lint --test", agents)
            self.assertIn("uv run gz check", agents)
            self.assertIn("Documentation/process/template-only changes stay", agents)
            self.assertNotIn("uv run -m unittest discover tests", agents)
            # Slim CLAUDE.md delegates governance via @AGENTS.md directive
            self.assertIn("AGENTS.md", claude)

    def test_sync_manifest_uses_gz_native_verification_defaults(self) -> None:
        """Generated manifests use gz-native verification commands."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            sync_all(project_root, config)

            manifest = (project_root / ".gzkit" / "manifest.json").read_text(encoding="utf-8")
            self.assertIn('"test": "uv run gz test"', manifest)
            self.assertIn('"lint": "uv run gz lint"', manifest)
            self.assertIn('"typecheck": "uv run gz typecheck"', manifest)
            self.assertIn('"docs": "uv run mkdocs build --strict"', manifest)
            self.assertIn('"bdd": "uv run -m behave features/"', manifest)

    def test_sync_points_generated_surfaces_to_skill_catalog_command(self) -> None:
        """Generated AGENTS/CLAUDE files avoid embedding the skill catalog."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            skill_dir = project_root / config.paths.skills / "demo-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                "# SKILL.md\n\n## Demo Skill\n\nRun the demo command.\n", encoding="utf-8"
            )

            sync_all(project_root, config)

            agents = (project_root / config.paths.agents_md).read_text(encoding="utf-8")
            claude = (project_root / config.paths.claude_md).read_text(encoding="utf-8")

            self.assertNotIn("`demo-skill`", agents)
            self.assertIn("uv run gz skill list", agents)
            self.assertIn(".gzkit/skills/<skill-name>/", agents)
            # Slim CLAUDE.md no longer includes skill catalog
            self.assertNotIn("`demo-skill`", claude)

    def test_sync_skills_catalog_indirection_omits_frontmatter_description(self) -> None:
        """AGENTS points to the live skill catalog instead of embedding descriptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            skill_dir = project_root / config.paths.skills / "demo-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(_skill_markdown("demo-skill"), encoding="utf-8")

            sync_all(project_root, config)

            agents = (project_root / config.paths.agents_md).read_text(encoding="utf-8")
            self.assertNotIn("`demo-skill`", agents)
            self.assertIn("uv run gz skill list", agents)
            self.assertNotIn("---: ---", agents)

    def test_sync_mirrors_skills_into_all_tool_directories(self) -> None:
        """Canonical skills are mirrored into every declared vendor skill path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            skill_dir = project_root / config.paths.skills / "audit-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            source_file = skill_dir / "SKILL.md"
            source_file.write_text(
                "# SKILL.md\n\n## Audit Skill\n\nAudit behavior.\n", encoding="utf-8"
            )

            updated = sync_all(project_root, config)
            claude_mirror = project_root / config.paths.claude_skills / "audit-skill" / "SKILL.md"
            codex_mirror = project_root / config.paths.codex_skills / "audit-skill" / "SKILL.md"

            self.assertTrue(claude_mirror.exists())
            self.assertTrue(codex_mirror.exists())
            source_text = source_file.read_text(encoding="utf-8")
            self.assertEqual(claude_mirror.read_text(encoding="utf-8"), source_text)
            self.assertEqual(codex_mirror.read_text(encoding="utf-8"), source_text)
            self.assertIn(".claude/skills/audit-skill/SKILL.md", updated)
            self.assertIn(".agents/skills/audit-skill/SKILL.md", updated)

    def test_sync_bootstraps_canonical_from_legacy_github_skills_mirror(self) -> None:
        """When canonical is empty, sync seeds it from a legacy `.github/skills` tree.

        The Copilot vendor is retired (GHI #924), but the legacy path stays a
        bootstrap CANDIDATE so an adopter migrating an old tree is still seeded.
        Hence the literal rather than a config field: nothing declares it now."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            legacy_skill = project_root / ".github/skills" / "legacy-skill"
            legacy_skill.mkdir(parents=True, exist_ok=True)
            (legacy_skill / "SKILL.md").write_text(
                "# SKILL.md\n\n## Legacy Skill\n", encoding="utf-8"
            )

            sync_all(project_root, config)

            canonical_file = project_root / config.paths.skills / "legacy-skill" / "SKILL.md"
            self.assertTrue(canonical_file.exists())

    def test_sync_outputs_deterministic_updated_paths_for_unchanged_inputs(self) -> None:
        """Second and third sync runs on unchanged input return identical updated lists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            skill_dir = project_root / config.paths.skills / "demo-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(_skill_markdown("demo-skill"), encoding="utf-8")
            (skill_dir / "notes.md").write_text("extra canonical file\n", encoding="utf-8")

            sync_all(project_root, config)
            second = sync_all(project_root, config)
            third = sync_all(project_root, config)

            self.assertEqual(second, third)
            self.assertEqual(second, sorted(second))

    def test_find_stale_mirror_paths_is_explicit_and_non_destructive(self) -> None:
        """Stale mirror paths are detected and preserved for manual recovery."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            canonical_skill = project_root / config.paths.skills / "demo-skill"
            canonical_skill.mkdir(parents=True, exist_ok=True)
            (canonical_skill / "SKILL.md").write_text(
                _skill_markdown("demo-skill"), encoding="utf-8"
            )

            stale_dir = project_root / config.paths.claude_skills / "stale-skill"
            stale_dir.mkdir(parents=True, exist_ok=True)
            (stale_dir / "SKILL.md").write_text(_skill_markdown("stale-skill"), encoding="utf-8")

            stale_file = project_root / config.paths.codex_skills / "demo-skill" / "extra.txt"
            stale_file.parent.mkdir(parents=True, exist_ok=True)
            stale_file.write_text("stale file\n", encoding="utf-8")

            sync_all(project_root, config)
            stale_paths = find_stale_mirror_paths(project_root, config)

            self.assertIn(".claude/skills/stale-skill", stale_paths)
            self.assertIn(".agents/skills/demo-skill/extra.txt", stale_paths)
            self.assertTrue(stale_dir.exists())
            self.assertTrue(stale_file.exists())

    def test_generated_claude_redirect_is_not_mirrored_into_a_foreign_root(self) -> None:
        """The mirror honours the nested writer's own foreign-root exclusion.

        ``sync_skill_mirror`` runs downstream of ``sync_nested_agents_md``, so the
        canonical tree it copies already carries that writer's output -- an
        ``AGENTS.md`` and its ``CLAUDE.md`` redirect. A wholesale ``rglob`` copy
        re-delivers the redirect into every mirror root, including a vendor's whose
        tree carries its own discovery convention and which the writer therefore
        declined to write into (GHI #925). The semantic under test is the writer's:
        no vendor's ``surface_root`` is seeded with another vendor's discovery file.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            canonical = project_root / config.paths.skills
            demo_skill = canonical / "demo-skill"
            demo_skill.mkdir(parents=True, exist_ok=True)
            (demo_skill / "SKILL.md").write_text(_skill_markdown("demo-skill"), encoding="utf-8")
            # Written WITHOUT the generated-surface marker on purpose. A marker-bearing
            # redirect is reaped by the stale sweep in a tree this small -- no rule is
            # scoped to the canonical skills dir, so the nested writer emits no
            # ``AGENTS.md`` there and therefore no redirect beside it. The unmarked form
            # is preserved (``test_hand_written_claude_md_is_preserved``), which is what
            # puts a ``CLAUDE.md`` in the canonical tree for ``rglob`` to pick up -- the
            # precondition the defect needs.
            (canonical / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")

            sync_all(project_root, config)

            codex_redirect = project_root / config.paths.codex_skills / "CLAUDE.md"
            claude_redirect = project_root / config.paths.claude_skills / "CLAUDE.md"

            self.assertFalse(
                codex_redirect.exists(),
                "a foreign vendor's surface_root must not receive a CLAUDE.md",
            )
            self.assertTrue(
                claude_redirect.exists(),
                "the exclusion must not overshoot into Claude's own surface_root",
            )

    def test_forbidden_nested_surface_in_a_foreign_root_is_reported_stale(self) -> None:
        """A canonical file of the same name does not excuse a forbidden mirror copy.

        ``NESTED_SURFACE_NAMES`` members are normally exempt from the stale sweep,
        because the canonical tree legitimately carries them. That blanket exemption
        is why a foreign-root ``CLAUDE.md`` survived every sweep before GHI #925: the
        sweep saw a generated-surface name and skipped it. The exemption must yield
        to the forbidden set, so a redirect sitting where no vendor may claim one is
        surfaced for the operator's non-destructive recovery rather than preserved.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            demo_skill = project_root / config.paths.skills / "demo-skill"
            demo_skill.mkdir(parents=True, exist_ok=True)
            (demo_skill / "SKILL.md").write_text(_skill_markdown("demo-skill"), encoding="utf-8")

            sync_all(project_root, config)

            leaked = project_root / config.paths.codex_skills / "CLAUDE.md"
            leaked.write_text("@AGENTS.md\n", encoding="utf-8")
            kept = project_root / config.paths.claude_skills / "CLAUDE.md"
            kept.parent.mkdir(parents=True, exist_ok=True)
            kept.write_text("@AGENTS.md\n", encoding="utf-8")

            stale_paths = find_stale_mirror_paths(project_root, config)

            self.assertIn(".agents/skills/CLAUDE.md", stale_paths)
            self.assertNotIn(".claude/skills/CLAUDE.md", stale_paths)
            self.assertTrue(leaked.exists(), "the sweep reports, it never deletes")

    def test_canonical_sync_preflight_blocks_missing_skill_frontmatter(self) -> None:
        """Canonical corruption is reported as a blocking preflight error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            broken_skill = project_root / config.paths.skills / "broken-skill"
            broken_skill.mkdir(parents=True, exist_ok=True)
            (broken_skill / "SKILL.md").write_text(
                "# SKILL.md\n\nMissing frontmatter.\n", encoding="utf-8"
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertTrue(
                any(
                    blocker.endswith("broken-skill/SKILL.md: missing YAML frontmatter.")
                    for blocker in blockers
                )
            )

    def test_canonical_sync_preflight_allows_bootstrap_candidate_when_canonical_empty(self) -> None:
        """Empty canonical root is non-blocking when a legacy bootstrap candidate exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            legacy_skill = project_root / ".github/skills" / "legacy-skill"
            legacy_skill.mkdir(parents=True, exist_ok=True)
            (legacy_skill / "SKILL.md").write_text(
                _skill_markdown("legacy-skill"), encoding="utf-8"
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertEqual(blockers, [])

    def test_canonical_sync_preflight_blocks_invalid_metadata_govzero_layer(self) -> None:
        """Invalid known metadata values are blocking preflight errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            broken_skill = project_root / config.paths.skills / "broken-skill"
            broken_skill.mkdir(parents=True, exist_ok=True)
            (broken_skill / "SKILL.md").write_text(
                _skill_markdown(
                    "broken-skill",
                    metadata={"govzero_layer": "Layer 99 - Unknown"},
                ),
                encoding="utf-8",
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertTrue(
                any(
                    "invalid metadata.govzero_layer 'Layer 99 - Unknown'" in blocker
                    for blocker in blockers
                )
            )

    def test_canonical_sync_preflight_blocks_overlong_skill_description(self) -> None:
        """Canonical descriptions must satisfy all mirrored harness metadata limits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            broken_skill = project_root / config.paths.skills / "broken-skill"
            broken_skill.mkdir(parents=True, exist_ok=True)
            (broken_skill / "SKILL.md").write_text(
                _skill_markdown("broken-skill", description="x" * 1025), encoding="utf-8"
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertTrue(
                any("maximum is 1024 for Claude Code and Codex" in blocker for blocker in blockers)
            )

    def test_canonical_sync_preflight_allows_unknown_metadata_keys(self) -> None:
        """Unknown metadata keys remain allowed for compatibility."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            skill_dir = project_root / config.paths.skills / "demo-skill"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                _skill_markdown(
                    "demo-skill",
                    metadata={
                        "govzero_layer": "Layer 1 - Evidence Gathering",
                        "custom-key": "custom-value",
                    },
                ),
                encoding="utf-8",
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertEqual(blockers, [])

    def test_canonical_sync_preflight_blocks_stale_last_reviewed(self) -> None:
        """Stale lifecycle review metadata is a blocking preflight error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            stale_date = (date.today() - timedelta(days=120)).isoformat()

            broken_skill = project_root / config.paths.skills / "broken-skill"
            broken_skill.mkdir(parents=True, exist_ok=True)
            (broken_skill / "SKILL.md").write_text(
                _skill_markdown("broken-skill", last_reviewed=stale_date), encoding="utf-8"
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertTrue(any("older than 90 days" in blocker for blocker in blockers))

    def test_canonical_sync_preflight_blocks_missing_deprecation_fields(self) -> None:
        """Deprecated skills must provide communication metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            broken_skill = project_root / config.paths.skills / "broken-skill"
            broken_skill.mkdir(parents=True, exist_ok=True)
            (broken_skill / "SKILL.md").write_text(
                _skill_markdown("broken-skill", lifecycle_state="deprecated"), encoding="utf-8"
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertTrue(
                any(
                    "missing frontmatter field 'deprecation_replaced_by'" in blocker
                    for blocker in blockers
                )
            )

    def test_canonical_sync_preflight_blocks_retired_without_retired_on(self) -> None:
        """Retired skills must include retired_on evidence metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            broken_skill = project_root / config.paths.skills / "broken-skill"
            broken_skill.mkdir(parents=True, exist_ok=True)
            (broken_skill / "SKILL.md").write_text(
                _skill_markdown(
                    "broken-skill",
                    lifecycle_state="retired",
                    deprecation_replaced_by="new-skill",
                    deprecation_migration="See migration guide",
                    deprecation_communication="Announced in release notes",
                    deprecation_announced_on=date.today().isoformat(),
                ),
                encoding="utf-8",
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertTrue(
                any("missing frontmatter field 'retired_on'" in blocker for blocker in blockers)
            )

    def test_canonical_sync_preflight_blocks_incomplete_transition_metadata(self) -> None:
        """Transition metadata must be fully specified when declared."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            broken_skill = project_root / config.paths.skills / "broken-skill"
            broken_skill.mkdir(parents=True, exist_ok=True)
            (broken_skill / "SKILL.md").write_text(
                _skill_markdown(
                    "broken-skill",
                    lifecycle_state="active",
                    lifecycle_transition_from="draft",
                ),
                encoding="utf-8",
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertTrue(
                any("transition metadata incomplete" in blocker for blocker in blockers)
            )

    def test_canonical_sync_preflight_blocks_unsupported_transition(self) -> None:
        """Unsupported lifecycle transitions fail canonical preflight."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            broken_skill = project_root / config.paths.skills / "broken-skill"
            broken_skill.mkdir(parents=True, exist_ok=True)
            (broken_skill / "SKILL.md").write_text(
                _skill_markdown(
                    "broken-skill",
                    lifecycle_state="retired",
                    lifecycle_transition_from="active",
                    lifecycle_transition_date=date.today().isoformat(),
                    lifecycle_transition_reason="Retired immediately",
                    lifecycle_transition_evidence="No intermediate deprecation phase.",
                    deprecation_replaced_by="new-skill",
                    deprecation_migration="See migration guide",
                    deprecation_communication="Announced in release notes",
                    deprecation_announced_on=date.today().isoformat(),
                    retired_on=date.today().isoformat(),
                ),
                encoding="utf-8",
            )

            blockers = collect_canonical_sync_blockers(project_root, config)
            self.assertTrue(
                any("unsupported lifecycle transition" in blocker for blocker in blockers)
            )

    def test_collect_skills_catalog_reads_category_from_frontmatter(self) -> None:
        """Skill catalog collection extracts the category field from frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            skill_dir = project_root / config.paths.skills / "gz-plan"
            skill_dir.mkdir(parents=True, exist_ok=True)
            (skill_dir / "SKILL.md").write_text(
                "---\nname: gz-plan\ndescription: Create ADR artifacts.\n"
                "category: adr-lifecycle\nlifecycle_state: active\n"
                "owner: gzkit-governance\nlast_reviewed: 2026-03-15\n---\n",
                encoding="utf-8",
            )

            skills = collect_skills_catalog(project_root, config.paths.skills)
            self.assertEqual(len(skills), 1)
            self.assertEqual(skills[0]["category"], "adr-lifecycle")

    def test_collect_skills_catalog_excludes_retired_skills(self) -> None:
        """Retired skills are excluded from the catalog."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            active_skill = project_root / config.paths.skills / "gz-plan"
            active_skill.mkdir(parents=True, exist_ok=True)
            (active_skill / "SKILL.md").write_text(
                "---\nname: gz-plan\ndescription: Create ADR artifacts.\n"
                "category: adr-lifecycle\nlifecycle_state: active\n"
                "owner: gzkit-governance\nlast_reviewed: 2026-03-15\n---\n",
                encoding="utf-8",
            )

            retired_skill = project_root / config.paths.skills / "old-skill"
            retired_skill.mkdir(parents=True, exist_ok=True)
            (retired_skill / "SKILL.md").write_text(
                _skill_markdown(
                    "old-skill",
                    lifecycle_state="retired",
                    deprecation_replaced_by="gz-plan",
                    deprecation_migration="Use /gz-plan",
                    deprecation_communication="Consolidated",
                    deprecation_announced_on=date.today().isoformat(),
                    retired_on=date.today().isoformat(),
                ),
                encoding="utf-8",
            )

            skills = collect_skills_catalog(project_root, config.paths.skills)
            names = [s["name"] for s in skills]
            self.assertIn("gz-plan", names)
            self.assertNotIn("old-skill", names)

    def test_find_stale_mirror_paths_includes_retired_skill_mirrors(self) -> None:
        """Mirrors of retired skills are reported as stale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            # Active canonical skill
            active_skill = project_root / config.paths.skills / "demo-skill"
            active_skill.mkdir(parents=True, exist_ok=True)
            (active_skill / "SKILL.md").write_text(_skill_markdown("demo-skill"), encoding="utf-8")

            # Retired canonical skill
            retired_skill = project_root / config.paths.skills / "old-skill"
            retired_skill.mkdir(parents=True, exist_ok=True)
            (retired_skill / "SKILL.md").write_text(
                _skill_markdown(
                    "old-skill",
                    lifecycle_state="retired",
                    deprecation_replaced_by="demo-skill",
                    deprecation_migration="Use /demo-skill",
                    deprecation_communication="Consolidated",
                    deprecation_announced_on=date.today().isoformat(),
                    retired_on=date.today().isoformat(),
                ),
                encoding="utf-8",
            )

            # Mirror of retired skill (leftover from before filtering)
            retired_mirror = project_root / config.paths.claude_skills / "old-skill"
            retired_mirror.mkdir(parents=True, exist_ok=True)
            (retired_mirror / "SKILL.md").write_text(
                _skill_markdown(
                    "old-skill",
                    lifecycle_state="retired",
                    deprecation_replaced_by="demo-skill",
                    deprecation_migration="Use /demo-skill",
                    deprecation_communication="Consolidated",
                    deprecation_announced_on=date.today().isoformat(),
                    retired_on=date.today().isoformat(),
                ),
                encoding="utf-8",
            )

            stale_paths = find_stale_mirror_paths(project_root, config)
            self.assertIn(".claude/skills/old-skill", stale_paths)

    def test_sync_skill_mirrors_skips_retired_skills(self) -> None:
        """Mirror sync does not copy retired skills to vendor mirrors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            active_skill = project_root / config.paths.skills / "demo-skill"
            active_skill.mkdir(parents=True, exist_ok=True)
            (active_skill / "SKILL.md").write_text(_skill_markdown("demo-skill"), encoding="utf-8")

            retired_skill = project_root / config.paths.skills / "old-skill"
            retired_skill.mkdir(parents=True, exist_ok=True)
            (retired_skill / "SKILL.md").write_text(
                _skill_markdown(
                    "old-skill",
                    lifecycle_state="retired",
                    deprecation_replaced_by="demo-skill",
                    deprecation_migration="Use /demo-skill",
                    deprecation_communication="Consolidated",
                    deprecation_announced_on=date.today().isoformat(),
                    retired_on=date.today().isoformat(),
                ),
                encoding="utf-8",
            )

            sync_all(project_root, config)

            # Active skill should be mirrored
            self.assertTrue(
                (project_root / config.paths.claude_skills / "demo-skill" / "SKILL.md").exists()
            )
            # Retired skill should NOT be mirrored
            self.assertFalse(
                (project_root / config.paths.claude_skills / "old-skill" / "SKILL.md").exists()
            )

    def test_render_skills_catalog_categorized_groups_by_category(self) -> None:
        """Categorized renderer groups skills under category headers."""
        from gzkit.sync import render_skills_catalog

        skills = [
            {
                "name": "gz-plan",
                "description": "Create ADR.",
                "category": "adr-lifecycle",
                "path": ".gzkit/skills/gz-plan/SKILL.md",
            },
            {
                "name": "lint",
                "description": "Run linting.",
                "category": "code-quality",
                "path": ".gzkit/skills/lint/SKILL.md",
            },
            {
                "name": "gz-attest",
                "description": "Record attestation.",
                "category": "adr-lifecycle",
                "path": ".gzkit/skills/gz-attest/SKILL.md",
            },
        ]
        result = render_skills_catalog(skills, categorized=True)
        self.assertIn("#### ADR Lifecycle", result)
        self.assertIn("#### Code Quality", result)
        self.assertIn("`gz-plan`", result)
        self.assertIn("`gz-attest`", result)
        self.assertIn("`lint`", result)
        # Should NOT contain full descriptions or per-skill paths
        self.assertNotIn("Create ADR.", result)
        self.assertNotIn(".gzkit/skills/gz-plan/SKILL.md", result)

    def test_render_skills_catalog_categorized_shows_uncategorized_for_missing_category(
        self,
    ) -> None:
        """Skills without a category field appear under Uncategorized."""
        from gzkit.sync import render_skills_catalog

        skills = [
            {
                "name": "gz-plan",
                "description": "Create ADR.",
                "category": "adr-lifecycle",
                "path": ".gzkit/skills/gz-plan/SKILL.md",
            },
            {
                "name": "orphan-skill",
                "description": "No category.",
                "category": "",
                "path": ".gzkit/skills/orphan-skill/SKILL.md",
            },
        ]
        result = render_skills_catalog(skills, categorized=True)
        self.assertIn("#### ADR Lifecycle", result)
        self.assertIn("#### Uncategorized", result)
        self.assertIn("`orphan-skill`", result)

    def test_render_skills_catalog_flat_mode_preserves_existing_format(self) -> None:
        """Non-categorized rendering preserves the existing flat bullet format."""
        from gzkit.sync import render_skills_catalog

        skills = [
            {
                "name": "lint",
                "description": "Run linting.",
                "category": "code-quality",
                "path": ".gzkit/skills/lint/SKILL.md",
            },
        ]
        result = render_skills_catalog(skills, categorized=False)
        self.assertIn("- `lint`: Run linting. (`.gzkit/skills/lint/SKILL.md`)", result)

    def test_sync_claude_rules_mirrors_instructions_to_claude_rules(self) -> None:
        """Instructions from .github/instructions/ are mirrored to .claude/rules/."""
        from gzkit.sync import sync_claude_rules

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            instructions_dir = project_root / ".github" / "instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)
            (instructions_dir / "tests.instructions.md").write_text(
                '---\napplyTo: "tests/**"\n---\n\n# Test Policy\n\nUse unittest.\n',
                encoding="utf-8",
            )
            sync_claude_rules(project_root)
            rules_file = project_root / ".claude" / "rules" / "tests.md"
            self.assertTrue(rules_file.exists())
            content = rules_file.read_text(encoding="utf-8")
            self.assertIn("paths:", content)
            self.assertIn('  - "tests/**"', content)
            self.assertIn("# Test Policy", content)
            self.assertIn("Use unittest.", content)

    def test_sync_claude_rules_strips_frontmatter_for_universal_rules(self) -> None:
        """Instructions with applyTo: '**/*' become unconditional rules (no frontmatter)."""
        from gzkit.sync import sync_claude_rules

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            instructions_dir = project_root / ".github" / "instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)
            (instructions_dir / "governance_core.instructions.md").write_text(
                '---\napplyTo: "**/*"\n---\n\n# Governance Core\n\nRead AGENTS.md.\n',
                encoding="utf-8",
            )
            sync_claude_rules(project_root)
            rules_file = project_root / ".claude" / "rules" / "governance_core.md"
            content = rules_file.read_text(encoding="utf-8")
            self.assertNotIn("paths:", content)
            self.assertNotIn("---", content)
            self.assertIn("# Governance Core", content)

    def test_sync_claude_rules_splits_comma_separated_apply_to(self) -> None:
        """Comma-separated applyTo patterns become a YAML list in paths."""
        from gzkit.sync import sync_claude_rules

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            instructions_dir = project_root / ".github" / "instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)
            (instructions_dir / "gate5.instructions.md").write_text(
                '---\napplyTo: "docs/**,src/gzkit/**"\n---\n\n# Gate 5\n', encoding="utf-8"
            )
            sync_claude_rules(project_root)
            rules_file = project_root / ".claude" / "rules" / "gate5.md"
            content = rules_file.read_text(encoding="utf-8")
            self.assertIn('  - "docs/**"', content)
            self.assertIn('  - "src/gzkit/**"', content)

    def test_sync_claude_rules_skips_excluded_coding_agent_rules(self) -> None:
        """Instructions with excludeAgent: coding-agent are not mirrored."""
        from gzkit.sync import sync_claude_rules

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            instructions_dir = project_root / ".github" / "instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)
            (instructions_dir / "review_only.instructions.md").write_text(
                '---\napplyTo: "**/*"\nexcludeAgent: coding-agent\n---\n\n# Review Only\n',
                encoding="utf-8",
            )
            sync_claude_rules(project_root)
            rules_file = project_root / ".claude" / "rules" / "review_only.md"
            self.assertFalse(rules_file.exists())

    def test_sync_claude_rules_skips_readme_and_non_instruction_files(self) -> None:
        """Only *.instructions.md files are mirrored."""
        from gzkit.sync import sync_claude_rules

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            instructions_dir = project_root / ".github" / "instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)
            (instructions_dir / "README.md").write_text("# Instructions\n", encoding="utf-8")
            (instructions_dir / "tests.instructions.md").write_text(
                '---\napplyTo: "tests/**"\n---\n\n# Tests\n', encoding="utf-8"
            )
            sync_claude_rules(project_root)
            rules_dir = project_root / ".claude" / "rules"
            mirrored = [f.name for f in rules_dir.iterdir()] if rules_dir.exists() else []
            self.assertIn("tests.md", mirrored)
            self.assertNotIn("README.md", mirrored)

    def test_sync_claude_rules_deletes_stale_mirrored_rules(self) -> None:
        """Rules that no longer have a source instruction file are deleted."""
        from gzkit.sync import sync_claude_rules

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            instructions_dir = project_root / ".github" / "instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)
            (instructions_dir / "tests.instructions.md").write_text(
                '---\napplyTo: "tests/**"\n---\n\n# Tests\n', encoding="utf-8"
            )
            rules_dir = project_root / ".claude" / "rules"
            rules_dir.mkdir(parents=True, exist_ok=True)
            (rules_dir / "old_rule.md").write_text("# Stale\n", encoding="utf-8")
            sync_claude_rules(project_root)
            self.assertTrue((rules_dir / "tests.md").exists())
            self.assertFalse((rules_dir / "old_rule.md").exists())

    def test_sync_all_creates_claude_rules_from_instructions(self) -> None:
        """sync_all() mirrors .github/instructions/ to .claude/rules/."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            instructions_dir = project_root / ".github" / "instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)
            (instructions_dir / "tests.instructions.md").write_text(
                '---\napplyTo: "tests/**"\n---\n\n# Test Policy\n', encoding="utf-8"
            )
            sync_all(project_root, config)
            rules_file = project_root / ".claude" / "rules" / "tests.md"
            self.assertTrue(rules_file.exists())
            content = rules_file.read_text(encoding="utf-8")
            self.assertIn("paths:", content)
            self.assertIn("# Test Policy", content)


class TestDetectClaudeSettingsDrift(unittest.TestCase):
    """Tests for Claude settings drift detection."""

    def _setup_synced(self, project_root: Path) -> GzkitConfig:
        """Sync settings to disk and return config."""
        import json

        from gzkit.hooks.claude import generate_claude_settings

        config = GzkitConfig(project_name="gzkit-test")
        settings = generate_claude_settings(config)
        settings_path = project_root / config.paths.claude_settings
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        return config

    def test_no_drift_when_synced(self) -> None:
        """No drift when settings match generator output."""
        from gzkit.sync import detect_claude_settings_drift

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = self._setup_synced(project_root)

            diffs = detect_claude_settings_drift(project_root, config)

            self.assertEqual(diffs, [])

    def test_drift_on_extra_key(self) -> None:
        """Detects extra top-level key in tracked settings."""
        import json

        from gzkit.sync import detect_claude_settings_drift

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = self._setup_synced(project_root)

            settings_path = project_root / config.paths.claude_settings
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            data["unexpectedKey"] = True
            settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            diffs = detect_claude_settings_drift(project_root, config)

            self.assertTrue(any("Extra top-level key: unexpectedKey" in d for d in diffs))

    def test_drift_on_missing_hook(self) -> None:
        """Detects removed hook in tracked settings."""
        import json

        from gzkit.sync import detect_claude_settings_drift

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = self._setup_synced(project_root)

            settings_path = project_root / config.paths.claude_settings
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            # Remove one hook from Write|Edit
            write_edit = data["hooks"]["PreToolUse"][1]
            write_edit["hooks"] = write_edit["hooks"][:1]
            settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            diffs = detect_claude_settings_drift(project_root, config)

            self.assertTrue(any("hook commands differ" in d for d in diffs))

    def test_drift_on_missing_file(self) -> None:
        """Detects missing settings.json."""
        from gzkit.sync import detect_claude_settings_drift

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")

            diffs = detect_claude_settings_drift(project_root, config)

            self.assertTrue(any("Missing" in d for d in diffs))


class TestSyncClaudeSettingsPreservesUserPhases(unittest.TestCase):
    """GHI #329: sync_claude_settings must preserve user-added hook phases.

    The `setup_claude_hooks` writer in `gzkit.hooks.claude` correctly merges
    user-added hooks via `_merge_settings`, but the parallel writer
    `gzkit.sync.sync_claude_settings` (called by `gz agent sync
    control-surfaces`) bypassed the merge and overwrote the file with the
    bare gzkit-owned subset. That stripped any user-defined phases — most
    importantly `SessionStart` and `PreCompact`, which AGENTS.md § Behavior
    Rules — Always #1 names as the mechanical orientation backstop
    (CAP-13; GHI #326). These tests pin the contract on the sync writer:
    user phases survive, user top-level keys survive, and gzkit-owned
    phases are still refreshed.
    """

    def _seed_user_settings(self, project_root: Path, config: GzkitConfig) -> Path:
        import json

        from gzkit.hooks.claude import generate_claude_settings

        settings = generate_claude_settings(config)
        settings.setdefault("hooks", {})["SessionStart"] = [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "type": "command",
                        "command": "uv run python scripts/session_orientation.py",
                    }
                ],
            }
        ]
        settings["hooks"]["PreCompact"] = [
            {
                "matcher": "*",
                "hooks": [
                    {
                        "type": "command",
                        "command": "uv run python scripts/session_orientation.py",
                    }
                ],
            }
        ]
        settings["myCustomKey"] = "preserve-me"
        settings_path = project_root / config.paths.claude_settings
        settings_path.parent.mkdir(parents=True, exist_ok=True)
        settings_path.write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        return settings_path

    def test_session_start_phase_survives_sync(self) -> None:
        import json

        from gzkit.sync import sync_claude_settings

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            settings_path = self._seed_user_settings(project_root, config)

            sync_claude_settings(project_root, config)

            result = json.loads(settings_path.read_text(encoding="utf-8"))
            self.assertIn("SessionStart", result.get("hooks", {}))
            session_hooks = result["hooks"]["SessionStart"][0]["hooks"]
            commands = [h["command"] for h in session_hooks]

            # SessionStart became a gzkit-OWNED phase in GHI #757, so this is no
            # longer the untouched-passthrough case (`test_pre_compact_phase_
            # survives_sync` still covers that). The property that matters here
            # is the one `_merge_hook_phase` guarantees for an owned phase: a
            # hook the project wired itself — one that does not live under the
            # gzkit hooks dir — is preserved ALONGSIDE gzkit's, not evicted by
            # it. Asserted by membership rather than index, because ordering
            # within the group is not a contract and pinning it would fail on
            # any future addition without a real defect behind it.
            self.assertIn("uv run python scripts/session_orientation.py", commands)
            self.assertTrue(
                any("session-start-advisement.py" in c for c in commands),
                f"gzkit's own SessionStart hook must also be present; got {commands}",
            )

    def test_pre_compact_phase_survives_sync(self) -> None:
        import json

        from gzkit.sync import sync_claude_settings

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            settings_path = self._seed_user_settings(project_root, config)

            sync_claude_settings(project_root, config)

            result = json.loads(settings_path.read_text(encoding="utf-8"))
            self.assertIn("PreCompact", result.get("hooks", {}))

    def test_user_top_level_key_survives_sync(self) -> None:
        import json

        from gzkit.sync import sync_claude_settings

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            settings_path = self._seed_user_settings(project_root, config)

            sync_claude_settings(project_root, config)

            result = json.loads(settings_path.read_text(encoding="utf-8"))
            self.assertEqual(result.get("myCustomKey"), "preserve-me")

    def test_gzkit_phases_refresh_after_tampering(self) -> None:
        """gzkit-owned PreToolUse/PostToolUse hooks remain authoritative."""
        import json

        from gzkit.sync import sync_claude_settings

        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            config = GzkitConfig(project_name="gzkit-test")
            settings_path = self._seed_user_settings(project_root, config)
            data = json.loads(settings_path.read_text(encoding="utf-8"))
            for group in data["hooks"]["PreToolUse"]:
                if group.get("matcher") == "ExitPlanMode":
                    group["hooks"][0]["command"] = "tampered"
            settings_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

            sync_claude_settings(project_root, config)

            result = json.loads(settings_path.read_text(encoding="utf-8"))
            exit_plan_groups = [
                g for g in result["hooks"]["PreToolUse"] if g.get("matcher") == "ExitPlanMode"
            ]
            self.assertEqual(len(exit_plan_groups), 1)
            self.assertIn(
                "plan-audit-gate.py",
                exit_plan_groups[0]["hooks"][0]["command"],
            )


if __name__ == "__main__":
    unittest.main()
