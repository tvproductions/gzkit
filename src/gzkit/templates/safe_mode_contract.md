# Safe mode contract — {{title}}

> Template for a safe-mode period. Doctrine: `docs/governance/safe-mode-doctrine.md`.
> The `gz-mx` skill reads this document before entry and refuses when a required section is
> missing. Fill every section; delete this note.

## Authority

The operator's words that declare the need and book the pilot, verbatim and dated. Each is also
on the insights file at the time it was given.

## Purpose

What this flip is for, in one paragraph: what structure is re-rigged, reconfigured, retooled or
restructured, and what it does not do. Safe mode designs and lands structure; it does not populate
it, and it is turned off when the re-rigging is done.

## The general arrangement

The drawing of the target structure, saved beside this contract and ratified by the operator, with
one line per band and the rails. Every repair order below names the band it serves.

## What is suspended, and what is not

Suspended while the marker is open: every guard outside the four below, lowered to advisory; the
operator-only initiation clause, for repair orders; the brief ceremony. Not suspended, in every
mode: Gate 5 attestation; the ledger written only through `gz` verbs; operator PII; the PRIME
DIRECTIVE; no control is removed.

## Division of labor

- **The session** appraises, plans, measures, drafts and rules with the operator; it executes a
  repair order itself only when it is the measurement's own finding and small enough to read in
  one sitting.
- **Cheaper sessions** execute the deterministic repair orders under § Records.
- **The operator** rules every structural question with the facts and at most three options,
  enters and exits through the `gz-mx` skill, and attests.

## Mandate

Numbered. Each item names a structural outcome, not a task, and serves a band of the general
arrangement.

## Records

- This contract changes only by its own amendment, never through a repair order: a repair order
  that needs a contract change stops for a contract amendment first. Each committed edit is booked
  `mx_contract_amended` against the hash pinned at entry (decision *B1*, after DFARS
  217.7103-6(b): *"A master agreement shall be changed only by modifying the master agreement
  itself. It shall not be changed through a job order."*).
- Every change is one commit with a `Task:` trailer naming its repair order. No long check runs
  per act: the alarms are off in safe mode (`gzkit.mx.alarms`), and what an act leaves broken goes
  on § List of discrepancies. The exit clears every line that blocks return to service before the
  alarms come back on, and the handback transfers the rest.
- Three records, carried by the handback: § Tag-out log, the temporary isolations with their
  removal procedures, empty at return to service; the maintenance record, the permanent work
  under 14 CFR § 43.9(a), whose per-act entries are § Passage log and each order closed by the
  operator's Gate 5; § List of discrepancies, the outstanding work.
- Every operator ruling is an insight record when given and an `[operator-ruled]` handoff entry.
- Every session ends with a handoff citing this file and listing the commits since the last.
- § Passage log is appended per act with bytes or counts before and after.
- The state of every order is read from the work package log, never from this contract (see
  § Repair orders).

## Repair orders

In dependency order (the standard shape; keep the numbers, mark an order not applicable with its
reason, add orders as the appraisal finds them). Each order owns restoring what it disconnects,
reroutes or changes, to the prior or to the new stable state, and closes only when its line items
on § Tag-out log are cleared and its discrepancies that block return to service are cleared.

The table states what each order lands; it is changed only by amendment of this contract. Which
orders are open is the **work package log**: a Layer 3 view assembled from the repair work
packages, their issues and the ledger, never edited, and never blocking a gate (decision *B11*;
`docs/governance/safe-mode-doctrine.md` § The instruments, item 3). Read it there, not here.

| Order | Serves | What it lands | Witness | Owner |
|---|---|---|---|---|
| RO-0 | the drydock itself | this contract and the drawing ratified; the suspension in force; prior drift disposed | | |
| RO-1 | control plane | the bleeding stopped: loaded surfaces cut to budget first, measured for effect | | |
| RO-2 | identity | the identity seam by alias and resolver, renaming nothing | | |
| RO-3 | catalog | the requirements store and feature-area registry as empty structure | | |
| RO-4 | version | the release detached and keyed to one release shape | | |
| RO-5 | labor, maintenance | the work-package, task-card and repair-order structure | | |
| RO-6 | every band | contradicted canon retired with retention maps | | |
| RO-7 | control plane | the rest of the cut, staged, with an effectiveness report per stage | | |
| RO-8 | the in-flight work | disposition of what was open, and the handback | | |

## Tag-out log

One line item per isolation an order hangs: a Danger tag (an alarm off and locked) or a Caution
tag (a tripwire that records). Each carries its removal procedure and is cleared, restored or
reconnected, by the person assigned before return to service.

| Line item | Order | Tag | What is isolated | Removal procedure | Cleared |
|---|---|---|---|---|---|

## List of discrepancies

One line per discrepancy, graded *blocks return to service* or *due by a named event*, cleared
with its evidence. A line takes the fuller record (root cause and corrective action) only when it
blocks return to service or recurs, by the threshold in `data/recurrence_threshold.json` checked
by `gz insights recurrence`.

| Discrepancy | Order | Grade | Root cause and corrective action | Cleared, with evidence |
|---|---|---|---|---|

## Exit — seaworthiness

Numbered structural conditions, each read from its witness; the handback amendment the operator
ratifies (every commit kept or reverted, the passage log carried, the suspended rules restored).
The sea trial belongs to civil rule's first voyage, not to the exit.

## Rulings

The operator's words during the period, verbatim and dated, each also an insight record.

## Passage log

| Date | Act | Before | After | Commit | Witness |
|---|---|---|---|---|---|
