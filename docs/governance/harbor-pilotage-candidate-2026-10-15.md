# Martial law to civil rule — the harbor pilotage contract

Status: **CANDIDATE, awaiting operator ratification.** A dated record drafted 2026-10-15 in
session `4fd13b45-724e-4433-ab23-fd6c5df2b932`. It binds nothing until the operator
ratifies it; on ratification its text is carried unchanged into
[`build-to-1.0-campaign-2026-09-20.md`](build-to-1.0-campaign-2026-09-20.md) § Amendments,
on the precedent of the 2026-10-10 entry. Until then the pilot acts on the operator's
verbatim words below and on nothing wider.

## Authority

Operator (`g0`), verbatim, 2026-10-15, in order:

> I basically want a VERY POWERFUL model to take over, like a harbor pilot, and bring me
> into port. we can then resume gzkit's normal ceremony. BOOK THAT MODEL NOW.

> this is a TEMPORARY ARRANGEMENT until we get to port and dry dock. undeestood?

> get me a contract for this temporary arrangement and a plan to leave this "martial law"
> - this is a phase that should yield back to the magna carta. From this martial law back
> to "civil control."

> I wanted to PLAN in Fable, but not do all the work in fable.

> contract for entering and exiting martial law so I can resume, using the redesign, back
> towards the magna carta.

> in the meantime, you can take control of everything. I think the ledger writing still
> matters, but let's talk about that.

> martial law to get us on the diagram's plan including control plane and work/design
> modularization, then a return to magna carta (civilian rule)

Each is on the insights file at the time it was given.

## Entry

Martial law entered 2026-10-15 at the operator's word above. Its purpose is one sentence:
**get gzkit onto the diagram's plan, control plane and work-design modularization both, and
hand back to the Magna Carta.** The diagram, one line per band: the requirements catalog is
the product's truth, each REQ carrying its contract and state; the ADR lands contracts on
REQs, the release plan says which REQ states advance in a version, the work package selects
the REQs sharing one contract, the TASK is the increment that proves them; the airlock
derives the slice from the contract, GHIs and MX visits classify by the contract they
repair, eval checks module design against module code; every control in the plane names the
contract it protects.

## What is suspended, and what is not

**Suspended for the duration, by the operator's "take control of everything":**

- The IRON LAW's initiation clause. The pilot may initiate, cut, author and execute work
  packages toward the diagram without an operator initiation per package.
- Ascending ADR order and the Decomposition Matrix's arithmetic, for the re-cut of
  OBPI-0.35.0-16 to -20 only.
- The pipeline skill's full ceremony for pilot work: a pilot package runs on the records in
  § Records, not on the stage machinery, until that machinery is itself re-cut.

**Not suspended, under any reading:**

- Gate 5. A completion is attested by the operator's own words or it is not complete. The
  pilot cannot attest for the operator.
- The ledger as system of record, written only through `gz` commands; never hand-edited.
- No control is removed, demoted or bypassed; `--no-verify` is not used; the hangar is not
  entered to escape a guard.
