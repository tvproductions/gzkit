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

Exit codes: 0 fresh, 1 usage/IO error, 3 policy breach (stale evidence).
"""

from __future__ import annotations

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
}


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


def main(argv: list[str]) -> int:
    """Report whether *slug*'s proofs postdate the surfaces they audit."""
    if len(argv) != 1 or argv[0] not in _AUDITED_SURFACES:
        print(
            f"usage: check_proof_freshness.py <{' | '.join(sorted(_AUDITED_SURFACES))}>",
            file=sys.stderr,
        )
        return 1
    slug = argv[0]
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
