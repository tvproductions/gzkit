"""Operator Authorization Gate for handoff resume — the RESUME half's teeth (GHI #574).

`.gzkit/skills/gz-session-handoff/SKILL.md` § RESUME declares a **universal**
Operator Authorization Gate:

    "Every resume requires explicit operator authorization before any execution,
    at every freshness level — Fresh included. ... no file mutation / `gz`
    ceremony / migration until the operator rules."

That was prose plus a template banner, enforced by nothing — it held only by the
model's goodwill. This module is the mechanism. It is the RESUME counterpart to
`validate_sections_populated` (GHI #692, the CREATE half): together they close
`gz-session-handoff`'s two declared-but-unenforced clauses, so the skill now binds
both what a handoff must CONTAIN and what an agent may DO on reading one.

Design notes that are load-bearing:

* **The decision lives here, not in the hook.** `.claude/hooks/*.py` are generated
  text (`src/gzkit/hooks/scripts/`), so logic embedded there is unreachable by
  `@enforces` and untestable as a unit. The hook is a thin adapter over
  :func:`decide` — the ports-and-adapters shape, and the only shape a live
  negative control can point an entrypoint at.

* **Session-scoped, not per-handoff — AND authorship-aware.** Authorization cites
  the harness ``session_id``. Per-handoff arming would let `gz obpi complete`'s
  mechanically written completion handoff (GHI #619) re-arm the gate mid-session,
  blocking the operator right after a completion they just attested. Session
  scoping closed that instance and left the CLASS open: it protects a session that
  is ALREADY authorized, and structurally cannot protect one that never was —
  there is no authorization event to scope to. So a session that did fresh work
  and then wrote a bookmark armed the gate against its own author (GHI #755).
  :func:`_authored_by_session` closes the class by asking who WROTE the handoff,
  which is the question the § RESUME clause's own scope word ("every *resume*")
  was always asking.

* **There is no allowlist, because Bash is not gated** (operator ruling
  2026-08-14 — see :data:`MUTATING_TOOLS` for the reasoning and what it gives
  up). A 44-entry allowlist of permitted reads lived here for a month and needed
  13 corrections in 29 days, every one of them a false refusal of a read the
  § Claim Verification Gate *mandates*. The root was never the list's contents:
  a handoff is a synthetic memory refresh, an artifact with no natural blast
  radius, so any answer to "what should reading it prevent?" had to be invented
  and the invented one was maximal. The gate now blocks file mutation, which is
  the one consequence the artifact actually supports.

* **The gate never blocks its own recovery.** `gz handoff decide` runs through
  Bash and is therefore never gated at all now. A rule that forbids the command
  that lifts it is worse than the hole it plugs (operator ruling, 2026-07-16
  permission-surface pass) — that hazard is now structurally impossible rather
  than handled by an allowlist entry.

Coverage limits are declared, not hidden — see :data:`UNWITNESSABLE`.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.handoff_validation import HandoffValidationError, parse_frontmatter

__all__ = [
    "MUTATING_TOOLS",
    "RESUME_GATE_CLAIM_IDS",
    "UNWITNESSABLE",
    "Verdict",
    "booking_targets_the_armed_handoff",
    "decide",
    "is_resume_authorized",
    "newest_handoff",
]

_LEDGER_REL = ".gzkit/ledger.jsonl"
_AUTHORIZED_EVENT = "handoff_resume_authorized"

#: The successor event (GHI #757). `handoff_resume_authorized` was a boolean —
#: booking it WAS consent, so the register could only ever say yes and an
#: operator who looked and said "not yet" left no record. The decision event
#: carries a token from the airlock's `Decision` grammar, so only PROCEED lifts.
#:
#: The legacy event is still read and still lifts. Every authorization booked
#: before this change is one, and a gate that stopped reading them would
#: retroactively un-authorize the entire committed ledger.
_DECIDED_EVENT = "handoff_resume_decided"

#: The only decision that lifts the gate. Compared exactly: the gate reads raw
#: JSONL, so nothing upstream guarantees the token is in the enum, and anything
#: that is not PROCEED is not consent.
_PROCEED = "proceed"

#: Tools whose use is "execution" under the § RESUME contract's "no file
#: mutation" clause.
#:
#: **`Bash` was here and was removed** (operator ruling 2026-08-14, verbatim:
#: *"why is the handoff gate so picky? it is a reminder of what we were doing
#: and what to do next, not a nanny"*, then *"i say the word"*). The arm was
#: added on the reasoning that `gz` ceremony and migration run through Bash, so
#: a `Write|Edit`-only gate would *"enforce one third of the declared clause"*.
#: That reasoning was sound about the clause and wrong about the artifact.
#:
#: A handoff is a **synthetic memory refresh** by operator canon (AGENTS.md,
#: `invariant` tier, 2026-08-06); entry/exit authorization is TRANSIT's subject,
#: the airlock's (ADR-0.33.0). A memory artifact has no natural blast radius, so
#: "what should reading a reminder prevent?" had no principled answer — the
#: answer invented was every mutating tool call, then whittled by 44 read
#: exceptions across 13 corrections in 29 days, EVERY ONE of them a Bash
#: refusal. This arm never needed one, because it has no allowlist to be
#: incomplete. GHI #574's own charter had quoted the remedy: *"place the human
#: at a mechanical gate, **not at every keystroke**."*
#:
#: What is given up is named, not hidden: `gz obpi complete`, `gz attest`, and
#: commits run via Bash are no longer refused on an unruled handoff. Gate 5's
#: attestation requirement, the pre-commit hook, and the pre-push `gz check`
#: still bind them; only the unruled-handoff precondition lifts. Re-adding Bash
#: here re-opens the recurrence — `BashIsNotGatedOnAHandoffTests` is the pin.
MUTATING_TOOLS = frozenset({"Write", "Edit", "NotebookEdit"})

UNWITNESSABLE: tuple[str, ...] = (
    "MCP tool calls: the harness routes them past the Write|Edit|NotebookEdit "
    "matchers, so a connector that writes is unseen by this gate.",
    "Harness-native mutation outside the tool layer (e.g. an IDE edit by the "
    "operator) is not a resuming agent's execution and is deliberately out of scope.",
    "Mutation via SHELL — `gz` ceremony, commits, `rm`, in-place editors — is "
    "deliberately out of scope since 2026-08-14 (see MUTATING_TOOLS). This gate "
    "no longer claims any coverage there; Gate 5, pre-commit and pre-push do. "
    "Stated because a green here once meant more than it does.",
    "Refusal CORRECTNESS: `handoff_resume_blocked` records that a call was "
    "refused, never whether refusing was right. A rising count is a prompt to "
    "look, not a defect measure — some refusals are the gate working.",
)


class Verdict(BaseModel):
    """Gate decision for one tool call. ``blocked`` is the whole contract."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    blocked: bool = Field(..., description="True when the tool call must be refused")
    reason: str = Field(default="", description="Three-part guardrail prose; empty when allowed")


