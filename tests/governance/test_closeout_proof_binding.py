"""Tests for closeout REQ↔receipt-ID proof-binding validator (OBPI-0.0.63-03).

Covers:
    REQ-0.0.63-03-01 — legacy-safe parse of optional ``ln`` field on BriefStructure.
    REQ-0.0.63-03-02 — validator fails closed when a body Acceptance-Criteria REQ
        has no ``ln`` entry or an entry with empty ``receipt_ids``. Briefs are
        legacy-shaped (REQs in the body, not frontmatter) — the real corpus shape.
    REQ-0.0.63-03-03 — ledger-existence floor: a cited receipt-ID resolves to a
        ledger receipt-binding event (``evidence.resolved_receipt_ids``), never a
        file on disk. A receipt absent from the ledger fails closed even when an
        ``artifacts/receipts/`` file is present; a ledger-bound receipt passes even
        when no file exists (survives the ARB cache flush, GHI #593).
    REQ-0.0.63-03-04 — validator returns no errors when every body REQ has a
        ledger-present receipt-ID, and is out of scope for completed/absent ceremonies.

Briefs in these fixtures are LEGACY-shaped (REQs under ``## Acceptance Criteria``,
no structured frontmatter ``reqs:``) because that is how 545/546 real briefs are
shaped (GHI #566). Scope is gated on an *in-progress* closeout ceremony
(``completed_at`` unset).
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


def _write_ceremony(project_root: Path, adr_id: str, *, completed: bool = False) -> Path:
    """Write a ceremony state file. completed=False means closeout is in progress."""
    ceremonies_dir = project_root / ".gzkit" / "ceremonies"
    ceremonies_dir.mkdir(parents=True, exist_ok=True)
    path = ceremonies_dir / f"{adr_id}.ceremony.json"
    path.write_text(
        json.dumps(
            {
                "adr_id": adr_id,
                "current_step": 6,
                "started_at": "2026-01-01T00:00:00Z",
                "completed_at": "2026-01-02T00:00:00Z" if completed else None,
            }
        ),
        encoding="utf-8",
    )
    return path


def _write_legacy_brief(
    adr_dir: Path, obpi_id: str, body_reqs: list[str], ln: list[dict] | None = None
) -> Path:
    """Write a LEGACY-shaped brief: minimal frontmatter (+ optional ln) and body REQs.

    The brief has NO structured frontmatter ``reqs:``/``allowlist:``/``verification:``
    — REQs live in the body ``## Acceptance Criteria`` section, as in real briefs.
    """
    obpis_dir = adr_dir / "obpis"
    obpis_dir.mkdir(parents=True, exist_ok=True)
    brief_path = obpis_dir / f"{obpi_id}.md"

    import yaml  # noqa: PLC0415 — yaml is a project dependency (pydantic transitive)

    fm: dict = {"id": obpi_id, "parent": adr_dir.name, "lane": "Heavy", "status": "Draft"}
    if ln is not None:
        fm["ln"] = ln
    fm_text = yaml.dump(fm, default_flow_style=False)

    ac_lines = "\n".join(f"- [ ] {req} [BEHAVIOR]: criterion {req}" for req in body_reqs)
    body = f"# {obpi_id}\n\n## Acceptance Criteria\n\n{ac_lines}\n"
    brief_path.write_text(f"---\n{fm_text}---\n\n{body}", encoding="utf-8")
    return brief_path


def _write_receipt(project_root: Path, receipt_id: str) -> Path:
    """Write an ARB receipt artifact FILE (the flushable, non-durable cache)."""
    receipts_dir = project_root / "artifacts" / "receipts"
    receipts_dir.mkdir(parents=True, exist_ok=True)
    path = receipts_dir / f"{receipt_id}.json"
    path.write_text(json.dumps({"id": receipt_id, "status": "pass"}), encoding="utf-8")
    return path


def _write_ledger_receipt(project_root: Path, receipt_ids: list[str]) -> Path:
    """Bind receipt-IDs into the ledger via ``evidence.resolved_receipt_ids``.

    This is the DURABLE record `gz obpi complete` writes at completion — it
    survives an ``artifacts/receipts/`` cache flush, unlike the receipt file.
    """
    gz_dir = project_root / ".gzkit"
    gz_dir.mkdir(parents=True, exist_ok=True)
    path = gz_dir / "ledger.jsonl"
    event = {
        "schema": "gzkit.ledger.v1",
        "event": "obpi_receipt_emitted",
        "id": "OBPI-0.0.99-01-test",
        "evidence": {"resolved_receipt_ids": list(receipt_ids), "exit_status": 0},
    }
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event) + "\n")
    return path


def _make_adr_dir(project_root: Path, adr_id: str) -> Path:
    adr_dir = project_root / "docs" / "design" / "adr" / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    return adr_dir


# ---------------------------------------------------------------------------
# REQ-0.0.63-03-01: optional ln field model (legacy-safe)
# ---------------------------------------------------------------------------


class TestReqEvidenceModel(unittest.TestCase):
    """REQ-0.0.63-03-01 — BriefStructure.ln round-trips; legacy briefs load unchanged."""

    @covers("REQ-0.0.63-03-01")
    def test_brief_without_ln_loads_with_empty_list(self) -> None:
        b = BriefStructure(**_VALID_BASE_FIELDS)
        self.assertEqual(b.ln, [])

    @covers("REQ-0.0.63-03-01")
    def test_brief_with_ln_roundtrips_req_evidence(self) -> None:
        entry = ReqEvidence(
            req_id="REQ-0.0.99-01-01", receipt_ids=["arb-ruff-abc123"], file_lines=["src/x.py:1"]
        )
        b = BriefStructure(**_VALID_BASE_FIELDS, ln=[entry])
        self.assertEqual(len(b.ln), 1)
        self.assertEqual(b.ln[0].req_id, "REQ-0.0.99-01-01")
        self.assertEqual(b.ln[0].receipt_ids, ["arb-ruff-abc123"])

    @covers("REQ-0.0.63-03-01")
    def test_req_evidence_rejects_extra_fields(self) -> None:
        from pydantic import ValidationError as PydanticValidationError  # noqa: PLC0415

        with self.assertRaises(PydanticValidationError):
            ReqEvidence(req_id="REQ-0.0.99-01-01", receipt_ids=[], bogus="x")  # type: ignore

    @covers("REQ-0.0.63-03-01")
    def test_parse_legacy_brief_without_reqs_frontmatter(self) -> None:
        """A legacy brief (no frontmatter reqs/allowlist/verification) still parses."""
        with tempfile.TemporaryDirectory() as tmp:
            adr_dir = _make_adr_dir(Path(tmp), "ADR-0.0.99-test-adr")
            brief = _write_legacy_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"])
            # parse_brief returns LegacyBriefShape for these; the validator does not
            # depend on BriefStructure for legacy briefs (it reads body + raw ln).
            result = parse_brief(brief)
            self.assertIsNotNone(result)


# ---------------------------------------------------------------------------
# REQ-0.0.63-03-02: fail-close on unbound body Acceptance-Criteria REQ
# ---------------------------------------------------------------------------


class TestUnboundReqFailsClosed(unittest.TestCase):
    """REQ-0.0.63-03-02 — validator fails on a body REQ with no ln binding.

    This is the regression test for GHI #566: the prior implementation read
    frontmatter ``reqs`` and skipped legacy briefs, so this case passed vacuously.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.63-03-02")
    def test_legacy_brief_body_req_without_ln_fails_closed(self) -> None:
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)  # in progress
        adr_dir = _make_adr_dir(self.root, adr_id)
        _write_legacy_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"])  # body REQ, no ln

        errors = validate_closeout_proof_binding(self.root)

        self.assertGreater(len(errors), 0, "Expected ≥1 error for unbound body REQ")
        self.assertIn("closeout_proof_binding", {e.type for e in errors})
        self.assertIn("REQ-0.0.99-01-01", " ".join(e.message for e in errors))

    @covers("REQ-0.0.63-03-02")
    def test_ln_entry_with_empty_receipt_ids_fails_closed(self) -> None:
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        ln = [{"req_id": "REQ-0.0.99-01-01", "receipt_ids": [], "file_lines": []}]
        _write_legacy_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"], ln=ln)

        errors = validate_closeout_proof_binding(self.root)

        self.assertGreater(len(errors), 0, "Expected ≥1 error for empty receipt_ids")
        self.assertIn("REQ-0.0.99-01-01", " ".join(e.message for e in errors))


