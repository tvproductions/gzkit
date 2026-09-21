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

from rich.markup import escape

from gzkit.commands.common import console, get_project_root
from gzkit.commands.reference_checker import live_reference_checker
from gzkit.handoff_api import (
    DecisionAttribution,
    HandoffInfo,
    NextStep,
    ResumeResult,
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
from gzkit.remote_divergence import (
    RemoteDivergence,
    behind_origin_caveat,
    probe_remote_divergence,
)
from gzkit.utils import git_cmd

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


def _render_step_references(step: NextStep) -> None:
    """Render one step's citations and their live state, indented under it.

    A citation naming another repository prints that repository, because its
    ``unknown`` means "not ours to answer" while a bare ``unknown`` means "this
    repository could not be read" — two different things for the reader to do.
    """
    if not step.references:
        return
    rendered = " · ".join(
        f"{ref.kind.value} {ref.repo + '#' if ref.repo else ''}{ref.identifier}: {ref.state.value}"
        for ref in step.references
    )
    console.print(f"       refs: {rendered}")


def _render_resume(result: ResumeResult, divergence: RemoteDivergence | None = None) -> None:
    """Human-readable resume report — path, staleness, and EVERY next step.

    All authored steps are rendered, not just the head: surfacing one is what
    let items 2-N fall out of the advisory channel and be re-adjudicated as
    open loops in the successor session (GHI #696).

    ``divergence`` carries the behind-origin caveat, printed directly under the
    path because it qualifies the DOCUMENT'S IDENTITY rather than its contents:
    on a clone behind ``origin/main`` the newest handoff on disk is not the
    newest handoff that exists, and every step below is then advice from a
    superseded document. ``staleness`` cannot say this — it measures the age of
    the document that WAS selected, never whether the tree it was selected from
    is current (GHI #872).

    Each step also carries the live state of what it cites. A step citing a
    settled reference is flagged, because relaying such a step unexamined is how a
    closed GHI got re-adjudicated three sessions running (GHI #696 defect 2). The
    flag reports the citation, not a verdict — whether the reference is a
    precondition (step is void) or provenance (step still stands) is the reader's
    call, and no available signal decides it.
    """
    console.print(f"resume — {result.path}")
    if divergence is not None and divergence.is_behind:
        console.print(f"  {behind_origin_caveat(divergence.behind)}")
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
            console.print(f"    {index}. {marker}{escape(step.text)}")
            _render_step_references(step)
        flagged = sum(1 for step in result.steps if step.cites_settled)
        if flagged:
            console.print(
                f"  {flagged} step(s) cite a settled reference — confirm whether it is a "
                "precondition (step is void) or context (step still stands)."
            )
    _render_chain(result)
    _render_decisions(result)
    _render_settled(result)


def _render_chain(result: ResumeResult) -> None:
    """Render the lineage `resume_handoff` already walked (GHI #870).

    `continues_from` was never the unbuilt half: `load_handoff_chain` has run on
    every resume since `af6bba3ed` (2026-07-13), filling `ResumeResult.chain`
    with a bounded, cycle-safe, multi-parent walk. Nothing read the field. A
    20-document lineage was resolved and discarded inside one function call
    while the reader saw a single path — so a CHECKPOINT sitting newest above a
    CREATE advised from the narrow document and never named the broad one.

    Oldest-first, head excluded: the head is already rendered as `resume — `,
    and repeating it as its own ancestor would misstate the depth.

    A chain of one prints nothing. Announcing a lineage a root does not have
    manufactures the continuity `create_handoff` refuses to fabricate at
    authoring time; the renderer must not reintroduce it downstream.
    """
    ancestors = result.chain[:-1]
    if not ancestors:
        return
    # Filenames, not paths: the directory is constant across every entry, so
    # repeating it 19 times spends the line budget on the one part that
    # identifies nothing — and pushes the timestamped name past the console
    # width, where rich soft-wraps it mid-token and the list stops scanning.
    # `soft_wrap` then holds even a long name on one line.
    console.print(f"  lineage ({len(ancestors)} ancestor(s) in .gzkit/handoffs/, oldest first):")
    for path in ancestors:
        console.print(f"    - {Path(path).name}", soft_wrap=True)
    if result.chain_truncated:
        # The walk truncates silently. Printing the truncated list without this
        # asserts a completeness it never established — and the bound only
        # becomes load-bearing once something reads the chain, which is now.
        console.print(
            "  lineage hit the walk's depth bound — additional ancestor references "
            "remain unvisited and are NOT listed above."
        )


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
            console.print(f"      - {escape(decision.text)}")


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
        console.print(f"    - {escape(entry)}")
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
    booked by ``gz handoff create`` (the document's own rulings plus those it
    inherits from the predecessor, GHI #1000), never
    by a hand edit here.
    """
    root = base_path if base_path is not None else get_project_root()
    corpus = read_rulings(root)
    entries = corpus
    if search:
        needle = search.casefold()
        entries = [entry for entry in entries if needle in entry.casefold()]
    if limit is not None and limit > 0:
        entries = entries[-limit:]
    if as_json:
        print(json.dumps(entries, indent=2, ensure_ascii=False))  # noqa: T201
        return 0
    if not entries:
        # A search miss is not an empty store: saying "none booked" to a reader
        # checking whether a question is settled misreports the whole corpus.
        if corpus:
            console.print(
                f'No settled ruling matches "{escape(search or "")}" ({len(corpus)} booked).'
            )
        else:
            console.print("No settled rulings booked.")
        return 0
    console.print(f"settled rulings — do NOT re-open ({len(entries)}):")
    for entry in entries:
        console.print(f"  - {escape(entry)}")
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
        reference_checker=live_reference_checker(root),
    )
    if as_json:
        # Deliberately unqualified: `--json` is the ``ResumeResult`` dump, and
        # divergence is a property of the TREE rather than of the resumed
        # document. Widening the model to carry it would put a probe result
        # inside an artifact projection. Machine consumers read the tree.
        print(json.dumps(result.model_dump(), indent=2))  # noqa: T201
        return
    _render_resume(result, probe_remote_divergence(root))


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
            reference_checker=live_reference_checker(base_path),
        )
    except HandoffValidationError as exc:
        console.print(f"[red]Refusing to write handoff:[/red] {escape(str(exc))}", style="red")
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
    airlock's ``Decision`` grammar (PROCEED / PAUSE / HOLD / REVERT); all four
    are equally bookable records and none gates anything. The predecessor shape
    was a bare consent boolean, so an operator who looked and said *not yet*
    left no record at all.

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
    precisely so vendor coupling cannot leak into the command layer. The caller
    passes the id of the harness session the ruling was given in.
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
            f"WHY: the decision grammar is closed, so an unknown token would book a "
            f"record that reads as a ruling but names no decision anyone can read "
            f"back (GHI #757).\n"
            f"NEXT STEP: re-run with one of: {allowed}.",
            style="red",
        )
        raise SystemExit(1) from None

    resolved_session = session_id.strip()
    if not resolved_session:
        console.print(
            "[red]Refusing to book:[/red] empty --session-id.\n"
            "WHY: a ruling is session-scoped so a prior session's ruling cannot be "
            "read as this one's (GHI #574). An empty id would record a ruling that "
            "belongs to no session.\n"
            "NEXT STEP: re-run with the id of the harness session the operator "
            "ruled in.",
            style="red",
        )
        raise SystemExit(1)

    root = get_project_root() if base_path == Path() else base_path
    handoff_path = Path(handoff)
    resolved = handoff_path if handoff_path.is_absolute() else root / handoff
    if not resolved.is_file():
        console.print(
            f"[red]Refusing to book:[/red] no handoff at {handoff}.\n"
            "WHY: a ruling must name the handoff it rules on, or the audit trail "
            "records a ruling on nothing.\n"
            "NEXT STEP: run `uv run gz handoff list` and book against a real path.",
            style="red",
        )
        raise SystemExit(1)

    rel = resolved.relative_to(root).as_posix() if resolved.is_relative_to(root) else handoff

    # The coupling `handoff_path` asserts, enforced where the record is created
    # (GHI #795). Booking time is where the operator's reading is verifiable,
    # because that is when they read it; the placement predates the resume gate's
    # retirement, when comparing paths at lift time re-armed an already-cleared
    # session the moment any new handoff landed (GHI #619, #755). Refusing here
    # means the wrong record is never written to an append-only ledger, rather
    # than written and later disbelieved.
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
    # Every decision is an equally bookable record and none gates anything (resume
    # gate retired 2026-08-15), so the line names the decision and nothing more.
    console.print(f"{resolved_decision} — {rel} (session {resolved_session}) recorded")