def newest_handoff(project_root: Path) -> Path | None:
    """Return the newest resumable session handoff, or None.

    Delegates selection to :func:`gzkit.handoff_api.list_handoffs` — the existing
    production newest-first projection — rather than re-deriving it. Recency is a
    frontmatter-``timestamp`` property, and ``list_handoffs`` already parses it,
    sorts by instant (offset-aware), and admits only documents carrying a
    ``mode``, which excludes the generated ``.gzkit/handoffs/AGENTS.md``
    subtree-rules file (it has no frontmatter at all). ``mode`` — not ``adr_id``
    — is the discriminator, so an ADR-less handoff still arms the gate
    (GHI #709).

    A newest-by-FILENAME sort is wrong and was the first implementation's bug: 14
    of the 205 on-disk handoffs are not timestamp-prefixed, and ``OBPI-…`` sorts
    after ``20260716T…`` in ASCII, so the gate named a months-old handoff as the
    one to authorize. The "reading frontmatter is too slow for a PreToolUse hot
    path" premise that motivated it was also false: the walk measures ~33ms
    against a ~300ms ``uv run`` interpreter start the hook already pays.

    Abandoned register entries are skipped — a distinct document class
    (OBPI-0.0.72-02) describing a surrendered token, not context to resume.

    Floor bookmarks are DEPRIORITIZED, not skipped (GHI #758). The exit beat
    writes one at every session end, so a floor bookmark is always the newest
    document on disk — under a plain newest-first rule the precaution
    structurally out-competes the artifact it exists to back up, every session,
    forever. Observed 2026-08-05: a 1,765-byte bookmark reading "Unknown to the
    writer" was selected over a 24,877-byte authored handoff written 48 minutes
    earlier, and a whole session's orientation was built on the empty one.

    GHI #756 named this hazard while closing it on the sibling selector —
    `find_exchange_for_release` skips checkpoints "rather than
    returning-and-rejecting, because a later checkpoint would otherwise win the
    newest-candidate sort and take a genuine register entry down with it". Same
    sort, same corpus; this arm had not been taught it.

    Deprioritize rather than skip, because the floor is the point: a session that
    crashed or `/clear`ed before authoring leaves nothing else, which is the case
    GHI #756 built the beat to cover. And the discriminator is AUTHORSHIP, not
    `mode` — a floor bookmark and an operator-authored mid-flight checkpoint are
    both `CHECKPOINT`, so filtering on mode here would discard the authored one.
    Mode is the right question on the release arm (no checkpoint of any
    authorship surrenders a token); "who wrote it" is the right question here.
    """
    from gzkit.handoff_api import list_handoffs  # noqa: PLC0415  (avoids an import cycle)
    from gzkit.handoff_selection import is_floor_bookmark  # noqa: PLC0415  (same cycle)

    # `selection_rank`'s rule, expressed for an ALREADY-SORTED newest-first walk:
    # take the first authored candidate, else the first floor seen. Equivalent to
    # `max(..., key=selection_rank)` and deliberately not written that way — this
    # is a PreToolUse hot path, and max() would read every file in the corpus to
    # answer what early exit usually answers from one. The differential test in
    # `tests/governance/test_handoff_selection.py` is what holds the two readers
    # to the same answer, since sharing the constant alone cannot.
    floor: Path | None = None
    for info in list_handoffs(base_path=project_root):
        path = Path(info.path)
        candidate = path if path.is_absolute() else project_root / path
        try:
            frontmatter = parse_frontmatter(candidate.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, HandoffValidationError):
            continue
        if not isinstance(frontmatter, dict):
            # Unreadable shape → treat as resumable, deliberately. Skipping here
            # would fail OPEN for the gate: fewer candidates can mean no handoff
            # found, which means no gate at all. Arming on an odd document is the
            # safe direction; this is the pre-existing behavior, kept.
            return candidate
        if frontmatter.get("abandoned"):
            continue
        if is_floor_bookmark(frontmatter.get("agent")):
            # First one wins: the walk is newest-first, so this is the newest
            # floor. Held, not returned, until the corpus is known to carry no
            # authored handoff.
            floor = floor or candidate
            continue
        return candidate
    return floor


