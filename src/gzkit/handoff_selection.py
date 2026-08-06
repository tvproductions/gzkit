"""One ranking rule for choosing which handoff to present (GHI #758).

Three independent readers select over `.gzkit/handoffs/`, and each learned the
same lesson separately:

* `gzkit.handoff_resume_gate.newest_handoff` — what the resume gate arms on.
* `scripts.session_orientation.collect_handoff` — what renders as "Most-recent
  handoff" at session start.
* `gzkit.exchange_records.find_exchange_for_release` — what may discharge a token
  surrender.

The first two answer *"which document describes the current state?"* and rank an
AUTHORED handoff above a mechanical floor bookmark. The third answers a different
question — *"may this document discharge a surrender?"* — and since GHI #763 it
does not even read this corpus: exchange records live in `.gzkit/locks/exchange/`
and its predicate is default-DENY (token-block § Sub-Invariant 5). It is
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

This module also owns the corpus's OTHER cross-reader rule: given a handoff, what
counts as having happened SINCE it (`HANDOFF_PATHSPEC_EXCLUDE`,
`commits_since_range`). That rule drifted exactly the way selection did — the exit
beat's skip predicate and the orientation account each built their own range and
spelled the exclusion pathspec themselves, and each learned the GHI #760 lesson
in a separate commit with a separate test. The two rules live together because
they are the same kind of thing about the same corpus, with the same drift risk
and the same structural fence.
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "FLOOR_BOOKMARK_AGENT",
    "HANDOFF_PATHSPEC_EXCLUDE",
    "commits_since_range",
    "is_floor_bookmark",
    "selection_rank",
]

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


#: Git pathspec excluding the handoff corpus from a since-the-handoff query.
#:
#: Load-bearing on every such query, for two distinct reasons that both reduce to
#: "the corpus is not the work": a staged exit bookmark would otherwise read as a
#: dirty tree, and a later handoff would otherwise read as work the earlier one
#: failed to describe. Defined HERE rather than in each caller —
#: `test_the_exclusion_pathspec_appears_only_in_its_defining_module` fails closed
#: on a second copy anywhere under `src/` or `scripts/`.
HANDOFF_PATHSPEC_EXCLUDE = ":(exclude).gzkit/handoffs"


def commits_since_range(landing_sha: str | None) -> str:
    """Return the `git log` revision range for commits postdating a handoff.

    Anchored on the landing commit's IDENTITY, never its timestamp. `gz git-sync`
    bundles `.gzkit/**` into one `chore: update .gzkit` commit, so the commit that
    lands a handoff routinely carries adjacent files; a `--since=<landing time>`
    window therefore reports the handoff's own arrival as work it failed to
    describe, on every handoff, forever. `<sha>..HEAD` cannot make that mistake —
    a range excludes its own endpoint, and no path filter can (GHI #760).

    An absent sha means the handoff is staged but not yet committed, which needs
    no anchor: every commit in history predates it, so nothing can postdate it.
    `HEAD..HEAD` is that fact as a range, and it is empty by construction rather
    than by luck. Treating the absence as an uncertainty instead is what made a
    staged handoff unable to cover a session at all.
    """
    return f"{(landing_sha or '').strip() or 'HEAD'}..HEAD"
