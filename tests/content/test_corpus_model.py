"""Append-only corpus model tests — OBPI-0.0.37-18.

REQ-derived (ADR-0.0.37 § Decision Re-Alignment part 1): the corpus is the
append-only source of truth; entries are addressed/provenanced; sections resolve
against the AgentContract/Pillar substrate; a JSON Schema mirrors the entry.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema
from pydantic import ValidationError

from gzkit.content.models import AgentContract, Corpus, CorpusEntry, Pillar
from gzkit.traceability import covers

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "gzkit" / "schemas" / "corpus_entry.json"
)


def _entry(**overrides: object) -> CorpusEntry:
    """Build a conformant CorpusEntry; override any field for negative cases."""
    base: dict[str, object] = {
        "id": "c1",
        "surface": "AGENTS.md",
        "section": "prime-directive",
        "tier": "invariant",
        "classification": "Mechanical",
        "text": "YOU OWN THE WORK COMPLETELY.",
        "origin": "GHI#519",
        "ts": "2026-06-05T00:00:00Z",
    }
    base.update(overrides)
    return CorpusEntry(**base)  # type: ignore[arg-type]


def _contract() -> AgentContract:
    """A minimal AgentContract whose only Pillar id is 'prime-directive'."""
    return AgentContract(
        name="Test",
        purpose="conformance fixture",
        pillars=[Pillar(id="prime-directive", title="Prime Directive", order=1)],
    )


class TestCorpusEntryModel(unittest.TestCase):
    """REQ-0.0.37-18-01: frozen, extra=forbid, exactly the ten addressed fields."""

    @covers("REQ-0.0.37-18-01")
    def test_carries_the_ten_addressed_fields(self) -> None:
        """All ten ADR-named fields are present and carry the constructed values."""
        e = _entry(anchor="a1", witness="gz validate --foo")
        self.assertEqual(
            (
                e.id,
                e.surface,
                e.section,
                e.anchor,
                e.tier,
                e.classification,
                e.witness,
                e.text,
                e.origin,
                e.ts,
            ),
            (
                "c1",
                "AGENTS.md",
                "prime-directive",
                "a1",
                "invariant",
                "Mechanical",
                "gz validate --foo",
                "YOU OWN THE WORK COMPLETELY.",
                "GHI#519",
                "2026-06-05T00:00:00Z",
            ),
        )

    @covers("REQ-0.0.37-18-01")
    def test_model_has_exactly_ten_fields(self) -> None:
        """The entry is exactly the ten ADR-named fields — no inherited 11th field."""
        self.assertEqual(
            set(CorpusEntry.model_fields),
            {
                "id",
                "surface",
                "section",
                "anchor",
                "tier",
                "classification",
                "witness",
                "text",
                "origin",
                "ts",
            },
        )

    @covers("REQ-0.0.37-18-01")
    def test_anchor_and_witness_are_optional(self) -> None:
        """anchor and witness default to None (the two optional address fields)."""
        e = _entry()
        self.assertIsNone(e.anchor)
        self.assertIsNone(e.witness)

    @covers("REQ-0.0.37-18-01")
    def test_frozen_rejects_mutation(self) -> None:
        """An entry is immutable — reassigning a field fails closed."""
        e = _entry()
        with self.assertRaises(ValidationError):
            e.text = "mutated"  # type: ignore[misc]

    @covers("REQ-0.0.37-18-01")
    def test_extra_field_forbidden(self) -> None:
        """extra='forbid' rejects an unknown field (typo defense)."""
        with self.assertRaises(ValidationError):
            _entry(unexpected="x")

    @covers("REQ-0.0.37-18-01")
    def test_out_of_enum_tier_rejected(self) -> None:
        """tier is constrained to the invariant|compressible enum."""
        with self.assertRaises(ValidationError):
            _entry(tier="ephemeral")


class TestCorpusAppendOnly(unittest.TestCase):
    """REQ-0.0.37-18-02: append-only aggregate with a JSONL round-trip."""

    @covers("REQ-0.0.37-18-02")
    def test_append_returns_new_corpus_and_leaves_original_unchanged(self) -> None:
        """append produces a NEW Corpus; the source corpus is not mutated."""
        c0 = Corpus()
        c1 = c0.append(_entry(id="a"))
        self.assertEqual(len(c0.entries), 0)
        self.assertEqual(len(c1.entries), 1)
        self.assertIsNot(c0, c1)

    @covers("REQ-0.0.37-18-02")
    def test_entries_is_an_immutable_tuple(self) -> None:
        """The entries collection is a tuple — no in-place append/remove possible."""
        c = Corpus().append(_entry())
        self.assertIsInstance(c.entries, tuple)

    @covers("REQ-0.0.37-18-02")
    def test_append_is_the_only_mutation_surface(self) -> None:
        """No edit/remove/delete/insert/pop/clear method exists — append-only contract."""
        forbidden = {"remove", "delete", "edit", "insert", "pop", "clear", "discard", "set"}
        self.assertEqual(forbidden & set(dir(Corpus)), set())

    @covers("REQ-0.0.37-18-02")
    def test_jsonl_round_trip_reconstructs_equal_corpus(self) -> None:
        """Corpus.loads(c.dumps()) == c — the lossless store round-trip."""
        c = (
            Corpus()
            .append(_entry(id="a"))
            .append(_entry(id="b", tier="compressible", classification="Promotable"))
        )
        self.assertEqual(Corpus.loads(c.dumps()), c)

    @covers("REQ-0.0.37-18-02")
    def test_dumps_is_one_json_object_per_line(self) -> None:
        """dumps emits JSONL — one standalone JSON object per entry, per line."""
        c = Corpus().append(_entry(id="a")).append(_entry(id="b"))
        lines = c.dumps().splitlines()
        self.assertEqual(len(lines), 2)
        for line in lines:
            json.loads(line)  # each line parses as a standalone JSON object


class TestCorpusSectionConformance(unittest.TestCase):
    """REQ-0.0.37-18-03: validate_against resolves each section to a Pillar.id."""

    @covers("REQ-0.0.37-18-03")
    def test_conformant_section_passes(self) -> None:
        """An entry whose section is a real Pillar id validates without raising."""
        c = Corpus().append(_entry(section="prime-directive"))
        c.validate_against(_contract())  # must not raise

    @covers("REQ-0.0.37-18-03")
    def test_section_resolving_to_no_pillar_raises(self) -> None:
        """An entry whose section is not a Pillar id fails closed."""
        c = Corpus().append(_entry(section="no-such-section"))
        with self.assertRaises(ValueError):
            c.validate_against(_contract())


class TestCorpusEntrySchemaMirror(unittest.TestCase):
    """REQ-0.0.37-18-04: corpus_entry.json mirrors CorpusEntry exactly."""

    def _schema(self) -> dict:
        return json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))

    @covers("REQ-0.0.37-18-04")
    def test_schema_accepts_conformant_entry(self) -> None:
        """The schema validates a fully-populated, conformant entry."""
        jsonschema.validate(_entry(anchor="a", witness="w").model_dump(), self._schema())

    @covers("REQ-0.0.37-18-04")
    def test_schema_rejects_unknown_property(self) -> None:
        """additionalProperties:false — an unknown property is rejected."""
        bad = _entry().model_dump()
        bad["unexpected"] = "x"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, self._schema())

    @covers("REQ-0.0.37-18-04")
    def test_schema_rejects_out_of_enum_tier(self) -> None:
        """The schema enforces the tier enum (invariant|compressible)."""
        bad = _entry().model_dump()
        bad["tier"] = "ephemeral"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, self._schema())

    @covers("REQ-0.0.37-18-04")
    def test_schema_property_set_matches_model_fields(self) -> None:
        """Schema↔model parity: the schema's property set equals the model's field set."""
        self.assertEqual(
            set(self._schema()["properties"]),
            set(CorpusEntry.model_fields),
        )


if __name__ == "__main__":
    unittest.main()
