"""Rendition-lineage gate tests — OBPI-0.35.0-06 (ADR-0.35.0 § Decision item 4).

REQ-derived: the gate fails closed over OWNED sections only, reports unowned
bytes as measured debt that never changes an exit code, computes its coverage
figure at run time, reads the EFFECTIVE corpus, and carries three-part recovery
prose that never names un-owning as the escape.

Every expected number below is hand-derived from the fixture's own byte
fragments (`_OWNED_CHUNK`, `_UNOWNED_CHUNK`), never transcribed from a run of
the code and never a stored constant — REQ-0.35.0-06-03 forbids exactly that.
"""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from gzkit.content.corpus_store import append_entry
from gzkit.content.lineage import lineage_path
from gzkit.content.models import CorpusEntry
from gzkit.content.ownership import declaration_path, sections_digest
from gzkit.content.rendition_store import rendition_path
from gzkit.governance.events import emit_section_ownership_genesis
from gzkit.governance.trust_audits.rendition_lineage import (
    LineageCoverage,
    measure_coverage,
    validate_rendition_lineage,
)
from gzkit.traceability import covers

_SURFACE = "TestSurface.md"
_OWNER = "TestType"
_CONSUMER = "root"

_MANIFEST = {
    "content_type_routes": {_OWNER: [_CONSUMER]},
    "content_type_temperatures": {_OWNER: {_CONSUMER: "lite"}},
    "surface_content_types": {_SURFACE: _OWNER},
}

#: The one corpus entry addressed to the owned section. `generate_candidate`
#: materializes an owned section as `<heading line>` + `"\n"` + body + `"\n"`,
#: so a committed rendition in that exact shape is the clean baseline.
_CANON_TEXT = "Canon body line the corpus owns."
_OWNED_CHUNK = f"## Owned Section\n\n{_CANON_TEXT}\n"
_UNOWNED_CHUNK = "## Unowned Section\nHand-authored prose nobody claims.\n"
_CLEAN_TEXT = _OWNED_CHUNK + _UNOWNED_CHUNK

_DECL_SECTIONS = {"owned-section": "corpus-owned", "unowned-section": "unowned"}


def _span_of(chunk: str) -> int:
    """UTF-8 byte length of one committed-text fragment (the hand-derived oracle)."""
    return len(chunk.encode("utf-8"))


