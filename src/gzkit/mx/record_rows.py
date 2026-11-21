"""The records' typed row readers, a leaf below every writer (RP-12 rulings 141 and 184).

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the maintenance record
and the list of discrepancies are ledger events, rendered as views (rulings 8 and
9). `gzkit.mx.discrepancies` imports the order ledger, and the order's acceptance
reads the list to admit a carry (rulings 171 and 184), so the list's reader lives
here, importing only the events and the ledger, as the tag-out log's readers live
in `gzkit.mx.tag_rows` (ruling 141). A malformed row is refused by this one reader
everywhere, with the void that recovers it.
"""

from typing import TYPE_CHECKING, NoReturn

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gzkit.events import DiscrepancyClearedEvent, DiscrepancyGrade, DiscrepancyRecordedEvent

if TYPE_CHECKING:
    from gzkit.ledger import Ledger, LedgerEvent

#: The grade a line is due by a named event under, the one a carry reads (rulings 9, 171, 179).
DUE_BY: DiscrepancyGrade = "due-by-event"


class DiscrepancyError(ValueError):
    """A list-of-discrepancies act the ruled grammar refuses; nothing was written."""


class Discrepancy(BaseModel):
    """One line of the list as its view reads it: the record, its clear, whether open."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    record: DiscrepancyRecordedEvent = Field(..., description="The line as recorded")
    clear: DiscrepancyClearedEvent | None = Field(None, description="Its clear, None while open")

    @property
    def is_open(self) -> bool:
        """Whether the line is still on the list: it has no clear."""
        return self.clear is None


def malformed_row_message(
    row: LedgerEvent, exc: ValidationError, reading: str, *, ruling: int = 8
) -> str:
    """Name a row its event's shape does not admit and the void that recovers it.

    Shared by the maintenance record and the list of discrepancies (rulings 8 and 9).

    Returns:
        The refusal's text.

    """
    return (
        f"The ledger's {row.event} row {row.id!r} at {row.ts} does not parse "
        f"({exc.error_count()} error(s)), so {reading} (RP-12 ruling {ruling}). The ledger is "
        f"append-only; void the row with `uv run gz ledger correct --subject-event {row.event} "
        f"--subject-id {row.id} --subject-ts {row.ts} --disposition void --cause agent-error "
        '--reason "<why>" --attestor g0`, then read it again.'
    )


def _refuse(message: str) -> NoReturn:
    raise DiscrepancyError(message)


def _parsed[T: BaseModel](ledger: Ledger, event_type: str, model: type[T]) -> list[T]:
    rows: list[T] = []
    for row in ledger.query(event_type=event_type):
        try:
            rows.append(model.model_validate(row.model_dump()))
        except ValidationError as exc:
            _refuse(
                malformed_row_message(
                    row, exc, "the list of discrepancies cannot be read", ruling=9
                )
            )
    return rows


def discrepancy_list(ledger: Ledger) -> list[Discrepancy]:
    """Read every line the ledger records, oldest first, each with its clear (ruling 9).

    A void correction drops a row from the live stream, so a malformed row is
    recovered by voiding it, never by editing the ledger. A line's first clear is its
    clear; the writer refuses a second.

    Returns:
        Each line the live ledger holds.

    """
    clears: dict[str, DiscrepancyClearedEvent] = {}
    for clear in _parsed(ledger, "discrepancy_cleared", DiscrepancyClearedEvent):
        clears.setdefault(clear.discrepancy_id, clear)
    return [
        Discrepancy(record=record, clear=clears.get(record.discrepancy_id))
        for record in _parsed(ledger, "discrepancy_recorded", DiscrepancyRecordedEvent)
    ]


def open_discrepancies(ledger: Ledger) -> list[Discrepancy]:
    """Read the lines still open, the list's default view.

    Returns:
        The lines with no clear, oldest first.

    """
    return [line for line in discrepancy_list(ledger) if line.is_open]
