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

from gzkit.content.corpus_store import load_corpus
from gzkit.content.models import AgentContract, Corpus, CorpusEntry, Pillar
from gzkit.content.models.corpus import (
    BASELINE_IDENTITY_FIELDS,
    POST_BASELINE_IDENTITY_FIELDS,
    effective_corpus,
)
from gzkit.content.rendition_store import corpus_fingerprint
from gzkit.content.tier_policy import assert_invariant_verbatim, invariant_entries
from gzkit.traceability import covers

#: The corpus fingerprint at the pre-OBPI-0.35.0-01 baseline (REQ-0.35.0-01-01),
#: asserted against the PRODUCTION `corpus_fingerprint()` over the real on-disk
#: corpus below — so this REQ's covering test fails if the production hash
#: algorithm, encoding, or normalization ever changes. The additive `supersedes`
#: field must never perturb this — a value in a Markdown doc is illustrative,
#: never authoritative (`.claude/rules/governance-core.md`), so this constant is
#: the load-bearing assertion, not the OBPI brief's stale "51 rows" table.
_PRE_OBPI_0_35_0_01_FINGERPRINT = "8459d30b0fbacc8e5e33da8dd391f9355daef6ac1912d5c175f53888bd3f92de"

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "src" / "gzkit" / "schemas" / "corpus_entry.json"
)

#: Project root, derived the same way as `_SCHEMA_PATH` above rather than depending
#: on the process working directory — a test that only passes when run from the
#: repo root is fragile.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


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
    return CorpusEntry(**base)


def _jsonl(*entries: CorpusEntry) -> str:
    """Serialize *entries* to JSONL exactly as the on-disk store holds them.

    The fold algebra is validated at LOAD time (brief Algebra 2/3/7 — "a
    load-time ValueError"), never at construction, so a negative case has to
    arrive through ``Corpus.loads`` the way ``corpus_store.load_corpus`` feeds
    it. Building the malformed corpus in memory first is deliberate: it proves
    construction stays permissive, which is what keeps Algebra 9 satisfiable
    (a folded view legitimately carries a `supersedes` row whose target the
    fold just removed).
    """
    return Corpus(entries=entries).dumps()


def _folded_ids(*entries: CorpusEntry) -> list[str]:
    """Load *entries* through the real load path and return the folded ids, in order.

    Going through ``Corpus.loads`` rather than constructing the corpus directly
    means every fold fixture is also asserted to be LEGAL under Algebra 2/3/7 —
    a fold assertion over a shape the loader would refuse proves nothing about
    the corpus an operator can actually have on disk.
    """
    return [e.id for e in effective_corpus(Corpus.loads(_jsonl(*entries))).entries]


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
    def test_model_field_set_is_exactly_the_declared_fields(self) -> None:
        """The entry carries exactly its declared fields — nothing inherited.

        The ten ADR-0.0.37-18 address/provenance fields, plus ``retires`` (the
        GHI #635 append-only retirement pointer) and ``supersedes`` (the
        OBPI-0.35.0-01 replace-and-retire pointer). The fence is against fields
        arriving by inheritance, which is why it asserts set equality rather
        than a count.
        """
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
                "retires",
                "supersedes",
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
            e.text = "mutated"  # ty: ignore[invalid-assignment]

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


class TestDerivationIdentity(unittest.TestCase):
    """The corpus derivation identity must survive additive schema evolution (GHI #635).

    ``rendition_store.corpus_fingerprint`` hashes ``Corpus.dumps()``, so that
    string IS the identity the committed renditions' provenance is proven
    against. Adding ``retires`` alone re-fingerprinted every surface while the
    .jsonl on disk stayed byte-identical, because every row began emitting
    ``"retires":null`` — costing a corpus-attested recompose for a semantically empty
    change. These tests pin the rule that makes additive evolution possible,
    and the fence that stops the next field from re-opening the trap silently.
    """

    def test_every_field_is_classified(self) -> None:
        """Adding a field to CorpusEntry must be a decision, not a silent re-fingerprint.

        This is the fence. A new field that is in neither tuple fails here, which
        is the prompt to choose: POST_BASELINE (inert at default, the safe
        default for anything additive) or BASELINE (identity-bearing always —
        which re-fingerprints every committed rendition and needs an operator
        recompose, so it is almost never right after the baseline).
        """
        classified = set(BASELINE_IDENTITY_FIELDS) | set(POST_BASELINE_IDENTITY_FIELDS)
        self.assertEqual(
            set(CorpusEntry.model_fields),
            classified,
            "unclassified CorpusEntry field(s): "
            f"{sorted(set(CorpusEntry.model_fields) - classified)}. Add to "
            "POST_BASELINE_IDENTITY_FIELDS (inert while default) unless the field "
            "genuinely belongs to the derivation identity for every row.",
        )

    def test_baseline_field_order_is_frozen(self) -> None:
        """Reordering baseline fields would re-fingerprint every committed rendition.

        The digest is over a JSON serialization whose key order follows field
        declaration order, so this tuple is a wire format, not a preference.
        """
        self.assertEqual(
            BASELINE_IDENTITY_FIELDS,
            (
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
            ),
        )

    def test_post_baseline_field_at_default_is_inert(self) -> None:
        """A row that predates a post-baseline field serializes as if it never existed."""
        self.assertNotIn("retires", Corpus(entries=(_entry(),)).dumps())

    def test_post_baseline_field_in_use_is_identity_bearing(self) -> None:
        """The converse — the inertness rule must not swallow real canon drift.

        A row that actually retires something changed what canon requires, so it
        SHOULD perturb the digest and fire the freshness gate.
        """
        self.assertIn("retires", Corpus(entries=(_entry(id="c2", retires="c1"),)).dumps())

    def test_baseline_optional_fields_still_serialize_when_none(self) -> None:
        """`anchor`/`witness` predate the rule and are emitted as null.

        They are baseline-identity fields, so the inertness rule must NOT reach
        them — doing so would re-fingerprint every existing row, the exact
        failure this whole mechanism exists to prevent.
        """
        dumped = Corpus(entries=(_entry(),)).dumps()
        self.assertIn('"anchor":null', dumped)
        self.assertIn('"witness":null', dumped)


