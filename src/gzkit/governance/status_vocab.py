"""Canonical status-vocabulary mapping (ADR-0.0.16 OBPI-05).

Frontmatter ``status:`` terms observed in circulation across gzkit map to
the ledger state-machine canonical terms defined in ADR-0.0.9 and enumerated
in ``gzkit.ledger.OBPI_RUNTIME_STATES``. Downstream consumers — ``gz gates``
error output (OBPI-0.0.16-02) and the ``frontmatter-ledger-coherence`` chore
(OBPI-0.0.16-03) — import ``STATUS_VOCAB_MAPPING`` from this module and never
inline duplicates.

Consumers that encounter a frontmatter term not in ``STATUS_VOCAB_MAPPING``
MUST block with a clear error naming the unmapped term. They never silently
skip.
"""

from __future__ import annotations

from types import MappingProxyType

CANONICAL_LEDGER_TERMS: frozenset[str] = frozenset(
    {
        "pending",
        "in_progress",
        "completed",
        "attested_completed",
        "validated",
        "drift",
        "withdrawn",
        "abandoned",
    }
)

_RAW_MAPPING: dict[str, str] = {
    "Draft": "pending",
    "Proposed": "pending",
    "Pool": "pending",
    "Promoted": "pending",
    "Pending": "pending",
    "Active": "in_progress",
    "in_progress": "in_progress",
    "In-Progress": "in_progress",
    "In Progress": "in_progress",
    "Accepted": "validated",
    "Validated": "validated",
    "Pending-Attestation": "completed",
    "Completed": "completed",
    "attested_completed": "attested_completed",
    "Attested": "attested_completed",
    "Superseded": "abandoned",
    "Deprecated": "abandoned",
    "Abandoned": "abandoned",
    "Withdrawn": "abandoned",
    "archived": "abandoned",
    "drift": "drift",
}

STATUS_VOCAB_MAPPING: MappingProxyType[str, str] = MappingProxyType(_RAW_MAPPING)

_OBPI_FRONTMATTER_BY_LEDGER_STATE: MappingProxyType[str, str] = MappingProxyType(
    {
        "pending": "Draft",
        "in_progress": "Active",
        "completed": "Completed",
        "attested_completed": "Completed",
        "validated": "Completed",
        "abandoned": "Abandoned",
        "drift": "drift",
    }
)

_ADR_FRONTMATTER_BY_LEDGER_STATE: MappingProxyType[str, str] = MappingProxyType(
    {
        "pending": "Pending",
        "completed": "Completed",
        "validated": "Validated",
        "abandoned": "Abandoned",
    }
)


def canonicalize_status(term: str) -> str | None:
    """Return the canonical ledger term for a frontmatter status term.

    Case-insensitive lookup. Returns ``None`` for an empty input or a term
    not present in the mapping — consumers MUST block on ``None`` with a
    clear error naming the unmapped term (REQ-0.0.16-05-06).
    """
    if not term:
        return None
    lowered = term.lower()
    for key, value in STATUS_VOCAB_MAPPING.items():
        if key.lower() == lowered:
            return value
    return None


def canonicalize_ledger_status(term: str) -> str | None:
    """Return a comparable canonical ledger term for raw runtime/status output."""
    canon = canonicalize_status(term)
    if canon is not None:
        return canon
    normalized = term.strip().lower()
    return normalized or None


def frontmatter_status_for_ledger(term: str, artifact_type: str) -> str:
    """Project a raw ledger status to the canonical frontmatter mirror term."""
    canon = canonicalize_ledger_status(term)
    if canon is None:
        return term
    if artifact_type == "obpi":
        return _OBPI_FRONTMATTER_BY_LEDGER_STATE.get(canon, term)
    if artifact_type == "adr":
        return _ADR_FRONTMATTER_BY_LEDGER_STATE.get(canon, term)
    return term


__all__ = [
    "CANONICAL_LEDGER_TERMS",
    "STATUS_VOCAB_MAPPING",
    "canonicalize_ledger_status",
    "canonicalize_status",
    "frontmatter_status_for_ledger",
]
