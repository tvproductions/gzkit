---
id: ADR-pool.primary-source-corroboration
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.primary-source-corroboration: Primary Source Corroboration

## Status

Pool

## Intent

**A summary without its primary source is an assertion.** The operator names this
**the Memento problem** — the artifact remembers that a conclusion was reached and
nothing about what it was reached from.

It surfaced on three separate surfaces inside a single session (2026-08-07), which
is why it is a doctrine and not a defect:

| Surface | The summary | The missing primary source |
|---|---|---|
| Step 4b | An adversarial verdict recorded as `refuted`/`confirmed` | The ARB receipt proving a critic actually ran (GHI #765) |
| Handoff | An authored account of what a session decided | The transcript the account was drawn from |
| ADR | `ADR-pool.convergence-moment-cross-family-critic` as first drafted | The three design transcripts — the ADR was built from handoffs *about* them |

The third case is the sharpest, because the operator diagnosed it in flight and
the diagnosis is on record in that ADR: *"multiple audio tape recordings of audio
tape recordings where the quality is dissipating rapidly."* Recovering that design
required going back to the transcripts, and one recovered artifact (the operator's
`AskUserQuestion` exhibit) survived **only** because it was still base64-embedded
in a transcript whose image cache had already been cleared.

### The lifetime mismatch is the actual defect

A citation is only corroboration for as long as its referent exists. Session
transcripts are deleted on a rolling window; ADRs, campaigns, and doctrine are
permanent. A permanent artifact citing an ephemeral source is **corroborated on the
day it is written and uncorroborated forever after** — with nothing in the artifact
to signal the transition.

### The operator's ruling on transcript-carrying handoffs

Verbatim (spelling preserved):

> I like B with an important caveat. Handoffs need to refer to transcripts - we get
> agent sensemaking in a full handoff PLUS corroboration in the transcript. If we
> emit a 'session_exit_uncovered' we force an a priori handoff by having the agent
> review the transcript to see what was happening. I should get HIGHER QUALITY
> results when I call for a handoff that the ounter-checks the transcript, but I'll
> get some quality if I see that ledger entry and force the just-initiated agent to
> review prior transcript. even then, campaigns and other longer-running
> memory/guidance docs are better understood. All of this is the 'Memento' problem.

And on the forcing function, verbatim:

> I liked your ledger suggestion, I just want sessionstart to see that legder entry
> and consult the transcripts.

**These two paths are not equivalent and this ADR must not let them be read as
equivalent.** An authored handoff counter-checked against its transcript is the
**higher-quality** path: sensemaking and corroboration happen together, at authoring
time, by the agent that was there. The `session_exit_uncovered` → SessionStart →
agent-reads-transcript path is **the floor**: reconstruction after the fact, by an
agent that was not there. The ledger path buys *some* quality where there would
otherwise be none. It never substitutes for a real handoff.

### Why this is an ADR and not a rule

The operator's challenge, verbatim: *"ok, but why not an adr?"*

The doctrine is ADR-shaped, not rule-shaped. It decides something new, it carries
rejected alternatives, and it requires building. In gzkit, rules are the
**enforcement surface** for an ADR's decision — 15 of 26 rules under `.gzkit/rules/`
reference an ADR id (measured 2026-08-07). A
rule here would come *after* this decision, as its enforcement arm, not instead of
it.

## Decision

**1. A summary artifact must cite the primary source that corroborates it.**

**2. The corroboration window must match the artifact's lifetime — pointers for
short-lived artifacts, archived passages for permanent ones.**

| Artifact | Lifetime | Corroboration |
|---|---|---|
| Handoff | days | `session_id` + transcript reference — the ~30-day window covers it |
| `session_exit_uncovered` | days | transcript reference in the event payload |
| ADR / campaign / doctrine | permanent | archive the passages in-package — a pointer alone dangles |

### The governing design principle: liberal with pointers, conservative with archives

This follows from reversibility, and it is a design rule rather than an observation.
A pointer field is a **two-way door** — additive, nullable, droppable in one commit.
An archived appendix is a **one-way door**: once it is in git history, removing it
costs `git filter-repo` plus a force-push. Therefore add pointers freely wherever a
summary is produced, and archive only where the artifact's permanence makes a
pointer structurally insufficient.

### Three properties every transcript reference must carry

These are not refinements. Each closes a defect that would otherwise ship inert.

**(a) Portable, never a machine-local path.** An absolute path such as
`/Users/jeff/.claude/projects/…` dangles for every reader who is not the operator on
that machine — in a fresh clone, on another machine, for any other agent. The
reference is a `session_id` plus a resolver; the raw filesystem path is never the
reference. The worked instance is in-repo today:
`.gzkit/handoffs/20260807T110928Z-session-exit-bookmark.md:16` and `:39` both cite
`/Users/jeff/.claude/projects/-Users-jeff-Documents-Code-gzkit/cb2b04c0-e5f2-478c-b22e-7638f13a4e3f.jsonl`,
and that handoff is the one resumed to author this ADR.

**(b) A liveness signal.** A pointer with no expiry information *reads as
corroborated when it is dead* — strictly worse than no pointer, because it converts
a known gap into an unknown one. Either the reference carries the source's expiry
estimate, or a validator flags dangling references. One of the two is required.

**(c) Producer-stamped, not authored.** Every authored-convention channel in gzkit
has decayed to near-zero: `@advances` has zero registrations; `tasks:` produced 7 of
534 before `gz task start` began stamping it; the commit trailer decayed to ~15%
authored. The measurement for this surface is the same shape — **20 of 277 authored
handoffs (7.2%) mention a transcript at all, every one of them as unstructured
prose.** The transcript reference is therefore stamped by the writer at authoring
time. `.gzkit/rules/task-discovery.md` § 0.6.0/0.7.0 is the precedent: the identical
decay was diagnosed there and fixed the same way.

### Archiving carries a mandatory scrub-before-commit obligation

Archived passages are raw operator prose, and the standing operator-PII prohibition
is binding on appendices exactly as it is on commits, trailers, and attestation text:
*"never include the operator's personal email in any repo-bound artifact… A leak
needs a filter-repo rewrite + force-push to recover"* (2026-04-19 incident). The
scrub happens **before** the appendix is committed, and it is the archiving agent's
obligation under this doctrine. This is handled at doctrine level deliberately — a
mechanical pre-commit scrub gate was offered and **declined**.

Note the interaction with the one-way door above: the PII obligation and the
irreversibility of an archive are the same fact seen twice. That is why the doctrine
is conservative about archives rather than merely careful.

### What this requires building

Named here, not decomposed — pool ADRs carry no OBPIs.

1. **A structured, portable transcript reference on `HandoffFrontmatter`** — added
   as a **declared field**, never by relaxing the model guard.
   `src/gzkit/handoff_validation.py:128-131` keeps `extra="forbid"` deliberately,
   with every real field declared as an explicit superset under OBPI-0.0.72-02, and
   the comment states *"Dropping the guard is forbidden."*

2. **The `session_exit_uncovered` ledger event**, carrying `session_id` and a
   portable transcript reference. It closes a live asymmetry:
   `src/gzkit/ledger_events.py:1050` defines `session_exit_bookmark_skipped_event`
   with **no corresponding `..._written_event`** — the exit beat books its
   non-actions and not its actions, so the bookmark files on disk have zero ledger
   counterparts.

3. **Generalizing the ADR-appendix pattern.** Precedent already exists in-tree:
   `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/appendices/`
   carries 29 operator turns, two adversary verdicts, and the recovered operator
   exhibit. A general requirement falls out of that package and must be carried
   forward: **a formatter that rewrites a primary source destroys the one property
   it must have.** `.pre-commit-config.yaml:87,89` now excludes
   `docs/design/adr/.*/appendices/` from `end-of-file-fixer` and
   `trailing-whitespace` for exactly this reason.

## Alternatives Considered

1. **Pointer-only — every artifact cites a path, nothing is ever archived.**
   Rejected. It is correct for artifacts that live days and wrong for artifacts that
   live forever: the permanent artifact outlives its source, and a pointer alone
   dangles. This alternative is not discarded so much as **narrowed** — it is the
   adopted answer for the short-lifetime rows of the table.

2. **Archive-everything — every artifact carries its passages in-package.**
   Rejected on two independent grounds. The archive half is a **one-way door**
   (removal costs `git filter-repo` + force-push), and the storage and
   passage-selection cost is unjustified for artifacts whose lifetime is days. The
   asymmetry between (1) and (2) is the whole content of the second decision.

3. **Extend `cleanupPeriodDays` — widen the transcript retention window.**
   On its face the cheapest fix available, which is why it must be rejected
   explicitly rather than passed over: **retention config is machine-local and does
   not travel with the repo.** Extending it helps one operator on one machine and
   does nothing for a fresh clone, a second machine, or any other agent. It also
   cannot make a window permanent — only longer — so it does not address the
   permanent-artifact row at all.

4. **A rule instead of an ADR.** Withdrawn under the operator's challenge (*"ok, but
   why not an adr?"* — see § Intent). Recorded rather than deleted because the agent
   proposed it and was corrected; the correction is part of the decision record, and
   a later session that reaches for a rule should find the reasoning already spent.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.

### Relationship to GHI #766

GHI #766 remains the tracked home for the **bookmark-retirement half**. This ADR is
the decision home for the **doctrine**. They are coupled, and the coupling runs in
the dangerous direction: the mechanical exit bookmark is currently the only reliable
transcript citer in the system — it is the one artifact that *always* cites one.
**Landing bookmark retirement without the handoff transcript channel is a net loss of
corroboration**, not a cleanup. Order matters; the channel lands first.

### Campaign placement

Pool, uncommitted, drawn later. The operator's standing sequencing discipline,
verbatim: **"only one feature at a time, feature, finish, draw from pool."**
`ADR-0.35.0-canon-entry-corpus-landing` is the in-flight feature (Movement A item 2,
0/10 landed), so this ADR waits in pool and is drawn when that finishes. Placement
past that ordering is undecided — no promotion date, no semver, no kind is proposed
here.

### Risks and open questions

1. **The field ships and goes inert — the most likely failure.** This is exactly
   what happened to `@advances` (zero registrations) and to `tasks:` before it was
   producer-stamped. The producer-stamped ruling in § Decision is the countermeasure,
   and it is countermeasure to *this specific* pre-mortem outcome, not a general
   preference.

2. **Dangling-by-construction absolute paths — the second most likely failure.**
   Already instantiated in the handoff resumed to author this ADR. The portability
   requirement exists because the defect is observed, not anticipated.

3. **Corroboration theater.** An agent cites a transcript path without reading it,
   satisfying the gate while the summary stays uncorroborated. This is
   **metagaming** — pattern 9 in `.gzkit/rules/agent-failure-modes.md` — and it is
   named by that name here so a promoting session recognizes it as a known family
   rather than rediscovering it.

4. **The shakiest condition, and the single biggest risk: *that agents actually read
   the pointer*.** SessionStart can direct a read. Direction is not verification.
   Nothing in the design distinguishes "read and corroborated" from "saw the path".
   **Unresolved**, and recorded as unresolved rather than papered over.

5. **Corroboration is not verifiable — an assumed property that is false.** Nothing
   checks that an archived appendix actually corresponds to the claim it corroborates;
   an unrelated passage passes the check as well as the right one. The doctrine buys
   *presence* of a primary source, not *correspondence*.

6. **A transcript is primary for what was *said*, not for what was *meant*.** It
   carries the operator's words; it does not carry their intent. Reading it as
   settled intent is a second-order version of the same over-trust this ADR exists
   to correct.

7. **The inverted core assumption — the strongest argument against this whole ADR.**
   Maybe summaries are fine and the real defect is **hop count**. The critic design
   degraded across three handoffs — "tape recordings of tape recordings" — and fewer
   hops would have preserved it with **no corroboration machinery at all**. If that
   diagnosis is right, this ADR buys a channel where a sequencing discipline would
   have sufficed. Recorded honestly; a promoting session should answer it rather than
   assume it away.

8. **The ~30-day window is inherited, not real.** `cleanupPeriodDays` is unset, so
   the window is a Claude Code default and is configurable. Measured 2026-08-07: the
   oldest surviving transcript was exactly 30 days. Treat "~30 days" as a
   *currently-observed* value, never as a constant to design against.

9. **`extra="forbid"` on `HandoffFrontmatter` IS real and load-bearing** — the
   counterpart finding to item 8. `src/gzkit/handoff_validation.py:128-131` keeps it
   deliberately; the transcript field is added as a declared field and the guard is
   not relaxed.

10. **The 2am case.** A handoff cites a transcript that no longer exists, and the
    design as it stands gives the operator nothing: no expiry estimate, no
    dangling-reference validator, and an absolute path that cannot be checked from
    another machine. Items (b) and (a) of § Three properties are the response to this
    scenario specifically.

11. **Open question — which ADR owns `HandoffFrontmatter`.** Deliberately left
    unresolved. Standing canon routes a correction under the ADR owning the surface,
    and two candidates have a claim: the handoff record names
    **ADR-0.0.65** (handoff-system-consolidation), while the model's own comment at
    `src/gzkit/handoff_validation.py:128-131` credits **OBPI-0.0.72-02** for the
    explicit-superset design the new field must join. Resolving this is the promoting
    session's call, not this ADR's.

### Scope minimization

The smallest version that delivers value is the **handoff transcript field alone** —
the path the operator ranked higher-quality. `session_exit_uncovered` is explicitly
the floor and can land later. At half the time: ship the field, and leave bookmark
retirement to GHI #766.
