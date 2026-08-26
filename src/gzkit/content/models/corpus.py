"""Append-only corpus model — addressed/provenanced contract content (ADR-0.0.37-18).

The corpus is the append-only *source of truth* for agent control-surface content
(ADR-0.0.37 § Decision Re-Alignment, 2026-06-03 part 1). Operator "remember X"
moments and agent course-corrections append entries; nothing is hand-edited at the
rendered location.

A ``CorpusEntry`` is a *store record* (cf. ``ConstitutionalInvariant``), not a
renderable per-turn surface — so it is a plain frozen ``BaseModel``, not a
``BaseContentModel``, and is deliberately absent from ``CONTENT_MODELS``. "Reuse the
AgentContract/Pillar substrate" is honored through *conformance*
(:meth:`Corpus.validate_against`), not inheritance.

Out of scope here (downstream OBPIs): the ``gz content remember`` capture CLI and the
``corpus_entry_appended`` ledger event (OBPI-19), the compression setpoint (OBPI-20),
the authoring-time compressor (OBPI-21), committed-rendition playback (OBPI-22), and
the invariant-tier *designation* + presence enforcement (OBPI-23).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict

from .agent_contract import AgentContract

_Tier = Literal["invariant", "compressible"]
_Classification = Literal["Mechanical", "Promotable", "Judgment", "Ambiguous"]

# -- Corpus derivation identity (GHI #635) -----------------------------------
#
# `rendition_store.corpus_fingerprint` hashes `Corpus.dumps()`, so that string
# IS the corpus derivation identity: the committed renditions' provenance is
# proven against it, and any change red-flags every surface and demands a
# corpus-attested recompose (`gz content compose` + `gz content commit --attestor ...`).
#
# That makes the *field set* part of the identity, not just the values. Adding
# `retires` alone changed every surface's fingerprint while the .jsonl on disk
# stayed byte-identical, because every row began emitting `"retires":null`.
# A semantically empty schema change should never cost an operator attestation.
#
# The two tuples below classify every field explicitly, so the next field
# addition is a decision rather than a silent trap. `gz validate` has no scope
# for this; the fence is `tests/content/test_corpus_model.py::
# TestDerivationIdentity::test_every_field_is_classified`, which fails closed
# when a field appears in neither tuple.

#: Fields fixed at the fingerprint baseline (digest `a862c327d6d9`). These are
#: always serialized, including when they hold `None` (`anchor`, `witness`
#: predate the identity rule and are emitted as `null`). NEVER reorder or
#: remove: doing so re-fingerprints every committed rendition.
BASELINE_IDENTITY_FIELDS: tuple[str, ...] = (
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
)

#: Fields added after the baseline. Omitted from the identity serialization
#: while they hold their default, so a row that predates the field fingerprints
#: exactly as it did before the field existed. A row that USES the field does
#: perturb the digest — that is real canon drift, and the freshness gate should
#: fire on it. New fields belong here, not in BASELINE_IDENTITY_FIELDS.
POST_BASELINE_IDENTITY_FIELDS: tuple[str, ...] = ("retires", "supersedes")


class CorpusEntry(BaseModel):
    """A single addressed, provenanced corpus entry — one append-only source-of-truth row.

    The fields are the ten named in ADR-0.0.37 § Decision Re-Alignment part 1
    (``id, surface, section, anchor?, tier, classification, witness?, text, origin, ts``)
    plus ``retires?`` — the append-only retirement pointer (GHI #635).

    ``retires`` names the id of an earlier entry this row supersedes. It is how a
    store with no delete retires content: the retired row stays on disk, and
    consumers that care about *current* canon (``tier_policy.invariant_entries``)
    skip it. Retirement therefore only ever shrinks the invariant floor, so
    already-committed renditions cannot be invalidated by one.

    ``supersedes`` names the id of an earlier entry this row both retires AND
    replaces (OBPI-0.35.0-01): unlike ``retires``, a ``supersedes`` row is itself
    a content row in the effective view. The fold that interprets both fields
    (``effective_corpus``) lands in a later task; this task only declares the
    additive field and its schema/identity classification.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str
    surface: str
    section: str
    anchor: str | None = None
    tier: _Tier
    classification: _Classification
    witness: str | None = None
    text: str
    origin: str
    ts: str
    retires: str | None = None
    supersedes: str | None = None


def _inert_fields(entry: CorpusEntry) -> set[str]:
    """Return the post-baseline fields *entry* leaves at their default.

    These carry no information for this row, so they are excluded from the
    identity serialization — a row that predates a field fingerprints exactly
    as it did before the field existed (GHI #635).
    """
    defaults = type(entry).model_fields
    return {
        name
        for name in POST_BASELINE_IDENTITY_FIELDS
        if getattr(entry, name) == defaults[name].default
    }


def tombstone_target(entry: CorpusEntry) -> str | None:
    """Return the id *entry* retires, whichever pointer names it, or ``None``.

    Algebra 4 gives the two pointers different roles in the projection, but
    Algebra 2 and Algebra 5 treat them identically: BOTH register a tombstone
    edge against an earlier row. Reading them through one accessor is what stops
    a fence from covering ``retires`` and quietly missing ``supersedes``.

    PUBLIC because that trap is not model-internal (GHI #885):
    ``trust_audits.corpus_retirement_witness`` walks these same edges to assert a
    Layer-2 witness, and a fence that re-derived the pointer pair locally would
    be free to drift from the fold it claims to guard.
    """
    return entry.retires if entry.retires is not None else entry.supersedes


def validate_tombstone_algebra(entries: tuple[CorpusEntry, ...]) -> None:
    """Fail closed on a corpus that breaks Algebra 2 or Algebra 3 (OBPI-0.35.0-01).

    Algebra 2 (TARGETS): ``retires`` and ``supersedes`` each name exactly one id
    appearing STRICTLY EARLIER in the append log. Algebra 3 (EXCLUSIVITY): no row
    populates both pointers. Algebra 7 (NO SILENT DOUBLE-RETIRE): at most one
    LIVE tombstone may target a given entry.

    Clauses 2 and 3 exist to keep the Algebra 5 reverse pass total. That pass reads
    ``live[t]`` for every tombstone ``t`` targeting a row, and it is only safe to
    read because every tombstone strictly follows its target — a forward, self,
    or unknown reference breaks the premise, and a row with both pointers has no
    single role under Algebra 4. They are therefore checked FIRST: the liveness
    pass clause 7 depends on is only meaningful once they hold.

    Clause 7 is about LIVENESS, not arity. Two live tombstones on one target
    would fold that target back to live under Algebra 5, silently reading
    "retired twice" as "restored" — so the shape is refused. A second tombstone
    whose predecessor is itself retired is LEGAL and must load: that is the
    retire -> un-retire -> retire-again cycle Algebra 6 opens, and a plain
    per-target count would close it forever.

    Raises:
        ValueError: naming the offending entry id, so an operator can find the
            row in an append log that only ever grows.

    """
    known = {entry.id for entry in entries}
    earlier: set[str] = set()
    for entry in entries:
        if entry.retires is not None and entry.supersedes is not None:
            raise ValueError(
                f"corpus entry {entry.id!r} populates both 'retires' "
                f"({entry.retires!r}) and 'supersedes' ({entry.supersedes!r}); "
                "an entry may hold at most one tombstone pointer (Algebra 3)"
            )
        target = tombstone_target(entry)
        if target is not None:
            if target == entry.id:
                raise ValueError(
                    f"corpus entry {entry.id!r} names itself as its tombstone "
                    "target; a tombstone must name a STRICTLY EARLIER entry (Algebra 2)"
                )
            if target not in known:
                raise ValueError(
                    f"corpus entry {entry.id!r} names unknown tombstone target "
                    f"{target!r}; no entry in the log carries that id (Algebra 2)"
                )
            if target not in earlier:
                raise ValueError(
                    f"corpus entry {entry.id!r} forward-references tombstone target "
                    f"{target!r}, which appears LATER in the append log; a tombstone "
                    "must name a strictly earlier entry (Algebra 2)"
                )
        earlier.add(entry.id)

    live = _liveness(entries)
    claimed: dict[str, str] = {}
    for entry in entries:
        target = tombstone_target(entry)
        if target is None or not live[entry.id]:
            continue
        if target in claimed:
            raise ValueError(
                f"corpus entry {entry.id!r} is a second LIVE tombstone targeting "
                f"{target!r}, which {claimed[target]!r} already retires; at most one "
                "live tombstone may target an entry, so a double-retire is never "
                "silently folded into an un-retirement (Algebra 7). To retire "
                f"{target!r} again, first retire {claimed[target]!r}"
            )
        claimed[target] = entry.id


def _tombstones_by_target(entries: tuple[CorpusEntry, ...]) -> dict[str, list[str]]:
    """Map each targeted entry id to the ids of the rows that tombstone it.

    BOTH pointers register an edge. Algebra 5 is stated over "tombstones
    targeting e", and Algebra 4 gives ``supersedes`` the retire-AND-replace
    role — so a replacement removes its target exactly as a pure tombstone does.
    The two roles diverge only in :func:`effective_corpus`, which additionally
    drops rows whose ``retires`` is set. Registering ``retires`` alone would
    publish both the old and the corrected wording side by side.
    """
    edges: dict[str, list[str]] = {}
    for entry in entries:
        target = tombstone_target(entry)
        if target is not None:
            edges.setdefault(target, []).append(entry.id)
    return edges


def _liveness(entries: tuple[CorpusEntry, ...]) -> dict[str, bool]:
    """Return ``{entry id: is live}`` via the Algebra 5 single reverse pass.

    ``live(e) = not any(live(t) for t in tombstones targeting e)``, evaluated
    LAST to FIRST. Because Algebra 2 guarantees every tombstone strictly follows
    its target, one backward loop resolves every dependency before it is read —
    so this is a single reverse pass, NEVER a fixpoint iteration and NEVER
    unbounded recursion.

    That ordering is what makes Algebra 6 work: in ``[X, T1(retires=X),
    T2(retires=T1)]``, T2 is resolved live, which kills T1, which restores X.
    A flat ``{e.retires for e in entries}`` set cannot express this — it yields
    ``{X, T1}`` and leaves X retired forever, silently.

    An unresolved tombstone is REFUSED, never guessed at. Every tombstone ``t``
    targeting the row being resolved must already carry a liveness value at the
    moment it is read; Algebra 2 guarantees exactly that, because ``t`` strictly
    follows its target. Where it does not hold, this helper RAISES instead of
    substituting a default: the caller handed over a log the algebra is not
    defined over, and there is no correct value to supply there.

    Two inputs reach that state, and BOTH are defects in the input:

    * A corpus assembled in memory without going through :meth:`Corpus.loads`,
      so nothing checked Algebra 2 and a tombstone may precede its target.
    * A corpus that DID pass :func:`validate_tombstone_algebra` but carries a
      DUPLICATE entry id. That uniqueness is an UNENFORCED PREMISE, not a
      guarantee this module (or the schema, or ``corpus_store``) makes:
      ``known`` and ``earlier`` in that validator are both sets, and nothing
      anywhere rejects a duplicate id (tracked separately as GHI #874; NOT
      fixed here, that fix is out of this OBPI's scope). The shape
      ``[A(id="x"), T1(id="t1", retires="x"), B(id="x")]`` passes that
      validator cleanly — "x" is in ``known`` and in ``earlier`` when T1 is
      checked — yet the reverse pass reaches the second ``B(id="x")`` before
      T1 is resolved.

    The branch used to substitute ``live.get(t, True)``, justified as keeping
    this helper TOTAL and as failing safe toward keeping an entry retired. That
    rationale is REVERSED. A cross-vendor adversarial review of OBPI-0.35.0-01
    showed the default does not merely fail safe — it invents an answer the
    recurrence above does not give. On ``[T1(retires=X), X, T2(retires=T1)]``
    it resolved X before T1 and folded to ``[]``, where the recurrence gives
    live(T2)=True, live(T1)=False, live(X)=True and therefore ``['X']``.
    Substituting one answer for another under a green gate is exactly how
    retired canon gets republished (ADR-0.35.0 § Consequences Negative #5), and
    a totality bought by guessing is not totality over the stated domain. The
    fence is ``tests/content/test_corpus_model.py::
    TestLivenessRefusesAnUnresolvableTombstone``.

    A DANGLING TARGET is NOT this state and must never raise, or Algebra 9
    breaks outright: a folded view legitimately carries a ``supersedes`` row
    whose target the fold just removed, so ``edges`` holds a key that is no
    longer an entry. The reverse pass iterates ENTRIES and looks up
    ``edges.get(entry.id)``, so such a key is never consulted at all. Only an
    id appearing inside an edge LIST is ever read, and only that id can be
    unresolved.
    """
    edges = _tombstones_by_target(entries)
    live: dict[str, bool] = {}
    for entry in reversed(entries):
        tombstones = edges.get(entry.id, ())
        for tombstone in tombstones:
            if tombstone not in live:
                raise ValueError(
                    f"corpus entry {entry.id!r} is targeted by tombstone "
                    f"{tombstone!r}, whose own liveness is UNRESOLVED at that point "
                    "in the reverse pass; the append log is out of order (a tombstone "
                    "must strictly follow its target, Algebra 2) or carries duplicate "
                    "entry ids, so liveness is not computable for this corpus"
                )
        live[entry.id] = not any(live[t] for t in tombstones)
    return live


def effective_corpus(corpus: Corpus) -> Corpus:
    """Return the current-canon projection of *corpus* (Algebra 8).

    Every row where ``live(e)`` holds AND ``e.retires is None``, in APPEND order.
    A pure ``retires`` row is a marker contributing no text (Algebra 4), so it
    leaves the view alongside the row it retired; a ``supersedes`` row retires
    its target and stays, because it IS the replacement content.

    A PURE PROJECTION: the raw append log is never mutated, and the algebra is
    NOT re-validated here. Re-validating would make Algebra 2 and Algebra 9
    contradict each other — a folded view legitimately carries a ``supersedes``
    row whose target this very fold removed, so a second pass would raise
    "unknown target" instead of returning an equal corpus.
    """
    live = _liveness(corpus.entries)
    return Corpus(entries=tuple(e for e in corpus.entries if live[e.id] and e.retires is None))


class Corpus(BaseModel):
    """Append-only aggregate of :class:`CorpusEntry` rows. The ONLY mutation is ``append``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: tuple[CorpusEntry, ...] = ()

    def append(self, entry: CorpusEntry) -> Corpus:
        """Return a NEW corpus with *entry* appended; the original is unchanged."""
        return Corpus(entries=(*self.entries, entry))

    def retired_ids(self) -> frozenset[str]:
        """Return the ids that are NOT live under the Algebra 5 fold (GHI #635).

        Repointed onto :func:`_liveness` (OBPI-0.35.0-01 D3) rather than the
        flat ``{e.retires for e in entries}`` scan this method used to be: the
        flat form is a one-way ratchet — appending a tombstone T2 that retires
        tombstone T1 left T1's original target retired FOREVER, because the
        flat set only ever grows. The fold is the difference: un-retirement
        (Algebra 6) means a later tombstone can retire an earlier tombstone and
        bring its target back, and this method must see that or every reader
        still routed through it — including ``retire.py``'s own guard, a
        DENIED path this repoint updates for free — silently carries the
        Algebra-6 defect forward.

        Kept, not deleted: its remaining consumer is
        ``src/gzkit/commands/content/retire.py``, owned by OBPI-0.35.0-02 and
        out of this task's allowlist. Redefining the method in place repoints
        that guard without touching the denied file.
        """
        live = _liveness(self.entries)
        return frozenset(entry_id for entry_id, is_live in live.items() if not is_live)

    def live_entry_with_text(self, text: str) -> CorpusEntry | None:
        """Return a live entry carrying *text* verbatim, or ``None`` (GHI #862).

        "Live" means membership in :func:`effective_corpus`'s projection, not a
        flat retired-ids scan (OBPI-0.35.0-01 D3): after
        ``[X, T1(retires=X), T2(retires=T1)]`` folds, X is live again, so a
        re-captured text matching X must be FOUND here, not reported absent.
        A text whose only prior copy is currently retired is a re-capture, not
        a duplicate — that is the amendment path (retire the old wording,
        remember the corrected one), and it must stay open.

        The predicate is byte-equality. GHI #635's duplicates differed by quote
        style and broke composition loudly; the seven GHI #862 measured were
        byte-identical, so one rendered occurrence satisfied both invariant-floor
        obligations and nothing fired. Near-miss detection would refuse
        legitimate rewordings and is deliberately not attempted here.
        """
        return next((e for e in effective_corpus(self).entries if e.text == text), None)

    def entry(self, entry_id: str) -> CorpusEntry | None:
        """Return the entry with *entry_id*, or ``None`` when no row carries it."""
        return next((e for e in self.entries if e.id == entry_id), None)

    def dumps(self) -> str:
        """Serialize to JSONL — one ``CorpusEntry`` JSON object per line.

        This string IS the corpus derivation identity (see the module-level
        ``BASELINE_IDENTITY_FIELDS`` / ``POST_BASELINE_IDENTITY_FIELDS`` note):
        a post-baseline field holding its default is omitted, so adding a field
        cannot re-fingerprint rows that predate it and cost an operator a
        corpus-attested recompose for a semantically empty change. A row that actually
        uses the field is serialized with it — real canon drift, which the
        freshness gate should catch.
        """
        return "\n".join(
            entry.model_dump_json(exclude=_inert_fields(entry)) for entry in self.entries
        )

    @classmethod
    def loads(cls, text: str) -> Corpus:
        """Reconstruct a corpus from JSONL produced by :meth:`dumps`.

        This is the LOAD-TIME boundary the tombstone algebra is validated at
        (:func:`validate_tombstone_algebra`), never a model validator on
        ``Corpus``. A model validator would fire on every in-memory construction
        — including the one :func:`effective_corpus` performs — and a folded view
        legitimately carries a ``supersedes`` row whose target the fold just
        removed, so Algebra 2 and Algebra 9 would contradict each other directly.
        """
        entries = tuple(
            CorpusEntry.model_validate_json(line) for line in text.splitlines() if line.strip()
        )
        validate_tombstone_algebra(entries)
        return cls(entries=entries)

    def validate_against(self, contract: AgentContract) -> None:
        """Fail closed when any entry's ``section`` resolves to no ``Pillar`` in *contract*.

        Conformance is computed against the template-defined ``Pillar`` set
        (``contract.pillars``), never a separate registry. Invariant-tier *presence*
        enforcement is OBPI-0.0.37-23 — ``Pillar.tier`` has no ``invariant`` value yet,
        so it is intentionally not checked here.
        """
        valid_sections = {pillar.id for pillar in contract.pillars}
        for entry in self.entries:
            if entry.section not in valid_sections:
                raise ValueError(
                    f"corpus entry {entry.id!r} section {entry.section!r} "
                    "resolves to no Pillar in the contract"
                )
