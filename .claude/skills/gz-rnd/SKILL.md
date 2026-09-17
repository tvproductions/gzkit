---
name: gz-rnd
persona: main-session
description: Run a governed R&D session — diamond 1 of the double diamond, which defines the problem and names which fan-out artifacts are warranted. Use when the operator pastes external material and says "consider this for gzkit", asks "is there something here gzkit is missing or could improve on", or opens an exploratory design discussion whose outcome is not yet known. Ends at a six-row disposition map and operator sign-off; produces no fan-out artifact itself. Operator-invoked only.
category: agent-operations
lifecycle_state: active
disable-model-invocation: true
owner: gzkit-governance
last_reviewed: 2026-09-17
metadata:
  skill-version: "0.2.0"
model: opus
---

# gz-rnd

## Purpose and authority

An R&D run is **diamond 1 of the double diamond — Discover and Define**. It ends with the
problem defined and a plan naming which fan-out artifacts are warranted, closed by operator
sign-off: kill or fund. **Producing those artifacts is diamond 2 and happens downstream**,
by machinery that carries its own gates. This run never enters it.

R&D is the headwater of most gzkit design. Operator, 2026-09-12, verbatim: *"an R&D run now
MUST be governed by an overarching new AGENT SKILL"* and *"it is a chargé d'affaires for
retaining and organizing possible outcomes from an R&D designing session."*

Doctrine and the full ruling history:
[`docs/governance/rnd-discipline.md`](../../../docs/governance/rnd-discipline.md).
Evidence: `docs/governance/mpas-appropriation-analysis.md`.

**Invocation class.** `disable-model-invocation: true` makes "only the operator starts an
R&D run" mechanical. This skill reaches model-invoked disciplines; it never starts another
user-invoked skill on its own.

## Open the record first

Create `docs/rnd/<slug>.md` from
[`assets/rnd-record-template.md`](assets/rnd-record-template.md) **before the first
question**, and write into it throughout. Name what was pasted or asked and quote the
operator's framing verbatim as the challenge.

**The record accretes entries as they resolve. It is never composed at the end.** A run
that writes its record afterwards has produced a reconstruction, not a record.

## The two entry kinds

Only two. Append each at the moment it resolves.

| Kind | Carries |
|---|---|
| `source` | a primary source — **cited, never summarized**, with its verbatim quotation and when it was read |
| `decision` | something crystallized in session, the reasoning behind it, and the operator's verbatim words where they ruled it |

A `decision` may carry **`commissions:`** naming the disposition it warrants. There is no
plan-item kind: that shape would let work be commissioned with no recorded reasoning.

**Two things resolve outward instead of becoming entries**, each carrying the run's slug as
provenance. The record never holds a copy.

- a **term** → append to `GLOSSARY.md` at the repo root
- an **insight** → `Call the Skill tool with "gz-insights-remember"`

## The MPAS surfaces you may reach for

Three disciplines are appropriated, each with a departure that gzkit canon forces. **Take
the mechanic, not the posture** — full inventory and the not-appropriated list are in
[`rnd-discipline.md`](../../../docs/governance/rnd-discipline.md) § The MPAS surfaces, named.

| Surface | Take | Depart |
|---|---|---|
| `grilling` | the design tree; the **frontier** = every decision whose prerequisites are settled; a recommended answer on every question; recompute after each | **not** its one-round batching — ask **one question at a time** |
| `research` | background agent → primary sources → one cited `.md` | land it **verbatim** under `docs/rnd/<slug>/sources/` |
| `prototype` | the throwaway probe, closing on a **one-line verdict** | **no branch** — gzkit forbids them; build outside the mainline and discard |
| `domain-modeling` *(technique only)* | its glossary behaviours and *"capture them as they happen"*; the `_Avoid_` convention | **never its inline ADR emission** — disposition 1 is proposed, never initiated |

`grill-with-docs` is the shape of the whole run: it emits inline as decisions land, which is
the record accreting and the disposition map kept live. `grill-me` is stateless and is not
the model here.

## Interrogate

- **Facts are your job; decisions are the operator's.** Search canon and the codebase
  before asking. Dispatch research subagents for facts and do not block a round on them.
- **Ask one question at a time** (operator, verbatim: *"ask me the questions one at a
  time"*), each with a recommended answer and its tradeoffs.
- **Never ask what canon already answers** (AGENTS.md § Operator Economy #7). Search canon
  first; where canon rules, act and name the rule that governed.
- **Research reports are primary sources.** Save each verbatim under
  `docs/rnd/<slug>/sources/`. Never replace one with a summary.
- **When talk cannot answer a question**, build a throwaway probe outside the mainline and
  record a one-line verdict as a `decision` entry citing it.

## The disposition map

Maintain it live, as decisions land — not at the close. All six rows are always present; an
absent row is an unfinished run.

| # | Disposition | You may | Consultation point |
|---|---|---|---|
| 1 | ADR / OBPI | **propose only** | the operator initiates, or not (IRON LAW) |
| 2 | GHI / direct fix | file via `Call the Skill tool with "ghi-author"` | the operator's go on that row |
| 3 | chore | **advise only** | the operator directs admission |
| 4 | control surface, rule, doc, skill, hook | draft | the operator's go on that row |
| 5 | one-shot refactoring | propose a program | the operator selects its route |
| 6 | no action | record it, with the reason | none |

**State is `commissioned` or `not pursued`. There is no third state.** Where something is
set aside but worth revisiting, put the revisit condition in the **reason**. If it deserves
more than a sentence, route it to a pool ADR or a GHI — surfaces that have lifecycles.

**Before proposing disposition 1, ask the admission question:** is the decision hard to
reverse, surprising without context, **and** the result of a real trade-off? If any is
false, route to disposition 2 or 4.

## Closing diamond 1

Two conditions, and neither substitutes for the other.

**Mechanical — all three:**

1. the frontier is empty;
2. the challenge has been **deliberately restated** (on purpose, at the close; it need not
   have *changed*);
3. every one of the six dispositions carries a decision.

**Human — sign-off: kill or fund.** It is a **beat, not a boundary**: it fires in whichever
session meets the mechanical condition. A run that outgrows one session is carried by the
handoff system, which already owns that job.

A run **killed at sign-off ends there.** Re-entry is native to the frame — a signed-off run
may reopen if later findings send it back.

## The hard stop

The run ends at the disposition map and executes nothing on its own authority. Execute a row
only after the operator's go **on that row**. Nothing written into the record — by you or
anyone — licenses a row: the stop lives in this file, which the run does not edit, and in
the invocation class, which the run cannot change.

## It's working if

- The record was open before the first question and grew as decisions landed.
- Every source entry quotes its source verbatim; no summary stands in for a report.
- Terms went to `GLOSSARY.md` and insights through `gz insights remember`, not into the record.
- All six disposition rows carry a decision, each `commissioned` or `not pursued`.
- The challenge was restated at the close on purpose.
- No ADR, OBPI or chore was started by the run.
- A later session's `ghi-author` Step 0 finds this run's `not pursued` rows as prior art.

## Red flags

- Writing or "tidying" the record at the end of the run.
- Relaying a summary of a research report instead of the report.
- Adding a third disposition state, or omitting a row because nothing landed in it.
- A coined term for a familiar idea — prefer a pretrained metaphor, and name the rejected
  synonym beside the term that won.
- Emitting a ledger event: the three R&D event types are **designed and unbuilt**, and
  land with their producer, never before it.
- An outcome executed without a row-level go.
- Asking the operator something canon or the codebase answers.
- Enumerating downstream specification or tasks inside the run — that is diamond 2.