class TestSupersedesAdditive(unittest.TestCase):
    """REQ-0.35.0-01-01: `supersedes` is additive — a tombstone-free row must

    round-trip byte-identically and the real on-disk corpus fingerprint must
    survive the field's addition unchanged (OBPI-0.35.0-01).
    """

    @covers("REQ-0.35.0-01-01")
    def test_supersedes_field_exists_and_defaults_to_none(self) -> None:
        """`supersedes` is a declared field on CorpusEntry, defaulting to None."""
        self.assertIn("supersedes", CorpusEntry.model_fields)
        self.assertIsNone(_entry().supersedes)

    @covers("REQ-0.35.0-01-01")
    def test_entry_without_tombstone_fields_round_trips_byte_identically(self) -> None:
        """A tombstone-free row's serialized bytes are unaffected by the new field."""
        c = Corpus().append(_entry(id="c1"))
        dumped = c.dumps()
        self.assertNotIn("supersedes", dumped)
        self.assertEqual(Corpus.loads(dumped).dumps(), dumped)

    @covers("REQ-0.35.0-01-01")
    def test_real_on_disk_corpus_fingerprint_is_unchanged(self) -> None:
        """The additive field must not re-fingerprint the real, committed corpus.

        Asserts against the PRODUCTION `corpus_fingerprint()` over the real,
        on-disk corpus — this fails if the production hash algorithm, encoding,
        or normalization ever changes, which a local reimplementation would not.
        """
        self.assertEqual(
            corpus_fingerprint(load_corpus(_PROJECT_ROOT, "AGENTS.md")),
            _PRE_OBPI_0_35_0_01_FINGERPRINT,
        )


class TestLiveEntryWithText(unittest.TestCase):
    """Duplicate-text detection over the live (non-retired) set — GHI #862.

    `retired_ids` already tells the store which rows stopped binding. The
    duplicate question has to be asked against the same set: a text whose
    only prior copy is retired is a re-capture, which is exactly the
    amendment path (retire, then remember the corrected wording).
    """

    def test_finds_a_live_entry_carrying_the_same_text(self):
        """Two live rows with one text is the state GHI #862 measured 7 times."""
        corpus = Corpus(entries=(_entry(id="c1", text="Never create feature branches."),))
        found = corpus.live_entry_with_text("Never create feature branches.")
        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.id, "c1")

    def test_ignores_a_retired_entry(self):
        """A retired copy must not block re-capture.

        This is the load-bearing case: amending canon means retiring the old
        wording and remembering the new one. If retired rows counted, the
        second half of that workflow would be refused.
        """
        corpus = Corpus(
            entries=(
                _entry(id="c1", text="old wording"),
                _entry(id="r1", text="superseded", retires="c1", tier="compressible"),
            )
        )
        self.assertIsNone(corpus.live_entry_with_text("old wording"))

    def test_returns_none_when_no_entry_carries_the_text(self):
        corpus = Corpus(entries=(_entry(id="c1", text="something else"),))
        self.assertIsNone(corpus.live_entry_with_text("not present"))

    def test_matches_on_exact_text_only(self):
        """Byte-identical is the predicate.

        The 7 pairs GHI #862 found were byte-identical, which is why nothing
        fired; GHI #635's pair differed by quote style and broke composition
        loudly. Near-miss detection is a different problem and would refuse
        legitimate rewordings, so it is deliberately out of scope.
        """
        corpus = Corpus(entries=(_entry(id="c1", text="Work directly on main."),))
        self.assertIsNone(corpus.live_entry_with_text("Work directly on main"))


