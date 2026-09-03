"""Section-ownership declaration tests — OBPI-0.35.0-04 Task 1 (plan steps 1-3).

REQ-derived (ADR-0.35.0 § Decision item 4): a section declaration whose value
is outside the closed {corpus-owned, unowned} enum, or a surface section with
no declaration at all, fails closed naming the offending section id
(REQ-0.35.0-04-01). Ownership keys on the stable kebab-case section id, never
the heading title (REQ-0.35.0-04-06).
"""

from __future__ import annotations

import ast
import contextlib
import fcntl
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from typing import get_args
from unittest import mock

import jsonschema
from pydantic import ValidationError

from gzkit.content import ownership
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
    sections_digest,
    write_declaration_atomically,
)
from gzkit.content.parse import section_id
from gzkit.governance.events import emit_section_ownership_genesis
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.traceability import covers

_CORPUS_PATH = Path(__file__).resolve().parents[2] / ".gzkit" / "corpus" / "AGENTS.md.jsonl"

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "gzkit" / "schemas" / "section_ownership.json"
)
_AGENTS_MD_PATH = Path(__file__).resolve().parents[2] / "AGENTS.md"
_REPO_ROOT = Path(__file__).resolve().parents[2]
_AGENTS_MD_DECLARATION_PATH = _REPO_ROOT / ".gzkit" / "ownership" / "AGENTS.md.json"

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

    _DEFAULT_FIXTURE_SECTIONS = {
        "doc-title": "corpus-owned",
        "alpha-section": "unowned",
        "beta-section": "unowned",
    }

    def _seed_genesis_event(
        self, surface: str, floor: int, *, sections: dict[str, str] | None = None
    ) -> str:
        """Emit a real `section_ownership_genesis` event into this fixture's ledger.

        Returns the minted event id so a caller can point a declaration's
        `floor_event_id` at a genuinely ledger-resolvable proof rather than a
        hand-typed string -- the fixture must be as real as the attack it
        defends against.

        *sections* is the map the witness records. It defaults to the map this
        module's declarations use, so a caller testing a floor-side property need
        not restate it; a caller testing a MAP-side property passes its own, and
        an event whose digest disagrees with the declaration is exactly what the
        loader must refuse.
        """
        digest = sections_digest(self._DEFAULT_FIXTURE_SECTIONS if sections is None else sections)
        event_id = f"section-ownership-genesis-{surface}-{digest[:12]}"
        emit_section_ownership_genesis(self._root, event_id, surface, digest, floor)
        return event_id


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
        spans = measure_section_spans(_SIMPLE_SURFACE)
        floor = spans["alpha-section"] + spans["beta-section"]
        event_id = self._seed_genesis_event("Doc.md", floor)
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
            unowned_byte_floor=floor,
            floor_event_id=event_id,
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
        spans = measure_section_spans(renamed_surface)
        floor = spans["behavior-rules"]
        event_id = self._seed_genesis_event(
            "Doc.md",
            floor,
            sections={"doc-title": "corpus-owned", "behavior-rules": "unowned"},
        )
        path = self._write_declaration(
            {"doc-title": "corpus-owned", "behavior-rules": "unowned"},
            surface_text=renamed_surface,
            unowned_byte_floor=floor,
            floor_event_id=event_id,
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
    def test_null_floor_event_id_is_refused_the_genesis_branch_no_longer_exists(self) -> None:
        # The Step-4b adversary's exact probe: a null floor_event_id was
        # witnessed only by self-coherence (the stored floor equalling the
        # summed span of its own declared-'unowned' sections), which the
        # attacker simply recomputes after flipping a section. There is no
        # longer a genesis branch that trusts a null id at all -- EVERY
        # floor, day-one included, must resolve to a real ledger event.
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
            floor_event_id=None,
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("null", message)

    @covers("REQ-0.35.0-04-05")
    def test_an_ownership_flip_inside_ratchet_slack_is_refused(self) -> None:
        """Would break if the witness bound only the floor and not the map.

        Step-4b round-3 finding 2 (`[high]`). The span check is `<=` because the
        ratchet is decrease-only, so whenever the stored floor sits ABOVE the true
        summed span -- the legitimate state after a surface shrink -- that slack
        is room to move a section from `corpus-owned` to `unowned` with the
        arithmetic still satisfied. Measured before the fix: the flip loaded
        cleanly with the ledger holding one row before and one row after, so the
        coverage loss had no witness anywhere.

        The fixture carries EXACTLY one section's worth of slack, so the flipped
        map's summed span equals the stored floor and every scalar check still
        passes. Only the map digest can refuse it.
        """
        sections = {
            "doc-title": "corpus-owned",
            "alpha-section": "corpus-owned",
            "beta-section": "unowned",
        }
        spans = measure_section_spans(_SIMPLE_SURFACE)
        slack_floor = spans["beta-section"] + spans["alpha-section"]
        event_id = self._seed_genesis_event("Doc.md", slack_floor, sections=sections)

        baseline = self._write_declaration(
            sections, unowned_byte_floor=slack_floor, floor_event_id=event_id
        )
        self.assertEqual(
            load_declaration(baseline, _SIMPLE_SURFACE, self._root).sections["alpha-section"],
            "corpus-owned",
            "control: the unflipped declaration must load, or the refusal below proves nothing",
        )

        flipped = dict(sections)
        flipped["alpha-section"] = "unowned"
        path = self._write_declaration(
            flipped, unowned_byte_floor=slack_floor, floor_event_id=event_id
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("does not witness", message)
        self.assertIn("REQ-0.35.0-04-05", message)

    @covers("REQ-0.35.0-04-02")
    def test_a_decrease_only_event_may_not_witness_a_raise(self) -> None:
        """Would break if roster membership alone were treated as corroboration.

        Step-4b round-3 finding 1 (`[critical]`), reproducing the adversary's
        probe. `unowned_ratchet_updated` is the ORDINARY path and
        `record_unowned_total` refuses to emit it for an increase -- so a row of
        that type recording `prior=26, new=83` describes a move its own type
        cannot make. The loader checked only that the type was on the roster,
        the surface matched, and the floor value agreed, so the raise was
        ACCEPTED with no attestor, no reason, and no `gz content unown`.

        The assertion is on the DIRECTION prose, not merely on refusal: three
        other checks in this loader also refuse and cite the same REQ, so a bare
        "it raised" assertion would pass with this gate deleted.
        """
        ledger = Ledger(self._root / ".gzkit" / "ledger.jsonl")
        ledger.append(
            LedgerEvent(
                event="unowned_ratchet_updated",
                id="wrong-direction-event",
                extra={
                    "surface": "Doc.md",
                    "prior_unowned_byte_floor": 26,
                    "new_unowned_byte_floor": 83,
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
            floor_event_id="wrong-direction-event",
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("decrease-only", message)
        self.assertIn("26 -> 83", message)

    @covers("REQ-0.35.0-04-02")
    def test_a_raise_only_event_may_not_witness_a_decrease(self) -> None:
        """Would break if the direction gate checked only one of the two types.

        The mirror of the case above: `section_ownership_unowned` is the ATTESTED
        RAISE path, so a row of that type recording a decrease-or-equal move is
        equally self-contradictory. Testing only the raise direction would leave
        half the gate unwitnessed.
        """
        ledger = Ledger(self._root / ".gzkit" / "ledger.jsonl")
        ledger.append(
            LedgerEvent(
                event="section_ownership_unowned",
                id="backwards-raise-event",
                extra={
                    "surface": "Doc.md",
                    "section": "alpha-section",
                    "prior_unowned_byte_floor": 83,
                    "new_unowned_byte_floor": 26,
                    "attestor": "g0",
                    "reason": "probe",
                },
            )
        )
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "corpus-owned",
                "beta-section": "unowned",
            },
            unowned_byte_floor=26,
            floor_event_id="backwards-raise-event",
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("raise-only", message)

    @covers("REQ-0.35.0-04-02")
    def test_genesis_records_no_prior_floor_and_is_exempt_from_the_direction_gate(
        self,
    ) -> None:
        """Would break if the direction gate rejected a legitimate genesis load.

        `section_ownership_genesis` carries no `prior_unowned_byte_floor`, so it
        asserts no direction and must load cleanly. This is the negative control
        for the gate above: without it, a gate that refused every event lacking a
        prior floor would look identical to a correct one on the two tests above.
        """
        sections = {
            "doc-title": "corpus-owned",
            "alpha-section": "unowned",
            "beta-section": "unowned",
        }
        spans = measure_section_spans(_SIMPLE_SURFACE)
        floor = sum(span for sid, span in spans.items() if sections[sid] == "unowned")
        event_id = self._seed_genesis_event("Doc.md", floor)
        path = self._write_declaration(sections, unowned_byte_floor=floor, floor_event_id=event_id)
        declaration = load_declaration(path, _SIMPLE_SURFACE, self._root)
        self.assertEqual(declaration.floor_event_id, event_id)

    @covers("REQ-0.35.0-04-02")
    def test_floor_event_id_resolving_to_the_wrong_event_type_is_refused(self) -> None:
        # The adversary showed a `task_started` event accepted as proof --
        # ANY event type resolving to the right id used to pass. Only the
        # recognized ownership roster (section_ownership_genesis,
        # section_ownership_unowned, unowned_ratchet_updated) may witness a
        # floor, even when the floor VALUE happens to match.
        ledger = Ledger(self._root / ".gzkit" / "ledger.jsonl")
        ledger.append(
            LedgerEvent(
                event="task_started",
                id="wrong-type-event",
                extra={"surface": "Doc.md", "new_unowned_byte_floor": 83},
            )
        )
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
            unowned_byte_floor=83,
            floor_event_id="wrong-type-event",
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("task_started", message)

    @covers("REQ-0.35.0-04-02")
    def test_floor_event_id_resolving_to_a_different_surface_is_refused(self) -> None:
        # An event for "Other.md" accepted as proof for "Doc.md" used to pass
        # whenever the floor value happened to agree.
        ledger = Ledger(self._root / ".gzkit" / "ledger.jsonl")
        ledger.append(
            LedgerEvent(
                event="unowned_ratchet_updated",
                id="other-surface-event",
                extra={
                    "surface": "Other.md",
                    "prior_unowned_byte_floor": 0,
                    "new_unowned_byte_floor": 83,
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
            floor_event_id="other-surface-event",
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("Other.md", message)

    @covers("REQ-0.35.0-04-02")
    def test_unowned_span_exceeding_the_stored_floor_is_refused(self) -> None:
        # The reproduced attack: flip a corpus-owned section ('doc-title') to
        # 'unowned' WITHOUT touching the stored floor or its real, resolving
        # floor_event_id. The true unowned span now sits ABOVE the floor the
        # chain check alone would still accept.
        event_id = self._seed_genesis_event(
            "Doc.md",
            83,
            sections={
                "doc-title": "unowned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
        )
        path = self._write_declaration(
            {
                "doc-title": "unowned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
            unowned_byte_floor=83,
            floor_event_id=event_id,
        )
        with self.assertRaises(OwnershipLoadError) as ctx:
            load_declaration(path, _SIMPLE_SURFACE, self._root)
        message = str(ctx.exception)
        self.assertIn("REQ-0.35.0-04-02", message)
        self.assertIn("83", message)

    @covers("REQ-0.35.0-04-02")
    def test_unowned_span_below_the_stored_floor_loads_cleanly(self) -> None:
        # A legitimate AGENTS.md shrink before the next ratchet recording:
        # the true unowned span may sit BELOW the stored floor -- the ratchet
        # is decrease-only, so `<=` is the correct relation, never `==`.
        spans = measure_section_spans(_SIMPLE_SURFACE)
        true_span = spans["alpha-section"] + spans["beta-section"]
        stored_floor = true_span + 10
        event_id = self._seed_genesis_event("Doc.md", stored_floor)
        path = self._write_declaration(
            {
                "doc-title": "corpus-owned",
                "alpha-section": "unowned",
                "beta-section": "unowned",
            },
            unowned_byte_floor=stored_floor,
            floor_event_id=event_id,
        )
        declaration = load_declaration(path, _SIMPLE_SURFACE, self._root)
        self.assertEqual(declaration.unowned_byte_floor, stored_floor)

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
        # still be caught -- a null floor_event_id is refused outright now,
        # there is no genesis branch left for it to hide behind.
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
            "floor_event_id": "section-ownership-genesis-AGENTS.md-example",
        }
        jsonschema.validate(instance, schema)

    def test_schema_rejects_a_null_floor_event_id(self) -> None:
        # REQ-0.35.0-04-02: the genesis branch no longer exists -- a null
        # floor_event_id is refused at the schema level too, not merely by
        # the loader.
        schema = json.loads(_SCHEMA_PATH.read_text(encoding="utf-8"))
        instance = {
            "surface": "AGENTS.md",
            "sections": {"attestation": "corpus-owned", "skills": "unowned"},
            "unowned_byte_floor": 8637,
            "measured_at": "2026-09-02T00:00:00Z",
            "floor_event_id": None,
        }
        with self.assertRaises(jsonschema.ValidationError):
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


class TestCommittedDeclarationLoadsCleanly(unittest.TestCase):
    """REQ-0.35.0-04-08: the day-one declaration validates and loads for real.

    Not a scratch fixture -- the actual `.gzkit/ownership/AGENTS.md.json`
    against the actual `AGENTS.md` and the actual project root, so this
    would fail if the genesis event minted for the committed declaration
    were ever missing or repointed to the wrong id.
    """

    # No @covers here BY DESIGN. REQ-0.35.0-04-08 is a SUPPORT REQ, and its
    # proof channel is a path-citing ledger event plus a structural validator
    # (`gz validate --documents`), never a test decoration (ADR-0.0.59,
    # GHI #571). Decorating it would be the category error the brief's own
    # Acceptance Criteria warn against; the test is still valuable as a live
    # regression guard, it simply is not REQ-08's proof.
    def test_committed_agents_md_declaration_loads_against_the_real_ledger(self) -> None:
        surface_text = _AGENTS_MD_PATH.read_text(encoding="utf-8")
        declaration = load_declaration(_AGENTS_MD_DECLARATION_PATH, surface_text, _REPO_ROOT)
        self.assertIsNotNone(declaration.floor_event_id)
        self.assertEqual(declaration.surface, "AGENTS.md")


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
        #
        # The fault is injected at `os.replace` rather than at `Path.write_text`:
        # the declaration is now written atomically, so the rename is the ONLY
        # step that can make new contents visible and therefore the only place
        # a partial write could ever be observed. This is a real OS-level fault
        # inside the production write, not a stub of it -- so the assertion is
        # strictly stronger than the truncating-write version it replaces: no
        # witness, no torn file, and no staging left behind.
        before = self._declaration_path.read_bytes()
        real_replace = os.replace

        def refuse_declaration_replace(src, dst, *args, **kwargs):
            if Path(dst).name == "Doc.md.json":
                msg = "disk full"
                raise OSError(msg)
            return real_replace(src, dst, *args, **kwargs)

        with (
            mock.patch("os.replace", side_effect=refuse_declaration_replace),
            self.assertRaises(OSError),
        ):
            record_unowned_total(self._root, self._declaration, 40)

        self.assertFalse(self._ledger_path.exists())
        self.assertEqual(
            self._declaration_path.read_bytes(),
            before,
            "a failed declaration write must leave the file byte-unchanged, never torn",
        )
        residue = sorted(
            path.name
            for path in self._declaration_path.parent.iterdir()
            if path.name not in {"Doc.md.json", "Doc.md.json.lock"}
        )
        self.assertEqual(residue, [], f"a rolled-back write leaves no staging file: {residue}")


class TestRecordUnownedTotalRefusesAnOnDiskSurfaceMismatch(unittest.TestCase):
    """`_committed_state` fail-closes when the on-disk `surface` disagrees.

    Genuinely reachable in production: a case-insensitive filesystem resolves
    `declaration_path(root, "doc.md")` and `declaration_path(root, "Doc.md")`
    to the SAME file, so a caller holding one surface's declaration can open
    a file another surface actually wrote. The condition itself needs no
    case-insensitive filesystem to construct, though -- it is purely "the
    file at the resolved path names a different surface than the declaration
    in hand" -- so this test reproduces it directly by writing that file,
    which is portable across filesystems. Every sibling `OwnershipLoadError`
    branch in this module is covered; this one previously was not (Step-4b
    review, closure minor A).
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)
        self._declaration = OwnershipDeclaration(
            surface="Doc.md",
            sections={"doc-title": "corpus-owned"},
            unowned_byte_floor=100,
            measured_at="2026-09-02T00:00:00Z",
            floor_event_id="seed-unowned-ratchet-updated-0",
        )
        self._path = declaration_path(self._root, self._declaration.surface)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # The file living at Doc.md's resolved path actually names a
        # DIFFERENT surface -- the exact disagreement `_committed_state`
        # must refuse rather than overwrite.
        other_surface_declaration = self._declaration.model_copy(update={"surface": "Other.md"})
        self._path.write_text(
            other_surface_declaration.model_dump_json(indent=2) + "\n", encoding="utf-8"
        )

    @covers("REQ-0.35.0-04-02")
    def test_an_on_disk_surface_disagreement_fails_closed_and_never_writes(self) -> None:
        before = self._path.read_bytes()
        with self.assertRaises(OwnershipLoadError) as ctx:
            record_unowned_total(self._root, self._declaration, 40)

        message = str(ctx.exception)
        self.assertIn(str(self._path), message)
        self.assertIn("Other.md", message)
        self.assertIn("Doc.md", message)
        self.assertEqual(
            self._path.read_bytes(),
            before,
            "a surface-mismatched file must be left byte-unchanged, never "
            "overwritten with another surface's declaration",
        )


class TestRecordUnownedTotalIsTransactional(unittest.TestCase):
    """`record_unowned_total` writes the SAME file as the attested raise-path.

    A lock only serializes when EVERY writer takes it, and an event id nobody
    can reproduce makes an interrupted run unrecoverable rather than untidy --
    so these are properties of this writer, not of its sibling.
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name) / "a"
        self._declaration = OwnershipDeclaration(
            surface="Doc.md",
            sections={"doc-title": "corpus-owned", "alpha-section": "unowned"},
            unowned_byte_floor=100,
            measured_at="2026-09-02T00:00:00Z",
            floor_event_id="seed-unowned-ratchet-updated-0",
        )
        self._path = declaration_path(self._root, "Doc.md")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(self._declaration.model_dump_json(indent=2) + "\n", encoding="utf-8")

    @covers("REQ-0.35.0-04-02")
    def test_the_minted_event_id_is_reproducible_from_the_transitions_own_content(
        self,
    ) -> None:
        """Would break if the id embedded a wall-clock timestamp.

        The declaration is written before its ledger witness, so an interrupted
        run leaves a declaration naming an event the ledger lacks --
        `load_declaration` then fails closed forever. A retry can only complete
        that move if it mints the SAME id, which a `datetime.now()` id can
        never do.
        """
        other_root = Path(self._tempdir.name) / "b"
        first = record_unowned_total(self._root, self._declaration, 40)
        second = record_unowned_total(other_root, self._declaration, 40)
        self.assertEqual(
            first.floor_event_id,
            second.floor_event_id,
            "the same transition from the same predecessor must mint the same id",
        )

    @covers("REQ-0.35.0-04-02")
    def test_a_distinct_predecessor_mints_a_distinct_event_id(self) -> None:
        """Would break if the id were a bare content fingerprint.

        Two genuinely distinct recordings of the same total -- lower, restore,
        lower again -- start from different predecessors. A pure content hash
        would collide and silently drop the second witness, so the id must be a
        CHAIN LINK over the declaration's current `floor_event_id`.
        """
        from_seed = record_unowned_total(self._root, self._declaration, 40)
        successor = self._declaration.model_copy(
            update={"floor_event_id": from_seed.floor_event_id}
        )
        from_successor = record_unowned_total(Path(self._tempdir.name) / "c", successor, 40)
        self.assertNotEqual(from_seed.floor_event_id, from_successor.floor_event_id)

    @covers("REQ-0.35.0-04-02")
    def test_the_declaration_write_and_its_witness_both_happen_inside_the_lock(self) -> None:
        """Would break if this writer did not take the lock its sibling takes.

        A lock serializes only if EVERY writer takes it: a non-participating
        second writer reopens the lost-update race the attested raise-path just
        closed -- both readers see the pre-transition floor, the second clobbers
        the first, and one transition is discarded while its witness still
        claims it happened.

        Scoped deliberately to the two DURABLE WRITES: this test asserts their
        ORDER inside the lock. That the committed floor is re-read under the
        same lock -- the other half of the read-modify-write -- is asserted by
        `TestRecordUnownedTotalReadsTheFloorInsideTheLock`, which observes the
        outcome rather than the call order.
        """
        trace: list[str] = []
        real_lock = ownership.exclusive_declaration_lock
        real_write = ownership.write_declaration_atomically
        real_emit = ownership.emit_unowned_ratchet_updated

        @contextlib.contextmanager
        def traced_lock(path: Path):
            trace.append("lock-enter")
            with real_lock(path):
                yield
            trace.append("lock-exit")

        def traced_write(path: Path, text: str) -> None:
            trace.append("declaration-write")
            return real_write(path, text)

        def traced_emit(*args, **kwargs):
            trace.append("ledger-append")
            return real_emit(*args, **kwargs)

        with (
            mock.patch.object(ownership, "exclusive_declaration_lock", traced_lock),
            mock.patch.object(ownership, "write_declaration_atomically", traced_write),
            mock.patch.object(ownership, "emit_unowned_ratchet_updated", traced_emit),
        ):
            record_unowned_total(self._root, self._declaration, 40)

        self.assertEqual(
            trace,
            ["lock-enter", "declaration-write", "ledger-append", "lock-exit"],
            "both durable writes must be enclosed by the declaration lock",
        )


class TestComputeBaseline(unittest.TestCase):
    """REQ-0.35.0-04-07/-08: the baseline is derived at call time, never stored."""

    @covers("REQ-0.35.0-04-07")
    def test_baseline_arithmetic_is_self_consistent_against_the_real_surface_and_corpus(
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

    @covers("REQ-0.35.0-04-07")
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

    @covers("REQ-0.35.0-04-07")
    def test_baseline_deltas_a_known_perturbation_by_exactly_that_amount(self) -> None:
        """Differential control for REQ-0.35.0-04-07 (Step-4b adversary finding 5).

        The class's other covering test re-derives its expectation by
        re-executing `compute_baseline`'s own algorithm against the same
        primitives, so it only proves `compute_baseline` equals a copy of
        itself -- the adversary substituted a STORED DAY-ONE SNAPSHOT for
        live computation and that test class still passed whole.

        This control cannot be fooled that way: it PERTURBS the real surface
        and corpus by a quantity constructed independently of any
        `compute_baseline` primitive (a plain `len(text.encode("utf-8"))` on
        a string this test wrote, and one corpus entry this test constructed),
        and asserts every reported figure moves by EXACTLY that quantity. If
        `compute_baseline` returned a frozen snapshot instead of measuring
        live, EVERY delta asserted below would read zero -- that is the
        precise failure mode this control exists to catch, made explicit in
        the final block below.
        """
        surface_text = _AGENTS_MD_PATH.read_text(encoding="utf-8")
        corpus = Corpus.loads(_CORPUS_PATH.read_text(encoding="utf-8"))
        before = compute_baseline(surface_text, corpus)

        # --- Control 1: SURFACE perturbation --------------------------------
        # Append one synthetic H2 section, addressed by no corpus entry,
        # directly at the end of the document (no leading blank line: the
        # real AGENTS.md already ends with a newline, so the new heading
        # line starts EXACTLY at the old EOF offset). `measure_section_spans`
        # bounds the final section's span at EOF (see its own module
        # function docstring / the boundary loop above), so appending there cannot
        # change any EXISTING section's span -- only the new section's own
        # span, which runs from its heading to the new EOF, is added.
        appended_section = (
            "## REQ-04-07 Differential Control Probe Section\n"
            "Synthetic probe body addressed by no corpus entry.\n"
        )
        appended_byte_len = len(appended_section.encode("utf-8"))
        perturbed_surface_text = surface_text + appended_section
        probe_section_id = section_id("REQ-04-07 Differential Control Probe Section")
        self.assertNotIn(
            probe_section_id,
            measure_section_spans(surface_text),
            "fixture collision: pick a probe title whose section id does "
            "not already exist in AGENTS.md",
        )

        after_surface = compute_baseline(perturbed_surface_text, corpus)

        self.assertEqual(
            after_surface.total_section_count,
            before.total_section_count + 1,
            "appending one H2 section must increase the section count by "
            "exactly 1 -- a stored snapshot would report zero delta",
        )
        self.assertEqual(
            after_surface.total_byte_span,
            before.total_byte_span + appended_byte_len,
            "total_byte_span must grow by EXACTLY the bytes appended -- a "
            "stored snapshot would report zero delta here",
        )
        self.assertEqual(
            after_surface.unowned_byte_span,
            before.unowned_byte_span + appended_byte_len,
            "the new section is addressed by no corpus entry, so the "
            "entire appended span must land in unowned_byte_span",
        )
        self.assertEqual(
            after_surface.owned_section_count,
            before.owned_section_count,
            "the appended section is unowned, so owned_section_count must not move",
        )
        self.assertLess(
            after_surface.coverage_pct,
            before.coverage_pct,
            "adding unowned span against a fixed owned span must strictly decrease coverage_pct",
        )

        # --- Control 2: CORPUS perturbation ----------------------------------
        # Address one section that is currently unowned, WITHOUT touching the
        # surface text at all.
        spans = measure_section_spans(surface_text)
        unowned_section_ids = sorted(set(spans) - set(before.entry_count_by_section))
        self.assertTrue(
            unowned_section_ids,
            "fixture drift: AGENTS.md/corpus no longer has any unowned "
            "section to address -- pick a different REQ-07 fixture",
        )
        target_section_id = unowned_section_ids[0]
        addressed_corpus = corpus.append(
            CorpusEntry(
                id="req-04-07-differential-control-probe-entry",
                surface="AGENTS.md",
                section=target_section_id,
                tier="invariant",
                classification="Mechanical",
                text="REQ-0.35.0-04-07 differential control probe entry.",
                origin="test",
                ts="2026-09-02T00:00:00Z",
            )
        )

        after_corpus = compute_baseline(surface_text, addressed_corpus)

        self.assertEqual(
            after_corpus.owned_section_count,
            before.owned_section_count + 1,
            "addressing one previously-unowned section must increase "
            "owned_section_count by exactly 1",
        )
        self.assertEqual(
            after_corpus.total_byte_span,
            before.total_byte_span,
            "the surface did not change, so total_byte_span must not move",
        )
        self.assertLess(
            after_corpus.unowned_byte_span,
            before.unowned_byte_span,
            "addressing a section must strictly decrease unowned_byte_span",
        )
        self.assertGreater(
            after_corpus.coverage_pct,
            before.coverage_pct,
            "addressing a section must strictly increase coverage_pct",
        )
        self.assertIn(target_section_id, after_corpus.entry_count_by_section)

        # --- Control 3: the snapshot-detection assertion ---------------------
        # The point of the whole control, made explicit rather than merely
        # implied by the individual assertions above: a stored day-one
        # snapshot would report IDENTICAL figures for `before`,
        # `after_surface`, and `after_corpus` regardless of either
        # perturbation, so every delta below would read zero.
        self.assertNotEqual(after_surface.total_byte_span, before.total_byte_span)
        self.assertNotEqual(after_surface.unowned_byte_span, before.unowned_byte_span)
        self.assertNotEqual(after_corpus.owned_section_count, before.owned_section_count)
        self.assertNotEqual(after_corpus.unowned_byte_span, before.unowned_byte_span)


class TestWriteDeclarationAtomically(unittest.TestCase):
    """A declaration write is all-or-nothing -- no reader ever sees a torn file.

    `Path.write_text` truncates the target before it writes, so an interrupted
    write leaves a half-serialized declaration on disk. A torn declaration is
    not merely a lost update: it is an unreadable coverage claim on the ONE
    surface that gates the unowned-byte ratchet, so every reader of it fails
    closed until a human repairs it by hand -- the silent-hand-edit path
    ADR-0.35.0 exists to close.
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._path = Path(self._tempdir.name) / "Doc.md.json"
        self._original = '{"unowned_byte_floor": 100}\n'
        self._path.write_text(self._original, encoding="utf-8")

    @covers("REQ-0.35.0-04-05")
    def test_a_failed_replace_leaves_the_target_byte_unchanged(self) -> None:
        """Would break if production went back to a truncating in-place write.

        The failure is injected at the rename, which is the ONLY step that may
        make the new contents visible; everything before it must be confined
        to staging.
        """
        before = self._path.read_bytes()
        raised: list[OSError] = []
        with mock.patch("os.replace", side_effect=OSError("disk full")):
            try:
                write_declaration_atomically(self._path, '{"unowned_byte_floor": 999}\n')
            except OSError as exc:  # noqa: PERF203 - one call, not a loop body
                raised.append(exc)

        self.assertEqual(
            self._path.read_bytes(),
            before,
            "a failed declaration write must leave the target byte-unchanged, "
            "never a partially-written file",
        )
        self.assertTrue(
            raised, "a failed atomic replace must propagate to the caller, never be swallowed"
        )
        residue = sorted(p.name for p in self._path.parent.iterdir() if p.name != "Doc.md.json")
        self.assertEqual(residue, [], f"staging files must be cleaned up, found {residue}")

    @covers("REQ-0.35.0-04-05")
    def test_a_successful_write_replaces_the_contents_and_leaves_no_staging(self) -> None:
        """Would break if the staging file were left behind or never renamed in."""
        write_declaration_atomically(self._path, '{"unowned_byte_floor": 42}\n')

        self.assertEqual(self._path.read_text(encoding="utf-8"), '{"unowned_byte_floor": 42}\n')
        residue = sorted(p.name for p in self._path.parent.iterdir() if p.name != "Doc.md.json")
        self.assertEqual(residue, [], f"staging files must be cleaned up, found {residue}")

    @unittest.skipUnless(os.name == "posix", "F_GETFL access-mode probe is POSIX-only")
    @covers("REQ-0.35.0-04-05")
    def test_the_descriptor_handed_to_fsync_is_open_for_writing(self) -> None:
        """Would break if the durability barrier fsynced a READ-ONLY handle.

        On Windows `os.fsync` is `_commit` -> `FlushFileBuffers`, which needs
        GENERIC_WRITE; a read handle returns ERROR_ACCESS_DENIED and `os.fsync`
        raises OSError. That OSError is caught by this module's own `except
        OSError` and re-raised, so the FIRST step of every declaration write
        fails and `gz content unown` -- including its recovery path -- can
        never complete on Windows. The access mode of the descriptor is
        therefore the semantic under test, not an implementation detail.
        """
        observed: list[int] = []
        real_fsync = os.fsync

        def probing_fsync(fd: int) -> None:
            # Directory descriptors are EXEMPT, not overlooked. A directory
            # cannot be opened for writing on POSIX -- O_RDONLY is the only
            # way to obtain a syncable handle -- and the directory barrier is
            # guarded by `os.name == "posix"`, so it never executes on the
            # platform whose GENERIC_WRITE requirement this fence protects.
            # Narrowing to regular files keeps the fence load-bearing for the
            # descriptor that DOES cross to Windows; dropping the assertion
            # wholesale is what would silently re-admit the read-handle bug.
            if not stat.S_ISDIR(os.fstat(fd).st_mode):
                observed.append(fcntl.fcntl(fd, fcntl.F_GETFL) & os.O_ACCMODE)
            return real_fsync(fd)

        with mock.patch("gzkit.content.ownership.os.fsync", side_effect=probing_fsync):
            write_declaration_atomically(self._path, '{"surface": "Doc.md"}\n')

        self.assertTrue(observed, "the durability barrier must actually fsync")
        for mode in observed:
            self.assertIn(
                mode,
                (os.O_WRONLY, os.O_RDWR),
                "fsync must be handed a writable descriptor; a read handle "
                "makes this write unrunnable on Windows",
            )

    @covers("REQ-0.35.0-04-05")
    def test_the_bytes_on_disk_are_byte_identical_to_the_text_handed_in(self) -> None:
        """Would break if newline translation were left at the platform default.

        The declaration is a TRACKED artifact, so on Windows a default-newline
        write turns every `\n` into `\r\n` and the committed JSON differs by
        platform. `newline="\n"` is pinned, so this assertion is GREEN on
        both: the fence FIRES only on Windows and is INERT on POSIX, where
        the default translation is already a no-op. A regression that drops
        that pin therefore reads green in every POSIX run of this suite and
        RED only on Windows -- the same one-sided blindness the
        writable-descriptor test above carries, and the reason both are
        written as cross-platform fences rather than local assertions.
        """
        text = '{\n  "surface": "Doc.md"\n}\n'
        write_declaration_atomically(self._path, text)
        self.assertEqual(self._path.read_bytes(), text.encode("utf-8"))

    @unittest.skipUnless(os.name == "posix", "directory fsync is POSIX-only")
    @covers("REQ-0.35.0-04-02")
    def test_the_parent_directory_is_synced_so_the_rename_is_durable(self) -> None:
        """Would break if the barrier stopped at the file descriptor.

        Step-4b adversary finding 4. Syncing the staging descriptor makes the
        BYTES durable and says nothing about the RENAME: on POSIX the directory
        entry `os.replace` rewrites is buffered metadata, so a power loss right
        after the swap can leave the directory still naming the old inode. The
        write is then atomic but NOT durable, on the one artifact gating the
        unowned-byte ratchet.

        The assertion is on the fsync TARGETS, not on a call count: a count
        cannot tell a second file-descriptor sync from a directory sync, so it
        would stay green if the barrier were pointed at the wrong object. Here
        the parent directory must appear among the synced fds, which is false
        unless the directory itself was opened and synced.
        """
        synced_dirs: list[str] = []
        real_fsync = os.fsync

        def tracking_fsync(fd: int) -> None:
            try:
                if stat.S_ISDIR(os.fstat(fd).st_mode):
                    synced_dirs.append(os.path.realpath(f"/dev/fd/{fd}"))
            except OSError:
                pass
            real_fsync(fd)

        with mock.patch.object(os, "fsync", tracking_fsync):
            write_declaration_atomically(self._path, '{"surface": "Doc.md"}\n')

        self.assertTrue(
            synced_dirs,
            msg="no directory was fsynced -- the rename is atomic but not durable",
        )


class TestRecordUnownedTotalReadsTheFloorInsideTheLock(unittest.TestCase):
    """REQ-0.35.0-04-02: the refusal is decided against the COMMITTED floor.

    `record_unowned_total` receives a declaration the caller read at some
    earlier moment. Deciding the decrease-only comparison against that
    parameter alone lets two callers holding the same pre-read floor commit
    40 and then 60 -- an INCREASE through the one path REQ-0.35.0-04-02
    forbids raising the floor from -- and the result is internally consistent,
    so `load_declaration` accepts it. The authoritative floor is the one on
    disk at write time.
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
            floor_event_id="seed-unowned-ratchet-updated-0",
        )
        self._path = declaration_path(self._root, "Doc.md")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(self._declaration.model_dump_json(indent=2) + "\n", encoding="utf-8")

    def _persisted_floor(self) -> int:
        return int(json.loads(self._path.read_text(encoding="utf-8"))["unowned_byte_floor"])

    @covers("REQ-0.35.0-04-02")
    def test_a_stale_read_second_caller_cannot_raise_the_committed_floor(self) -> None:
        """Would pass if the comparison used the caller's stale parameter.

        Both callers hold the SAME declaration read before either wrote --
        floor 100. The first commits 40. The second's 60 is below the stale
        100 it holds but ABOVE the 40 now committed, so accepting it raises
        the ratchet. The refusal must be decided against 40.
        """
        stale = self._declaration
        record_unowned_total(self._root, stale, 40)
        self.assertEqual(self._persisted_floor(), 40)

        refusal: str | None = None
        try:
            record_unowned_total(self._root, stale, 60)
        except RatchetRefusedError as exc:
            refusal = str(exc)

        # The durable claim first: a raise through this path is the defect,
        # and it is observable on disk whether or not an exception was raised.
        self.assertEqual(
            self._persisted_floor(),
            40,
            "a stale-read caller raised the committed ratchet floor through the "
            "ordinary path, which REQ-0.35.0-04-02 forbids",
        )
        self.assertIsNotNone(
            refusal,
            "recording 60 over a committed floor of 40 must be REFUSED, not accepted",
        )
        assert refusal is not None
        self.assertIn("REQ-0.35.0-04-02", refusal)
        self.assertIn("60", refusal)
        # The prose must name that the refusal is against the CURRENT committed
        # floor, which may have moved since the caller read it -- otherwise the
        # operator reads "above the stored value" and checks the wrong number.
        self.assertIn("40", refusal)
        self.assertIn("gz content unown", refusal)

    @covers("REQ-0.35.0-04-02")
    def test_the_minted_id_chains_on_the_predecessor_that_is_actually_on_disk(self) -> None:
        """Would pass if the chain link were read off the caller's parameter.

        The event id is a CHAIN LINK over the predecessor `floor_event_id`. If
        it is minted from the id the caller read rather than the one committed
        at write time, the link names a predecessor that is no longer the
        predecessor -- a broken chain wearing a valid-looking id, which
        `load_declaration`'s chain validation cannot detect because the stored
        floor and its minted event still agree.
        """
        committed = self._declaration.model_copy(
            update={"floor_event_id": "committed-unowned-ratchet-updated-9"}
        )
        self._path.write_text(committed.model_dump_json(indent=2) + "\n", encoding="utf-8")

        # The caller still holds the OLD chain link it read before the commit.
        stale = self._declaration  # floor_event_id="seed-unowned-ratchet-updated-0"
        minted = record_unowned_total(self._root, stale, 40)

        # Reference: the same move made by a caller whose declaration already
        # carries the committed predecessor. Semantics, not a hardcoded digest.
        reference = record_unowned_total(Path(self._tempdir.name) / "reference", committed, 40)
        self.assertEqual(
            minted.floor_event_id,
            reference.floor_event_id,
            "the minted id must chain on the predecessor committed at write time",
        )
        from_stale = record_unowned_total(Path(self._tempdir.name) / "from-stale", stale, 40)
        self.assertNotEqual(
            minted.floor_event_id,
            from_stale.floor_event_id,
            "chaining on the stale predecessor would mint a different id -- proving "
            "the assertion above is not vacuous",
        )

    @covers("REQ-0.35.0-04-02")
    def test_an_attested_section_flip_committed_in_between_survives_this_write(self) -> None:
        """The in-lock re-read must govern the WHOLE persisted object.

        `gz content unown` commits an attested transition: `alpha-section`
        flips to `unowned` and the floor RISES to 200. A caller still holding
        the PRE-FLIP declaration (floor 100, `alpha-section` corpus-owned)
        then records 90 -- legal against the committed 200, so it is accepted
        and must land. If the persisted object is built from the CALLER'S
        stale copy with only the two ratchet scalars patched, that write
        silently REVERTS the attested flip while its ledger event still
        stands, and the reverted file is self-consistent enough that
        `load_declaration` accepts it forever. That is the same lost-update
        class the committed-floor re-read closes, one field over, on the same
        locked file -- so the re-read has to decide the sections map too.
        """
        stale = self._declaration.model_copy(
            update={"sections": {"doc-title": "corpus-owned", "alpha-section": "corpus-owned"}}
        )
        attested = self._declaration.model_copy(
            update={
                "sections": {"doc-title": "corpus-owned", "alpha-section": "unowned"},
                "unowned_byte_floor": 200,
                "measured_at": "2026-09-02T12:00:00Z",
                "floor_event_id": "attested-section-ownership-unowned-1",
            }
        )
        self._path.write_text(attested.model_dump_json(indent=2) + "\n", encoding="utf-8")

        returned = record_unowned_total(self._root, stale, 90)

        persisted = json.loads(self._path.read_text(encoding="utf-8"))
        # The recording itself must have landed -- otherwise the flip would
        # survive merely because nothing was written, and the assertion below
        # would be vacuous.
        self.assertEqual(persisted["unowned_byte_floor"], 90)
        self.assertEqual(
            persisted["sections"]["alpha-section"],
            "unowned",
            "recording a total through the ordinary path reverted an attested "
            "section flip committed in between, leaving its ledger event "
            "announcing a transition the declaration no longer carries",
        )
        self.assertEqual(
            persisted["measured_at"],
            "2026-09-02T12:00:00Z",
            "the persisted declaration must carry the committed measurement, "
            "not the moment the stale caller happened to read",
        )
        # The returned object is the declaration as COMMITTED, so a caller who
        # persists or compares it does not reintroduce the staleness this
        # re-read exists to close.
        self.assertEqual(returned.sections["alpha-section"], "unowned")
        self.assertEqual(returned.measured_at, "2026-09-02T12:00:00Z")
        self.assertEqual(returned.unowned_byte_floor, 90)

    @covers("REQ-0.35.0-04-03")
    def test_a_first_write_with_no_declaration_on_disk_uses_the_callers_floor(self) -> None:
        """The genuine first-write case: nothing committed to be stale against.

        Falling back to the parameter here is not a weakening of the in-lock
        re-read -- with no file on disk there is no committed floor for the
        caller's read to have gone stale against, and refusing would make the
        very first recording unreachable.
        """
        fresh = Path(self._tempdir.name) / "fresh"
        updated = record_unowned_total(fresh, self._declaration, 40)

        path = declaration_path(fresh, "Doc.md")
        persisted = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["unowned_byte_floor"], 40)
        self.assertEqual(persisted["floor_event_id"], updated.floor_event_id)

        events = [
            json.loads(line)
            for line in (fresh / ".gzkit" / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["prior_unowned_byte_floor"], 100)
        self.assertEqual(events[0]["new_unowned_byte_floor"], 40)


class TestNoDefinitionInThisModuleIsShadowed(unittest.TestCase):
    """A test that cannot fail is the exact class this OBPI exists to kill.

    Python rebinds a duplicate `class` or `def` name silently: the second
    definition replaces the first, `unittest` collects only the survivor, and
    the suite reports OK while every assertion in the shadowed definition is
    never executed. This happened during authoring -- a duplicate
    `TestWriteDeclarationAtomically` swallowed a block of assertions and
    nothing reported it. The hazard is self-detecting from here on.
    """

    def setUp(self) -> None:
        self._module = ast.parse(Path(__file__).read_text(encoding="utf-8"), filename=__file__)

    def test_no_top_level_class_name_is_defined_twice(self) -> None:
        names = [node.name for node in self._module.body if isinstance(node, ast.ClassDef)]
        duplicates = sorted({name for name in names if names.count(name) > 1})
        self.assertEqual(
            duplicates,
            [],
            f"these class names are defined more than once, so the earlier "
            f"definition's tests never run: {duplicates}",
        )

    def test_no_method_name_is_defined_twice_within_a_class(self) -> None:
        shadowed: list[str] = []
        for klass in (n for n in self._module.body if isinstance(n, ast.ClassDef)):
            names = [
                node.name
                for node in klass.body
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
            ]
            shadowed.extend(
                f"{klass.name}.{name}" for name in sorted(set(names)) if names.count(name) > 1
            )
        self.assertEqual(
            shadowed,
            [],
            f"these methods are defined more than once in their class, so the "
            f"earlier definition never runs: {sorted(shadowed)}",
        )

    def test_no_definition_follows_a_module_level_unittest_main_call(self) -> None:
        """A `unittest.main()` block above a definition drops it, silently.

        Under `unittest discover` every definition binds and the suite is
        green, so nothing reports the hazard. Run this file DIRECTLY as a
        script and execution stops at `unittest.main()`: every class and
        function below it never binds, is never collected, and its assertions
        never run -- including this guard itself. That is the same
        "assertions present but not executed" family as a shadowed
        definition, which is why it belongs to this guard rather than beside
        it. The `if __name__ == "__main__":` block belongs at the END of the
        file, with nothing after it.
        """
        last_main = -1
        for index, node in enumerate(self._module.body):
            for child in ast.walk(node):
                if (
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and child.func.attr == "main"
                    and isinstance(child.func.value, ast.Name)
                    and child.func.value.id == "unittest"
                ):
                    last_main = index
        if last_main == -1:
            return
        stranded = [
            node.name
            for node in self._module.body[last_main + 1 :]
            if isinstance(node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef)
        ]
        self.assertEqual(
            stranded,
            [],
            f"these definitions follow a module-level unittest.main() call, so "
            f"running this file as a script never binds them and their "
            f"assertions never execute: {stranded}",
        )


if __name__ == "__main__":
    unittest.main()
