# Safe mode contract — {{title}}

> Template for a safe-mode (martial law) period. Doctrine: `docs/governance/safe-mode-doctrine.md`.
> The `gz-mx` skill reads this document before entry and refuses when a required section is
> missing. Fill every section; delete this note.

## Authority

The operator's words that declare the crisis and book the pilot, verbatim and dated. Each is
also on the insights file at the time it was given.

## Entry

Entered on {{date}} at the operator's word above. The purpose in one sentence, and the target
shape in one line per band.

## What is suspended, and what is not

Suspended: the operator-only initiation of OBPI work and the brief ceremony, as named here.
Not suspended, in every mode: Gate 5 attestation; the ledger written only through `gz` verbs;
operator PII; the removal of a control; the PRIME DIRECTIVE.

## On the ledger

How the ledger is written during the period (through the verbs that already write it) and
which design questions about events are put to the operator rather than decided here.

## Division of labor

- **The pilot** plans, measures, drafts and rules with the operator; it executes a cut itself
  only when the cut is the measurement's own finding and small enough to read in one sitting.
- **Cheaper sessions** execute the work orders under § Records.
- **The operator** rules every structural question with the facts and at most three options,
  enters and exits through the `gz-mx` skill, and attests every completion.

## Mandate

Numbered. Each item names an outcome, not a task.

## Records

- Every pilot change is one commit with a `Task:` trailer, a failing test observed before the
  change, and `gz arb red --commit <sha>` run after it with its verdict recorded; an `undriven`
  verdict is repaired in the same commit before it counts.
- Every operator ruling is an insight record when given and an `[operator-ruled]` handoff entry.
- Every session ends with a handoff citing this file and listing the pilot commits since the last.
- § Passage log is appended per act with bytes or counts before and after.

## Exit — the pilotage chart

### The regime

| Phase | Regime | Produces | Done when |
|---|---|---|---|
| Harbor | safe mode | | |
| Drydock | safe mode | | the first release through a release plan; the exit numbers met |
| Sea trial | safe mode | one work package on a fresh install of the release | the trial recorded below |
| Handback | ratification | the amendment | the operator's word; the exit through the hard gate |
| Voyage | civil rule | | |

### Legs

| Leg | What it means | Witness | Reading | Owner |
|---|---|---|---|---|
| H1 | | | | |

### Drydock exit numbers

| Measure | Today | Exit |
|---|---|---|
| | | |

### Executive decisions

Numbered, dated, with the reason; the operator may overrule any by a word.

## Work orders

In order. Each is a GHI with a closure contract, executed under § Records, closed through
`ghi-close`.

## Passage log

| Date | Act | Before | After | Commit | Witness |
|---|---|---|---|---|---|
