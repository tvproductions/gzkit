"""Re-measure the Build-to-1.0 campaign's reckoning against the live tree.

Read-only. Runs `git`, reads the ledger and walks the tree; writes nothing and
makes no network call.

Carries NO literals from its authoring date: every figure is derived at run time,
so re-running this on a later tree reports that tree. The campaign edition cites
this script rather than transcribing its output, per the operator's 2026-09-20
"Pointer, not value" ruling.

The 90-day window is measured from the run date, matching how the 07-18 and 08-16
passes measured theirs -- so a later run's window is a later window, and the
figures are comparable in method rather than in period.

Scorecard tallies are deliberately NOT computed here. `gz validate
--advisory-scorecard` already checks the Summary roll-up against the scored rows,
and a second counter that disagreed with it would be a fresh instance of the
defect this campaign is chasing -- a draft of this script produced 70/34/71/1
against the validated 71/33/72/0 and was removed rather than reconciled.
"""

import json
import re
import subprocess
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
WINDOW = "90 days ago"


def git(*args):
    """Return stdout of a git command run in the repository root."""
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
    ).stdout


def commit_mix():
    """Return the conventional-commit type mix over the measurement window."""
    subjects = [s for s in git("log", f"--since={WINDOW}", "--format=%s").splitlines() if s]
    kinds = Counter()
    for subject in subjects:
        match = re.match(r"^(\w+)", subject)
        kinds[match.group(1) if match else "other"] += 1
    sync = sum(1 for subject in subjects if "gz git-sync" in subject)
    return len(subjects), kinds, sync


def ledger_events():
    """Return the total ledger event count and the airlock transit tallies."""
    path = REPO / ".gzkit" / "ledger.jsonl"
    total = 0
    transits = Counter()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            total += 1
            if '"airlock_in"' in line or '"airlock_out"' in line:
                try:
                    transits[json.loads(line)["event"]] += 1
                except (json.JSONDecodeError, KeyError):
                    continue
    return total, transits


def loc(root, pattern="*.py"):
    """Return the total physical line count under a directory."""
    return sum(
        len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        for path in (REPO / root).rglob(pattern)
        if "__pycache__" not in path.parts
    )


def oversized_modules(threshold=600):
    """Return the modules over the stated line threshold."""
    found = []
    for path in (REPO / "src").rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        if lines > threshold:
            found.append((path.relative_to(REPO).as_posix(), lines))
    return found


def main():
    """Print the re-measured reckoning."""
    total, kinds, sync = commit_mix()
    events, transits = ledger_events()
    adrs = list((REPO / "docs" / "design" / "adr").rglob("ADR-*.md"))
    pool = list((REPO / "docs" / "design" / "adr" / "pool").glob("*.md"))
    briefs = list((REPO / "docs" / "design" / "adr").rglob("obpis/OBPI-*.md"))
    oversized = oversized_modules()

    assert total, "no commits in the window -- is this a git checkout?"
    assert events, "ledger is empty"
    assert adrs, "no ADRs found"

    print(f"=== commit mix, {WINDOW} to today ===")
    print(f" total commits: {total}")
    for kind, count in kinds.most_common(6):
        print(f"   {kind:<8} {count:>5}  ({100 * count / total:.1f}%)")
    print(f"   of which `gz git-sync`: {sync} ({100 * sync / total:.1f}% of all commits)")

    print("\n=== airlock (cumulative, whole ledger) ===")
    inn, out = transits.get("airlock_in", 0), transits.get("airlock_out", 0)
    print(f" airlock_in={inn}  airlock_out={out}  unaccounted exits={inn - out}")

    print("\n=== surface ===")
    print(f" src LOC:        {loc('src'):>7}")
    print(f" test LOC:       {loc('tests'):>7}")
    print(f" ADRs:           {len(adrs):>7}   (pool: {len(pool)}; glob: **/ADR-*.md)")
    print(f" OBPI briefs:    {len(briefs):>7}   (glob: **/obpis/OBPI-*.md)")
    print(f" ledger events:  {events:>7}")

    print(f"\n=== oversized modules (>600 lines): {len(oversized)} ===")
    for path, lines in sorted(oversized, key=lambda row: -row[1])[:5]:
        print(f"   {lines:>5}  {path}")
    if len(oversized) > 5:
        print(f"   ... and {len(oversized) - 5} more")


if __name__ == "__main__":
    main()