class TestTombstoneTargetAlgebra(unittest.TestCase):
    """REQ-0.35.0-01-02: Algebra 2 (targets) and Algebra 3 (exclusivity) fail closed on load.

    Both clauses exist to keep the reverse pass of Algebra 5 total: it resolves
    every tombstone before the row it targets ONLY because every tombstone
    strictly follows its target. A forward, self, or unknown reference breaks
    that premise, and an entry populating both pointers has no single role
    under Algebra 4. Each must be refused where the corpus enters the process,
    naming the offending row so an operator can find it in a 79-line append log.
    """

    def _load_error(self, *entries: CorpusEntry) -> str:
        with self.assertRaises(ValueError) as caught:
            Corpus.loads(_jsonl(*entries))
        return str(caught.exception)

    @covers("REQ-0.35.0-01-02")
    def test_forward_reference_is_refused(self) -> None:
        """A tombstone naming a LATER row breaks the reverse pass's ordering premise."""
        message = self._load_error(
            _entry(id="tomb-early", retires="row-late", tier="compressible"),
            _entry(id="row-late"),
        )
        self.assertIn("tomb-early", message)

    @covers("REQ-0.35.0-01-02")
    def test_self_reference_is_refused(self) -> None:
        """A row retiring itself has no fixed point under Algebra 5 and is refused."""
        message = self._load_error(_entry(id="row-ouroboros", retires="row-ouroboros"))
        self.assertIn("row-ouroboros", message)

    @covers("REQ-0.35.0-01-02")
    def test_unknown_target_is_refused(self) -> None:
        """A tombstone naming an id no row carries retires nothing — a silent no-op otherwise."""
        message = self._load_error(
            _entry(id="row-present"),
            _entry(id="tomb-dangling", retires="row-never-appended", tier="compressible"),
        )
        self.assertIn("tomb-dangling", message)

    @covers("REQ-0.35.0-01-02")
    def test_populating_both_pointers_is_refused(self) -> None:
        """Algebra 3: `retires` and `supersedes` assign contradictory roles (Algebra 4)."""
        message = self._load_error(
            _entry(id="row-first"),
            _entry(id="row-second"),
            _entry(id="tomb-ambiguous", retires="row-first", supersedes="row-second"),
        )
        self.assertIn("tomb-ambiguous", message)

    @covers("REQ-0.35.0-01-02")
    def test_supersedes_obeys_the_same_target_rule_as_retires(self) -> None:
        """Algebra 2 covers BOTH pointers; a `supersedes`-only check is half a fence."""
        message = self._load_error(
            _entry(id="repl-early", supersedes="row-late"),
            _entry(id="row-late"),
        )
        self.assertIn("repl-early", message)

    @covers("REQ-0.35.0-01-02")
    def test_the_real_on_disk_corpus_still_loads(self) -> None:
        """The fence must not refuse the append log it was written to govern.

        A validator that rejects the live corpus would take every consumer
        offline, so the negative cases above are only half the requirement.
        """
        self.assertGreater(len(load_corpus(_PROJECT_ROOT, "AGENTS.md").entries), 0)


class TestEffectiveCorpusPureTombstone(unittest.TestCase):
    """REQ-0.35.0-01-03: a retired row AND its pure tombstone both leave the view.

    Algebra 8 removes the retired row; Algebra 4 removes the tombstone itself,
    because a `retires` row is a marker and contributes no text. Dropping only
    the first half would publish the retraction row's own text as canon — the
    retirement would read as an edit that ADDED a line.
    """

    @covers("REQ-0.35.0-01-03")
    def test_retired_row_and_its_tombstone_are_both_absent(self) -> None:
        """`[X, T1(retires=X)]` folds to an EMPTY effective view."""
        self.assertEqual(
            _folded_ids(
                _entry(id="row-x", text="old canon"),
                _entry(id="tomb-1", retires="row-x", tier="compressible"),
            ),
            [],
        )

    @covers("REQ-0.35.0-01-03")
    def test_an_untouched_row_survives_alongside_the_retirement(self) -> None:
        """The fold removes the retired pair and NOTHING else.

        Without a bystander the empty-view assertion above is equally satisfied
        by a fold that drops every row, which would silently empty the whole
        invariant floor.
        """
        self.assertEqual(
            _folded_ids(
                _entry(id="row-x", text="old canon"),
                _entry(id="tomb-1", retires="row-x", tier="compressible"),
                _entry(id="row-y", text="unrelated canon"),
            ),
            ["row-y"],
        )


