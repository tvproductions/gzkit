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
POST_BASELINE_IDENTITY_FIELDS: tuple[str, ...] = ("retires",)


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


class Corpus(BaseModel):
    """Append-only aggregate of :class:`CorpusEntry` rows. The ONLY mutation is ``append``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    entries: tuple[CorpusEntry, ...] = ()

    def append(self, entry: CorpusEntry) -> Corpus:
        """Return a NEW corpus with *entry* appended; the original is unchanged."""
        return Corpus(entries=(*self.entries, entry))

    def retired_ids(self) -> frozenset[str]:
        """Return the ids retired by a later retraction row (GHI #635)."""
        return frozenset(e.retires for e in self.entries if e.retires is not None)

    def live_entry_with_text(self, text: str) -> CorpusEntry | None:
        """Return a live entry carrying *text* verbatim, or ``None`` (GHI #862).

        "Live" means not retired by a later retraction row, the same set
        :meth:`retired_ids` governs. A text whose only prior copy is retired is
        a re-capture, not a duplicate — that is the amendment path (retire the
        old wording, remember the corrected one), and it must stay open.

        The predicate is byte-equality. GHI #635's duplicates differed by quote
        style and broke composition loudly; the seven GHI #862 measured were
        byte-identical, so one rendered occurrence satisfied both invariant-floor
        obligations and nothing fired. Near-miss detection would refuse
        legitimate rewordings and is deliberately not attempted here.
        """
        retired = self.retired_ids()
        return next(
            (
                e
                for e in self.entries
                if e.text == text and e.retires is None and e.id not in retired
            ),
            None,
        )

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
        """Reconstruct a corpus from JSONL produced by :meth:`dumps`."""
        entries = tuple(
            CorpusEntry.model_validate_json(line) for line in text.splitlines() if line.strip()
        )
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
