"""Composer engine tests — OBPI-0.0.37-21 (BEHAVIOR REQ proofs for engine layer).

REQ-derived: composer is deterministic (no network/LLM), invariant-tier entries
appear verbatim in the candidate, and violations are rejected.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from gzkit.content.composer import _byte_evidence, compose, generate_candidate
from gzkit.content.corpus_store import append_entry
from gzkit.content.models import Corpus, CorpusEntry
from gzkit.content.ownership import (
    declaration_path,
    iter_section_boundaries,
    measure_section_spans,
    sections_digest,
)
from gzkit.content.rendition_store import rendition_path
from gzkit.governance.events import emit_section_ownership_genesis
from gzkit.traceability import covers

_VENDOR_MANIFEST = {
    "content_type_routes": {"AgentContract": ["root"]},
    "content_type_temperatures": {"AgentContract": {"root": "lite"}},
}

_INVARIANT_TEXT = "YOU OWN THE WORK COMPLETELY."
_COMPRESSIBLE_TEXT = "Prefer stdlib JSONL for append-only stores."


def _seed_project(root: Path) -> None:
    """Write a minimal project with corpus + vendor manifest into *root*."""
    (root / "data").mkdir(exist_ok=True)
    (root / "data" / "vendor-manifest.json").write_text(
        json.dumps(_VENDOR_MANIFEST), encoding="utf-8"
    )
    (root / ".gzkit").mkdir(exist_ok=True)
    append_entry(
        root,
        "AGENTS.md",
        CorpusEntry(
            id="e-invariant",
            surface="AGENTS.md",
            section="prime-directive",
            tier="invariant",
            classification="Mechanical",
            text=_INVARIANT_TEXT,
            origin="test",
            ts="2026-06-14T00:00:00Z",
        ),
    )
    append_entry(
        root,
        "AGENTS.md",
        CorpusEntry(
            id="e-compressible",
            surface="AGENTS.md",
            section="behavior-rules",
            tier="compressible",
            classification="Ambiguous",
            text=_COMPRESSIBLE_TEXT,
            origin="test",
            ts="2026-06-14T00:00:00Z",
        ),
    )


class TestComposerEngine(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        _seed_project(self._root)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.0.37-21-02")
    def test_deterministic_output(self) -> None:
        """Identical corpus + setpoint + candidate → identical byte evidence; no network call."""
        candidate_text = f"{_INVARIANT_TEXT}\ncompressed content"

        with patch("socket.socket") as mock_sock:
            result1 = compose(self._root, "AGENTS.md", "root", candidate_text)
            result2 = compose(self._root, "AGENTS.md", "root", candidate_text)

        mock_sock.assert_not_called()
        self.assertEqual(result1.byte_evidence, result2.byte_evidence)
        self.assertEqual(result1.setpoint, result2.setpoint)
        self.assertEqual(result1.candidate_text, result2.candidate_text)

    @covers("REQ-0.0.37-21-03")
    def test_invariant_tier_verbatim_presence(self) -> None:
        """Invariant-tier entry text appears verbatim in a valid candidate."""
        candidate_text = f"{_INVARIANT_TEXT}\nsome compressed content"
        result = compose(self._root, "AGENTS.md", "root", candidate_text)

        self.assertIn(_INVARIANT_TEXT, result.candidate_text)
        self.assertGreater(result.byte_evidence.invariant_bytes, 0)

    @covers("REQ-0.0.37-21-03")
    def test_invariant_floor_violation_raises(self) -> None:
        """A candidate dropping an invariant entry is refused with ValueError."""
        candidate_text = "only compressible content, no invariant"

        with self.assertRaises(ValueError) as ctx:
            compose(self._root, "AGENTS.md", "root", candidate_text)

        self.assertIn("Invariant-floor violation", str(ctx.exception))

    @covers("REQ-0.0.37-21-04")
    def test_absent_corpus_raises_file_not_found(self) -> None:
        """An absent corpus store raises FileNotFoundError (caller maps to exit 1)."""
        with self.assertRaises(FileNotFoundError):
            compose(self._root, "NONEXISTENT.md", "root", "some text")

    @covers("REQ-0.0.37-21-04")
    def test_undeclared_setpoint_raises_value_error(self) -> None:
        """An undeclared (content_type, consumer) setpoint raises ValueError."""
        candidate_text = f"{_INVARIANT_TEXT}\nsome content"
        with self.assertRaises(ValueError):
            compose(self._root, "AGENTS.md", "unknown-vendor", candidate_text)


class ComposeResolvesContentTypeFromSurfaceTest(unittest.TestCase):
    """The owning content type comes from the surface registry, never a literal default.

    GHI #921. ``compose`` defaulted ``content_type`` to ``"AgentContract"`` and never
    called ``content_type_for_surface``, so every surface — a ``Rule`` corpus included —
    was graded at AgentContract's setpoint. The registry existed for exactly this
    question and was consulted nowhere.
    """

    _RULE_SURFACE = ".gzkit/rules/probe.md"

    _MANIFEST = {
        "content_type_routes": {"AgentContract": ["root"], "Rule": ["claude"]},
        "content_type_temperatures": {
            "AgentContract": {"root": "lite"},
            "Rule": {"claude": "heavy"},
        },
        "surface_content_types": {_RULE_SURFACE: "Rule"},
    }

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self._root = Path(self._tmp.name)
        (self._root / "data").mkdir()
        (self._root / "data" / "vendor-manifest.json").write_text(
            json.dumps(self._MANIFEST), encoding="utf-8"
        )
        for surface in (self._RULE_SURFACE, "UNMAPPED.md"):
            append_entry(
                self._root,
                surface,
                CorpusEntry(
                    id="e-invariant",
                    surface=surface,
                    section="core",
                    tier="invariant",
                    classification="Mechanical",
                    text=_INVARIANT_TEXT,
                    origin="test",
                    ts="2026-08-29T00:00:00Z",
                ),
            )

    def test_rule_surface_composes_at_its_own_declared_setpoint(self) -> None:
        """A Rule-owned surface resolves Rule's setpoint, not AgentContract's.

        ``AgentContract`` declares no ``claude`` temperature here, so resolving the
        owner from the surface is the only way this call can succeed: a hardcoded
        default fails closed inside ``temperature_for``.
        """
        rendition = compose(self._root, self._RULE_SURFACE, "claude", f"{_INVARIANT_TEXT}\nbody")

        self.assertEqual(rendition.setpoint, "heavy")

    def test_unmapped_surface_fails_closed_naming_the_registry(self) -> None:
        """A surface the manifest declares no owner for is refused, not guessed."""
        with self.assertRaises(ValueError) as ctx:
            compose(self._root, "UNMAPPED.md", "claude", f"{_INVARIANT_TEXT}\nbody")

        message = str(ctx.exception)
        self.assertIn("surface_content_types", message)
        self.assertIn("UNMAPPED.md", message)


class TestByteEvidenceAccounting(unittest.TestCase):
    """`compressible_bytes_after` uses attribution, never `total_bytes - invariant_bytes`.

    GHI captured in ADR-0.35.0 § Intent: the retired formula reported 22,378 B
    against a 354 B input, a 63x inflation labelled as compression. These tests
    pin the replacement accounting (REQ-0.35.0-05-06/07).
    """

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self._root = Path(self._tempdir.name)
        _seed_project(self._root)

    def tearDown(self) -> None:
        self._tempdir.cleanup()

    @covers("REQ-0.35.0-05-06")
    def test_candidate_with_no_compressible_text_reports_zero_after(self) -> None:
        """A candidate carrying no compressible entry text attributes zero bytes."""
        candidate_text = f"{_INVARIANT_TEXT}\nfreehand text sharing nothing with the corpus"
        result = compose(self._root, "AGENTS.md", "root", candidate_text)

        self.assertEqual(result.byte_evidence.compressible_bytes_after, 0)

    def test_candidate_with_one_compressible_entry_attributes_its_bytes(self) -> None:
        """A candidate carrying one compressible entry verbatim attributes exactly its bytes."""
        candidate_text = f"{_INVARIANT_TEXT}\n{_COMPRESSIBLE_TEXT}"
        result = compose(self._root, "AGENTS.md", "root", candidate_text)

        self.assertEqual(
            result.byte_evidence.compressible_bytes_after,
            len(_COMPRESSIBLE_TEXT.encode("utf-8")),
        )

    @covers("REQ-0.35.0-05-06")
    def test_after_never_exceeds_before_for_a_realistic_candidate(self) -> None:
        """`compressible_bytes_after` <= `compressible_bytes_before` for a realistic candidate."""
        candidate_text = f"{_INVARIANT_TEXT}\n{_COMPRESSIBLE_TEXT}\nsome extra freehand prose too"
        result = compose(self._root, "AGENTS.md", "root", candidate_text)

        self.assertLessEqual(
            result.byte_evidence.compressible_bytes_after,
            result.byte_evidence.compressible_bytes_before,
        )

    def test_retired_compressible_entry_contributes_to_neither_before_nor_after(self) -> None:
        """A retired compressible entry counts toward neither before nor after (BI-01)."""
        retired_text = "This wording was retired and must never be counted again."
        append_entry(
            self._root,
            "AGENTS.md",
            CorpusEntry(
                id="e-compressible-2",
                surface="AGENTS.md",
                section="behavior-rules",
                tier="compressible",
                classification="Ambiguous",
                text=retired_text,
                origin="test",
                ts="2026-06-14T00:00:01Z",
            ),
        )
        append_entry(
            self._root,
            "AGENTS.md",
            CorpusEntry(
                id="e-compressible-2-tomb",
                surface="AGENTS.md",
                section="behavior-rules",
                tier="compressible",
                classification="Ambiguous",
                text="",
                origin="test",
                ts="2026-06-14T00:00:02Z",
                retires="e-compressible-2",
            ),
        )
        # The retired entry's text is present verbatim in the candidate -- proving
        # that liveness, not textual absence, is what excludes it (BI-01).
        candidate_text = f"{_INVARIANT_TEXT}\n{retired_text}"
        result = compose(self._root, "AGENTS.md", "root", candidate_text)

        self.assertEqual(
            result.byte_evidence.compressible_bytes_before,
            len(_COMPRESSIBLE_TEXT.encode("utf-8")),
        )
        self.assertEqual(result.byte_evidence.compressible_bytes_after, 0)

    @covers("REQ-0.35.0-05-07")
    def test_byte_evidence_raises_when_attributed_exceeds_before(self) -> None:
        """`_byte_evidence` raises ValueError when attributed bytes exceed the before-total."""
        corpus = Corpus(
            entries=(
                CorpusEntry(
                    id="e-compressible",
                    surface="AGENTS.md",
                    section="behavior-rules",
                    tier="compressible",
                    classification="Ambiguous",
                    text=_COMPRESSIBLE_TEXT,
                    origin="test",
                    ts="2026-06-14T00:00:00Z",
                ),
            )
        )
        # Not a member of corpus's effective compressible set -- attributing it
        # makes compressible_bytes_after exceed compressible_bytes_before.
        foreign_entry = CorpusEntry(
            id="e-not-in-corpus",
            surface="AGENTS.md",
            section="behavior-rules",
            tier="compressible",
            classification="Ambiguous",
            text="Text that inflates the attributed sum well beyond the before-total.",
            origin="test",
            ts="2026-06-14T00:00:01Z",
        )

        with self.assertRaises(ValueError) as ctx:
            _byte_evidence(
                corpus=corpus,
                candidate_text="anything",
                setpoint="lite",
                attributed_compressible=[foreign_entry],
            )

        message = str(ctx.exception)
        self.assertIn("compressible_bytes_after", message)
        self.assertIn("compressible_bytes_before", message)

    def test_emission_attribution_counts_only_attributed_entries(self) -> None:
        """Passing `attributed_compressible` counts exactly those entries, ignoring presence."""
        entry_a = CorpusEntry(
            id="e-a",
            surface="AGENTS.md",
            section="behavior-rules",
            tier="compressible",
            classification="Ambiguous",
            text="Entry A text.",
            origin="test",
            ts="2026-06-14T00:00:00Z",
        )
        entry_b = CorpusEntry(
            id="e-b",
            surface="AGENTS.md",
            section="behavior-rules",
            tier="compressible",
            classification="Ambiguous",
            text="Entry B text.",
            origin="test",
            ts="2026-06-14T00:00:01Z",
        )
        corpus = Corpus(entries=(entry_a, entry_b))
        # Both entries' text is textually present in the candidate, but only
        # entry_a is attributed -- emission attribution must ignore entry_b's
        # mere presence.
        candidate_text = "Entry A text.\nEntry B text."

        evidence = _byte_evidence(
            corpus=corpus,
            candidate_text=candidate_text,
            setpoint="lite",
            attributed_compressible=[entry_a],
        )

        self.assertEqual(
            evidence.compressible_bytes_after,
            len(b"Entry A text."),
        )


# -- generate_candidate (OBPI-0.35.0-05 Task 3b) -----------------------------
#
# Unlike `compose`, `generate_candidate` never accepts agent-supplied text: it
# derives owned-section bodies from the corpus and carries unowned-section
# bytes forward verbatim from the prior committed rendition, returning a pure
# (rendition, lineage) result it never writes to disk.

_GEN_SURFACE = "TestSurface.md"
_GEN_OWNER = "TestType"
_GEN_CONSUMER = "root"

_GEN_MANIFEST = {
    "content_type_routes": {_GEN_OWNER: [_GEN_CONSUMER]},
    "content_type_temperatures": {_GEN_OWNER: {_GEN_CONSUMER: "lite"}},
    "surface_content_types": {_GEN_SURFACE: _GEN_OWNER},
}

_GEN_PRIOR_TEXT = (
    "## Owned Section\n"
    "old body text to be replaced\n"
    "## Unowned Section\n"
    "carried forward text verbatim\n"
)

_GEN_DECL_SECTIONS = {"owned-section": "corpus-owned", "unowned-section": "unowned"}


class _GenerateCandidateFixtureMixin:
    """Shared temp-dir + fixture-writer setup for `generate_candidate` tests."""

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._root = Path(self._tempdir.name)

    def _write_manifest(self, manifest: dict | None = None) -> None:
        (self._root / "data").mkdir(exist_ok=True)
        (self._root / "data" / "vendor-manifest.json").write_text(
            json.dumps(manifest or _GEN_MANIFEST), encoding="utf-8"
        )

    def _write_prior_rendition(self, surface: str, consumer: str, text: str) -> None:
        path = rendition_path(self._root, surface, consumer)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(text.encode("utf-8"))

    def _write_declaration(
        self,
        surface: str,
        sections: dict[str, str],
        *,
        prior_text_for_floor: str | None = None,
        unowned_byte_floor: int | None = None,
    ) -> Path:
        if unowned_byte_floor is None:
            spans = measure_section_spans(prior_text_for_floor or "")
            unowned_byte_floor = sum(
                span for sid, span in spans.items() if sections.get(sid) == "unowned"
            )
        digest = sections_digest(sections)
        event_id = f"section-ownership-genesis-{surface}-{digest[:12]}"
        emit_section_ownership_genesis(self._root, event_id, surface, digest, unowned_byte_floor)
        path = declaration_path(self._root, surface)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "surface": surface,
                    "sections": sections,
                    "unowned_byte_floor": unowned_byte_floor,
                    "measured_at": "2026-09-07T00:00:00Z",
                    "floor_event_id": event_id,
                }
            ),
            encoding="utf-8",
        )
        return path

    def _seed(
        self,
        *,
        surface: str = _GEN_SURFACE,
        consumer: str = _GEN_CONSUMER,
        manifest: dict | None = None,
        prior_text: str = _GEN_PRIOR_TEXT,
        sections: dict[str, str] | None = None,
    ) -> None:
        self._write_manifest(manifest)
        self._write_prior_rendition(surface, consumer, prior_text)
        self._write_declaration(
            surface, sections or dict(_GEN_DECL_SECTIONS), prior_text_for_floor=prior_text
        )


class TestOwnedSectionBodyFromCorpus(_GenerateCandidateFixtureMixin, unittest.TestCase):
    @covers("REQ-0.35.0-05-01")
    def test_owned_section_body_is_derived_from_corpus_not_prior_text(self) -> None:
        """An owned section's body comes from the corpus, never the caller/prior text."""
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Fresh corpus-authored wording.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        self.assertIn("Fresh corpus-authored wording.", result.rendition.candidate_text)
        self.assertNotIn("old body text to be replaced", result.rendition.candidate_text)