def booking_targets_the_armed_handoff(project_root: Path, handoff: Path) -> bool:
    """Return True when *handoff* is the document the gate is currently armed on.

    The coupling `handoff_path` was always supposed to express, enforced at the
    moment the record is CREATED (GHI #795). The field was written into every
    decision event and read back by nothing, so a ruling booked against document
    A discharged a gate armed on document B — consent recorded for advised steps
    the operator never read. A near-miss is recorded in
    ``.gzkit/handoffs/20260812T073455Z-…md`` § Important Context, where the
    advisement printed one path directly beside a recovery command for another.

    **Booking time, NOT lift time — and that placement is the whole design.**
    Comparing paths inside :func:`_lifts_the_gate` is per-handoff arming reached
    from the other direction, and it reintroduces the two regressions this module
    already closed: the instant any new handoff becomes :func:`newest_handoff`
    mid-session — `gz obpi complete`'s mechanically written completion record
    (GHI #619), an exit bookmark, a mid-flight checkpoint — an already-granted
    clearance stops matching and the gate re-arms against a session the operator
    cleared minutes earlier (GHI #755). A clearance is AMENDED mid-flight, never
    revoked. `LiftTimeStaysSessionScopedTests` is the fence that keeps it so.

    Nothing is armed → True. There is no document to mismatch, so refusing would
    block a harmless no-op, and the gate's standing rule is that it never blocks
    its own recovery.

    Relative paths resolve against *project_root*, because the repo-relative
    spelling is what the block prose prints — a predicate that compared only
    absolute paths would refuse the exact command it tells the operator to run.
    """
    armed = newest_handoff(project_root)
    if armed is None:
        return True
    candidate = handoff if handoff.is_absolute() else project_root / handoff
    try:
        return candidate.resolve() == armed.resolve()
    except OSError:
        return False


