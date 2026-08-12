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

* **The allowlist is OBLIGATION-derived, not example-derived.** What RESUME may
  read while unauthorized is fixed by the § Claim Verification Gate's duty —
  "verify every completion / lock / gate / readiness claim before presenting it" —
  NOT by the § Trust Model's illustrative list of `gz` verbs. Deriving it from the
  examples under-covered the duty twice (see :data:`_PERMITTED_BASH`), most
  recently leaving a resume unable to check the GHI claims its own advised steps
  turned on. Blocking a mandated read makes the skill un-compliable; everything
  that is not a mandated read fails CLOSED.

* **The gate never blocks its own recovery.** `gz handoff decide` is always
  permitted. A rule that forbids the command that lifts it is worse than the hole
  it plugs (operator ruling, 2026-07-16 permission-surface pass).

Coverage limits are declared, not hidden — see :data:`UNWITNESSABLE`.
"""

from __future__ import annotations

import json
import shlex
import tempfile
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.handoff_validation import HandoffValidationError, parse_frontmatter
from gzkit.shell_reading import split_on, strip_uv_run, tokenize_shell

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
#: mutation" clause. `Bash` is included because `gz` ceremony and migration —
#: both named in the contract — run through it; a `Write|Edit`-only gate would
#: enforce one third of the declared clause and call it done.
MUTATING_TOOLS = frozenset({"Write", "Edit", "NotebookEdit", "Bash"})

#: Read-only Bash prefixes permitted while unauthorized. Matched against the
#: command's leading tokens after `uv run` is stripped.
#:
#: Derived from the OBLIGATION, not from a list of examples. Four times now this
#: allowlist has been wrong, and every time the root was the same: it was scoped by
#: enumerating the § Trust Model's example surfaces instead of asking what the
#: § Claim Verification Gate REQUIRES — "verify every completion / lock / gate /
#: readiness claim before presenting it". Enumerate-the-examples under-covers the
#: rule it serves, and — the fourth miss — silently over-grants beside it, because
#: an enumeration records no reason a reader could use to judge either edge.
#:
#: * First miss: only `gz` verbs, on the premise that "Read/Grep/Glob are never
#:   gated, so Bash is not the read path". False in this harness — `Grep`/`Glob`
#:   may be absent, making Bash `grep`/`cat`/`git log` the only instrument.
#: * Second miss: no `gh`, because the § Trust Model table has no row for a
#:   GHI-state claim — while handoffs routinely assert "GHI #N CLOSED" and advise
#:   "rule on GHI #M" as next steps. Those claims had NO verifiable surface
#:   (operator ruling, 2026-07-17: "this is essential").
#: * Third miss: no `git rev-list`, so an "origin/main in sync" / ahead-behind
#:   claim had no counting instrument — `rev-parse` resolves a ref but cannot
#:   count a range. Caught 2026-08-02 when a handoff's OWN Verification Checklist
#:   prescribed `git rev-list --left-right --count origin/main...HEAD` and this
#:   gate refused it.
#:
#: The third fix took the INSTANCE and left the class open — GHI #732 had already
#: named the family ("read-only git plumbing/porcelain verbs absent from an
#: allowlist that advertises 'git reads' generically") and listed `blame`,
#: `shortlog`, `describe`, `merge-base`, `cat-file`, `for-each-ref`. Admitting one
#: verb per discovery is the enumerate-the-examples habit itself, so the whole
#: named family is admitted below under one stated membership predicate:
#:
#:     A git verb belongs here when it is READ-ONLY BY CONSTRUCTION — it has no
#:     write form at all, in any flag combination.
#:
#: That predicate is what makes the set closable. Verbs excluded by it are excluded
#: on purpose: `tag`, `fetch`, `checkout`, `update-ref`, and `hash-object` all read
#: in one form and write in another, so allowlisting the head would license the
#: write. `_MUTATING_FLAGS` guards the flag surface of what IS admitted; it is not
#: a substitute for the predicate.
#:
#: * Fourth miss, and the first that was too WIDE rather than too narrow: the
#:   predicate was stated for the `git` arm only, leaving the plain-shell arm a bare
#:   enumeration — so `find` sat in it, admitted, while `find . -fprint FILE`,
#:   `-fls`, and `-fprintf` WROTE FILES through this gate (observed 2026-08-05).
#:   GHI #732 proposed extending the enumeration by admitting a write-capable verb
#:   whose "write-enabling flags are all in `_MUTATING_FLAGS`", on the premise that
#:   `find`'s grant proved the flag guard was the intended pattern. Probing the real
#:   tools disproved the premise in both directions: `find`'s write primitives are
#:   not flags anyone had enumerated, and `sed` writes from INSIDE its script operand
#:   (`sed -n '1,2w FILE'`, `s///w FILE`) where no flag set can see it. `-i` is not
#:   sed's only write form, only its most famous one.
#:
#: So ONE predicate governs the whole Bash arm, and `find` is removed by it rather
#: than `sed` added under a weaker one. Excluded on purpose, each for a reason that
#: is a flag guard's blind spot: `find` (`-fprint`/`-fls`/`-fprintf` primitives),
#: `sed` (in-script `w`), `awk` (in-program redirect), `sort` (`-o`, which cannot
#: even be guarded — it collides with `find`'s OR operator), `uniq` (positional
#: output operand), `tee` (writes by definition), `env`/`xargs` (execute arbitrary
#: commands). Nothing is lost: `rg --files`, `ls`, and `git ls-files` locate files,
#: and a line RANGE is the ungated `Read` tool's `offset`/`limit`, not `sed -n`.
#: Judge a candidate against the predicate, never against the list.
#:
#: A gate that forbids the verification its own skill mandates cannot be complied
#: with, and an un-compliable gate gets worked around — the failure mode gzkit
#: exists to close. Reads are not execution; the contract forbids MUTATION.
_PERMITTED_BASH: tuple[tuple[str, ...], ...] = (
    # The recovery path — must never be blocked by the gate it lifts. BOTH
    # spellings: `decide` is canonical (GHI #757) and `authorize` is its
    # retained alias, and an allowlist carrying only one of them would let the
    # gate refuse its own recovery. Renaming the recovery verb without adding
    # it here would have been the fifth miss on THIS allowlist — the
    # enumerate-the-examples class GHI #732 is open against.
    ("gz", "handoff", "decide"),
    ("gz", "handoff", "authorize"),
    # § Trust Model: the Layer-2 surfaces RESUME must read to verify claims. The
    # same predicate, said in this arm's terms: a `gz` verb is admitted when the
    # ADMITTED PREFIX has no write form — because matching is on leading tokens, a
    # verb that reads only under a later flag cannot be expressed here at all.
    #
    # That is why `gz gates` is in and `gz closeout` is out, a pair the #743
    # control-surface audit recorded on GHI #732 as an over/under-grant. It is
    # neither. Deprecation (#705, successor `gz closeout`) governs what docs may
    # PRESCRIBE, not what this gate may READ: `gz gates` still runs and still
    # answers a gate-status claim. `gz closeout` is ceremony whose only read is
    # `--dry-run`, four tokens deep — admitting the head would license the write,
    # and its dry-run is an advised STEP requiring authorization, not a claim
    # verification. `gz status` already answers the claim.
    ("gz", "obpi", "status"),
    ("gz", "obpi", "lock", "list"),
    ("gz", "gates"),
    ("gz", "state"),
    ("gz", "status"),
    ("gz", "adr", "status"),
    ("gz", "context"),
    # Reading the handoff corpus itself in order to present it.
    ("gz", "handoff", "list"),
    ("gz", "handoff", "resume"),
    # § Claim Verification Gate: the Layer-2 surface for a GHI / PR / release
    # claim is GitHub, and `gh` is the only instrument that reaches it. READ
    # verbs ONLY — `gh issue create` is independently forbidden by AGENTS.md
    # § Behavior Rules — Always #13 (author GHIs through `/ghi-author`), so
    # admitting it would put this gate in conflict with the contract it serves.
    # `gh api` is deliberately absent: it mutates via `-X POST`.
    ("gh", "issue", "view"),
    ("gh", "issue", "list"),
    ("gh", "issue", "status"),
    ("gh", "pr", "view"),
    ("gh", "pr", "list"),
    ("gh", "pr", "diff"),
    ("gh", "pr", "status"),
    ("gh", "release", "view"),
    ("gh", "release", "list"),
    # Plain shell reads — the § Claim Verification Gate's actual instrument when
    # the harness exposes no Grep/Glob tool. ONE predicate governs this whole
    # arm, git and non-git alike: admitted only when READ-ONLY BY CONSTRUCTION.
    ("git", "status"),
    ("git", "log"),
    ("git", "diff"),
    ("git", "show"),
    ("git", "branch"),
    ("git", "rev-parse"),
    # The ahead/behind counting instrument. `rev-parse` resolves a ref; only
    # `rev-list` counts a range, which is what a "branch in sync" claim asserts.
    ("git", "rev-list"),
    ("git", "ls-files"),
    # The rest of the read-only-by-construction family GHI #732 named. Each
    # answers a distinct verification question a handoff can raise: who last
    # touched this line, what work landed over a span, where HEAD sits relative
    # to a release tag, what the divergence point is, what an object actually
    # contains, and what refs exist.
    ("git", "blame"),
    ("git", "shortlog"),
    ("git", "describe"),
    ("git", "merge-base"),
    ("git", "cat-file"),
    ("git", "for-each-ref"),
    # The non-git half of the same predicate. Each has NO write form: writing
    # with one of these takes a shell redirect, which `_is_compound` already
    # refuses before the head is ever matched.
    ("grep",),
    ("rg",),
    ("ls",),
    ("cat",),
    ("head",),
    ("tail",),
    ("wc",),
    ("jq",),
    ("pwd",),
)

#: Ceremonies that are ALWAYS authorized, ruled handoff or not. Held SEPARATE
#: from `_PERMITTED_BASH` on purpose: a git-sync writes, and filing it under a
#: constant named "read-only" would be a lie the next reader has to unpick.
#:
#: Operator canon, verbatim 2026-07-26: "a git-sync will ALWAYS be authorized -
#: think about it, if we need to sync with remote, your local handoff is almost
#: always likely to have been superseded by something on remote. Challenging me
#: on a handoff for a git-sync is silly." Reaffirmed 2026-08-09 after this gate
#: blocked a `/git-sync` anyway: "handoffs should never, never, never, ever,
#: block git-sync. NEVER."
#:
#: Derived from the OBLIGATION, not enumerated — the correction this module's
#: own allowlist has needed four times. The gate exists so an unruled handoff
#: cannot DRIVE work. A sync does not act on the handoff's advice; it replaces
#: the state the handoff describes, which is the precondition for ruling on it
#: at all. Gating the sync on the handoff is circular, and worst exactly where
#: it bites hardest: the clone most in need of a sync is the one whose handoff
#: is most likely already superseded on the remote. Borne out in the 2026-07-26
#: session, where the 24 pulled commits had already landed all five advised
#: steps of the handoff being gated on.
#:
#: This opens no quality hole. `gz git-sync` runs its commit through the
#: pre-commit hook and its push through the pre-push `gz check` gate, so every
#: gate still fires; what lifts is the handoff-ruling precondition alone.
#: Compound commands stay refused by `_is_compound`, so nothing rides in on a
#: `gz git-sync && ...` prefix.
_ALWAYS_AUTHORIZED_BASH: tuple[tuple[str, ...], ...] = (("gz", "git-sync"),)

#: Flags that turn an otherwise-read-only command into a mutation. DEFENSE IN
#: DEPTH, never the membership test: every verb in `_PERMITTED_BASH` is read-only
#: by construction, so nothing admitted can legally carry one of these and a hit
#: here means the head was matched by something that should not have been. Trusting
#: this guard AS the predicate is what admitted `find` — whose write primitives
#: (`-fprint`, `-fls`, `-fprintf`) were never in this set — for three releases.
#:
#: That premise is also the membership test for THIS set, and it is why `-i` was
#: removed (2026-08-08). `-i` means in-place for `sed` and `perl` — both excluded
#: by the predicate, both refused at the HEAD before any flag is read — while for
#: `grep`, `rg`, and `git log` it means case-insensitive, an ordinary read. So the
#: entry could not reach the verbs it was written for and blocked only the ones it
#: was not: `grep -rn -i "skill" <file>` was refused mid-resume while the same grep
#: without `-i` was permitted. A flag an admitted verb can LEGALLY carry falsifies
#: the premise above and does not belong here. This is the `find` miss mirrored —
#: there the guard was trusted to cover a verb whose writes it could not see, here
#: it fired for a verb that was not present. Both read the flag set as the predicate.
#:
#: Membership test, stated: a flag belongs here only when some verb ADMITTED by
#: `_PERMITTED_BASH` could carry it to perform a write. Judge a candidate against
#: that, never against the write meaning it happens to have for some excluded verb.
_MUTATING_FLAGS: frozenset[str] = frozenset({"--in-place", "-delete", "-exec", "--fix"})

#: Shell control operators that make a command compound. `shlex` with
#: ``punctuation_chars=True`` emits each as its own token, so a metacharacter
#: inside a quoted argument is never mistaken for one (see :func:`_is_compound`).
_SHELL_OPERATOR_CHARS: frozenset[str] = frozenset(";|&<>()")

#: Coverage this gate structurally cannot provide. Stated so a green is never
#: read as total (the Pass D `unwitnessable.md` precedent: a gate that reports a
#: clean run without its coverage limits advertises coverage it does not have).
UNWITNESSABLE: tuple[str, ...] = (
    "MCP tool calls: the harness routes them past the Write|Edit|Bash matchers, "
    "so a connector that writes is unseen by this gate.",
    "Harness-native mutation outside the tool layer (e.g. an IDE edit by the "
    "operator) is not a resuming agent's execution and is deliberately out of scope.",
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


def _tokens(command: str) -> list[str]:
    """Split a Bash command into leading tokens, `uv run` stripped.

    `shlex` failures (unbalanced quotes) yield an empty token list, which matches
    no allowlist entry and therefore fails CLOSED.
    """
    try:
        parts = shlex.split(command)
    except ValueError:
        return []
    return strip_uv_run(parts)


def _is_shell_operator(token: str) -> bool:
    """Return True when a token is a bare control operator (``&&``, ``;``, ``|``, ``>``…)."""
    return bool(token) and set(token) <= _SHELL_OPERATOR_CHARS


def _can_expand(token: str) -> bool:
    """Return True when a token carries command substitution.

    Checked in EVERY quoting form, deliberately. Double quotes do not make
    substitution inert (bash expands ``"$(rm -rf x)"`` and ``"`rm -rf x`"`` just
    as it would bare), and posix-mode tokenization — required by
    :func:`_is_compound` — strips quotes, so the inert single-quoted form is
    indistinguishable from the live double-quoted one by the time we see a token.
    Facing that ambiguity the gate refuses both: a false refusal costs a literal
    ``$(``-in-a-pattern search that no claim verification needs; a false permit
    costs a subshell.
    """
    return "`" in token or "$(" in token


def _is_compound(command: str) -> bool:
    r"""Return True when the command chains, redirects, or substitutes.

    Quote-aware by construction. The first implementation ran a regex over the RAW
    string, which cannot tell a pipe from the ``|`` inside ``grep "A\\|B"`` — so it
    refused alternation patterns and `jq` filters, the most ordinary instruments
    the § Claim Verification Gate has (dogfooded 2026-07-17: three of the first
    four verification calls of a resume died on it). `shlex` knows quoting and,
    with ``punctuation_chars``, emits real operators as standalone tokens.

    Two lexer facts are load-bearing here and were established by probing the real
    lexer, not by reasoning about it:

    * ``posix=True`` is REQUIRED. In non-posix mode a quote that opens mid-token
      raises ``No closing quotation`` — which would fail closed on
      ``git log --since='60 days ago' --grep='^fix('``, the precedent-check command
      AGENTS.md § Defect-fix routing *mandates*, leaving the agent stuck between
      two binding rules.
    * Tokenization ALONE is not sufficient. Backticks are not punctuation to
      `shlex`, so ``gz state `rm -rf x``` yields an allowlisted head and NO
      operator token — it would have ridden straight in. :func:`_can_expand`
      covers what the split cannot see.

    The lexer configuration itself lives in :func:`gzkit.shell_reading.tokenize_shell`
    — the verifier-exit-status gate (GHI #589) reads the same command strings with
    the same two facts, and a second copy of them is how the two gates would come
    to disagree about what a pipe is.
    """
    tokens = tokenize_shell(command)
    if tokens is None:
        return True  # unbalanced quotes → unparseable → fail closed
    return any(_is_shell_operator(token) or _can_expand(token) for token in tokens)


def _bash_is_read_only(command: str) -> bool:
    """Return True only when the command is an allowlisted read-only invocation.

    Fail-closed by construction: an unrecognized command is NOT read-only. A
    compound command (``&&``, ``;``, ``|``, redirection, substitution) is never
    read-only regardless of its head — ``gz state && rm -rf x`` must not ride in
    on its prefix.
    """
    if _is_compound(command):
        return False
    tokens = _tokens(command)
    if not any(tuple(tokens[: len(allowed)]) == allowed for allowed in _PERMITTED_BASH):
        return False
    # An allowlisted head does not license a write-capable flag: `grep -r x . --fix`,
    # `find . -delete`, `sed -i` are mutations wearing a read's name.
    return not any(token in _MUTATING_FLAGS for token in tokens)


def _bash_is_always_authorized(command: str) -> bool:
    """Return True for a ceremony the operator ruled is never gated on a handoff.

    Compound commands are refused here exactly as in :func:`_bash_is_read_only`:
    the standing ruling covers the sync ceremony, not anything chained onto it.
    """
    if _is_compound(command):
        return False
    tokens = _tokens(command)
    return any(tuple(tokens[: len(allowed)]) == allowed for allowed in _ALWAYS_AUTHORIZED_BASH)


def _admissible_segments(command: str) -> list[str]:
    """Return the parts of a compound command each predicate would admit alone.

    Derived by re-running the REAL predicates on each segment, never by re-reading
    the allowlists: a second copy of the membership test is how this prose would
    come to promise an admission the gate then refuses. Segments carry no operator
    by construction, so :func:`_is_compound` is inert inside each call.
    """
    tokens = tokenize_shell(command)
    if tokens is None:
        return []
    operators = frozenset(token for token in tokens if _is_shell_operator(token))
    segments = (shlex.join(part) for part in split_on(tokens, operators) if part)
    return [
        segment
        for segment in segments
        if _bash_is_read_only(segment) or _bash_is_always_authorized(segment)
    ]


def _shape_refusal_note(command: str) -> str:
    """Name a SHAPE refusal when the parts were each admissible on their own.

    A compound command is refused before any verb is read (:func:`_is_compound`),
    so a caller who batched admitted reads onto an admitted ceremony sees a block
    whose every stated reason is about AUTHORIZATION, and concludes the ceremony
    itself is gated. Dogfooded 2026-08-12: a session opened with
    ``git status --short && uv run gz git-sync``, read the refusal as the
    already-fixed git-sync block (:data:`_ALWAYS_AUTHORIZED_BASH`) recurring, and
    asked the operator to re-fix a defect that had landed three days earlier.

    Emitted ONLY when some segment is admissible. With none, shape is not what
    made the command surprising and the ordinary prose is already correct —
    claiming "refused for its shape, not its verbs" over a chained ``rm -rf``
    would be false.
    """
    if not command or not _is_compound(command):
        return ""
    admissible = _admissible_segments(command)
    if not admissible:
        return ""
    listed = "\n".join(f"    {segment}" for segment in admissible)
    return (
        "WHAT YOU RAN was refused for its SHAPE, not its verbs — it chains, "
        "redirects, or substitutes, and a compound command is refused before any "
        "verb is read so nothing rides in on an allowlisted prefix. Reissue each "
        "part as its own bare call. These parts are permitted RIGHT NOW, with no "
        "ruling and exactly as written:\n"
        f"{listed}\n\n"
    )


def _block_prose(
    handoff: Path,
    tool_name: str,
    project_root: Path,
    session_id: str,
    command: str = "",
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
        f"{_shape_refusal_note(command)}"
        "WHY: `gz-session-handoff` SKILL.md § RESUME declares a universal Operator "
        "Authorization Gate — 'Every resume requires explicit operator authorization "
        "before any execution, at every freshness level — Fresh included ... no file "
        "mutation / gz ceremony / migration until the operator rules.' A handoff "
        "ADVISES; it does not authorize. Freshness shortens re-verification; it never "
        "converts an advisory into a license.\n\n"
        "NEXT STEP: present the handoff's advised next steps to the operator and wait "
        "for a ruling. When they rule, book their VERBATIM words (copy this line; the "
        "session id is already filled in):\n"
        f"  uv run gz handoff decide --handoff {rel} \\\n"
        f'    --session-id {session_id} --decision proceed --operator-text "<their exact words>"\n'
        "Only `proceed` lifts this gate. `pause`, `hold`, and `revert` are equally "
        "bookable rulings and leave it armed — an operator who looks and says 'not yet' "
        'should be recorded, not left unbooked. Add `--set-aside "<step>"` for any '
        "advised step the ruling declines.\n\n"
        "Run it BARE — a `cd ...;` prefix makes it a compound command, which this "
        "gate correctly refuses.\n"
        "Reading is permitted while unauthorized (gz state / gz gates / gz obpi status, "
        "gh issue|pr read verbs, and git/grep/cat reads; quoted metacharacters like "
        'grep "A\\|B" are data, not pipes) — the gate blocks execution, never the '
        "verification that precedes it, and never its own recovery.\n"
        "Admitted Bash reads are read-only BY CONSTRUCTION, so a verb with any write "
        "form is refused even in a read shape: `sed` writes in-script (`1,2w FILE`) "
        "and `find` writes via `-fprint`/`-fls`. Use the Read/Grep/Glob tools — never "
        "gated — for a line range or a file search."
    )


def decide(
    project_root: Path,
    *,
    session_id: str,
    tool_name: str,
    tool_input: dict | None = None,
) -> Verdict:
    """Decide whether a tool call is permitted under the Operator Authorization Gate.

    Blocks when ALL hold: the tool can mutate, a resumable handoff exists, this
    session did not AUTHOR that handoff, and no operator authorization is on the
    ledger for this session. Read-only Bash named by the skill's § Trust Model is
    permitted so the mandated Claim Verification Gate can run before the operator
    is asked to rule, and the git-sync ceremony is permitted unconditionally per
    the standing operator ruling on :data:`_ALWAYS_AUTHORIZED_BASH`.
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
    command = str((tool_input or {}).get("command", "")) if tool_name == "Bash" else ""
    if command and (_bash_is_always_authorized(command) or _bash_is_read_only(command)):
        return Verdict(blocked=False)
    return Verdict(
        blocked=True,
        reason=_block_prose(handoff, tool_name, project_root, session_id, command),
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

RESUME_GATE_CLAIM_IDS: frozenset[str] = frozenset(
    {
        "handoff-resume-unauthorized-write",
        "handoff-resume-unauthorized-bash",
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


def _ep_resume_gate_bash(root: Path) -> int:
    """Production entrypoint: the "gz ceremony / migration" clause, over both poles.

    `gz obpi complete` is ceremony, not one of the § Trust Model reads — so it
    must be refused while unauthorized and permitted once the operator rules.
    """
    return _ep_resume_gate_differential(root, "Bash", {"command": "gz obpi complete OBPI-x"})


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
    if "handoff-resume-unauthorized-bash" not in existing:
        enforces(
            "handoff-resume-unauthorized-bash",
            _build_unauthorized_resume_violation,
            _ep_resume_gate_bash,
            exempts=RESUME_GATE_COUPLING_CLAIM_ID,
        )(_resume_gate_marker)
    if RESUME_GATE_COUPLING_CLAIM_ID not in existing:
        enforces(
            RESUME_GATE_COUPLING_CLAIM_ID,
            _build_mis_targeted_booking_violation,
            _ep_resume_gate_booking_coupling,
            exempts=EXEMPTS_NONE,
        )(_resume_gate_marker)
