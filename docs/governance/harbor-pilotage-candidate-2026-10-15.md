# Safe mode to civil rule — the harbor pilotage contract

Status: **RATIFIED 2026-10-15** (operator, verbatim: *"ratify the contract, draft the three
catalog shapes"*); **AMENDED 2026-10-17** to the ratified drydock plan (operator rulings of that
day, § Rulings of 2026-10-17). Drafted 2026-10-15 in session `4fd13b45-724e-4433-ab23-fd6c5df2b932`.
This file is the binding text; the campaign plan carries a pointer entry at
[`build-to-1.0-campaign-2026-09-20.md`](build-to-1.0-campaign-2026-09-20.md)
§ Amendments 2026-10-15 so that the plan, which the orientation and every session read for
sequencing, knows the phase is in force and where its terms are. The sections the 2026-10-17
amendment replaced are kept verbatim under § Superseded on 2026-10-17 as a record.

## Authority

> This contract is the first instance of `docs/governance/safe-mode-doctrine.md`; the
> reusable shape is `.gzkit/templates/safe_mode_contract.md` (entrenched 2026-10-16).

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

Operator (`g0`), verbatim, 2026-10-17, the drydock's purpose restated after two days of drift:

> safe mode isn't here to drive req/feature work, it is for deep repairs/realignments

> When I told you take charge and use a deep, rich model like Fable to plan, it was to plan what
> the dry dock order of work would be, right? What are we retooling, redesigning, reconfiguring?

> your whole dry dock plan was ill conceived - can we get the purpose of safe mode and dry dock
> clear please?

## Purpose

Safe mode is an occasional flip inside the standing maintenance mode (the Maintenance Hangar, the
chores, the patch releases, and the GitHub issues that carry repair and refactor work). It lowers
the ceremony's constraints and most of its safeguards so that structure can be re-rigged,
reconfigured, retooled and restructured quickly, and it is turned off when that is done. Operator,
2026-10-17, verbatim:

> Safe mode has to be a way to quickly, without all the uh, constraints of the ceremony and all
> those other safeguards, which are important, to be able to just lower all that, to be able to
> make the re-rigging, reconfiguring, retooling, restructuring, and all that. But once we do that,
> we then want to turn off safe mode and return to normal operations under the new structures.

This period is a drydock: the ship is out of the water so the structure can be repaired and
realigned. It designs and lands the new structures and does not populate them (operator, verbatim:
*"yes, repair and realign the structure, don't populate it"*). The new structures are the general
arrangement below. Normal voyages, ordinary operations under them (work-package management,
release management, the feature and requirement backlog), resume when safe mode is turned off.

