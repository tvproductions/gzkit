"""``gz canary`` commands over the reviewed guard mutation canaries (GHI #1161)."""

from __future__ import annotations

import json

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.guard_canary import record_review


def canary_review_cmd(
    *,
    claims: list[str],
    operator_text: str,
    attestor: str,
    ruling_source: str | None,
    as_json: bool,
) -> None:
    """Record the operator's review of each named canary as a ``guard_canary_reviewed`` event.

    The event carries the operator's verbatim words and the binding they reviewed; it is the
    only thing ``gzkit.guard_canary.unreviewed`` accepts as a review, so a hand edit of
    ``reviewed_by`` in ``data/guard_canaries.json`` no longer passes. ``reviewed_by`` is
    written as a readable projection. Refusals raise before any write: empty words, an empty
    attestor or an unknown claim exits 1; a stale binding exits 3.
    """
    config = ensure_initialized()
    root = get_project_root()
    recorded = record_review(
        root,
        claims,
        attestor=attestor,
        operator_text=operator_text,
        ruling_source=ruling_source,
        ledger_path=root / config.paths.ledger,
    )
    if as_json:
        print(json.dumps({"status": "reviewed", "claims": recorded, "attestor": attestor}))  # noqa: T201
        return
    noun = "canary" if len(recorded) == 1 else "canaries"
    console.print(f"Recorded the operator's review of {len(recorded)} {noun}:")
    for claim in recorded:
        console.print(f"  {claim}")
