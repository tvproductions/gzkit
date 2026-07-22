"""gz content retire command handler — append-only corpus retirement (GHI #635).

The corpus store has exactly one mutation, append, and no delete. That made a
superseded operator directive permanent: two invariant-tier entries carrying the
same doctrine in different wording both bound the floor forever, and any
rendition that deduplicated them was rejected. The only escape was hand-deleting
a line from the append-only store, which is not a governed operation.

``gz content retire <surface> --entry <id> --reason <text>`` is the governed
exit. It appends a *retraction row* whose ``retires`` field names the superseded
id. Nothing is deleted — the retired row stays on disk with its provenance — but
``tier_policy.invariant_entries`` skips it, so the invariant floor shrinks.

Retirement therefore never invalidates a committed rendition: the floor only
loses requirements, never gains them. No recomposition is implied, and this
command never touches a rendered surface.
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime

from gzkit.commands.common import get_project_root
from gzkit.content.corpus_store import append_entry, load_corpus
from gzkit.content.models import CorpusEntry
from gzkit.ledger import Ledger
from gzkit.ledger_events import corpus_entry_retired_event


def content_retire_cmd(*, surface: str, entry_id: str, reason: str, origin: str) -> None:
    """Handle ``gz content retire <surface> --entry <id> --reason <text>``.

    Exit 0 on a successful retirement; 1 on unknown entry or an entry already
    retired; 2 on IO error writing the corpus store.
    """
    root = get_project_root()
    corpus = load_corpus(root, surface)

    target = corpus.entry(entry_id)
    if target is None:
        print(
            f"Error: no corpus entry {entry_id!r} in surface {surface!r}. "
            "Retirement targets an existing entry; nothing written.",
            file=sys.stderr,
        )
        sys.exit(1)

    if entry_id in corpus.retired_ids():
        print(
            f"Error: corpus entry {entry_id!r} is already retired. "
            "Retirement is idempotent by refusal, not by silent re-append; nothing written.",
            file=sys.stderr,
        )
        sys.exit(1)

    timestamp = datetime.now(UTC).isoformat()
    retraction = CorpusEntry(
        id=f"corpus-retraction-{entry_id}-{timestamp}",
        surface=surface,
        # Inherit the retired row's section so the retraction stays addressable
        # against the same Pillar its target was validated against.
        section=target.section,
        # Compressible: the retraction is bookkeeping, never new canon to render.
        tier="compressible",
        classification="Mechanical",
        text=reason,
        origin=origin,
        ts=timestamp,
        retires=entry_id,
    )

    try:
        append_entry(root, surface, retraction)
    except OSError as exc:
        print(f"Error writing corpus store for {surface!r}: {exc}", file=sys.stderr)
        sys.exit(2)

    Ledger(root / ".gzkit" / "ledger.jsonl").append(
        corpus_entry_retired_event(
            surface=surface,
            retired_entry_id=entry_id,
            retraction_entry_id=retraction.id,
            reason=reason,
        )
    )

    print(
        f"Retired corpus entry {entry_id} in {surface} "
        f"(retraction {retraction.id}). The invariant floor shrank; "
        "committed renditions remain valid."
    )