class TestUnownedSectionByteVerbatim(_GenerateCandidateFixtureMixin, unittest.TestCase):
    @covers("REQ-0.35.0-05-02")
    def test_unowned_section_bytes_are_byte_verbatim(self) -> None:
        """An unowned section's candidate bytes are an exact slice of the prior rendition."""
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Owned body.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        prior_bytes = rendition_path(self._root, _GEN_SURFACE, _GEN_CONSUMER).read_bytes()
        boundary = next(
            b for b in iter_section_boundaries(_GEN_PRIOR_TEXT) if b.section_id == "unowned-section"
        )
        expected = prior_bytes[boundary.start : boundary.end]

        span = result.lineage.sections["unowned-section"].byte_span
        actual = result.rendition.candidate_text.encode("utf-8")[span[0] : span[1]]
        self.assertEqual(actual, expected)


class TestRetiredEntryExcludedButVerbatimSpanUnaffected(
    _GenerateCandidateFixtureMixin, unittest.TestCase
):
    @covers("REQ-0.35.0-05-03")
    def test_retired_entry_contributes_nothing_while_verbatim_span_is_unaffected(self) -> None:
        """A retired entry contributes no owned bytes/id; a coincidentally-identical
        verbatim (unowned) span is unaffected because it never derives from the corpus.
        """
        prior_text = (
            "## Owned Section\n"
            "old body text to be replaced\n"
            "## Unowned Section\n"
            "Duplicate wording appears here too.\n"
        )
        self._seed(prior_text=prior_text)
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-live",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Live wording stays.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-retired",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Duplicate wording appears here too.",
                origin="test",
                ts="2026-09-07T00:00:01Z",
            ),
        )
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-retired-tomb",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="",
                origin="test",
                ts="2026-09-07T00:00:02Z",
                retires="e-retired",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)
        candidate_bytes = result.rendition.candidate_text.encode("utf-8")

        owned_span = result.lineage.sections["owned-section"].byte_span
        owned_text = candidate_bytes[owned_span[0] : owned_span[1]].decode("utf-8")
        unowned_span = result.lineage.sections["unowned-section"].byte_span
        unowned_text = candidate_bytes[unowned_span[0] : unowned_span[1]].decode("utf-8")

        self.assertNotIn("Duplicate wording appears here too.", owned_text)
        self.assertIn("Live wording stays.", owned_text)
        self.assertNotIn("e-retired", result.lineage.sections["owned-section"].entry_ids)
        self.assertIn("Duplicate wording appears here too.", unowned_text)


