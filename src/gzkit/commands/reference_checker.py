"""Adapter: resolve a cited GHI's live state through ``gh``.

One adapter behind the ``ReferenceChecker`` port (``gzkit.handoff_api``), shared
by every command that renders a GHI citation against live state — handoff
authoring and resume (GHI #696), and the OBPI status view's tracked-defect
annotation (GHI #966). A second GitHub resolver would be a second place for the
"unknown is not live" contract to drift, so there is exactly one.
"""

from __future__ import annotations

import json
from pathlib import Path

from gzkit.handoff_api import ReferenceChecker, ReferenceKind, ReferenceState, StepReference
from gzkit.utils import run_exec

__all__ = ["gh_issue_state", "live_reference_checker"]


def gh_issue_state(number: str, project_root: Path) -> ReferenceState:
    """Resolve one GHI number to a live/settled verdict via the ``gh`` read verb.

    Any failure — ``gh`` absent, unauthenticated, offline, malformed payload —
    resolves to ``UNKNOWN`` rather than to ``LIVE``. Degrading to "verified"
    when the check could not run would reintroduce exactly the unverified
    advisory this adapter exists to catch.
    """
    rc, out, _ = run_exec(
        ["gh", "issue", "view", number, "--json", "state"], project_root, timeout=10
    )
    if rc != 0:
        return ReferenceState.UNKNOWN
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return ReferenceState.UNKNOWN
    state = str(payload.get("state", "")).upper() if isinstance(payload, dict) else ""
    if state == "CLOSED":
        return ReferenceState.SETTLED
    if state == "OPEN":
        return ReferenceState.LIVE
    return ReferenceState.UNKNOWN


def live_reference_checker(project_root: Path) -> ReferenceChecker:
    """Adapter: resolve cited references against live state (GHI #696).

    GHI state is read through ``gh``, which is its only Layer-2 surface. OBPI and
    ADR references resolve to ``UNKNOWN``: their only repo-local index
    (``adr-status.md``) is a **Layer-3 derived view**, and
    ``docs/governance/state-doctrine.md`` forbids reading one as truth — an
    honest UNKNOWN beats a confident answer sourced from a non-authority.

    Results are memoized per reference, and a missing/failing ``gh`` latches the
    adapter off so an offline run costs one failed call, not one per citation.
    Build one checker per command invocation so the memo spans every citation
    that invocation renders.
    """
    cache: dict[str, ReferenceState] = {}
    reachable = True

    def check(reference: StepReference) -> ReferenceState:
        nonlocal reachable
        if reference.kind is not ReferenceKind.GHI or not reachable:
            return ReferenceState.UNKNOWN
        if reference.identifier not in cache:
            state = gh_issue_state(reference.identifier, project_root)
            if state is ReferenceState.UNKNOWN:
                reachable = False
            cache[reference.identifier] = state
        return cache[reference.identifier]

    return check
