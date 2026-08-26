"""Corpus retirement-witness gate (GHI #885, GHI #878).

A retraction row in a corpus IS a canon change: ``Corpus.retired_ids()`` folds
the on-disk pointer, the target leaves the effective corpus, and the invariant
floor moves. ``AGENTS.md`` § Architectural Boundaries #6 requires every fact to
trace to Layer 1 canon or Layer 2 ledger — so each of those changes must have a
ledger witness naming the entry it retired.

Two ways the witness goes missing, with one signature between them:

    #885  BYPASS         the row is appended by hand; ``gz content retire``
                         never runs, so neither of its events is emitted
    #878  PARTIAL WRITE  the verb runs, appends the corpus row, then dies
                         before one or both ledger appends

Both leave a Layer-1 tombstone with no matching Layer-2 row, which is why one
gate detects both. They stay distinct in cause and prevention; only detection
and repair converge.

WHY THIS IS NOT A PRESENCE CHECK. The gate matches a witness to a tombstone by
``retired_entry_id`` — the SUBJECT — never by event type alone. That distinction
is the whole gate. Measured on ``main`` 2026-08-26: twelve corpus rows carried a
retirement pointer, five ``corpus_entry_retired`` events existed, and seven
retirements had no witness at all — yet every validator in the tree read green,
because nothing compared a witness to the id it claimed to witness.
``AGENTS.md`` § DO IT RIGHT: *"A PRESENCE CHECK ANSWERS 'is something armed',
NEVER 'did the governed procedure run'."*

TWO EVENT TYPES COUNT AS A WITNESS, and the pair is load-bearing:

    corpus_entry_retired            the governed path ran
    corpus_retirement_reconciled    a tombstone was FOUND unwitnessed and
                                    accounted for after the fact (GHI #885 arm 2)

Backfilling the first type over the seven would have stamped a current
timestamp and an attestor onto a procedure nobody performed — a fabricated
receipt under ``AGENTS.md`` § Attestation. Keeping the types separate lets Layer
2 answer *"was this retirement governed?"* long after the reconciliation, which
a single collapsed type could not.

Registered as ``gz validate --corpus-retirement-witness``.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.content.corpus_store import load_corpus
from gzkit.content.models.corpus import tombstone_target
from gzkit.core.validation_rules import ValidationError

_WITNESS_EVENT_TYPES: frozenset[str] = frozenset(
    {"corpus_entry_retired", "corpus_retirement_reconciled"}
)


def _witnessed_subjects(root: Path) -> set[tuple[str, str]]:
    """Return every ``(surface, retired_entry_id)`` Layer 2 witnesses.

    Reads the JSON ``event`` field rather than scanning for the type name as a
    substring: event names appear inside other events' prose payloads, and a
    grep-shaped read of this ledger has already produced a wrong count once
    (GHI #885's own filing session).
    """
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return set()

    witnessed: set[tuple[str, str]] = set()
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("event") not in _WITNESS_EVENT_TYPES:
            continue
        surface = event.get("surface")
        retired = event.get("retired_entry_id")
        if isinstance(surface, str) and isinstance(retired, str):
            witnessed.add((surface, retired))
    return witnessed


def validate_corpus_retirement_witness(root: Path) -> list[ValidationError]:
    """Assert every corpus retirement pointer has a subject-matching Layer-2 witness.

    Walks ``<root>/.gzkit/corpus/*.jsonl``, and for each entry carrying a
    ``retires`` or ``supersedes`` pointer requires a ``corpus_entry_retired`` or
    ``corpus_retirement_reconciled`` event whose ``retired_entry_id`` equals the
    pointer's target on the same surface. One error per unwitnessed retirement,
    so a repair pass can act per subject. Empty list when no corpus exists
    (bootstrap-safe) or every retirement is accounted for.

    Both pointers are read through ``tombstone_target``, the accessor the fold
    itself uses — a fence that re-derived the pair here could drift from the
    projection it guards, which is the trap that accessor exists to close.
    """
    corpus_dir = root / ".gzkit" / "corpus"
    if not corpus_dir.exists():
        return []

    witnessed = _witnessed_subjects(root)
    errors: list[ValidationError] = []

    for store in sorted(corpus_dir.glob("*.jsonl")):
        surface = store.name.removesuffix(".jsonl")
        for entry in load_corpus(root, surface).entries:
            target = tombstone_target(entry)
            if target is None or (surface, target) in witnessed:
                continue
            errors.append(
                ValidationError(
                    type="corpus_retirement_witness",
                    artifact=store.relative_to(root).as_posix(),
                    field=target,
                    message=(
                        f"corpus entry {target!r} is retired by row {entry.id!r} on "
                        f"surface {surface!r}, but no corpus_entry_retired or "
                        f"corpus_retirement_reconciled event names it as "
                        f"retired_entry_id. Canon changed in Layer 1 with no Layer-2 "
                        f"witness (GHI #885, GHI #878). Repair with "
                        f"`gz content reconcile-retirements {surface}`."
                    ),
                )
            )
    return errors
