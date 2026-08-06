"""Shared `--older-than` duration grammar for retention verbs.

Two verbs now age a governed store — ``gz handoff archive`` (GHI #585) and
``gz arb archive`` (GHI #594) — and both spell the threshold ``--older-than 30d``.
The grammar lives here once so the two cannot drift into accepting different
values under the same flag name, which is the ``cli.md`` § Core Principles
consistency failure and, more generally, the N-readers-of-one-shape pattern this
repo keeps paying for (four copies of the REQ-kind taxonomy, ~20 REQ-identifier
regexes). A third retention verb derives from here rather than re-spelling it.
"""

from __future__ import annotations

from gzkit.commands.common import console


def parse_older_than_days(raw: str) -> int:
    """Parse an ``--older-than`` duration like ``30d`` or ``30`` into a day count.

    Exits 1 on a non-integer or negative value — a retention threshold that cannot
    be read must never fall through to a default, because the default would silently
    age a store the operator did not intend to age.
    """
    token = raw.strip().lower().removesuffix("d")
    try:
        days = int(token)
    except ValueError:
        console.print(f"[red]invalid --older-than value:[/red] {raw!r} (expected e.g. 30d)")
        raise SystemExit(1) from None
    if days < 0:
        console.print(f"[red]invalid --older-than value:[/red] {raw!r} (must be non-negative)")
        raise SystemExit(1)
    return days


__all__ = ["parse_older_than_days"]
