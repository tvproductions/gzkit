"""Section-ownership declaration tests — OBPI-0.35.0-04 Task 1 (plan steps 1-3).

REQ-derived (ADR-0.35.0 § Decision item 4): a section declaration whose value
is outside the closed {corpus-owned, unowned} enum, or a surface section with
no declaration at all, fails closed naming the offending section id
(REQ-0.35.0-04-01). Ownership keys on the stable kebab-case section id, never
the heading title (REQ-0.35.0-04-06).
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from typing import get_args
from unittest import mock

import jsonschema
from pydantic import ValidationError

from gzkit.content.models.corpus import Corpus, CorpusEntry, effective_corpus
from gzkit.content.ownership import (
    _OWNERSHIP_VALUES,
    OwnershipDeclaration,
    OwnershipLoadError,
    RatchetRefusedError,
    _Ownership,
    compute_baseline,
    declaration_path,
    load_declaration,
    measure_section_spans,
    record_unowned_total,
)
from gzkit.content.parse import section_id
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.traceability import covers

_CORPUS_PATH = Path(__file__).resolve().parents[2] / ".gzkit" / "corpus" / "AGENTS.md.jsonl"

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "gzkit" / "schemas" / "section_ownership.json"
)
_AGENTS_MD_PATH = Path(__file__).resolve().parents[2] / "AGENTS.md"

_SIMPLE_SURFACE = (
    "# Doc Title\n"
    "preamble text under the H1\n"
    "## Alpha Section\n"
    "alpha body line one\n"
    "alpha body line two\n"
    "## Beta Section\n"
    "beta body\n"
)


class _DeclarationFixtureMixin:
    """Shared temp-dir + declaration-writer setup for load_declaration tests."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)

    def _write_declaration(
        self,
        sections: dict[str, str],
        *,
        surface_text: str = _SIMPLE_SURFACE,
        unowned_byte_floor: int | None = None,
        floor_event_id: str | None = None,
    ) -> Path:
        # A genesis declaration (floor_event_id=None) is only load-bearing
        # valid when its floor equals the summed span of its own
        # declared-'unowned' sections (REQ-0.35.0-04-02) -- derive that sum
        # here, never hardcode a floor, so this fixture stays genesis-coherent
        # by construction for every caller that doesn't override it.
        if unowned_byte_floor is None:
            spans = measure_section_spans(surface_text)
            unowned_byte_floor = sum(
                span for sid, span in spans.items() if sections.get(sid) == "unowned"
            )
        path = self._root / "declaration.json"
        path.write_text(
            json.dumps(
                {
                    "surface": "Doc.md",
                    "sections": sections,
                    "unowned_byte_floor": unowned_byte_floor,
                    "measured_at": "2026-09-02T00:00:00Z",
                    "floor_event_id": floor_event_id,
                }
            ),
            encoding="utf-8",
        )
        return path


