"""Census the ARB receipt store so a harvest reports its reach (GHI #594).

`collect_arb_advice` and `collect_patterns` both walk the newest N files and skip
every receipt whose ``schema`` is not the lint schema. Neither reported the
denominator, so both looked busy: ``scanned_receipts`` counted what they read and
nothing counted what they walked past. Measured on the live store that gap is
130 read against 3,286 present — and 2,265 step receipts that no harvester in the
codebase is able to read at all.

This module supplies the census. It is a separate pass over the store rather than
a tally inside the harvest loop, because the harvest loop only ever sees the
window a ``--limit`` already selected — counting there would report reach against
the window and always look complete, which is the exact self-narrowing denominator
:class:`gzkit.efficacy.StoreCoverage` exists to refuse.

The pass reads each file's ``schema`` field. That is deliberate over deriving the
kind from the filename prefix: the prefix is a naming convention and the schema is
the contract, and a census that trusted the convention would misreport precisely
when a producer drifted from it.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from gzkit.efficacy import StoreCoverage


def _schema_of(path: Path) -> str:
    """Return a receipt's declared schema, or a marker for an unreadable one."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return "<unparseable>"
    if not isinstance(payload, dict):
        return "<not-an-object>"
    schema = payload.get("schema")
    return schema if isinstance(schema, str) and schema else "<no-schema>"


def measure_receipt_coverage(
    root: Path,
    *,
    readable_schema: str,
    covered: int,
    truncated: bool,
) -> StoreCoverage:
    """Pair a store census with what the caller actually read.

    Args:
        root: the receipts directory.
        readable_schema: the schema id this consumer is able to process.
        covered: how many receipts the caller actually read this run.
        truncated: whether a limit stopped the caller before exhausting the
            eligible set.

    Returns:
        A :class:`StoreCoverage` whose ``unreadable`` lists every other schema
        present, descending by count — so the report names what has no harvester
        rather than silently excluding it from the denominator.

    """
    schemas: Counter[str] = Counter()
    for path in sorted(root.glob("*.json")) if root.is_dir() else []:
        schemas[_schema_of(path)] += 1

    eligible = schemas.get(readable_schema, 0)
    unreadable = sorted(
        ((kind, count) for kind, count in schemas.items() if kind != readable_schema),
        key=lambda item: (-item[1], item[0]),
    )
    return StoreCoverage(
        store=root.as_posix(),
        present=sum(schemas.values()),
        eligible=eligible,
        covered=covered,
        truncated=truncated,
        unreadable=unreadable,
    )


__all__ = ["measure_receipt_coverage"]