class TestLineageCoversEverySectionId(_GenerateCandidateFixtureMixin, unittest.TestCase):
    @covers("REQ-0.35.0-05-04")
    def test_lineage_carries_owned_entry_ids_and_byte_span_for_every_section(self) -> None:
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Owned body.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        self.assertEqual(set(result.lineage.sections), {"owned-section", "unowned-section"})
        owned = result.lineage.sections["owned-section"]
        unowned = result.lineage.sections["unowned-section"]
        self.assertTrue(owned.owned)
        self.assertEqual(owned.entry_ids, ("e-owned",))
        self.assertFalse(unowned.owned)
        self.assertEqual(unowned.entry_ids, ())
        for lineage in result.lineage.sections.values():
            self.assertIsInstance(lineage.byte_span, tuple)
            self.assertEqual(len(lineage.byte_span), 2)


class TestPerConsumerOffsetsAndRouteRefusal(_GenerateCandidateFixtureMixin, unittest.TestCase):
    @covers("REQ-0.35.0-05-05")
    def test_two_routed_consumers_get_different_offsets_and_off_route_is_refused(self) -> None:
        """Spans are computed per-candidate; an off-route consumer is refused."""
        # vendorC is deliberately given a DECLARED TEMPERATURE and (below) a
        # prior rendition, while being left OFF the route list. Round 3's
        # mutation audit found the earlier fixture could not isolate the route
        # gate: vendorC lacked a temperature, so defeating the route guard
        # still refused -- via `temperature_for` -- and the covering assertion
        # could only fail on diagnostic wording. With every other precondition
        # satisfied, the refusal is now attributable to the route gate alone.
        manifest = {
            "content_type_routes": {_GEN_OWNER: ["vendorA", "vendorB"]},
            "content_type_temperatures": {
                _GEN_OWNER: {"vendorA": "lite", "vendorB": "lite", "vendorC": "lite"},
            },
            "surface_content_types": {_GEN_SURFACE: _GEN_OWNER},
        }
        self._write_manifest(manifest)

        prior_a = "## Prefix Section\nshort\n## Shared Section\nold A content\n"
        prior_b = (
            "## Prefix Section\n"
            "a much longer prefix section body that pushes the shared section further "
            "along\n"
            "## Shared Section\nold B content\n"
        )
        sections = {"prefix-section": "unowned", "shared-section": "corpus-owned"}

        self._write_prior_rendition(_GEN_SURFACE, "vendorA", prior_a)
        self._write_prior_rendition(_GEN_SURFACE, "vendorB", prior_b)
        self._write_prior_rendition(_GEN_SURFACE, "vendorC", prior_a)

        spans_a = measure_section_spans(prior_a)
        spans_b = measure_section_spans(prior_b)
        floor = max(spans_a["prefix-section"], spans_b["prefix-section"])
        self._write_declaration(_GEN_SURFACE, sections, unowned_byte_floor=floor)

        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-shared",
                surface=_GEN_SURFACE,
                section="shared-section",
                tier="compressible",
                classification="Ambiguous",
                text="Shared corpus wording.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result_a = generate_candidate(self._root, _GEN_SURFACE, "vendorA")
        result_b = generate_candidate(self._root, _GEN_SURFACE, "vendorB")

        self.assertNotEqual(
            result_a.lineage.sections["shared-section"].byte_span,
            result_b.lineage.sections["shared-section"].byte_span,
        )

        with self.assertRaises(ValueError) as ctx:
            generate_candidate(self._root, _GEN_SURFACE, "vendorC")

        message = str(ctx.exception)
        self.assertIn(_GEN_SURFACE, message)
        self.assertIn("vendorC", message)