A drydock session holds repair orders. A repair order is the maintenance mirror of the work
package: one bounded repair with a scope, a witness and an owner, recorded to the ledger, and held
as a GitHub issue under the repair tagging scheme once RO-5 lands it (operator, verbatim: *"dry
dock orders can have repair orders... Those can still go over to the ledger. And for all I know, we
might even be able to make them as a part of the GitHub issue system, which I'd be fine with"*).

## The general arrangement

![gzkit general arrangement, 2026-10-17](general-arrangement-2026-10-17.svg)

Redrawn 2026-10-17 from § Entry of the 2026-10-15 text and the operator's rulings of that day; the
pilot's original drawing of 2026-10-15 was made outside this repository and is not recoverable.
Verified from first principles the same day (§ Rulings of 2026-10-17). The bands, top to bottom:

| Band | Carrier | Holds | Relation downward |
|---|---|---|---|
| Product intent | PRD | functional requirements (`FR-nnn`) and non-functional requirements (§7 quality attributes) | feature areas trace to an FR or a quality attribute |
| The product's truth, and decisions, as peers | Requirements catalog, beside the ADR | Catalog: feature areas, first-class and typed functional or non-functional; REQs, each in one area, carrying its contract, state, revision history and its legacy id as an alias; Gherkin feature files prove functional REQs where there is a user (the `gz` CLI). ADR: a decision and its rationale, made only where a decision is needed; it lands contracts on the REQs it touches and carries no version and no release. The REQ–ADR link is two-way for those REQs. Not every requirement or feature needs an ADR | a work package is cut from the catalog directly in the ordinary case, or from an ADR where one exists |
| Labor | Work package, then task cards | a work package selects the REQs sharing one contract, from the catalog or from an ADR, and always names its REQs; a task card is the increment: one commit, one trailer, one commit-grain witness citing the REQ | the Release Package ships work packages; the release record carries the task cards' witnesses |
| Version | Release Package, and the ledger release record | the Release Package (planned, in-flight, released) selects the work packages that ship and says which REQ states advance in the version; the version lives here. The ledger release record says what actually shipped. The campaign sequences releases; a Release Package says what one release contains | — |

The rails: the control plane reads the contract (the airlock derives its slice from the contract's
modules; GHIs and MX visits classify by the contract they repair; eval checks module design
against module code; every control names the contract it protects; every surface an agent loads
is within a witnessed budget; the ledger is the record and the human attests). Maintenance mode is
standing (the hangar, the chores, the patch releases; GHIs carry repair and refactor work, never
feature or requirements work); safe mode is an occasional flip inside it; a drydock is one session
of safe mode holding repair orders.

There is no bounded-advance document. The feature area groups the requirements and the Release
Package selects the work packages that ship together, so which work packages advance a feature
together is a query over those records.

**Amended 2026-10-18.** The operator ruled [the requirements model](ieee/requirements-model.md):
a work package delivers exactly one outcome (an outcome's REQs are those sharing its contract), and
the Release Package selects outcomes, not REQ states. Where the table above says otherwise, that
model governs. The engineering-order rung of the 2026-10-05 ladder is
retired (operator, verbatim: *"A, no separate document — retire the engineering order rung"*);
the ladder's other rungs stand, and identifiers still migrate at 1.0 with aliases before it.

Every arrow is realizable by a stored field on one condition the as-built tree violates: REQ
identity independent of the ADR and the work package. Today the ADR's semver is embedded in every
REQ, TASK and OBPI id, so the drawing is a target until that seam lands (RO-2).

## What is suspended, and what is not

Suspended while `.gzkit/mx.json` carries `mode: safe`, by the ruling of 2026-10-17 (R6, "A"):

- Every guard outside the four below drops to advisory, as the Maintenance Hangar's do, and the
  hard-gate exit re-runs every guard at full strength. In force since RO-0's second act: the
  checkpoint demotes under either mode and the pipeline gate honors the marker.
- The IRON LAW's initiation clause, for repair orders: the session cuts, authors and executes
  repair orders toward the general arrangement without an initiation per order.
- Brief ceremony. No OBPI is initiated or completed under safe mode; OBPI completion is work in the
  paradigm the drydock replaces (R4; operator, verbatim: *"I don't know why you would do an OBPI,
  which is actually completed work in the old paradigm, when I'm still actually discussing what the
  new paradigm might look like"*).

Not suspended, under any reading:

- Gate 5. A completion is attested by the operator's own words or it is not complete.
- The ledger as system of record, written only through `gz` commands; never hand-edited.
- The operator-PII rule. The Prime Directive.
- No control is removed. Lowered to advisory is not removed; the exit restores it.
- Rulings. Structure is decided by the operator on the session's draft.

## Division of labor

- **The session** appraises, plans, measures, drafts and rules with the operator, and executes a
  repair order itself only when it is the measurement's own finding and small enough to read in
  one sitting (operator, 2026-10-16: *"fable extra is expensive if you have a deterministic plan
  you are now executing"*).
- **Cheaper sessions** execute the deterministic repair orders under § Records.
- **The operator** rules every structural question, with the facts and at most three options,
  enters and exits through the `gz-mx` skill, and attests.

## Mandate

1. Cut what every agent loads to a witnessed budget, each cut measured for effect.
2. Give REQ, TASK and release identity independent of the ADR, by alias and resolver, renaming
   nothing before 1.0.
3. Land the requirements store and the feature-area registry as empty structure, with their
   validators and the BDD alignment check.
4. Detach the release from the ADR: one release shape, the Release Package with the ledger release
   record, and `gz closeout` keyed to it.
5. Land the work-package, task-card and repair-order structure, with the repair tagging scheme for
   GitHub issues.
6. Retire the canon the general arrangement contradicts, with retention maps.
7. Dispose of the in-flight work and hand back.

## Records

- Every change is one commit, `fix(<scope>): … (GHI #N)` or `feat(<scope>): …`, with a `Task:`
  trailer naming its repair order (`TASK-ro<n>-<slug>` until the repair tagging scheme lands), a
  failing test observed before a code change, and `gz arb red --commit <sha>` run after it with its
  verdict recorded; an `undriven` verdict is repaired in the same commit before it counts.
- Every operator ruling is an insight record when given and an `[operator-ruled]` handoff entry.
- Every session ends with a handoff citing this file and listing the commits since the last.
- § Passage log is appended per act with bytes or counts before and after.
- § Repair orders is the register of this drydock until RO-5 moves repair orders to GitHub issues;
  an order's state moves only by an act in the passage log.

## Repair orders

In dependency order. RO-1 and RO-7 run in parallel with the rest on cheaper sessions. Each names
the band of the general arrangement it serves.

| Order | Serves | What it lands | Witness | Owner |
|---|---|---|---|---|
| RO-0 | the drydock itself | this contract rewritten to the ratified plan with the drawing saved beside it; the doctrine page and the contract template to match; safe mode lowering every guard but the four to advisory while the marker is open (R6); the uncommitted 2026-10-17 drift disposed | `mkdocs build --strict`; `gz validate --distribution`; the guard tests | the session |
| RO-1 | control plane | the bleeding stopped: session-start text under 4 KB on one channel; the dead `instruction-router` hook removed; skill descriptions to one sentence, under 6,000 chars in total; rule version banners lifted to rule-version-history; the governance read mandate pointed at the Coverage Ledger section; the budget witness extended to every loaded surface, measuring the skills that load | `gz validate --instructions-files-budget` over every surface; the proof file; WP-16's effectiveness read per cut | cheaper sessions (GHIs #1246, #1249, #1252) |
| RO-2 | catalog, labor, version | the keystone: one id-resolution seam shared by every reader (phase 1 of `ADR-pool.identifier-ladder-migration`, pulled forward by R5); explicit parent fields on REQ and TASK read everywhere the regex sites recover them today; the nine width-loose grammar copies replaced by the one body; no identifier changes | a validator proving every reader resolves through the seam; the 412 behave tags and every `@covers` still resolve | the session specifies; a cheaper session lands |
| RO-3 | catalog | the requirements store as empty structure: the schema for `data/requirements_catalog.json` and for the feature-area registry (area typed functional or non-functional, traced to a PRD FR or §7 attribute); REQ lifecycle events; a validator that fails a brief assignment naming no entry; acceptance records keyed by REQ; the BDD alignment validator (a feature file declares one area; each scenario's REQ tag resolves through the alias to an entry in that area; areas with no scenario reported). No entry authored | schemas validate; `gz test` green; the validators registered | the session specifies; a cheaper session lands |
| RO-4 | version | release detached from the ADR (R3): the Release Package as the plan and the ledger release record as the shipped claim; the version lives on the release; `version_sync` stops deriving from the ADR id (Q-08); `gz closeout` keyed to a Release Package; patch qualification stated on the receipt; `gz-release` subsumes `gz-patch-release` (GHI #1248); `releases/README.md` and `adr-lifecycle.md` ADR-as-carrier text retired | `gz validate --version-release`; a dry-run closeout keyed to an empty Release Package | the session specifies; a cheaper session lands |
| RO-5 | labor, maintenance | the work-package and task-card structure: lane held once, on the work package; checklist to brief link by stored id, not position; the decomposition matrix detached from lane and kind; the repair-order template and the repair tagging scheme for GitHub issues; a repair-order lifecycle event with the issue number as alias; `ghi-close` carrying the PR-closeout distinctions | schema validation; one repair order of this drydock run through the new template | the session specifies; a cheaper session lands |
| RO-6 | every band | contradicted canon retired with retention maps: PRD INV-013, INV-017, INV-023, FR-005a, FR-006 and its stale frontmatter; the GovZero docs stale as a class (GHI #1188); the IEEE README's bars and Q-18's "names chosen later"; the engineering-order rung in the ladder records; Astra's rejection reconciled in DISAGREEMENTS; the glossary | `mkdocs build --strict`; `gz validate --adr-status-fresh`; the retention maps | cheaper sessions |
| RO-7 | control plane | the rest of the cut, staged, one WP-16 report per stage: skill bodies' rationalizations and doctrine restatements to `references/`, the catalogue merged toward 40 with the merge plan put to the operator first (GHI #1250); rules narrative lifted (GHI #1246); personas, agents and nested `AGENTS.md` to budget after confirming what Claude loads (GHI #1251); AGENTS.md only by operator retire or re-tier of invariant entries | `gz validate --instructions-files-budget`; the stage reports under `docs/evals/` | cheaper sessions |
| RO-8 | the in-flight work | ADR-0.35.0 frozen (R4): no further OBPI completions; briefs 17 and 20 stand on the passage log and their receipts; the unlanded items and the obligations of 11 to 20 carried into the catalog at civil rule; the Movement A to F boxes and the handback's kept-or-reverted list | the handback amendment | the operator rules; the session drafts |

## Exit — seaworthiness

Safe mode ends when every repair order is closed and each of the following reads true from its
witness, or earlier at the operator's word:

1. Every surface an agent loads is within a witnessed budget, with an effectiveness report per cut.
2. The resolver and the parent fields are in place and every regex reader is replaced.
3. The catalog, feature-area and release schemas and their validators are landed, empty.
4. One release shape is ruled and `gz closeout` is keyed to it.
5. The contradicted canon is retired.
6. The in-flight work is disposed.
7. The handback amendment is ratified: every drydock commit listed, kept or reverted; this
   passage log carried; the suspended rules restored. Civil rule resumes on the ratification.

The sea trial (a fresh project on the released wheel runs one work package end to end) is civil
rule's first act, in Movement E of the campaign where it already lives; it is not an exit
condition of the drydock.

## Rulings of 2026-10-17

Operator, verbatim, in order; each is also an insight record at the time it was given.

- *"proceed with H8, invoke /gz-mx"* — safe mode entered through the skill (H8 met).
- *"accept all four disclosures, A for the coupled consumer"* — the cutover disclosures (a) to (d)
  of `d47de23c8` accepted; `features/steps/acceptance_recovery_steps.py` recorded in brief 17.
- *"A, features are first-class requirement areas (will this bdd align?)"*.
- *"yes, repair and realign the structure, don't populate it"*.
- *"We're not sunsetting ADRs. They've got to stop driving release"*.
- *"I use GitHub issues largely for repair and, and address and refactor and all that. I don't do
  it for feature work or requirements work at all... I'd like maintenance mode and GitHub issues to
  be very tightly coupled."*
- *"maintenance mode is really rich... I just am able to go to safe mode occasionally"*; *"there's
  equal entries between requirements and ADRs"*.
- *"You're still insisting that ADRs always lead to work packages and that's just not true... It's
  possible that ADR could lead to work package, or the requirements catalog could lead to it."*
- *"A, no separate document — retire the engineering order rung"*.
- *"A on all five"*: R1 the repair order mirrors the work package and the work order stays retired;
  R2 Gate 5 stays per work package with a release attestation on top; R3 the Release Package is
  the plan and the ledger release record the shipped claim, `gz-release` subsumes
  `gz-patch-release`; R4 ADR-0.35.0 frozen, no further OBPI completions; R5 the alias resolver
  pulled into the drydock as RO-2; R6 safe mode drops every guard to advisory except Gate 5, the
  ledger through `gz`, operator PII and the Prime Directive.

Rulings of 2026-10-15 and 2026-10-16 that stand unchanged: the contract ratified; the control
inventory attested; "adrs are not releases" and the Release Package; safe mode as a mode of the
hangar and the sole term; the work order retired; the control-plane cut ruled A with backups; the
chart amended to one exceptional period, now superseded by § Exit above.

## What does not change

Gate 5. The ledger rule. The operator-PII rule. The Prime Directive. TOPMOST remains `ADR-0.35.0`
until RO-8 disposes of it; the drydock works inside the campaign, which sequences what follows.

## Superseded on 2026-10-17 (record, not binding)

The text below is the contract as it stood from 2026-10-15 to 2026-10-17: the diagram prose of
§ Entry, the first mandate, the harbor and drydock legs, the exit numbers, the sea trial as exit, the
executive decisions and the work packages. It is kept verbatim because the passage log cites it.
Where it conflicts with the sections above, the sections above govern. Standing from it: the
WP-4 shapes as civil-rule design input (the category field is a first-class feature area; no
engineering order); executive decisions 2, 3 and 6; the backup tag `control-plane-baseline-2026-10-16`
and the measured baseline; WP-10 to WP-16 as filed, now the GHIs RO-1 and RO-7 cite.

### Entry

Safe mode entered 2026-10-15 at the operator's word above. Its purpose is one sentence:
**get gzkit onto the diagram's plan, control plane and work-design modularization both, and
hand back to the Magna Carta.** The diagram, one line per band: the requirements catalog is
the product's truth, each REQ in one first-class feature area and carrying its contract and
state; the engineering order, the feature bundle that succeeds the (m)ADR (Q-18; ladder ruled
2026-10-05), lands contracts on REQs for one bounded advance, and an ADR records an
architecture decision only; the Release Package says which REQ states advance in a version, the work package selects
the REQs sharing one contract, the TASK is the increment that proves them; the airlock
derives the slice from the contract, GHIs and MX visits classify by the contract they
repair, eval checks module design against module code; every control in the plane names the
contract it protects.

### What is suspended, and what is not

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

### On the ledger, for the operator's ruling

The operator holds that ledger writing still matters. The pilot agrees, and distinguishes
two things the ledger carries today. The acts that matter to the handback are few: commits
with their trailers, red receipts at commit grain, operator rulings, attestations, and the
passage log. The process traffic is most of the volume (five thousand `artifact_edited`,
thirteen hundred `agent_sync_completed`, eight hundred `brief_reconciled`) and is written by
hooks and sync verbs that stand. Under safe mode nothing changes in how the ledger is
written: every pilot act lands through the verbs that already write it, and the hooks keep
writing what they write. What the redesign decides, under civil rule, is which events the
catalog-centred shape keeps: events keyed by contract and work package, with process events
demoted to derived views. That is a design question, not a safe-mode act, and it is put
to the operator with the catalog.

### Division of labor

- **The pilot, a Fable-class session,** plans, measures, drafts and rules with the
  operator. It writes this contract, the work packages, the candidate canon and the catalog's
  first entries. It executes a cut itself only when the cut is the measurement's own
  finding and small enough to read in one sitting; it does not do all the work.
- **Cheaper sessions** execute the work packages under § Records, each a GHI-cited change
  with mechanical witnesses. A work package carries no structural decision.
- **The operator** rules every structural question the pilotage surfaces, with the facts
  and at most three options, and attests every completion.

### Mandate

1. Cut context load at session start, per edit turn and at pipeline invoke.
2. Author the requirements catalog's first entries from the obligations OBPI-0.35.0-16
   to -20 carry, each with its contract, legacy ids as aliases, no identifier change.
3. Re-cut 16 to 20 as work packages selected by contract from those entries.
4. Make the TASK the increment: cut per increment, dispatched with its REQ, witnessed at
   commit grain on the pipeline route, recorded against its REQ.
5. Give every control in the plane the contract it protects, and move incident history out
   of the per-turn load into rationale records keyed by control.
6. Measure before and after every act; report counts with what they show and do not show.

### Records

- Every pilot change is one commit, `fix(<scope>): … (GHI #N)` or
  `feat(<scope>): … (GHI #N)`, with a `Task:` trailer, a failing test observed before the
  change, and `gz arb red --commit <sha>` run after it with its verdict recorded; an
  `undriven` verdict is repaired in the same commit before it counts.
- Every operator ruling is an insight record when given and an `[operator-ruled]` handoff
  entry.
- Every session ends with a handoff citing this file and listing the pilot commits since the
  last.
- This file's § Passage log is appended per act with bytes or counts before and after.

### Exit — port, then dry dock, then civil rule

Safe mode ends when all of the following hold, each read from its witness, or earlier at
the operator's word. It does not renew itself. A session that cannot meet a condition says
so in its handoff.

1. **Session start is bounded.** Orientation under 8 KB, the campaign block under its test
   cap. Witness: `TestCampaignBlockIsBounded` and a live render. *(Met 2026-10-15.)*
2. **AGENTS.md is within budget.** Witness: `gz validate --instructions-files-budget`
   without the budget advisory. *(Met 2026-10-16, by ruling: GHI #1243, verbatim "A, record
   the budget at the invariant floor"; the enforced budget records the attested floor plus
   margin, and the doctrine ceiling stays destination work.)*
3. **Pipeline invoke is bounded.** Incident history out of the skill body into a rationale
   record keyed by control; the body ceiling re-derived from the lifted size; bytes at invoke
   measured before and after. Witness: `gz skill audit` and § Passage log. *(Met 2026-10-15
   by the cutover `d47de23c8`: 125,923 B to 11,445 B at invocation, the ceiling entry removed,
   no audit finding.)*
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

### Work packages

In order. Each is a GHI through `ghi-author`, executed under § Records, closed through
`ghi-close`. WP-1 to WP-3 and WP-5 to WP-6 go to cheaper sessions; WP-4 and WP-7 are the
pilot's, because they carry the catalog's shape and the re-cut, which the operator rules on.

- **WP-1 (done).** GHI #1242, the orientation campaign block as pointers. Commit
  `5cd4c3ece` (amended to drive every hunk; see § Passage log).
- **WP-2.** AGENTS.md to budget through the `instructions-files-diet` chore; the session
  stops at the chore's step 4 and presents the items for the operator's ruling.
- **WP-3.** The pipeline skill's incident history (49 cited issues, 16 rationalization
  rows) to a rationale record keyed by control, on the rule-version-history precedent; the
  body ceiling re-derived.
- **WP-4 (pilot).** The catalog's first entries, with contracts, from the obligations of
  16 to 20; the three shapes (entry, assignment row, contract) put to the operator first.
  Amended 2026-10-17: the entries follow [the joined requirements model](ieee/design-candidates.md#the-joined-requirements-model) (`Q-19`), each in one first-class feature area typed functional or non-functional; no entry is authored until the operator ratifies that model and rules its five open points. Amended 2026-10-18: the operator ruled the model and its open points; it now lives in [the requirements model](ieee/requirements-model.md), and its family legend is ruled (decision 8.3), so entries are no longer blocked on the model.
- **WP-5.** `extract_plan_tasks` stops dispatching rejected alternatives; interim until
  the dispatch unit is the TASK.
- **WP-6.** One tracker for the 27 helper-or-loop gates of the 2026-10-14 sweep.
- **WP-7 (pilot).** The re-cut of 16 to 20 as work packages by contract, with the TASK as
  increment and the commit-grain witness on the pipeline route; the three re-cut decisions
  put to the operator with the cut.
- **WP-8.** The obligation column on the advisory scorecard. GHI #1247 (filed 2026-10-16).

Not work packages under safe mode: the identifier ladder's timing, the crew split's final
shape, the second-substrate sortie, the Matrix's replacement text. These are civil-rule
decisions this pilotage prepares.

Booked for civil rule on 2026-10-16, from the operator's words that day:

- **The release artifact.** Verbatim: *"adrs are not releases, i am surprised you
  recommend this."* An ADR records a decision and lands contracts on REQs; a separate
  release artifact says which REQ states advance in a version and which work packages ship,
  and carries the closeout that is the release today. The pilot's recommendation to reshape
  the feature ADR into the Release Package is withdrawn; the feature ADR's semver and `gz
  closeout`'s "a feature/minor closeout is a release" are the conflation the migration
  retires.
- **Safe mode.** Verbatim: *"we need a 'safe mode' that allows this sort of unencumbered
  'martial law' as a toggle."* This contract is a hand-written instance of it. The nearest
  existing toggle is the MX hangar (`gz mx enter`, `.gzkit/mx.json`, `.gzkit/rules/mx-mode.md`),
  which demotes guards to advisory while the Gate 5 invariants, the ledger and the PRIME
  DIRECTIVE still bind; safe mode differs in what it suspends (initiation and brief ceremony,
  not guards) and in carrying a contract: entry, mandate, records, exit.

#### WP-4 draft — the three catalog shapes (drafted 2026-10-15, for ruling)

Three shapes, each composed from fields the candidate design already names
([`ieee/design-candidates.md`](ieee/design-candidates.md) § Requirement, assignment, and
evidence identity) and from readers that already exist. Nothing below renames a historical
identifier; legacy `REQ-X.Y.Z-NN-MM` ids become aliases, and every proof channel keeps
binding to the alias until the acceptance store's transition is designed under civil rule.
The worked example is a real obligation of `OBPI-0.35.0-16`.

**Shape 1 — the catalog entry.** One per obligation, in a git-versioned JSON file read by
code (`data/requirements_catalog.json`; registries under `data/` are the precedent, and
execution reads state from JSON, never prose). A Markdown view of the catalog is derived,
never authored.

```json
{
  "id": "REQ-C0001",
  "statement": "Given an in-flight pipeline run whose position is recorded on disk, when a process holding only the repository reads the run through `gz obpi status` or the session orientation, then it obtains the next command for that position, and the read changes no marker field and appends no ledger event.",
  "kind": "BEHAVIOR",
  "feature": "pipeline-runtime",
  "source": ["ADR-0.13.0 § Decision", "ADR-0.35.0 checklist item 16"],
  "applicability": "gzkit >= 0.35.0",
  "state": "approved",
  "revision": 1,
  "history": [{"revision": 1, "date": "2026-10-15", "change": "entered from REQ-0.35.0-16-03", "by": "g0"}],
  "aliases": ["REQ-0.35.0-16-03"],
  "contract": "see shape 2",
  "proof": {"channel": "covers", "tests": []}
}
```

`id` is a sequential integer under a `REQ-C` prefix and is never reused. `feature` names one
first-class feature area: a requirement area with its own registry entry beside the catalog
(slug, name, scope statement), FDAU's semantic area made explicit (operator, 2026-10-17). Moving
an entry between areas is a new revision and changes no identity. `state` is
one of `proposed`, `approved`, `implemented`, `verified`, `retired`; a retirement is a new
revision with the reason, never a deletion. `kind` and `proof.channel` keep the three kinds
and their channels from ADR-0.0.59.

**Shape 2 — the contract on the entry.** The design the REQ carries, versioned with the
entry's revision, which is what "design exists within the REQ" means mechanically. It is
what the constraints sortie lands before any red, so the red witness classifies on an
assertion and not on a missing symbol.

```json
"contract": {
  "interfaces": ["gzkit.pipeline_next_command.next_command(position: PipelinePosition) -> NextCommand"],
  "invariants": ["reading the next command writes no marker field and appends no ledger event"],
  "modules": ["src/gzkit/pipeline_next_command.py", "src/gzkit/commands/status.py", "scripts/session_orientation.py"],
  "stub": "next_command exists and returns NextCommand(command=None, blockers=()) until its TASK lands, so a covering test reaches its assertion",
  "witness": ["tests/test_pipeline_next_command.py"]
}
```

`modules` is the binding the airlock derives a slice from, and the obligation column of the
scorecard points at the contract a control protects. A work package selects entries whose
contracts share a module set.

**Shape 3 — the assignment row in a brief.** Machine-readable, in the brief's frontmatter
beside `tasks:` and `req_atomic:`, which the frontmatter readers already parse. The brief's
Acceptance Criteria keep one line per assignment carrying the legacy id as the alias the
proof channels bind to.

```yaml
assignments:
  - req: REQ-C0001
    revision: 1
    contribution: implement
    acceptance: "both consumers state the next command for a recorded position; the read is pure"
    constraints: ["contract.invariants[0]"]
    proof:
      channel: covers
      tests: ["tests/test_pipeline_next_command.py::TestNextCommand::test_fresh_process_reads_the_recorded_position"]
    tasks: ["TASK-0.35.0-16-03-01"]
```

`contribution` is one of `implement`, `refine`, `verify`, `repair`, `retire`. A brief may
carry several assignments; an entry may have assignments in several briefs; no assignment
needs its own document. Completing the brief accepts its contributions; whole-requirement
satisfaction is the entry's `state`, a separate claim.

**Three rulings these shapes need.**

1. The id grammar: `REQ-C<n>` sequential, category as metadata (recommended), or an id that
   encodes the category.
2. The home: one JSON file under `data/` read by code with a derived Markdown view
   (recommended), or authored Markdown entries.
3. The assignment channel: brief frontmatter with the legacy line kept as alias
   (recommended), or a Markdown table in the brief body.

With the three ruled, WP-4 authors the entries for the obligations of `OBPI-0.35.0-16` to
`-20`, thirty-three BEHAVIOR and twelve SUPPORT lines today, each with its contract, and
WP-7 re-cuts the briefs as work packages by contract.

### Pilotage chart — one exceptional period: harbor, drydock, sea trial, handback (amended 2026-10-16)

Written under crisis mode at the operator's word (verbatim: *"lean in and make executive decisions
to achieve outcomes"*; *"gzkit has become untenable"*). Amended the same day on three
confirmations, verbatim *"confirm all three, amend the chart"*: safe mode runs through the drydock
and the sea trial and ends at seaworthiness; the sea trial substrate is a fresh project on the
released wheel; the Release Package has the shape in § The Release Package. The chart is the tracking
instrument: one row per leg, each with its witness and its last reading. The passage log records
each act; a leg's reading moves only by an act in that log. WP-10 (GHI #1245) makes the readings
mechanical.

#### The regime

| Phase | Regime | Produces | Done when |
|---|---|---|---|
| Harbor | safe mode | load cut, inventory, serving, the toggle, the budget | H1 to H9 met |
| Drydock | safe mode | the catalog, the Release Package type, work packages for 16 to 20, controls naming their contracts, the control plane cut to budget and measured, the ladder migrated, the first release | the first release built and published through a Release Package, with the drydock exit numbers met |
| Sea trial | safe mode | a fresh project on the released wheel runs one work package end to end | the trial recorded in the passage log |
| Handback | ratification | the amendment: every pilot commit kept or reverted, the passage log carried, the initiation clause restored | the operator's word; `/gz-mx` exits through the hard gate |
| Voyage | Magna Carta | releases planned, packaged, witnessed, attested | ordinary operations |

Safe mode is left once, at seaworthiness. Nothing returns to civil rule in between.

#### Harbor legs

| Leg | What it means | Witness | Reading 2026-10-16 | Owner |
|---|---|---|---|---|
| H1 | Session start bounded | `TestCampaignBlockIsBounded`; orientation under 8 KB | met, 4,831 B | done |
| H2 | AGENTS.md within budget | `gz validate --instructions-files-budget`, no advisory | met by ruling (GHI #1243), 846 chars headroom | done |
| H3 | Pipeline invoke bounded | `gz skill audit`; § Passage log | met, 125,923 B to 11,445 B | done |
| H4 | Per-turn rules and skill descriptions cut | the two sizes in the passage log before and after; `gz skill audit` | not started: rules 150 KB over 26 files, descriptions 15,085 chars | cheaper session, WP-11, GHI #1246 |
| H5 | The catalog exists and is used | `data/requirements_catalog.json` loads through the registry seam; briefs 16 to 20 carry `assignments:` | not started; shapes decided below | pilot, WP-4 |
| H6 | The TASK is the increment on one package | ledger: one package's TASKs each with a `red_commit_receipt_emitted`, in one session | not started | pilot cuts, cheaper session flies, WP-7 |
| H7 | Every control names its contract | `gz validate --advisory-scorecard` reads an obligation column | not started | cheaper session, WP-8, GHI #1247 |
| H8 | The toggle is on the record | `.gzkit/mx.json` with `mode: safe`, bound to its event | met 2026-10-17: `mode: safe`, bound to `mx_session_opened` at 2026-10-17T08:36:59Z | done |
| H9 | 17 and 20 attested | `gz obpi status` shows `attested_completed` for both | `Draft`; disclosures recorded in the log | operator |

#### Drydock repairs (under safe mode; the pilot specifies and cuts, cheaper sessions execute)

| Repair | What is rebuilt | Witness |
|---|---|---|
| D1 | The ladder (ruled 2026-10-05): ADR records architecture decisions; the engineering order, the feature bundle, lands contracts on REQs for one bounded advance; the Release Package (its own rung, § The Release Package) governs a version; the work package replaces the OBPI as the labor unit; the TASK is the increment | the first release planned and closed through a Release Package, with `gz closeout` keyed to it; the `gz-release` skill of WP-12 (GHI #1248) measures the pressure and runs the ceremony |
| D2 | The catalog as the product's truth: every live REQ an entry with its contract and state; legacy ids as aliases | a `gz validate` scope that fails on a brief assignment naming no entry |
| D3 | GHIs classified by the contract they repair; MX visits likewise | `ghi-triage` reports the contract per issue; an unclassified issue is a finding |
| D4 | The control plane subtracted: every control names its contract or retires; no rule body carries a dated narrative; every surface an agent loads is within its budget, cut in stages and each stage measured before the next (WP-13 to WP-16) | the obligation column full; the counts below, read by the WP-13 witness |
| D5 | The airlock derives the slice from the contract's `modules` | a transit whose reach exceeds the contract's modules is refused |
| D6 | Eval checks module design against module code | one eval run on one package, reported |

**Drydock exit numbers** (executive decisions 2026-10-16, widened the same day to every loaded surface on the operator's ruling A; the operator may move any by a word; backup: tag `control-plane-baseline-2026-10-16`; baseline proof `.gzkit/chores/instructions-files-diet/proofs/baseline-2026-10-16-control-plane.txt`):

| Measure | Today | Exit |
|---|---|---|
| Per-turn load: AGENTS.md | 24,154 chars | at or under the ruled budget, 25,000 |
| Per-turn load: skill descriptions, all skills | 15,816 chars | at or under 6,000 chars |
| Per-turn load: rules, total and largest | 149,529 B over 26 files; `tests.md` 11,618 B | at or under 60 KB; no rule over 4,000 B |
| Skills in the catalogue | 73; bodies 639,408 B | at most 40; every skill either model-invoked with a one-sentence description or `disable-model-invocation: true`; every body under its `skill_contract` ceiling (WP-14) |
| On dispatch: agent definitions, `.claude/agents/` | 10,799 B over 5 | at or under 6 KB (WP-15) |
| In a subtree: nested `AGENTS.md`, repo side | 175,877 B over 17 files | at or under 60 KB in total (WP-15, after the rules cut) |
| On assignment: personas | 24,879 B | at or under 12 KB (WP-15) |
| Per turn: text the hooks inject | orientation 4,831 B plus the MX banner | at or under 4 KB per turn (WP-15) |
| Every number above | measured by hand (the proof file) | read by `gz validate --instructions-files-budget` from `data/instructions_files_budget.json` (WP-13); each cut stage carries its effectiveness report (WP-16) |
| Controls with no named contract | 189 scored, 0 assigned | 0 unassigned: each names its contract or is retired by a logged act |
| Operator attestations | one per OBPI | one per release, plus the sea trial |

#### The Release Package

Entrenched as a document type in `docs/governance/safe-mode-doctrine.md` § The Release Package with
the template `.gzkit/templates/release_package.md`. One document per version under `docs/design/releases/`, named by the version it governs.
Frontmatter: the version; `status` (`planned`, `in-flight`, `released`); the catalog entries whose
state advances, each with its from and to state; the work packages shipped; the lane and its gates;
the operator's attestation. Body: the intent of the version for the operator and for adopters, and
the one-open-defect assessment the constitution's policy 12 requires. `gz closeout` keys to it
(D1). The campaign sequences releases; a Release Package says what one release contains. ADRs stop
carrying a version at the migration; a patch release uses the same document with a short list.

#### The sea trial

The drydock's product is the first release, built and published through the first Release Package.
The trial: a fresh project installs that release from the wheel, `gz init` scaffolds it, and a
cheaper session takes one work package from the catalog, cuts its TASKs, lands each as one commit
with its trailer and its `red_commit_receipt` on the pipeline route; the operator attests the
package from two artifacts only, its entries' states and its TASK receipts. The constitution's
governor rule is the ground: doctrine under construction is proven on another project before it
binds its own making. A second substrate, if the operator names one, flies as a flight-test sortie.
Passed once and recorded here, the ship is seaworthy and the handback follows.

#### Executive decisions taken 2026-10-16 (the operator may overrule any by a word)

1. **WP-4 shapes, decided as recommended:** `REQ-C<n>` sequential ids, each entry in one
   first-class feature area (amended 2026-10-17, operator verbatim *"A, features are
   first-class requirement areas"*, overruling category as navigation metadata);
   one JSON file `data/requirements_catalog.json` read through the registry seam with a derived
   Markdown view; assignments in brief frontmatter with the legacy `REQ-X.Y.Z-NN-MM` line kept as
   the alias the proof channels bind to.
2. **The Release Package, confirmed by the operator** (§ The Release Package).
3. **The disclosures of the cutover row stand as recorded.** The pilot cannot attest; it proceeds
   on them and the operator rules at H9.
4. **Execution leaves the pilot.** Every leg marked "cheaper session" is a GHI with a closure
   contract written by the pilot; the pilot executes nothing deterministic from here.
5. **The drydock exit numbers above.**
6. **The control-plane cut, ruled A by the operator** (2026-10-16, verbatim *"A (in safe mode - make
   backups!!! - help me test how much we can cut and remain effective, I need to better balance
   context bloat)"*): one exit number per surface an agent loads; the backup is the pushed tag
   `control-plane-baseline-2026-10-16`; the cut proceeds in stages and no stage is accepted without
   WP-16's report (meaning retention, instruction eval, one work package flown on the cut surfaces);
   canon is reset against the trimmed state (operator, verbatim *"we can reset canon against the
   trimmed state"*) through `gz content retire` and `gz content land` with retention maps, never by
   editing a rendition. Harbor leg H4 (#1246) is stage 1.

#### Work packages added

- **WP-10 (GHI #1245).** The orientation prints this chart's readings while `.gzkit/mx.json` is in safe mode:
  each leg's witness run and its reading, so the path is read from the tree, never from memory.
- **WP-11 (GHI #1246).** The per-turn rules narrative lift and the skill-description cut (H4), measured
  before and after, nothing compressed in a binding clause.
<!-- gz-validate-skip: command-shape -->
- **WP-12 (GHI #1248).** The `gz-release` skill: `gz release pressure` measures pipeline pressure
  (GHIs closed since the last release by label, catalog entries verified and unreleased, work
  packages completed, the governor gap in commits, days since the last release) against thresholds
  in `data/release_pressure.json`, prints a draft Release Package and recommends `none`, `patch`
  or `minor`; on the operator's word it runs the ceremony and subsumes `gz-patch-release`, which
  retires from every surface root. Drydock D1's mechanism; the first Release Package is the
  drydock's own release.
- **WP-13 (GHI #1249).** A budget for every surface an agent loads in `data/instructions_files_budget.json`,
  read by `gz validate --instructions-files-budget`; lands before the cuts so each is read by the witness.
- **WP-14 (GHI #1250).** The skills catalogue merged to at most 40, one-sentence descriptions, bodies
  under ceiling; the merge plan put to the operator before the first deletion; staged.
- **WP-15 (GHI #1251).** Nested `AGENTS.md`, agent definitions, personas and injected hook text to
  budget, after the rules cut.
- **WP-16 (GHI #1252, pilot writes the protocol).** The effectiveness measure of each cut stage:
  retention maps and a compression-sweep read, `gz readiness evaluate` before and after, one work
  package flown by a fresh session on the cut surfaces; a report per stage under `docs/evals/`.

## Passage log

| Date | Act | Before | After | Commit | Witness |
|---|---|---|---|---|---|
| 2026-10-15 | orientation campaign block to pointers (GHI #1242, closed) | 19,431 B block; ~22,500 B orientation | 1,570 B block; 5,524 B orientation | `99acdc8a0` | `TestCampaignBlockIsBounded` (RED at 22,639 B); `gz arb red --commit 99acdc8a0` verdict `driven`, receipt `arb-red-commit-99acdc8a0433-4c5dabe3a61449cf82abc3b2343f282a` (a first run on the pre-amendment commit was `undriven` on 5 `_campaign_head` hunks; assertions added, commit re-cut); `gz check` passed |
| 2026-10-15 | pipeline control inventory: model, pure checker, skeleton pinned to the skill body (OBPI-0.35.0-17 first half; GHI #1174 closed into 17 and 20) | no inventory; skill body 125,414 B, 471 blocks, 0 mapped | checker in `src/gzkit/governance/pipeline_control_inventory.py`; `data/obpi_pipeline_control_inventory.json` with all 471 blocks verbatim, 0 controls mapped; body unchanged, sha256 `fe97fe31…8367` at `072317673` | `8306625ad` | 18 tests, RED on 10 assertions against the no-op skeleton; `gz arb red --commit 8306625ad` 35 killed, 0 survived, 11 declaration hunks `inconclusive` (receipt `arb-red-commit-8306625adac7-af02cd6c0d8049c894aa074f8c1af4b2`); `gz check` passed |
| 2026-10-15 | pipeline control inventory mapped, every block, by the pilot (operator: *"If you need to override to do lots of hand-authoring, that's part of what martial law means"*) | 0 of 471 blocks mapped | 471 of 471: 521 controls (invocation 49, stage1 80, stage2 131, stage3 84, stage4 212, stage5 93), 149 rationale quotes, 96 structure quotes; by characters controls 85,524, rationale 33,548, structure 4,014 of 125,923; body digest unchanged | `9451ed057`, `4f1b12be4`, `4f2c33b51`, `5850b4954`, `5f7ca2b63`, `6c403c912` | `check_before_state` returns no violation on the real tree; `test_committed_inventory_is_a_complete_partition` (19 tests pass); `gz arb red --commit 6c403c912` verdict `no-production-hunks` (data and test only, receipt `arb-red-commit-6c403c9129f2-c441cbac1e4f462abc8c06b01a60909e`); `gz check` passed. **Gate:** the operator attests the inventory before any text leaves the skill (brief 17, Q6); WP-3's lift then runs under `check_rationale_record` and `check_delivery` |
| 2026-10-15 | stage entry serves its procedure as a pinned file (OBPI-0.35.0-17 second half; operator attested the inventory: *"attest the inventory, keep going with the load cuts"*; rulings Q1 "A" and Q3 "A") | the 125,923 B skill body was the only text at every stage and nothing refused a stage on missing text | five served files generated from the attested inventory (stage1 18,146 B; stage2 27,419; stage3 19,310; stage4 55,289; stage5 22,243), pins in `src/gzkit/pipeline_procedure.py`; every launch resolves the stages it will visit before a marker is written and prints one path-plus-digest pointer per stage entry; a missing, unreadable, empty or altered file refuses with three-part prose; `--cli-alignment` and the skill code-citation audit walk the stage files; body unchanged, skill 6.68.0 | `fbe298c26` | 11 tests in `tests/test_pipeline_procedure.py`, 3 in `TestStageEntryServesProcedures`, 2 audit tests; `check_delivery` over the five served texts plus the invocation body returns no violation on the real tree; `gz arb red --commit fbe298c26` 18 killed, 0 survived, 13 declaration hunks `inconclusive` (receipt `arb-red-commit-fbe298c26d10-84c5fe762c144b49b95d61d8d95f8d6b`; a first run on the pre-amendment commit was `undriven` on 6 hunks: the Stage 3 and Stage 5 pointer prints, both audit widenings, the unreadable branch and the seeder's return; assertions added, commit re-cut); `gz check` passed. **Bytes at invoke are not yet cut:** the body still loads at invocation and each stage now adds its file; the cut is brief 20's cutover, which this step makes checkable |
| 2026-10-15 | pipeline skill cut over to the invocation text: stage procedures and the rationale record rendered from the attested inventory (OBPI-0.35.0-20, executed by the pilot under § Mandate 1 and 5; nothing compressed, per the Q5 ruling) | skill file 125,923 B loaded at invocation and at every stage; under brief 17 each stage entry added its file on top (Stage 4: 181,212 B) | skill file 11,445 B (238 body lines, under the 300-line contract; grandfather entry removed); stage files 15,408 / 24,869 / 16,566 / 44,166 / 18,009 B; at Stage 4 entry 55,611 B, at Stage 2 entry 36,314 B; rationale record 59,315 B under `docs/governance/`, loaded by no turn | `d47de23c8` | renderer `src/gzkit/governance/pipeline_procedure_render.py` with 20 tests (RED on import, then on each edge); on the real tree `check_delivery`, `check_placement`, `check_stage_placement` and `check_rationale_record` return no violation and the committed stage files equal the render; 5 behave scenarios (brief 17's Gate 4) pass; `gz check` passed; `gz arb red --commit d47de23c8` 55 killed, 0 survived, 36 `inconclusive` (declaration hunks and reverts that error rather than assert; receipt `arb-red-commit-d47de23c85a4-549c116e40744850a9a4faebb5f53435`). A first run on the pre-rewrite commit was `undriven` on 14 hunks: the behave step module (the witness counted `features/` as production) and 13 renderer guards; the guards gained tests or were removed as unreachable, and the step-module blind spot is the fix below. **Disclosed for the operator's attestation of 17 and 20:** (a) the pilot ran the cutover outside the OBPI pipeline and before brief 17's ledger completion, against brief 20 Requirements 2 and 10, under the ratified contract; (b) the renderer and its test module are outside brief 20's Allowed Paths; (c) one non-control row of the attested inventory was reclassified from `rationale` to `structure`, the Stage 1→2 block's citation of invariant 11, because attested REQ-0.0.19-04-06 (GHI #1025 ruling) requires the block to keep it; no control row changed and the baseline is untouched; (d) a `git reset --hard` taken to re-cut the commit discarded two uncommitted red receipts for SHAs the rewrite retired; both witnesses were re-run and the slip is an insight record |
| 2026-10-15 | commit witness: a behave step module is test code, not a production hunk (direct repair, in flight) | every `.py` outside `tests/` was a production hunk, so a commit carrying its Gate 4 scenarios read `undriven` whatever its guards did | `features/` is neither production nor a unit-test module to the witness; the manpage states the rule | `4e424fa2b` | 2 tests RED first (`TestBehaveStepsAreTestCode`); `gz check` passed; `gz arb red --commit 4e424fa2b` verdict `driven` (receipt `arb-red-commit-4e424fa2ba52-e16390a735604a49b1a20778b5702db5`) |
| 2026-10-16 | full unit tier repaired after the cutover (direct repair, in flight; found by the `instructions-files-diet` chore's advise step, which runs `gz test`) | `gz test` exit 2: the acceptance-integration fixture called a stage runner with no served procedure, and the import-boundary policy refused two private cross-package imports the inventory had taken from the retention module | 11,889 tests, exit 0; the fixture seeds the stage procedures; the retention module gains a public seam (`meaningful_positions`) and the inventory reads covered characters through it | `31576beba` | 3 tests RED first; `gz check` passed; `gz arb red --commit 31576beba` 1 killed, 0 survived, 2 `inconclusive` (an import line and a return whose reverts error rather than assert; receipt `arb-red-commit-31576bebaaff-4495eeba83814abc9cba7d2373ade2d9`). A first cut was `undriven` on the inventory's two hunks because the commit touched no inventory test; re-cut with a semantic test that pins the uncovered detail the seam yields. **Finding:** the per-change gate ran green on every cutover commit because it runs only the tests a change touches; the two breakages were in modules the change did not touch and surfaced only in the full tier |
| 2026-10-16 | WP-2 opened: `instructions-files-diet` steps 1 to 3 run and stopped at § 4 (GHI #1243) | AGENTS.md 24,154 chars against a 20,000-char budget; nothing measured | the delivered rendition is 22,599 B invariant text over 101 live entries, 876 B compressible over 4 (all Judgment, three of them one-line pointers), 804 B structure; required delta 4,154; the gap exceeds the compressible budget (§ When to stop and ask, state 2); no edit made | `5c6e9a493` | `proofs/baseline-2026-10-15.txt`, `proofs/recommendation-2026-10-15.md`, `proofs/CHORE-LOG.md`; three options put to the operator in GHI #1243: A the budget recorded at the invariant floor plus margin (25,000) with a dated history entry, B operator re-tiering of named canon, C per-consumer delivery; the chore's step 1 command validated a stale on-disk candidate rather than rendering the corpus, noted in the log. Per-turn load outside the budget: `.claude/rules/*.md` 150 KB in 26 files and 15,085 chars of skill descriptions over 73 skills |
| 2026-10-16 | safe mode, built as a mode of the MX hangar (GHI #1244; operator ruling verbatim *"A, extend gz mx with a safe mode - which is 'martial law' toggle"*) | martial law existed only as this contract: no marker, no per-turn banner, no ledger anchor, no exit gate; the hangar demoted guards and knew no mode | `gz mx enter --mode safe --contract <path>` opens the marker in safe mode: the marker and the `mx_session_opened` event carry `mode` and `contract`; the banner and the orientation name them each turn; `checkpoint.hangar_demotes` is true only under `mode: mx`, so every guard stays at full strength; a missing or outside contract, or a contract under the hangar, is refused; `gz mx exit` closes either mode through the same hard gate; rule 1.5.0 with § Safe mode (Coverage Ledger row 62f, Promotable), skill 1.2.0 with its flags corrected, manpages updated | `ac3b0005e` | 9 tests RED first across marker, checkpoint, awareness and enter, then 12 more to drive every hunk; `gz check` passed; `gz cli audit` passed; `gz arb red --commit ac3b0005e` 18 killed, 0 survived, 17 `inconclusive` (declaration hunks and reverts that error rather than assert; receipt `arb-red-commit-ac3b0005e9f0-0c3a60a8eb8047b9a5d3d80e03896fc4`). Three earlier cuts were `undriven` (13, then 2, then 1 hunks: the hook mirror and template, the parser flags, the typed event, the enter and exit labels, an unreachable assert that was removed, and two guards whose refusal message no test read); each re-cut before pushing. **Next:** the operator enters the present pilotage through the verb so the ledger carries the toggle: `uv run gz mx enter --mode safe --contract docs/governance/harbor-pilotage-candidate-2026-10-15.md --reason "harbor pilotage" --attestor g0` |
| 2026-10-16 | WP-2 closed by ruling (GHI #1243, operator verbatim *"A, record the budget at the invariant floor"*) | AGENTS.md 24,154 chars against a 20,000-char budget; the chore stopped at § 4 because 876 B of compressible text could not close a 4,154-char gap | the enforced budget is 25,000 chars, the attested invariant floor (22,599 B) plus margin, with a dated entry in `docs/governance/instructions-files-budget-history.md`; the doctrine page says the enforced value sits above the 20,000 ceiling, which is destination work again; options B and C recorded as declined; `gz validate --instructions-files-budget` exits 0 with no advisory; 846 chars of headroom | `e0dab8ee4` | data and docs only: `gz arb red --commit e0dab8ee4` verdict `no-production-hunks` (receipt `arb-red-commit-e0dab8ee443c-860c9d481d8649469a524129803afc2b`); `gz check` and `mkdocs build --strict` green (the strict build caught a lifted version-history link from the safe-mode commit, repaired here); GHI #1243 closed `fixed`. Exit condition 2 is met by ruling, not by trimming |
| 2026-10-16 | pilotage chart written: harbor legs H1 to H10 with witnesses and readings, drydock repairs D1 to D6 with seaworthiness witnesses, the sea trial, four executive decisions (WP-4 shapes, the release artifact as its own rung, the disclosures stand, execution leaves the pilot), WP-10 and WP-11 added | the path existed as seven exit conditions and a passage log; no instrument read the legs | § Pilotage chart; readings move only by a logged act | this commit | the operator's word of 2026-10-16 (*"lean in and make executive decisions"*); nothing executed |
| 2026-10-16 | entry and exit made skill-driven (operator correction, verbatim *"these need to be skill driven: 'gz mx exit'"*) | the chart and the handoff handed the operator raw `gz mx enter` and `gz mx exit` commands; the skill carried only the hangar | gz-mx skill 1.3.0 carries the safe-mode workflow: confirm the contract, enter, work under § Records, read the chart, exit through the hard gate, hand back; the chart's H8 and the quay name the skill | this commit | `gz skill audit` and `gz validate --cli-alignment` green after `gz agent sync control-surfaces`; insight recorded |
| 2026-10-16 | the chart amended to one exceptional period (operator, verbatim *"confirm all three, amend the chart"*): safe mode runs through the drydock and the sea trial and ends at seaworthiness; the sea trial is a fresh project on the released wheel; the Release Package is its own rung with the shape in § The Release Package | the chart had put the drydock under civil rule and the exit at the harbor's quay | § The regime, § Drydock repairs with exit numbers, § The Release Package, § The sea trial; H10 folded into the handback phase; WO and WP distinguished (WO a pilotage instrument of 2026-10-15, WP the ruled civil-rule unit of 2026-10-05) | this commit | nothing executed; insight recorded |
| 2026-10-16 | the metaphor entrenched in canon (operator, verbatim *"keep these metaphor entrenched in canon, this won't be the last time we need to reach for this approach"*) | the regime lived in this contract only | `docs/governance/safe-mode-doctrine.md` (the doctrine: when declared, the metaphor and why it holds, the one-period regime, the six instruments, what is never suspended, entry and exit, lineage); `.gzkit/templates/safe_mode_contract.md`; the ratified glossary gains the terms; `mx-mode.md` 1.5.1 and `gz-mx` 1.3.1 point at both; one corpus entry captured for AGENTS.md § Governance doctrine surfaces (rendering awaits the operator's corpus attestation) | this commit | `mkdocs build --strict`, `gz skill audit`, `gz validate --distribution --advisory-scorecard` green |
| 2026-10-16 | the entrenchment completed to the operator's meaning (verbatim: *"i meant these"*, the chart's specifics): the standard harbor legs H1 to H9 and drydock repairs D1 to D6 with their witnesses, the standing exit measures, the Release Package as a document type with its template, and the sea trial as a five-step procedure | the doctrine carried the regime and the instruments only | `safe-mode-doctrine.md` § The standard chart, § The Release Package, § The sea trial; `.gzkit/templates/release_package.md`; the contract template's chart pre-filled with the standard set; the glossary gains *Release Package* | this commit | `mkdocs build --strict`, `gz validate --distribution` (regenerated), `tests.test_templates` green |
| 2026-10-16 | the work order retired; the work package everywhere (operator, verbatim *"retire it, work package everywhere - change now: 'WO-1 to WO-11' to WP"*) | two names for one labor unit: WO under the pilotage (keyed to a GHI), WP under civil rule (keyed to catalog entries) | one unit, the work package, keyed to a GHI until the catalog lands and to entries after; the GHI is the tasking order's carrier; WP-1 to WP-11 keep their numbers and GHIs (#1242, #1243, #1244, #1245, #1246, #1247; the issue titles stay as filed, `gh issue edit` is outside the allowed commands) | this commit | the doctrine, both templates, the glossary and this contract renamed; the operator-verbatim canon "the GHI is the work order and the receipt" (direct repair) and every dated record are untouched; `mkdocs build --strict` and `gz check` green |
| 2026-10-16 | the release management document type named the Release Package and WP-12 written (operator, verbatim *"Release Package it is, rename and write WP-12"*) | the type was called the release plan; no mechanism measured whether a release was due | one document type with its lifecycle in `status`; the vocabulary runs work package, Release Package, release; renamed across the doctrine, both templates (`.gzkit/templates/release_package.md`), the glossary and this contract; WP-12 filed as GHI #1248 with its closure contract: its planned verb, gz release pressure (unlanded), reads the ledger, the tags and the catalog against `data/release_pressure.json`, recommends, and the skill runs the ceremony, subsuming `gz-patch-release` | this commit | `mkdocs build --strict`, `gz validate --distribution` (regenerated) and `gz check` green; nothing executed |
| 2026-10-16 | safe mode is the sole term (operator, verbatim *"safe mode is the sole term, update the canon"*) | two names for one regime | every authored surface says safe mode: the doctrine's title and terms, the rule heading (1.5.2) and scorecard row 62f, the skill (1.3.2), the banner, the enter and exit labels, the parser help, the manpages, the templates, the glossary and the AGENTS.md corpus entry; "martial law" survives only inside the operator's quoted words | this commit | tests updated; `gz check` green |
| 2026-10-16 | sync pass order repaired: the package copy of `.gzkit/skills/<slug>/` ran before the nested `AGENTS.md` pass, so the wheel copy of a skill-scoped `AGENTS.md` lagged one sync behind canon (found while renaming the safe-mode heading; `src/gzkit/skills/gz-mx/AGENTS.md` still read the old heading after a sync) | one stale derived view in the wheel | `sync_pkg_surfaces` runs downstream of `sync_nested_agents_md`, as the skill mirrors already do; one sync delivers the nested file to the package side | this commit | `tests/test_sync.py::test_the_package_copy_of_a_skill_carries_its_nested_agents_md_in_one_sync`, red then green; 376 sync-suite tests green |
| 2026-10-16 | the control-plane cut booked (operator: *"where in this safe-mode drydock plan will you aggressively trim all control plane artifacts (agents, rules, skills and any other items that an agent loads and saturates context)?"*, then *"A (in safe mode - make backups!!! - help me test how much we can cut and remain effective, I need to better balance context bloat)"*) | the chart carried exit numbers for two of seven loaded surfaces; the skill count was "reported, not targeted" | backup tag `control-plane-baseline-2026-10-16` pushed; baseline proof written; D4, the exit table, the regime row and the doctrine's standing measures widened to every loaded surface; executive decision 6; WP-13 #1249, WP-14 #1250, WP-15 #1251, WP-16 #1252 filed with closure contracts | this commit | measured: rules 149,529 B/26, descriptions 15,816 chars, bodies 639,408 B/73, agents 10,799 B/5, nested AGENTS.md 175,877 B/17, personas 24,879 B, hooks 17 |
| 2026-10-17 | H8: safe mode entered through the gz-mx skill under this contract (operator, verbatim *"proceed with H8, invoke /gz-mx"*) | the regime lived in this contract only; `.gzkit/mx.json` absent; no `mx_session_opened` event carried `mode: safe` | `.gzkit/mx.json` with `mode: safe` and `contract` naming this file; `mx_session_opened` (session `696ca9a4-7b6b-4d3a-8611-0da2766bf075`, ts 2026-10-17T08:36:59Z, attestor `g0`) in the ledger; every guard at full strength | this commit | the marker and the ledger row; the skill confirmed § Entry, § Mandate, § Records and § Exit with the chart before entry |
| 2026-10-17 | H9, first half: the cutover disclosures ruled and the coupled consumer recorded (operator, verbatim *"accept all four disclosures, A for the coupled consumer"*) | disclosures (a) to (d) of the `d47de23c8` row unruled; `features/steps/acceptance_recovery_steps.py`, edited in `f88ea9a7e`, outside OBPI-0.35.0-17's Allowed Paths | brief 17: the file is in the frontmatter `allowlist:` and § Allowed Paths as a coupled consumer (DO IT RIGHT 1a), with a Change Log entry citing the ruling; brief 20: a Change Log entry accepting (a) to (d) as recorded; the ruling is an insight record (scope `harbor-pilotage-h9`). Attestation of 17 and 20 still awaits the operator's words | this commit | `gz obpi brief-drift OBPI-0.35.0-17` and `OBPI-0.35.0-20` both clean (all five deltas 0) after the edits; `gz obpi brief-drift --apply` adds only `src/` modules, so the amendment was hand-made under safe mode's brief-ceremony suspension |
| 2026-10-17 | the ladder restored to canon, and features made first-class requirement areas (operator, verbatim *"A, features are first-class requirement areas (will this bdd align?)"*, after *"I thought this was all settled?"*) | § Entry and D1 gave the ADR the role of landing contracts and named no engineering order, against the 2026-10-05 ladder ruling and Q-18; executive decision 1 made the REQ's category navigation metadata | § Entry and D1 carry the 2026-10-05 ladder: catalog governs REQs (Q-17, Magna Carta §3 of 2026-09-25), the engineering order lands contracts for one bounded advance, ADR for architecture decisions only; WP-4 shape 1 and executive decision 1 name one first-class feature area per entry, held in a registry beside the catalog, ids unchanged on a move | this commit | insight records `harbor-pilotage-wp4` and `campaign-ladder-drift`; the doctrine page's standard chart is amended in the same commit |
| 2026-10-17 | the joined requirements model written into canon (operator, verbatim *"A, write it into canon"*, after *"i want the feature files and steps AND the REQ system. think of functional and non-functional requirements"*) | every direction booked (Q-16 to Q-18, the 2026-10-05 ladder, the Release Package) with no record joining them; the PRD's FR/NFR split and the 79 Gherkin feature files placed nowhere | `ieee/design-candidates.md` § The joined requirements model: PRD, typed feature areas, catalog REQs, feature files and steps, non-functional proof, engineering order, ADR, work package and task cards, Release Package; the BDD alignment check; five open points; `OPEN-QUESTIONS.md` Q-19; WP-4 waits on ratification | this commit | `mkdocs build --strict` |
| 2026-10-17 | RO-0, first act: the contract rewritten to the ratified drydock plan (operator rulings of the day, § Rulings of 2026-10-17: structure not population; safe mode an occasional flip in the standing maintenance mode; the ADR a peer of the catalog, not a layer above the work; no engineering order; R1 to R6 ruled A) | the chart: harbor legs H1 to H9, drydock repairs D1 to D6, exit numbers, a sea trial as the exit, Mandate 2 to 4 populating the catalog; the drawing existed only as prose | § Purpose, § The general arrangement with `general-arrangement-2026-10-17.svg` verified from first principles, § Repair orders RO-0 to RO-8, § Exit as structural conditions, § Rulings of 2026-10-17; the old text kept under § Superseded; `safe-mode-doctrine.md` and `.gzkit/templates/safe_mode_contract.md` rewritten to the same shape; the 2026-10-17 drift (Q-19, the joined requirements model) kept as civil-rule design input with no work tie | this commit | `mkdocs build --strict`; `gz validate --distribution` after the control-surface sync; the guard lowering (R6) is RO-0's second act and is not yet in force |
| 2026-10-17 | RO-0, second act: safe mode lowers every guard outside the floor to advisory while its marker is open, as the hangar does (R6, ruled A); the pipeline gate honors the marker (it had blocked this act's own test edit, knowing nothing of the marker) | `gzkit.mx.checkpoint.hangar_demotes` true only under `mode: mx`; the pipeline gate ignored the marker; the banner said every guard runs at full strength | `hangar_demotes` true under either mode, `GATE5_INVARIANTS` pinned CRITICAL in both; the pipeline-gate template consults the checkpoint and exits 0 with the demote notice under an open marker; the banner and its stdlib fallback say most guards advisory; rule `mx-mode.md` 1.6.0, skill `gz-mx` 1.5.0, both manpages, this contract's § What is suspended | this commit | red first: `TestSafeMode` (2) and `TestSafeModeBannerStatesTheDemotion` failed on the old code; green: 106 tests across `tests.mx.test_checkpoint`, `tests.hooks.test_mx_awareness`, `tests.test_hooks` plus the seam, hardening, enter and exit suites; the `gz arb red --commit` receipt is cited in the session handoff |
| 2026-10-17 | RO-0, witness repair: the second act's `gz arb red --commit 1cd6cf841` read `undriven` on two hunks, the generated `pipeline-gate.py` and the `mx-awareness` template, because each generated hook and its template counted as separate hunks with tests on one side only (receipt `arb-red-commit-1cd6cf8414f2-e6240092c58c40c1a6895bf4502cb401`: 4 killed, 2 survived) | no parity check between a committed hook and its template | `tests/test_hooks.py::TestCommittedHooksMatchTheirTemplates` compares both hooks with a fresh render as syntax trees; both sides are driven from this commit on. The 1cd6cf841 receipt stands as a record; it was pushed before the witness ran, so it was not re-cut | `db9354c7a` | 84 hooks tests green; `gz arb red --commit db9354c7a` verdict `no-production-hunks` (receipt `arb-red-commit-db9354c7ad36-46029abd57df47c7929dfe55c7690d0b`) |
| 2026-10-17 | RO-1 act (a): session-start text on one channel, under 4 KB (operator ruling, choosing *"Orientation only (Recommended)"*; insight scope `drydock-ro1a`) | Claude session start 9,848 B: orientation 6,362 B (over Codex's 6,000-char `additionalContextLimit`, so truncated there) plus the handoff advisement 1,743 B delivered twice (`additionalContext` and `initialUserMessage`), and the orientation's own handoff, account and bookmark sections repeating it; the MX banner in both the orientation and the per-turn hook; the advisement named the handoff by an absolute path carrying the host account name | 3,974 B on one hook: the orientation's handoff section hosts the advisement (every advised step, the lineage, the count warning, the ruling verb); the advisement hook is not registered where `scripts/session_orientation.py` exists (Claude settings, hooks dir, Codex sync), and elsewhere speaks on `additionalContext` only; the 24h ledger summary, the always-empty blockers section and the orientation's banner copy removed; campaign, account, bookmark, chore and skill notes compressed to pointers; the handoff path project-relative; `gz readiness evaluate` 10 of 10 PASS before and after | this commit | 8 new tests RED first (orientation budget, steps and ruling verb, no banner, no ledger window; Claude registration, sync removal, one-channel adapter; Codex sync and adapter), plus the relative-path test; a first `gz arb red --commit` on the pre-amendment commit (`422b8a4c3`, receipt `arb-red-commit-422b8a4c3350-f3e2d7fbe24f4a40988b8e0065b70ffd`) was `undriven` on 27 hunks, and a second (`cd718eed2`) on 4; the budget fixture was sized to the measured boot so each prose cut is load-bearing, the collector, wiring, relative-path fallback, warning separation, sync writer and generated README gained assertions, and three cosmetic hunks and one no-op were reverted; the drift check's blindness to SessionStart and SessionEnd is an insight record; `gz check` passed; the final receipt is cited in the session handoff. Variable sections (advised steps, the account's commit list) can still exceed the budget; act (f)'s witness measures it |
| 2026-10-17 | RO-1 act (b): the dead instruction-router hook removed with its settings entry (operator, verbatim *"proceed with RO-1 act (b)"*) | `instruction-router.py` (6,167 B) registered on every Write, Edit and NotebookEdit, one of 4 hooks there: one `uv run` start (measured 36 ms) and 0 B of output per call, because it reads `.github/instructions/`, which nothing renders since GHI #924, while Claude loads the same rules natively from `.claude/rules/` (ADR-0.14.0); generated for every adopter; 12 gzkit commands across PreToolUse, PostToolUse and Stop | 3 hooks on Write/Edit/NotebookEdit, 11 commands; the generator, its template and the README entry gone; a sync deletes the router an earlier sync wrote (`_RETIRED_HOOKS`), leaving a project's own hooks alone; the pool ADR's row 4 marked moot; the `gz init` manpage example re-captured from a real run (the hook line, and the chore, template and rule counts and the pre-commit line, which had drifted) | this commit | 2 tests RED first (`TestInstructionRouterIsRetired`), the pinned settings, tranche, count and import-boundary fixtures updated; `gz check`, `mkdocs build --strict` and `gz validate --distribution` passed; the `gz arb red --commit` receipt is cited in the session handoff |
| 2026-10-17 | RO-1 act (c): skill descriptions to one sentence, under 6,000 chars (operator, verbatim *"proceed with RO-1 act (c)"*; canon already rules it, `.gzkit/rules/skill-authoring.md`: one line that says when to reach for the skill and what it produces) | 13,229 chars over the 62 model-invocable skills (YAML-measured; gzkit's own parser read 12,343 because it takes a block-scalar or continued description as its first line: `gz-airlock` and `gz-mx` measured 1 char, `>`), many of several sentences; `gz-deps-upgrade`'s frontmatter not valid YAML; routing read 122/124 goals, 6/10 "none" correct | 5,938 chars, every description one plain-line sentence, all 73 frontmatters valid YAML; each of the 62 skills patch-bumped with `last_reviewed` moved; routing read 122/124, 7/10 "none" correct. The first draft (5,879) routed 120/124, losing `gz-airlock`'s "seam map" and "disturbed" and `gz-plan`'s "pool ADR"; those words were restored before landing. No skill was made `disable-model-invocation` (that choice is the operator's) | this commit | WP-16 read: `.gzkit/chores/skill-trigger-testing/proofs/routing-2026-10-17-report.md` with its inputs and picks (134-goal basket of 2026-10-10, one blind sonnet pass per set, sample size 1); `gz check`, `gz skill audit` and the 267-test skill, sync, router and how-coverage suites green; the parser defect is an insight record for act (f); the `gz arb red --commit` receipt is cited in the session handoff |
| 2026-10-17 | RO-1 act (d): rule version banners lifted to rule-version-history with their scorecard rows (operator, verbatim *"proceed with RO-1 act (d)"*; `skill-surface-sync.md` § Non-negotiable rules #2 already asks for a one-sentence rationale) | 25 of 27 rules carried a multi-sentence banner, 10,076 B of them (10,707 B over all 27), loaded every turn the rule applies; rules total 161,070 B; nothing checked the banner's shape; the Coverage Ledger held `mx-mode.md` at `1.5.2` while the rule stood at `1.6.0` since RO-0, and row 62f still described safe mode as non-demoting, a drift `--advisory-scorecard` reported but safe mode demoted to advisory | each lifted banner verbatim under a dated `Lifted 2026-10-17` entry in its `rule-version-history.md` section (one new section, `skill-authoring.md`), its links rewritten to resolve from `docs/`; each rule a one-sentence banner pointing there, patch-bumped in marker and banner, its Coverage Ledger row moved with it; 4,340 B for the 25 banners; rules total 154,985 B; `--rule-version-markers` reports `banner-not-one-sentence` so the banners cannot regrow; row 62f re-scored to R6 and `mx-mode.md` set to `1.6.1` | this commit | 1 test RED first (`test_a_banner_of_more_than_one_sentence_is_reported`), plus the code-span negative control (a first `gz arb red --commit` on `38536e755`, receipt `arb-red-commit-38536e75516e-08fbe65d1daa46b39f79c8d97093c9fd`, was `undriven` on the counter's line-joining and link-stripping, neither of which any fixture needed, and a second, on `8ec4881fb` (receipt `arb-red-commit-8ec4881fbc2f-d90b3344aad84d06839ffb993762aad0`), on a no-banner guard the call site made unreachable; all three removed, the count now starting at the matched quote, and the commit re-cut); read directly, since safe mode demotes their exit codes: `audit_advisory_scorecard` 1 error before (the `mx-mode.md` drift) and 0 after, `validate_bullet_retention` 0 errors, `audit_rule_version_markers` 25 violations before the lift and 0 after; `mkdocs build --strict` (which caught the rule-relative links on the first lift) and `gz check` passed; `gz readiness evaluate` 10 of 10; the `gz arb red --commit` receipt is cited in the session handoff |
| 2026-10-18 | RO-1 act (e): the governance read mandate pointed at the Coverage Ledger section (operator ruling, choosing *"A: Ledger + scoped (Rec.)"*; insight scope `drydock-ro1e`) | AGENTS.md § Governance doctrine surfaces had every governance-code, rule or audit task read three whole documents before starting: `trust-doctrine.md` 18,082 B, `advisory-rules-audit.md` 208,766 B and `state-doctrine.md` 10,434 B (237,282 B; with the constitution entry, unchanged, 264,552 B); AGENTS.md 24,629 B | the mandate reads the Coverage Ledger section (3,413 B) and the touched rule's scorecard rows, `trust-doctrine.md` when the change moves a witness or gate, `state-doctrine.md` when it moves state between layers; AGENTS.md 24,785 B (+156 B, 215 B under its 25,000 budget); the constitution entry unchanged | this commit | invariant entry `corpus-governance-doctrine-surfaces-2026-09-18T01:52:09` retired (attestor g0) and its successor captured (`gz content remember`, tier invariant); landed through `gz content land` under the operator's words with the dropped condition ids appended; retention map `.gzkit/chores/instructions-files-diet/proofs/retention-map-2026-10-18-ro1e.json`, conditions extracted by an independent spec-reviewer (8 conditions: C1 to C4 kept verbatim, C5 to C8 dropped as unconditional reads narrowed to scoped ones); `gz check` passed; the `gz arb red --commit` receipt is cited in the session handoff |
| 2026-10-18 | RO-1 act (f): the budget witness extended to every loaded surface (GHI #1249; operator, verbatim *"keep safemode open keep going with drydock"*, then on how the hook text is measured *"A: the orientation reads its budget from the JSON and checks itself at render; the validator measures the MX banner. Proceed with act (f)."*; insight scope `drydock-ro1f`) | `gz validate --instructions-files-budget` read three surfaces: `AGENTS.md` 25,000, `CLAUDE.md` 15,000 and each rule file 30,000 chars, a per-file cap no rule reached, and no total anywhere; every other number in the drydock exit table was measured by hand in the baseline proof; the orientation's 4,000-B budget was a literal in its test | `data/instructions_files_budget.json` carries `totals` at the exit numbers (rules 60,000 B, skill descriptions 6,000 chars over the skills that load, read by a YAML parse, agent definitions 6,000 B, nested `AGENTS.md` 60,000 B with the vendor and wheel mirrors excluded, personas 12,000 B), `injected_hook_text` 4,000 B, and the per-file rules cap at 4,000; every total is printed on each run and an overrun is an advisory, under the stay; the witness measures the MX banner (307 B), and the orientation reads the budget and appends a warning to its own output when over; an unparseable skill frontmatter is an advisory, never a traceback. Measured at landing: rules 144,097 B (20 files over 4,000), descriptions 5,938 chars, agents 10,799 B, nested `AGENTS.md` 198,627 B over 22, personas 24,879 B, orientation 3,996 B | this commit | 9 tests RED first in `tests/governance/test_audit_instructions_files_budget.py` and 8 in `tests/scripts/test_session_orientation.py` (7 new, plus the measured-boot test now reading the budget file), the frontmatter test RED on a raw `ScannerError`; a first `gz arb red --commit` on `8bf300788` (receipt `arb-red-commit-8bf3007882ec-1c5a8fdc8df945d4a253151d3a489af7`) was `undriven` on the unterminated-frontmatter guard, which no fixture reached, so a test now holds it and the commit was re-cut; the witness run on a worktree at tag `control-plane-baseline-2026-10-16` re-measures rules, agents and personas to the byte, while descriptions (12,976 chars over the skills that load, against the proof's 15,816 over all 73) and nested `AGENTS.md` (206,536 B over 22, against 175,877 B over 17) differ by population, recorded in `docs/governance/instructions-files-budget-history.md` § 2026-10-18; manpage, Coverage Ledger config row and `agent-contract-rationale.md` (which still said fail-closed) moved with it; root `AGENTS.md`'s budget bullet still names only the per-file budgets, true but incomplete, and moves only by an operator ruling through the corpus; `gz check` passed; the `gz arb red --commit` receipt is cited in the session handoff |
