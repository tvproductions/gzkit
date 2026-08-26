"""Tests for the corpus retirement-witness gate (GHI #885, GHI #878).

A retraction row in a corpus is a canon change: ``Corpus.retired_ids()`` folds
the on-disk pointer and the entry leaves the effective corpus. Layer 2 must
carry a witness for that change, and the witness must name the SUBJECT — the
id actually retired — not merely exist.

These tests assert that semantics. The load-bearing one is
``test_event_for_a_different_id_does_not_witness_this_tombstone``: a gate that
answers "does an event of this type exist" is the presence-check substitution
``AGENTS.md`` § DO IT RIGHT forbids, and it is precisely how seven unwitnessed
retirements sat green on ``main``. Deleting the subject comparison must fail
that test.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.content.corpus_store import append_entry
from gzkit.content.models.corpus import CorpusEntry
from gzkit.governance.trust_audits.corpus_retirement_witness import (
    validate_corpus_retirement_witness,
)
from gzkit.ledger import Ledger
from gzkit.ledger_events import (
    corpus_entry_retired_event,
    corpus_retirement_reconciled_event,
)
from tests.governance.common import QuietAdvisoriesMixin

_LIVE = "Human attestation is sacrosanct and gold; the mechanism serves it."


def _entry(
    entry_id: str,
    *,
    text: str = _LIVE,
    tier: str = "invariant",
    retires: str | None = None,
    supersedes: str | None = None,
) -> CorpusEntry:
    return CorpusEntry(
        id=entry_id,
        surface="AGENTS.md",
        section="attestation",
        tier=tier,
        classification="Judgment",
        text=text,
        origin="test",
        ts="2026-01-01T00:00:00+00:00",
        retires=retires,
        supersedes=supersedes,
    )


class _TempProject(QuietAdvisoriesMixin, unittest.TestCase):
    def setUp(self) -> None:
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        (self.root / ".gzkit").mkdir()
        self.ledger = Ledger(self.root / ".gzkit" / "ledger.jsonl")
        self.ledger.create()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _retire_event(self, retired_id: str, retraction_id: str = "corpus-tomb") -> None:
        self.ledger.append(
            corpus_entry_retired_event(
                surface="AGENTS.md",
                retired_entry_id=retired_id,
                retraction_entry_id=retraction_id,
                reason="superseded",
                tier="invariant",
                floor_added=set(),
                floor_removed={retired_id},
            )
        )


class TestWitnessPresent(_TempProject):
    def test_tombstone_with_matching_retired_event_is_clean(self) -> None:
        """A governed retirement — corpus pointer plus a subject-matching event — passes."""
        append_entry(self.root, "AGENTS.md", _entry("corpus-a"))
        append_entry(self.root, "AGENTS.md", _entry("corpus-tomb", retires="corpus-a"))
        self._retire_event("corpus-a")

        self.assertEqual(validate_corpus_retirement_witness(self.root), [])

    def test_reconciled_event_also_witnesses_a_tombstone(self) -> None:
        """The repair event is a legitimate witness (GHI #885 arm 2).

        A tombstone reconciled after the fact is accounted for in Layer 2 without
        claiming the governed procedure ran, so the gate must accept it — otherwise
        arm 2's repair cannot clear arm 1's gate and the seven stay permanently red.
        """
        append_entry(self.root, "AGENTS.md", _entry("corpus-a"))
        append_entry(self.root, "AGENTS.md", _entry("corpus-tomb", retires="corpus-a"))
        self.ledger.append(
            corpus_retirement_reconciled_event(
                surface="AGENTS.md",
                retired_entry_id="corpus-a",
                retraction_entry_id="corpus-tomb",
                reason="tombstone found without witness; reconciled under GHI #885",
            )
        )

        self.assertEqual(validate_corpus_retirement_witness(self.root), [])


class TestWitnessMissing(_TempProject):
    def test_tombstone_with_no_event_is_flagged(self) -> None:
        """The bypass class: a hand-appended retraction row with no Layer-2 witness."""
        append_entry(self.root, "AGENTS.md", _entry("corpus-a"))
        append_entry(self.root, "AGENTS.md", _entry("corpus-tomb", retires="corpus-a"))

        errors = validate_corpus_retirement_witness(self.root)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "corpus_retirement_witness")
        self.assertIn("corpus-a", errors[0].message)

    def test_event_for_a_different_id_does_not_witness_this_tombstone(self) -> None:
        """SUBJECT BINDING — the defect this gate exists to close (GHI #885).

        An event of the right TYPE exists, for an unrelated id. A presence check
        passes here; a subject-bound check does not. Measured on `main` 2026-08-26:
        five `corpus_entry_retired` events existed while seven tombstones went
        unwitnessed, and every validator read green.
        """
        append_entry(self.root, "AGENTS.md", _entry("corpus-a"))
        append_entry(self.root, "AGENTS.md", _entry("corpus-tomb", retires="corpus-a"))
        self._retire_event("corpus-SOMETHING-ELSE")

        errors = validate_corpus_retirement_witness(self.root)

        self.assertEqual(
            len(errors),
            1,
            "an event naming a different retired_entry_id must not witness this "
            "tombstone — matching on type alone is the presence-check substitution",
        )
        self.assertIn("corpus-a", errors[0].message)

    def test_supersedes_pointer_is_covered_too(self) -> None:
        """`supersedes` retires its target exactly as `retires` does.

        `content/models/corpus.py` warns that a fence covering `retires` and
        quietly missing `supersedes` is a live trap; both pointers must be walked.
        """
        append_entry(self.root, "AGENTS.md", _entry("corpus-a"))
        append_entry(
            self.root, "AGENTS.md", _entry("corpus-b", text="replacement", supersedes="corpus-a")
        )

        errors = validate_corpus_retirement_witness(self.root)

        self.assertEqual(len(errors), 1)
        self.assertIn("corpus-a", errors[0].message)

    def test_each_unwitnessed_tombstone_yields_its_own_error(self) -> None:
        """Errors are per-subject, so a repair pass can act on each id."""
        for name in ("a", "b", "c"):
            append_entry(self.root, "AGENTS.md", _entry(f"corpus-{name}"))
            append_entry(
                self.root, "AGENTS.md", _entry(f"corpus-tomb-{name}", retires=f"corpus-{name}")
            )

        errors = validate_corpus_retirement_witness(self.root)

        self.assertEqual(len(errors), 3)
        self.assertEqual({e.field for e in errors}, {"corpus-a", "corpus-b", "corpus-c"})


class TestBootstrapSafety(_TempProject):
    def test_absent_corpus_directory_is_clean(self) -> None:
        """A project with no corpus has nothing to witness."""
        self.assertEqual(validate_corpus_retirement_witness(self.root), [])

    def test_corpus_with_no_retirements_is_clean(self) -> None:
        """Live entries carrying no retirement pointer are not retirements."""
        append_entry(self.root, "AGENTS.md", _entry("corpus-a"))

        self.assertEqual(validate_corpus_retirement_witness(self.root), [])


if __name__ == "__main__":
    unittest.main()