class TestLivenessRefusesAnUnresolvableTombstone(unittest.TestCase):
    """REQ-0.35.0-01-03: an unresolvable tombstone is REFUSED, never guessed at.

    `_liveness`'s reverse pass reads `live[t]` for every tombstone `t` targeting
    the row it is resolving. Algebra 2 guarantees `t` is already resolved — a
    tombstone strictly follows its target — so an unresolved `t` means the
    caller handed over a log Algebra 2 forbids: a forward reference, or a
    duplicate id (an UNENFORCED premise, GHI #874).

    The helper used to substitute a `True` default there and call itself total.
    A cross-vendor adversarial review of this OBPI showed that default does not
    merely fail safe, it fails WRONG — it computes an answer the pinned
    recurrence does not give (see the regression case below). Refusing is the
    only honest answer: the input is outside the domain the algebra is defined
    over, and inventing a liveness value there is how retired canon gets
    republished behind a green gate.
    """

    @covers("REQ-0.35.0-01-03")
    def test_an_out_of_order_tombstone_raises_naming_both_ids(self) -> None:
        """`Corpus(entries=(t1, x))` — tombstone BEFORE its target.

        This shape is illegal under `Corpus.loads` (Algebra 2), so it is built
        directly, in memory, the ONLY way to reach the unresolved branch. The
        message must name both the unresolved tombstone and the entry it
        targets: in an append log that only ever grows, an operator needs the
        two ids to find the rows.
        """
        x = _entry(id="x", text="canon that must stay retired")
        t1 = _entry(id="t1", retires="x", tier="compressible")
        corpus = Corpus(entries=(t1, x))

        with self.assertRaises(ValueError) as ctx:
            effective_corpus(corpus)

        message = str(ctx.exception)
        self.assertIn("t1", message)
        self.assertIn("x", message)

    @covers("REQ-0.35.0-01-03")
    def test_the_adversary_sequence_raises_rather_than_folding_to_an_empty_view(self) -> None:
        """`[T1(retires=X), X, T2(retires=T1)]` — the cross-vendor adversary's case.

        Recorded verbatim from that review, because it is what falsified the
        "the default fails safe" reading two same-vendor reviewers had passed:

            sequence:  [('t1','x'), ('x',None), ('t2','t1')]
            _liveness: {'t2': True, 'x': False, 't1': False}
            effective: []
            algebraic live:      {'t2': True, 't1': False, 'x': True}
            algebraic effective: ['x']

        The pinned recurrence gives live(t2)=True, live(t1)=not live(t2)=False,
        live(x)=not live(t1)=True. The old default resolved `x` before `t1` and
        kept `x` retired — not a safe fallback but a DIFFERENT answer, invented
        where the algebra gives one. `[]` and `['x']` are both wrong to return
        here; the only correct behavior is to refuse.
        """
        corpus = Corpus(
            entries=(
                _entry(id="t1", retires="x", tier="compressible"),
                _entry(id="x", text="canon the algebra says is live"),
                _entry(id="t2", retires="t1", tier="compressible"),
            )
        )

        with self.assertRaises(ValueError):
            effective_corpus(corpus)


class TestEffectiveCorpusUnRetirement(unittest.TestCase):
    """REQ-0.35.0-01-04: retiring a tombstone brings its target back (Algebra 5 and 6).

    This is the clause the flat `retired_ids()` stand-in cannot express. Flatly,
    `{e.retires for e in entries}` over `[X, T1(retires=X), T2(retires=T1)]` is
    `{X, T1}` — X stays retired FOREVER, and the un-retirement fails silently.
    Liveness has to be evaluated last-to-first so T2 is resolved before T1 is
    read, and T1 before X. The store has no delete path, so this is the ONLY
    way a retirement can ever be undone.
    """

    def _un_retirement_log(self) -> tuple[CorpusEntry, ...]:
        """`[X, T1(retires=X), T2(retires=T1)]` — the canonical un-retirement shape."""
        return (
            _entry(id="row-x", text="canon that came back"),
            _entry(id="tomb-1", retires="row-x", tier="compressible"),
            _entry(id="tomb-2", retires="tomb-1", tier="compressible"),
        )

    @covers("REQ-0.35.0-01-04")
    def test_retiring_the_tombstone_makes_its_target_live_again(self) -> None:
        """X is LIVE again, and neither tombstone appears in the effective view."""
        self.assertEqual(_folded_ids(*self._un_retirement_log()), ["row-x"])

    @covers("REQ-0.35.0-01-04")
    def test_all_three_rows_remain_in_the_raw_log(self) -> None:
        """Retirement history is PRESERVED, never overwritten.

        The append log is the audit trail: it must still show that X was retired
        and then restored. A fold that achieved `["row-x"]` by dropping rows from
        the log would satisfy the assertion above and destroy the record.
        """
        raw = Corpus.loads(_jsonl(*self._un_retirement_log()))
        self.assertEqual(len(raw.entries), 3)
        self.assertEqual(
            [e.id for e in raw.entries],
            ["row-x", "tomb-1", "tomb-2"],
        )

    @covers("REQ-0.35.0-01-04")
    def test_a_fourth_row_can_retire_the_restored_entry_again(self) -> None:
        """The chain keeps alternating — liveness is a fold, not a one-shot toggle.

        `[X, T1, T2(retires=T1), T3(retires=X)]`: T3 is live, so X is retired
        again. A reverse pass that stopped at the first resolved tombstone, or a
        parity trick over the chain length, would get this wrong.
        """
        self.assertEqual(
            _folded_ids(
                *self._un_retirement_log(),
                _entry(id="tomb-3", retires="row-x", tier="compressible"),
            ),
            [],
        )