class TestDeterministicGeneration(_GenerateCandidateFixtureMixin, unittest.TestCase):
    @covers("REQ-0.35.0-05-08")
    def test_two_runs_produce_byte_identical_candidate_and_lineage(self) -> None:
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Deterministic wording.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result1 = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)
        result2 = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        self.assertEqual(result1.rendition.candidate_text, result2.rendition.candidate_text)
        self.assertEqual(result1.lineage, result2.lineage)


class TestGenerateCandidateEnforcesInvariantFloor(
    _GenerateCandidateFixtureMixin, unittest.TestCase
):
    """The 0-Kelvin floor binds `generate_candidate`, not only `compose` (Fix 1).

    `compose()` unconditionally calls `assert_invariant_verbatim`.
    `generate_candidate` called only `_refuse_duplicate_live_invariants`, which
    checks a DIFFERENT property (no two live invariant entries share text) --
    it never checks that every live invariant entry's text actually survives
    into the candidate. An invariant entry addressed to a section the
    declaration still marks `unowned` is never emitted (unowned sections carry
    forward from `prior_bytes` only), so if that text is not already present
    in the prior committed rendition, the candidate silently drops it.
    """

    def test_invariant_entry_addressed_to_unowned_section_is_enforced(self) -> None:
        """An invariant entry addressed to an unowned section must survive verbatim."""
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-invariant-unowned",
                surface=_GEN_SURFACE,
                section="unowned-section",
                tier="invariant",
                classification="Mechanical",
                text="This invariant wording is absent from the prior rendition.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        with self.assertRaises(ValueError) as ctx:
            generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        self.assertIn("Invariant-floor violation", str(ctx.exception))