class TestMeasureSectionSpans(unittest.TestCase):
    """REQ-0.35.0-04-06 substrate: span-based measurement over H1/H2 headings."""

    def test_spans_sum_to_the_surface_byte_length(self) -> None:
        # The Shape contract is explicit: spans MUST sum to the file's byte
        # length. Use a body with a multi-byte character so a naive
        # character-count implementation (rather than byte-encoded) would
        # under-count and fail this assertion.
        surface_text = "# Title\ncafé body\n## Section Two\nmore\n"
        spans = measure_section_spans(surface_text)
        self.assertEqual(sum(spans.values()), len(surface_text.encode("utf-8")))

    def test_spans_sum_to_full_agents_md_byte_length(self) -> None:
        # Regression grounded in the brief's measured ground truth
        # (2026-09-02): 22 H1/H2 sections, 46,876 B total. The byte-sum
        # assertion is content-independent and stays exact. The section-count
        # assertion is deliberately NOT hardcoded to 22 -- AGENTS.md is edited
        # by this repo's ongoing diet chores, so a hardcoded count would break
        # on an unrelated heading edit with no relation to
        # measure_section_spans' correctness. Instead re-derive the expected
        # count independently, from the same H1/H2-prefix rule
        # measure_section_spans applies, and assert the two counts agree.
        surface_text = _AGENTS_MD_PATH.read_text(encoding="utf-8")
        spans = measure_section_spans(surface_text)
        self.assertEqual(sum(spans.values()), len(surface_text.encode("utf-8")))
        independent_ids: set[str] = set()
        for raw_line in surface_text.splitlines(keepends=True):
            line = raw_line.rstrip("\r\n")
            if line.startswith("## "):
                independent_ids.add(section_id(line[3:].strip()))
            elif line.startswith("# "):
                independent_ids.add(section_id(line[2:].strip()))
        self.assertEqual(len(spans), len(independent_ids))

    def test_keys_by_section_id_not_by_heading_offset_position(self) -> None:
        spans = measure_section_spans(_SIMPLE_SURFACE)
        self.assertIn("doc-title", spans)
        self.assertIn("alpha-section", spans)
        self.assertIn("beta-section", spans)

    def test_h3_headings_do_not_open_a_new_span(self) -> None:
        surface_text = "# Title\n## Section\nbody\n### Not A Boundary\nmore body\n"
        spans = measure_section_spans(surface_text)
        # Only the H1 and the H2 open spans; the H3 line stays inside "section".
        self.assertEqual(set(spans), {"title", "section"})
        self.assertEqual(sum(spans.values()), len(surface_text.encode("utf-8")))

    @covers("REQ-0.35.0-04-01")
    def test_two_distinct_headings_colliding_on_the_same_id_fail_closed(self) -> None:
        # "Alpha Beta" and "Alpha, Beta!" both slugify to "alpha-beta". Silently
        # summing their spans under one id hides the second heading behind the
        # first's declaration entry -- the undeclared-section check never fires
        # for it, and un-owning the id would mis-feed the ratchet by both
        # sections' bytes. This must fail closed instead of silently summing.
        surface_text = "# Alpha Beta\nbody one\n\n## Alpha, Beta!\nbody two\n"
        with self.assertRaises(OwnershipLoadError) as ctx:
            measure_section_spans(surface_text)
        message = str(ctx.exception)
        # What failed: both offending heading titles and the shared id are named.
        self.assertIn("Alpha Beta", message)
        self.assertIn("Alpha, Beta!", message)
        self.assertIn("alpha-beta", message)
        # Why forbidden: the governing REQ is cited.
        self.assertIn("REQ-0.35.0-04-01", message)

    @covers("REQ-0.35.0-04-01")
    def test_two_identical_headings_colliding_on_the_same_id_fail_closed(self) -> None:
        # Two physically separate "## Related" headings both slugify to
        # "related" -- identical titles are the same class of collision as
        # distinct titles that collide (both hide the second heading's bytes
        # behind the first's declaration entry). The title comparison is not
        # the discriminator; a second boundary resolving to a seen id is.
        surface_text = "# Doc Title\n## Related\nbody one\n## Related\nbody two\n"
        with self.assertRaises(OwnershipLoadError) as ctx:
            measure_section_spans(surface_text)
        message = str(ctx.exception)
        # What failed: the repeated title and the shared id are named.
        self.assertIn("Related", message)
        self.assertIn("related", message)
        # Why forbidden: the governing REQ is cited.
        self.assertIn("REQ-0.35.0-04-01", message)