class TestEffectiveCorpusSupersedes(unittest.TestCase):
    """REQ-0.35.0-01-05: a `supersedes` row retires its target AND stays (Algebra 4).

    This is the role asymmetry the fold turns on. Both pointers register a
    tombstone edge under Algebra 5, so both remove their target. Only `retires`
    additionally suppresses the row's OWN text: it is a marker. `supersedes` is
    a replacement — the corrected wording IS that row, so dropping it would
    delete the amendment and leave canon with a hole.
    """

    @covers("REQ-0.35.0-01-05")
    def test_the_replacement_row_survives_and_its_target_does_not(self) -> None:
        """`[X, S1(supersedes=X)]` folds to `[S1]`."""
        self.assertEqual(
            _folded_ids(
                _entry(id="row-x", text="the old wording"),
                _entry(id="repl-1", supersedes="row-x", text="the corrected wording"),
            ),
            ["repl-1"],
        )

    @covers("REQ-0.35.0-01-05")
    def test_the_corrected_text_is_what_the_effective_view_carries(self) -> None:
        """The point of a replacement is its TEXT, not its id.

        An id-only assertion would pass against a fold that kept the row but
        published the retired wording, which is the resurrect-retired-canon
        failure this ADR ranks worst.
        """
        folded = effective_corpus(
            Corpus.loads(
                _jsonl(
                    _entry(id="row-x", text="the old wording"),
                    _entry(id="repl-1", supersedes="row-x", text="the corrected wording"),
                )
            )
        )
        self.assertEqual([e.text for e in folded.entries], ["the corrected wording"])

    @covers("REQ-0.35.0-01-05")
    def test_the_same_shape_with_retires_drops_both_rows(self) -> None:
        """The contrast that isolates the asymmetry to the POINTER, not the shape.

        Identical two-row log, identical edge, one field changed: `retires`
        folds to nothing, `supersedes` folds to the replacement. A fold that
        treated the two pointers alike would fail exactly one of this pair.
        """
        self.assertEqual(
            _folded_ids(
                _entry(id="row-x", text="the old wording"),
                _entry(
                    id="repl-1",
                    retires="row-x",
                    text="the corrected wording",
                    tier="compressible",
                ),
            ),
            [],
        )

    @covers("REQ-0.35.0-01-05")
    def test_superseding_a_replacement_restores_the_original_row(self) -> None:
        """A `supersedes` edge is REVOCABLE, exactly like a `retires` edge (Algebra 5 + 6).

        `[X, S1(supersedes=X), S2(supersedes=S1)]` folds to `[X, S2]`, NOT to
        `[S2]`. The reverse pass reads `live(X) = not any(live(t) for t
        targeting X)`; S2 kills S1, so S1's retirement of X is itself undone and
        X returns. That is not a quirk of this implementation — it is Algebra 6's
        stated mechanism ("retiring the tombstone makes its target live again")
        applied through D2's "BOTH `retires` and `supersedes` register a
        tombstone edge."

        This test asserts the PINNED algebra, not the author's intuition. The
        intuitive answer is `[S2]` — an amendment of an amendment should surely
        leave only the newest wording — and encoding that would have been
        choosing the algebra at implementation time, which brief requirement 3
        explicitly refuses. It is pinned here rather than left latent because
        the consequence is sharp and reachable (amend an amendment and the
        original wording returns to canon), and a REQ-05 suite that tested only
        the one-link case would have hidden it entirely.
        """
        self.assertEqual(
            _folded_ids(
                _entry(id="row-x", text="first wording"),
                _entry(id="repl-1", supersedes="row-x", text="second wording"),
                _entry(id="repl-2", supersedes="repl-1", text="third wording"),
            ),
            ["row-x", "repl-2"],
        )


class TestNoSilentDoubleRetire(unittest.TestCase):
    """REQ-0.35.0-01-06: at most one LIVE tombstone may target an entry (Algebra 7).

    Without this clause, `[X, T1(retires=X), T2(retires=X)]` folds X back to
    LIVE — `live(X) = not any(live(T1), live(T2))` is false, but an operator who
    retired the same row twice meant "retired", not "restored". Algebra 7 refuses
    the shape at load rather than letting a double-retire be silently read as an
    un-retirement.

    The clause is about LIVENESS, not arity: a second tombstone is perfectly
    legal once its predecessor has itself been retired, because that is the
    retire -> un-retire -> retire-again cycle Algebra 6 opens.
    """

    @covers("REQ-0.35.0-01-06")
    def test_two_live_tombstones_on_one_target_are_refused(self) -> None:
        """The load fails, naming the second tombstone."""
        with self.assertRaises(ValueError) as caught:
            Corpus.loads(
                _jsonl(
                    _entry(id="row-x"),
                    _entry(id="tomb-1", retires="row-x", tier="compressible"),
                    _entry(id="tomb-2", retires="row-x", tier="compressible"),
                )
            )
        self.assertIn("tomb-2", str(caught.exception))

    @covers("REQ-0.35.0-01-06")
    def test_a_live_retires_and_a_live_supersedes_on_one_target_are_refused(self) -> None:
        """Algebra 7 counts tombstone EDGES, so a mixed pair is the same violation.

        `[X, T1(retires=X), S1(supersedes=X)]` is two live tombstones on X. A
        check that only looked at `retires` would admit it and then fold X back
        to live — the double-retire-read-as-un-retire failure, through the door
        the narrower check left open.
        """
        with self.assertRaises(ValueError) as caught:
            Corpus.loads(
                _jsonl(
                    _entry(id="row-x"),
                    _entry(id="tomb-1", retires="row-x", tier="compressible"),
                    _entry(id="repl-1", supersedes="row-x"),
                )
            )
        self.assertIn("repl-1", str(caught.exception))

    @covers("REQ-0.35.0-01-06")
    def test_a_second_tombstone_is_legal_once_its_predecessor_is_retired(self) -> None:
        """THE CONTRAST CASE — this is what makes the check about liveness, not counting.

        `[X, T1(retires=X), T2(retires=T1), T3(retires=X)]` has TWO tombstones
        targeting X, but T1 is dead, so only T3 is live. This is retirement
        after an un-retirement, and it must load. A naive "count tombstones per
        target" implementation passes the two tests above and wrongly refuses
        this one, permanently closing the re-retirement path.
        """
        Corpus.loads(
            _jsonl(
                _entry(id="row-x"),
                _entry(id="tomb-1", retires="row-x", tier="compressible"),
                _entry(id="tomb-2", retires="tomb-1", tier="compressible"),
                _entry(id="tomb-3", retires="row-x", tier="compressible"),
            )
        )  # must not raise

    @covers("REQ-0.35.0-01-06")
    def test_the_legal_re_retirement_folds_the_target_back_out(self) -> None:
        """Loading it is half the requirement; it must also mean what it says.

        Accepting the shape and then folding X back into the effective view
        would be the resurrect-retired-canon failure with a GREEN gate over it.
        """
        self.assertEqual(
            _folded_ids(
                _entry(id="row-x"),
                _entry(id="tomb-1", retires="row-x", tier="compressible"),
                _entry(id="tomb-2", retires="tomb-1", tier="compressible"),
                _entry(id="tomb-3", retires="row-x", tier="compressible"),
            ),
            [],
        )