class TestDuplicateLiveInvariantRefusal(_GenerateCandidateFixtureMixin, unittest.TestCase):
    @covers("REQ-0.35.0-05-09")
    def test_two_live_byte_identical_invariant_entries_are_refused(self) -> None:
        """Two live invariant entries sharing exact text are refused before any bytes emit."""
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-inv-1",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="invariant",
                classification="Mechanical",
                text="Duplicate invariant wording.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-inv-2",
                surface=_GEN_SURFACE,
                section="unowned-section",
                tier="invariant",
                classification="Mechanical",
                text="Duplicate invariant wording.",
                origin="test",
                ts="2026-09-07T00:00:01Z",
            ),
        )

        with self.assertRaises(ValueError) as ctx:
            generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        message = str(ctx.exception)
        self.assertIn("e-inv-1", message)
        self.assertIn("e-inv-2", message)
        self.assertIn("owned-section", message)
        self.assertIn("unowned-section", message)
        self.assertIn("gz content retire", message)


# -- GHI-flagged edge-case gap: fenced headings, empty owned sections, ------
# missing carry-forward, multibyte byte offsets (REQ-0.35.0-05-01/02) -------
#
# A post-fix independent review found these promised in the brief's
# Generation and Accounting Contract but absent from this file. Added as a
# direct repair, not new-design; no production change expected.


