"""gz handoff — operator-facing surface over the handoff authoring API.

Surfaces the fail-closed handoff authoring gate (``gzkit.handoff_api``, shipped
by OBPI-0.0.65-02) as a CLI verb group (ADR-0.0.65 § Decision #3). ``gz handoff
create`` routes authoring through :func:`validate_handoff_document` so a handoff
is mechanically validated rather than hand-written markdown; ``gz handoff list``
and ``gz handoff resume`` are read-only projections over the on-disk corpus.

Thin adapter contract: NO domain logic lives here. Each command builds a
structured payload from the API's Pydantic return objects and either serializes
it (``--json``) or renders it for humans. The ``airlock in|out`` verb group is
the structural exemplar.

@covers ADR-0.0.65 (OBPI-0.0.65-03)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.common import console, get_project_root
from gzkit.handoff_api import (
    DecisionAttribution,
    HandoffInfo,
    NextStep,
    ReferenceChecker,
    ReferenceKind,
    ReferenceState,
    ResumeResult,
    StepReference,
    create_handoff,
    list_handoffs,
    resume_handoff,
)
from gzkit.handoff_rulings import read_rulings
from gzkit.handoff_validation import (
    SETTLED_SECTION,
    HandoffValidationError,
    continues_from_refs,
)
from gzkit.utils import git_cmd, run_exec

# Required section -> the handoff_create_cmd parameter that fills it. Every
# REQUIRED_SECTIONS entry MUST appear here: a section with no parameter cannot be
# filled from the CLI, which is exactly how GHI #692 happened — the map had two
# entries for seven sections, so the default invocation emitted five empty
# headings. Bound to REQUIRED_SECTIONS by a coherence test.
SECTION_PARAMS: dict[str, str] = {
    "Current State Summary": "summary",
    "Important Context": "context",
    "Decisions Made": "decisions",
    "Immediate Next Steps": "next_steps",
    "Pending Work / Open Loops": "pending",
    "Verification Checklist": "verification",
    "Evidence / Artifacts": "evidence",
}


def _list_payload(infos: list[HandoffInfo]) -> list[dict]:
    """Machine-readable projection of a handoff listing (the ``--json`` shape)."""
    return [info.model_dump() for info in infos]


def handoff_list_cmd(
    *,
    adr: str | None = None,
    as_json: bool = False,
    base_path: Path = Path(),
) -> None:
    """List handoffs newest-first, optionally scoped by ADR (REQ-0.0.65-03-01).

    Read-only projection of :func:`list_handoffs`. ``--json`` emits the list of
    ``HandoffInfo`` dumps; the human form is a newest-first table.
    """
    infos = list_handoffs(adr_id=adr, base_path=base_path)
    if as_json:
        print(json.dumps(_list_payload(infos), indent=2))  # noqa: T201
        return
    if not infos:
        console.print("No handoffs found.")
        return
    for info in infos:
        console.print(f"{info.timestamp}  {info.adr_id}  {info.obpi_id or '-'}  {info.path}")


def _gh_issue_state(number: str, project_root: Path) -> ReferenceState:
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


def _live_reference_checker(project_root: Path) -> ReferenceChecker:
    """Adapter: resolve a step's cited references against live state (GHI #696).

    GHI state is read through ``gh``, which is its only Layer-2 surface. OBPI and
    ADR references resolve to ``UNKNOWN``: their only repo-local index
    (``adr-status.md``) is a **Layer-3 derived view**, and
    ``docs/governance/state-doctrine.md`` forbids reading one as truth — an
    honest UNKNOWN beats a confident answer sourced from a non-authority.

    Results are memoized per reference, and a missing/failing ``gh`` latches the
    adapter off so an offline resume costs one failed call, not one per citation.
    """
    cache: dict[str, ReferenceState] = {}
    reachable = True

    def check(reference: StepReference) -> ReferenceState:
        nonlocal reachable
        if reference.kind is not ReferenceKind.GHI or not reachable:
            return ReferenceState.UNKNOWN
        if reference.identifier not in cache:
            state = _gh_issue_state(reference.identifier, project_root)
            if state is ReferenceState.UNKNOWN:
                reachable = False
            cache[reference.identifier] = state
        return cache[reference.identifier]

    return check


def _render_step_references(step: NextStep) -> None:
    """Render one step's citations and their live state, indented under it."""
    if not step.references:
        return
    rendered = " · ".join(
        f"{ref.kind.value} {ref.identifier}: {ref.state.value}" for ref in step.references
    )
    console.print(f"       refs: {rendered}")