class TestLoadDeclarationFailClosed(_DeclarationFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-04-01: no undeclared third state; every failure names the section id."""

    @covers("REQ-0.35.0-04-01")
    def test_value_outside_closed_enum_fails_closed_naming_the_section(self) -> None:
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "sort-of-owned",
                "beta-section": "unowned",
            }
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        # What failed: the offending id and its bogus value are named.
        self.assertIn("alpha-section", message)
        self.assertIn("sort-of-owned", message)
        # Why forbidden: the governing REQ is cited, not just "invalid value".
        self.assertIn("REQ-0.35.0-04-01", message)
        # Governed next step: an actionable recovery, not "see docs".
        self.assertTrue(
            "corpus-owned" in message and "unowned" in message,
            "recovery prose must name the two legal enum values",
        )

    @covers("REQ-0.35.0-04-01")
    def test_measured_section_with_no_declaration_fails_closed(self) -> None:
        path = self._write_declaration(
            {"doc-title": "corpus-owned", "alpha-section": "unowned"}
            # beta-section is present in the surface but undeclared.
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("beta-section", message)
        self.assertIn("REQ-0.35.0-04-01", message)

    def test_declared_section_absent_from_surface_fails_closed(self) -> None:
        # Cross-check direction not literally quoted in REQ-01's Given clause
        # but required by this task's Shape contract: a stale declaration
        # pointing at a section the surface no longer carries is itself
        # unresolvable and must fail closed, naming the orphaned id.
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
                "gamma-section": "unowned",
            }
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("gamma-section", message)

    @covers("REQ-0.35.0-04-01")
    def test_sections_field_that_is_not_an_object_fails_closed(self) -> None:
        # A "sections" value that is not an object (e.g. a JSON array) cannot
        # be cross-checked against the surface at all -- this must fail
        # closed with the same three-part recovery prose as every other
        # branch, not raise an unhandled TypeError/AttributeError.
        path = self._root / "declaration.json"
        path.write_text(
            json.dumps(
                {
                    "surface": "Doc.md",
                    "sections": ["doc-title", "alpha-section", "beta-section"],
                    "unowned_byte_floor": 0,
                    "measured_at": "2026-09-02T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        # What failed: the path and the non-object value are named.
        self.assertIn(path.as_posix(), message)
        self.assertIn("sections", message)
        # Why forbidden: the governing REQ is cited.
        self.assertIn("REQ-0.35.0-04-01", message)
        # Governed next step: the actionable recovery shape is named.
        self.assertIn("object", message)

    def test_fully_declared_surface_loads_cleanly(self) -> None:
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            }
        )
        declaration = load_declaration(path, _SIMPLE_SURFACE, self._root)
        self.assertIsInstance(declaration, OwnershipDeclaration)
        self.assertEqual(declaration.sections["doc-title"], "corpus-owned")


class TestOwnershipKeysOnSectionId(_DeclarationFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-04-06: ownership keys on the id, never the heading title."""

    @covers("REQ-0.35.0-04-06")
    def test_declaration_still_resolves_when_heading_text_changes_but_id_does_not(
        self,
    ) -> None:
        # "Behavior Rules" and "Behavior, RULES!!" collapse to the same
        # kebab-case id (behavior-rules) via the canonical slugifier -- a
        # renamed heading whose id survives must not orphan its declaration.
        renamed_surface = "# Doc Title\npreamble\n## Behavior, RULES!!\nrenamed body\n"
        path = self._write_declaration(
            {"doc-title": "corpus-owned", "behavior-rules": "unowned"},
            surface_text=renamed_surface,
        )
        declaration = load_declaration(path, renamed_surface, self._root)
        self.assertEqual(declaration.sections["behavior-rules"], "unowned")


class TestLoadDeclarationChainValidation(_DeclarationFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-04-02: an increase is only reachable through the attested
    raise-path. `gz content unown` is only the SUPPLIED raise path; nothing
    stopped a direct hand-edit of the declaration file from raising the
    floor with no attestation until `load_declaration` itself refuses to
    trust an unproven number. This is the Stage-2 fix cycle's regression
    coverage for that adversary finding.
    """

    def _seed_attested_declaration(self) -> Path:
        """A genuinely chain-valid declaration produced via the real
        raise-path primitive (`record_unowned_total`), never by hand-typing
        a `floor_event_id` -- the fixture must be as real as the attack it
        defends against. Starts genesis-coherent against `_SIMPLE_SURFACE`
        (floor = summed span of its declared-'unowned' sections), then
        records that SAME total through `record_unowned_total` (a
        decrease-or-equal call, never a raise) so the resulting declaration
        carries a real, ledger-resolvable `floor_event_id`.
        """
        spans = measure_section_spans(_SIMPLE_SURFACE)
        coherent_floor = spans["alpha-section"] + spans["beta-section"]
        genesis = OwnershipDeclaration(
            surface="Doc.md",
            sections={
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
            unowned_byte_floor=coherent_floor,
            measured_at="2026-09-02T00:00:00Z",
            floor_event_id=None,
        )
        path = declaration_path(self._root, genesis.surface)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(genesis.model_dump_json(indent=2) + "\n", encoding="utf-8")
        record_unowned_total(self._root, genesis, coherent_floor)
        return path

    @covers("REQ-0.35.0-04-02")
    def test_genesis_declaration_with_coherent_floor_loads_cleanly(self) -> None:
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            }
        )
        declaration = load_declaration(path, _SIMPLE_SURFACE, self._root)
        self.assertIsNone(declaration.floor_event_id)

    @covers("REQ-0.35.0-04-02")
    def test_direct_hand_edit_of_the_floor_fails_closed_the_adversary_attack(self) -> None:
        # The adversary's exact probe: seed an attested declaration, hand-edit
        # its floor upward by one byte with no matching new attested
        # transition, and reload -- this must be REFUSED, never silently
        # returned as `{"unattested_direct_raise_reloaded": <n>}`. The finding
        # this closes: `gz content unown` was only the SUPPLIED raise path,
        # not the ONLY one.
        path = self._seed_attested_declaration()
        before = load_declaration(path, _SIMPLE_SURFACE, self._root)
        self.assertIsNotNone(before.floor_event_id, "fixture must carry a real attested chain")

        raw = json.loads(path.read_text(encoding="utf-8"))
        raised_floor = raw["unowned_byte_floor"] + 1
        raw["unowned_byte_floor"] = raised_floor
        path.write_text(json.dumps(raw), encoding="utf-8")

        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn(str(raised_floor), message)

    @covers("REQ-0.35.0-04-02")
    def test_hand_edited_floor_with_nulled_event_id_still_fails_closed(self) -> None:
        # Closing the loophole the chain check alone would leave open: an
        # attacker who hand-raises the floor AND nulls floor_event_id must
        # still be caught, this time by genesis coherence -- a null-id
        # declaration proves itself only by the summed-span rule, and a
        # hand-raised floor disagrees with that sum too.
        path = self._seed_attested_declaration()
        raw = json.loads(path.read_text(encoding="utf-8"))
        raw["unowned_byte_floor"] = raw["unowned_byte_floor"] + 1
        raw["floor_event_id"] = None
        path.write_text(json.dumps(raw), encoding="utf-8")

        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        self.assertIn("REQ-0.35.0-04-02", str(ctx.exception))

    @covers("REQ-0.35.0-04-02")
    def test_floor_event_id_naming_a_nonexistent_event_fails_closed(self) -> None:
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
            floor_event_id="does-not-exist-in-the-ledger",
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("does-not-exist-in-the-ledger", message)

    @covers("REQ-0.35.0-04-02")
    def test_floor_event_id_naming_an_event_with_a_disagreeing_floor_fails_closed(self) -> None:
        ledger = Ledger(self._root / ".gzkit" / "ledger.jsonl")
        ledger.append(
            LedgerEvent(
                event="unowned_ratchet_updated",
                id="unowned-ratchet-updated-Doc.md-mismatch",
                extra={
                    "surface": "Doc.md",
                    "prior_unowned_byte_floor": 0,
                    "new_unowned_byte_floor": 999,
                },
            )
        )
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
            unowned_byte_floor=83,
            floor_event_id="unowned-ratchet-updated-Doc.md-mismatch",
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("999", message)


class TestOwnershipDeclarationModel(unittest.TestCase):
    """The Pydantic model mirrors the schema's closed enum and required shape."""

    def test_extra_field_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            OwnershipDeclaration(
                surface="Doc.md",
                sections={"doc-title": "corpus-owned"},
                unowned_byte_floor=0,
                measured_at="2026-09-02T00:00:00Z",
                floor_event_id=None,
                bogus_extra="nope",
            )

    def test_negative_floor_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            OwnershipDeclaration(
                surface="Doc.md",
                sections={"doc-title": "corpus-owned"},
                unowned_byte_floor=-1,
                measured_at="2026-09-02T00:00:00Z",
                floor_event_id=None,
            )

    def test_section_value_outside_enum_is_rejected_at_construction(self) -> None:
        with self.assertRaises(ValidationError):
            OwnershipDeclaration(
                surface="Doc.md",
                sections={"doc-title": "bogus-value"},
                unowned_byte_floor=0,
                measured_at="2026-09-02T00:00:00Z",
                floor_event_id=None,
            )


class TestSectionOwnershipSchema(unittest.TestCase):
    """The JSON schema mirrors the Pydantic model's closed shape."""

    def test_schema_accepts_a_conformant_declaration(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        instance = {
            "surface": "AGENTS.md",
            "sections": {"attestation": "corpus-owned", "skills": "unowned"},
            "unowned_byte_floor": 8637,
            "measured_at": "2026-09-02T00:00:00Z",
            "floor_event_id": None,
        }
        jsonschema.validate(instance, schema)

    def test_schema_rejects_a_value_outside_the_closed_enum(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        instance = {
            "surface": "AGENTS.md",
            "sections": {"attestation": "half-owned"},
            "unowned_byte_floor": 0,
            "measured_at": "2026-09-02T00:00:00Z",
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)

    def test_schema_rejects_an_extra_top_level_property(self) -> None:
        # Mirrors the Pydantic model's extra="forbid" -- the schema-side
        # equivalent of the same closed-shape contract had no negative test.
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        instance = {
            "surface": "AGENTS.md",
            "sections": {"attestation": "corpus-owned"},
            "unowned_byte_floor": 0,
            "measured_at": "2026-09-02T00:00:00Z",
            "bogus_extra": "nope",
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)

    def test_schema_rejects_a_negative_unowned_byte_floor(self) -> None:
        # Mirrors the Pydantic model's Field(ge=0) -- the schema-side
        # equivalent of the same non-negative-floor contract had no negative
        # test.
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        instance = {
            "surface": "AGENTS.md",
            "sections": {"attestation": "corpus-owned"},
            "unowned_byte_floor": -1,
            "measured_at": "2026-09-02T00:00:00Z",
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)


class TestOwnershipEnumSingleSourced(unittest.TestCase):
    """The closed ownership enum has three hand-authored copies; pin them equal.

    `section_ownership.json`'s `sections.additionalProperties.enum`, the
    `_Ownership = Literal[...]` type, and `_OWNERSHIP_VALUES` frozenset are
    three independently hand-authored copies of the same closed set with
    nothing asserting they stay equal -- an edit to one that misses the
    others is a silent drift no test catches until a value slips through one
    copy but not another.
    """

    def test_schema_literal_and_frozenset_all_agree(self) -> None:
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        schema_enum = set(schema["properties"]["sections"]["additionalProperties"]["enum"])
        literal_values = set(get_args(_Ownership))
        self.assertEqual(schema_enum, literal_values)
        self.assertEqual(schema_enum, _OWNERSHIP_VALUES)
        self.assertEqual(literal_values, _OWNERSHIP_VALUES)


class TestRecordUnownedTotalRatchet(unittest.TestCase):
    """REQ-0.35.0-04-02/-03: the unowned-byte ratchet is decrease-or-equal only.

    A declaration genuinely exists ON DISK before every test runs -- REQ-03's
    claim ("the floor is updated") is a claim about durable state, and a
    fixture that only builds an in-memory `OwnershipDeclaration` cannot prove
    or disprove it (the defect this rewrite exists to catch).
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)
        self._ledger_path = self._root / ".gzkit" / "ledger.jsonl"
        self._declaration = OwnershipDeclaration(
            surface="Doc.md",
            sections={"doc-title": "corpus-owned", "alpha-section": "unowned"},
            unowned_byte_floor=100,
            measured_at="2026-09-02T00:00:00Z",
            # record_unowned_total mints its OWN floor_event_id per call; this
            # fixture declaration's seed value is never read as a chain proof
            # by record_unowned_total itself (only load_declaration validates
            # the chain), so an arbitrary prior id is fine here.
            floor_event_id="seed-unowned-ratchet-updated-0",
        )
        self._declaration_path = declaration_path(self._root, self._declaration.surface)
        self._declaration_path.parent.mkdir(parents=True, exist_ok=True)
        self._declaration_path.write_text(
            self._declaration.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )

    @covers("REQ-0.35.0-04-02")
    def test_a_total_greater_than_the_floor_is_refused_and_nothing_is_persisted(self) -> None:
        declaration_bytes_before = self._declaration_path.read_bytes()
        with self.assertRaises(RatchetRefusedError) as ctx:
            record_unowned_total(self._root, self._declaration, 101)
        message = str(ctx.exception)
        # What failed / why forbidden: the REQ and the offending total are named.
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("101", message)
        # Governed next step: the attested raise-path is named, not "see docs".
        self.assertIn("gz content unown", message)
        # Prove the absence, not merely that an exception path was taken: the
        # ledger file was never even created, and the input declaration's
        # floor -- the only thing "stored" at this layer -- is untouched
        # (OwnershipDeclaration is frozen, so this also proves no mutation).
        self.assertFalse(self._ledger_path.exists())
        self.assertEqual(self._declaration.unowned_byte_floor, 100)
        # The necessary-but-not-sufficient in-memory assertion above could not
        # have caught the durable-state defect this rewrite fixes: assert the
        # on-disk declaration is BYTE-UNCHANGED, not merely "a refusal path
        # was taken".
        self.assertEqual(self._declaration_path.read_bytes(), declaration_bytes_before)

    @covers("REQ-0.35.0-04-03")
    def test_a_total_less_than_or_equal_to_the_floor_updates_it_and_emits_a_ratchet_event(
        self,
    ) -> None:
        # "or equal" (REQ-0.35.0-04-03): equality updates, it is decrease-or-equal,
        # not strictly-decrease. Exercise equality first, then a genuine decrease.
        for total in (100, 40):
            with self.subTest(total=total):
                updated = record_unowned_total(self._root, self._declaration, total)
                self.assertEqual(updated.unowned_byte_floor, total)
                # The input declaration is frozen and unaffected by the call.
                self.assertEqual(self._declaration.unowned_byte_floor, 100)
                # The claim under test is about DURABLE state: read the floor
                # back from disk, not from the returned in-memory object.
                persisted = json.loads(self._declaration_path.read_text(encoding="utf-8"))
                self.assertEqual(persisted["unowned_byte_floor"], total)

        raw_lines = [
            line
            for line in self._ledger_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        events = [json.loads(line) for line in raw_lines]
        self.assertEqual(len(events), 2)
        first, second = events
        self.assertEqual(first["event"], "unowned_ratchet_updated")
        self.assertEqual(first["surface"], "Doc.md")
        self.assertEqual(first["prior_unowned_byte_floor"], 100)
        self.assertEqual(first["new_unowned_byte_floor"], 100)
        self.assertEqual(second["prior_unowned_byte_floor"], 100)
        self.assertEqual(second["new_unowned_byte_floor"], 40)

    @covers("REQ-0.35.0-04-03")
    def test_a_failed_declaration_write_never_outlives_its_witness(self) -> None:
        # A witness (the ledger event) must never outlive the state it
        # witnesses. Induce a failure on the declaration write and prove no
        # ledger event was emitted -- Layer-2 may never announce a floor that
        # Layer-1 does not durably carry, even under a mid-operation fault.
        with (
            mock.patch.object(Path, "write_text", side_effect=OSError("disk full")),
            self.assertRaises(OSError),
        ):
            record_unowned_total(self._root, self._declaration, 40)
        self.assertFalse(self._ledger_path.exists())


class TestComputeBaseline(unittest.TestCase):
    """REQ-0.35.0-04-07/-08: the baseline is derived at call time, never stored."""

    @covers("REQ-0.35.0-04-07")
    def test_baseline_against_real_agents_md_matches_independently_rederived_figures(
        self,
    ) -> None:
        surface_text = _AGENTS_MD_PATH.read_text(encoding="utf-8")
        corpus = Corpus.loads(_CORPUS_PATH.read_text(encoding="utf-8"))
        baseline = compute_baseline(surface_text, corpus)

        # Independently re-derive expected figures from the SAME primitives
        # compute_baseline is built on (measure_section_spans + the corpus's
        # own tombstone-folded liveness), rather than hardcoding literals
        # copied from a prior run -- a hardcoded 8637/38239 would pass even
        # if compute_baseline silently stopped deriving them.
        spans = measure_section_spans(surface_text)
        live_sections: dict[str, int] = {}
        for entry in effective_corpus(corpus).entries:
            if entry.section in spans:
                live_sections[entry.section] = live_sections.get(entry.section, 0) + 1
        expected_owned_ids = set(live_sections)
        expected_total_span = sum(spans.values())
        expected_unowned_span = sum(
            span for sid, span in spans.items() if sid not in expected_owned_ids
        )
        expected_owned_span = expected_total_span - expected_unowned_span

        self.assertEqual(baseline.total_section_count, len(spans))
        self.assertEqual(baseline.owned_section_count, len(expected_owned_ids))
        self.assertEqual(baseline.total_byte_span, expected_total_span)
        self.assertEqual(baseline.unowned_byte_span, expected_unowned_span)
        self.assertEqual(baseline.entry_count_by_section, live_sections)
        self.assertAlmostEqual(
            baseline.coverage_pct,
            expected_owned_span / expected_total_span * 100,
            places=9,
        )

        # No literal-figure pin here (REQ-0.35.0-04-07: "derived by
        # measurement, never by a stored constant"). A pinned snapshot of
        # 2026-09-02's totals would false-fail on the next legitimate
        # AGENTS.md edit unrelated to compute_baseline's correctness, and
        # the rote recovery -- pasting in whatever the function now prints
        # -- verifies nothing; it can silently launder a genuine coverage
        # regression as the new "expected" constant. The independent
        # re-derivation above is the REQ-07 proof: it fails if
        # compute_baseline's arithmetic diverges from the primitives it is
        # built on, regardless of what AGENTS.md currently contains.

        # REQ-0.35.0-04-08: the honesty companion -- the per-section
        # histogram must surface thin coverage, not just a bare percentage.
        # A named-section equality check here would be tautological: the
        # full-dict equality on line 473 (baseline.entry_count_by_section ==
        # live_sections) already forces any singleton subset of one to equal
        # the singleton subset of the other, so re-asserting that equality
        # proves nothing further about compute_baseline. The one honest
        # claim left to make against the real fixture is that the histogram
        # actually identifies at least one thin (single-entry) section --
        # i.e. that REQ-08's feature has a non-trivial instance today, not a
        # degenerate always-empty one.
        singleton_sections = {
            sid for sid, count in baseline.entry_count_by_section.items() if count == 1
        }
        self.assertTrue(
            singleton_sections,
            "fixture drift: AGENTS.md/corpus no longer has any "
            "single-entry owned section -- pick a real REQ-08 fixture",
        )

    def test_baseline_is_recomputed_when_the_corpus_changes_not_read_from_a_constant(
        self,
    ) -> None:
        surface_text = _SIMPLE_SURFACE
        empty_corpus = Corpus()
        empty_baseline = compute_baseline(surface_text, empty_corpus)
        self.assertEqual(empty_baseline.owned_section_count, 0)
        self.assertEqual(empty_baseline.unowned_byte_span, empty_baseline.total_byte_span)
        self.assertEqual(empty_baseline.entry_count_by_section, {})

        addressed_corpus = Corpus().append(
            CorpusEntry(
                id="doc-title-1",
                surface="Doc.md",
                section="doc-title",
                tier="invariant",
                classification="Mechanical",
                text="preamble text under the H1",
                origin="test",
                ts="2026-09-02T00:00:00Z",
            )
        )
        addressed_baseline = compute_baseline(surface_text, addressed_corpus)
        self.assertEqual(addressed_baseline.owned_section_count, 1)
        self.assertEqual(addressed_baseline.entry_count_by_section, {"doc-title": 1})
        self.assertLess(addressed_baseline.unowned_byte_span, empty_baseline.unowned_byte_span)


if __name__ == "__main__":
    unittest.main()