- The operator-PII rule. The Prime Directive.
- Rulings. Structure is decided by the operator on the pilot's draft; the pilot recommends
  and does not decide. The two standing rulings the second substrate touches ("ADR ORDER
  IS ABSOLUTE"; "wait for ADR-0.38.0 in strict order") fall only by the operator's word.

## On the ledger, for the operator's ruling

The operator holds that ledger writing still matters. The pilot agrees, and distinguishes
two things the ledger carries today. The acts that matter to the handback are few: commits
with their trailers, red receipts at commit grain, operator rulings, attestations, and the
passage log. The process traffic is most of the volume (five thousand `artifact_edited`,
thirteen hundred `agent_sync_completed`, eight hundred `brief_reconciled`) and is written by
hooks and sync verbs that stand. Under martial law nothing changes in how the ledger is
written: every pilot act lands through the verbs that already write it, and the hooks keep
writing what they write. What the redesign decides, under civil rule, is which events the
catalog-centred shape keeps: events keyed by contract and work package, with process events
demoted to derived views. That is a design question, not a martial-law act, and it is put
to the operator with the catalog.

## Division of labor

- **The pilot, a Fable-class session,** plans, measures, drafts and rules with the
  operator. It writes this contract, the work orders, the candidate canon and the catalog's
  first entries. It executes a cut itself only when the cut is the measurement's own
  finding and small enough to read in one sitting; it does not do all the work.
- **Cheaper sessions** execute the work orders under § Records, each a GHI-cited change
  with mechanical witnesses. A work order carries no structural decision.
- **The operator** rules every structural question the pilotage surfaces, with the facts
  and at most three options, and attests every completion.

## Mandate

1. Cut context load at session start, per edit turn and at pipeline invoke.
2. Author the requirements catalog's first entries from the obligations OBPI-0.35.0-16
   to -20 carry, each with its contract, legacy ids as aliases, no identifier change.
3. Re-cut 16 to 20 as work packages selected by contract from those entries.
4. Make the TASK the increment: cut per increment, dispatched with its REQ, witnessed at
   commit grain on the pipeline route, recorded against its REQ.
5. Give every control in the plane the contract it protects, and move incident history out
   of the per-turn load into rationale records keyed by control.
6. Measure before and after every act; report counts with what they show and do not show.

## Records

- Every pilot change is one commit, `fix(<scope>): … (GHI #N)` or
  `feat(<scope>): … (GHI #N)`, with a `Task:` trailer, a failing test observed before the
  change, and `gz arb red --commit <sha>` run after it with its verdict recorded; an
  `undriven` verdict is repaired in the same commit before it counts.
- Every operator ruling is an insight record when given and an `[operator-ruled]` handoff
  entry.
- Every session ends with a handoff citing this file and listing the pilot commits since the
  last.
- This file's § Passage log is appended per act with bytes or counts before and after.

## Exit — port, then dry dock, then civil rule

Martial law ends when all of the following hold, each read from its witness, or earlier at
the operator's word. It does not renew itself. A session that cannot meet a condition says
so in its handoff.

1. **Session start is bounded.** Orientation under 8 KB, the campaign block under its test
   cap. Witness: `TestCampaignBlockIsBounded` and a live render. *(Met 2026-10-15.)*
2. **AGENTS.md is within budget.** Witness: `gz validate --instructions-files-budget`
   without the budget advisory.
3. **Pipeline invoke is bounded.** Incident history out of the skill body into a rationale
   record keyed by control; the body ceiling re-derived from the lifted size; bytes at invoke
   measured before and after. Witness: `gz skill audit` and § Passage log.
4. **The catalog exists and is used.** Catalog entries with contracts for the obligations of
   16 to 20, and those briefs re-cut as work packages selected by contract. Witness: the
   catalog file and the re-cut briefs, each naming its contract and its entries.
5. **The TASK is the increment on one package.** At least one work package lands with TASKs
   cut per increment, each commit carrying its trailer and a `red_commit_receipt_emitted`
   event, in one session, with the operator witnessing two artifacts: its REQs and its TASK
   receipts. Witness: the ledger's events and session count for that package; the
   attestation text.
6. **Every control names its contract.** The advisory scorecard carries an obligation
   column, and a control with no obligation is listed for the operator's disposition.
   Witness: `gz validate --advisory-scorecard` reading the column.
7. **Handback.** The operator ratifies a campaign amendment that lists every pilot commit,
   marks each kept or reverted, carries this § Passage log, restores the IRON LAW's
   initiation clause, and declares civil rule resumed. The campaign then sequences the
   catalog-first work; dry dock is that work.

## Work orders

In order. Each is a GHI through `ghi-author`, executed under § Records, closed through
`ghi-close`. WO-1 to WO-3 and WO-5 to WO-6 go to cheaper sessions; WO-4 and WO-7 are the
pilot's, because they carry the catalog's shape and the re-cut, which the operator rules on.

- **WO-1 (done).** GHI #1242, the orientation campaign block as pointers. Commit
  `5cd4c3ece` (amended to drive every hunk; see § Passage log).
- **WO-2.** AGENTS.md to budget through the `instructions-files-diet` chore; the session
  stops at the chore's step 4 and presents the items for the operator's ruling.
- **WO-3.** The pipeline skill's incident history (49 cited issues, 16 rationalization
  rows) to a rationale record keyed by control, on the rule-version-history precedent; the
  body ceiling re-derived.
- **WO-4 (pilot).** The catalog's first entries, with contracts, from the obligations of
  16 to 20; the three shapes (entry, assignment row, contract) put to the operator first.
- **WO-5.** `extract_plan_tasks` stops dispatching rejected alternatives; interim until
  the dispatch unit is the TASK.
- **WO-6.** One tracker for the 27 helper-or-loop gates of the 2026-10-14 sweep.
- **WO-7 (pilot).** The re-cut of 16 to 20 as work packages by contract, with the TASK as
  increment and the commit-grain witness on the pipeline route; the three re-cut decisions
  put to the operator with the cut.
- **WO-8.** The obligation column on the advisory scorecard.

Not work orders under martial law: the identifier ladder's timing, the crew split's final
shape, the second-substrate sortie, the Matrix's replacement text. These are civil-rule
decisions this pilotage prepares.

## What does not change

Gate 5. The ledger rule. Every control standing under § Amendments 2026-10-04 (2). The
operator-PII rule. The Prime Directive. TOPMOST remains `ADR-0.35.0`; the pilotage works
inside it.

## Passage log

| Date | Act | Before | After | Commit | Witness |
|---|---|---|---|---|---|
| 2026-10-15 | orientation campaign block to pointers (GHI #1242, closed) | 19,431 B block; ~22,500 B orientation | 1,570 B block; 5,524 B orientation | `99acdc8a0` | `TestCampaignBlockIsBounded` (RED at 22,639 B); `gz arb red --commit 99acdc8a0` verdict `driven`, receipt `arb-red-commit-99acdc8a0433-4c5dabe3a61449cf82abc3b2343f282a` (a first run on the pre-amendment commit was `undriven` on 5 `_campaign_head` hunks; assertions added, commit re-cut); `gz check` passed |
