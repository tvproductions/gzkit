"""Handoff-resume support: selection and booking coupling, with no enforcement arm.

This module once carried an Operator Authorization Gate that refused tool calls
while a session had resumed a handoff the operator had not ruled on. **That gate
is fully retired** (operator ruling 2026-08-15, verbatim: *"the handoff should be
an advisor, not a gate-keeping nanny"*). The `Bash` arm went first on 2026-08-14
(`bc9b72f6`); the surviving `Write|Edit|NotebookEdit` arm goes here, and with it
the PreToolUse hook, its registration, and its negative control.

**Why the whole arm, not a narrower one.** The gate's own paper trail closed the
question. GHI #574, which authorized it, quoted the remedy it was meant to apply:
*"place the human at a mechanical gate, **not at every keystroke**."* It shipped
as a PreToolUse hook on every mutating call. Operator canon recorded 2026-08-06 at
`invariant` tier assigns entry/exit authorization to TRANSIT — the airlock's
subject (ADR-0.33.0) — while a handoff is a *"synthetic memory refresh, from agent
session to agent session, for context management"*. A memory artifact has no
natural blast radius, so "what should reading a reminder prevent?" had no
principled answer; the invented answer was maximal, then whittled by 44 read
exceptions across 13 corrections in 29 days.

**What the measurement said.** Refusal recording landed 2026-08-14 (`2a326f04`),
so the arm has exactly one day of evidence: **9 lifts, 1 block**. The single
block was a `Write` on 2026-08-15T00:08. The arm's protective value was never
measurable; its friction was.

**Retired ahead of its planned successor, deliberately and on the record.**
`REQ-0.37.0-05-02` says the arm retires *with* the session-entry door and that
*"a retirement that precedes the door is a regression, not an increment"*.
ADR-0.37.0 is `Pending` at 0/6 with no implementation, so that REQ's own premise
(*"Given the session-entry door is live"*) is unmet and unscheduled. The operator
ruled the retirement ahead of the door; the REQ and the campaign's Movement B
item 3 were amended in the same commit rather than silently contradicted.

**What still binds.** Gate 5 human attestation, the pre-commit hook (ruff, ty,
unittest, xenon), and the pre-push `gz check` are untouched. Only the
unruled-handoff precondition is gone.

**What survives here.** :func:`newest_handoff` (the selection projection, three
independent production consumers) and :func:`booking_targets_the_armed_handoff`
(the `gz handoff decide` coupling predicate, GHI #795). The advisory half — the
SessionStart handoff advisement and `gz handoff decide`'s Layer-2 record of the
operator's verbatim ruling — is unchanged and is now the whole mechanism.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from gzkit.handoff_validation import HandoffValidationError, parse_frontmatter

__all__ = [
    "RESUME_GATE_CLAIM_IDS",
    "booking_targets_the_armed_handoff",
    "newest_handoff",
]


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


# ---------------------------------------------------------------------------
# Live negative control — the floor's teeth for what remains (ADR-0.0.74 §5)
#
# ONE CLAIM, because one clause survives. The two enforcement claims that lived
# here are both RETIRED with the arms they witnessed:
# `handoff-resume-unauthorized-bash` on 2026-08-14, and
# `handoff-resume-unauthorized-write` on 2026-08-15. A control asserting
# enforcement that no longer happens reports green while blind, which is the
# facade shape §5 exists to refuse — you cannot write a negative control for a
# surface you did not hook, and the converse binds just as hard: you must not
# keep one for a surface you unhooked.
#
# What survives is not an enforcement claim at all. The booking-coupling control
# witnesses `gz handoff decide`'s own correctness — that a ruling is recorded
# against the document the operator actually read — which is a property of the
# ADVISORY half and outlives the gate entirely.
# ---------------------------------------------------------------------------

#: The coupling claim (GHI #797), now the only member. It proves a booking
#: names the document the advisement surfaced. The distinction was never
#: academic — the two retired rule claims were registered, enrolled, and passing
#: on every `gz check` for the entire life of GHI #795's coupling gap, because
#: neither ever asked WHICH document a ruling named.
RESUME_GATE_COUPLING_CLAIM_ID = "handoff-resume-booking-coupling"

#: `handoff-resume-unauthorized-bash` (retired 2026-08-14) and
#: `handoff-resume-unauthorized-write` (retired 2026-08-15, operator ruling
#: *"the handoff should be an advisor, not a gate-keeping nanny"*) were the
#: other members. Both asserted that an unruled handoff refuses a mutation —
#: a claim this module no longer makes on any surface.
RESUME_GATE_CLAIM_IDS: frozenset[str] = frozenset({RESUME_GATE_COUPLING_CLAIM_ID})


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
    # `handoff-resume-unauthorized-bash` (2026-08-14) and
    # `handoff-resume-unauthorized-write` (2026-08-15) were both registered here
    # and are both RETIRED with their arms. Each asserted that an unruled handoff
    # refuses a mutation; this module no longer refuses anything, so keeping
    # either would assert enforcement that does not exist — the facade shape the
    # negative-control system exists to refuse. No enforcement claim survives,
    # because no enforcement survives.
    if RESUME_GATE_COUPLING_CLAIM_ID not in existing:
        enforces(
            RESUME_GATE_COUPLING_CLAIM_ID,
            _build_mis_targeted_booking_violation,
            _ep_resume_gate_booking_coupling,
            exempts=EXEMPTS_NONE,
        )(_resume_gate_marker)
