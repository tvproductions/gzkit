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

import json
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


def auto_memory_enabled(home: Path) -> bool | None:
    """Return Claude Code's ``autoMemoryEnabled`` setting, or None when it is not declared.

    The witness below can only fire while the harness writes memories. When the
    operator has switched auto-memory off, the files on disk are inert and a
    "clean" verdict says nothing about drift, so the state is reported beside it
    (maintenance visit A, 2026-10-10).
    """
    settings = home / ".claude" / "settings.json"
    try:
        value = json.loads(settings.read_text(encoding="utf-8")).get("autoMemoryEnabled")
    except (OSError, ValueError):
        return None
    return value if isinstance(value, bool) else None


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
    enabled = auto_memory_enabled(Path.home())
    if enabled is False:
        print(
            "auto-memory is OFF in ~/.claude/settings.json: the memories on disk are inert "
            "and this witness cannot observe new drift while it stays off"
        )
    elif enabled is None:
        print("auto-memory setting not declared in ~/.claude/settings.json (harness default)")
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
