"""Adapters: resolve a cited reference's live state against its own Layer-2 surface.

One adapter per kind behind the ``ReferenceChecker`` port (``gzkit.handoff_api``),
shared by every command that renders a citation against live state — handoff
authoring and resume (GHI #696), and the OBPI status view's tracked-defect
annotation (GHI #966). A second resolver for either kind would be a second place
for the "unknown is not live" contract to drift, so there is exactly one each.

The GHI resolver has two transports, one issue at a time (:func:`gh_issue_read`,
REST) and many in one call (:func:`gh_issue_reads`, GraphQL; GHI #1334), and one
verdict: both return an :class:`IssueAnswer`, and :func:`_state_of` alone maps an
answer to a :class:`ReferenceState`.
"""

import json
import re
from datetime import datetime
from enum import StrEnum
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.artifact_prefix import active_prefix_matches
from gzkit.handoff_api import ReferenceKind, ReferenceState, StepReference
from gzkit.utils import run_exec

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = [
    "ISSUES_PER_QUERY",
    "GhUnansweredError",
    "IssueAnswer",
    "IssueRead",
    "LiveReferenceChecker",
    "adr_ledger_state",
    "gh_issue_read",
    "gh_issue_reads",
    "gh_issue_state",
    "live_reference_checker",
    "obpi_ledger_state",
]

#: OBPI completion values that mean the work is recorded done in the ledger.
_SETTLED_COMPLETIONS = frozenset({"completed", "attested_completed"})

#: ADR lifecycle values that mean the ADR's closeout is RECORDED (GHI #1078).
_CLOSED_OUT_LIFECYCLES = frozenset({"Validated", "Completed", "Abandoned"})


class IssueAnswer(StrEnum):
    """What the GitHub API answered about one issue number (RP-12 ruling 182)."""

    OPEN = "open"
    CLOSED = "closed"
    #: The API says no such issue: 404 or 410, or the number is a pull request's.
    MISSING = "missing"
    #: No answer about the issue: `gh` absent or offline, or a status that says nothing of it.
    UNANSWERED = "unanswered"


