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

    def entry(self, entry_id: str) -> CorpusEntry | None:
        """Return the entry with *entry_id*, or ``None`` when no row carries it."""
        return next((e for e in self.entries if e.id == entry_id), None)

    def dumps(self) -> str:
        """Serialize to JSONL — one ``CorpusEntry`` JSON object per line.

        A ``retires`` of ``None`` is omitted rather than emitted as ``null``
        (GHI #635). This serialization IS the corpus derivation identity —
        ``rendition_store.corpus_fingerprint`` hashes exactly this string — so
        emitting a key that carries no information would have changed every
        surface's fingerprint the moment the field was added, invalidating the
        provenance of every committed rendition and demanding a Gate-5
        recompose for a no-op schema change. Rows that genuinely retire
        something still perturb the digest, which is the drift the freshness
        gate exists to catch.
        """
        return "\n".join(
            entry.model_dump_json(exclude={"retires"} if entry.retires is None else set())
            for entry in self.entries
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
