"""One id series read from the ledger's history (RP-12 rulings 111, 169 and 176).

A tag and a maintenance-record entry are each minted `<PREFIX>-<NN>-<slug>` in
one series read from the ledger, their only store (rulings 4, 8, 111 and 169).
The series is numbered past every number the ledger's history names, a voided
row included, so a number never returns (ruling 176): ruling 170 has a commit
subject name its entry, and a reissued number would point to two acts.
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gzkit.ledger import Ledger


def next_series_id(ledger: Ledger, event_type: str, prefix: str, slug: str) -> str:
    """Return the next id in ``prefix``'s series: the highest number its history names, plus one.

    The number is read from each row's ``id`` by its shape, so a voided row and a row
    the event's model no longer admits both still hold their number.

    Returns:
        ``<prefix>-<NN>-<slug>``, numbered past every ``event_type`` row ever booked.

    """
    shape = re.compile(rf"^{re.escape(prefix)}-([0-9]+)-")
    numbers = [
        int(match.group(1))
        for row in ledger.query(event_type=event_type, stream="history")
        if (match := shape.match(row.id))
    ]
    return f"{prefix}-{max(numbers, default=0) + 1:02d}-{slug}"