def is_resume_authorized(project_root: Path, session_id: str) -> bool:
    """Return True when this session carries an operator authorization on the ledger.

    Fails CLOSED (returns False) on an unreadable or absent ledger: a gate that
    opens when it cannot read its own evidence is not a gate. Scans raw JSONL
    rather than through the typed reader so a single malformed line elsewhere in
    the ledger cannot make the gate un-liftable.

    Matching is on ``session_id`` ALONE, deliberately — see
    :func:`booking_targets_the_armed_handoff` for why the event's
    ``handoff_path`` is not compared here and what breaks if it is.
    """
    if not session_id:
        return False
    ledger = project_root / _LEDGER_REL
    try:
        text = ledger.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    for line in text.splitlines():
        if _AUTHORIZED_EVENT not in line and _DECIDED_EVENT not in line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        if event.get("session_id") != session_id:
            continue
        if _lifts_the_gate(event):
            return True
    return False


def _lifts_the_gate(event: dict) -> bool:
    """Return True when this session-scoped event is consent to proceed.

    Two shapes, one meaning. The legacy `handoff_resume_authorized` is a
    boolean — its existence was consent — and it must keep lifting, or the
    whole committed ledger un-authorizes itself. The successor
    `handoff_resume_decided` carries a token, and only PROCEED is consent:
    PAUSE / HOLD / REVERT are rulings to NOT proceed and leave the gate armed,
    which is the state the boolean shape could not express.

    Fails CLOSED on an unrecognized token — a future or malformed decision is
    not consent (GHI #757).
    """
    kind = event.get("event")
    if kind == _AUTHORIZED_EVENT:
        return True
    if kind == _DECIDED_EVENT:
        return str(event.get("decision", "")).strip().lower() == _PROCEED
    return False


def _authored_by_session(handoff: Path, session_id: str) -> bool:
    """Return True when THIS session WROTE the handoff, rather than resuming one.

    § RESUME gates every *resume*, and authoring is not resuming. :func:`decide`
    read the newest handoff's mere EXISTENCE as proof the session was un-cleared
    and never asked who wrote it, so a session that authored one — a session-end
    bookmark, or a mid-flight checkpoint — armed the gate against itself and was
    refused its next mutation by prose asserting it had "resumed" the document it
    had just written (GHI #755). The operator's frame: a clearance is AMENDED
    mid-flight, never revoked.

    Fails CLOSED on every ambiguity — no session id, an unreadable or malformed
    document, or a handoff carrying no ``session_id`` at all (the entire corpus
    predating the field). The empty-id guard is load-bearing rather than
    defensive: without it an unattributed session would match an unattributed
    handoff and open the gate for both.

    No bypass is created. A session holding no clearance cannot ``Write``, and
    ``gz handoff create`` is Bash outside :data:`_PERMITTED_BASH` — so a handoff
    carrying this session's id can only exist if the session was already
    permitted to write it.
    """
    if not session_id:
        return False
    try:
        frontmatter = parse_frontmatter(handoff.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, HandoffValidationError):
        return False
    if not isinstance(frontmatter, dict):
        return False
    return frontmatter.get("session_id") == session_id


def record_refusal(
    project_root: Path,
    *,
    session_id: str,
    tool_name: str,
    tool_input: dict | None = None,
) -> bool:
    """Write the Layer-2 record of a refusal. Returns True when one was written.

    **Fail-open by contract, and this is the load-bearing property.** Every
    failure path returns False rather than raising: an unwritable ledger is a
    plumbing problem, and if it could raise, the hook would die with an error
    instead of a block — converting a telemetry improvement into a way to defeat
    the gate. The gate stays fail-CLOSED; only the measurement is fail-open.

    Records nothing when the call was not actually blocked, so the count means
    what it says. :func:`decide` is re-entered rather than trusted from a
    caller-supplied flag — a second copy of "was this blocked" is how the
    counter would come to disagree with the gate it counts.

    Advisory telemetry, never a gate: nothing reads this to make a decision. It
    exists so the question "what is this gate refusing?" has an answer that is
    not a session transcript (operator report 2026-08-14, *"that class of error
    is happening frequently - why is it recurring?"*).
    """
    verdict = decide(
        project_root, session_id=session_id, tool_name=tool_name, tool_input=tool_input
    )
    if not verdict.blocked:
        return False
    handoff = newest_handoff(project_root)
    if handoff is None:
        return False
    try:
        rel = handoff.relative_to(project_root).as_posix()
    except ValueError:
        rel = handoff.as_posix()
    try:
        from gzkit.ledger import Ledger  # noqa: PLC0415 — hot path; hook pays import cost once
        from gzkit.ledger_events import handoff_resume_blocked_event  # noqa: PLC0415

        Ledger(project_root / _LEDGER_REL).append(
            handoff_resume_blocked_event(
                session_id=session_id,
                handoff_path=rel,
                tool_name=tool_name,
            )
        )
    except (OSError, ValueError):
        return False
    return True