# ---------------------------------------------------------------------------
# REQ-0.0.63-03-03: ledger-existence floor
# ---------------------------------------------------------------------------


class TestLedgerExistenceFloor(unittest.TestCase):
    """REQ-0.0.63-03-03 — the floor is ledger-binding, not file presence (GHI #593).

    The binding moment is ``gz obpi complete`` (which writes
    ``evidence.resolved_receipt_ids``); that always precedes the ADR-closeout
    gate, so the gate resolves against the ledger — never the flushable
    ``artifacts/receipts/`` cache. These two tests pin the discriminating
    semantics: file presence is neither sufficient nor necessary.
    """

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.63-03-03")
    def test_receipt_absent_from_ledger_fails_closed_even_with_file(self) -> None:
        """File presence is NOT sufficient: a receipt unbound in the ledger fails closed."""
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        _write_receipt(self.root, "arb-file-only-unbound")  # file exists, but no ledger binding
        ln = [
            {
                "req_id": "REQ-0.0.99-01-01",
                "receipt_ids": ["arb-file-only-unbound"],
                "file_lines": [],
            }
        ]
        _write_legacy_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"], ln=ln)

        errors = validate_closeout_proof_binding(self.root)

        self.assertGreater(
            len(errors), 0, "A receipt absent from the ledger must fail closed even with a file"
        )
        self.assertIn("arb-file-only-unbound", " ".join(e.message for e in errors))

    @covers("REQ-0.0.63-03-03")
    def test_receipt_bound_in_ledger_passes_without_file(self) -> None:
        """File presence is NOT necessary: a ledger-bound receipt passes, no file (flush-safe)."""
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        _write_ledger_receipt(self.root, ["arb-ledger-bound"])  # ledger binding, NO file on disk
        ln = [{"req_id": "REQ-0.0.99-01-01", "receipt_ids": ["arb-ledger-bound"], "file_lines": []}]
        _write_legacy_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"], ln=ln)

        errors = validate_closeout_proof_binding(self.root)

        self.assertEqual(errors, [], f"Ledger-bound receipt must pass with no file; got: {errors}")


