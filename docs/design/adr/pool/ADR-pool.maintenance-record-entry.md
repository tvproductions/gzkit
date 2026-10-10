---
id: ADR-pool.maintenance-record-entry
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.maintenance-record-entry: Maintenance record entry: one ledger event per chore run

## Status

Pool

## Intent

**Origin.** Proposed under row 1 of R&D run `renewing-vows` (`docs/rnd/renewing-vows.md`), signed off *fund* on 2026-10-10 and given its go on row 1 the same day (operator, verbatim: 'pool; beside it, provisional, new, now — create, then git sync'). A pool ADR is a change proposal: it books nothing and initiates nothing; promotion is the operator's (IRON LAW).

A chore run leaves a pass stamp in a Markdown log outside the ledger; the board's state
(35 overdue of 40 on 2026-10-05, 2026-10-07 and 2026-10-09) is read from files and prose. The
operator ruled on 2026-10-07 ('Runs yes, findings no'): each run of a chore is a ledger
event; a finding is not. The aviation analogue the run landed is the maintenance record
entry of 14 CFR § 43.9(a): a description of the work, the date, and the signature that
"constitutes the approval for return to service only for the work performed". The chore
estate is scheduled maintenance; its visits are scheduled work packages (FAA AC 120-16G
§ 6-1).

This is a new proposal, not an amendment of `ADR-pool.chores-system-maturity-absorption`
(operator ruling 2026-10-10: 'new'): that ADR absorbs executor-pipeline capability; this one
makes the run a Layer-2 record.

## Decision

Proposed, not decided. When promoted, the feature ADR would carry:

1. One ledger event per chore run, naming the chore, the trigger that made it due, the
   interval it discharges, the receipt of what it ran, and the attestor where the chore's
   class requires one. The event type lands with its producer and never before it
   (`docs/governance/rnd-discipline.md` § Ledger events; the ledger-vocabulary-inertness
   chore).
2. The chore board reads due-ness from those events, replacing the pass stamp as the run
   witness; the Markdown log becomes a rendering.
3. Findings stay where they are: insights, issues, or the run's receipt. A finding is not an
   event.
4. The maintenance visit of the rhythm (ratified 2026-10-10) is a named scheduled work
   package of due chores; its coming due is announced from the events, and gates nothing.

## Alternatives Considered

- **Keep the pass stamp.** Rejected: a stamp outside the ledger is a Layer-3 artifact
  standing in for Layer-2 truth (`docs/governance/state-doctrine.md`), and the board cannot
  be measured from it.
- **Findings as events too.** Refused 2026-10-07 ('findings no'): a finding has a home with
  a lifecycle already.
- **Amend the absorption ADR.** Rejected 2026-10-10 ('new'): capability and record are
  different subjects.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