def _render_resume(result: ResumeResult) -> None:
    """Human-readable resume report — path, staleness, and EVERY next step.

    All authored steps are rendered, not just the head: surfacing one is what
    let items 2-N fall out of the advisory channel and be re-adjudicated as
    open loops in the successor session (GHI #696).

    Each step also carries the live state of what it cites. A step citing a
    settled reference is flagged, because relaying such a step unexamined is how a
    closed GHI got re-adjudicated three sessions running (GHI #696 defect 2). The
    flag reports the citation, not a verdict — whether the reference is a
    precondition (step is void) or provenance (step still stands) is the reader's
    call, and no available signal decides it.
    """
    console.print(f"resume — {result.path}")
    console.print(f"  staleness: {result.staleness.value}")
    console.print(f"  requires human verification: {result.requires_human_verification}")
    # No early return on an empty step list: decisions and settled rulings are
    # independent channels, and skipping them because no step parsed is how a
    # carried operator ruling would go unseen (GHI #696 defects 3 and 4).
    if not result.steps:
        console.print("  next steps: (none extracted)")
    else:
        console.print(f"  next steps ({len(result.steps)}):")
        for index, step in enumerate(result.steps, start=1):
            marker = "CITES SETTLED — " if step.cites_settled else ""
            console.print(f"    {index}. {marker}{step.text}")
            _render_step_references(step)
        flagged = sum(1 for step in result.steps if step.cites_settled)
        if flagged:
            console.print(
                f"  {flagged} step(s) cite a settled reference — confirm whether it is a "
                "precondition (step is void) or context (step still stands)."
            )
    _render_decisions(result)
    _render_settled(result)


def _render_decisions(result: ResumeResult) -> None:
    """Render decisions grouped by who made them (GHI #696 defect 4).

    Operator rulings print first and are labelled AUTHORITY: canon is verbatim —
    "MY WORD IS AUTHORITY IN ALL CASES" — so a ruling must not arrive looking like
    an agent's own preference, which is how both became equally re-arguable.
    Unattributed entries are shown as such rather than sorted into either bucket.
    """
    if not result.decisions:
        return
    console.print(f"  decisions ({len(result.decisions)}):")
    labels = {
        DecisionAttribution.OPERATOR_RULED: "AUTHORITY (operator-ruled)",
        DecisionAttribution.AGENT_CHOSE: "agent-chose",
        DecisionAttribution.UNATTRIBUTED: "unattributed",
    }
    for attribution in (
        DecisionAttribution.OPERATOR_RULED,
        DecisionAttribution.AGENT_CHOSE,
        DecisionAttribution.UNATTRIBUTED,
    ):
        matching = [d for d in result.decisions if d.attribution is attribution]
        if not matching:
            continue
        console.print(f"    {labels[attribution]}:")
        for decision in matching:
            console.print(f"      - {decision.text}")


#: How many settled rulings a resume renders inline before pointing at the store.
#: Resume is read at session start, where the corpus is the single largest thing
#: an agent reads and the least likely to be acted on — 457 entries rendered in
#: full is the same crowding-out inside the terminal that GHI #838 measured
#: inside the document. The tail is shown rather than the head: the newest
#: rulings are the ones a resuming session has not already met.
_SETTLED_PREVIEW = 10


def _render_settled(result: ResumeResult) -> None:
    """Render rulings carried forward as settled (GHI #696 defect 3).

    Previews the newest few and names the rest rather than eliding them silently
    — a count the reader can see is what separates a preview from a cap that
    quietly hides booked rulings.
    """
    if not result.settled:
        return
    total = len(result.settled)
    console.print(f"  settled — do NOT re-open ({total}):")
    for entry in result.settled[-_SETTLED_PREVIEW:]:
        console.print(f"    - {entry}")
    if total > _SETTLED_PREVIEW:
        console.print(
            f"    ({total - _SETTLED_PREVIEW} older rulings not shown — "
            f"read them all with `gz handoff rulings`)"
        )


