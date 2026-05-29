"""Tests for closeout REQ↔receipt-ID proof-binding validator (OBPI-0.0.63-03).

Covers:
    REQ-0.0.63-03-01 — legacy-safe parse of optional ``ln`` field on BriefStructure;
        briefs without ``ln`` load unchanged (empty list); briefs with ``ln`` round-trip
        a list of ``ReqEvidence``.
    REQ-0.0.63-03-02 — validator fails closed (exit-3-type error) when a REQ has no
        ``ln`` entry or an entry with empty ``receipt_ids``.
    REQ-0.0.63-03-03 — ledger-existence floor: a typo'd or fabricated receipt-ID
        (no matching artifact file) fails closed even when the entry exists.
    REQ-0.0.63-03-04 — validator returns no errors when every REQ has ≥1 ``ln``
        entry with a non-empty ``receipt_ids`` list and each ID resolves to a real
        receipt artifact.

All tests use ``tempfile.TemporaryDirectory`` for sandbox isolation; no live repo
state is consumed.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.governance.brief_structure import BriefStructure, ReqEvidence, parse_brief
from gzkit.governance.trust_audits.closeout_proof_binding import (
    validate_closeout_proof_binding,
)
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_VALID_BASE_FIELDS = {
    "id": "OBPI-0.0.99-01-test",
    "parent": "ADR-0.0.99-test-adr",
    "lane": "Heavy",
    "status": "Draft",
    "allowlist": ["src/x.py"],
    "reqs": ["REQ-0.0.99-01-01"],
    "verification": ["uv run gz lint"],
}


def _write_ceremony(project_root: Path, adr_id: str) -> Path:
    """Write a minimal ceremony state file for the given ADR ID."""
    ceremonies_dir = project_root / ".gzkit" / "ceremonies"
    ceremonies_dir.mkdir(parents=True, exist_ok=True)
    path = ceremonies_dir / f"{adr_id}.ceremony.json"
    path.write_text(
        json.dumps({"adr_id": adr_id, "current_step": 6, "started_at": "2026-01-01T00:00:00Z"}),
        encoding="utf-8",
    )
    return path


def _write_brief(
    adr_dir: Path, obpi_id: str, reqs: list[str], ln: list[dict] | None = None
) -> Path:
    """Write a minimal structured OBPI brief with optional ln frontmatter."""
    obpis_dir = adr_dir / "obpis"
    obpis_dir.mkdir(parents=True, exist_ok=True)
    brief_path = obpis_dir / f"{obpi_id}.md"

    fm: dict = {
        "id": obpi_id,
        "parent": adr_dir.name,
        "lane": "Heavy",
        "status": "Draft",
        "allowlist": ["src/x.py"],
        "reqs": reqs,
        "verification": ["uv run gz lint"],
    }
    if ln is not None:
        fm["ln"] = ln

    import yaml  # noqa: PLC0415 — stdlib-first; yaml is a project dep (pydantic transitive)

    fm_text = yaml.dump(fm, default_flow_style=False)
    brief_path.write_text(f"---\n{fm_text}---\n\n# {obpi_id}\n", encoding="utf-8")
    return brief_path


def _write_receipt(project_root: Path, receipt_id: str) -> Path:
    """Write a minimal receipt JSON artifact so the validator can confirm existence."""
    receipts_dir = project_root / "artifacts" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    path = receipts_dir / f"{receipt_id}.json"
    path.write_text(json.dumps({"id": receipt_id, "status": "pass"}), encoding="utf-8")
    return path


def _make_adr_dir(project_root: Path, adr_id: str) -> Path:
    """Create and return docs/design/adr/<adr_id>/ directory."""
    adr_dir = project_root / "docs" / "design" / "adr" / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    return adr_dir


# ---------------------------------------------------------------------------
# REQ-0.0.63-03-01: legacy-safe parse of optional ln field
# ---------------------------------------------------------------------------


class TestReqEvidenceModel(unittest.TestCase):
    """REQ-0.0.63-03-01 — BriefStructure.ln round-trips; legacy briefs load unchanged."""

    @covers("REQ-0.0.63-03-01")
    def test_brief_without_ln_loads_with_empty_list(self) -> None:
        """A structured brief that has no ln key parses to BriefStructure with ln=[]."""
        b = BriefStructure(**_VALID_BASE_FIELDS)
        self.assertEqual(b.ln, [])

    @covers("REQ-0.0.63-03-01")
    def test_brief_with_ln_roundtrips_req_evidence(self) -> None:
        """A structured brief with ln entries loads the correct ReqEvidence objects."""
        ln_entry = ReqEvidence(
            req_id="REQ-0.0.99-01-01",
            receipt_ids=["arb-ruff-abc123"],
            file_lines=["src/x.py:1"],
        )
        b = BriefStructure(**_VALID_BASE_FIELDS, ln=[ln_entry])
        self.assertEqual(len(b.ln), 1)
        self.assertEqual(b.ln[0].req_id, "REQ-0.0.99-01-01")
        self.assertEqual(b.ln[0].receipt_ids, ["arb-ruff-abc123"])
        self.assertEqual(b.ln[0].file_lines, ["src/x.py:1"])

    @covers("REQ-0.0.63-03-01")
    def test_req_evidence_rejects_extra_fields(self) -> None:
        """ReqEvidence has extra='forbid'; unexpected keys raise ValidationError."""
        from pydantic import ValidationError as PydanticValidationError  # noqa: PLC0415

        with self.assertRaises(PydanticValidationError):
            ReqEvidence(req_id="REQ-0.0.99-01-01", receipt_ids=[], unknown_field="bad")  # type: ignore

    @covers("REQ-0.0.63-03-01")
    def test_parse_brief_without_ln_returns_brief_structure(self) -> None:
        """parse_brief on a brief without ln in frontmatter returns BriefStructure with ln=[]."""
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = _make_adr_dir(Path(tmp), "ADR-0.0.99-test-adr")
            brief_path = _write_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"])
            result = parse_brief(brief_path)
            self.assertIsInstance(result, BriefStructure)
            self.assertEqual(result.ln, [])

    @covers("REQ-0.0.63-03-01")
    def test_parse_brief_with_ln_roundtrips(self) -> None:
        """parse_brief on a brief with ln entries round-trips ReqEvidence correctly."""
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = _make_adr_dir(Path(tmp), "ADR-0.0.99-test-adr")
            ln_data = [
                {"req_id": "REQ-0.0.99-01-01", "receipt_ids": ["arb-test-abc"], "file_lines": []}
            ]
            brief_path = _write_brief(
                adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"], ln=ln_data
            )
            result = parse_brief(brief_path)
            self.assertIsInstance(result, BriefStructure)
            self.assertEqual(len(result.ln), 1)
            self.assertEqual(result.ln[0].req_id, "REQ-0.0.99-01-01")
            self.assertEqual(result.ln[0].receipt_ids, ["arb-test-abc"])


# ---------------------------------------------------------------------------
# REQ-0.0.63-03-02: fail-close on unbound REQ
# ---------------------------------------------------------------------------


class TestUnboundReqFailsClosed(unittest.TestCase):
    """REQ-0.0.63-03-02 — validator exits-3-type error when a REQ has no ln entry."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.63-03-02")
    def test_no_ln_entry_for_req_produces_error(self) -> None:
        """A brief whose reqs contains REQ-A but ln is empty → validation error citing REQ-A."""
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        _write_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"])  # no ln

        errors = validate_closeout_proof_binding(self.root)

        self.assertGreater(len(errors), 0, "Expected ≥1 error for unbound REQ")
        types = {e.type for e in errors}
        self.assertIn("closeout_proof_binding", types)
        messages = " ".join(e.message for e in errors)
        self.assertIn("REQ-0.0.99-01-01", messages)

    @covers("REQ-0.0.63-03-02")
    def test_ln_entry_with_empty_receipt_ids_produces_error(self) -> None:
        """A brief with an ln entry for REQ-A but receipt_ids=[] → validation error."""
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        ln_data = [{"req_id": "REQ-0.0.99-01-01", "receipt_ids": [], "file_lines": []}]
        _write_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"], ln=ln_data)

        errors = validate_closeout_proof_binding(self.root)

        self.assertGreater(len(errors), 0, "Expected ≥1 error for empty receipt_ids")
        messages = " ".join(e.message for e in errors)
        self.assertIn("REQ-0.0.99-01-01", messages)

    @covers("REQ-0.0.63-03-02")
    def test_no_ceremony_file_means_out_of_scope(self) -> None:
        """An ADR with no ceremony file is not in scope; validator returns no errors."""
        adr_dir = _make_adr_dir(self.root, "ADR-0.0.99-test-adr")
        _write_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"])  # no ceremony

        errors = validate_closeout_proof_binding(self.root)

        self.assertEqual(errors, [], "ADR without ceremony file should be out of scope")


