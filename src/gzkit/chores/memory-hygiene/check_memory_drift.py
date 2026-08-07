"""Witness that the auto-memory surface has not drifted since the last hygiene pass.

The acceptance criterion this backs must be able to FAIL for the reason the chore
exists (GHI #743): a criterion that cannot fail when the chore's subject changes is
green by construction. `test -f MEMORY.md` witnessed that an index was written once,
never that it still describes the surface — and the criterion that replaced it
observed the instructions-files budget, a different surface entirely.

What this observes instead: whether any memory file postdates the chore's last
recorded pass. A new `feedback_`/`project_` memory written after the last hygiene run
is precisely the shadow-persistence the chore exists to catch — a correction that
went to machine-local memory instead of a governed artifact.

Exit 0 when the surface is clean or absent; exit 1 when memories postdate the pass.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROOF_LOG = Path(__file__).parent / "proofs" / "CHORE-LOG.md"


def memory_dir(cwd: Path, home: Path) -> Path:
    """Return the Claude Code auto-memory directory for a project checkout.

    Derived from the checkout path rather than hardcoded: the shipped wheel used to
    carry the gzkit maintainer's own absolute project path literally, so every
    adopter's copy of this chore checked a file on a machine they do not own.
    """
    slug = str(cwd).replace("/", "-").replace("\\", "-").replace(":", "")
    return home / ".claude" / "projects" / slug / "memory"


def drifted_memories(mem_dir: Path, since_mtime: float) -> list[Path]:
    """Return memory files modified after the last recorded hygiene pass."""
    if not mem_dir.is_dir():
        return []
    return sorted(p for p in mem_dir.glob("*.md") if p.stat().st_mtime > since_mtime)


def main() -> int:
    """Report memory drift since the last pass; return the process exit code."""
    mem_dir = memory_dir(Path.cwd(), Path.home())
    if not mem_dir.is_dir():
        print(f"memory surface absent at {mem_dir} — nothing to audit")
        return 0

    if not PROOF_LOG.is_file():
        print(f"no hygiene pass recorded at {PROOF_LOG} — run the chore to establish one")
        return 1

    drifted = drifted_memories(mem_dir, PROOF_LOG.stat().st_mtime)
    total = len(list(mem_dir.glob("*.md")))
    if drifted:
        print(f"{len(drifted)} of {total} memories postdate the last hygiene pass:")
        for path in drifted:
            print(f"  {path.name}")
        print("Classify each per CHORE.md § Policy, migrate process content to a")
        print("governed artifact, then re-run the chore to record a fresh pass.")
        return 1

    print(f"{total} memories, none newer than the last hygiene pass — clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