def handoff_rulings_cmd(
    *,
    limit: int | None = None,
    search: str | None = None,
    as_json: bool = False,
    base_path: Path | None = None,
) -> int:
    """Read the settled-ruling corpus (GHI #838).

    The corpus left the handoff documents when it reached 91.4% of them; this is
    the verb that replaced opening one and scrolling. Read-only: rulings are
    booked by ``gz handoff create`` composing them from the predecessor, never
    by a hand edit here.
    """
    root = base_path if base_path is not None else get_project_root()
    entries = read_rulings(root)
    if search:
        needle = search.casefold()
        entries = [entry for entry in entries if needle in entry.casefold()]
    if limit is not None and limit > 0:
        entries = entries[-limit:]
    if as_json:
        console.print_json(json.dumps(entries))
        return 0
    if not entries:
        console.print("No settled rulings booked.")
        return 0
    console.print(f"settled rulings — do NOT re-open ({len(entries)}):")
    for entry in entries:
        console.print(f"  - {entry}")
    return 0


def handoff_resume_cmd(
    *,
    adr: str | None = None,
    as_json: bool = False,
    now: str | None = None,
    base_path: Path = Path(),
) -> None:
    """Resume the newest handoff for ``adr`` with staleness (REQ-0.0.65-03-02).

    Read-only projection of :func:`resume_handoff`. ``now`` is computed here when
    not supplied (the API takes it as a required parameter); it is injectable so
    staleness classification can be asserted deterministically. ``--json`` emits
    the ``ResumeResult`` dump; the human form shows path, staleness, and every
    extracted next step with the live state of the references it cites.
    """
    resolved_now = now if now is not None else datetime.now(UTC).isoformat()
    root = get_project_root() if base_path == Path() else base_path
    result = resume_handoff(
        adr_id=adr,
        base_path=base_path,
        now=resolved_now,
        reference_checker=_live_reference_checker(root),
    )
    if as_json:
        print(json.dumps(result.model_dump(), indent=2))  # noqa: T201
        return
    _render_resume(result)


def _current_branch(base_path: Path) -> str:
    """Resolve the current git branch, or empty string when unavailable.

    An empty branch is not silently tolerated: it fails the downstream
    frontmatter gate (fail-closed), which is the correct refusal.
    """
    root = get_project_root() if base_path == Path() else base_path
    rc, out, _ = git_cmd(root, "rev-parse", "--abbrev-ref", "HEAD")
    return out.strip() if rc == 0 else ""


def handoff_create_cmd(
    *,
    adr: str | None = None,
    slug: str,
    agent: str,
    decisions: str,
    branch: str | None = None,
    summary: str | None = None,
    context: str | None = None,
    next_steps: str | None = None,
    pending: str | None = None,
    verification: str | None = None,
    evidence: str | None = None,
    obpi: str | None = None,
    continues_from: str | list[str] | None = None,
    session_id: str | None = None,
    settled: list[str] | None = None,
    mode: str = "CREATE",
    as_json: bool = False,
    base_path: Path = Path(),
) -> None:
    """Write a handoff through the fail-closed gate (REQ-0.0.65-03-03).

    Builds all seven required sections from their flags and routes them through
    :func:`create_handoff`. On a validation refusal NOTHING is written and the
    verb exits 1; on success the written path is reported.

    Every required section has a flag (GHI #692). Previously only Decisions Made
    and Current State Summary did, so the default invocation emitted five empty
    headings and the gate — which checked presence, not population — blessed the
    result. An unsupplied section is now a refusal, not a silent hollow.

    ``mode`` selects the register-entry class. ``CREATE`` (the default) and
    ``RESUME`` are departure notices; ``CHECKPOINT`` is the mid-flight bookmark
    (GHI #756) — the session writes one WITHOUT departing, so it is not a token
    surrender and `find_exchange_for_release` skips it. Without this parameter
    every write took the ``CREATE`` default, recording a bookmark as a departure.

    ``settled`` seats rulings that arrived after the PRIOR handoff was authored —
    the operator rules on a GHI once the session's handoff is already committed, so
    the next handoff is the only seat available. It is normally unnecessary: the
    section self-populates from the predecessor's ``[operator-ruled]`` decisions.
    """
    supplied = {
        "summary": summary,
        "context": context,
        "decisions": decisions,
        "next_steps": next_steps,
        "pending": pending,
        "verification": verification,
        "evidence": evidence,
    }
    sections = {
        section: body
        for section, param in SECTION_PARAMS.items()
        if (body := supplied[param]) is not None
    }
    # Seat late-arriving rulings. `create_handoff` UNIONS these with whatever the
    # predecessor carried, so passing --settled never drops booked history.
    if settled:
        sections[SETTLED_SECTION] = "\n".join(f"- {entry}" for entry in settled)
    _warn_on_silent_chain_root(adr=adr, continues_from=continues_from, base_path=base_path)
    try:
        path = create_handoff(
            adr_id=adr,
            branch=branch or _current_branch(base_path),
            agent=agent,
            slug=slug,
            sections=sections,
            obpi_id=obpi,
            continues_from=continues_from,
            session_id=session_id,
            base_path=base_path,
            mode=mode,
            reference_checker=_live_reference_checker(base_path),
        )
    except HandoffValidationError as exc:
        console.print(f"[red]Refusing to write handoff:[/red] {exc}", style="red")
        raise SystemExit(1) from exc

    if as_json:
        print(json.dumps({"path": path.as_posix()}))  # noqa: T201
        return
    console.print(path.as_posix())


