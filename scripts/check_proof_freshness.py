#!/usr/bin/env python3
"""Freshness gate for the control-surface audit chores.

The four ``control-surface-*`` chores gate on ``test -f <proofs>/<name>.md`` —
existence, never currency. A report written once satisfies that criterion
forever, so the chore reports ``All criteria pass`` while its evidence describes
a surface that has since moved. Measured on 2026-08-01: ALL FOUR chores carried
proofs older than the surfaces they audit — two frozen at 2026-05-10 and two at
2026-07-16, against surfaces last moved 2026-07-29 and 2026-08-01 — and all four
were reporting green throughout.

The 2026-05-10 pair read as 2026-06-25 until ``_iso`` was corrected on
2026-08-01; that date was the local reflog floor, not a commit date. See
``_iso``.

This gate compares git commit dates, not filesystem mtimes: a fresh clone or a
branch switch rewrites every mtime, which would make an mtime comparison report
whatever the checkout did last rather than what the repository knows.

A proof is stale when any file in the surface it audits has a newer last-commit
date than the proof itself. Uncommitted proofs are treated as fresh — they are
being written right now.

That comparison cannot express a chore whose staleness is driven from *outside*
the repository. ``frontier-model-card-currency`` scans vendor publication hubs;
no repo file's commit date moves when Anthropic or OpenAI ships a system card,
so its registry stays internally valid — and its criteria stay green — for as
long as nobody looks. Measured 2026-09-02 under GHI #935: both criteria passed
while the Mythos-class ``current`` entry had been superseded since 2026-09-01
(GHI #934), found only because an operator happened to supply the new card URL.

Such chores are gated on the second arm below: wall-clock elapsed time since
the procedure last ran, keyed by ``_SCAN_INTERVALS``. The witness is the
timestamped block ``gz chores run`` appends to ``CHORE-LOG.md``, never a
hand-authored narrative heading — see ``_newest_scan_timestamp``.

Exit codes: 0 fresh, 1 usage/IO error, 3 policy breach (stale evidence).
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[unresolved-attribute]

# Each chore's proofs are only as good as the surfaces they were derived from.
_AUDITED_SURFACES: dict[str, tuple[str, ...]] = {
    "control-surface-rule-conflicts": (".gzkit/rules",),
    "control-surface-skill-rule-reachability": (".gzkit/rules", ".gzkit/skills"),
    "control-surface-rule-vs-check-drift": (
        ".gzkit/rules",
        "src/gzkit/governance/trust_audits",
    ),
    "control-surface-permission-consent-drift": (".gzkit/rules", ".claude/settings.json"),
    # Vocabulary evidence goes stale when the schema that declares types moves,
    # or when a producer lands that could drain a never-fired entry.
    "ledger-vocabulary-inertness": (
        "src/gzkit/schemas/ledger.json",
        "src/gzkit/ledger_events.py",
        "src/gzkit/events.py",
    ),
    # Pass D audits what *invokes* a validator, so its evidence goes stale when a
    # caller surface moves — the CLI parser (which scopes exist), the `gz check`
    # step registry, or any of the three gating surfaces.
    "control-surface-validator-reachability": (
        "src/gzkit/cli",
        "src/gzkit/commands/quality.py",
        ".pre-commit-config.yaml",
        ".github/workflows",
        ".claude/hooks",
    ),
}

# Chores whose staleness is externally driven have no in-repo signal to key on,
# so they gate on elapsed time instead of on a surface's commit date. The value
# is the maximum age, in days, of the newest recorded run.
#
# 30d is derived from measured Anthropic tracked-tier publication intervals
# (n=4 across 2026-04-16..2026-09-01: min 12d, median 40.5d, mean 34.5d). It is
# the largest interval that keeps at most one release outstanding against that
# mean, and it would have fired on 2026-09-01 — the publication day of the card
# whose 30 days of undetected staleness produced GHI #935. Re-derive it, do not
# transcribe it, when the observed cadence moves.
_SCAN_INTERVALS: dict[str, int] = {
    "frontier-model-card-currency": 30,
}

# ``gz chores run`` appends "## <ISO timestamp>"; findings sections are written
# by hand as "## <date> — <prose>". Only the former witnesses a governed run.
_RUN_HEADING = re.compile(r"^##[ \t]+(\d{4}-\d{2}-\d{2}T[0-9:.+\-]+)[ \t]*$", re.MULTILINE)


def _last_commit_epoch(path: str) -> int | None:
    """Return the unix time of the newest commit touching *path*, or None."""
    completed = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", path],
        cwd=_PROJECT_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        return None
    raw = completed.stdout.strip()
    return int(raw) if raw.isdigit() else None


def _iso(epoch: int) -> str:
    """Render a commit epoch as an ISO date.

    Formats the epoch directly. The prior implementation asked git via
    ``git show -s --format=%cs @{<epoch>}``, but ``@{<n>}`` is git's
    *reflog-relative* revision syntax, not an epoch formatter: it resolves
    against the local reflog and clamps to the reflog floor for anything
    older, emitting ``warning: log for 'main' only goes back to ...``. Every
    epoch predating the reflog therefore rendered as the same wrong date,
    which is why three separate chores all reported ``2026-06-25``. Only the
    printed prose was affected — ``main`` compares raw epochs, so the exit
    code was always sound.
    """
    return datetime.fromtimestamp(epoch, UTC).date().isoformat()


def _newest_scan_timestamp(log_text: str) -> datetime | None:
    """Return the newest recorded run stamp in *log_text*, or None.

    Reads only the timestamped blocks ``gz chores run`` appends. Narrative
    headings a human wrote (``## 2026-09-02 — findings``) are deliberately not
    matched: keying on them would make appending prose enough to mark the chore
    fresh, rebuilding the gate whose only witness is that an artifact exists
    (``AGENTS.md`` § DO IT RIGHT). File order is not trusted either — the newest
    stamp wins wherever it sits.
    """
    stamps: list[datetime] = []
    for raw in _RUN_HEADING.findall(log_text):
        try:
            when = datetime.fromisoformat(raw)
        except ValueError:
            continue
        # A stamp written without an offset is read as UTC rather than skipped;
        # dropping it would silently age the log toward a false breach.
        stamps.append(when if when.tzinfo else when.replace(tzinfo=UTC))
    return max(stamps, default=None)


def _check_scan_interval(slug: str, interval_days: int) -> int:
    """Report whether *slug*'s last recorded run is within *interval_days*."""
    log = _PROJECT_ROOT / ".gzkit" / "chores" / slug / "proofs" / "CHORE-LOG.md"
    print(f"scan-interval gate — {slug}")
    print(f"  maximum age:  {interval_days}d")

    newest = _newest_scan_timestamp(log.read_text(encoding="utf-8")) if log.is_file() else None
    if newest is None:
        reason = (
            "no CHORE-LOG.md" if not log.is_file() else "no timestamped run block in CHORE-LOG.md"
        )
        print("  last run:     never", file=sys.stderr)
        print(
            f"\nPOLICY BREACH:\n  {slug} has no run on record ({reason}).\n"
            f"    Why: absence of a record is not evidence of a recent run, and this "
            f"chore's subject changes outside the repository — nothing else will "
            f"signal that it is stale.\n"
            f"    Fix: run `uv run gz chores run {slug}` and commit the log.",
            file=sys.stderr,
        )
        return 3

    age = (datetime.now(UTC) - newest).days
    print(f"  last run:     {newest.date().isoformat()} ({age}d ago)")
    if age > interval_days:
        print(
            f"\nPOLICY BREACH:\n  {slug} last ran {newest.date().isoformat()}, "
            f"{age}d ago, exceeding its {interval_days}d interval.\n"
            f"    Why: this chore's criteria check the shape of what was already "
            f"consumed, never whether anything newer has published. They report "
            f"green for as long as nobody looks.\n"
            f"    Fix: run `uv run gz chores run {slug}`, route any drift it "
            f"finds, and commit the log.",
            file=sys.stderr,
        )
        return 3

    print("\nPASS: the last recorded run is within the scan interval.")
    return 0


def main(argv: list[str]) -> int:
    """Report whether *slug*'s evidence is current, by whichever arm gates it."""
    known = sorted({*_AUDITED_SURFACES, *_SCAN_INTERVALS})
    if len(argv) != 1 or argv[0] not in known:
        print(f"usage: check_proof_freshness.py <{' | '.join(known)}>", file=sys.stderr)
        return 1
    slug = argv[0]
    if slug in _SCAN_INTERVALS:
        return _check_scan_interval(slug, _SCAN_INTERVALS[slug])
    surfaces = _AUDITED_SURFACES[slug]
    proofs_dir = _PROJECT_ROOT / ".gzkit" / "chores" / slug / "proofs"
    proofs = sorted(p for p in proofs_dir.glob("*.md") if p.name != "CHORE-LOG.md")

    if not proofs:
        print(f"no proof artifacts under {proofs_dir.relative_to(_PROJECT_ROOT)}", file=sys.stderr)
        return 3

    surface_epoch = max(
        (e for s in surfaces if (e := _last_commit_epoch(s)) is not None), default=0
    )
    print(f"proof-freshness gate — {slug}")
    print(f"  audited surfaces:  {', '.join(surfaces)}")
    print(f"  surface last moved: {_iso(surface_epoch)}")

    stale: list[tuple[str, int]] = []
    for proof in proofs:
        rel = proof.relative_to(_PROJECT_ROOT).as_posix()
        proof_epoch = _last_commit_epoch(rel)
        if proof_epoch is None:
            print(f"  {proof.name:<28} uncommitted — treated as fresh")
            continue
        marker = "STALE" if proof_epoch < surface_epoch else "fresh"
        print(f"  {proof.name:<28} {_iso(proof_epoch)}  {marker}")
        if proof_epoch < surface_epoch:
            stale.append((rel, proof_epoch))

    if stale:
        print("\nPOLICY BREACH:", file=sys.stderr)
        for rel, epoch in stale:
            print(
                f"  {rel} was last committed {_iso(epoch)}, before its audited surface "
                f"last moved ({_iso(surface_epoch)}).\n"
                f"    Why: this chore's acceptance previously gated on `test -f`, which "
                f"passes forever once a report exists and cannot see that the evidence "
                f"now describes a surface that has changed.\n"
                f"    Fix: re-run the {slug} audit and commit refreshed proofs. Touching "
                f"the file without redoing the analysis restores the green-by-"
                f"construction gate this replaced.",
                file=sys.stderr,
            )
        return 3

    print("\nPASS: every proof postdates the surfaces it audits.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
