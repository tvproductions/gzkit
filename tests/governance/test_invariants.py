"""Tests for ConstitutionalInvariant model and registry loader (OBPI-0.0.37-01).

REQ-derived assertions for:
  REQ-0.0.37-01-01: frozen Pydantic model, structural_witness min_length=1
  REQ-0.0.37-01-02: JSON Schema mirror with additionalProperties=false, minItems=1
  REQ-0.0.37-01-03: load_invariants returns all three seed invariants
  REQ-0.0.37-01-04: load_invariants raises on schema-invalid JSON (no silent skip)
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import jsonschema
from pydantic import ValidationError

from gzkit.governance.invariants import ConstitutionalInvariant, load_invariants
from gzkit.traceability import covers


class TestConstitutionalInvariantModel(unittest.TestCase):
    """REQ-0.0.37-01-01: frozen model, structural_witness min_length=1."""

    @covers("REQ-0.0.37-01-01")
    def test_model_is_frozen_raises_on_mutation(self) -> None:
        inv = ConstitutionalInvariant(
            id="TEST-1",
            claim="A test claim.",
            structural_witness=["gz validate --test"],
            composition_targets=[],
        )
        with self.assertRaises((ValueError, TypeError)):
            inv.id = "MUTATED"  # type: ignore

    @covers("REQ-0.0.37-01-01")
    def test_empty_structural_witness_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ConstitutionalInvariant(
                id="TEST-2",
                claim="A test claim.",
                structural_witness=[],
                composition_targets=[],
            )

    @covers("REQ-0.0.37-01-01")
    def test_extra_fields_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            ConstitutionalInvariant(
                id="TEST-3",
                claim="A test claim.",
                structural_witness=["gz validate --test"],
                composition_targets=[],
                unknown_field="should fail",
            )

    @covers("REQ-0.0.37-01-01")
    def test_valid_model_constructs(self) -> None:
        inv = ConstitutionalInvariant(
            id="CIC-1",
            claim="Every claim in AGENTS.md originates from the registry.",
            structural_witness=["gz validate --invariant-coherence"],
            composition_targets=["AGENTS.md"],
        )
        self.assertEqual(inv.id, "CIC-1")
        self.assertEqual(inv.composition_targets, ["AGENTS.md"])


class TestConstitutionalInvariantSchema(unittest.TestCase):
    """REQ-0.0.37-01-02: JSON Schema mirror correctness."""

    SCHEMA_PATH = Path("src/gzkit/schemas/constitutional_invariant.json")

    @covers("REQ-0.0.37-01-02")
    def test_schema_file_exists(self) -> None:
        self.assertTrue(self.SCHEMA_PATH.exists(), "constitutional_invariant.json must exist")

    @covers("REQ-0.0.37-01-02")
    def test_schema_additional_properties_false(self) -> None:
        schema = json.loads(self.SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertIs(schema.get("additionalProperties"), False)

    @covers("REQ-0.0.37-01-02")
    def test_schema_structural_witness_min_items_one(self) -> None:
        schema = json.loads(self.SCHEMA_PATH.read_text(encoding="utf-8"))
        sw = schema["properties"]["structural_witness"]
        self.assertEqual(sw.get("minItems"), 1)
        self.assertEqual(sw.get("type"), "array")

    @covers("REQ-0.0.37-01-02")
    def test_schema_required_keys_present(self) -> None:
        schema = json.loads(self.SCHEMA_PATH.read_text(encoding="utf-8"))
        required = set(schema.get("required", []))
        self.assertLessEqual({"id", "claim", "structural_witness", "composition_targets"}, required)

    @covers("REQ-0.0.37-01-02")
    def test_schema_validates_known_good_invariant(self) -> None:
        import jsonschema

        schema = json.loads(self.SCHEMA_PATH.read_text(encoding="utf-8"))
        good = {
            "id": "CIC-1",
            "claim": "A claim.",
            "structural_witness": ["gz validate --invariant-coherence"],
            "composition_targets": [],
        }
        jsonschema.validate(good, schema)

    @covers("REQ-0.0.37-01-02")
    def test_schema_rejects_missing_id(self) -> None:
        import jsonschema

        schema = json.loads(self.SCHEMA_PATH.read_text(encoding="utf-8"))
        bad = {
            "claim": "Missing id.",
            "structural_witness": ["gz validate --test"],
            "composition_targets": [],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)


class TestLoadInvariants(unittest.TestCase):
    """REQ-0.0.37-01-03: load_invariants returns all three seed invariants."""

    @covers("REQ-0.0.37-01-03")
    def test_load_invariants_returns_three_seeds(self) -> None:
        inv = load_invariants(Path("."))
        self.assertIn("CIC-1", inv, "CIC-1 seed invariant must be present")
        self.assertIn("CIC-2", inv, "CIC-2 seed invariant must be present")
        self.assertIn(
            "foundation-adr-registers-invariant",
            inv,
            "foundation-adr-registers-invariant must be present",
        )

    @covers("REQ-0.0.37-01-03")
    def test_load_invariants_returns_model_instances(self) -> None:
        inv = load_invariants(Path("."))
        for key, value in inv.items():
            self.assertIsInstance(
                value,
                ConstitutionalInvariant,
                f"Entry '{key}' must be a ConstitutionalInvariant",
            )

    @covers("REQ-0.0.37-01-03")
    def test_load_invariants_cic1_has_composition_targets(self) -> None:
        inv = load_invariants(Path("."))
        cic1 = inv["CIC-1"]
        self.assertIn("AGENTS.md", cic1.composition_targets)

    @covers("REQ-0.0.37-01-03")
    def test_load_invariants_structural_witness_non_empty(self) -> None:
        inv = load_invariants(Path("."))
        for key, value in inv.items():
            self.assertGreater(
                len(value.structural_witness),
                0,
                f"'{key}' must have at least one structural_witness",
            )


class TestLoadInvariantsError(unittest.TestCase):
    """REQ-0.0.37-01-04: load_invariants raises on invalid JSON (no silent skip)."""

    @covers("REQ-0.0.37-01-04")
    def test_raises_on_missing_required_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            inv_dir = tmp_path / ".gzkit" / "invariants"
            inv_dir.mkdir(parents=True)
            bad_yaml = {"claim": "Missing id and structural_witness."}
            (inv_dir / "bad.json").write_text(json.dumps(bad_yaml), encoding="utf-8")
            with self.assertRaises(jsonschema.ValidationError):
                load_invariants(tmp_path)

    @covers("REQ-0.0.37-01-04")
    def test_raises_on_empty_structural_witness(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            inv_dir = tmp_path / ".gzkit" / "invariants"
            inv_dir.mkdir(parents=True)
            bad_yaml = {
                "id": "X",
                "claim": "A claim.",
                "structural_witness": [],
                "composition_targets": [],
            }
            (inv_dir / "bad.json").write_text(json.dumps(bad_yaml), encoding="utf-8")
            with self.assertRaises(jsonschema.ValidationError):
                load_invariants(tmp_path)

    @covers("REQ-0.0.37-01-04")
    def test_raises_on_extra_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            inv_dir = tmp_path / ".gzkit" / "invariants"
            inv_dir.mkdir(parents=True)
            bad_yaml = {
                "id": "Y",
                "claim": "A claim.",
                "structural_witness": ["gz validate --test"],
                "composition_targets": [],
                "extra_field": "should fail",
            }
            (inv_dir / "bad.json").write_text(json.dumps(bad_yaml), encoding="utf-8")
            with self.assertRaises(jsonschema.ValidationError):
                load_invariants(tmp_path)

    @covers("REQ-0.0.37-01-04")
    def test_empty_directory_returns_empty_dict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            inv_dir = tmp_path / ".gzkit" / "invariants"
            inv_dir.mkdir(parents=True)
            result = load_invariants(tmp_path)
            self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
