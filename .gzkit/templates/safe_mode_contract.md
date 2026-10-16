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
- **Cheaper sessions** execute the work packages under § Records.
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
| Drydock | safe mode | | the first release through a Release Package; the exit numbers met |
| Sea trial | safe mode | one work package on a fresh install of the release | the trial recorded below |
| Handback | ratification | the amendment | the operator's word; the exit through the hard gate |
| Voyage | civil rule | | |

### Harbor legs (the standard set; keep the letters, mark a leg not applicable with its reason)

| Leg | What it means | Witness | Reading | Owner |
|---|---|---|---|---|
| H1 | Session start bounded | | | |
| H2 | The root contract within budget | `gz validate --instructions-files-budget` | | |
| H3 | Pipeline invoke bounded | `gz skill audit`; bytes at invoke | | |
| H4 | Per-turn rules and skill descriptions cut | sizes before and after | | |
| H5 | The catalog exists and is used | | | |
| H6 | The TASK is the increment on one package | | | |
| H7 | Every control names its contract | | | |
| H8 | The toggle is on the record | `.gzkit/mx.json` with `mode: safe` | | |
| H9 | Executed briefs attested | `gz obpi status` | | |

### Drydock repairs (the standard set)

| Repair | What is rebuilt | Witness |
|---|---|---|
| D1 | The ladder: Release Package, work package, TASK | one release through a Release Package |
| D2 | The catalog as the product's truth | |
| D3 | GHIs and MX visits classified by contract | |
| D4 | The control plane subtracted | |
| D5 | The airlock derives the slice from the contract | |
| D6 | Eval checks design against code | |

### Drydock exit numbers (the standing measures; set the values)

| Measure | Today | Exit |
|---|---|---|
| Per-turn load: the root contract | | |
| Per-turn load: skill descriptions, all skills | | |
| Per-turn load: rules, total and largest | | |
| Controls with no named contract | | 0 |
| Operator attestations | | one per release, plus the sea trial |

### The sea trial

The Release Package it rides on; the substrate (a fresh project on the released wheel); the
package; the session; the two artifacts the operator attests from; the record below.

### Executive decisions

Numbered, dated, with the reason; the operator may overrule any by a word.

## Work packages

In order. Each is a GHI with a closure contract, executed under § Records, closed through
`ghi-close`.

## Passage log

| Date | Act | Before | After | Commit | Witness |
|---|---|---|---|---|---|
