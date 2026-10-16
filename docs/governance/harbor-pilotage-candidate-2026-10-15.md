# Martial law to civil rule — the harbor pilotage contract

Status: **RATIFIED 2026-10-15** (operator, verbatim: *"ratify the contract, draft the three
catalog shapes"*). Drafted the same day in session `4fd13b45-724e-4433-ab23-fd6c5df2b932`.
This file is the binding text; the campaign plan carries a pointer entry at
[`build-to-1.0-campaign-2026-09-20.md`](build-to-1.0-campaign-2026-09-20.md)
§ Amendments 2026-10-15 so that the plan, which the orientation and every session read for
sequencing, knows the phase is in force and where its terms are.

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
  operator. It writes this contract, the work packages, the candidate canon and the catalog's
  first entries. It executes a cut itself only when the cut is the measurement's own
  finding and small enough to read in one sitting; it does not do all the work.
- **Cheaper sessions** execute the work packages under § Records, each a GHI-cited change
  with mechanical witnesses. A work package carries no structural decision.
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

## Work packages

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
- **WP-5.** `extract_plan_tasks` stops dispatching rejected alternatives; interim until
  the dispatch unit is the TASK.
- **WP-6.** One tracker for the 27 helper-or-loop gates of the 2026-10-14 sweep.
- **WP-7 (pilot).** The re-cut of 16 to 20 as work packages by contract, with the TASK as
  increment and the commit-grain witness on the pipeline route; the three re-cut decisions
  put to the operator with the cut.
- **WP-8.** The obligation column on the advisory scorecard. GHI #1247 (filed 2026-10-16).

Not work packages under martial law: the identifier ladder's timing, the crew split's final
shape, the second-substrate sortie, the Matrix's replacement text. These are civil-rule
decisions this pilotage prepares.

Booked for civil rule on 2026-10-16, from the operator's words that day:

- **The release artifact.** Verbatim: *"adrs are not releases, i am surprised you
  recommend this."* An ADR records a decision and lands contracts on REQs; a separate
  release artifact says which REQ states advance in a version and which work packages ship,
  and carries the closeout that is the release today. The pilot's recommendation to reshape
  the feature ADR into the release plan is withdrawn; the feature ADR's semver and `gz
  closeout`'s "a feature/minor closeout is a release" are the conflation the migration
  retires.
- **Safe mode.** Verbatim: *"we need a 'safe mode' that allows this sort of unencumbered
  'martial law' as a toggle."* This contract is a hand-written instance of it. The nearest
  existing toggle is the MX hangar (`gz mx enter`, `.gzkit/mx.json`, `.gzkit/rules/mx-mode.md`),
  which demotes guards to advisory while the Gate 5 invariants, the ledger and the PRIME
  DIRECTIVE still bind; safe mode differs in what it suspends (initiation and brief ceremony,
  not guards) and in carrying a contract: entry, mandate, records, exit.

### WP-4 draft — the three catalog shapes (drafted 2026-10-15, for ruling)

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
  "category": "pipeline runtime",
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

`id` is a sequential integer under a `REQ-C` prefix and is never reused; `category` is
navigation metadata, so moving an entry between categories changes no identity. `state` is
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

## Pilotage chart — one exceptional period: harbor, drydock, sea trial, handback (amended 2026-10-16)

Written under crisis mode at the operator's word (verbatim: *"lean in and make executive decisions
to achieve outcomes"*; *"gzkit has become untenable"*). Amended the same day on three
confirmations, verbatim *"confirm all three, amend the chart"*: safe mode runs through the drydock
and the sea trial and ends at seaworthiness; the sea trial substrate is a fresh project on the
released wheel; the release plan has the shape in § The release plan. The chart is the tracking
instrument: one row per leg, each with its witness and its last reading. The passage log records
each act; a leg's reading moves only by an act in that log. WP-10 (GHI #1245) makes the readings
mechanical.

### The regime

| Phase | Regime | Produces | Done when |
|---|---|---|---|
| Harbor | safe mode | load cut, inventory, serving, the toggle, the budget | H1 to H9 met |
| Drydock | safe mode | the catalog, the release plan type, work packages for 16 to 20, controls naming their contracts, the ladder migrated, the first release | the first release built and published through a release plan, with the drydock exit numbers met |
| Sea trial | safe mode | a fresh project on the released wheel runs one work package end to end | the trial recorded in the passage log |
| Handback | ratification | the amendment: every pilot commit kept or reverted, the passage log carried, the initiation clause restored | the operator's word; `/gz-mx` exits through the hard gate |
| Voyage | Magna Carta | releases planned, packaged, witnessed, attested | ordinary operations |

Safe mode is left once, at seaworthiness. Nothing returns to civil rule in between.

### Harbor legs

| Leg | What it means | Witness | Reading 2026-10-16 | Owner |
|---|---|---|---|---|
| H1 | Session start bounded | `TestCampaignBlockIsBounded`; orientation under 8 KB | met, 4,831 B | done |
| H2 | AGENTS.md within budget | `gz validate --instructions-files-budget`, no advisory | met by ruling (GHI #1243), 846 chars headroom | done |
| H3 | Pipeline invoke bounded | `gz skill audit`; § Passage log | met, 125,923 B to 11,445 B | done |
| H4 | Per-turn rules and skill descriptions cut | the two sizes in the passage log before and after; `gz skill audit` | not started: rules 150 KB over 26 files, descriptions 15,085 chars | cheaper session, WP-11, GHI #1246 |
| H5 | The catalog exists and is used | `data/requirements_catalog.json` loads through the registry seam; briefs 16 to 20 carry `assignments:` | not started; shapes decided below | pilot, WP-4 |
| H6 | The TASK is the increment on one package | ledger: one package's TASKs each with a `red_commit_receipt_emitted`, in one session | not started | pilot cuts, cheaper session flies, WP-7 |
| H7 | Every control names its contract | `gz validate --advisory-scorecard` reads an obligation column | not started | cheaper session, WP-8, GHI #1247 |
| H8 | The toggle is on the record | `.gzkit/mx.json` with `mode: safe`, bound to its event | the verb exists (`ac3b0005e`); the operator has not entered through the gz-mx skill | operator, through the gz-mx skill |
| H9 | 17 and 20 attested | `gz obpi status` shows `attested_completed` for both | `Draft`; disclosures recorded in the log | operator |

### Drydock repairs (under safe mode; the pilot specifies and cuts, cheaper sessions execute)

| Repair | What is rebuilt | Witness |
|---|---|---|
| D1 | The ladder: ADR records decisions and lands contracts; the release plan (its own rung, § The release plan) governs a version; the work package replaces the OBPI as the labor unit; the TASK is the increment | the first release planned and closed through a release plan, with `gz closeout` keyed to it |
| D2 | The catalog as the product's truth: every live REQ an entry with its contract and state; legacy ids as aliases | a `gz validate` scope that fails on a brief assignment naming no entry |
| D3 | GHIs classified by the contract they repair; MX visits likewise | `ghi-triage` reports the contract per issue; an unclassified issue is a finding |
| D4 | The control plane subtracted: every control names its contract or retires; no rule body carries a dated narrative | the obligation column full; the counts below |
| D5 | The airlock derives the slice from the contract's `modules` | a transit whose reach exceeds the contract's modules is refused |
| D6 | Eval checks module design against module code | one eval run on one package, reported |

**Drydock exit numbers** (executive decisions 2026-10-16; the operator may move any by a word):

| Measure | Today | Exit |
|---|---|---|
| Per-turn load: AGENTS.md | 24,154 chars | at or under the ruled budget, 25,000 |
| Per-turn load: skill descriptions, all skills | 15,085 chars | at or under 8,000 chars |
| Per-turn load: rules, total and largest | 150 KB over 26 files; `tests.md` 11,618 B | at or under 90 KB; no rule over 6,000 B |
| Skills in the catalogue | 73 | every skill either model-invoked with a one-sentence description or `disable-model-invocation: true`; the count is reported, not targeted |
| Controls with no named contract | 189 scored, 0 assigned | 0 unassigned: each names its contract or is retired by a logged act |
| Operator attestations | one per OBPI | one per release, plus the sea trial |

### The release plan

Entrenched as a document type in `docs/governance/safe-mode-doctrine.md` § The release plan with
the template `.gzkit/templates/release_plan.md`. One document per version under `docs/design/releases/`, named by the version it governs.
Frontmatter: the version; `status` (`planned`, `in-flight`, `released`); the catalog entries whose
state advances, each with its from and to state; the work packages shipped; the lane and its gates;
the operator's attestation. Body: the intent of the version for the operator and for adopters, and
the one-open-defect assessment the constitution's policy 12 requires. `gz closeout` keys to it
(D1). The campaign sequences releases; a release plan says what one release contains. ADRs stop
carrying a version at the migration; a patch release uses the same document with a short list.

### The sea trial

The drydock's product is the first release, built and published through the first release plan.
The trial: a fresh project installs that release from the wheel, `gz init` scaffolds it, and a
cheaper session takes one work package from the catalog, cuts its TASKs, lands each as one commit
with its trailer and its `red_commit_receipt` on the pipeline route; the operator attests the
package from two artifacts only, its entries' states and its TASK receipts. The constitution's
governor rule is the ground: doctrine under construction is proven on another project before it
binds its own making. A second substrate, if the operator names one, flies as a flight-test sortie.
Passed once and recorded here, the ship is seaworthy and the handback follows.

### Executive decisions taken 2026-10-16 (the operator may overrule any by a word)

1. **WP-4 shapes, decided as recommended:** `REQ-C<n>` sequential ids with category as metadata;
   one JSON file `data/requirements_catalog.json` read through the registry seam with a derived
   Markdown view; assignments in brief frontmatter with the legacy `REQ-X.Y.Z-NN-MM` line kept as
   the alias the proof channels bind to.
2. **The release plan, confirmed by the operator** (§ The release plan).
3. **The disclosures of the cutover row stand as recorded.** The pilot cannot attest; it proceeds
   on them and the operator rules at H9.
4. **Execution leaves the pilot.** Every leg marked "cheaper session" is a GHI with a closure
   contract written by the pilot; the pilot executes nothing deterministic from here.
5. **The drydock exit numbers above.**

### Work packages added

- **WP-10 (GHI #1245).** The orientation prints this chart's readings while `.gzkit/mx.json` is in safe mode:
  each leg's witness run and its reading, so the path is read from the tree, never from memory.
- **WP-11 (GHI #1246).** The per-turn rules narrative lift and the skill-description cut (H4), measured
  before and after, nothing compressed in a binding clause.

## What does not change

Gate 5. The ledger rule. Every control standing under § Amendments 2026-10-04 (2). The
operator-PII rule. The Prime Directive. TOPMOST remains `ADR-0.35.0`; the pilotage works
inside it.

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
| 2026-10-16 | safe mode, the martial-law toggle, built as a mode of the MX hangar (GHI #1244; operator ruling verbatim *"A, extend gz mx with a safe mode - which is 'martial law' toggle"*) | martial law existed only as this contract: no marker, no per-turn banner, no ledger anchor, no exit gate; the hangar demoted guards and knew no mode | `gz mx enter --mode safe --contract <path>` opens the marker in safe mode: the marker and the `mx_session_opened` event carry `mode` and `contract`; the banner and the orientation name them each turn; `checkpoint.hangar_demotes` is true only under `mode: mx`, so every guard stays at full strength; a missing or outside contract, or a contract under the hangar, is refused; `gz mx exit` closes either mode through the same hard gate; rule 1.5.0 with § Safe mode (Coverage Ledger row 62f, Promotable), skill 1.2.0 with its flags corrected, manpages updated | `ac3b0005e` | 9 tests RED first across marker, checkpoint, awareness and enter, then 12 more to drive every hunk; `gz check` passed; `gz cli audit` passed; `gz arb red --commit ac3b0005e` 18 killed, 0 survived, 17 `inconclusive` (declaration hunks and reverts that error rather than assert; receipt `arb-red-commit-ac3b0005e9f0-0c3a60a8eb8047b9a5d3d80e03896fc4`). Three earlier cuts were `undriven` (13, then 2, then 1 hunks: the hook mirror and template, the parser flags, the typed event, the enter and exit labels, an unreachable assert that was removed, and two guards whose refusal message no test read); each re-cut before pushing. **Next:** the operator enters the present pilotage through the verb so the ledger carries the toggle: `uv run gz mx enter --mode safe --contract docs/governance/harbor-pilotage-candidate-2026-10-15.md --reason "harbor pilotage" --attestor g0` |
| 2026-10-16 | WP-2 closed by ruling (GHI #1243, operator verbatim *"A, record the budget at the invariant floor"*) | AGENTS.md 24,154 chars against a 20,000-char budget; the chore stopped at § 4 because 876 B of compressible text could not close a 4,154-char gap | the enforced budget is 25,000 chars, the attested invariant floor (22,599 B) plus margin, with a dated entry in `docs/governance/instructions-files-budget-history.md`; the doctrine page says the enforced value sits above the 20,000 ceiling, which is destination work again; options B and C recorded as declined; `gz validate --instructions-files-budget` exits 0 with no advisory; 846 chars of headroom | `e0dab8ee4` | data and docs only: `gz arb red --commit e0dab8ee4` verdict `no-production-hunks` (receipt `arb-red-commit-e0dab8ee443c-860c9d481d8649469a524129803afc2b`); `gz check` and `mkdocs build --strict` green (the strict build caught a lifted version-history link from the safe-mode commit, repaired here); GHI #1243 closed `fixed`. Exit condition 2 is met by ruling, not by trimming |
| 2026-10-16 | pilotage chart written: harbor legs H1 to H10 with witnesses and readings, drydock repairs D1 to D6 with seaworthiness witnesses, the sea trial, four executive decisions (WP-4 shapes, the release artifact as its own rung, the disclosures stand, execution leaves the pilot), WP-10 and WP-11 added | the path existed as seven exit conditions and a passage log; no instrument read the legs | § Pilotage chart; readings move only by a logged act | this commit | the operator's word of 2026-10-16 (*"lean in and make executive decisions"*); nothing executed |
| 2026-10-16 | entry and exit made skill-driven (operator correction, verbatim *"these need to be skill driven: 'gz mx exit'"*) | the chart and the handoff handed the operator raw `gz mx enter` and `gz mx exit` commands; the skill carried only the hangar | gz-mx skill 1.3.0 carries the safe-mode workflow: confirm the contract, enter, work under § Records, read the chart, exit through the hard gate, hand back; the chart's H8 and the quay name the skill | this commit | `gz skill audit` and `gz validate --cli-alignment` green after `gz agent sync control-surfaces`; insight recorded |
| 2026-10-16 | the chart amended to one exceptional period (operator, verbatim *"confirm all three, amend the chart"*): safe mode runs through the drydock and the sea trial and ends at seaworthiness; the sea trial is a fresh project on the released wheel; the release plan is its own rung with the shape in § The release plan | the chart had put the drydock under civil rule and the exit at the harbor's quay | § The regime, § Drydock repairs with exit numbers, § The release plan, § The sea trial; H10 folded into the handback phase; WO and WP distinguished (WO a pilotage instrument of 2026-10-15, WP the ruled civil-rule unit of 2026-10-05) | this commit | nothing executed; insight recorded |
| 2026-10-16 | the metaphor entrenched in canon (operator, verbatim *"keep these metaphor entrenched in canon, this won't be the last time we need to reach for this approach"*) | the regime lived in this contract only | `docs/governance/safe-mode-doctrine.md` (the doctrine: when declared, the metaphor and why it holds, the one-period regime, the six instruments, what is never suspended, entry and exit, lineage); `.gzkit/templates/safe_mode_contract.md`; the ratified glossary gains the terms; `mx-mode.md` 1.5.1 and `gz-mx` 1.3.1 point at both; one corpus entry captured for AGENTS.md § Governance doctrine surfaces (rendering awaits the operator's corpus attestation) | this commit | `mkdocs build --strict`, `gz skill audit`, `gz validate --distribution --advisory-scorecard` green |
| 2026-10-16 | the entrenchment completed to the operator's meaning (verbatim: *"i meant these"*, the chart's specifics): the standard harbor legs H1 to H9 and drydock repairs D1 to D6 with their witnesses, the standing exit measures, the release plan as a document type with its template, and the sea trial as a five-step procedure | the doctrine carried the regime and the instruments only | `safe-mode-doctrine.md` § The standard chart, § The release plan, § The sea trial; `.gzkit/templates/release_plan.md`; the contract template's chart pre-filled with the standard set; the glossary gains *release plan* | this commit | `mkdocs build --strict`, `gz validate --distribution` (regenerated), `tests.test_templates` green |
| 2026-10-16 | the work order retired; the work package everywhere (operator, verbatim *"retire it, work package everywhere - change now: 'WO-1 to WO-11' to WP"*) | two names for one labor unit: WO under the pilotage (keyed to a GHI), WP under civil rule (keyed to catalog entries) | one unit, the work package, keyed to a GHI until the catalog lands and to entries after; the GHI is the tasking order's carrier; WP-1 to WP-11 keep their numbers and GHIs (#1242, #1243, #1244, #1245, #1246, #1247; the issue titles stay as filed, `gh issue edit` is outside the allowed commands) | this commit | the doctrine, both templates, the glossary and this contract renamed; the operator-verbatim canon "the GHI is the work order and the receipt" (direct repair) and every dated record are untouched; `mkdocs build --strict` and `gz check` green |