# ---------------------------------------------------------------------------
# REQ-0.0.63-03-03: ledger-existence floor (typo'd receipt-ID fails closed)
# ---------------------------------------------------------------------------


class TestLedgerExistenceFloor(unittest.TestCase):
    """REQ-0.0.63-03-03 — receipt-ID with no matching artifact fails closed."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.63-03-03")
    def test_typo_receipt_id_fails_closed(self) -> None:
        """A receipt-ID that has no matching artifacts/receipts/<id>.json → error."""
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        # The receipt-ID is cited in ln, but no artifact file is created
        ln_data = [
            {
                "req_id": "REQ-0.0.99-01-01",
                "receipt_ids": ["arb-typo-does-not-exist"],
                "file_lines": [],
            }
        ]
        _write_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"], ln=ln_data)

        errors = validate_closeout_proof_binding(self.root)

        self.assertGreater(len(errors), 0, "Expected ≥1 error for non-existent receipt artifact")
        messages = " ".join(e.message for e in errors)
        self.assertIn("arb-typo-does-not-exist", messages)


# ---------------------------------------------------------------------------
# REQ-0.0.63-03-04: exit 0 when all REQs are ledger-bound
# ---------------------------------------------------------------------------


class TestAllReqsBoundPasses(unittest.TestCase):
    """REQ-0.0.63-03-04 — no errors when every REQ has a ledger-present receipt-ID."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.63-03-04")
    def test_all_reqs_bound_with_existing_receipt_passes(self) -> None:
        """Each REQ has an ln entry with a ledger-present receipt-ID → no errors."""
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        _write_receipt(self.root, "arb-ruff-realreceipt")
        ln_data = [
            {
                "req_id": "REQ-0.0.99-01-01",
                "receipt_ids": ["arb-ruff-realreceipt"],
                "file_lines": ["src/x.py:1"],
            }
        ]
        _write_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"], ln=ln_data)

        errors = validate_closeout_proof_binding(self.root)

        self.assertEqual(errors, [], f"Expected no errors; got: {errors}")

    @covers("REQ-0.0.63-03-04")
    def test_multiple_reqs_all_bound_passes(self) -> None:
        """Multiple REQs, each with a valid ln entry and receipt, all pass."""
        adr_id = "ADR-0.0.99-multi-req-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        _write_receipt(self.root, "arb-ruff-receipt01")
        _write_receipt(self.root, "arb-typecheck-receipt02")
        ln_data = [
            {"req_id": "REQ-0.0.99-01-01", "receipt_ids": ["arb-ruff-receipt01"], "file_lines": []},
            {
                "req_id": "REQ-0.0.99-01-02",
                "receipt_ids": ["arb-typecheck-receipt02"],
                "file_lines": [],
            },
        ]
        _write_brief(
            adr_dir,
            "OBPI-0.0.99-01-multi",
            ["REQ-0.0.99-01-01", "REQ-0.0.99-01-02"],
            ln=ln_data,
        )

        errors = validate_closeout_proof_binding(self.root)

        self.assertEqual(errors, [], f"Expected no errors; got: {errors}")


if __name__ == "__main__":
    unittest.main()