def _warn_on_silent_chain_root(
    *, adr: str | None, continues_from: str | list[str] | None, base_path: Path
) -> None:
    """Speak up when this handoff will inherit no settled rulings (GHI #717).

    ``_newest_predecessor`` returns ``None`` for every ADR-less handoff, and
    ``_carried_settled`` inherits nothing from a ``None`` predecessor. Since
    GHI #709 made ``adr_id`` optional the ADR-less path is the *normal* path, so
    the default invocation in a repo that already has handoffs quietly produces
    a chain root carrying zero settled rulings. Observed live 2026-07-26: a
    handoff dropped all 32 booked rulings and validated clean, caught only by a
    human noticing the section was short.

    Auto-linking to the newest handoff is NOT the cure — ``handoff_api``'s
    ``_newest_predecessor`` already rejected it (*"the newest handoff overall is
    not its lineage, and linking to it would assert a continuity that does not
    exist"*). The author is the only one who knows the lineage; this makes sure
    they are asked rather than silently defaulted.

    Advisory by design: an unlinked handoff can be a genuine chain root, so this
    warns and proceeds rather than fail-closing on a legitimate shape.
    """
    if continues_from_refs(continues_from):
        return
    prior = list_handoffs(adr_id=adr, base_path=base_path)
    if not prior:
        return  # A genuine chain root — there is nothing to inherit.

    newest = Path(prior[0].path).name
    console.print(
        f"[yellow]Warning:[/yellow] no --continues-from, so this handoff is a chain root "
        f"and inherits ZERO settled rulings from {len(prior)} existing handoff(s). "
        "Rulings booked by predecessors will not carry forward (GHI #717).\n"
        f"  If it continues prior work, re-run with: --continues-from {newest}\n"
        "  If it is a genuine chain root, no action is needed."
    )


