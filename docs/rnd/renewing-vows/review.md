# Renewing vows — the plan, for the operator's review

> **What this is.** One readable account of R&D run `renewing-vows`, written 2026-10-07 after
> the operator reopened the run. It is a view over the run record
> [`../renewing-vows.md`](../renewing-vows.md) and has no authority of its own. Where the two
> differ the record governs and this page is corrected. Figures here are dated observations;
> re-run the command before relying on one.
>
> **What it is for.** You signed off on this plan without reading it. Read it here, correct
> it, and then rule on § 9. Nothing below has been built, and no row has your go.

> **Stale, 2026-10-08. Do not review from this page yet.** It was written before the
> one-doctrine ruling and before `docs/governance/GovZero/` was read. Sections 8a and 9 are
> current to 2026-10-08 morning; sections 1 to 8 are not. Known wrong today: § 1 and § 7 still
> plan a separate concept of operations and a small constitution; § 2 and § 8 item 8 say the
> ladder's names are unsourced (three are sourced as terms); § 3 quotes the 2013 JP 3-60 and
> leaves "planned or flown" open (ruled); § 5 rows 5 and 7 and § 6 say FOC is unverified and
> one text is outstanding (both closed); § 8 item 13 says the eight roles are unmapped (they
> are mapped in § 3); "nothing owns" the collateral output (it had an owner and lapsed). The
> record governs. This page is rewritten after your first ruling on the recomputed frontier.

## 1. The problem in one paragraph

gzkit's trouble is not a shortage of controls. Every control addresses every agent as though
that agent could hold the whole project. Your words, 2026-10-05: the bloat comes from
"treating every model/agent like it is omniscient and omnipotent", and the better goal is "a
series of much smaller, and much more focused agents, being orchestrated, often by
skill-driven workflow". Joint air doctrine states the same limit: "No single commander or
headquarters can have the necessary situational awareness or maintain the tempo of operations
required to effectively execute tactical operations in a highly dynamic combat environment"
(JP 3-30, 2019, Chapter I § 3b(4)).

Most of the machinery the remedy needs is already in flight or queued. What is missing is
the statement those pieces answer to: a concept of operations, with its seat and its names.

## 2. The frame

You ruled a full military and aviation combination on 2026-10-05, with the combat register
at full strength. The reasoning you accepted: operations, airworthiness, certification,
safety management, flight test, configuration management and crew discipline are departments
of one air force, and each metaphor you had circled is one department seen alone.

