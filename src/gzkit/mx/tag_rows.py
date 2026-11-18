"""The tag-out log's typed row readers, a leaf below every writer (RP-12 ruling 141).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the tag-out log is
ledger events (ruling 4). `gzkit.mx.tag_out` imports the order and package
ledgers, so they cannot import it; the readers of the four tag events live here,
importing only the events and the ledger, and every writer that reads tags, the
tag-out log's own, the order's commencement and acceptance and the repair
package's close, reads through them. A malformed row is refused by this one
reader everywhere, with the void that recovers it.
"""

from typing import TYPE_CHECKING, NoReturn

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gzkit.events import TagClearanceAuthorizedEvent, TagClearedEvent, TagHungEvent, TagIssuedEvent

if TYPE_CHECKING:
    from gzkit.ledger import Ledger


class TagOutError(ValueError):
    """A tag-out act the ruled grammar refuses; nothing was written."""


class OrderTags(BaseModel):
    """One order's tags as the log reads them, each tuple in issue order."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    issued: tuple[str, ...] = Field(..., description="Every tag issued on the order")
    unhung: tuple[str, ...] = Field(..., description="Issued and not hung (ruling 108)")
    hung_uncleared: tuple[str, ...] = Field(
        ..., description="Hung and not cleared, so open whatever the order's state (ruling 129)"
    )


def _refuse(message: str) -> NoReturn:
    raise TagOutError(message)


def _read[E: (TagIssuedEvent, TagHungEvent, TagClearanceAuthorizedEvent, TagClearedEvent)](
    ledger: Ledger, event_type: str, model: type[E]
) -> list[E]:
    """Read every live row of one tag-out event, refusing a row its shape does not admit.

    A void correction drops a row from the live stream (`gzkit.ledger_corrections`),
    so a malformed row is recovered by voiding it, never by editing the ledger.

    Returns:
        Each event the live ledger holds, oldest first.

    """
    events: list[E] = []
    for row in ledger.query(event_type=event_type):
        try:
            events.append(model.model_validate(row.model_dump()))
        except ValidationError as exc:
            _refuse(
                f"The ledger's {event_type} row {row.id!r} at {row.ts} does not parse "
                f"({exc.error_count()} field errors), so the tag-out log cannot be read; it is "
                "ledger events alone (RP-12 ruling 4) and a ledger row is never hand-edited. "
                "Have the operator void it: `uv run gz ledger correct --subject-event "
                f"{event_type} --subject-id {row.id} --subject-ts {row.ts} --disposition void "
                '--cause agent-error --reason "<why>" --attestor g0`.'
            )
    return events


def tag_issues(ledger: Ledger) -> list[TagIssuedEvent]:
    """Read every tag's issue, oldest first.

    Returns:
        Each issue the live ledger holds.

    """
    return _read(ledger, "tag_issued", TagIssuedEvent)


def tag_hangs(ledger: Ledger) -> dict[str, TagHungEvent]:
    """Read each hung tag's hang, by tag id; the first stands, as a tag is hung once (ruling 6).

    Returns:
        Each hang the live ledger holds, keyed by its tag.

    """
    hangs: dict[str, TagHungEvent] = {}
    for hang in _read(ledger, "tag_hung", TagHungEvent):
        hangs.setdefault(hang.tag_id, hang)
    return hangs


def tag_clearances(ledger: Ledger) -> dict[str, TagClearanceAuthorizedEvent]:
    """Read each tag's clearance authorized, by tag id; the first stands, as it is booked once.

    Returns:
        Each clearance the live ledger holds, keyed by its tag.

    """
    clearances: dict[str, TagClearanceAuthorizedEvent] = {}
    for clearance in _read(ledger, "tag_clearance_authorized", TagClearanceAuthorizedEvent):
        clearances.setdefault(clearance.tag_id, clearance)
    return clearances


def tag_clears(ledger: Ledger) -> dict[str, TagClearedEvent]:
    """Read each cleared tag's clear, by tag id; the first stands, as a tag is cleared once.

    Returns:
        Each clear the live ledger holds, keyed by its tag.

    """
    clears: dict[str, TagClearedEvent] = {}
    for clear in _read(ledger, "tag_cleared", TagClearedEvent):
        clears.setdefault(clear.tag_id, clear)
    return clears


def order_tags(ledger: Ledger, order: str) -> OrderTags:
    """Read the tags issued on one order: issued, unhung, and hung but not cleared.

    Returns:
        The order's standing, each tuple in issue order.

    """
    hangs, clears = tag_hangs(ledger), tag_clears(ledger)
    issued = tuple(issue.tag_id for issue in tag_issues(ledger) if issue.order == order)
    return OrderTags(
        issued=issued,
        unhung=tuple(tag for tag in issued if tag not in hangs),
        hung_uncleared=tuple(tag for tag in issued if tag in hangs and tag not in clears),
    )
