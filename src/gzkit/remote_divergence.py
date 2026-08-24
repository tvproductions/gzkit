"""One behind-origin probe and one caveat for every handoff renderer (GHI #872).

:mod:`gzkit.handoff_selection` fences the handoff readers into selecting the
SAME document. It does not fence what they SAY about it, and that is where they
drifted. Observed 2026-08-23 on a clone 8 commits behind ``origin/main``:
``scripts.session_orientation`` rendered the behind-origin caveat, while
``gzkit.session_start`` rendered ``Freshness: Fresh`` and no qualifier at all.

The delivery asymmetry is what made it bite. The defended rendering goes to
stdout — 19.3 KB that session, truncated to a 2 KB preview which clipped the
caveat at line 19. The undefended one is injected whole as ``additionalContext``
and reads as instruction. The surface that reliably reaches the agent carried no
defense, so a session re-derived an OBPI draw order from a tree that was missing
the handoff cementing it.

``Freshness`` is not this qualifier and cannot stand in for it: it measures the
AGE OF THE SELECTED DOCUMENT (``resume_handoff``), never whether the corpus it
was selected from is current. ``Fresh`` was correct on 2026-08-23 and still
misled.

Probe and caveat live here, once, for the reason ``FLOOR_BOOKMARK_AGENT`` and
``HANDOFF_PATHSPEC_EXCLUDE`` live in one module: a second copy is the drift.
``tests/governance/test_handoff_selection.py`` fences both arms — a differential
asserting every renderer emits this qualifier for the same state, and a literal
scan failing closed on a restatement anywhere under ``src/`` or ``scripts/``.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "FETCH_TIMEOUT_SEC",
    "NO_FETCH_ENV",
    "QUERY_TIMEOUT_SEC",
    "RemoteDivergence",
    "behind_origin_caveat",
    "probe_remote_divergence",
]

#: The operator's offline escape hatch, named for orientation because that is
#: where it was introduced (GHI #338) and operators already set it. One variable
#: governs every boot-path fetch; a second name would mean an operator who
#: silenced one hook still pays the other's timeout.
NO_FETCH_ENV = "GZKIT_ORIENTATION_NO_FETCH"

FETCH_TIMEOUT_SEC = 8
QUERY_TIMEOUT_SEC = 4


class RemoteDivergence(BaseModel):
    """How far the working clone has drifted from ``origin/main``."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    branch: str = Field(..., description="Current branch, or '?' when unresolvable")
    ahead: int = Field(..., description="Commits in HEAD not in origin/main")
    behind: int = Field(..., description="Commits in origin/main not in HEAD")

    @property
    def is_behind(self) -> bool:
        """True when unmerged commits exist upstream."""
        return self.behind > 0


def behind_origin_caveat(behind: int) -> str:
    """Render the qualifier every handoff renderer carries on a behind clone.

    States what ``Freshness`` structurally cannot: a fetch updates refs, never
    the working tree, and every handoff reader selects over the TREE. So the
    newest handoff on disk is not the newest handoff that exists, and the
    document named above this line may be several generations stale.

    Carries the measured distance rather than a generic warning — an operator
    deciding whether to stop and pull needs the magnitude, and "behind" alone
    reads the same at 1 commit as at 20.
    """
    return (
        f"CAVEAT: this clone is {behind} commits behind origin, and this "
        "selection reads the WORKING TREE — newer handoffs may exist in the "
        "unmerged commits. Run `git pull --ff-only origin main` and re-read "
        "before treating this as the most-recent handoff."
    )


def probe_remote_divergence(cwd: Path | None = None) -> RemoteDivergence | None:
    """Measure divergence from ``origin/main``. Never raises; None when unknowable.

    Returns None when git is absent, the repo has no resolvable ``origin/main``,
    or any subprocess fails. Both callers are session-boot hooks that must
    degrade to silence rather than take orientation down with them (GHI #338).

    Fetches unless :data:`NO_FETCH_ENV` is set. Reading stale refs instead would
    report ``behind=0`` on precisely the clone this caveat exists to warn about
    — a fix that renders green in the failing case is the defect wearing a fix's
    clothes.
    """
    if os.environ.get(NO_FETCH_ENV) != "1":
        fetched = _git(["fetch", "--quiet", "origin"], FETCH_TIMEOUT_SEC, cwd)
        if fetched is None and _git(["--version"], QUERY_TIMEOUT_SEC, cwd) is None:
            # git missing entirely is a hard "no remote state available". A
            # fetch that failed with git present (offline, no origin) still
            # leaves local refs queryable, so fall through and count.
            return None

    branch_proc = _git(["rev-parse", "--abbrev-ref", "HEAD"], QUERY_TIMEOUT_SEC, cwd)
    if branch_proc is None or branch_proc.returncode != 0:
        return None

    # `--left-right --count origin/main...HEAD` prints "<behind>\t<ahead>":
    # left = commits in origin/main not in HEAD; right = the converse.
    # `origin/main` is hard-coded because the warning class GHI #338 names is
    # specific to the canonical branch — editing canonical surfaces against a
    # stale main is the failure mode, not divergence on a feature branch.
    count_proc = _git(
        ["rev-list", "--left-right", "--count", "origin/main...HEAD"], QUERY_TIMEOUT_SEC, cwd
    )
    if count_proc is None or count_proc.returncode != 0:
        return None
    parts = count_proc.stdout.strip().split()
    if len(parts) != 2:
        return None
    try:
        behind, ahead = int(parts[0]), int(parts[1])
    except ValueError:
        return None

    return RemoteDivergence(branch=branch_proc.stdout.strip() or "?", ahead=ahead, behind=behind)


def _git(
    args: list[str], timeout: int, cwd: Path | None
) -> subprocess.CompletedProcess[str] | None:
    """Run one git subprocess; None on any failure shape (missing git, timeout).

    ``errors="replace"`` is load-bearing, not decoration: a branch name in
    cp1252/latin-1 would otherwise raise ``UnicodeDecodeError`` — a
    ``ValueError``, which the guard below does NOT catch — and kill session boot
    (the lesson GHI #688 already taught the file-read side).
    """
    try:
        return subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            cwd=cwd,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None