class TestGeneratedLineageSpansMatchActualBoundaries(
    _GenerateCandidateFixtureMixin, unittest.TestCase
):
    @covers("REQ-0.35.0-05-04")
    @covers("REQ-0.35.0-05-05")
    def test_same_roster_heading_injection_that_moves_boundaries_is_refused(self) -> None:
        """A same-roster injection that MOVES real boundaries is refused.

        Round 3 (cross-vendor adversarial review) refuted the roster-only
        check: an entry whose text carries a heading DUPLICATING an existing
        later heading, plus an unbalanced fence hiding the original, leaves the
        section-id roster byte-identical while the actual boundary moves. The
        id comparison and `assert_complete_partition` both passed, because the
        generator's own numbers stayed internally consistent -- so the lineage
        named spans belonging to a different section (REQ-04/05 false
        provenance). Reproduced on the live corpus at
        lineage (30261, 30682) vs actual (30261, 30650).
        """
        prior_text = "## Owned Section\nold body\n## Unowned Section\ncarried text\n"
        self._seed(prior_text=prior_text)
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-attack",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                # Duplicates the later heading AND opens a fence that hides it.
                text="## Unowned Section\n```",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        with self.assertRaises(ValueError) as ctx:
            generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        message = str(ctx.exception)
        self.assertIn("moved spans", message)
        self.assertIn("EXACT UTF-8 section bytes", message)

    @covers("REQ-0.35.0-05-04")
    def test_ordinary_generation_is_still_accepted(self) -> None:
        """The positive direction: a legitimate body-only entry still generates."""
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-ok",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Ordinary body text, no heading.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        candidate_bytes = result.rendition.candidate_text.encode("utf-8")
        for boundary in iter_section_boundaries(result.rendition.candidate_text):
            self.assertEqual(
                tuple(result.lineage.sections[boundary.section_id].byte_span),
                (boundary.start, boundary.end),
                "every lineage span must equal the candidate's actual boundary",
            )
        self.assertEqual(
            max(s.byte_span[1] for s in result.lineage.sections.values()),
            len(candidate_bytes),
        )


class TestGeneratedEmissionAttributionCountsOnlyEmittedEntries(
    _GenerateCandidateFixtureMixin, unittest.TestCase
):
    @covers("REQ-0.35.0-05-06")
    def test_a_compressible_entry_in_an_unowned_section_is_never_attributed(self) -> None:
        """`compressible_bytes_after` counts only entries the generator EMITTED.

        Round 3's mutation audit found the prior REQ-06 control bound to the
        EXPLICIT path's presence filter, which leaves generated emission
        attribution unaffected -- so it did not witness the generator-specific
        requirement it claimed. This binds it: a compressible entry addressed
        to an UNOWNED section is a member of the effective corpus (so it counts
        toward `before`) but is never emitted, because unowned sections carry
        forward from the prior rendition only. Attributing it would be exactly
        the substring-subtraction accounting REQ-06 retires.
        """
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Emitted body.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-unowned",
                surface=_GEN_SURFACE,
                section="unowned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Never emitted -- this section carries forward verbatim.",
                origin="test",
                ts="2026-09-07T00:00:01Z",
            ),
        )

        evidence = generate_candidate(
            self._root, _GEN_SURFACE, _GEN_CONSUMER
        ).rendition.byte_evidence

        self.assertEqual(evidence.compressible_bytes_after, len(b"Emitted body."))
        self.assertGreater(evidence.compressible_bytes_before, evidence.compressible_bytes_after)


