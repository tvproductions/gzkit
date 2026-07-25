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
from gzkit.handoff_validation import SETTLED_SECTION, HandoffValidationError
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
    base_path: Path = Path("."),
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


def _render_settled(result: ResumeResult) -> None:
    """Render rulings carried forward as settled (GHI #696 defect 3)."""
    if not result.settled:
        return
    console.print(f"  settled — do NOT re-open ({len(result.settled)}):")
    for entry in result.settled:
        console.print(f"    - {entry}")


def handoff_resume_cmd(
    *,
    adr: str | None = None,
    as_json: bool = False,
    now: str | None = None,
    base_path: Path = Path("."),
) -> None:
    """Resume the newest handoff for ``adr`` with staleness (REQ-0.0.65-03-02).

    Read-only projection of :func:`resume_handoff`. ``now`` is computed here when
    not supplied (the API takes it as a required parameter); it is injectable so
    staleness classification can be asserted deterministically. ``--json`` emits
    the ``ResumeResult`` dump; the human form shows path, staleness, and every
    extracted next step with the live state of the references it cites.
    """
    resolved_now = now if now is not None else datetime.now(UTC).isoformat()
    root = get_project_root() if base_path == Path(".") else base_path
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
    root = get_project_root() if base_path == Path(".") else base_path
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
    continues_from: str | None = None,
    session_id: str | None = None,
    settled: list[str] | None = None,
    as_json: bool = False,
    base_path: Path = Path("."),
) -> None:
    """Author a handoff through the fail-closed gate (REQ-0.0.65-03-03).

    Builds all seven required sections from their flags and routes them through
    :func:`create_handoff`. On a validation refusal NOTHING is written and the
    verb exits 1; on success the written path is reported.

    Every required section has a flag (GHI #692). Previously only Decisions Made
    and Current State Summary did, so the default invocation emitted five empty
    headings and the gate — which checked presence, not population — blessed the
    result. An unsupplied section is now a refusal, not a silent hollow.

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
        )
    except HandoffValidationError as exc:
        console.print(f"[red]Refusing to write handoff:[/red] {exc}", style="red")
        raise SystemExit(1) from exc

    if as_json:
        print(json.dumps({"path": path.as_posix()}))  # noqa: T201
        return
    console.print(path.as_posix())


def handoff_authorize_cmd(
    *,
    handoff: str,
    operator_text: str,
    session_id: str,
    as_json: bool = False,
    base_path: Path = Path("."),
) -> None:
    """Book the operator's ruling on a resumed handoff (GHI #574).

    Discharges the Operator Authorization Gate (`gz-session-handoff` SKILL.md
    § RESUME) for this session: until this event is on the ledger, the resume
    gate refuses every mutating tool call. The gate reads Layer-2, so the ruling
    must be BOOKED — presenting the steps and being told "go" in conversation
    leaves no record, which is the state that let the gate hold by goodwill alone.

    ``--operator-text`` is the operator's VERBATIM words. Do not paraphrase,
    summarize, or improve them (AGENTS.md § Attestation; § OPERATOR ECONOMY OF
    EFFORT #3 — the agent seats the operator's words, never rewrites them).
    Authorizing without a ruling actually given is fabrication, the same failure
    as fabricating a receipt id.

    ``session_id`` is passed explicitly rather than read from a harness env var:
    `commands/` is fenced to a two-entry env allowlist (NO_COLOR / FORCE_COLOR)
    precisely so vendor coupling cannot leak into the command layer. The gate's
    block prose interpolates the id, so the caller never has to discover it.
    """
    from gzkit.commands.common import ensure_initialized  # noqa: PLC0415
    from gzkit.ledger import Ledger  # noqa: PLC0415
    from gzkit.ledger_events import handoff_resume_authorized_event  # noqa: PLC0415

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

    root = get_project_root() if base_path == Path(".") else base_path
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
    config = ensure_initialized()
    Ledger(root / config.paths.ledger).append(
        handoff_resume_authorized_event(
            session_id=resolved_session,
            handoff_path=rel,
            operator_text=operator_text,
        )
    )

    payload = {"status": "authorized", "handoff_path": rel, "session_id": resolved_session}
    if as_json:
        print(json.dumps(payload))  # noqa: T201
        return
    console.print(f"authorized — {rel} (session {resolved_session})")
