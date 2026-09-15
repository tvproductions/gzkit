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
being written right now. The audited surfaces are the chore's declared
``staleness.surfaces`` in ``.gzkit/chores/registry.json``; this gate holds no
surface map of its own, so ``gz chores status`` and this gate read one
declaration (GHI #936).

That comparison cannot express a chore whose staleness is driven from *outside*
the repository. ``frontier-model-card-currency`` scans vendor publication hubs;
no repo file's commit date moves when Anthropic or OpenAI ships a system card,
so its registry stays internally valid — and its criteria stay green — for as
long as nobody looks. Measured 2026-09-02 under GHI #935: both criteria passed
while the Mythos-class ``current`` entry had been superseded since 2026-09-01
(GHI #934), found only because an operator happened to supply the new card URL.

Such chores are gated on the second arm below: wall-clock elapsed time since
the procedure last ran. A chore takes this arm when its class declaration in
``.gzkit/chores/registry.json`` says ``staleness.signal: elapsed-time``, and its
``periodDays`` is the maximum age — the declaration is the one authority, so the
gate holds no interval of its own (GHI #999).

The witness is the chore's declared ``staleness.artifacts``: the record its
procedure writes. It is never ``CHORE-LOG.md``. The run blocks there are written
by ``gz chores run`` only when every criterion passes, and this gate IS a
criterion, so reading them left an overdue chore with no run that could clear
it; a bare run inside the period also wrote a fresh block and extended the clock
with no scan (GHI #935, reopened). Operator ruling 2026-09-14, verbatim
*"Declare it (Recommended)"*.

Exit codes: 0 fresh, 1 usage/IO error, 3 policy breach (stale evidence).
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.chores_staleness import git_artifact_changed

_PROJECT_ROOT = Path(__file__).resolve().parents[1]

sys.stdout.reconfigure(encoding="utf-8")  # ty: ignore[unresolved-attribute]

# Chores whose staleness is externally driven have no in-repo signal to key on,
# so they gate on elapsed time instead of on a surface's commit date. The maximum
# age is the chore's declared ``staleness.periodDays``, read by
# ``_declared_period``; this module holds no interval of its own (GHI #999).
#
# Dated record (2026-09-02, GHI #935), not the authority: the
# frontier-model-card-currency period of 30d was derived from measured Anthropic
# tracked-tier publication intervals (n=4 across 2026-04-16..2026-09-01: min 12d,
# median 40.5d, mean 34.5d) — the largest interval that keeps at most one release
# outstanding against that mean. Re-derive it when the observed cadence moves.
# permission-consent-drift took this arm at its 2026-09-13 calibration because
# `.claude/settings.local.json` is gitignored and grows with no commit.


def _declared_staleness(slug: str) -> dict | None:
    """Return *slug*'s declared ``staleness`` object, or None if it declares none."""
    registry = _PROJECT_ROOT / ".gzkit" / "chores" / "registry.json"
    try:
        entries = json.loads(registry.read_text(encoding="utf-8")).get("chores", [])
    except (OSError, json.JSONDecodeError, AttributeError):
        return None
    for entry in entries:
        if isinstance(entry, dict) and entry.get("slug") == slug:
            staleness = entry.get("staleness")
            return staleness if isinstance(staleness, dict) else None
    return None


def _declared_period(slug: str) -> int | None:
    """Return *slug*'s declared elapsed-time ``periodDays``, or None if it declares none."""
    staleness = _declared_staleness(slug) or {}
    if staleness.get("signal") != "elapsed-time":
        return None
    period = staleness.get("periodDays")
    return period if isinstance(period, int) and period > 0 else None


def _declared_surfaces(slug: str) -> tuple[str, ...] | None:
    """Return *slug*'s declared content-delta ``surfaces``, or None if it declares none."""
    staleness = _declared_staleness(slug) or {}
    surfaces = staleness.get("surfaces")
    if staleness.get("signal") != "content-delta" or not isinstance(surfaces, list) or not surfaces:
        return None
    return tuple(str(surface) for surface in surfaces)


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


def _declared_artifacts(slug: str) -> tuple[str, ...]:
    """Return *slug*'s declared elapsed-time scan ``artifacts``, empty if it declares none."""
    staleness = _declared_staleness(slug) or {}
    artifacts = staleness.get("artifacts")
    if staleness.get("signal") != "elapsed-time" or not isinstance(artifacts, list):
        return ()
    return tuple(str(artifact) for artifact in artifacts)


def _check_scan_interval(slug: str, interval_days: int) -> int:
    """Report whether *slug*'s declared scan artifact changed within *interval_days*."""
    print(f"scan-interval gate — {slug}")
    print(f"  maximum age:  {interval_days}d")
    artifacts = _declared_artifacts(slug)
    if not artifacts:
        print(
            f"\n{slug} declares no staleness.artifacts, so this gate has no scan record to "
            f"read.\n"
            f"    Why: the only record left is the PASS block `gz chores run` writes, and "
            f"only a run that passes this gate writes one, so an overdue chore could "
            f"never clear (GHI #935).\n"
            f"    Fix: declare the file its procedure writes as staleness.artifacts in "
            f".gzkit/chores/registry.json.",
            file=sys.stderr,
        )
        return 1
    print(f"  scan record:  {', '.join(artifacts)}")

    now = datetime.now(UTC)
    newest = git_artifact_changed(_PROJECT_ROOT, now)(artifacts)
    if newest is None:
        print("  last scan:    never", file=sys.stderr)
        print(
            f"\nPOLICY BREACH:\n  {slug} has no scan on record.\n"
            f"    Why: absence of a record is not evidence of a recent scan, and this "
            f"chore's subject changes outside the repository — nothing else will "
            f"signal that it is stale.\n"
            f"    Fix: perform the scan its CHORE.md describes, writing its scan record, "
            f"then run `uv run gz chores run {slug}` and commit both.",
            file=sys.stderr,
        )
        return 3

    age = (now - newest).days
    print(f"  last scan:    {newest.date().isoformat()} ({age}d ago)")
    if age > interval_days:
        print(
            f"\nPOLICY BREACH:\n  {slug} last scanned {newest.date().isoformat()}, "
            f"{age}d ago, exceeding its {interval_days}d interval.\n"
            f"    Why: this chore's subject moves where no commit records it, so only "
            f"its scan observes that; its other criteria report green for as long as "
            f"nobody looks, and re-running them is not looking.\n"
            f"    Fix: perform the scan its CHORE.md describes, writing its scan record, "
            f"then run `uv run gz chores run {slug}` and commit both.",
            file=sys.stderr,
        )
        return 3

    print("\nPASS: the scan record changed within the scan interval.")
    return 0


def main(argv: list[str]) -> int:
    """Report whether *slug*'s evidence is current, by whichever arm gates it."""
    period = _declared_period(argv[0]) if len(argv) == 1 else None
    if period is not None:
        return _check_scan_interval(argv[0], period)
    surfaces = _declared_surfaces(argv[0]) if len(argv) == 1 else None
    if surfaces is None:
        print(
            "usage: check_proof_freshness.py <slug of a chore declaring staleness.signal "
            "elapsed-time, or content-delta with surfaces>",
            file=sys.stderr,
        )
        return 1
    slug = argv[0]
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