class _LineageFixtureMixin:
    """Isolated tmp root plus the four fixture writers this gate's inputs need."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)

    def _validate(self, **kwargs: object) -> list:
        """Run the gate with its advisory captured, and return the findings.

        The gate emits one `emit_advisory` line to stderr on EVERY run. Left
        uncaptured that line interleaves into `unittest -v`'s own result line —
        it lands between the `... ` and the `ok` — which stops a verbose-output
        parser from recovering the executed test id. `gz obpi acceptance prove`
        is such a parser: with the ids unrecoverable it reads the baseline as
        not-green and reports every mutation `inconclusive`, so the covering
        test proves nothing. Capturing here keeps the real stderr clean for any
        consumer that parses it. Tests that ASSERT on the advisory capture it
        themselves and call the gate directly.
        """
        captured = io.StringIO()
        with redirect_stderr(captured):
            return validate_rendition_lineage(self._root, **kwargs)

    def _write_manifest(self) -> None:
        (self._root / "data").mkdir(exist_ok=True)
        (self._root / "data" / "vendor-manifest.json").write_text(
            json.dumps(_MANIFEST), encoding="utf-8"
        )

    def _write_rendition(self, text: str) -> None:
        path = rendition_path(self._root, _SURFACE, _CONSUMER)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def _write_declaration(self, sections: dict[str, str], unowned_byte_floor: int) -> Path:
        digest = sections_digest(sections)
        event_id = f"section-ownership-genesis-{_SURFACE}-{digest[:12]}"
        emit_section_ownership_genesis(self._root, event_id, _SURFACE, digest, unowned_byte_floor)
        path = declaration_path(self._root, _SURFACE)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "surface": _SURFACE,
                    "sections": sections,
                    "unowned_byte_floor": unowned_byte_floor,
                    "measured_at": "2026-09-11T00:00:00Z",
                    "floor_event_id": event_id,
                }
            ),
            encoding="utf-8",
        )
        return path

    def _write_lineage(self, chunks: list[tuple[str, bool, tuple[str, ...], str]]) -> None:
        """Write a committed lineage sidecar, spans accumulated from *chunks*' own bytes."""
        document: dict[str, object] = {}
        cursor = 0
        for section_id, owned, entry_ids, chunk in chunks:
            end = cursor + _span_of(chunk)
            document[section_id] = {
                "owned": owned,
                "entry_ids": list(entry_ids),
                "byte_span": [cursor, end],
            }
            cursor = end
        path = lineage_path(self._root, _SURFACE, _CONSUMER)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document, indent=2), encoding="utf-8")

    def _append_canon_entry(
        self,
        entry_id: str = "e-canon",
        text: str = _CANON_TEXT,
        *,
        tier: str = "compressible",
        classification: str = "Ambiguous",
        ts: str = "2026-09-11T00:00:00Z",
        **kwargs: object,
    ) -> None:
        append_entry(
            self._root,
            _SURFACE,
            CorpusEntry(
                id=entry_id,
                surface=_SURFACE,
                section="owned-section",
                tier=tier,
                classification=classification,
                text=text,
                origin="test",
                ts=ts,
                **kwargs,
            ),
        )

    def _seed(
        self,
        *,
        committed_text: str = _CLEAN_TEXT,
        sections: dict[str, str] | None = None,
        lineage_chunks: list[tuple[str, bool, tuple[str, ...], str]] | None = None,
    ) -> None:
        """Seed a complete gradeable surface: manifest, corpus, rendition, declaration, lineage."""
        sections = sections or dict(_DECL_SECTIONS)
        self._write_manifest()
        self._append_canon_entry()
        self._write_rendition(committed_text)
        unowned_floor = sum(
            _span_of(chunk)
            for section_id, _owned, _ids, chunk in (lineage_chunks or _clean_chunks(committed_text))
            if sections.get(section_id) == "unowned"
        )
        self._write_declaration(sections, unowned_floor)
        self._write_lineage(lineage_chunks or _clean_chunks(committed_text))


def _clean_chunks(committed_text: str) -> list[tuple[str, bool, tuple[str, ...], str]]:
    """Hand-derived lineage chunks for a two-section committed text."""
    owned_chunk, unowned_chunk = committed_text.split("## Unowned Section", 1)
    return [
        ("owned-section", True, ("e-canon",), owned_chunk),
        ("unowned-section", False, (), "## Unowned Section" + unowned_chunk),
    ]


