"""Index the authored ``## Class of failure`` statements across the GHI corpus.

Every GHI authored through ``/ghi-author`` carries a ``## Class of failure``
section — the author's own root-cause diagnosis, written at filing time. That
makes the corpus a recurrence dataset that already exists: measured 2026-08-07 by
this module, 288 of 333 closed GHIs carry the section (87%), and 71 of those 288
(25%) explicitly declare themselves a recurrence of a named prior class.

Nothing read it. ``#554`` could say *"5th instance in 4 weeks"* only because a
human happened to remember, and ``#732``'s *"(4th miss)"* was caught the same
way. This module makes that detection mechanical, so a chain surfaces before the
next instance is authored rather than after.

The core takes records as a parameter and never reaches for ``gh`` itself
(`.gzkit/rules/hexagonal-architecture.md` rules 1 and 4) — the chore's snapshot
step is the adapter. That keeps every function here testable with no network.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

#: Chains shorter than this are noise — two GHIs sharing a cause is a pair, not
#: yet a family worth a campaign box.
DEFAULT_MIN_DEPTH = 3

#: The section every ``/ghi-author`` GHI carries. Captured up to the next H2.
_SECTION = re.compile(r"##\s*Class of failure\s*\n+(.*?)(?=\n##\s|\Z)", re.IGNORECASE | re.DOTALL)

#: Phrases an author uses when naming a prior class. Deliberately generous:
#: a missed recurrence is the failure this module exists to prevent, while a
#: false positive costs one line of operator review.
_RECURRENCE = re.compile(
    r"same (?:class|root-cause|family|shape|defect)"
    r"|recurrence of"
    r"|\b\d+(?:st|nd|rd|th) instance"
    r"|class as GHI"
    r"|sibling"
    r"|regression #"
    r"|re-emerge"
    r"|\bthis is the \d+",
    re.IGNORECASE,
)

#: A GHI reference inside a class statement (``#537``). Three or four digits so
#: ordinary numbers ("#1 priority") do not read as citations.
_CITATION = re.compile(r"#(\d{3,4})\b")

_MARKUP = re.compile(r"[*`_]")


class FailureClassEntry(BaseModel):
    """One GHI's authored root-cause diagnosis, normalized."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    number: int = Field(..., description="GHI number")
    title: str = Field(..., description="GHI title")
    statement: str = Field(..., description="Normalized `## Class of failure` prose")
    declares_recurrence: bool = Field(
        ..., description="True when the statement names itself a recurrence of a prior class"
    )
    cites: tuple[int, ...] = Field((), description="GHI numbers named inside the statement")


class RecurrenceChain(BaseModel):
    """A set of GHIs linked by authored same-class citations."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    members: tuple[int, ...] = Field(..., description="All GHIs in the chain, ascending")
    declared: tuple[int, ...] = Field(
        ..., description="Members whose own statement declared the recurrence"
    )

    @property
    def depth(self) -> int:
        """Number of GHIs in the chain."""
        return len(self.members)


def extract_class_statement(body: str | None) -> str | None:
    """Return the normalized ``## Class of failure`` prose, or None when absent."""
    if not body:
        return None
    found = _SECTION.search(body)
    if found is None:
        return None
    text = " ".join(_MARKUP.sub("", found.group(1)).split())
    return text or None


def parse_entry(record: Mapping[str, object]) -> FailureClassEntry | None:
    """Build an entry from one issue record, or None when it carries no section.

    ``record`` is a plain mapping with ``number``, ``title``, and ``body`` keys —
    the shape ``gh issue list --json`` emits, taken as a parameter rather than
    fetched, so no adapter is required to exercise this.
    """
    body = record.get("body")
    statement = extract_class_statement(body if isinstance(body, str) else None)
    if statement is None:
        return None
    number = record.get("number")
    if not isinstance(number, int):
        return None
    cites = tuple(sorted({int(n) for n in _CITATION.findall(statement) if int(n) != number}))
    return FailureClassEntry(
        number=number,
        title=str(record.get("title") or ""),
        statement=statement,
        declares_recurrence=bool(_RECURRENCE.search(statement)),
        cites=cites,
    )


def build_index(records: Iterable[Mapping[str, object]]) -> tuple[FailureClassEntry, ...]:
    """Return one entry per record carrying a class statement, ascending by number."""
    entries = [e for e in (parse_entry(r) for r in records) if e is not None]
    return tuple(sorted(entries, key=lambda e: e.number))


def resolve_chains(entries: Sequence[FailureClassEntry]) -> tuple[RecurrenceChain, ...]:
    """Group GHIs into chains linked by authored same-class citations.

    Only a *declaring* entry contributes edges. A GHI that merely mentions
    another issue in passing does not merge two families — the author's
    recurrence phrasing is what makes the link, which is why the edge set is
    built from ``declares_recurrence`` rather than from citations alone.
    """
    parent: dict[int, int] = {}

    def find(x: int) -> int:
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    declaring = [e for e in entries if e.declares_recurrence]
    for entry in declaring:
        for cited in entry.cites:
            union(entry.number, cited)

    groups: dict[int, set[int]] = {}
    for entry in declaring:
        groups.setdefault(find(entry.number), set()).update({entry.number, *entry.cites})

    declared_numbers = {e.number for e in declaring}
    chains = [
        RecurrenceChain(
            members=tuple(sorted(members)),
            declared=tuple(sorted(n for n in members if n in declared_numbers)),
        )
        for members in groups.values()
    ]
    return tuple(sorted(chains, key=lambda c: (-c.depth, c.members)))