class IssueRead(BaseModel):
    """One read of an issue: the API's answer, and when a found issue was created."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    answer: IssueAnswer = Field(..., description="What the API answered")
    created_at: datetime | None = Field(None, description="A found issue's creation time")


class GhUnansweredError(OSError):
    """The GitHub API gave no answer about an issue, so whether it exists is unknown."""


_STATUS_LINE = re.compile(r"^HTTP/\S+ (\d{3})")
#: Get an issue: 404 "Resource not found", 410 "Gone" (a deleted issue).
_NOT_AN_ISSUE = frozenset({404, 410})


def gh_issue_read(number: str, project_root: Path) -> IssueRead:
    """Read one issue through `gh api --include`, telling a missing issue from no answer.

    `gh` exits 1 for any failure, so its exit code cannot tell an issue that does
    not exist from an API it could not reach; the HTTP status line can (RP-12
    ruling 182). A pull request is returned by the issues endpoint and is not an
    issue, so it reads missing.

    Canonical: `gh help exit-codes`; https://cli.github.com/manual/gh_api (`--include`);
    https://docs.github.com/en/rest/issues/issues#get-an-issue (200, 301, 304, 404, 410;
    the `pull_request` key).

    Returns:
        The answer, with a found issue's creation time.

    """
    rc, out, _ = run_exec(
        ["gh", "api", "--include", f"repos/{{owner}}/{{repo}}/issues/{number}"],
        project_root,
        timeout=10,
    )
    head, _, body = out.replace("\r\n", "\n").partition("\n\n")
    status = _STATUS_LINE.match(head)
    if status is not None and int(status.group(1)) in _NOT_AN_ISSUE:
        return IssueRead(answer=IssueAnswer.MISSING)
    if status is None or int(status.group(1)) != HTTPStatus.OK or rc != 0:
        return IssueRead(answer=IssueAnswer.UNANSWERED)
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return IssueRead(answer=IssueAnswer.UNANSWERED)
    return _issue_from(payload)


def _issue_from(payload: object) -> IssueRead:
    """Read an issue's answer from a 200 body.

    Returns:
        Open or closed with its creation time, missing for a pull request, or
        unanswered for a body that is not an issue.

    """
    if not isinstance(payload, dict):
        return IssueRead(answer=IssueAnswer.UNANSWERED)
    if "pull_request" in payload:
        return IssueRead(answer=IssueAnswer.MISSING)
    state = str(payload.get("state", "")).lower()
    if state not in {IssueAnswer.OPEN, IssueAnswer.CLOSED}:
        return IssueRead(answer=IssueAnswer.UNANSWERED)
    created = payload.get("created_at")
    try:
        stamp = datetime.fromisoformat(created) if isinstance(created, str) else None
    except ValueError:
        stamp = None
    return IssueRead(answer=IssueAnswer(state), created_at=stamp)


def gh_issue_state(number: str, project_root: Path) -> ReferenceState:
    """Resolve one GHI number to a live/settled verdict through `gh_issue_read`.

    Any failure — ``gh`` absent, unauthenticated, offline, malformed payload, an
    issue that does not exist — resolves to ``UNKNOWN`` rather than to ``LIVE``.
    Degrading to "verified" when the check could not run would reintroduce
    exactly the unverified advisory this adapter exists to catch.

    Returns:
        ``SETTLED`` for a closed issue, ``LIVE`` for an open one, ``UNKNOWN`` otherwise.

    """
    return _state_of(gh_issue_read(number, project_root).answer)


def _state_of(answer: IssueAnswer) -> ReferenceState:
    """Map one API answer to its verdict; the one mapping both transports share.

    Returns:
        ``SETTLED`` for a closed issue, ``LIVE`` for an open one, ``UNKNOWN`` otherwise.

    """
    if answer is IssueAnswer.CLOSED:
        return ReferenceState.SETTLED
    if answer is IssueAnswer.OPEN:
        return ReferenceState.LIVE
    return ReferenceState.UNKNOWN


#: Issue numbers asked of GitHub in one GraphQL query (GHI #1334). GitHub bounds a
#: query by node count and complexity, not by alias; 50 one-node aliases stay far
#: inside both, and one query answered in ~0.7 s on 2026-11-20.
ISSUES_PER_QUERY = 50

#: A number put into the query text. ASCII digits only: ``str.isdigit`` admits
#: other scripts' digits, and anything else would be query text a citation wrote.
_ISSUE_NUMBER = re.compile(r"[0-9]+")

_UNANSWERED = IssueRead(answer=IssueAnswer.UNANSWERED)
_MISSING = IssueRead(answer=IssueAnswer.MISSING)


def gh_issue_reads(numbers: Iterable[str], project_root: Path) -> dict[str, IssueRead]:
    """Read many issues through `gh api graphql`, one call per batch (GHI #1334).

    One ``issueOrPullRequest`` alias per number, :data:`ISSUES_PER_QUERY` to a
    query, so an ADR whose briefs track 31 GHIs costs one round trip, not 31. The
    answers keep RP-12 ruling 182's distinction, read from what GraphQL returns in
    place of a status line: an ``Issue`` node is open or closed; a ``PullRequest``
    node is no issue, so MISSING; a null node is MISSING only when a ``NOT_FOUND``
    error names its own alias, and UNANSWERED otherwise. `gh` exits 1 whenever the
    answer carries errors, a not-found number included, so the exit code says
    nothing here and is not read. A number that is not ASCII digits is never put
    into the query and reads UNANSWERED.

    Canonical: https://cli.github.com/manual/gh_api (graphql, the ``{owner}`` and
    ``{repo}`` placeholders in fields); https://docs.github.com/en/graphql/reference/objects#repository
    (``issueOrPullRequest``); the shapes observed against this repository 2026-11-20.

    Returns:
        One read per distinct number asked.

    """
    wanted = list(dict.fromkeys(numbers))
    reads = {number: _UNANSWERED for number in wanted if not _ISSUE_NUMBER.fullmatch(number)}
    queried = [number for number in wanted if number not in reads]
    for start in range(0, len(queried), ISSUES_PER_QUERY):
        reads.update(_read_batch(queried[start : start + ISSUES_PER_QUERY], project_root))
    return reads


def _read_batch(numbers: list[str], project_root: Path) -> dict[str, IssueRead]:
    """Ask one GraphQL query for *numbers*; every number UNANSWERED when no answer came.

    Returns:
        One read per number.

    """
    aliases = " ".join(
        f"i{number}:issueOrPullRequest(number:{number})"
        "{__typename ... on Issue{state createdAt}}"
        for number in numbers
    )
    query = (
        f"query($owner:String!,$name:String!){{repository(owner:$owner,name:$name){{{aliases}}}}}"
    )
    _, out, _ = run_exec(
        [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={query}",
            "-F",
            "owner={owner}",
            "-F",
            "name={repo}",
        ],
        project_root,
        timeout=10,
    )
    try:
        payload = json.loads(out)
    except json.JSONDecodeError:
        return dict.fromkeys(numbers, _UNANSWERED)
    match payload:
        case {"data": {"repository": dict() as repository}}:
            not_found = _not_found_aliases(payload.get("errors"))
        case _:
            return dict.fromkeys(numbers, _UNANSWERED)
    return {
        number: _node_read(repository.get(f"i{number}"), not_found=f"i{number}" in not_found)
        for number in numbers
    }


def _not_found_aliases(errors: object) -> set[str]:
    """Return every alias a ``NOT_FOUND`` error names directly under ``repository``.

    Returns:
        The aliases GitHub says resolve to no issue or pull request.

    """
    if not isinstance(errors, list):
        return set()
    aliases: set[str] = set()
    for error in errors:
        match error:
            case {"type": "NOT_FOUND", "path": ["repository", str() as alias]}:
                aliases.add(alias)
    return aliases


def _node_read(node: object, *, not_found: bool) -> IssueRead:
    """Read one alias's node; an Issue goes through :func:`_issue_from`, as REST does.

    Returns:
        The node's answer.

    """
    match node:
        case None:
            return _MISSING if not_found else _UNANSWERED
        case {"__typename": "PullRequest"}:
            return _MISSING
        case {"__typename": "Issue"}:
            return _issue_from(
                {"state": node.get("state", ""), "created_at": node.get("createdAt")}
            )
        case _:
            return _UNANSWERED


def _unique_prefix_entry(
    graph: dict[str, dict[str, Any]], identifier: str
) -> dict[str, Any] | None:
    """Return the one graph entry whose id extends *identifier*, else ``None`` (GHI #1079).

    The separator is load-bearing: the match is against ``<identifier>-``, never
    raw text, so ``OBPI-0.1.0-1`` does not name ``OBPI-0.1.0-10-…``. A truncated
    citation resolving to a numerically adjacent OBPI would be a wrong verdict
    wearing a right one's confidence, and the extractor does produce truncations.

    TWO OR MORE ACTIVE MATCHES RESOLVE TO NOTHING. GHI #826 ruled that an id is
    matched "on the id the caller SUPPLIED, never on a prefix derived from it",
    because one prefix can name two OBPIs under two different parent ADRs.
    Refusing that is the ruling, not a shortfall.

    A parked or withdrawn sibling is not that case (GHI #1162). Demoting a feature
    ADR parks its OBPIs and releases the semver, so ``OBPI-0.35.0-08`` extends to
    both a parked ``-forbid-pytest`` and the live ``-remember-post-append-advisory``.
    Candidates come from :func:`gzkit.artifact_prefix.active_prefix_matches`, the
    rule ``gz obpi status`` also resolves through, so the two cannot disagree.

    Returns:
        The single active graph entry extending ``identifier``, or None when zero or several match.

    """
    matches = active_prefix_matches(graph, identifier)
    if len(matches) == 1:
        return graph[matches[0]]
    return None


def _artifact_info(identifier: str, project_root: Path) -> dict[str, Any] | None:
    """Read one artifact's entry in the ledger's graph, or ``None`` when Layer 2 is silent.

    Shared by every ledger-backed arm so the "unknown is not live" contract has
    one implementation. Any failure — no ledger, unreadable rows, an id the
    ledger never recorded — returns ``None``, which each caller renders
    ``UNKNOWN``: a surface that could not be read has verified nothing.

    **The citation is the id the PROSE wrote, not the graph key (GHI #1079).**
    ``_extract_references`` takes the matched text verbatim, and real handoffs
    write ``ADR-0.35.0`` and ``OBPI-0.35.0-08``, never the full slug — measured
    over this repository's handoff corpus, 1264 of 1854 ADR citations and 397 of
    867 OBPI citations are unique prefixes, and **no** OBPI citation was an exact
    graph key. An exact-key lookup therefore answered almost nothing.

    Resolution is ``Ledger.resolve_artifact_id`` first, which folds renames and
    already resolves a unique ADR prefix (GHI #222), then
    :func:`_unique_prefix_entry` for the kinds that method passes through. The
    fold is reused rather than reimplemented so two resolvers cannot disagree
    about what an id means.

    Returns:
        The artifact's graph entry, or None when the ledger is absent, unreadable, or has no
        matching id (including a prefix that matches zero or several active entries).

    """
    from gzkit.ledger import Ledger  # noqa: PLC0415 — import cost stays off the CLI's cold path

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.is_file():
        return None
    try:
        ledger = Ledger(ledger_path)
        graph = ledger.get_artifact_graph()
        resolved = ledger.resolve_artifact_id(identifier)
    except OSError, ValueError:
        return None
    info = graph.get(resolved)
    if info is None:
        info = _unique_prefix_entry(graph, resolved)
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

    Returns:
        ``SETTLED`` when withdrawn or completed, ``LIVE`` when repudiated or not completed,
        ``UNKNOWN`` when the ledger is absent or unreadable or has no entry.

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

    Returns:
        ``SETTLED`` when the derived lifecycle is closed out, ``LIVE`` otherwise, ``UNKNOWN`` when
        the ledger is absent or unreadable or has no entry.

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


def live_reference_checker(project_root: Path) -> LiveReferenceChecker:
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

    Results are memoized per reference, and a ``gh`` that gives no answer, absent,
    unauthenticated or offline, latches the GHI arm off so an offline run costs one
    failed call, not one per citation. An issue that does not exist is an answer, so
    it does not latch the arm (GHI #1335, RP-12 ruling 182).
    The ledger arms carry no such latch: they read a local file, so a failure is
    per-reference rather than a broken transport. Build one checker per command
    invocation so the memo spans every citation that invocation renders.

    The checker is also a :class:`~gzkit.handoff_api.ReferencePrefetcher`
    (GHI #1334): ``prefetch`` answers every uncached local GHI citation through
    one :func:`gh_issue_reads` batch, so a caller that knows its citations pays
    one round trip for them, not one each (`gz adr status ADR-0.35.0` asked 31
    serially, ~21 s). Both transports map their answer through :func:`_state_of`,
    so a citation's verdict does not depend on which one produced it.

    Returns:
        A memoizing checker that maps a :class:`StepReference` to its :class:`ReferenceState`.

    """
    return LiveReferenceChecker(project_root)


class LiveReferenceChecker:
    """The memoizing checker :func:`live_reference_checker` builds; see its docstring."""

    def __init__(self, project_root: Path) -> None:
        """Build an empty memo for one command invocation over *project_root*."""
        self._project_root = project_root
        self._cache: dict[tuple[ReferenceKind, str], ReferenceState] = {}
        self._reachable = True

    def __call__(self, reference: StepReference, /) -> ReferenceState:
        """Resolve one reference, from the memo when it was already answered.

        Returns:
            The reference's state; ``UNKNOWN`` for a foreign or unreachable one.

        """
        if reference.repo is not None:
            return ReferenceState.UNKNOWN
        key = (reference.kind, reference.identifier)
        if key in self._cache:
            return self._cache[key]
        ledger_arm = _LEDGER_ARMS.get(reference.kind)
        if ledger_arm is not None:
            state = ledger_arm(reference.identifier, self._project_root)
        elif reference.kind is not ReferenceKind.GHI or not self._reachable:
            return ReferenceState.UNKNOWN
        else:
            answer = gh_issue_read(reference.identifier, self._project_root).answer
            state = _state_of(answer)
            # GHI #1335: only no answer latches the arm off; MISSING is an answer (ruling 182).
            self._reachable = answer is not IssueAnswer.UNANSWERED
        self._cache[key] = state
        return state

    def prefetch(self, references: Iterable[StepReference], /) -> None:
        """Answer every uncached local numeric GHI citation in *references* in one batch.

        A batch in which no number was answered is an unreachable ``gh``, and
        latches the arm off as a failed single read does. A number answered
        MISSING is an answer, so it does not. A number a batch that did answer
        left unanswered is not memoized, so a later check asks it singly.
        """
        if not self._reachable:
            return
        pending = [
            reference.identifier
            for reference in references
            if reference.kind is ReferenceKind.GHI
            and reference.repo is None
            and _ISSUE_NUMBER.fullmatch(reference.identifier)
            and (ReferenceKind.GHI, reference.identifier) not in self._cache
        ]
        if not pending:
            return
        reads = gh_issue_reads(pending, self._project_root)
        answered = {n: r for n, r in reads.items() if r.answer is not IssueAnswer.UNANSWERED}
        self._reachable = bool(answered)
        for number, read in answered.items():
            self._cache[ReferenceKind.GHI, number] = _state_of(read.answer)