def _block_prose(
    handoff: Path,
    tool_name: str,
    project_root: Path,
    session_id: str,
) -> str:
    """Three-part guardrail prose: what failed, why forbidden, governed next step.

    Per `.claude/rules/guardrail-feedback-prose.md` — the feedback IS the prompt
    the operator would otherwise have typed, so it names the exact recovery
    command rather than pointing at documentation.
    """
    try:
        rel = handoff.relative_to(project_root).as_posix()
    except ValueError:
        rel = handoff.as_posix()
    # --session-id is INTERPOLATED, not left as a placeholder: the agent cannot
    # read its own harness session id (the id lives in the hook payload, and the
    # commands that would reveal it are themselves gated). A recovery command the
    # blocked party cannot complete is not a recovery path — the first version
    # omitted this and bricked its own author (dogfooded 2026-07-16).
    return (
        f"BLOCKED: {tool_name} refused — this session resumed a handoff "
        f"({rel}) and the operator has not ruled on it.\n\n"
        "WHY: `gz-session-handoff` SKILL.md § RESUME declares an Operator "
        "Authorization Gate — 'Every resume requires explicit operator authorization "
        "before any execution, at every freshness level — Fresh included ... no file "
        "mutation ... until the operator rules.' A handoff ADVISES; it does not "
        "authorize. Freshness shortens re-verification; it never converts an advisory "
        "into a license.\n\n"
        "NEXT STEP: present the handoff's advised next steps to the operator and wait "
        "for a ruling. When they rule, book their VERBATIM words (copy this line; the "
        "session id is already filled in):\n"
        f"  uv run gz handoff decide --handoff {rel} \\\n"
        f'    --session-id {session_id} --decision proceed --operator-text "<their exact words>"\n'
        "Only `proceed` lifts this gate. `pause`, `hold`, and `revert` are equally "
        "bookable rulings and leave it armed — an operator who looks and says 'not yet' "
        'should be recorded, not left unbooked. Add `--set-aside "<step>"` for any '
        "advised step the ruling declines.\n\n"
        "SCOPE: this gate blocks Write / Edit / NotebookEdit only. Bash is NOT gated "
        "— run any command you need, including `gz` verbs and `git`, to verify the "
        "handoff's claims before presenting them. Nothing about shell is inspected."
    )


def decide(
    project_root: Path,
    *,
    session_id: str,
    tool_name: str,
    tool_input: dict | None = None,
) -> Verdict:
    """Decide whether a tool call is permitted under the Operator Authorization Gate.

    Blocks when ALL hold: the tool mutates a file, a resumable handoff exists,
    this session did not AUTHOR that handoff, and no operator authorization is on
    the ledger for this session.

    There is no command inspection and no allowlist. Bash is not a mutating tool
    here (see :data:`MUTATING_TOOLS` for the ruling and what it gives up), which
    is what makes this function four checks long instead of four checks plus a
    shell parser — and what ends the false-refusal recurrence at its source
    rather than at its latest instance.
    """
    if tool_name not in MUTATING_TOOLS:
        return Verdict(blocked=False)
    handoff = newest_handoff(project_root)
    if handoff is None:
        return Verdict(blocked=False)
    # Authoring is not resuming (GHI #755). Checked BEFORE the ledger lookup so a
    # session that never held a clearance is still not un-cleared by its own
    # bookmark — the case session-scoping structurally cannot reach.
    if _authored_by_session(handoff, session_id):
        return Verdict(blocked=False)
    if is_resume_authorized(project_root, session_id):
        return Verdict(blocked=False)
    return Verdict(
        blocked=True,
        reason=_block_prose(handoff, tool_name, project_root, session_id),
    )


