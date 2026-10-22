"""Requirements catalog scope, the forward rule (drydock RO-3 tranche 4).

`docs/governance/harbor-ro3-requirements-store.md` § The witness: a delivery event
appended after the cutover that names no REQ or outcome is announced, advisory
until RO-5's verbs can supply an outcome id (ruling 4). Legacy events, before the
cutover, are never read or backfilled.

Rulings of 2026-10-22: the types are the registry's (`data/catalog/
delivery_events.json`, "All nine (Rec.)"); an event names a REQ when any of its
values carries a REQ id in either grammar, matched by the identity seam's
patterns, or names an outcome when its `outcome` field holds a code the catalog
holds ("Grammar over fields (Rec.)"). A TASK id never names its REQ by spelling.
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Iterable, Mapping
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from gzkit.core.models import CATALOG_REQ_ID_BODY, REQ_ID_BODY_PLAIN
from gzkit.models.catalog import DeliveryEventsFile

#: A REQ id in either grammar, standing alone as a token.
_REQ_NAME = re.compile(rf"(?<![\w.-])(?:{REQ_ID_BODY_PLAIN}|{CATALOG_REQ_ID_BODY})(?![\w.-])")
_ENVELOPE = frozenset({"schema", "event", "ts"})


class ForwardRuleReading(BaseModel):
    """What the forward rule read: delivery events since the cutover, and the unnamed ones."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    read: int = Field(..., ge=0, description="Listed delivery events after the cutover")
    unnamed: dict[str, int] = Field(
        ..., description="Event type -> events naming no REQ or outcome"
    )


def _strings(value: object) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list | tuple):
        for item in value:
            yield from _strings(item)


def names_req_or_outcome(row: Mapping[str, object], outcomes: frozenset[str]) -> bool:
    """Return whether a ledger row names a REQ in any value, or an outcome the catalog holds."""
    if row.get("outcome") in outcomes:
        return True
    values = (value for key, value in row.items() if key not in _ENVELOPE)
    return any(_REQ_NAME.search(text) for value in values for text in _strings(value))


def _after(ts: object, cutover: datetime) -> bool:
    try:
        stamp = datetime.fromisoformat(str(ts))
    except ValueError:
        return False
    return stamp.tzinfo is not None and stamp > cutover


def forward_rule_reading(
    rows: Iterable[Mapping[str, object]],
    registry: DeliveryEventsFile,
    outcomes: frozenset[str],
) -> ForwardRuleReading:
    """Read the listed delivery events after the cutover and count the unnamed ones by type."""
    types = set(registry.event_types)
    delivered = [
        row for row in rows if row.get("event") in types and _after(row.get("ts"), registry.cutover)
    ]
    unnamed = Counter(
        str(row["event"]) for row in delivered if not names_req_or_outcome(row, outcomes)
    )
    return ForwardRuleReading(read=len(delivered), unnamed=dict(sorted(unnamed.items())))