class TestEffectiveCorpusIdempotenceAndOrder(unittest.TestCase):
    """REQ-0.35.0-01-07: the fold is idempotent and preserves append order (Algebra 8 and 9).

    Idempotence is what makes the effective view safe to pass around: a consumer
    that folds an already-folded corpus must not get a different answer, or the
    "which view am I holding" question becomes load-bearing at every call site.

    It is also the clause that fixes WHERE the algebra is validated. A folded
    view legitimately carries a `supersedes` row whose target the fold just
    removed, so a `Corpus` model-validator — or any re-validation inside
    `effective_corpus` — would raise "unknown target" on the second application.
    Algebra 2 and Algebra 9 would contradict each other directly. Validation
    therefore lives at the `Corpus.loads` boundary, and the projection is pure.
    """

    def _dangling_supersedes_view(self) -> Corpus:
        """Fold `[X, S1(supersedes=X)]` — the output keeps S1, whose target is gone."""
        return effective_corpus(
            Corpus.loads(
                _jsonl(
                    _entry(id="row-x", text="the old wording"),
                    _entry(id="repl-1", supersedes="row-x", text="the corrected wording"),
                )
            )
        )

    @covers("REQ-0.35.0-01-07")
    def test_the_folded_view_really_does_carry_a_dangling_supersedes_row(self) -> None:
        """The PREMISE of the idempotence case below, asserted rather than assumed.

        If the fold ever stopped emitting the replacement row, or stopped
        removing its target, the idempotence assertion would still pass while
        testing a shape that no longer exercises the D1 hazard at all — a test
        that quietly stops testing what it was written for.
        """
        folded = self._dangling_supersedes_view()
        surviving = [e for e in folded.entries if e.supersedes is not None]
        self.assertEqual([e.id for e in surviving], ["repl-1"])
        self.assertNotIn("row-x", [e.id for e in folded.entries])
        self.assertEqual(surviving[0].supersedes, "row-x")

    @covers("REQ-0.35.0-01-07")
    def test_a_dangling_supersedes_target_is_not_an_unresolved_tombstone(self) -> None:
        """A DANGLING TARGET must never raise; only an UNRESOLVED TOMBSTONE does.

        This fence exists to stop the refusal in `_liveness` from being
        "simplified" into one that also rejects a folded view, which would
        break Algebra 9 outright. The two states look alike and are not:

        - Dangling target — `[S1(supersedes=X)]` with X gone. `edges` is
          `{"X": ["S1"]}`. The reverse pass iterates ENTRIES and looks up
          `edges.get(entry.id)`, so it asks for `edges.get("S1")` and never
          consults the key `"X"` at all. Nothing is read; nothing is unknown.
        - Unresolved tombstone — an id inside an edge LIST that the reverse
          pass has not assigned yet. That value IS read, and it is the one
          that cannot be invented.

        A refusal keyed on "is every edge key an entry" would fire on the
        first bullet and take the idempotence clause with it.
        """
        folded = self._dangling_supersedes_view()
        self.assertEqual([e.id for e in folded.entries], ["repl-1"])
        self.assertEqual(folded.entries[0].supersedes, "row-x")
        self.assertIsNone(folded.entry("row-x"))

        self.assertEqual(effective_corpus(folded), folded)
        self.assertEqual(folded.retired_ids(), frozenset())

    @covers("REQ-0.35.0-01-07")
    def test_folding_a_dangling_supersedes_view_again_is_a_no_op(self) -> None:
        """Algebra 9 over exactly the shape Algebra 2 would refuse at load."""
        once = self._dangling_supersedes_view()
        self.assertEqual(effective_corpus(once), once)

    @covers("REQ-0.35.0-01-07")
    def test_folding_an_un_retirement_view_again_is_a_no_op(self) -> None:
        """The restored row must not be re-retired by a second pass.

        `[X, T1(retires=X), T2(retires=T1)]` folds to `[X]`; the tombstones that
        made X live are gone from that view, so a fold that recomputed liveness
        from a stale assumption would drop X on the second application.
        """
        once = effective_corpus(
            Corpus.loads(
                _jsonl(
                    _entry(id="row-x"),
                    _entry(id="tomb-1", retires="row-x", tier="compressible"),
                    _entry(id="tomb-2", retires="tomb-1", tier="compressible"),
                )
            )
        )
        self.assertEqual([e.id for e in once.entries], ["row-x"])
        self.assertEqual(effective_corpus(once), once)

    @covers("REQ-0.35.0-01-07")
    def test_entry_order_is_append_order_not_a_reversed_or_sorted_order(self) -> None:
        """Algebra 8 projects "in append order" — the reverse pass is an implementation detail.

        Liveness is computed LAST to FIRST, so a fold that emitted rows as it
        resolved them would hand back a reversed view. `ts` is provenance and
        never sequence (Algebra 1), so the ids here are deliberately NOT in
        alphabetical or timestamp order: a sorted result would fail this.
        """
        self.assertEqual(
            _folded_ids(
                _entry(id="zulu", ts="2026-01-03T00:00:00Z"),
                _entry(id="alpha", ts="2026-01-01T00:00:00Z"),
                _entry(id="tomb-1", retires="alpha", tier="compressible"),
                _entry(id="mike", ts="2026-01-02T00:00:00Z"),
            ),
            ["zulu", "mike"],
        )

    @covers("REQ-0.35.0-01-07")
    def test_the_real_on_disk_corpus_folds_idempotently(self) -> None:
        """Algebra 9 on the corpus that actually ships, not only on fixtures.

        The live append log carries real tombstones, so this exercises the fold
        against the shape an operator has on disk today.
        """
        raw = load_corpus(_PROJECT_ROOT, "AGENTS.md")
        once = effective_corpus(raw)
        self.assertEqual(effective_corpus(once), once)
        self.assertLess(len(once.entries), len(raw.entries))

    @covers("REQ-0.35.0-01-07")
    def test_the_fold_never_mutates_the_raw_log(self) -> None:
        """The append log is the audit trail; the projection is a pure read of it."""
        raw = Corpus.loads(
            _jsonl(
                _entry(id="row-x"),
                _entry(id="tomb-1", retires="row-x", tier="compressible"),
            )
        )
        before = raw.dumps()
        effective_corpus(raw)
        self.assertEqual(raw.dumps(), before)
        self.assertEqual([e.id for e in raw.entries], ["row-x", "tomb-1"])


