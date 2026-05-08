"""Tests for advisor verdict <-> proof binding validator (OBPI-0.0.29-08).

Covers:
    REQ-0.0.29-08-01..07 — fixture, ledger, schema scan scopes; error-message
        quality; speculative-marker escape; CLI integration with --all and
        gz check.

All tests use ``tempfile.TemporaryDirectory`` for sandbox isolation; never
write to the live repo root.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits.advisor_proof_binding import (
    validate_advisor_proof_binding,
)
from gzkit.traceability import covers


def _well_formed_diagnosis(diag_id: str = "diag-001") -> dict:
    """Return a schema-conforming diagnosis dict with non-empty proof."""
    return {
        "id": diag_id,
        "metric": "radon_cc",
        "crossing_band": "warn",
        "crossing_value": 8.5,
        "archetype": "long_parameter_list",
        "doctrinal_frame": {
            "authority": "fowler",
            "citation": "Refactoring 2e p.78",
            "excerpt": "Long parameter lists are a code smell.",
        },
        "proof": [
            {
                "file_path": "src/foo.py",
                "start_line": 10,
                "end_line": 20,
                "ast_node_kind": "FunctionDef",
            }
        ],
        "recommended_move": "Extract Parameter Object.",
    }


def _empty_proof_diagnosis(diag_id: str = "diag-empty") -> dict:
    """Return a diagnosis dict whose proof is empty (the rule violation)."""
    diag = _well_formed_diagnosis(diag_id)
    diag["proof"] = []
    return diag


def _write_fixture(project_root: Path, name: str, payload: dict) -> Path:
    fixtures_dir = project_root / "tests" / "fixtures" / "advisor"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    fixture_path = fixtures_dir / name
    fixture_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return fixture_path


def _write_ledger(project_root: Path, events: list[dict]) -> Path:
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("w", encoding="utf-8") as f:
        for ev in events:
            f.write(json.dumps(ev) + "\n")
    return ledger_path


def _write_schema(project_root: Path, *, proof_min_items: int | None = 1) -> Path:
    schema_path = project_root / "src" / "gzkit" / "schemas" / "advisor_diagnosis.json"
    schema_path.parent.mkdir(parents=True, exist_ok=True)
    proof_node: dict = {"type": "array", "items": {"type": "object"}}
    if proof_min_items is not None:
        proof_node["minItems"] = proof_min_items
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {"proof": proof_node},
    }
    schema_path.write_text(json.dumps(schema, indent=2), encoding="utf-8")
    return schema_path


class _ProjectRootMixin(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.project_root = Path(self._tmp.name)
        # By default plant a conforming schema so unrelated scopes don't fire.
        _write_schema(self.project_root, proof_min_items=1)

    def tearDown(self) -> None:
        self._tmp.cleanup()


class TestFixtureScope(_ProjectRootMixin):
    """Fixture scope: walks tests/fixtures/advisor/*.json."""

    @covers("REQ-0.0.29-08-01")
    def test_well_formed_fixture_passes(self) -> None:
        _write_fixture(self.project_root, "good.json", _well_formed_diagnosis())
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.29-08-02")
    def test_empty_proof_fixture_fails_with_path_and_line(self) -> None:
        path = _write_fixture(self.project_root, "empty.json", _empty_proof_diagnosis())
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(len(errors), 1, f"expected 1 error, got {errors}")
        msg = errors[0].message
        rel = path.relative_to(self.project_root).as_posix()
        self.assertIn(rel, msg)
        self.assertRegex(msg, r":\d+")  # cites a line number
        self.assertEqual(errors[0].type, "advisor_proof_binding")

    @covers("REQ-0.0.29-08-06")
    def test_speculative_marker_escapes_negative_case_fixture(self) -> None:
        # Negative-case fixture: tests the rejection itself; not a defect.
        diag = _empty_proof_diagnosis("diag-neg")
        diag["_negative_case"] = True
        _write_fixture(self.project_root, "negative_case.json", diag)
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.29-08-01")
    def test_no_fixtures_dir_is_vacuous_pass(self) -> None:
        # No fixtures directory; scope is vacuously empty.
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.29-08-02")
    def test_invalid_json_is_not_proof_binding_concern(self) -> None:
        # Invalid JSON is a schema-validator concern, not this scope's failure.
        fixtures_dir = self.project_root / "tests" / "fixtures" / "advisor"
        fixtures_dir.mkdir(parents=True, exist_ok=True)
        (fixtures_dir / "broken.json").write_text("not json", encoding="utf-8")
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(errors, [])


class TestLedgerScope(_ProjectRootMixin):
    """Ledger scope: scans intrinsic-complexity-attestation events."""

    @covers("REQ-0.0.29-08-03")
    def test_event_citing_empty_proof_diagnosis_fails_with_event_id(self) -> None:
        diag = _empty_proof_diagnosis("diag-cited")
        _write_fixture(self.project_root, "cited.json", diag)
        event = {
            "schema": "gzkit.ledger.v1",
            "event": "intrinsic-complexity-attestation",
            "id": "ica-evt-001",
            "ts": "2026-05-08T00:00:00+00:00",
            "diagnosis_id": "diag-cited",
        }
        _write_ledger(self.project_root, [event])
        errors = validate_advisor_proof_binding(self.project_root)
        # Both fixture-scope (cited.json) and ledger-scope (event id) flag.
        ledger_errors = [e for e in errors if e.artifact == "ica-evt-001"]
        self.assertEqual(len(ledger_errors), 1, f"expected event flagged, got {errors}")
        self.assertIn("ica-evt-001", ledger_errors[0].message)

    @covers("REQ-0.0.29-08-03")
    def test_event_citing_well_formed_diagnosis_passes(self) -> None:
        diag = _well_formed_diagnosis("diag-good")
        _write_fixture(self.project_root, "good.json", diag)
        event = {
            "schema": "gzkit.ledger.v1",
            "event": "intrinsic-complexity-attestation",
            "id": "ica-evt-002",
            "diagnosis_id": "diag-good",
        }
        _write_ledger(self.project_root, [event])
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.29-08-03")
    def test_unresolvable_diagnosis_ref_is_not_this_scopes_concern(self) -> None:
        # OBPI-07 owns event-shape validation; unresolvable refs aren't ours.
        event = {
            "schema": "gzkit.ledger.v1",
            "event": "intrinsic-complexity-attestation",
            "id": "ica-evt-003",
            "diagnosis_id": "diag-missing",
        }
        _write_ledger(self.project_root, [event])
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(errors, [])

    @covers("REQ-0.0.29-08-03")
    def test_no_ledger_is_vacuous_pass(self) -> None:
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(errors, [])


class TestSchemaScope(_ProjectRootMixin):
    """Schema scope: asserts advisor_diagnosis.json requires non-empty proof."""

    @covers("REQ-0.0.29-08-04")
    def test_schema_without_min_items_fails(self) -> None:
        _write_schema(self.project_root, proof_min_items=None)
        errors = validate_advisor_proof_binding(self.project_root)
        schema_errors = [e for e in errors if "advisor_diagnosis.json" in e.artifact]
        self.assertEqual(len(schema_errors), 1, f"expected schema flagged, got {errors}")
        self.assertIn("minItems", schema_errors[0].message)

    @covers("REQ-0.0.29-08-04")
    def test_schema_with_min_items_zero_fails(self) -> None:
        _write_schema(self.project_root, proof_min_items=0)
        errors = validate_advisor_proof_binding(self.project_root)
        schema_errors = [e for e in errors if "advisor_diagnosis.json" in e.artifact]
        self.assertEqual(len(schema_errors), 1, f"expected schema flagged, got {errors}")

    @covers("REQ-0.0.29-08-04")
    def test_schema_with_min_items_one_passes(self) -> None:
        # Default setUp planted minItems=1; just confirm it's accepted.
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(errors, [])


class TestErrorMessageQuality(_ProjectRootMixin):
    """REQ-05: error messages cite navigable positions."""

    @covers("REQ-0.0.29-08-05")
    def test_fixture_error_cites_path_and_line(self) -> None:
        path = _write_fixture(self.project_root, "bad.json", _empty_proof_diagnosis())
        errors = validate_advisor_proof_binding(self.project_root)
        self.assertEqual(len(errors), 1)
        rel = path.relative_to(self.project_root).as_posix()
        self.assertIn(rel, errors[0].message)
        self.assertRegex(errors[0].message, r":\d+")

    @covers("REQ-0.0.29-08-05")
    def test_ledger_error_cites_event_id(self) -> None:
        diag = _empty_proof_diagnosis("diag-x")
        _write_fixture(self.project_root, "x.json", diag)
        _write_ledger(
            self.project_root,
            [
                {
                    "event": "intrinsic-complexity-attestation",
                    "id": "ica-evt-005",
                    "diagnosis_id": "diag-x",
                }
            ],
        )
        errors = validate_advisor_proof_binding(self.project_root)
        ledger_errors = [e for e in errors if e.artifact == "ica-evt-005"]
        self.assertEqual(len(ledger_errors), 1)
        self.assertIn("ica-evt-005", ledger_errors[0].message)


class TestCliIntegration(_ProjectRootMixin):
    """REQ-03 / REQ-07f: --advisor-proof-binding wires through validate_cmd
    and is included in --all aggregation (`_resolve_scopes`).
    """

    @covers("REQ-0.0.29-08-03")
    def test_resolve_scopes_includes_advisor_proof_binding_when_flag_set(self) -> None:
        from gzkit.commands.validate_cmd import _resolve_scopes

        scopes = _resolve_scopes({"advisor_proof_binding": True})
        self.assertIn(
            "advisor_proof_binding",
            scopes,
            "--advisor-proof-binding must surface as an opt-in scope",
        )

    @covers("REQ-0.0.29-08-03")
    def test_collect_errors_dispatches_advisor_proof_binding(self) -> None:
        from gzkit.commands.validate_cmd import _collect_errors

        path = _write_fixture(self.project_root, "bad.json", _empty_proof_diagnosis())
        errors = _collect_errors(
            self.project_root,
            check_manifest=False,
            check_documents=False,
            check_surfaces=False,
            check_ledger=False,
            check_instructions=False,
            check_briefs=False,
            check_advisor_proof_binding=True,
        )
        proof_errors = [e for e in errors if e.type == "advisor_proof_binding"]
        self.assertEqual(len(proof_errors), 1)
        rel = path.relative_to(self.project_root).as_posix()
        self.assertIn(rel, proof_errors[0].message)


if __name__ == "__main__":
    unittest.main()