# ---------------------------------------------------------------------------
# Live negative controls — the floor's teeth for this gate (ADR-0.0.74 §5)
#
# ONE CLAIM PER DECLARED CLAUSE, deliberately. § RESUME names "no file mutation
# / gz ceremony / migration"; file mutation reaches the harness through
# Write|Edit|NotebookEdit, and gz ceremony/migration only through Bash. Splitting
# the claims means a gate that hooked only Write|Edit would leave
# `handoff-resume-unauthorized-bash` undischargeable — a FAILING claim in
# `gz check`, not a caveat an author can note and ship past. That is the whole
# point: you cannot write a negative control for a surface you did not hook.
# ---------------------------------------------------------------------------

#: This gate's EXEMPTION half (GHI #797). The two claims below prove the rule
#: fires on an unauthorized mutation; this one proves the clearance admits only
#: a ruling on the document the gate armed on. The distinction is not academic —
#: both rule claims were registered, enrolled, and passing on every `gz check`
#: for the entire life of GHI #795's coupling gap, because neither ever asked
#: WHICH document a ruling named.
RESUME_GATE_COUPLING_CLAIM_ID = "handoff-resume-booking-coupling"

#: `handoff-resume-unauthorized-bash` was a member and is RETIRED with the Bash
#: arm (operator ruling 2026-08-14). A claim asserting enforcement the gate no
#: longer performs is worse than an absent one — it reports green while blind.
RESUME_GATE_CLAIM_IDS: frozenset[str] = frozenset(
    {
        "handoff-resume-unauthorized-write",
        RESUME_GATE_COUPLING_CLAIM_ID,
    }
)


def _build_unauthorized_resume_violation() -> Path:
    """Plant a resumable handoff and a RUNTIME-UNIQUE authorized session.

    Both session ids derive from the ``mkdtemp``-random root name, so they are
    unknowable at mutation-authoring time: a broken :func:`decide` cannot
    special-case a fixed sentinel to sneak past the control (the Step-4b facade
    attack — a FIXED sentinel proves only that the gate blocks THAT ONE string,
    never the general rule). Returns the temp ROOT so the runner's
    ``shutil.rmtree(fixture())`` cleans it without leaking the parent.
    """
    root = Path(tempfile.mkdtemp(prefix="gzkit-resume-nc-"))
    handoffs = root / ".gzkit" / "handoffs"
    handoffs.mkdir(parents=True, exist_ok=True)
    # `mode` and `timestamp` are REQUIRED for this to be a handoff at all —
    # recency is a frontmatter property and `mode` is what distinguishes a
    # handoff from the generated AGENTS.md (GHI #709 moved the discriminator off
    # `adr_id`, which is now optional). A fixture lacking them arms nothing, so
    # the control would report FACADE against a working gate (caught live
    # 2026-07-16 when this fixture omitted them, and again 2026-07-21 when the
    # discriminator moved).
    (handoffs / "20260716T000000Z-nc.md").write_text(
        "---\n"
        "mode: CREATE\n"
        "adr_id: ADR-0.0.65\n"
        "branch: main\n"
        "timestamp: '2026-07-16T00:00:00Z'\n"
        "agent: g0\n"
        "---\n\n## Decisions Made\n\nnc\n",
        encoding="utf-8",
    )
    authorized = {
        "event": _AUTHORIZED_EVENT,
        "session_id": f"nc-auth-{root.name}",
        "handoff_path": ".gzkit/handoffs/20260716T000000Z-nc.md",
        "operator_text": "negative control",
    }
    (root / ".gzkit" / "ledger.jsonl").write_text(json.dumps(authorized) + "\n", encoding="utf-8")
    return root


def _ep_resume_gate_differential(root: Path, tool_name: str, tool_input: dict) -> int:
    """Assert the DIFFERENTIAL: refuse unauthorized AND permit authorized.

    Truthy only when BOTH hold, which proves the verdict tracks AUTHORIZATION
    (the general rule) rather than any fixed answer. An always-block mutation
    fails the permit pole; an always-allow mutation fails the refuse pole; a
    sentinel special-case fails the refuse pole on the unknowable session id.
    The verdict is COMPUTED by production :func:`decide` with no forcing kwarg
    pre-bound (§ Boundary Invariants #7).
    """
    refused = decide(
        root, session_id=f"nc-unauth-{root.name}", tool_name=tool_name, tool_input=tool_input
    ).blocked
    permitted = not decide(
        root, session_id=f"nc-auth-{root.name}", tool_name=tool_name, tool_input=tool_input
    ).blocked
    return 1 if (refused and permitted) else 0