The organising idea, in the doctrine's words, is **centralized control and decentralized
execution**: one place plans and tasks; execution is delegated; and the centre is told of
every change. Standing guidance travels inside the order ("special instructions (SPINS)
located in the air tasking order"), and "less detail is required" when one unit flies alone.

### The ladder of work

Ruled by you on 2026-10-05 ("A"). Identifiers migrate at 1.0; aliases bridge until then.

| Today | Ultimate name | Identifier | What it is |
|---|---|---|---|
| pool ADR | change proposal | `ECP-<slug>` | an idea not yet funded |
| feature ADR, the "(m)ADR" | engineering order | `EO-0.35.0-<slug>` | a themed bundle for one release increment |
| OBPI | work package | `WP-0.35.0-10-<slug>` | one bounded assignment; the brief is its document |
| TASK | task card | `TASK-…` (kept) | one unit of labour |
| ADR | ADR, for architecture decisions only | `ADR-<n>` | a decision record; the closed 0.0.x series stays as the certification basis |
| release | block | — | what shipped |

Beneath the work package, from the Operations rows: a **pipeline run is a mission** and a
**dispatch is a sortie**. JP 3-30's definitions agree: a sortie is "an operational flight by
one aircraft"; a mission is "the dispatching of one or more aircraft to accomplish one
particular task."

**Finding you should see:** none of the five ladder names (change proposal, engineering
order, work package, task card, block) appears in any source this run has landed. They are
your ruling and common practice; they are not yet sourced.

## 3. How one work package is flown

Each line is a decision in the record, with who ruled it.

| Element | What was decided | Ruled |
|---|---|---|
| Constraints sortie | A design act that lands contracts (interfaces, invariants, stubs) before any failing test, so that a red test fails on an assertion and not on a missing symbol. Measured 2026-10-05: 207 of 282 red receipts failed on `error`. | you, 2026-10-05 |
| Red, then green | Green keeps local cleanup; wider refactor is its own traversal. | you, 2026-10-05 |
| Weaponeering | The kind of requirement fixes which sorties fly. BEHAVIOR flies constraints, red and green; SUPPORT flies one documentary sortie; STRUCTURAL-FENCE flies none and is audited at closeout. An order may add sorties freely. A standard sortie is skipped only when its product is already on the ledger and the order cites it. Green and assessment are never waived. The runtime checks the rule; the planner never decides it. | you, 2026-10-05 |
| Chase and damage assessment | Two roles. Chase confirms a test passes, from outside. Damage assessment asks about target effect, how well the means worked, and collateral. Collateral has no owner in gzkit today. | you, 2026-10-05 |
| Tasking order | A ledger event, completing the chain tasked → dispatched → outcome → position. The mission card and the sortie matrix are views of it. | you, 2026-10-05 |
| Model and effort | Allocated by echelon and role: strongest model at high effort for synthesis and the constraints sortie; mid-tier at low effort for execution; strong at high for assessment; maximum for cross-vendor review and security-sensitive assessment. A regeneration test is the falsifier. | you, 2026-10-05 |
| Where effort is set | On the agent definition, never on the dispatch call. `model-selection.md` describes a mechanism the harness does not have. | agent finding, verified against the documentation |
| General orders | They exist and are tiny. Three candidates, **my draft and not your words**: report truthfully; call knock-it-off when lost or blocked; never forge evidence. Everything else rides on the order, in the loadout, or behind an interlock. | you ruled that they exist; the wording is unruled |

Joint doctrine supports three of these directly (JP 3-60, 2013 edition): combat assessment
"is composed of three related elements: BDA, MEA, and reattack recommendations"; weaponeering
is "determining the quantity of a specific type of lethal or nonlethal means required to
create a desired effect on a given target"; and collateral damage is estimated before and
"also assessed and reported during BDA". The crew's own report is one input among several;
a designated cell makes "the final assessment".

### The core model, mapped (added 2026-10-07; shape ruled 2026-10-08)

Your Gemini dialogue named eight roles: mission planning, mission constraints, target
planning, infiltration, ordnance delivery, exfiltration, decontamination, BDA. The record
quoted them and never mapped them. This is the mapping, built from the two cycles after
reading them. The full table with the tasking cycle beside it is in the record.

| # | Targeting phase (JP 3-60) | What happens | Your role | gzkit today | State |
|---|---|---|---|---|---|
| 1 | Commander's objectives, guidance and intent | Objectives and measures fixed at the start | none: command | Order intent; the work package's requirements | exists |
| 2 | Target development | The commander approves a prioritised list; no-strike list; restricted targets | target planning | Campaign order; allowed and denied paths | exists, other names |
| 3 | Capabilities analysis | Weaponeering; collateral damage estimated | mission constraints (estimated) | Model tier by task complexity; airlock seam-map, mostly empty | weak |
| 4 | Commander's decision | Tasking order issued with reasoning and special instructions | mission constraints (in the order) | You initiate; plan-audit receipt; no tasking record | gap |
| 5 | Mission planning and execution | Unit plans; target revalidated; engage | mission planning; ordnance delivery | Plan, lock, implementer red then green | exists |
| 6 | Combat assessment | Damage in three phases; munitions effectiveness; collateral; reattack | BDA | Receipts, spec review, Step 4b, fix cycles | two outputs unowned |

**You ruled the shape on 2026-10-08: "i want both."** The six phases are the process; your
eight roles are the crew; the airlock roles are flown around execution; constraints are
flown and their product travels in the order. The staffing is my drawing of that ruling,
for you to correct:

| Phase | Who | What they hand on |
|---|---|---|
| 1. Objectives | command: you and the order's author | intent, requirements, measures |
| 2. Target development | **target planning** | what changes, what is protected, what is restricted |
| 3. Capabilities analysis | **mission constraints**; the runtime applies the weaponeering rule | contracts, the collateral estimate, the sortie set |
| 4. Commander's decision | command: you initiate | the tasking order |
| 5. Mission planning and execution | **mission planning**, **infiltration**, **ordnance delivery**, **exfiltration**, **decontamination** | plan; entry; red then green; exit; cleanup reported |
| 6. Assessment | **BDA** | damage in three phases, munitions effectiveness, collateral, reattack |

Open seams: mission planning is first in your list and fifth in the cycle; ordnance delivery
is already split into red and green; BDA is one role against five outputs.

Three things the mapping showed before the ruling:

1. **Five of your eight roles are in the targeting cycle. Three are the airlock's**
   (infiltration, exfiltration, decontamination) and appear in neither publication. The
   model is two things: the cycle, borrowed and sourced, and the airlock transit, gzkit's
   own.
2. **In the doctrine, constraints are planned and travel in the order; they are not
   flown.** You ruled the constraints sortie "a Design act". Whether it is dispatched as a
   sortie or done by the planner is open.
3. **Assessment is where gzkit is thinnest.** Nothing owns what a change did to the system
   around its target, and nothing owns whether the means used performed as estimated.

## 4. What already exists, what is queued, what is new

States are as the record measured them on 2026-10-05 and 2026-10-06. Run
`uv run gz adr status <ADR-ID>` for the live count.

| The remedy needs | Carried by | State when measured |
|---|---|---|
| A runtime that holds a run's position, next command, stage procedure, dispatch outcome and lock continuity | `ADR-0.35.0` briefs 15 to 20 | ADR at 10 of 20; these six unstarted, next in the ruled order |
| A second opinion at the convergence moment | `ADR-0.36.0` | 0 of 9 |
| An airlock that bites | `ADR-0.37.0` | 0 of 6 |
| A flight test on someone else's substrate | `ADR-0.38.0` | not yet authored; 0 of 6 sorties ever flown |
| One config system | `ADR-0.39.0` | authored, behind the four above |
| The parts of the sortie layer | sixteen pool nominations, listed in the record's accounting entry | pool |
| **New:** the crew split with the tasking event and sortie matrix | proposed engineering order | row 1, after briefs 15 to 20 |
| **New:** combat assessment with a collateral owner | proposed engineering order | row 1 |
| **New:** integrity level as a second axis | proposed engineering order | row 1, conditional on you lifting PROVISIONAL on the bands |
| **New:** a ledger event per chore run | proposed engineering order | row 1 |

Your question on 2026-10-05 was whether to stop using gzkit to build gzkit. The accounting
answered: nothing in flight is wasted, and the new layer cannot start before the spine
lands. Your reply, as the prior session captured it: "If nearly all of the remedy is in
planned work, then I can hold on."

## 5. What you ruled on 2026-10-07

Each was a selection of the option I recommended. Reconsider any of them here.

| # | Question | Your ruling | What it rests on |
|---|---|---|---|
| 1 | Where the concept of operations sits | Under the constitution, above the PRD and the campaign plan. The plan keeps sequencing. | The constitution is root by your 2026-06-14 ruling; no standard ranks it this way. |
| 2 | What to do with the consequence bands | Lane keeps its external-contract criterion. The bands (detectability plus recoverability, C0 to C3) are proposed as a second axis. | Your two lane rulings of September; your bands of 2026-09-22. |
| 2a | The axis's name | Integrity level | IEEE 1012-2024 Clause 5, quoted in IEEE piece 01. |
| 3 | Chore runs and findings as ledger events | Runs yes, findings no | Amends one line of the chore design you ratified 2026-09-12. |
| 4 | Slower tiers of the rhythm | Two, each due on an announced signal, never a calendar: a plan republish that folds amendments, and a maintenance visit. Neither gates. | Your 2026-07-18 session rhythm stands as the first tier. |
| 5 | What IOC is | A waypoint before 1.0: `ADR-0.35.0` to `0.38.0` landed, S1 flown on a non-gzkit substrate, the stale canon items repaired. 1.0 is full operational capability with all ten gates. | "Nothing — move the date instead" (you, 2026-08-17). **The IOC and FOC definitions are unverified.** |
| 6 | The unwritten constitution | A small one in `Draft`, through `gz constitute`, for you to ratify: the general orders, the four charter principles, a pointer to the floor. | The root has no document today. |
| 7 | Unread standards | "b": you supply the public texts before their rows are drafted. | Four of five supplied and read. |

One thing I closed without asking you: the identifier migration was ruled "at IOC" when IOC
meant 1.0, so I kept it timed to 1.0. Overrule it if you meant the waypoint.

## 6. The names, row by row

Status: **R** ruled by you · **S** a source was read and supports the name · **D** a source
was read and differs · **U** no source has been read; the name is from memory or is a plain
metaphor. Every unmarked name is my proposal, not your ruling.

### Guidance

| gzkit term | Ultimate name | Status | Note |
|---|---|---|---|
| lodestar | doctrine library | U | |
| constitution | constitution (standing constraints) | U | Operations specifications are issued by a regulator and state only "certain" procedures: a weak analogue. |
| PRD | functional baseline of a major version | S | MIL-HDBK-61B defines the functional baseline. |
| (new) | concept of operations | R, S | Placement ruled; the term is 29148's. |
| campaign amendments | fragmentary orders, folded on republish | S / U | JP 3-60 (2018) names the fragmentary order as a kind of tasking order. Whether a plan amendment is one is unsourced. |
| sequenced campaign items | prioritised target list | D | JP 3-60 (2018): "Targets may not be engaged in the same priority order as they appear on the JIPTL." Your ADR order is absolute. |

### Configuration management

| gzkit term | Ultimate name | Status | Note |
|---|---|---|---|
| ledger | configuration status accounting | S | MIL-HDBK-61B; also a DO-178C activity by a secondary source. "Flight data recorder" is a metaphor, U. |
| receipts | objective evidence; life-cycle data | U / S | "Life-cycle data" is DO-178C section 11 by two secondary sources. "Objective evidence" is unsourced. |
| closeout | functional and physical configuration audit | S | MIL-HDBK-61B. |
| attestation | return to service | S | 14 CFR § 43.9: "The signature constitutes the approval for return to service only for the work performed." |
| repudiate | release withdrawn | U | |
| `--distribution` | configuration index | S | Secondary sources only. |

### Operations

| gzkit term | Ultimate name | Status | Note |
|---|---|---|---|
| orchestrating session | operations centre | S | JP 3-30. |
| | duty officer | D | JP 3-30's centre has a director. No duty officer of this kind appears. |
| pipeline run | mission | S | JP 3-30 glossary. |
| dispatch | launch (a sortie) | S | "Sortie" is JP 3-30's; "launch" is plain usage. |
| `HandoffResult` | mission report (MISREP) | S | JP 3-60. It is an input to assessment, never the verdict. |
| spec, quality, collateral review | combat assessment: BDA, MEA, reattack | S | JP 3-60 (2018), where it is now the name of the whole sixth phase. |
| Step 4b adversary | independent verification and validation | D | IEEE 1012 requires technical, managerial **and** financial independence. Step 4b has only been argued for the first. |
| airlock in | last-chance check with collateral damage estimation | S / U | The estimate is JP 3-60's. "Last-chance check" is unsourced. |
| airlock out | safing and FOD walk | U | |
| seam-map | interface control documents; zones affected | U | |
| lock | custody | U | |
| handoff | position relief briefing | S | FAA JO 7110.65BB Appendix A, which you supplied the model for in August. |
| session | watch | D | The order's noun is the *position*. "Watch" is in no text read. |
| allowed and denied paths | rules of engagement, special instructions | S | JP 3-30. JP 3-60 offers a closer fit: a **no-strike list** and a **restricted target**. |
| tool grants | loadout | U | |
| implementer, reviewers, narrator | pilot flying, pilot monitoring, assessor, briefer | D | AC 120-71B (read 2026-10-08): the monitoring pilot works *at the same time* as the flying pilot; gzkit's reviewers assess afterwards. And gzkit's own command doctrine, Article 3: "The model is a crew resource, not a crew member." "Assessor" and "briefer" are in no text read. |

### Airworthiness

| gzkit term | Ultimate name | Status | Note |
|---|---|---|---|
| chores | scheduled maintenance tasks | S | AC 121-22D: "minimum scheduled maintenance tasking/interval requirements". The test for a task is "applicable and effective". |
| registry | maintenance planning document | D | The phrase is in no text read. |
| chore visit | letter check (your mapping, 2026-10-05) | D | "Letter check", "A-check" and "C-check" are in neither Title 14 nor AC 121-22D. Industry practice; its source would be MSG-3. |
| `gz mx` | maintenance visit | U | |
| `gz check`, CI | preflight; functional check flight | U | |
| GHI | squawk; problem report | U / S | "Problem report" is DO-178C's by secondary sources; "squawk" is your word and unsourced. |
| operator hold | deferred defect | U | |
| direct repair, ghi-close | rectification, sign-off | U | |
| chore run event | maintenance record entry | S | 14 CFR § 43.9(a). My proposal, 2026-10-07. |

### Safety

| gzkit term | Ultimate name | Status | Note |
|---|---|---|---|
| governance of governance | safety management system | S | 14 CFR § 5.3. |
| failure-mode taxonomy | hazard log | D | The phrase occurs nowhere in Title 14. Needs another source or is dropped. |
| insights file | occurrence reports | U | |
| finding-rate panel | flight operational quality assurance | S | AC 120-82, from a facsimile copy. |
| V.I.B.E.S. | normalisation of deviance | S | Vaughan; two of four claims verified. |

### Assurance

| gzkit term | Ultimate name | Status | Note |
|---|---|---|---|
| lane | lane | R | Unchanged. |
| consequence bands | integrity level | R, S | |
| gates | objectives | D | Your standing constraint of 2026-09-22: "do not abandon the five gates without a discussion with me." I recommend dropping this row. |
| `@covers` | bidirectional traceability; requirements-based testing | S | Secondary sources. |
| gating validators | qualified tools | S | DO-330. Verifying tools are held to less than generating tools, and a qualification does not carry between projects. |
| hooks | interlocks | U | |
| rules | standing instructions | U | |
| skills | procedures; challenge-and-response checklists | S / D | AC 120-71B: "procedure" fits a skill. A checklist is a different thing: a short list read after the work to confirm the critical items, which is nearer the per-change gate. |
| fix, refactor, chores, vendor alignment, feature work | corrective, perfective, preventive, adaptive, additive | S | ISO/IEC/IEEE 14764:2022. |

### Fielding

| gzkit term | Ultimate name | Status | Note |
|---|---|---|---|
| 1.0 | full operational capability | R, U | Ruled; the definition is unread. |
| spine landed and S1 flown | initial operational capability | R, S | Ruled; verified 2026-10-08 from the DSCA manual's glossary: "some units ... have received it and have the ability to employ and maintain it". Each system sets its own IOC conditions. |
| adopter `gz init` | entry into service | U | |
| AirlineOps | lead wing | U | |

**The count**, over the 55 rows above (the ladder's six names in § 2 are separate): 22 have
a source that was read and supports them; 3 are part sourced and part not; 8 are contradicted
or strained by a text that was read; 19 have no source at all; 2 are ruled and unverified
(the Fielding pair); 1 is ruled and needs none (lane). The unsourced ones are mostly plain
metaphors, and you may want them anyway; they should not be cited as doctrine.

## 7. What each row of the plan would produce

No row has your go. Rows 1, 3 and 5 can never be started by me.

| Row | What it would produce | Who starts it |
|---|---|---|
| 1 ADR / OBPI | Four proposals, after briefs 15 to 20: the crew split with the tasking event and sortie matrix; combat assessment with a collateral owner; the integrity-level axis; the chore-run event. | You initiate each, or not. |
| 2 GHI / direct fix | Issues for five stale-canon items (dead constitution link; stale non-goal; INV-007 against universal Gate 5; lodestar README against Boundary #5; both charters scoping Gate 5 to heavy lane). The malformed `@covers` tags. The Markdown lint that nothing runs. | Your go, plus two routing picks. |
| 3 chore | Advice only: move per-flight checks off the interval board; package due chores into named visits; two announcements (republish due, visit due). | You direct admission. |
| 4 docs and rules | The concept of operations. A small constitution in `Draft`. The campaign plan republished, naming the concept of operations and carrying the IOC waypoint. PRD repairs. The weaponeering rule text. A corrected model-and-effort section. The ladder's names recorded in the IEEE thread. | Your go. |
| 5 one-shot refactoring | The identifier migration to ECP, EO and WP, with aliases, timed to 1.0. | You select its route. |
| 6 no action | Ideas rejected, kept as prior art so they are not re-filed. | — |

## 8. What the supplied texts put in doubt

Each is a finding from a text you supplied on 2026-10-07. None changes a ruling.

1. **"Battle rhythm" means a timeline by the clock.** JP 3-30: "a detailed timeline ... to
   produce specific products by a specified time". You ruled tiers that come due on a
   signal. JP 3-60 calls its own cycle "not time-constrained", which is the nearer model.
2. **"Watch" and "duty officer" are in no text read.**
3. **Letter checks and the maintenance planning document are in no text read.**
4. **The prioritised target list is not a firing order.**
5. **"Hazard log" is not a regulatory term.**
6. **"Gates → objectives" touches the five-gate vocabulary** you told me not to abandon.
7. **Step 4b is not independent verification and validation** as the standard defines it.
8. **The ladder's five names are unsourced.**
9. **"Qualified tools" hides a gradient**: validators and code-writing agents are different
   classes of tool.
10. **FOC is unverified; IOC is now verified** (2026-10-08, from an official Defense
    Department glossary). Two files you sent for them contained neither term.
11. **Resolved 2026-10-08: you supplied the 2018 edition of JP 3-60**, which supersedes 2013.
    The combat register is now cited to it. Two phases were renamed and the weaponeering
    definition shortened; nothing the run relied on was reversed.
12. **The campaign plan misquotes the FAA order.** Its 2026-08-17 amendment sets five
    phrases in quotation marks that occur nowhere in JO 7110.65BB. A defect, logged as an
    insight, not yet in any row.
13. **The eight roles from your dialogue are unmapped.**

## 8a. The largest finding (added 2026-10-08): gzkit already has a command doctrine

`docs/governance/GovZero/command-doctrine.md` is canonical, ratified by you on 2026-06-10,
and this run never read it. It is the philosophy layer: ten articles on authority,
accountability and automation, in an aircrew frame, to which every policy, procedure and
practice is required to trace. It was found on 2026-10-08 by following a reference in
AC 120-71B.

What it does to this plan:

- **Rulings 1 and 6 in § 5 were made without it** and need to be put to you again: where the
  concept of operations sits, and what the constitution draft contains. A ratified apex
  already exists.
- **Article 3 says "The model is a crew resource, not a crew member."** Calling the
  implementer the pilot flying does not agree with it. Your eight sortie roles may stand;
  naming an agent a pilot may not.
- **Article 4 already owns one of the two unowned assessment outputs**: a diff of delivered
  work against commanded scope, which its own appendix marks as only partly built.
- **The tasking order has a ratified ancestor**: the captain's brief with a scope manifest.

**Ruled 2026-10-08.** Asked what the new concept of operations is relative to the command
doctrine, you said: "incorporate and merge/subsume, I am in search of binding/bounding
doctrine for gzkit to hold me and agents to account." So there is one doctrine, not two: the
ten ratified articles carried in as they stand, with the model in § 3 merged in beneath
them. Ruling 1 in § 5 is superseded as far as it made a separate document; ruling 6 is
superseded as to what the constitution contains.

One fact that explains the miss and is itself a defect: the command doctrine is named by the
charter, one pool ADR and two evaluation records, and by nothing an agent loads each turn.
The entry that carried it into `AGENTS.md` was dropped and never recaptured.

## 9. What I need you to rule

In the order I would ask them, one at a time, once you have read the above:

0. *Ruled 2026-10-08:* one merged doctrine. Next under it: is the merged doctrine the
   constitution, or does it sit under a separate one?
1. Does § 1 state the problem you meant?
2. Is the core model in § 3 right: the targeting cycle as the spine for one work package,
   the airlock as a separate transit, constraints planned or flown, and who owns the two
   unowned assessment outputs? **This comes first; the names wait on it.**
3. Do the three general orders say what you want the constitution to say?
4. Which of the eight **D** names in § 6 do you keep as stated departures, rename, or drop?
5. Do the unsourced names stay as metaphors, or does each need a text before it is used?
6. Do any of the seven rulings in § 5 change now that you have read what they rest on?
7. Does the migration stay timed to 1.0?
8. Does the campaign-plan misquotation join row 2?
9. Then, and only then: kill or fund.
