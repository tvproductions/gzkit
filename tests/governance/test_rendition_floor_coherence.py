"""Tests for the rendition floor-coherence gate (GHI #623, corrective to ADR-0.0.37).

The REAL content witness that repudiated OBPI-0.0.37-22 only simulated: every
invariant-tier corpus entry MUST appear verbatim in the committed rendition for
its surface. These tests assert the *semantics* of canon→rendition coherence —
a rendition that drops an invariant entry is a fail-closed defect — not the
string shape of any one message.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.content.corpus_store import append_entry
from gzkit.content.models.corpus import CorpusEntry
from gzkit.content.rendition_store import save_rendition
from gzkit.governance.trust_audits.rendition_floor_coherence import (
    validate_rendition_floor_coherence,
)
from gzkit.mx import marker as _marker
from gzkit.mx.marker import Marker
from gzkit.traceability import covers
from tests.governance.common import QuietAdvisoriesMixin

_INV = "Never, ever again give me that TTY or PTY bullshit — attestation is sacrosanct."
_INV2 = "There is no such thing as a headless OBPI: every OBPI traces to a parent ADR."


def _entry(text: str, *, tier: str = "invariant", entry_id: str = "corpus-x") -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="attestation",
        tier=tier,  # type: ignore[arg-type]
        classification="Judgment",
        text=text,
        origin="test",
        ts="2026-01-01T00:00:00+00:00",
    )


class _TempProject(QuietAdvisoriesMixin):
    def setUp(self) -> None:
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".gzkit").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()


class TestFloorViolation(_TempProject):
    @covers("REQ-0.0.74-09-02")
    def test_missing_invariant_entry_is_fail_closed(self) -> None:
        """A rendition that omits an invariant-tier corpus entry returns one error."""
        append_entry(self.root, "AGENTS.md", _entry(_INV, entry_id="corpus-tty"))
        save_rendition(self.root, "AGENTS.md", "claude", b"# AGENTS.md\n\nUnrelated body.\n")

        errors = validate_rendition_floor_coherence(self.root, fail_closed=True)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "rendition_floor_coherence")
        self.assertIn("corpus-tty", errors[0].message)

    def test_one_error_per_rendition_lists_every_missing_entry(self) -> None:
        """Two missing invariants on one rendition → one error naming both ids."""
        append_entry(self.root, "AGENTS.md", _entry(_INV, entry_id="corpus-tty"))
        append_entry(self.root, "AGENTS.md", _entry(_INV2, entry_id="corpus-headless"))
        save_rendition(self.root, "AGENTS.md", "claude", b"# AGENTS.md\n\nNeither here.\n")

        errors = validate_rendition_floor_coherence(self.root, fail_closed=True)

        self.assertEqual(len(errors), 1)
        self.assertIn("corpus-tty", errors[0].message)
        self.assertIn("corpus-headless", errors[0].message)


class TestFloorSatisfied(_TempProject):
    def test_rendition_containing_all_invariants_verbatim_passes(self) -> None:
        """A rendition that carries every invariant entry verbatim returns no errors."""
        append_entry(self.root, "AGENTS.md", _entry(_INV, entry_id="corpus-tty"))
        body = f"# AGENTS.md\n\nPreamble.\n\n{_INV}\n\nMore.\n".encode()
        save_rendition(self.root, "AGENTS.md", "claude", body)

        self.assertEqual(validate_rendition_floor_coherence(self.root), [])

    def test_compressible_entries_are_not_required_verbatim(self) -> None:
        """Only invariant-tier entries are floor-enforced; compressible may be absent."""
        note = _entry("a summarizable note", tier="compressible", entry_id="c-1")
        append_entry(self.root, "AGENTS.md", note)
        save_rendition(self.root, "AGENTS.md", "claude", b"# AGENTS.md\n\nNo note here.\n")

        self.assertEqual(validate_rendition_floor_coherence(self.root), [])


class TestBootstrapSafe(_TempProject):
    def test_no_renditions_dir_returns_empty(self) -> None:
        self.assertEqual(validate_rendition_floor_coherence(self.root), [])

    def test_rendition_without_corpus_returns_empty(self) -> None:
        """A surface with a rendition but no corpus cannot violate a floor."""
        save_rendition(self.root, "AGENTS.md", "claude", b"# AGENTS.md\n")
        self.assertEqual(validate_rendition_floor_coherence(self.root), [])


class TestCheckpointWiringFloor(_TempProject):
    """OBPI-0.0.74-09: the gate resolves severity via the shared MX checkpoint.

    Outside the hangar (no marker): fail-closed by default.
    Inside the hangar (marker present): advisory (warns, no errors).
    """

    @covers("REQ-0.0.74-09-01")
    def test_without_mx_marker_gate_is_fail_closed(self) -> None:
        """No MX marker → default mode is fail-closed (full strength outside the hangar)."""
        append_entry(self.root, "AGENTS.md", _entry(_INV, entry_id="corpus-tty"))
        save_rendition(self.root, "AGENTS.md", "claude", b"# AGENTS.md\n\nUnrelated body.\n")
        errors = validate_rendition_floor_coherence(self.root)
        self.assertEqual(len(errors), 1, "outside hangar: gate must be fail-closed by default")

    @covers("REQ-0.0.74-09-01")
    def test_with_mx_marker_gate_is_advisory(self) -> None:
        """Active MX marker → default mode is advisory (gates demote inside the hangar)."""
        append_entry(self.root, "AGENTS.md", _entry(_INV, entry_id="corpus-tty"))
        save_rendition(self.root, "AGENTS.md", "claude", b"# AGENTS.md\n\nUnrelated body.\n")
        _marker.write(Marker(session_id="test-session"), self.root)
        errors = validate_rendition_floor_coherence(self.root)
        self.assertEqual(errors, [], "inside hangar: gate must be advisory by default")


if __name__ == "__main__":
    unittest.main()