class TestInvariantFloorRoutesThroughTheFold(unittest.TestCase):
    """REQ-0.35.0-01-08: `tier_policy.invariant_entries()` reads the fold.

    Repointed off the flat `retired_ids()` stand-in (D3, OBPI-0.35.0-01):
    retirement shrinking the floor already worked under the flat form, but
    un-retirement (Algebra 6) restoring an entry to the floor never did — a
    flat `{e.retires for e in entries}` set only ever grows, so once
    `inv-x` was named by a tombstone it stayed off the floor FOREVER, even
    after that tombstone was itself retired. This is the exact defect the
    repoint exists to fix.
    """

    @covers("REQ-0.35.0-01-08")
    def test_retired_invariant_entry_is_absent_from_the_floor(self) -> None:
        x = _entry(id="inv-x", tier="invariant", text="doctrine that gets retired")
        t1 = _entry(id="t1", retires="inv-x", tier="compressible")
        corpus = Corpus.loads(_jsonl(x, t1))

        floor = invariant_entries(corpus)

        self.assertNotIn("inv-x", [e.id for e in floor])

    @covers("REQ-0.35.0-01-08")
    def test_retired_invariant_text_no_longer_binds_a_rendition(self) -> None:
        """The REQ's actual wording, asserted directly rather than assumed.

        Omitting `inv-x` from `invariant_entries()` is only half the
        requirement; `assert_invariant_verbatim` must actually stop demanding
        its text be present in a candidate rendition.
        """
        x = _entry(id="inv-x", tier="invariant", text="doctrine that gets retired")
        t1 = _entry(id="t1", retires="inv-x", tier="compressible")
        corpus = Corpus.loads(_jsonl(x, t1))

        assert_invariant_verbatim(corpus, "a rendition mentioning neither entry")  # must not raise

    @covers("REQ-0.35.0-01-08")
    def test_un_retirement_puts_the_invariant_back_on_the_floor(self) -> None:
        """Algebra 6: `[inv X, T1(retires=X), T2(retires=T1)]` restores X.

        This is the Algebra-6 defect the flat `retired_ids()` stand-in
        carried and the whole reason this repoint exists: a flat set can only
        grow, so it would report `inv-x` retired forever. If this test passes
        against the PRE-repoint `invariant_entries()`, it is not asserting
        what REQ-08 requires (verified by hand against the flat form: it
        reports `inv-x` absent, and this `assertIn` fails).
        """
        x = _entry(id="inv-x", tier="invariant", text="doctrine that comes back")
        t1 = _entry(id="t1", retires="inv-x", tier="compressible")
        t2 = _entry(id="t2", retires="t1", tier="compressible")
        corpus = Corpus.loads(_jsonl(x, t1, t2))

        floor = invariant_entries(corpus)

        self.assertIn("inv-x", [e.id for e in floor])

    @covers("REQ-0.35.0-01-08")
    def test_the_real_on_disk_corpus_still_yields_a_floor_of_exactly_54(self) -> None:
        """Regression: the repoint must not move the measured floor.

        Measured 2026-08-24: 79 raw rows fold to 55; all 12 tombstones are
        `compressible` tier, so the fold does not move the invariant floor.
        Asserted against `load_corpus`, never a hardcoded '51 rows' table --
        a value in a Markdown doc is illustrative, never authoritative
        (`.claude/rules/governance-core.md`).
        """
        corpus = load_corpus(_PROJECT_ROOT, "AGENTS.md")
        self.assertEqual(len(invariant_entries(corpus)), 54)