# ---------------------------------------------------------------------------
# REQ-0.0.63-03-04: pass when bound; out of scope when ceremony done/absent
# ---------------------------------------------------------------------------


class TestBoundAndScope(unittest.TestCase):
    """REQ-0.0.63-03-04 — passes when bound; scope honors in-progress ceremony only."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    @covers("REQ-0.0.63-03-04")
    def test_all_body_reqs_bound_with_existing_receipt_passes(self) -> None:
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id)
        adr_dir = _make_adr_dir(self.root, adr_id)
        _write_ledger_receipt(self.root, ["arb-ruff-real"])
        ln = [
            {"req_id": "REQ-0.0.99-01-01", "receipt_ids": ["arb-ruff-real"], "file_lines": []},
            {"req_id": "REQ-0.0.99-01-02", "receipt_ids": ["arb-ruff-real"], "file_lines": []},
        ]
        _write_legacy_brief(
            adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01", "REQ-0.0.99-01-02"], ln=ln
        )

        errors = validate_closeout_proof_binding(self.root)

        self.assertEqual(errors, [], f"Expected no errors; got: {errors}")

    @covers("REQ-0.0.63-03-04")
    def test_completed_ceremony_is_out_of_scope(self) -> None:
        """A finished closeout (completed_at set) is out of scope even with unbound REQs."""
        adr_id = "ADR-0.0.99-test-adr"
        _write_ceremony(self.root, adr_id, completed=True)
        adr_dir = _make_adr_dir(self.root, adr_id)
        _write_legacy_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"])  # no ln

        errors = validate_closeout_proof_binding(self.root)

        self.assertEqual(errors, [], "Completed ceremony must be out of scope")

    @covers("REQ-0.0.63-03-04")
    def test_no_ceremony_file_is_out_of_scope(self) -> None:
        adr_dir = _make_adr_dir(self.root, "ADR-0.0.99-test-adr")
        _write_legacy_brief(adr_dir, "OBPI-0.0.99-01-test", ["REQ-0.0.99-01-01"])  # no ceremony

        errors = validate_closeout_proof_binding(self.root)

        self.assertEqual(errors, [], "ADR without an in-progress ceremony must be out of scope")


if __name__ == "__main__":
    unittest.main()
