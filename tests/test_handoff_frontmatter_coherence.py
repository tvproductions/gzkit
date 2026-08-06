"""Coherence tests for HandoffFrontmatter and the handoff-document gate.

Reconciles the authoring model (``HandoffFrontmatter``) with the fields its own
writers emit (``write_degenerate_exchange``, ``lock_manager._write_reaping_exchange``)
and its consumers require (``validate_lock_exchange_coupling``'s min-info fields,
``find_exchange_for_release``'s slug-bearing ``obpi_id``). Before this OBPI the
model was a strict consumer with a toothless authoring guard, so invalid-
frontmatter handoffs shipped.

@covers ADR-0.0.72 (OBPI-0.0.72-02)
"""

from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from pydantic import ValidationError

from gzkit.commands.quality import _build_check_steps
from gzkit.exchange_records import (
    AbandonSpec,
    exchange_dir,
    find_exchange_for_release,
    write_degenerate_exchange,
)
from gzkit.handoff_validation import (
    REQUIRED_SECTIONS,
    HandoffFrontmatter,
    validate_handoff_document,
)
from gzkit.lock_manager import LockData, _write_reaping_exchange
from gzkit.quality import _HANDOFF_ENFORCEMENT_CUTOVER, run_handoff_document_audit
from gzkit.traceability import covers

_SLUG_OBPI_ID = "OBPI-0.0.72-02-handoff-frontmatter-reconcile"

# Minimal, non-placeholder section bodies (no TBD/TODO/.../FIXME, no backtick
# file paths in Evidence so validate_referenced_files stays empty).
_SECTION_BODIES = {
    "Current State Summary": "Handoff schema reconciliation captured for this register entry.",
    "Important Context": "The frontmatter model now mirrors every field the writers emit.",
    "Decisions Made": "- Declared the writer fields explicitly and widened the OBPI id pattern.",
    "Immediate Next Steps": "1. Run the unit suite. 2. Confirm the coupling validator stays green.",
    "Pending Work / Open Loops": "- None outstanding for this register entry.",
    "Verification Checklist": "- [ ] Unit tests pass for the reconciled model.",
    "Evidence / Artifacts": "- The reconciled handoff validation module records the change.",
}


def _base_kwargs() -> dict[str, str]:
    """Return the five always-required HandoffFrontmatter fields with valid values."""
    return {
        "mode": "CREATE",
        "adr_id": "ADR-0.0.72",
        "branch": "main",
        "timestamp": "2026-06-13T00:00:00Z",
        "agent": "agent:test",
    }


def _full_document(frontmatter: dict[str, object]) -> str:
    """Build a complete handoff doc: frontmatter + all seven required sections."""
    parts = ["---", yaml.safe_dump(frontmatter, sort_keys=False).rstrip("\n"), "---", ""]
    for name in REQUIRED_SECTIONS:
        parts.extend([f"## {name}", "", _SECTION_BODIES[name], ""])
    return "\n".join(parts)


def _document_missing_section(frontmatter: dict[str, object]) -> str:
    """Build a handoff doc that is malformed by omitting one required section."""
    omit = "Evidence / Artifacts"
    parts = ["---", yaml.safe_dump(frontmatter, sort_keys=False).rstrip("\n"), "---", ""]
    for name in REQUIRED_SECTIONS:
        if name == omit:
            continue
        parts.extend([f"## {name}", "", _SECTION_BODIES[name], ""])
    return "\n".join(parts)


