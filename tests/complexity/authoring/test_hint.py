"""Tests for AuthoringHint model + project_diagnosis_to_hint (OBPI-0.0.30-03).

REQ-IDs in this module map to the brief Acceptance Criteria
REQ-0.0.30-03-01 through REQ-0.0.30-03-08:

- REQ-01: model instantiation / frozen contract
- REQ-02: advise -> AuthoringHint projection
- REQ-03: warn/block -> None
- REQ-04: proof + intrinsic_attestation dropped; ProofRange promoted
- REQ-08: mutation raises ValidationError on the frozen instance

REQ-05/06/07 land in test_engine.py.
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
from gzkit.complexity.authoring.hint import AuthoringHint, project_diagnosis_to_hint
from gzkit.traceability import covers

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[3] / "src" / "gzkit" / "schemas" / "authoring_hint.json"
)


def _load_schema() -> dict:
    return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))


def _proof(
    file_path: str = "src/gzkit/example.py", start_line: int = 10, end_line: int = 20
) -> ProofRange:
    return ProofRange(
        file_path=file_path,
        start_line=start_line,
        end_line=end_line,
        ast_node_kind="FunctionDef",
    )


def _frame(
    excerpt: str = "Long parameter list is hard to understand.\nMore context follows.",
) -> DoctrinalFrame:
    return DoctrinalFrame(
        authority="fowler",
        citation="Refactoring, 2nd ed., p. 78",
        excerpt=excerpt,
    )


def _diagnosis(
    *,
    crossing_band: str = "advise",
    crossing_value: float = 5.0,
    proof: tuple[ProofRange, ...] | None = None,
    excerpt: str | None = None,
    intrinsic: IntrinsicAttestationRef | None = None,
) -> AdvisorDiagnosis:
    return AdvisorDiagnosis(
        metric="radon_cc",
        crossing_band=crossing_band,
        crossing_value=crossing_value,
        archetype=RefactorArchetype.LONG_PARAMETER_LIST,
        doctrinal_frame=_frame(excerpt) if excerpt is not None else _frame(),
        proof=proof if proof is not None else (_proof(),),
        recommended_move="Introduce Parameter Object",
        intrinsic_attestation=intrinsic,
    )


def _valid_hint_kwargs() -> dict:
    return {
        "metric": "radon_cc",
        "precedence_band": "approaching",
        "crossing_value": 5.5,
        "archetype": RefactorArchetype.LONG_PARAMETER_LIST,
        "doctrinal_frame_headline": "Long parameter list is hard to understand.",
        "recommended_move": "Introduce Parameter Object",
        "file_path": "src/gzkit/example.py",
        "start_line": 10,
        "end_line": 20,
    }


class TestAuthoringHintModel(unittest.TestCase):
    @covers("REQ-0.0.30-03-01")
    def test_valid_instance_is_frozen(self) -> None:
        hint = AuthoringHint(**_valid_hint_kwargs())
        self.assertEqual(hint.metric, "radon_cc")
        self.assertEqual(hint.precedence_band, "approaching")
        self.assertEqual(hint.start_line, 10)
        self.assertEqual(hint.end_line, 20)

    @covers("REQ-0.0.30-03-08")
    def test_mutation_raises(self) -> None:
        hint = AuthoringHint(**_valid_hint_kwargs())
        with self.assertRaises(ValidationError):
            hint.metric = "lizard_ccn"  # type: ignore

    @covers("REQ-0.0.30-03-01")
    def test_extra_field_forbidden(self) -> None:
        kwargs = _valid_hint_kwargs()
        kwargs["unexpected"] = "x"
        with self.assertRaises(ValidationError):
            AuthoringHint(**kwargs)

    @covers("REQ-0.0.30-03-01")
    def test_invalid_precedence_band_rejected(self) -> None:
        kwargs = _valid_hint_kwargs()
        kwargs["precedence_band"] = "warning"
        with self.assertRaises(ValidationError):
            AuthoringHint(**kwargs)

    @covers("REQ-0.0.30-03-01")
    def test_invalid_archetype_rejected(self) -> None:
        kwargs = _valid_hint_kwargs()
        kwargs["archetype"] = "not_an_archetype"
        with self.assertRaises(ValidationError):
            AuthoringHint(**kwargs)

    @covers("REQ-0.0.30-03-01")
    def test_end_line_before_start_line_rejected(self) -> None:
        kwargs = _valid_hint_kwargs()
        kwargs["start_line"] = 20
        kwargs["end_line"] = 10
        with self.assertRaises(ValidationError):
            AuthoringHint(**kwargs)

    @covers("REQ-0.0.30-03-01")
    def test_zero_start_line_rejected(self) -> None:
        kwargs = _valid_hint_kwargs()
        kwargs["start_line"] = 0
        with self.assertRaises(ValidationError):
            AuthoringHint(**kwargs)


class TestProjection(unittest.TestCase):
    @covers("REQ-0.0.30-03-02")
    def test_advise_projects_to_hint(self) -> None:
        diag = _diagnosis(crossing_band="advise", crossing_value=5.0)
        hint = project_diagnosis_to_hint(diag, precedence_band="approaching")
        self.assertIsNotNone(hint)
        assert hint is not None  # for ty
        self.assertEqual(hint.metric, "radon_cc")
        self.assertEqual(hint.precedence_band, "approaching")
        self.assertEqual(hint.crossing_value, 5.0)
        self.assertEqual(hint.archetype, RefactorArchetype.LONG_PARAMETER_LIST)
        self.assertEqual(hint.recommended_move, "Introduce Parameter Object")

    @covers("REQ-0.0.30-03-03")
    def test_warn_returns_none(self) -> None:
        diag = _diagnosis(crossing_band="warn", crossing_value=8.0)
        self.assertIsNone(project_diagnosis_to_hint(diag, precedence_band="approaching"))

    @covers("REQ-0.0.30-03-03")
    def test_block_returns_none(self) -> None:
        diag = _diagnosis(crossing_band="block", crossing_value=12.0)
        self.assertIsNone(project_diagnosis_to_hint(diag, precedence_band="approaching"))

    @covers("REQ-0.0.30-03-04")
    def test_proof_dropped_first_range_promoted(self) -> None:
        proof = (
            _proof(file_path="src/gzkit/a.py", start_line=15, end_line=30),
            _proof(file_path="src/gzkit/a.py", start_line=40, end_line=42),
        )
        diag = _diagnosis(crossing_band="advise", proof=proof)
        hint = project_diagnosis_to_hint(diag, precedence_band="approaching_warn")
        assert hint is not None
        self.assertEqual(hint.file_path, "src/gzkit/a.py")
        self.assertEqual(hint.start_line, 15)
        self.assertEqual(hint.end_line, 30)
        # proof field absent on AuthoringHint
        self.assertFalse(hasattr(hint, "proof"))

    @covers("REQ-0.0.30-03-04")
    def test_intrinsic_attestation_dropped(self) -> None:
        diag = _diagnosis(
            crossing_band="advise",
            intrinsic=IntrinsicAttestationRef(attestation_id="att-1"),
        )
        hint = project_diagnosis_to_hint(diag, precedence_band="approaching")
        assert hint is not None
        self.assertFalse(hasattr(hint, "intrinsic_attestation"))

    @covers("REQ-0.0.30-03-04")
    def test_excerpt_truncated_to_first_line(self) -> None:
        diag = _diagnosis(
            crossing_band="advise",
            excerpt="First line of doctrine.\nSecond line ignored.\nThird line ignored.",
        )
        hint = project_diagnosis_to_hint(diag, precedence_band="approaching")
        assert hint is not None
        self.assertEqual(hint.doctrinal_frame_headline, "First line of doctrine.")


class TestAuthoringHintSchemaMirror(unittest.TestCase):
    @covers("REQ-0.0.30-03-01")
    def test_valid_payload_validates_against_schema(self) -> None:
        hint = AuthoringHint(**_valid_hint_kwargs())
        payload = hint.model_dump(mode="json")
        jsonschema.validate(payload, _load_schema())

    @covers("REQ-0.0.30-03-01")
    def test_extra_property_rejected_by_schema(self) -> None:
        payload = AuthoringHint(**_valid_hint_kwargs()).model_dump(mode="json")
        payload["unexpected"] = "x"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(payload, _load_schema())

    @covers("REQ-0.0.30-03-01")
    def test_invalid_precedence_band_rejected_by_schema(self) -> None:
        payload = AuthoringHint(**_valid_hint_kwargs()).model_dump(mode="json")
        payload["precedence_band"] = "warning"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(payload, _load_schema())

    @covers("REQ-0.0.30-03-01")
    def test_invalid_archetype_rejected_by_schema(self) -> None:
        payload = AuthoringHint(**_valid_hint_kwargs()).model_dump(mode="json")
        payload["archetype"] = "not_an_archetype"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(payload, _load_schema())


if __name__ == "__main__":
    unittest.main()
