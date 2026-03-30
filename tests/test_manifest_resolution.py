"""Tests for manifest_path() resolution helper (OBPI-0.0.7-02)."""

import unittest
from pathlib import Path

from gzkit.commands.common import manifest_path


class TestManifestPathV2(unittest.TestCase):
    """manifest_path() with v2 sectioned manifests."""

    def setUp(self):
        self.manifest = {
            "schema": "gzkit.manifest.v2",
            "data": {
                "eval_datasets": "data/eval",
                "eval_schema": "data/schemas/eval_dataset.schema.json",
            },
            "ops": {
                "chores": "config/chores",
                "receipts": "artifacts/receipts",
            },
            "thresholds": {
                "coverage_floor": 40.0,
            },
        }

    def test_resolves_data_section_key(self):
        """REQ-0.0.7-02-01: resolve data.eval_datasets to Path."""
        result = manifest_path(self.manifest, "data", "eval_datasets")
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path("data/eval"))

    def test_resolves_ops_section_key(self):
        result = manifest_path(self.manifest, "ops", "receipts")
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path("artifacts/receipts"))

    def test_missing_key_raises_keyerror(self):
        """REQ-0.0.7-02-02: missing key raises KeyError with section+key."""
        with self.assertRaises(KeyError) as ctx:
            manifest_path(self.manifest, "data", "nonexistent")
        msg = str(ctx.exception)
        self.assertIn("data", msg)
        self.assertIn("nonexistent", msg)

    def test_missing_section_raises_keyerror(self):
        """REQ-0.0.7-02-02: missing section raises KeyError with section name."""
        with self.assertRaises(KeyError) as ctx:
            manifest_path(self.manifest, "nosection", "somekey")
        msg = str(ctx.exception)
        self.assertIn("nosection", msg)

    def test_numeric_value_coerced_to_path(self):
        """Non-string values are str-coerced before Path construction."""
        result = manifest_path(self.manifest, "thresholds", "coverage_floor")
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path("40.0"))


class TestManifestPathV1Fallback(unittest.TestCase):
    """manifest_path() with v1 flat manifests (no sectioned dicts)."""

    def setUp(self):
        self.manifest = {
            "eval_datasets": "data/eval",
            "schemas": "data/schemas",
        }

    def test_resolves_v1_key_at_top_level(self):
        """REQ-0.0.7-02-03: v1 manifest resolves top-level key."""
        result = manifest_path(self.manifest, "data", "eval_datasets")
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path("data/eval"))

    def test_v1_missing_key_raises_keyerror(self):
        """v1 manifest with missing key still raises KeyError."""
        with self.assertRaises(KeyError) as ctx:
            manifest_path(self.manifest, "data", "nonexistent")
        msg = str(ctx.exception)
        self.assertIn("nonexistent", msg)


if __name__ == "__main__":
    unittest.main()
