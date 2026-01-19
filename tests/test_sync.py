"""Tests for gzkit sync module."""

import tempfile
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.sync import (
    detect_project_name,
    detect_project_structure,
    generate_manifest,
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
            self.assertIn("brief", artifacts)
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


if __name__ == "__main__":
    unittest.main()