class TestEmptyOwnedSectionRetainsHeading(_GenerateCandidateFixtureMixin, unittest.TestCase):
    @covers("REQ-0.35.0-05-01")
    def test_empty_owned_section_retains_its_heading(self) -> None:
        """An owned section with ZERO live corpus entries still emits its heading."""
        self._seed()
        # A corpus store must exist for the surface (generate_candidate fails
        # closed with no store at all), but the owned section must end up with
        # zero LIVE entries -- retire the only one addressed to it.
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned-to-retire",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Wording that will be retired.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned-tomb",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="",
                origin="test",
                ts="2026-09-07T00:00:01Z",
                retires="e-owned-to-retire",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        prior_bytes = _GEN_PRIOR_TEXT.encode("utf-8")
        boundary = next(
            b for b in iter_section_boundaries(_GEN_PRIOR_TEXT) if b.section_id == "owned-section"
        )
        newline_index = prior_bytes.find(b"\n", boundary.start, boundary.end)
        expected_heading = prior_bytes[boundary.start : newline_index + 1]

        # The "retain" claim is that the heading TEXT is present in the
        # candidate -- asserting only that the section exists in the lineage
        # would not prove that.
        self.assertIn(expected_heading.decode("utf-8"), result.rendition.candidate_text)

        lineage = result.lineage.sections["owned-section"]
        self.assertTrue(lineage.owned)
        self.assertEqual(lineage.entry_ids, ())
        span = lineage.byte_span
        actual_span_bytes = result.rendition.candidate_text.encode("utf-8")[span[0] : span[1]]
        self.assertEqual(actual_span_bytes, expected_heading)


_GEN_FENCED_PRIOR_TEXT = (
    "## Owned Section\n"
    "old body text to be replaced\n"
    "## Unowned Section\n"
    "carried text before fence\n"
    "```\n"
    "## Fake Heading Inside Fence\n"
    "```\n"
    "carried text after fence\n"
)


class TestFencedHeadingDoesNotCreateSpuriousSection(
    _GenerateCandidateFixtureMixin, unittest.TestCase
):
    @covers("REQ-0.35.0-05-02")
    def test_fenced_heading_in_prior_rendition_does_not_create_spurious_section(self) -> None:
        """A '## ' line inside a fenced code block is not a real section boundary."""
        self._seed(prior_text=_GEN_FENCED_PRIOR_TEXT)
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Owned body.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        # No section id derived from the fenced example line.
        self.assertEqual(set(result.lineage.sections), {"owned-section", "unowned-section"})

        prior_bytes = _GEN_FENCED_PRIOR_TEXT.encode("utf-8")
        boundary = next(
            b
            for b in iter_section_boundaries(_GEN_FENCED_PRIOR_TEXT)
            if b.section_id == "unowned-section"
        )
        expected = prior_bytes[boundary.start : boundary.end]
        # Sanity: the fenced bytes really are inside the enclosing section's
        # own span, independent of the ownership/generator code path.
        self.assertIn(b"```\n## Fake Heading Inside Fence\n```\n", expected)

        span = result.lineage.sections["unowned-section"].byte_span
        actual = result.rendition.candidate_text.encode("utf-8")[span[0] : span[1]]
        self.assertEqual(actual, expected)


_GEN_MULTIBYTE_PRIOR_TEXT = (
    "## Owned Section\n"
    "placeholder body to be replaced\n"
    "## Unowned Section\n"
    "carried forward text verbatim\n"
)
_MULTIBYTE_ENTRY_TEXT = "Café — a résumé note about naïve façade."


class TestMultibyteOffsetsAreByteOffsets(_GenerateCandidateFixtureMixin, unittest.TestCase):
    @covers("REQ-0.35.0-05-02")
    def test_multibyte_content_produces_byte_offsets_not_character_offsets(self) -> None:
        """Section byte_span offsets are UTF-8 BYTE offsets, never codepoint offsets."""
        self._seed(prior_text=_GEN_MULTIBYTE_PRIOR_TEXT)
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-multibyte",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text=_MULTIBYTE_ENTRY_TEXT,
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        prior_bytes = _GEN_MULTIBYTE_PRIOR_TEXT.encode("utf-8")
        boundary = next(
            b
            for b in iter_section_boundaries(_GEN_MULTIBYTE_PRIOR_TEXT)
            if b.section_id == "owned-section"
        )
        newline_index = prior_bytes.find(b"\n", boundary.start, boundary.end)
        heading_bytes = prior_bytes[boundary.start : newline_index + 1]
        body_bytes = b"\n" + _MULTIBYTE_ENTRY_TEXT.strip().encode("utf-8") + b"\n"
        expected_owned_end = len(heading_bytes) + len(body_bytes)

        # Independently prove the byte length actually diverges from the
        # codepoint length here -- otherwise a codepoint-offset regression
        # would pass this test by accident.
        char_based_end = len(heading_bytes.decode("utf-8")) + len(body_bytes.decode("utf-8"))
        self.assertNotEqual(expected_owned_end, char_based_end)

        owned_span = result.lineage.sections["owned-section"].byte_span
        unowned_span = result.lineage.sections["unowned-section"].byte_span
        self.assertEqual(owned_span[1], expected_owned_end)
        self.assertEqual(unowned_span[0], expected_owned_end)


class TestMissingCarryForwardIsNamedRefusal(_GenerateCandidateFixtureMixin, unittest.TestCase):
    def test_missing_prior_text_for_unowned_section_is_named_refusal(self) -> None:
        """A section declared 'unowned' but absent from the prior rendition is refused by name."""
        prior_text = "## Owned Section\nold body text to be replaced\n"
        # _GEN_DECL_SECTIONS still declares 'unowned-section', which this
        # prior rendition does not carry at all.
        self._seed(prior_text=prior_text)
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-owned",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Owned body.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        with self.assertRaises(ValueError) as ctx:
            generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        self.assertIn("unowned-section", str(ctx.exception))