def summarize(
    entries: Sequence[FailureClassEntry], chains: Sequence[RecurrenceChain]
) -> dict[str, object]:
    """Return the headline counts a report and a run log both need."""
    declaring = [e for e in entries if e.declares_recurrence]
    return {
        "entries": len(entries),
        "declaring_recurrence": len(declaring),
        "recurrence_rate": round(len(declaring) / len(entries), 4) if entries else 0.0,
        "chains": len(chains),
        "chains_3_plus": sum(1 for c in chains if c.depth >= 3),
        "deepest_chain": max((c.depth for c in chains), default=0),
    }


def render_report(
    entries: Sequence[FailureClassEntry],
    chains: Sequence[RecurrenceChain],
    *,
    min_depth: int = 3,
) -> str:
    """Render the operator-facing markdown report."""
    stats = summarize(entries, chains)
    titles = {e.number: e.title for e in entries}
    lines = [
        "# Failure-class index",
        "",
        f"- GHIs carrying `## Class of failure`: **{stats['entries']}**",
        f"- Declaring a recurrence of a prior class: **{stats['declaring_recurrence']}**"
        f" ({stats['recurrence_rate']:.0%})",
        f"- Chains: **{stats['chains']}** ({stats['chains_3_plus']} of depth >= {min_depth})",
        f"- Deepest chain: **{stats['deepest_chain']}**",
        "",
        f"## Chains of depth >= {min_depth}",
        "",
    ]
    deep = [c for c in chains if c.depth >= min_depth]
    if not deep:
        lines.append("_None._")
    for chain in deep:
        members = ", ".join(f"#{n}" for n in chain.members)
        lines.append(f"### depth {chain.depth} — {members}")
        for number in chain.members:
            title = titles.get(number, "(outside the indexed window)")
            marker = "*" if number in chain.declared else " "
            lines.append(f"- {marker} #{number} {title}")
        lines.append("")
    lines.append("`*` = this GHI's own class statement declared the recurrence.")
    return "\n".join(lines) + "\n"


def write_report(text: str, proofs_dir: Path, *, stamp: str) -> Path:
    """Write the report under the chore's proofs directory and return its path."""
    proofs_dir.mkdir(parents=True, exist_ok=True)
    path = proofs_dir / f"failure-class-index-{stamp}.md"
    path.write_text(text, encoding="utf-8")
    return path


def write_run_log(run: Mapping[str, object], proofs_dir: Path, *, stamp: str) -> Path:
    """Write run telemetry so a zero-finding run is legible (GHI #614 shape)."""
    proofs_dir.mkdir(parents=True, exist_ok=True)
    path = proofs_dir / f"run-{stamp}.json"
    path.write_text(json.dumps(dict(run), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def load_snapshot(path: Path) -> list[Mapping[str, object]]:
    """Load a ``gh issue list --json number,title,body`` snapshot.

    Fails soft: an unreadable or malformed snapshot yields an empty corpus rather
    than raising, so the chore reports "nothing indexed" instead of crashing a
    maintenance run.
    """
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    return [r for r in data if isinstance(r, dict)] if isinstance(data, list) else []


def _default_proofs_dir() -> Path:
    """Proofs land under the chore that owns this surface."""
    return Path.cwd() / ".gzkit" / "chores" / "failure-class-index" / "proofs"


def main(argv: list[str] | None = None) -> int:
    """Index a GHI snapshot's class statements and report (or write) the chains."""
    parser = argparse.ArgumentParser(description="Index GHI `## Class of failure` statements.")
    parser.add_argument(
        "--snapshot",
        type=Path,
        required=True,
        help="Path to a `gh issue list --json number,title,body` snapshot.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the summary without writing the report or run telemetry.",
    )
    parser.add_argument("--proofs-dir", type=Path, default=None)
    parser.add_argument("--min-depth", type=int, default=DEFAULT_MIN_DEPTH)
    parser.add_argument(
        "--stamp",
        default="latest",
        help="Filename stamp for emitted proofs; pass a UTC date for an archival run.",
    )
    args = parser.parse_args(argv)

    records = load_snapshot(args.snapshot)
    entries = build_index(records)
    chains = resolve_chains(entries)
    stats = summarize(entries, chains)

    # Always report the scan counts. A run that indexes 300 issues and finds no
    # chain is a different fact from a run that read an empty snapshot, and only
    # stdout can carry that under --dry-run (the GHI #614 negative-signal shape).
    sys.stdout.write(
        f"failure-class-index: {stats['chains_3_plus']} chain(s) of depth >= {args.min_depth}\n"
    )
    sys.stdout.write(
        f"  read {len(records)} record(s), indexed {stats['entries']} class statement(s), "
        f"{stats['declaring_recurrence']} declaring recurrence "
        f"({stats['recurrence_rate']:.0%}), deepest chain {stats['deepest_chain']}\n"
    )
    for chain in chains:
        if chain.depth >= args.min_depth:
            members = ", ".join(f"#{n}" for n in chain.members)
            sys.stdout.write(f"  [depth {chain.depth}] {members}\n")

    if args.dry_run:
        return 0

    proofs_dir = args.proofs_dir or _default_proofs_dir()
    text = render_report(entries, chains, min_depth=args.min_depth)
    report = write_report(text, proofs_dir, stamp=args.stamp)
    log = write_run_log({**stats, "records_read": len(records)}, proofs_dir, stamp=args.stamp)
    sys.stdout.write(f"  wrote report to {report}\n")
    sys.stdout.write(f"  recorded run telemetry to {log}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