class OwnedSectionMatchingCorpusPassesTest(_LineageFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-06-01: an owned section equal to its corpus materialization is clean."""

    @covers("REQ-0.35.0-06-01")
    def test_owned_section_matching_its_materialization_yields_no_findings(self) -> None:
        self._seed()

        self.assertEqual(self._validate(fail_closed=True), [])


_DRIFT_OWNED_CHUNK = "## Owned Section\n\nHand-authored prose the corpus never said.\n"
_DRIFT_TEXT = _DRIFT_OWNED_CHUNK + _UNOWNED_CHUNK


class OwnedSectionDriftFailsClosedTest(_LineageFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-06-02: hand-authored prose inside an OWNED section is drift."""

    @covers("REQ-0.35.0-06-02")
    def test_owned_section_not_derivable_from_corpus_names_the_section(self) -> None:
        self._seed(committed_text=_DRIFT_TEXT)

        errors = self._validate(fail_closed=True)

        self.assertEqual(len(errors), 1, f"expected exactly one finding, got {errors!r}")
        self.assertEqual(errors[0].type, "rendition_lineage")
        self.assertIn("owned-section", errors[0].message)


class UnownedSectionNeverFailsTheGateTest(_LineageFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-06-03: unowned bytes are measured debt, never an exit-code contribution.

    Both fixtures are built to be FALSIFIABLE, not merely green. The second is
    the load-bearing one: a surface whose every section is `unowned` carries no
    enforceable scope at all, so the missing-lineage fail-closed path
    (design decision 1 — a declared owned section with no committed lineage is an
    enforcement gap) must not reach it. Dropping the owned-count guard on that
    path turns unowned bytes into an exit-3 contribution, which is exactly what
    this REQ forbids.
    """

    @covers("REQ-0.35.0-06-03")
    def test_arbitrary_prose_in_an_unowned_section_yields_no_findings(self) -> None:
        self._seed()
        append_entry(
            self._root,
            _SURFACE,
            CorpusEntry(
                id="e-debt",
                surface=_SURFACE,
                section="unowned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Wording the corpus would put in the unowned section.",
                origin="test",
                ts="2026-09-11T00:00:01Z",
            ),
        )

        self.assertEqual(self._validate(fail_closed=True), [])

    @covers("REQ-0.35.0-06-03")
    def test_fully_unowned_surface_without_a_lineage_yields_no_findings(self) -> None:
        """No section is owned, so there is no scope to witness and nothing to fail."""
        all_unowned = dict.fromkeys(_DECL_SECTIONS, "unowned")
        self._seed(sections=all_unowned)
        lineage_path(self._root, _SURFACE, _CONSUMER).unlink()

        self.assertEqual(self._validate(fail_closed=True), [])

    @covers("REQ-0.35.0-06-03")
    def test_unowned_section_citing_a_dead_entry_id_yields_no_findings(self) -> None:
        """The liveness check is scoped to OWNED sections and never reaches unowned ones.

        A committed lineage can cite an entry id that is not live in the effective
        corpus from within an UNOWNED section's `entry_ids`: `owned` is left `False`
        so this test probes the liveness guard alone, never the owned-flag-mismatch
        check that precedes it in `verify_candidate_against_declaration`. Without the
        `if declared != _OWNED: continue` guard this dead reference would surface as
        a "not live in the effective corpus" finding; with it, the surface is clean.
        """
        owned_chunk, unowned_chunk = _CLEAN_TEXT.split("## Unowned Section", 1)
        lineage_chunks = [
            ("owned-section", True, ("e-canon",), owned_chunk),
            ("unowned-section", False, ("e-nonexistent",), "## Unowned Section" + unowned_chunk),
        ]
        self._seed(lineage_chunks=lineage_chunks)

        self.assertEqual(self._validate(fail_closed=True), [])


_MULTIBYTE_CHUNK = "## Accented Section\n\nCafé naïve — em dash too.\n"


class CoverageIsComputedAtRunTimeTest(_LineageFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-06-04: the coverage figure is derived, never stored.

    Every expected number is hand-derived from the fixture's own chunks, so a
    stored constant (the defect REQ-0.35.0-06-03 of the brief's numbered
    requirements names) cannot satisfy these assertions: flipping one section's
    declared ownership must move the figure.
    """

    @covers("REQ-0.35.0-06-04")
    def test_flipping_a_section_to_owned_changes_the_computed_coverage(self) -> None:
        baseline = measure_coverage(_CLEAN_TEXT, _DECL_SECTIONS)

        self.assertEqual(baseline.owned_sections, 1)
        self.assertEqual(baseline.total_sections, 2)
        self.assertEqual(baseline.owned_bytes, _span_of(_OWNED_CHUNK))
        self.assertEqual(baseline.total_bytes, _span_of(_CLEAN_TEXT))
        self.assertAlmostEqual(
            baseline.percentage,
            100.0 * _span_of(_OWNED_CHUNK) / _span_of(_CLEAN_TEXT),
        )

        flipped = measure_coverage(_CLEAN_TEXT, dict.fromkeys(_DECL_SECTIONS, "corpus-owned"))

        self.assertEqual(flipped.owned_sections, 2)
        self.assertEqual(flipped.owned_bytes, _span_of(_CLEAN_TEXT))
        self.assertAlmostEqual(flipped.percentage, 100.0)
        self.assertNotEqual(flipped, baseline)

    @covers("REQ-0.35.0-06-04")
    def test_coverage_counts_utf8_bytes_not_characters(self) -> None:
        """A multibyte section's span is its BYTE length — the unit the ratchet measures in."""
        text = _MULTIBYTE_CHUNK + _UNOWNED_CHUNK
        coverage = measure_coverage(
            text, {"accented-section": "corpus-owned", "unowned-section": "unowned"}
        )

        self.assertEqual(coverage.owned_bytes, _span_of(_MULTIBYTE_CHUNK))
        self.assertGreater(_span_of(_MULTIBYTE_CHUNK), len(_MULTIBYTE_CHUNK))

    @covers("REQ-0.35.0-06-04")
    def test_scope_surfaces_the_computed_figure_on_the_clean_path(self) -> None:
        """The figure is in the scope's own output even when there is nothing to report."""
        self._seed()
        expected = measure_coverage(_CLEAN_TEXT, _DECL_SECTIONS)

        captured = io.StringIO()
        with redirect_stderr(captured):
            errors = validate_rendition_lineage(self._root, fail_closed=True)

        self.assertEqual(errors, [])
        emitted = captured.getvalue()
        self.assertIn(f"{expected.owned_sections}/{expected.total_sections} sections", emitted)
        self.assertIn(f"{expected.owned_bytes}/{expected.total_bytes} bytes", emitted)
        self.assertIn(f"{expected.percentage:.1f}%", emitted)

    @covers("REQ-0.35.0-06-04")
    def test_merge_accumulates_all_six_fields_across_two_non_zero_renditions(self) -> None:
        """`merge()` sums six fields element-wise across two genuine renditions.

        Both operands use twelve mutually-distinct, distinguishable values
        chosen so that no two fields share a value and no pair of fields sums
        to the same total as another pair: a transposed or self-summed
        summand (e.g. `total_bytes` added to itself, or `ungraded_sections`
        swapped with `ungraded_bytes`) produces a number that disagrees with
        the hand-derived expectation below rather than surviving by
        coincidence. An identity-merge test (`LineageCoverage(0,0,0,0)`)
        cannot catch either defect, which is the gap this test closes
        (rendition-lineage-merge-untested-multi-operand). Every expected
        value is computed by hand from the operands, never by calling
        `merge()` to derive what this test then asserts.
        """
        root_rendition = LineageCoverage(
            owned_sections=2,
            total_sections=5,
            owned_bytes=11,
            total_bytes=47,
            ungraded_sections=3,
            ungraded_bytes=13,
        )
        codex_rendition = LineageCoverage(
            owned_sections=7,
            total_sections=19,
            owned_bytes=101,
            total_bytes=293,
            ungraded_sections=17,
            ungraded_bytes=29,
        )

        merged = root_rendition.merge(codex_rendition)

        self.assertEqual(merged.owned_sections, 2 + 7)
        self.assertEqual(merged.total_sections, 5 + 19)
        self.assertEqual(merged.owned_bytes, 11 + 101)
        self.assertEqual(merged.total_bytes, 47 + 293)
        self.assertEqual(merged.ungraded_sections, 3 + 17)
        self.assertEqual(merged.ungraded_bytes, 13 + 29)
        # percentage is a property over owned_bytes/total_bytes of the SUM,
        # so a numerator/denominator transposition surfaces here even if the
        # raw field assertions above happened to miss it.
        self.assertAlmostEqual(merged.percentage, 100.0 * (11 + 101) / (47 + 293))


_RETIRED_TEXT = "Doctrine the corpus has since retired."
_STALE_OWNED_CHUNK = f"## Owned Section\n\n{_CANON_TEXT}\n\n{_RETIRED_TEXT}\n"
_STALE_TEXT = _STALE_OWNED_CHUNK + _UNOWNED_CHUNK


class RetiredEntryLeftInAnOwnedSectionIsDriftTest(_LineageFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-06-05: the gate reads the EFFECTIVE corpus, so a retired entry is drift.

    Two independent arms, both of which a raw-append-log read would lose: the
    regeneration no longer materializes the retired entry's text (so the owned
    section mismatches), and the committed lineage still cites the retired id (so
    its provenance is stale). A gate left on `load_corpus`'s raw return reports
    GREEN over a rendition that carries retired doctrine — the worst detection
    latency named in this ADR's pre-mortem.
    """

    @covers("REQ-0.35.0-06-05")
    def test_retired_invariant_text_still_committed_fails_closed(self) -> None:
        self._seed(
            committed_text=_STALE_TEXT,
            lineage_chunks=[
                ("owned-section", True, ("e-canon", "e-invariant"), _STALE_OWNED_CHUNK),
                ("unowned-section", False, (), _UNOWNED_CHUNK),
            ],
        )
        self._append_canon_entry(
            entry_id="e-invariant",
            text=_RETIRED_TEXT,
            tier="invariant",
            classification="Mechanical",
            ts="2026-09-11T00:00:01Z",
        )
        self._append_canon_entry(
            entry_id="e-tomb", text="", ts="2026-09-11T00:00:02Z", retires="e-invariant"
        )

        errors = self._validate(fail_closed=True)
        messages = [error.message for error in errors]

        self.assertTrue(
            any("owned-section" in m and "materializes" in m for m in messages),
            f"no owned-section materialization finding in {messages!r}",
        )
        self.assertTrue(
            any("e-invariant" in m and "not live" in m for m in messages),
            f"no retired-id finding in {messages!r}",
        )


#: Phrasings that would offer un-owning as the way out of a lineage failure.
#: Pre-mortem #2: owned-section fail-closed becomes the thing agents route
#: around, and the cheapest route is un-owning. The word "unowned" is not
#: grep-forbidden outright — it legitimately names the other half of the closed
#: enum — only these SUGGESTING forms are.
_UNOWNING_ESCAPES = (
    "mark it unowned",
    "mark the section unowned",
    "declare it unowned",
    "declare the section unowned",
    "set it to unowned",
    "gz content unown",
    "re-declare",
)


class RecoveryProseCarriesThreePartsTest(_LineageFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-06-06: the exit-3 message is three-part and never offers the escape."""

    @covers("REQ-0.35.0-06-06")
    def test_drift_message_names_section_cites_the_adr_and_prescribes_the_round_trip(self) -> None:
        self._seed(committed_text=_DRIFT_TEXT)

        errors = self._validate(fail_closed=True)

        self.assertEqual(len(errors), 1, f"expected exactly one finding, got {errors!r}")
        message = errors[0].message

        # Part 1 — WHAT failed: the drifted owned section is named.
        self.assertIn("owned-section", message)
        # Part 2 — WHY forbidden: owned sections are corpus-derived by the ADR's ruling.
        self.assertIn("ADR-0.35.0", message)
        self.assertIn("Decision item 4", message)
        # Part 3 — NEXT step: the runnable corpus round-trip, and nothing about ownership.
        parts = message.split("Next step:", 1)
        self.assertEqual(len(parts), 2, f"message carries no 'Next step:' part: {message!r}")
        next_step = parts[1]
        self.assertIn("gz content compose", next_step)
        self.assertIn("gz content commit", next_step)
        self.assertNotIn("unowned", next_step)

        lowered = message.lower()
        for escape in _UNOWNING_ESCAPES:
            self.assertNotIn(escape, lowered, f"recovery prose offers the escape {escape!r}")


class MissingCommittedLineageIsDisclosedTest(_LineageFixtureMixin, unittest.TestCase):
    """REQ-0.35.0-06-03: a surface with no committed lineage has no graded scope.

    Operator ruling (2026-09-11): missing committed lineage is DISCLOSED, not
    fail-closed. A declaration without a lineage sidecar means the gate has
    nothing to grade those sections against — reporting them as owned coverage
    would be coverage the gate cannot prove, and failing on them would make the
    gate red for an artifact OBPI-0.35.0-07 has not yet published. Both are
    wrong; the honest answer is to count them UNGRADED and say so.
    """

    @covers("REQ-0.35.0-06-03")
    def test_declared_ownership_without_a_lineage_is_ungraded_not_failed(self) -> None:
        self._seed()
        lineage_path(self._root, _SURFACE, _CONSUMER).unlink()

        captured = io.StringIO()
        with redirect_stderr(captured):
            errors = validate_rendition_lineage(self._root, fail_closed=True)

        self.assertEqual(errors, [], f"missing lineage must not be a finding: {errors!r}")
        emitted = captured.getvalue()
        self.assertIn(f"1 section(s) / {_span_of(_OWNED_CHUNK)} byte(s) UNGRADED", emitted)
        self.assertIn("0/105 bytes owned", emitted.replace(str(_span_of(_CLEAN_TEXT)), "105"))
        self.assertIn("no committed lineage", emitted)
