"""Tests for eval dataset loading and schema validation.

Verifies that:
- All dataset fixtures are valid JSON
- All fixtures pass JSON schema validation
- The Pydantic loader returns typed models
- Each AI-sensitive surface has golden-path and edge-case coverage
- Datasets are reproducible (no timestamps, random values)
"""

import json
import re
import tempfile
import unittest
from pathlib import Path

from gzkit.eval.datasets import (
    KNOWN_SURFACES,
    EvalDataset,
    EvalDatasetCase,
    list_surfaces,
    load_all_datasets,
    load_dataset,
    validate_dataset_json,
)

_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "eval"
_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "data" / "schemas" / "eval_dataset.schema.json"

# Patterns that indicate non-reproducible data
_TIMESTAMP_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"  # ISO-8601
    r"|\d{10,13}"  # Unix timestamps (seconds or milliseconds)
)


class TestSchemaExists(unittest.TestCase):
    """Verify the JSON schema file exists and is valid JSON."""

    def test_schema_file_exists(self) -> None:
        self.assertTrue(_SCHEMA_PATH.is_file(), f"Schema not found: {_SCHEMA_PATH}")

    def test_schema_is_valid_json(self) -> None:
        data = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIn("properties", data)
        self.assertIn("cases", data["properties"])


class TestDatasetFixtures(unittest.TestCase):
    """Verify all dataset fixture files are valid JSON and pass schema validation."""

    def test_at_least_five_fixtures(self) -> None:
        fixtures = list(_DATA_DIR.glob("*.json"))
        self.assertGreaterEqual(len(fixtures), 5, "Expected at least 5 dataset fixtures")

    def test_all_fixtures_valid_json(self) -> None:
        for path in sorted(_DATA_DIR.glob("*.json")):
            with self.subTest(fixture=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                self.assertIsInstance(data, dict)

    def test_all_fixtures_pass_schema(self) -> None:
        for path in sorted(_DATA_DIR.glob("*.json")):
            with self.subTest(fixture=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                validate_dataset_json(data)  # raises on failure

    def test_no_duplicate_case_ids_within_dataset(self) -> None:
        for path in sorted(_DATA_DIR.glob("*.json")):
            with self.subTest(fixture=path.name):
                data = json.loads(path.read_text(encoding="utf-8"))
                case_ids = [c["id"] for c in data["cases"]]
                self.assertEqual(len(case_ids), len(set(case_ids)), "Duplicate case IDs found")


class TestSurfaceCoverage(unittest.TestCase):
    """Verify every AI-sensitive surface has golden-path and edge-case datasets."""

    def setUp(self) -> None:
        self.datasets = load_all_datasets(data_dir=_DATA_DIR)
        self.surfaces = {ds.surface for ds in self.datasets}

    def test_all_known_surfaces_covered(self) -> None:
        for surface in KNOWN_SURFACES:
            with self.subTest(surface=surface):
                self.assertIn(surface, self.surfaces, f"Missing dataset for surface: {surface}")

    def test_each_surface_has_golden_path(self) -> None:
        for ds in self.datasets:
            with self.subTest(surface=ds.surface):
                golden = [c for c in ds.cases if c.type == "golden_path"]
                self.assertGreaterEqual(
                    len(golden), 1, f"No golden_path case for surface: {ds.surface}"
                )

    def test_each_surface_has_edge_case(self) -> None:
        for ds in self.datasets:
            with self.subTest(surface=ds.surface):
                edges = [c for c in ds.cases if c.type == "edge_case"]
                self.assertGreaterEqual(len(edges), 1, f"No edge_case for surface: {ds.surface}")


class TestPydanticLoader(unittest.TestCase):
    """Verify the Pydantic dataset loader returns typed models."""

    def test_load_by_surface_name(self) -> None:
        for surface in KNOWN_SURFACES:
            with self.subTest(surface=surface):
                ds = load_dataset(surface, data_dir=_DATA_DIR)
                self.assertIsInstance(ds, EvalDataset)
                self.assertEqual(ds.surface, surface)

    def test_cases_are_typed(self) -> None:
        ds = load_dataset("instruction_eval", data_dir=_DATA_DIR)
        for case in ds.cases:
            self.assertIsInstance(case, EvalDatasetCase)
            self.assertIn(case.type, ("golden_path", "edge_case"))
            self.assertIsInstance(case.input, dict)
            self.assertIsInstance(case.expected_output, dict)

    def test_load_nonexistent_surface_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_dataset("nonexistent_surface", data_dir=_DATA_DIR)

    def test_load_all_returns_list(self) -> None:
        datasets = load_all_datasets(data_dir=_DATA_DIR)
        self.assertGreaterEqual(len(datasets), 5)
        for ds in datasets:
            self.assertIsInstance(ds, EvalDataset)

    def test_list_surfaces(self) -> None:
        surfaces = list_surfaces(data_dir=_DATA_DIR)
        self.assertGreaterEqual(len(surfaces), 5)
        for s in KNOWN_SURFACES:
            self.assertIn(s, surfaces)


class TestReproducibility(unittest.TestCase):
    """Verify datasets contain no timestamps, random values, or env-dependent data."""

    def test_no_timestamps_in_fixtures(self) -> None:
        for path in sorted(_DATA_DIR.glob("*.json")):
            with self.subTest(fixture=path.name):
                content = path.read_text(encoding="utf-8")
                matches = _TIMESTAMP_PATTERN.findall(content)
                # Filter out semver-like patterns (e.g., "0.99.0" matches \d{10,13} — no)
                real_timestamps = [m for m in matches if len(m) >= 10]
                self.assertEqual(
                    real_timestamps, [], f"Timestamps found in {path.name}: {real_timestamps}"
                )

    def test_no_random_seeds(self) -> None:
        for path in sorted(_DATA_DIR.glob("*.json")):
            with self.subTest(fixture=path.name):
                content = path.read_text(encoding="utf-8").lower()
                self.assertNotIn("random_seed", content)
                self.assertNotIn("uuid", content)


class TestCustomDataDir(unittest.TestCase):
    """Verify loader works with custom data directories."""

    def test_load_from_custom_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            fixture = {
                "surface": "test_surface",
                "version": "1.0.0",
                "description": "Test dataset",
                "cases": [
                    {
                        "id": "test-01",
                        "type": "golden_path",
                        "description": "Test case",
                        "input": {"key": "value"},
                        "expected_output": {"result": True},
                    }
                ],
            }
            (tmp_path / "test.json").write_text(json.dumps(fixture), encoding="utf-8")
            ds = load_dataset("test_surface", data_dir=tmp_path)
            self.assertEqual(ds.surface, "test_surface")
            self.assertEqual(len(ds.cases), 1)


if __name__ == "__main__":
    unittest.main()
