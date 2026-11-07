"""`gz chores record-processed` — book a tautological op the chore processed (GHI #1305).

The ``decommission-tautological-tests`` chore promised a ledger event per
processed item and no verb wrote one. This verb books it through
``gzkit.tautological_processed.record_processed``. Only that chore processes
items, so any other slug is refused.
"""

import json

from gzkit.commands.common import GzCliError, console, ensure_initialized, get_project_root
from gzkit.tautological_processed import record_processed

_SLUG = "decommission-tautological-tests"


class ChoreRecordsNoItemsError(GzCliError):
    """Only the decommission chore books processed items."""

    def __init__(self, slug: str) -> None:
        """Record the slug given."""
        self.slug = slug
        super().__init__(f"Chore {slug!r} books no processed items; only {_SLUG!r} does")


def chores_record_processed(
    *,
    slug: str,
    file_path: str,
    disposition: str,
    obpi_id: str | None,
    task_id: str | None,
    as_json: bool,
) -> None:
    """Book one ``chore_decommission_processed`` event for a processed tautological op.

    Every input is checked before the ledger is written: the slug is the
    decommission chore, the work order is exactly one of ``--obpi`` or
    ``--task``, the disposition is one the ledger schema admits, and the file
    holds an op in ``data/tautological_test_baseline.json``. A refusal exits 1
    and writes nothing.

    Raises:
        ChoreRecordsNoItemsError: the slug is not the decommission chore.

    """
    if slug != _SLUG:
        raise ChoreRecordsNoItemsError(slug)
    config = ensure_initialized()
    root = get_project_root()
    booked = record_processed(
        root,
        file_path=file_path,
        disposition=disposition,
        obpi_id=obpi_id,
        task_id=task_id,
        ledger_path=root / config.paths.ledger,
    )
    if as_json:
        print(json.dumps({"status": "recorded", **booked}))  # noqa: T201
        return
    order = booked.get("obpi_id") or booked.get("task_id")
    console.print(
        f"Recorded chore_decommission_processed: {booked['file_path']} "
        f"({booked['disposition']}) under {order}"
    )
