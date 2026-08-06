"""One ranking rule for choosing which handoff to present (GHI #758).

Three independent readers select over `.gzkit/handoffs/`, and each learned the
same lesson separately:

* `gzkit.handoff_resume_gate.newest_handoff` — what the resume gate arms on.
* `scripts.session_orientation.collect_handoff` — what renders as "Most-recent
  handoff" at session start.
* `gzkit.lock_manager.find_handoff_for_release` — what may discharge a token
  surrender.

The first two answer *"which document describes the current state?"* and rank an
AUTHORED handoff above a mechanical floor bookmark. The third answers a different
question — *"may this document discharge a surrender?"* — and refuses every
`CHECKPOINT` outright, whoever wrote it (token-block § Sub-Invariant 5). It is
deliberately NOT a caller here: sharing a rule across two questions that merely
look alike is how the wrong filter gets applied to the wrong arm.

What the two selection readers share is this module: the writer identity and the
predicate over it. They do NOT share one function, because their iteration shapes
genuinely differ — one early-exits over an already-sorted list (a PreToolUse hot
path that should not read 200 files to answer), the other holds `(ts, path, text)`
tuples and takes a `max()`. Forcing one signature would have made one of them
worse. `tests/governance/test_handoff_selection.py` closes the gap the shared
constant cannot: a DIFFERENTIAL test asserting both readers pick the same
document from the same corpus, which is the property that actually matters.

Why the identity and not `mode`: a floor bookmark and an operator-authored
mid-flight checkpoint are BOTH `mode: CHECKPOINT`, so a mode test on the
selection arms discards the authored document — the opposite of the intent. Mode
is the right question on the release arm; authorship is the right question here.
"""

from __future__ import annotations

from typing import Any

__all__ = ["FLOOR_BOOKMARK_AGENT", "is_floor_bookmark", "selection_rank"]

#: Writer identity stamped on every mechanically-written exit-beat bookmark.
#:
#: Defined HERE rather than beside the writer so that the writer and every reader
#: name the same string by import. A second copy is the drift this module exists
#: to prevent, and `test_the_identity_has_exactly_one_definition` fails closed on
#: one appearing anywhere under `src/` or `scripts/`.
FLOOR_BOOKMARK_AGENT = "gzkit-session-exit"


def is_floor_bookmark(agent: str | None) -> bool:
    """Return True when ``agent`` is the exit beat, i.e. nobody authored this document.

    The whole selection rule reduces to this predicate plus "authored wins".
    """
    return agent == FLOOR_BOOKMARK_AGENT


def selection_rank(agent: str | None, timestamp: Any) -> tuple[bool, Any]:
    """Sort key ranking an authored handoff above a floor bookmark.

    Ascending, so `max()` picks the winner: authored sorts above floor, and
    recency orders WITHIN each class rather than across them. A floor bookmark is
    written at every session end and is therefore always the newest document on
    disk, so a plain recency sort hands back the precaution instead of the
    artifact it backs up.

    Deprioritize, never drop: a session that crashed or `/clear`ed before
    authoring leaves nothing else, and covering that case is the whole reason the
    exit beat exists (GHI #756). A floor bookmark still wins when it is alone,
    because every candidate then carries the same first element.
    """
    return (not is_floor_bookmark(agent), timestamp)
