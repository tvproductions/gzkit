"""Tests for manifest v2 schema — OBPI-0.0.7-01.

Validates that generate_manifest() produces v2 manifests with data, ops,
and thresholds sections while preserving all v1 keys.
"""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.sync_surfaces import generate_manifest
from gzkit.validate_pkg.manifest import validate_manifest


class TestManifestV2Schema(unittest.TestCase):
    """Verify manifest v2 schema generation and validation."""

    def _generate(self) -> dict:
        with tempfile.TemporaryDirectory() as tmpdir:
            return generate_manifest(Path(tmpdir), GzkitConfig())

    def test_schema_version_is_v2(self) -> None:
        """REQ-0.0.7-01-02: Schema version reads gzkit.manifest.v2."""
        manifest = self._generate()
        self.assertEqual(manifest["schema"], "gzkit.manifest.v2")

    def test_data_section_present(self) -> None:
        """REQ-0.0.7-01-01: data top-level key exists."""
        manifest = self._generate()
        self.assertIn("data", manifest)
        data = manifest["data"]
        self.assertIn("eval_datasets", data)
        self.assertIn("eval_schema", data)
        self.assertIn("baselines", data)
        self.assertIn("schemas", data)

    def test_ops_section_present(self) -> None:
        """REQ-0.0.7-01-01: ops top-level key exists."""
        manifest = self._generate()
        self.assertIn("ops", manifest)
        ops = manifest["ops"]
        self.assertIn("chores", ops)
        self.assertIn("receipts", ops)
        self.assertIn("proofs", ops)

    def test_thresholds_section_present(self) -> None:
        """REQ-0.0.7-01-01: thresholds top-level key exists."""
        manifest = self._generate()
        self.assertIn("thresholds", manifest)
        thresholds = manifest["thresholds"]
        self.assertIn("coverage_floor", thresholds)
        self.assertIn("eval_regression_delta", thresholds)
        self.assertIn("function_lines", thresholds)
        self.assertIn("module_lines", thresholds)
        self.assertIn("class_lines", thresholds)

    def test_thresholds_have_sensible_defaults(self) -> None:
        """REQ-0.0.7-01-04: Bare gz init produces valid defaults."""
        manifest = self._generate()
        t = manifest["thresholds"]
        self.assertEqual(t["coverage_floor"], 40.0)
        self.assertEqual(t["eval_regression_delta"], 0.05)
        self.assertEqual(t["function_lines"], 50)
        self.assertEqual(t["module_lines"], 600)
        self.assertEqual(t["class_lines"], 300)

    def test_v1_keys_preserved(self) -> None:
        """REQ-0.0.7-01-02: All v1 keys remain present and unchanged."""
        manifest = self._generate()
        v1_keys = {"schema", "structure", "artifacts", "control_surfaces", "verification", "gates"}
        for key in v1_keys:
            self.assertIn(key, manifest, f"v1 key '{key}' missing from v2 manifest")

    def test_structure_fields_preserved(self) -> None:
        """v1 structure sub-keys unchanged."""
        manifest = self._generate()
        structure = manifest["structure"]
        for field in ("source_root", "tests_root", "docs_root", "design_root"):
            self.assertIn(field, structure)

    def test_artifacts_preserved(self) -> None:
        """v1 artifact types unchanged."""
        manifest = self._generate()
        artifacts = manifest["artifacts"]
        for artifact_type in ("prd", "constitution", "obpi", "adr"):
            self.assertIn(artifact_type, artifacts)
            self.assertIn("path", artifacts[artifact_type])
            self.assertIn("schema", artifacts[artifact_type])


class TestManifestV2Validation(unittest.TestCase):
    """Verify validate_manifest accepts v2 manifests."""

    def test_v2_manifest_passes_validation(self) -> None:
        """REQ-0.0.7-01-03: gz validate accepts v2 manifests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest = generate_manifest(Path(tmpdir), GzkitConfig())
            manifest_path = Path(tmpdir) / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_manifest(manifest_path)
            self.assertEqual(errors, [], f"Validation errors: {errors}")

    def test_v1_manifest_still_passes(self) -> None:
        """Backward compat: v1 manifests still validate."""
        v1_manifest = {
            "schema": "gzkit.manifest.v1",
            "structure": {
                "source_root": "src",
                "tests_root": "tests",
                "docs_root": "docs",
                "design_root": "design",
            },
            "artifacts": {
                "prd": {"path": "design/prd", "schema": "gzkit.prd.v1"},
                "constitution": {"path": "design/constitutions", "schema": "gzkit.constitution.v1"},
                "obpi": {"path": "design/adr", "schema": "gzkit.obpi.v1"},
                "adr": {"path": "design/adr", "schema": "gzkit.adr.v1"},
            },
            "control_surfaces": {
                "agents_md": "AGENTS.md",
                "claude_md": "CLAUDE.md",
                "hooks": ".claude/hooks",
                "skills": ".gzkit/skills",
                "claude_skills": ".claude/skills",
                "codex_skills": ".agents/skills",
                "copilot_skills": ".github/skills",
            },
            "verification": {
                "lint": "uv run gz lint",
                "format": "uv run gz format",
                "typecheck": "uv run gz typecheck",
                "test": "uv run gz test",
            },
            "gates": {"lite": [1, 2], "heavy": [1, 2, 3, 4, 5]},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(v1_manifest, f)
            f.flush()
            errors = validate_manifest(Path(f.name))
            self.assertEqual(errors, [], f"v1 validation errors: {errors}")

    def test_invalid_schema_version_rejected(self) -> None:
        """Manifests with wrong schema version are rejected."""
        bad_manifest = {
            "schema": "gzkit.manifest.v99",
            "structure": {
                "source_root": "src",
                "tests_root": "tests",
                "docs_root": "docs",
                "design_root": "design",
            },
            "artifacts": {
                "prd": {"path": "p", "schema": "s"},
                "constitution": {"path": "p", "schema": "s"},
                "obpi": {"path": "p", "schema": "s"},
                "adr": {"path": "p", "schema": "s"},
            },
            "control_surfaces": {
                "agents_md": "A",
                "claude_md": "C",
                "hooks": "h",
                "skills": "s",
                "claude_skills": "cs",
                "codex_skills": "xs",
                "copilot_skills": "ps",
            },
            "verification": {"lint": "l", "format": "f", "typecheck": "t", "test": "x"},
            "gates": {"lite": [1, 2], "heavy": [1, 2, 3, 4, 5]},
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(bad_manifest, f)
            f.flush()
            errors = validate_manifest(Path(f.name))
            schema_errors = [e for e in errors if e.field == "schema"]
            self.assertTrue(len(schema_errors) > 0, "Expected schema version error")


if __name__ == "__main__":
    unittest.main()
