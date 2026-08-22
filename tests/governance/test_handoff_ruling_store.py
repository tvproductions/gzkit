"""The settled-ruling corpus is transported by reference, not by copied prose (GHI #838).

Measured on `20260822T132232Z`: 98,247 of 107,480 bytes — 91.4% of the document —
were the carried corpus, because ``_carried_settled`` read its entries out of the
predecessor's RENDERED BODY. Every session therefore re-embedded all 457 rulings as
text purely to hand them to the next one, and seven authored handoffs over two days
spent 687,729 bytes transporting a corpus that is conceptually one list.

The repair separates the STORE from the TRANSPORT. Rulings live in one append-only
`.gzkit/handoffs/rulings.jsonl`; a handoff carries a count and a pointer. Nothing
retires, nothing is dropped, and ``ruling_key`` is untouched — so this cannot reach
the silent-loss direction that `handoff_api._ruling_key`'s docstring names as the
worse of the two, and that GHI #838 explicitly rules out fixing by loosening.

It also deletes a failure class rather than defending against it. ``_ruling_source``
exists only because the corpus travels THROUGH documents, one of which — the
machine-written floor bookmark — carries none by construction and acted as a sink
(453 rulings to 0, repaired in `02ca03ee`). A store cannot be sunk by an empty
document in the chain.

@covers GHI #838
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.handoff_api import create_handoff, resume_handoff, settled_rulings
from gzkit.handoff_rulings import (
    RULINGS_FILENAME,
    dedup_rulings,
    read_rulings,
    record_rulings,
    ruling_key,
    rulings_store_path,
)

SECTIONS = {
    "Current State Summary": "The work landed and the gate is green.",
    "Important Context": "The store is append-only; entries are never rewritten.",
    "Decisions Made": (
        "- [operator-ruled] Ship the transport fix (verbatim: 'do the 838 transport fix')."
    ),
    "Immediate Next Steps": "1. Verify the corpus survived the cutover.",
    "Pending Work / Open Loops": "Nothing deferred.",
    "Verification Checklist": "uv run gz check",
    "Evidence / Artifacts": "`EVIDENCE.md`",
}


def _sections(**overrides: str) -> dict[str, str]:
    return {**SECTIONS, **overrides}


def _project(root: Path) -> Path:
    """Return a project root whose Evidence reference resolves.

    ``validate_handoff_document`` checks every path cited in Evidence / Artifacts
    against disk, so a fixture that cites a file it never creates fails the gate
    for a reason unrelated to what these tests assert.
    """
    root.mkdir(parents=True, exist_ok=True)
    (root / "EVIDENCE.md").write_text("evidence\n", encoding="utf-8")
    return root


def _chained(base: Path) -> Path:
    """Author a chain root and return its SUCCESSOR.

    Only a successor inherits, so only a successor renders the pointer. A test
    that measured an unlinked handoff would pass no matter how large the corpus
    grew, which is the vacuous shape the discriminator in `.gzkit/rules/tests.md`
    exists to catch.
    """
    root = create_handoff(
        branch="main",
        agent="claude-code",
        slug="root",
        sections=_sections(),
        base_path=base,
    )
    return create_handoff(
        branch="main",
        agent="claude-code",
        slug="successor",
        sections=_sections(),
        continues_from=root.name,
        base_path=base,
    )


class RulingStoreTests(unittest.TestCase):
    """The store is an append-only log keyed on ruling identity."""

    def test_record_appends_new_entries_and_returns_the_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            corpus = record_rulings(["Ruling A", "Ruling B"], base_path=base, source="first.md")
            self.assertEqual(corpus, ["Ruling A", "Ruling B"])
            self.assertEqual(read_rulings(base), ["Ruling A", "Ruling B"])

    def test_record_is_idempotent_on_ruling_key(self) -> None:
        """Re-recording a booked ruling is a no-op, not a second line.

        The transport ran every session; without idempotence the store would
        reproduce the exact multiplication it was built to end.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            record_rulings(["Ruling A"], base_path=base, source="first.md")
            # Same ruling, different quote glyph and casing — what ruling_key folds.
            corpus = record_rulings(["ruling a", "Ruling B"], base_path=base, source="second.md")
            self.assertEqual(corpus, ["Ruling A", "Ruling B"])
            lines = rulings_store_path(base).read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 2, "an already-booked ruling must not append a line")

    def test_store_records_provenance_per_entry(self) -> None:
        """Each line names the handoff that booked it, so the log stays auditable."""
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            record_rulings(["Ruling A"], base_path=base, source="20260822T140000Z-work.md")
            line = json.loads(rulings_store_path(base).read_text(encoding="utf-8").strip())
            self.assertEqual(line["text"], "Ruling A")
            self.assertEqual(line["source"], "20260822T140000Z-work.md")
            self.assertTrue(line["ts"], "every entry carries a booking timestamp")

    def test_missing_store_reads_empty_rather_than_raising(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            self.assertFalse(rulings_store_path(base).exists())
            self.assertEqual(read_rulings(base), [])

    def test_ruling_key_still_folds_only_meaningless_difference(self) -> None:
        """The identity rule is CARRIED OVER unchanged, not re-litigated here.

        GHI #838 rejects a fix that widens it: collapsing two genuinely distinct
        rulings drops a booked operator ruling silently. This test pins that the
        transport repair inherited the narrow key rather than relaxing it.
        """
        self.assertEqual(ruling_key("Ship  it"), ruling_key("ship it"))
        self.assertEqual(ruling_key("Ship 'it'"), ruling_key('Ship "it"'))
        self.assertNotEqual(ruling_key("Ship it"), ruling_key("Ship it now"))
        self.assertEqual(dedup_rulings(["A", "a", "B"]), ["A", "B"])


class HandoffCarriesPointerNotCorpusTests(unittest.TestCase):
    """A handoff names the corpus; it no longer embeds it."""

    def test_created_handoff_carries_a_pointer_instead_of_every_ruling(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            record_rulings([f"Booked ruling {n}" for n in range(50)], base_path=base, source="seed")
            root = create_handoff(
                branch="main",
                agent="claude-code",
                slug="root",
                sections=_sections(),
                base_path=base,
            )
            # Chained deliberately: a handoff with no `continues_from` is a chain
            # root and inherits nothing (the GHI #709 guarantee), so it renders no
            # pointer at all. The claim under test is about a SUCCESSOR.
            path = create_handoff(
                branch="main",
                agent="claude-code",
                slug="pointer",
                sections=_sections(),
                continues_from=root.name,
                base_path=base,
            )
            body = path.read_text(encoding="utf-8")
            self.assertIn(RULINGS_FILENAME, body, "the handoff must name the corpus it points at")
            self.assertNotIn(
                "Booked ruling 7",
                body,
                "the corpus must NOT be copied into the document — that is the 91.4% "
                "of bytes this repair removes",
            )

    def test_successor_inherits_the_full_corpus_through_the_store(self) -> None:
        """The load-bearing property: carry-forward survives without copied prose.

        This is what makes the pointer safe. If it fails, the repair has traded a
        large document for a dropped corpus, which is the worse failure direction.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            record_rulings(["Earlier ruling holds."], base_path=base, source="seed")
            first = create_handoff(
                branch="main",
                agent="claude-code",
                slug="first",
                sections=_sections(),
                base_path=base,
            )
            self.assertNotIn("Earlier ruling holds.", first.read_text(encoding="utf-8"))

            create_handoff(
                branch="main",
                agent="claude-code",
                slug="second",
                sections=_sections(),
                continues_from=first.name,
                base_path=base,
            )
            corpus = read_rulings(base)
            self.assertIn("Earlier ruling holds.", corpus)
            self.assertIn(
                "Ship the transport fix (verbatim: 'do the 838 transport fix').",
                corpus,
                "the predecessor's operator-ruled decision must be promoted into the store",
            )

    def test_legacy_prose_ancestor_still_contributes_its_corpus(self) -> None:
        """The cutover cannot drop what pre-store handoffs carry in their bodies.

        Every handoff authored before this repair holds its rulings as prose and
        nothing else. If the ancestor walk stopped reading them, the transition
        itself would be the largest silent loss in the channel's history.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            legacy_dir = base / ".gzkit" / "handoffs"
            legacy_dir.mkdir(parents=True)
            legacy = legacy_dir / "20260101T000000Z-legacy.md"
            legacy.write_text(
                "---\n"
                "mode: CREATE\n"
                "adr_id: null\n"
                "branch: main\n"
                "timestamp: '2026-01-01T00:00:00Z'\n"
                "agent: claude-code\n"
                "---\n\n"
                "## Settled Rulings\n\n"
                "- A ruling only the legacy body knows.\n",
                encoding="utf-8",
            )
            create_handoff(
                branch="main",
                agent="claude-code",
                slug="successor",
                sections=_sections(),
                continues_from=legacy.name,
                base_path=base,
            )
            self.assertIn("A ruling only the legacy body knows.", read_rulings(base))

    def test_resume_reports_the_store_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            record_rulings(["Ruling from the store."], base_path=base, source="seed")
            create_handoff(
                branch="main",
                agent="claude-code",
                slug="resumed",
                sections=_sections(),
                base_path=base,
            )
            result = resume_handoff(base_path=base, now="2026-08-22T14:00:00Z")
            self.assertIn("Ruling from the store.", result.settled)

    def test_pointer_section_is_not_parsed_back_as_a_ruling(self) -> None:
        """The pointer is prose about the corpus, never an entry in it.

        A pointer that round-tripped into the store would book a ruling that no
        operator ever gave — fabrication through a parsing accident.
        """
        with tempfile.TemporaryDirectory() as tmp:
            base = _project(Path(tmp))
            record_rulings(["Genuine ruling."], base_path=base, source="seed")
            first = create_handoff(
                branch="main",
                agent="claude-code",
                slug="first",
                sections=_sections(),
                base_path=base,
            )
            create_handoff(
                branch="main",
                agent="claude-code",
                slug="second",
                sections=_sections(),
                continues_from=first.name,
                base_path=base,
            )
            for entry in read_rulings(base):
                self.assertNotIn(RULINGS_FILENAME, entry)
                self.assertNotIn("rulings booked", entry)

    def test_document_shrinks_by_the_size_of_the_corpus(self) -> None:
        """The measured claim of GHI #838, asserted as a property.

        A large corpus and a small one must produce handoffs of near-identical
        size, because the corpus is no longer part of the document.
        """
        with tempfile.TemporaryDirectory() as tmp:
            small_base = _project(Path(tmp) / "small")
            large_base = _project(Path(tmp) / "large")
            record_rulings(["Only ruling."], base_path=small_base, source="seed")
            record_rulings(
                [f"Ruling number {n} with enough text to matter." for n in range(500)],
                base_path=large_base,
                source="seed",
            )
            small = _chained(small_base)
            large = _chained(large_base)
            small_size = len(small.read_text(encoding="utf-8"))
            large_size = len(large.read_text(encoding="utf-8"))
            self.assertLess(
                large_size - small_size,
                200,
                "a 500-ruling corpus must not make the document meaningfully larger "
                "than a 1-ruling corpus; only the rendered count differs",
            )

    def test_settled_rulings_parser_survives_for_legacy_documents(self) -> None:
        """``settled_rulings`` keeps reading prose — 297+ authored documents hold it."""
        legacy = "## Settled Rulings\n\n- One.\n- Two.\n"
        self.assertEqual(settled_rulings(legacy), ["One.", "Two."])


if __name__ == "__main__":
    unittest.main()