def _ep_resume_gate_write(root: Path) -> int:
    """Production entrypoint: the "no file mutation" clause, over both poles."""
    return _ep_resume_gate_differential(root, "Write", {"file_path": "src/x.py"})


def _build_mis_targeted_booking_violation() -> Path:
    """Plant TWO resumable handoffs so one of them is provably not the armed one.

    A single-handoff fixture cannot express this violation at all: with one
    document on disk, every booking targets the armed one and the control would
    pass against a gate that never compares anything — the facade shape §5
    exists to refuse. The runtime-random root name keeps both paths unknowable
    at mutation-authoring time.
    """
    root = Path(tempfile.mkdtemp(prefix="gzkit-booking-nc-"))
    handoffs = root / ".gzkit" / "handoffs"
    handoffs.mkdir(parents=True, exist_ok=True)
    for name, stamp in (
        ("20260716T000000Z-older.md", "2026-07-16T00:00:00Z"),
        ("20260812T000000Z-armed.md", "2026-08-12T00:00:00Z"),
    ):
        (handoffs / name).write_text(
            "---\n"
            "mode: CREATE\n"
            "adr_id: ADR-0.0.65\n"
            "branch: main\n"
            f"timestamp: '{stamp}'\n"
            "agent: g0\n"
            "---\n\n## Decisions Made\n\nnc\n",
            encoding="utf-8",
        )
    return root


def _ep_resume_gate_booking_coupling(root: Path) -> int:
    """Assert the EXEMPTION differential: refuse a stale target, permit the armed one.

    Truthy only when BOTH hold. An always-refuse mutation blocks the gate's own
    recovery path; an always-permit mutation is GHI #795 itself — consent
    recorded against a document the operator never read.
    """
    handoffs = root / ".gzkit" / "handoffs"
    refused = not booking_targets_the_armed_handoff(root, handoffs / "20260716T000000Z-older.md")
    permitted = booking_targets_the_armed_handoff(root, handoffs / "20260812T000000Z-armed.md")
    return 1 if (refused and permitted) else 0


def _resume_gate_marker() -> None:
    """Inert carrier for the resume-gate ``@enforces`` registrations."""


def _ensure_resume_gate_claims_registered() -> None:
    """(Re)register the resume-gate enforcement claims (idempotent, reset-safe).

    Mirrors the airlock live-NC registration. MUST stay wired into
    ``_ensure_production_claims_registered`` — a registration authored but
    un-wired there is an ORPHAN whose floor membership is a facade (the §5
    failure class these NCs exist to prevent).
    """
    from gzkit.airlock.enter import _AIRLOCK_CLAIM_IDS  # noqa: PLC0415
    from gzkit.enforcement import (  # noqa: PLC0415
        EXEMPTS_NONE,
        enforces,
        get_enforcement_registry,
        set_known_claims,
    )
    from gzkit.governance.trust_audits._qc_negative_controls import (  # noqa: PLC0415
        _KNOWN_QC_CLAIM_IDS,
    )

    set_known_claims(_KNOWN_QC_CLAIM_IDS | _AIRLOCK_CLAIM_IDS | RESUME_GATE_CLAIM_IDS)
    existing = {r.claim_id for r in get_enforcement_registry()}
    if "handoff-resume-unauthorized-write" not in existing:
        enforces(
            "handoff-resume-unauthorized-write",
            _build_unauthorized_resume_violation,
            _ep_resume_gate_write,
            exempts=RESUME_GATE_COUPLING_CLAIM_ID,
        )(_resume_gate_marker)
    # `handoff-resume-unauthorized-bash` was registered here and is RETIRED
    # (operator ruling 2026-08-14). It asserted that `gz obpi complete` is refused
    # on an unruled handoff — a claim this gate no longer makes, so keeping the
    # control would assert enforcement that does not exist, which is the facade
    # shape the negative-control system exists to refuse. The retained
    # `-write` control covers the clause that survives.
    if RESUME_GATE_COUPLING_CLAIM_ID not in existing:
        enforces(
            RESUME_GATE_COUPLING_CLAIM_ID,
            _build_mis_targeted_booking_violation,
            _ep_resume_gate_booking_coupling,
            exempts=EXEMPTS_NONE,
        )(_resume_gate_marker)
