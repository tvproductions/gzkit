"""Adapters: resolve a cited reference's live state against its own Layer-2 surface.

One adapter per kind behind the ``ReferenceChecker`` port (``gzkit.handoff_api``),
shared by every command that renders a citation against live state — handoff
authoring and resume (GHI #696), and the OBPI status view's tracked-defect
annotation (GHI #966). A second resolver for either kind would be a second place
for the "unknown is not live" contract to drift, so there is exactly one each.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gzkit.handoff_api import ReferenceChecker, ReferenceKind, ReferenceState, StepReference
from gzkit.utils import run_exec

__all__ = [
    "adr_ledger_state",
    "gh_issue_state",
    "live_reference_checker",
    "obpi_ledger_state",
]

#: OBPI completion values that mean the work is recorded done in the ledger.
_SETTLED_COMPLETIONS = frozenset({"completed", "attested_completed"})

#: ADR lifecycle values that mean the ADR's closeout is RECORDED (GHI #1078).
_CLOSED_OUT_LIFECYCLES = frozenset({"Validated", "Completed", "Abandoned"})


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


def _artifact_info(identifier: str, project_root: Path) -> dict[str, Any] | None:
    """Read one artifact's entry in the ledger's graph, or ``None`` when Layer 2 is silent.

    Shared by every ledger-backed arm so the "unknown is not live" contract has
    one implementation. Any failure — no ledger, unreadable rows, an id the
    ledger never recorded — returns ``None``, which each caller renders
    ``UNKNOWN``: a surface that could not be read has verified nothing.
    """
    from gzkit.ledger import Ledger  # noqa: PLC0415 — import cost stays off the CLI's cold path

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.is_file():
        return None
    try:
        info = Ledger(ledger_path).get_artifact_graph().get(identifier)
    except (OSError, ValueError):
        return None
    return info if isinstance(info, dict) else None


def obpi_ledger_state(identifier: str, project_root: Path) -> ReferenceState:
    """Resolve one OBPI id to a live/settled verdict from the LEDGER (GHI #1076).

    The ledger is Layer 2 and records OBPI completion directly, so this asks the
    authority rather than a derived view: ``AGENTS.md`` § Execution Rules —
    "Completion evidence is the ledger. A brief's ``status: Completed`` and
    ``gz status`` output are derived views." ``gz obpi status`` already derives
    its runtime state from this same artifact graph.

    Three verdicts, and the ORDER of the first two is the contract. ``withdrawn``
    is checked first because ADR-0.0.71 retires such an OBPI permanently and it
    is not re-completable, so the citation is settled whatever completion record
    it also carries. ``repudiated`` is checked before completion for the mirror
    reason: it REVERSES a completion while the work intent stands, so the
    citation is live again even though a completion receipt exists.

    Any failure — no ledger, unreadable rows, an id the ledger never recorded —
    resolves to ``UNKNOWN`` rather than to ``LIVE``, on ``gh_issue_state``'s
    discipline: a surface that could not be read has verified nothing.
    """
    info = _artifact_info(identifier, project_root)
    if info is None:
        return ReferenceState.UNKNOWN
    if info.get("withdrawn"):
        return ReferenceState.SETTLED
    if info.get("repudiated"):
        return ReferenceState.LIVE
    if info.get("obpi_completion") in _SETTLED_COMPLETIONS:
        return ReferenceState.SETTLED
    return ReferenceState.LIVE


def adr_ledger_state(identifier: str, project_root: Path) -> ReferenceState:
    """Resolve one ADR id to a live/settled verdict from the LEDGER (GHI #1078).

    ``SETTLED`` asserts that the ADR's CLOSEOUT IS RECORDED — operator ruling
    2026-09-21, option (A) of the three GHI #1076's blocker comment set out.
    The reading it rejects, "every child OBPI attested", agrees on 84 of this
    repository's 85 candidate ADRs and diverges on exactly the case the ruling
    is about: an ADR can be fully implemented while its gate covenant still has
    work, and settling that would silence a step still worth advising.

    ``Ledger.derive_adr_semantics`` is the authority, so this verdict moves with
    the one definition ``gz adr status`` renders rather than a second copy of
    it. Read the LIFECYCLE, never the closeout PHASE: a bare
    ``closeout_initiated`` event leaves the lifecycle ``Pending`` on purpose,
    because a ceremony that began is not one that finished.

    ``Abandoned`` settles alongside ``Validated`` and ``Completed``. That is the
    GHI sense of settled — stop advising this — and not a claim the work
    shipped.
    """
    from gzkit.ledger import Ledger  # noqa: PLC0415 — import cost stays off the CLI's cold path

    info = _artifact_info(identifier, project_root)
    if info is None:
        return ReferenceState.UNKNOWN
    lifecycle = Ledger.derive_adr_semantics(info).get("lifecycle_status")
    if lifecycle in _CLOSED_OUT_LIFECYCLES:
        return ReferenceState.SETTLED
    return ReferenceState.LIVE


#: Citation kinds whose Layer-2 authority is this repository's own ledger.
_LEDGER_ARMS = {
    ReferenceKind.OBPI: obpi_ledger_state,
    ReferenceKind.ADR: adr_ledger_state,
}


def live_reference_checker(project_root: Path) -> ReferenceChecker:
    """Adapter: resolve cited references against live state (GHI #696, GHI #1076).

    Each kind is asked of its own Layer-2 authority. GHI state is read through
    ``gh``. OBPI and ADR state are read from the LEDGER, via the arms registered
    in :data:`_LEDGER_ARMS`.

    Neither ledger arm reads ``adr-status.md``, the **Layer-3 derived view**
    ``docs/governance/state-doctrine.md`` forbids reading as truth. The
    rationale this docstring carried until GHI #1076 treated that index as the
    only repo-local surface for both kinds, which was never true: the ledger
    records OBPI completion directly and carries every event
    ``Ledger.derive_adr_semantics`` needs for an ADR's lifecycle.

    What remained after GHI #1076 was not where to read but WHAT ``SETTLED``
    asserts for an ADR, which was the operator's to decide. Ruled 2026-09-21
    (GHI #1078): the ADR's closeout is recorded. See :func:`adr_ledger_state`.

    A citation that names ANOTHER repository resolves ``UNKNOWN`` for every
    kind, without a call: this adapter is built for one ``project_root``, and
    both authorities it reads are local to that root — ``gh issue view`` reads
    whatever repository it is run in, and the ledger is this repository's own.
    Resolving ``gz-skills#1`` here would answer with the LOCAL issue 1. That is
    not a missed check but a wrong one, and it reads exactly like a right one.

    Results are memoized per reference, and a missing/failing ``gh`` latches the
    GHI arm off so an offline run costs one failed call, not one per citation.
    The ledger arms carry no such latch: they read a local file, so a failure is
    per-reference rather than a broken transport. Build one checker per command
    invocation so the memo spans every citation that invocation renders.
    """
    cache: dict[tuple[ReferenceKind, str], ReferenceState] = {}
    reachable = True

    def check(reference: StepReference) -> ReferenceState:
        nonlocal reachable
        if reference.repo is not None:
            return ReferenceState.UNKNOWN
        key = (reference.kind, reference.identifier)
        ledger_arm = _LEDGER_ARMS.get(reference.kind)
        if ledger_arm is not None:
            if key not in cache:
                cache[key] = ledger_arm(reference.identifier, project_root)
            return cache[key]
        if reference.kind is not ReferenceKind.GHI or not reachable:
            return ReferenceState.UNKNOWN
        if key not in cache:
            state = gh_issue_state(reference.identifier, project_root)
            if state is ReferenceState.UNKNOWN:
                reachable = False
            cache[key] = state
        return cache[key]

    return check
