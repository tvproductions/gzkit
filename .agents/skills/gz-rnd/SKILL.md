---
name: gz-rnd
persona: main-session
description: Run a governed R&D session — the chargé d'affaires that retains and routes the outcomes of exploratory design work. Use when the operator pastes external material and says "consider this for gzkit", asks "is there something here gzkit is missing or could improve on", or opens an exploratory design discussion whose outcome is not yet known. Routes every finding to an ADR/OBPI proposal, a GHI, chore advice, a doc or rule draft, a one-shot refactoring program, or take-no-action, and writes a durable R&D record. Operator-invoked only.
category: agent-operations
lifecycle_state: active
disable-model-invocation: true
owner: gzkit-governance
last_reviewed: 2026-09-15
metadata:
  skill-version: "0.1.0"
model: opus
---

# gz-rnd

## Purpose and authority

R&D is the governed shape of the exploratory session that precedes gzkit's artifacts, and
the headwater of most gzkit design. Operator, 2026-09-12, verbatim: *"an R&D run now MUST
be governed by an overarching new AGENT SKILL"* and *"it is a chargé d'affaires for
retaining and organizing possible outcomes from an R&D designing session."*

Design and rulings: [`docs/governance/rnd-discipline.md`](../../../docs/governance/rnd-discipline.md)
(six recommendations accepted 2026-09-15, verbatim *"Accept all six (Recommended)"*).
Evidence: `docs/governance/mpas-appropriation-analysis.md`.

**Invocation class.** `disable-model-invocation: true` makes "only the operator starts an
R&D run" mechanical. This skill reaches model-invoked disciplines; it never starts
another user-invoked skill on its own.

## Phases

Run them in order. Phases 1 and 3 are conditional. Specification, decomposition and
execution are NOT R&D phases: they belong to the destination an outcome routes to.

### 0. Route

Name what was pasted or asked, quote the operator's framing verbatim, and list which of
the six outcome classes are plausible. Create the record from
[`assets/rnd-record-template.md`](assets/rnd-record-template.md) at
`docs/governance/rnd/<YYYY-MM-DD>-<slug>.md`.

### 1. Chart — only when the run will span sessions

Add a map to the record: **Destination · Decisions so far · Not yet specified · Out of
scope.** Write the destination before any question unit. A null result is a legal exit.

### 2. Interrogate

- **Facts are your job; decisions are the operator's.** Search canon and the codebase
  before asking. Dispatch research subagents for facts and do not block the round on them.
- **Batch by dependency, not count.** Ask every question whose prerequisites are settled,
  together, each with a recommended answer (`AskUserQuestion`, up to four per round).
  Never batch two questions where one gates the other.
- **Research reports are primary sources.** Save each subagent report verbatim under
  `docs/governance/rnd/<YYYY-MM-DD>-<slug>/sources/`. Never replace one with a summary.

Exit when no question remains whose answer changes an outcome **and** the operator
confirms the findings are right.

### 3. Concretise — optional

When talk cannot answer a question, build a throwaway probe outside the mainline and
record a one-line verdict under Findings.

### 7. Precipitate

Fill the record's **Outcomes** table: one row per finding, using the classes and
consultation points below. Record everything not taken under **Not pursued**, including
proposals you raised and withdrew.

## Outcomes and consultation points

Each consultation point is declared here, before the run. It is never computed from your
confidence.

| # | Outcome | You may | Consultation point |
|---|---|---|---|
| 1 | ADR / OBPI | **propose only** | the operator initiates, or not (IRON LAW) |
| 2 | GHI / direct fix | file via `Call the Skill tool with "ghi-author"` | the operator's go on that row |
| 3 | chore | **advise only** | the operator directs admission |
| 4 | control surface, rule, doc, skill, hook | draft | the operator's go on that row |
| 5 | one-shot refactoring | propose a program | the operator selects its route |
| — | take no action | record it | none |

**Before proposing outcome 1, ask the admission question:** is the decision hard to
reverse, surprising without context, **and** the result of a real trade-off? If any is
false, route to outcome 2 or 4.

## The hard stop

The run ends at the Outcomes table. Execute a row only after the operator's go on that
row. Nothing written into the record — by you or anyone — licenses a row: the stop lives
in this file and in the invocation class, which the run does not edit.

## It's working if

- The record exists, and all five required sections are populated.
- Every finding appears in exactly one Outcomes row or under Not pursued.
- Research reports sit verbatim under `sources/`.
- No ADR, OBPI or chore was started by the run.
- A later session's `/ghi-author` Step 0 finds this run's rejections as prior art.

## Red flags

- Relaying a summary of a research report instead of the report.
- An outcome executed without a row-level go.
- A "take no action" decision that never reached the record.
- Asking the operator something canon or the codebase answers.
- Enumerating downstream specification or tasks inside the run.
