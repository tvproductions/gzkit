"""gz content reconcile-retirements handler — Layer-2 repair for orphaned tombstones.

GHI #885 arm 2 (bypass ingress), GHI #878 option (a) (partial-write window).

``gz validate --corpus-retirement-witness`` detects a retraction row that changed
canon with no ledger witness. This verb is its repair arm: for each unwitnessed
tombstone it appends one ``corpus_retirement_reconciled`` event naming the
retired id.

WHY A DISTINCT EVENT TYPE, not a backfilled ``corpus_entry_retired``. Backfilling
would stamp a current timestamp — and, on the invariant floor, an attestor — onto
a governed procedure that never ran. ``AGENTS.md`` § Attestation: *"Fabricating a
receipt ID is the same failure as fabricating the claim."* Re-running the governed
verb is not available either: ``gz content retire`` fails closed on an
already-retired id. So the honest record is a different sentence — *a tombstone
was found without a witness and accounted for on this date* — and that is the only
sentence this verb writes.

Idempotent by construction: it emits only for tombstones the witness gate still
reports, so a second run over a reconciled corpus writes nothing and exits 0.
"""

from __future__ import annotations

import sys

from gzkit.commands.common import get_project_root
from gzkit.content.corpus_store import corpus_path, load_corpus
from gzkit.content.models.corpus import tombstone_target
from gzkit.governance.trust_audits import validate_corpus_retirement_witness
from gzkit.ledger import Ledger
from gzkit.ledger_events import corpus_retirement_reconciled_event

_DEFAULT_REASON = "tombstone found without a ledger witness; reconciled (GHI #885, GHI #878)"


def content_reconcile_retirements_cmd(
    *,
    surface: str,
    reason: str | None = None,
    dry_run: bool = False,
) -> None:
    """Handle ``gz content reconcile-retirements <surface> [--reason X] [--dry-run]``.

    Exit 0 when the surface is fully witnessed (before or after this run), 1 when
    the surface has no corpus store.
    """
    root = get_project_root()

    if not corpus_path(root, surface).exists():
        print(
            f"Error: no corpus store for surface {surface!r} "
            f"(expected {corpus_path(root, surface).relative_to(root).as_posix()}).",
            file=sys.stderr,
        )
        sys.exit(1)

    unwitnessed = {
        error.field
        for error in validate_corpus_retirement_witness(root)
        if error.artifact == corpus_path(root, surface).relative_to(root).as_posix()
        and error.field is not None
    }

    if not unwitnessed:
        print(f"{surface}: every retirement already carries a ledger witness. Nothing to do.")
        return

    # The retraction ROW is what carries the forensic trace (its `origin` prose is
    # the only surviving difference between a governed and a hand-written
    # tombstone), so the event is built from the row, not from the error.
    rows = [
        entry
        for entry in load_corpus(root, surface).entries
        if tombstone_target(entry) in unwitnessed
    ]

    if dry_run:
        print(f"{surface}: {len(rows)} unwitnessed retirement(s) would be reconciled:")
        for entry in rows:
            print(f"  {tombstone_target(entry)}")
            print(f"    via row {entry.id}  origin={entry.origin!r}")
        return

    ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
    for entry in rows:
        target = tombstone_target(entry)
        assert target is not None  # selected on a non-None target above
        ledger.append(
            corpus_retirement_reconciled_event(
                surface=surface,
                retired_entry_id=target,
                retraction_entry_id=entry.id,
                reason=reason or _DEFAULT_REASON,
                origin=entry.origin or "",
            )
        )
        print(f"reconciled {target}")

    remaining = [
        error
        for error in validate_corpus_retirement_witness(root)
        if error.artifact == corpus_path(root, surface).relative_to(root).as_posix()
    ]
    print(f"\n{surface}: {len(rows)} reconciled, {len(remaining)} still unwitnessed.")
    if remaining:
        # A row selected for repair that survives its own repair means the event
        # did not bind to the subject the gate reads -- fail loudly rather than
        # report a clean exit over a gate that is still red.
        sys.exit(3)