def handoff_authorize_cmd(
    *,
    handoff: str,
    operator_text: str,
    session_id: str,
    decision: str = "proceed",
    set_aside: list[str] | None = None,
    as_json: bool = False,
    base_path: Path = Path(),
) -> None:
    """Book the operator's transit decision on a resumed handoff (GHI #574, #757).

    Records the operator's ruling on this session's resumed handoff
    (`gz-session-handoff` SKILL.md § RESUME). It authorizes nothing: the
    Operator Authorization Gate was retired 2026-08-15 (operator ruling: a
    handoff is an advisor, not a gate-keeping nanny), and advising is now the
    whole mechanism. The ruling must still be BOOKED — presenting the steps and
    being told "go" in conversation leaves no Layer-2 record of what the
    operator actually decided.

    **This is a transit decision, not an attestation.** ADR-0.0.33 § Alternatives
    rejects the conflation by name — completion-attestation is reserved for
    claims about completed planned work, and spending that register on an
    every-transit gate cheapens the sacred word. ``decision`` borrows the
    airlock's ``Decision`` grammar (PROCEED / PAUSE / HOLD / REVERT); only
    PROCEED lifts. The predecessor shape was a bare consent boolean, so an
    operator who looked and said *not yet* left no record at all.

    ``set_aside`` names advised steps the ruling declines — the clearance
    AMENDMENT record (*"ATC keeps a record of all clearances issued and all
    amendments."*). Departure from counsel was previously invisible.

    ``--operator-text`` is the operator's VERBATIM words, and stays verbatim by
    operator ruling (2026-08-05). Do not paraphrase, summarize, or improve them
    (§ OPERATOR ECONOMY OF EFFORT #3 — the agent seats the operator's words,
    never rewrites them). Booking a decision the operator did not give is
    fabrication, the same failure as fabricating a receipt id.

    ``session_id`` is passed explicitly rather than read from a harness env var:
    `commands/` is fenced to a two-entry env allowlist (NO_COLOR / FORCE_COLOR)
    precisely so vendor coupling cannot leak into the command layer. The gate's
    block prose interpolates the id, so the caller never has to discover it.
    """
    from gzkit.airlock.model import Decision  # noqa: PLC0415
    from gzkit.commands.common import ensure_initialized  # noqa: PLC0415
    from gzkit.handoff_resume_gate import (  # noqa: PLC0415
        booking_targets_the_armed_handoff,
        newest_handoff,
    )
    from gzkit.ledger import Ledger  # noqa: PLC0415
    from gzkit.ledger_events import handoff_resume_decided_event  # noqa: PLC0415

    # The grammar is borrowed from the airlock; the RECORDS stay this layer's own
    # (GHI #757). Re-declaring the four tokens here would be the per-copy drift
    # the CHECKPOINT_MODE single-sourcing exists to avoid.
    try:
        resolved_decision = Decision(decision.strip().lower())
    except ValueError:
        allowed = ", ".join(d.value for d in Decision)
        console.print(
            f"[red]Refusing to book:[/red] unknown decision {decision!r}.\n"
            f"WHY: the gate compares the token exactly and fails closed on anything "
            f"it does not recognize, so an unknown token would book a record that "
            f"reads as a ruling but authorizes nothing (GHI #757).\n"
            f"NEXT STEP: re-run with one of: {allowed}.",
            style="red",
        )
        raise SystemExit(1) from None

    resolved_session = session_id.strip()
    if not resolved_session:
        console.print(
            "[red]Refusing to authorize:[/red] empty --session-id.\n"
            "WHY: authorization is session-scoped so a prior session's ruling cannot "
            "silently license this one (GHI #574). An empty id would authorize nothing "
            "and read as consent.\n"
            "NEXT STEP: copy the command from the resume gate's block message — it "
            "interpolates the session id the harness reported.",
            style="red",
        )
        raise SystemExit(1)

    root = get_project_root() if base_path == Path() else base_path
    handoff_path = Path(handoff)
    resolved = handoff_path if handoff_path.is_absolute() else root / handoff
    if not resolved.is_file():
        console.print(
            f"[red]Refusing to authorize:[/red] no handoff at {handoff}.\n"
            "WHY: an authorization must name the handoff it rules on, or the audit "
            "trail records consent to nothing.\n"
            "NEXT STEP: run `uv run gz handoff list` and authorize a real path.",
            style="red",
        )
        raise SystemExit(1)

    rel = resolved.relative_to(root).as_posix() if resolved.is_relative_to(root) else handoff

    # The coupling `handoff_path` asserts, enforced where the record is created
    # (GHI #795). Booking is the only place it CAN be enforced: the gate lifts on
    # `session_id` alone by design, because comparing paths at lift time re-arms
    # an already-cleared session the moment any new handoff lands (GHI #619,
    # #755). Refusing here means the wrong consent record is never written to an
    # append-only ledger, rather than written and later disbelieved.
    if not booking_targets_the_armed_handoff(root, resolved):
        armed = newest_handoff(root)
        armed_rel = (
            armed.relative_to(root).as_posix()
            if armed is not None and armed.is_relative_to(root)
            else str(armed)
        )
        console.print(
            f"[red]Refusing to book:[/red] {rel} is not the handoff this session resumed.\n"
            f"WHY: this session resumed {armed_rel}, and a ruling names the advised "
            f"steps the operator actually read. Booking against a different document "
            f"would record consent for steps nobody was shown — the coupling predicate "
            f"matches on session id, not on path (GHI #795).\n"
            f"NEXT STEP: re-run against the armed handoff, or rule on it explicitly:\n"
            f"  uv run gz handoff decide --handoff {armed_rel} \\\n"
            f"    --session-id {resolved_session} --decision {resolved_decision} "
            f'--operator-text "<their exact words>"',
            style="red",
        )
        raise SystemExit(1)

    config = ensure_initialized()
    Ledger(root / config.paths.ledger).append(
        handoff_resume_decided_event(
            session_id=resolved_session,
            handoff_path=rel,
            operator_text=operator_text,
            decision=resolved_decision,
            set_aside=set_aside,
        )
    )

    payload = {
        "status": "decided",
        "decision": resolved_decision,
        "handoff_path": rel,
        "session_id": resolved_session,
        "set_aside": list(set_aside or []),
    }
    if as_json:
        print(json.dumps(payload))  # noqa: T201
        return
    lifted = " (gate lifted)" if resolved_decision == Decision.PROCEED else " (gate stays armed)"
    console.print(f"{resolved_decision} — {rel} (session {resolved_session}){lifted}")
