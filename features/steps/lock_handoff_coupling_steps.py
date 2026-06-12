"""Behave step definitions for lock-handoff coupling validator (ADR-0.0.41 / OBPI-04).

@covers REQ-0.0.41-04-01
@covers REQ-0.0.41-04-02
"""

from __future__ import annotations

import json
from pathlib import Path

from behave import given  # type: ignore[import-untyped]

_SCHEMA = "gzkit.ledger.v1"
_CUTOVER_TS = "2026-06-07T11:00:00+00:00"
_CLAIM_TS = "2026-06-07T12:00:00+00:00"
_RELEASE_TS = "2026-06-07T13:00:00+00:00"


@given('a post-cutover obpi_lock_released event with no handoff_path for "{obpi_id}"')
def step_seed_broken_release_event(context, obpi_id: str) -> None:
    ledger_path = Path(".gzkit") / "ledger.jsonl"
    ledger_path.parent.mkdir(parents=True, exist_ok=True)

    cutover_event = {
        "schema": _SCHEMA,
        "event": "obpi_receipt_emitted",
        "id": "OBPI-0.0.41-02-claim-release-safety-primitives",
        "ts": _CUTOVER_TS,
    }
    claim_event = {
        "schema": _SCHEMA,
        "event": "obpi_lock_claimed",
        "id": obpi_id,
        "ts": _CLAIM_TS,
        "agent": "bdd-test-agent",
        "ttl_minutes": 120,
        "branch": "main",
        "session_id": "bdd-session",
    }
    release_event = {
        "schema": _SCHEMA,
        "event": "obpi_lock_released",
        "id": obpi_id,
        "ts": _RELEASE_TS,
        "agent": "bdd-test-agent",
        "force": False,
        # No handoff_path — the missing field that triggers the validator.
    }

    with ledger_path.open("a", encoding="utf-8") as f:
        for ev in (cutover_event, claim_event, release_event):
            f.write(json.dumps(ev) + "\n")
