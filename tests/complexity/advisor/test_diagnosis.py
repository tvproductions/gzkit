"""Tests for AdvisorDiagnosis schema (OBPI-0.0.29-01-advisor-diagnosis-schema).

Covers REQ-0.0.29-01-01 through REQ-0.0.29-01-06 via the @covers decorator.
REQ-07 (extra="forbid" on all models) is covered by test_all_models_forbid_extra
without a @covers binding (not in the brief Acceptance Criteria section).
REQ-08/09/10 are procedural; satisfied by TDD rhythm, tempfile usage, and
absence of operator email respectively.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
from pydantic import ValidationError

from gzkit.complexity.advisor.diagnosis import (
    AdvisorDiagnosis,
    DoctrinalFrame,
    IntrinsicAttestationRef,
    ProofRange,
    RefactorArchetype,
)
from gzkit.traceability import covers

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "src" / "gzkit" / "schemas" / "advisor_diagnosis.json"
)


def _load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _valid_proof_range() -> ProofRange:
    return ProofRange(
        file_path="src/gzkit/example.py",
        start_line=10,
        end_line=20,
        ast_node_kind="FunctionDef",
    )


def _valid_doctrinal_frame() -> DoctrinalFrame:
    return DoctrinalFrame(
        authority="fowler",
        citation="Refactoring, 2nd ed., p. 78",
        excerpt="A long parameter list is hard to understand.",
    )


def _valid_diagnosis_dict() -> dict:
    return {
        "metric": "radon_cc",
        "crossing_band": "warn",
        "crossing_value": 8.5,
        "archetype": "long_parameter_list",
        "doctrinal_frame": {
            "authority": "fowler",
            "citation": "Refactoring, 2nd ed., p. 78",
            "excerpt": "A long parameter list is hard to understand.",
        },
        "proof": [
            {
                "file_path": "src/gzkit/example.py",
                "start_line": 10,
                "end_line": 20,
                "ast_node_kind": "FunctionDef",
            }
        ],
        "recommended_move": "Introduce Parameter Object",
        "intrinsic_attestation": None,
    }


class TestAdvisorDiagnosisSchema(unittest.TestCase):
    """Test suite for the AdvisorDiagnosis frozen Pydantic data contract."""

    @covers("REQ-0.0.29-01-01")
    def test_advisor_diagnosis_valid_instantiation(self) -> None:
        """Given a valid input dict, AdvisorDiagnosis(**data) returns a frozen instance."""
        frame = _valid_doctrinal_frame()
        proof_range = _valid_proof_range()
        diagnosis = AdvisorDiagnosis(
            metric="radon_cc",
            crossing_band="warn",
            crossing_value=8.5,
            archetype=RefactorArchetype.LONG_PARAMETER_LIST,
            doctrinal_frame=frame,
            proof=(proof_range,),
            recommended_move="Introduce Parameter Object",
        )
        self.assertEqual(diagnosis.metric, "radon_cc")
        self.assertEqual(diagnosis.crossing_band, "warn")
        self.assertAlmostEqual(diagnosis.crossing_value, 8.5)
        self.assertEqual(diagnosis.archetype, RefactorArchetype.LONG_PARAMETER_LIST)
        self.assertIsNone(diagnosis.intrinsic_attestation)
        self.assertEqual(len(diagnosis.proof), 1)

    @covers("REQ-0.0.29-01-02")
    def test_advisor_diagnosis_rejects_empty_proof(self) -> None:
        """Given proof=(), AdvisorDiagnosis instantiation raises ValidationError."""
        frame = _valid_doctrinal_frame()
        with self.assertRaises(ValidationError):
            AdvisorDiagnosis(
                metric="radon_cc",
                crossing_band="warn",
                crossing_value=8.5,
                archetype=RefactorArchetype.LONG_PARAMETER_LIST,
                doctrinal_frame=frame,
                proof=(),
                recommended_move="Introduce Parameter Object",
            )

    @covers("REQ-0.0.29-01-03")
    def test_advisor_diagnosis_rejects_unknown_archetype(self) -> None:
        """Given archetype outside the ten-value enum, ValidationError is raised."""
        frame = _valid_doctrinal_frame()
        proof_range = _valid_proof_range()
        with self.assertRaises(ValidationError):
            AdvisorDiagnosis(
                metric="radon_cc",
                crossing_band="warn",
                crossing_value=8.5,
                archetype="not_a_valid_archetype",  # type: ignore
                doctrinal_frame=frame,
                proof=(proof_range,),
                recommended_move="Introduce Parameter Object",
            )

    @covers("REQ-0.0.29-01-04")
    def test_doctrinal_frame_rejects_unknown_authority(self) -> None:
        """Given authority outside the four-value enum, ValidationError is raised."""
        with self.assertRaises(ValidationError):
            DoctrinalFrame(
                authority="beck",  # type: ignore
                citation="Test citation",
                excerpt="Test excerpt",
            )

    @covers("REQ-0.0.29-01-04")
    def test_advisor_diagnosis_rejects_unknown_crossing_band(self) -> None:
        """Given crossing_band outside the three-value enum, ValidationError is raised."""
        frame = _valid_doctrinal_frame()
        proof_range = _valid_proof_range()
        with self.assertRaises(ValidationError):
            AdvisorDiagnosis(
                metric="radon_cc",
                crossing_band="critical",  # type: ignore
                crossing_value=8.5,
                archetype=RefactorArchetype.LONG_PARAMETER_LIST,
                doctrinal_frame=frame,
                proof=(proof_range,),
                recommended_move="Introduce Parameter Object",
            )

    @covers("REQ-0.0.29-01-04")
    def test_proof_range_rejects_end_before_start(self) -> None:
        """Given end_line < start_line, ProofRange instantiation raises ValidationError."""
        with self.assertRaises(ValidationError):
            ProofRange(
                file_path="src/gzkit/example.py",
                start_line=20,
                end_line=10,
                ast_node_kind="FunctionDef",
            )

    @covers("REQ-0.0.29-01-05")
    def test_advisor_diagnosis_is_frozen(self) -> None:
        """Given a frozen AdvisorDiagnosis instance, mutation attempts raise ValidationError."""
        frame = _valid_doctrinal_frame()
        proof_range = _valid_proof_range()
        diagnosis = AdvisorDiagnosis(
            metric="radon_cc",
            crossing_band="warn",
            crossing_value=8.5,
            archetype=RefactorArchetype.LONG_PARAMETER_LIST,
            doctrinal_frame=frame,
            proof=(proof_range,),
            recommended_move="Introduce Parameter Object",
        )
        with self.assertRaises(ValidationError):
            diagnosis.metric = "mutated"  # type: ignore

    @covers("REQ-0.0.29-01-06")
    def test_json_schema_validates_serialized_diagnosis(self) -> None:
        """Given a serialized AdvisorDiagnosis dict, JSON Schema validation passes."""
        schema = _load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        data = _valid_diagnosis_dict()
        errors = list(validator.iter_errors(data))
        self.assertEqual(errors, [], msg=f"Unexpected validation errors: {errors}")

    @covers("REQ-0.0.29-01-06")
    def test_json_schema_rejects_empty_proof(self) -> None:
        """JSON Schema rejects a diagnosis dict with an empty proof array."""
        schema = _load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        data = _valid_diagnosis_dict()
        data["proof"] = []
        errors = list(validator.iter_errors(data))
        self.assertGreater(len(errors), 0, "Expected validation error for empty proof")

    @covers("REQ-0.0.29-01-06")
    def test_json_schema_rejects_unknown_archetype_enum(self) -> None:
        """JSON Schema rejects a diagnosis dict with an archetype value outside the enum."""
        schema = _load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        data = _valid_diagnosis_dict()
        data["archetype"] = "god_class"
        errors = list(validator.iter_errors(data))
        self.assertGreater(len(errors), 0, "Expected validation error for unknown archetype")

    @covers("REQ-0.0.29-01-06")
    def test_json_schema_rejects_unknown_authority_enum(self) -> None:
        """JSON Schema rejects a doctrinal_frame with an authority outside the enum."""
        schema = _load_schema()
        validator = jsonschema.Draft202012Validator(schema)
        data = _valid_diagnosis_dict()
        data["doctrinal_frame"]["authority"] = "beck"
        errors = list(validator.iter_errors(data))
        self.assertGreater(len(errors), 0, "Expected validation error for unknown authority")

    def test_all_models_forbid_extra_fields(self) -> None:
        """All four model classes reject instantiation with unknown extra fields.

        Validates REQ-07: ConfigDict(frozen=True, extra="forbid") on all four classes.
        Not @covers-tagged because REQ-07 is not in the brief Acceptance Criteria section.
        """
        frame_data = {
            "authority": "fowler",
            "citation": "Test citation",
            "excerpt": "Test excerpt",
            "unknown_extra": "value",
        }
        with self.assertRaises(ValidationError):
            DoctrinalFrame(**frame_data)

        proof_data = {
            "file_path": "src/gzkit/example.py",
            "start_line": 10,
            "end_line": 20,
            "ast_node_kind": "FunctionDef",
            "unknown_extra": "value",
        }
        with self.assertRaises(ValidationError):
            ProofRange(**proof_data)

        attestation_data = {
            "attestation_id": "att-123",
            "unknown_extra": "value",
        }
        with self.assertRaises(ValidationError):
            IntrinsicAttestationRef(**attestation_data)

        frame = _valid_doctrinal_frame()
        proof_range = _valid_proof_range()
        diagnosis_data = {
            "metric": "radon_cc",
            "crossing_band": "warn",
            "crossing_value": 8.5,
            "archetype": RefactorArchetype.LONG_PARAMETER_LIST,
            "doctrinal_frame": frame,
            "proof": (proof_range,),
            "recommended_move": "Introduce Parameter Object",
            "unknown_extra": "value",
        }
        with self.assertRaises(ValidationError):
            AdvisorDiagnosis(**diagnosis_data)


if __name__ == "__main__":
    unittest.main()