class TestHandoffFrontmatterCoherence(unittest.TestCase):
    """The authoring model must accept all writer/consumer fields, typo-defended."""

    @covers("REQ-0.0.72-02-01")
    def test_slug_bearing_obpi_id_validates_and_matches_consumer(self) -> None:
        # Full slug-bearing id (canonical obpi.json pattern) must validate.
        full = HandoffFrontmatter(**_base_kwargs(), obpi_id=_SLUG_OBPI_ID)
        self.assertEqual(full.obpi_id, _SLUG_OBPI_ID)
        # Short form must STILL validate — widening is additive, not a swap.
        short = HandoffFrontmatter(**_base_kwargs(), obpi_id="OBPI-0.0.72-02")
        self.assertEqual(short.obpi_id, "OBPI-0.0.72-02")
        # The slug-bearing consumer (find_exchange_for_release) exact-matches it.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff_dir = exchange_dir(root)
            handoff_dir.mkdir(parents=True)
            frontmatter = {**_base_kwargs(), "obpi_id": _SLUG_OBPI_ID}
            target = handoff_dir / "20260613T000000Z-handoff.md"
            target.write_text(_full_document(frontmatter), encoding="utf-8")
            found = find_exchange_for_release(root, obpi_id=_SLUG_OBPI_ID)
            self.assertEqual(found, target)

    @covers("REQ-0.0.72-02-02")
    def test_min_info_fields_accepted(self) -> None:
        model = HandoffFrontmatter(
            **_base_kwargs(),
            last_lock_event_timestamp="2026-06-13T00:00:00Z",
            last_commit_sha="abc123",
        )
        self.assertEqual(model.last_lock_event_timestamp, "2026-06-13T00:00:00Z")
        self.assertEqual(model.last_commit_sha, "abc123")

    @covers("REQ-0.0.72-02-03")
    def test_degenerate_and_reaping_fields_accepted(self) -> None:
        model = HandoffFrontmatter(
            **_base_kwargs(),
            abandoned=True,
            category="reaping",
            abandoned_by="agent:reaper",
            abandoned_at="2026-06-13T00:00:00Z",
            previous_agent="agent:holder",
            reason="ttl",
        )
        self.assertTrue(model.abandoned)
        self.assertEqual(model.category, "reaping")
        self.assertEqual(model.previous_agent, "agent:holder")
        self.assertEqual(model.reason, "ttl")

    @covers("REQ-0.0.72-02-04")
    def test_misspelled_field_still_raises(self) -> None:
        # Typo-defense is preserved: the explicit superset keeps extra="forbid",
        # so a misspelled key (triple-m) still raises rather than silently passing.
        with self.assertRaises(ValidationError):
            HandoffFrontmatter(**_base_kwargs(), last_commmit_sha="x")

    @covers("REQ-0.0.72-02-05")
    def test_real_writer_documents_roundtrip_clean(self) -> None:
        # Validate the REAL emitted documents (driven live), NOT synthetic
        # substitutes. Register entries (abandoned: true) are a distinct
        # shape-aware document class — terse bodies + self-referential deleted-
        # lock evidence must round-trip clean.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            exchange_dir(root).mkdir(parents=True)

            # Degenerate writer: its Evidence section points at the now-deleted
            # lock file; shape-awareness must NOT flag that as a missing reference.
            spec = AbandonSpec(category="network_loss", reason="session network interruption")
            degenerate_path = write_degenerate_exchange(
                root,
                obpi_id=_SLUG_OBPI_ID,
                adr_id="ADR-0.0.72",
                agent="agent:abandoner",
                spec=spec,
                last_claim_timestamp="2026-06-13T00:00:00Z",
                commit_sha="abc123",
                branch="main",
            )
            self.assertEqual(
                validate_handoff_document(degenerate_path.read_text(encoding="utf-8"), root),
                [],
            )

            # Reaping writer driven from a REAL full-slug lock: the adr_id must be
            # derived valid (ADR-0.0.72, not ADR-0.0.72-02-handoff-frontmatter),
            # and the terse two-section register entry must validate.
            lock = LockData(
                obpi_id=_SLUG_OBPI_ID,
                agent="agent:holder",
                pid=1,
                session_id="s",
                claimed_at="2026-06-13T00:00:00Z",
                branch="main",
                ttl_minutes=120,
            )
            reaping_path = _write_reaping_exchange(root, lock, "agent:reaper")
            reaping_text = reaping_path.read_text(encoding="utf-8")
            self.assertEqual(validate_handoff_document(reaping_text, root), [])
            self.assertIn("adr_id: ADR-0.0.72\n", reaping_text)

    @covers("REQ-0.0.72-02-05")
    def test_shape_awareness_does_not_weaken_session_handoffs(self) -> None:
        # A normal CREATE/RESUME handoff (no abandoned flag) missing a section is
        # STILL flagged — shape-awareness is scoped to register entries, never a
        # blanket bypass of the seven-section contract.
        violations = validate_handoff_document(_document_missing_section(_base_kwargs()), Path("."))
        self.assertTrue(any("Missing required section" in v for v in violations))


class TestHandoffDocumentAuditGate(unittest.TestCase):
    """validate_handoff_document is gate-wired and grandfathers legacy entries."""

    def test_audit_importable_and_registered_in_gz_check(self) -> None:
        # Closes the enforcement asymmetry: the strict consumer now has an
        # authoring-time gate registered in the gz check bundle.
        runners = [runner for _, runner in _build_check_steps()]
        self.assertIn(run_handoff_document_audit, runners)

    def test_audit_grandfathers_pre_cutover_enforces_post_cutover(self) -> None:
        cutover = datetime.fromisoformat(_HANDOFF_ENFORCEMENT_CUTOVER.replace("Z", "+00:00"))
        before = (cutover - timedelta(days=1)).isoformat().replace("+00:00", "Z")
        after = (cutover + timedelta(days=1)).isoformat().replace("+00:00", "Z")
        # A malformed register entry dated before the cutover is grandfathered.
        self.assertTrue(self._audit_for_malformed_handoff(before).success)
        # The same malformed shape dated on/after the cutover fails the gate.
        self.assertFalse(self._audit_for_malformed_handoff(after).success)

    def _audit_for_malformed_handoff(self, timestamp: str):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            handoff_dir = root / ".gzkit" / "handoffs"
            handoff_dir.mkdir(parents=True)
            frontmatter = {**_base_kwargs(), "timestamp": timestamp}
            (handoff_dir / "h.md").write_text(
                _document_missing_section(frontmatter), encoding="utf-8"
            )
            return run_handoff_document_audit(root)


if __name__ == "__main__":
    unittest.main()