class TestRetiredIdsAndLiveEntryWithTextUnderUnRetirement(unittest.TestCase):
    """REQ-0.35.0-01-08: `retired_ids()` and `live_entry_with_text()` read the fold.

    `tier_policy.invariant_entries()` already has a direct un-retirement
    witness (`TestInvariantFloorRoutesThroughTheFold`). These two methods were
    repointed onto the SAME shared `_liveness`/`effective_corpus` fold (D3),
    but until now nothing exercised an Algebra-6 chain against either of them
    directly — both were proven only transitively, through the shared helper's
    own exhaustive tests. That is a different claim: a future edit could
    revert either method to a flat `{e.retires for e in entries}` scan and
    every existing test would stay green, because the shared helper being
    correct says nothing about whether these wrappers still call it. These two
    tests close that gap.
    """

    def _un_retirement_chain(self, *, x_text: str) -> tuple[CorpusEntry, ...]:
        """`[X, T1(retires=X), T2(retires=T1)]` — the canonical un-retirement shape."""
        return (
            _entry(id="row-x", text=x_text),
            _entry(id="tomb-1", retires="row-x", tier="compressible"),
            _entry(id="tomb-2", retires="tomb-1", tier="compressible"),
        )

    @covers("REQ-0.35.0-01-08")
    def test_retired_ids_excludes_the_un_retired_target_and_includes_the_dead_tombstone(
        self,
    ) -> None:
        """`retired_ids()` must read the fold, not a flat scan, under Algebra 6.

        The OLD flat form was `frozenset(e.retires for e in entries if
        e.retires is not None)`. Over this exact chain that scan collects the
        VALUE of every `.retires` pointer regardless of whether the pointing
        row is itself still live: `tomb-1.retires == "row-x"` and
        `tomb-2.retires == "tomb-1"`, so the flat set is `{"row-x",
        "tomb-1"}` — `"row-x"` sits in it PERMANENTLY, because a flat set
        only ever grows. `assertNotIn("row-x", ...)` below would therefore
        FAIL against the flat form. Under the fold, `tomb-2` is live (nothing
        retires it), which kills `tomb-1`, which restores `row-x`: the
        NOT-live set is `{"tomb-1"}` alone.
        """
        corpus = Corpus.loads(_jsonl(*self._un_retirement_chain(x_text="restored canon")))

        retired = corpus.retired_ids()

        self.assertNotIn("row-x", retired)
        self.assertIn("tomb-1", retired)

    @covers("REQ-0.35.0-01-08")
    def test_live_entry_with_text_finds_the_un_retired_entry(self) -> None:
        """`live_entry_with_text()` must read the fold, not a flat scan, under Algebra 6.

        Under the OLD flat form, `"row-x"` sat in `retired_ids()` forever (see
        the sibling test above), so the old predicate --
        `e.text == text and e.retires is None and e.id not in retired` --
        excluded `row-x` unconditionally and returned `None`. That is a real
        regression: `gz content remember` calls this method to detect
        duplicates, so a `None` here would have let an un-retired entry's
        wording be captured a second time, reopening GHI #862 for exactly the
        entries this fold is supposed to restore. `assertIsNotNone` below
        would FAIL against the flat form.
        """
        distinctive_text = "un-retired canon, findable again"
        corpus = Corpus.loads(_jsonl(*self._un_retirement_chain(x_text=distinctive_text)))

        found = corpus.live_entry_with_text(distinctive_text)

        self.assertIsNotNone(found)
        assert found is not None
        self.assertEqual(found.id, "row-x")


if __name__ == "__main__":
    unittest.main()