# -- Fix 1: entry text bytes are preserved verbatim, never stripped ----------
#
# Adversary-reproduced (cross-vendor Codex tier-1 review, refuting
# OBPI-0.35.0-05-corpus-candidate-generator): `e.text.strip()` mutilated a
# compressible entry's leading indentation (breaks fenced/indented code) and
# an invariant entry's trailing Markdown hard-break spaces, while the
# invariant floor's OWN check (`assert_invariant_verbatim`) reads the
# UNSTRIPPED entry text, so a valid leading-whitespace invariant entry was
# falsely refused as an "Invariant-floor violation" -- the generator stripped
# the text it then checked for verbatim presence.


class TestGeneratedBodyPreservesEntryBytesVerbatim(
    _GenerateCandidateFixtureMixin, unittest.TestCase
):
    def test_leading_indentation_survives_into_the_candidate_verbatim(self) -> None:
        """A compressible entry's leading indentation (e.g. code inside a fence)
        must round-trip byte-exactly -- stripping it breaks fenced/indented code.
        """
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-indented",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="    code_line()",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        owned_span = result.lineage.sections["owned-section"].byte_span
        owned_bytes = result.rendition.candidate_text.encode("utf-8")[owned_span[0] : owned_span[1]]
        self.assertIn(b"    code_line()", owned_bytes)

    def test_trailing_hard_break_spaces_survive_into_the_candidate_verbatim(self) -> None:
        """An entry's trailing two-space Markdown hard-break must round-trip byte-exactly."""
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-hardbreak",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="invariant",
                classification="Mechanical",
                text="Line with a hard break.  ",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        self.assertIn("Line with a hard break.  \n", result.rendition.candidate_text)

    def test_invariant_entry_with_leading_whitespace_is_never_falsely_refused(self) -> None:
        """A leading-whitespace invariant entry must be ACCEPTED, not refused.

        Adversary-reproduced: the generator stripped the entry's text before
        emitting it, then checked the UNSTRIPPED text for verbatim presence --
        so a genuinely valid invariant entry raised "Invariant-floor violation".
        """
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-inv-indented",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="invariant",
                classification="Mechanical",
                text="    invariant wording with leading indentation",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        # Must not raise -- this is a valid candidate.
        result = generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        self.assertIn(
            "    invariant wording with leading indentation", result.rendition.candidate_text
        )


# -- Fix 2: section identity validated against corpus input AND generated ---
# output -----------------------------------------------------------------
#
# Adversary-reproduced (cross-vendor Codex tier-1 review): (a) an entry
# addressed to a section id the declaration does not carry is silently
# omitted from both text and lineage instead of failing before writing; (b)
# an effective entry whose TEXT contains a heading line injects a real H2
# into the generated candidate with no lineage record, and
# `assert_complete_partition` cannot catch it because it validates only the
# generator's own numeric byte-span assignments, never the actual rendered
# Markdown.


class TestUnknownSectionAddressIsRefusedBeforeWriting(
    _GenerateCandidateFixtureMixin, unittest.TestCase
):
    def test_entry_addressed_to_undeclared_section_id_is_refused(self) -> None:
        """An entry naming a section id the declaration does not carry fails closed."""
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-orphan",
                surface=_GEN_SURFACE,
                section="no-such-section",
                tier="compressible",
                classification="Ambiguous",
                text="Orphaned wording addressed to nothing declared.",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        with self.assertRaises(ValueError) as ctx:
            generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        message = str(ctx.exception)
        self.assertIn("e-orphan", message)
        self.assertIn("no-such-section", message)


class TestGeneratedOutputSectionRosterMustMatchLineage(
    _GenerateCandidateFixtureMixin, unittest.TestCase
):
    def test_entry_text_containing_a_heading_line_is_refused(self) -> None:
        """An entry whose text embeds a real heading line injects an untracked section.

        The lineage the generator produces must describe the ACTUAL generated
        Markdown, never merely the generator's own intent -- an embedded
        heading renders a real, un-lineaged H2 that
        `ConsumerLineage.assert_complete_partition` cannot detect because it
        only checks the numeric spans the generator itself assigned.
        """
        self._seed()
        append_entry(
            self._root,
            _GEN_SURFACE,
            CorpusEntry(
                id="e-embedded-heading",
                surface=_GEN_SURFACE,
                section="owned-section",
                tier="compressible",
                classification="Ambiguous",
                text="Intro\n## Unexpected New Section\nNew policy",
                origin="test",
                ts="2026-09-07T00:00:00Z",
            ),
        )

        with self.assertRaises(ValueError) as ctx:
            generate_candidate(self._root, _GEN_SURFACE, _GEN_CONSUMER)

        message = str(ctx.exception)
        self.assertIn("unexpected-new-section", message)
