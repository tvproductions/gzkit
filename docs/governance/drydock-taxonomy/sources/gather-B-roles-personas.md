# Gather B: control roles, personas and positions, the crosswalk and its rejected synonyms

Gathered 2026-11-22 for `docs/governance/drydock-taxonomy.md` § 9 items 3, 4 and 5. Read-only; nothing in
the repo was edited and no writing `gz` verb was run. Status column, exactly one of: **RULED** (an operator
ruling exists, quoted), **SOURCED** (defined in canon or code, no operator ruling found after full reading of
the files listed at the end), **CONTRADICTED** (two sources disagree, both quoted), **UNSOURCED** (used, never
defined in what was read).

Abbreviations: `CCC` = `docs/rnd/contractor-kit/sources/census-code-controls.md`; `CMS` =
`docs/rnd/contractor-kit/sources/census-model-surfaces.md`; `KIT` = `docs/governance/harbor-ro12-contractor-kit.md`;
`REC` = `docs/rnd/contractor-kit.md` (the R&D record); `MAT` = `docs/rnd/contractor-kit/vocabulary-matrix.md`;
`REV` = `docs/rnd/contractor-kit/review.md`; `RO10` = `docs/governance/harbor-ro10-safe-mode-classification.md`;
`WPR` = `src/gzkit/work_package_run.py`.

Line numbers are of the tree on 2026-11-22.

## Domain 3: control roles (the two censuses)

The code census states its rule at `CCC:66-71`, verbatim: *"**Role classification.** The role is the
auditor's reading of each control's primary effect, by this rule: **gate** when it sits on a lifecycle
transition (OBPI completion, closeout, release, mx exit, plan exit, stage advance) or audits lifecycle
coherence; **safeguard** when it protects the ledger, attestation, the GATE5 floor, attested canon, or the
control system itself (a control over other controls); **tripwire** for any other blocking check; **alarm**
when it only announces or warns; **monitor** when it only records or observes. *Other* is named where used."*
The model census says of its own labels (`CMS:39-40`): *"Role assignments for skills and rules are this
census's judgment ... They are not a field the repo declares, so they are a reading and can be challenged."*
No code declares a role field for any control; the roles exist only in the two censuses and in prose that
cites them.

The only operator words on the role names are about counts and order, not definitions: `REC:2543-2544`
(2026-10-26), *"these might need decorators or something similar ... ==> "218 safeguards, 116 tripwires, 52
gates, 13 monitors, 12 alarms""*; and the RO-13 route, `REC:3189-3193`, option A *"code controls first, by
role: alarms, gates, then safeguards, monitors and tripwires"*, operator *"A"* (2026-10-27), carried as
`docs/governance/harbor-ro13-mode-contract.md:28` (*"The retrofit runs code by role ..."* operator *"a"*)
and `:54` (*"R1, code controls by role. Alarms, gates, then safeguards, monitors and tripwires."*). So the
**use** of the role names as RO-13's ordering is ruled; their **definitions** are not.

| Term | Meaning as stated | Defined at | In code | Status |
|---|---|---|---|---|
| gate (control role) | *"when it sits on a lifecycle transition (OBPI completion, closeout, release, mx exit, plan exit, stage advance) or audits lifecycle coherence"* | `CCC:68-69`; 52 counted `CCC:771` | none: no role field (`CCC:66`, `CMS:39-40`) | SOURCED (definition unruled; its use in RO-13's order ruled, `REC:3189-3193`). Homonym of Gates 1 to 5 (`AGENTS.md` § Gate Covenant) and of "gate procedure" (below) |
| safeguard | *"when it protects the ledger, attestation, the GATE5 floor, attested canon, or the control system itself (a control over other controls)"* | `CCC:69-70`; 218 counted `CCC:771` | none | SOURCED. Note: all 134 `@enforces` claims are counted as safeguards (`CCC:766`), though the same census calls each claim *"the self-test layer for the controls they name"* (`CCC:456-457`), so 134 of the 218 are self-tests, not controls |
| tripwire | census: *"for any other blocking check"* | `CCC:70`; 116 counted `CCC:771` | none | **CONTRADICTED**: `RO10:49` *"A **tripwire** does not stop the work and does not ring; it records that an order touched something it guards, as a list-of-discrepancies line"*; `REC:1084-1085` *"**Danger** and **Caution** tags (an alarm off and locked; a tripwire that records)"*, ruled *"A"* 2026-10-25. Operator, `RO10:22` (2026-10-25): *"tripwires for the cheap ones, long ones fully off"* |
| alarm | census: *"when it only announces or warns"* | `CCC:70-71`; 12 counted | `src/gzkit/mx/alarms.py:24-39` (`alarms_off`, the wrapper that skips blocking hooks) | **CONTRADICTED**: `RO10:49` *"An **alarm** stops the work."*; `safe-mode-doctrine.md:28` *"The alarm test decides between the line and out of service ... Work that must lower an alarm ... is out of service"*; the code's `gzkit.mx.alarms` switches off hooks the census itself classes *tripwire* (G6, G18) and *dispatcher* (G17) (`CCC:106`, `:117-118`). Operator, `RO10:18`: *"turn the "security alarms" back on"* |
| monitor | *"when it only records or observes"* | `CCC:71`; 13 counted | none | SOURCED. Overlaps RO-10's tripwire (*"records that an order touched something"*); see the tripwire row. Operator uses the word undefined, `REC:1875`: *"the controls, monitors, alarms, and safeguards each needs to understsnd what a safemode, standby, lockout singal is"* |
| dispatcher (role) | not in the five-role rule (`CCC:66-71`); glossed by § 10b's heading *"Distinct places of call (dispatchers) and what each dispatches"* | `CCC:779`; used as a role at `CCC:105`, `:117`, `:328`, `:760`; 3 counted `CCC:771` | the 22 dispatchers D1 to D22 (`CCC:781-804`), e.g. `gzkit.hooks.guards.run_guards`, `quality._run_check_steps` | SOURCED (by the § 10b gloss only; absent from the classification rule). RP-13 F4 reads *"the census's dispatchers (§ 10b)"* (`harbor-ro13-mode-contract.md:45`) |
| other: producer | G1 *"other: producer (stamps `Task:` trailers ...)"* | `CCC:101` | `.gzkit/hooks/prepare-commit-msg-task-trailers` | SOURCED (named where used, per `CCC:71`) |
| other: fixer | G3 *"other: fixer (the commit fails when files were rewritten)"*; G11 *"other: fixer/tripwire"*; G12, G13 | `CCC:103`, `:111-113` | pre-commit hooks | SOURCED (named where used) |
| other: router | H13 *"other: router (emits a routing instruction)"* | `CCC:171` | `.claude/hooks/pipeline-router.py` | SOURCED (named where used) |
| negative control (NC) | *"Each claim **is** a negative control: a fixture builds a violation and the production entrypoint must catch it."* | `CCC:456` | `src/gzkit/enforcement.py` (`production_enforcement_registry`, `enforcement.py:793-801` per `CCC:443`) | SOURCED |
| guard canary | *"38 canaries. Each binds one reviewed mutant to one claim."* | `CCC:620` | `src/gzkit/guard_canary.py`; `data/guard_canaries.json` | SOURCED |
| built-in self-test | operator, 2026-10-26: *"modules ... need to be able to built-in tests, you know, built-in self-test. So they can participate in this MEL process by indicating their suitability for function"* | `REC:2230-2235`, decision `REC:2241-2269` | seed: seven chore `--self-test` arms (`CCC:713-727`, `REC:2769-2790`) | RULED (in principle, `REC:2243`); *"Built-in self-test is the operator's term ... unsourced"* (`REC:2261-2262`) |
| place of call | *"The contract is **honored at the place of call**, where the behavior is suspended or modified."* | `REC:1979`; operator `REC:1941-1949` | `src/gzkit/mx/checkpoint.py` (the one switch today, `REC:1981-1982`) | RULED (in principle, `REC:1971`) |
| GATE5_INVARIANTS / the floor | five members, `gate5-attestation`, `secrets`, `operator-pii`, `ledger`, `grader-gaming` | `CCC:608-616` | `src/gzkit/mx/invariants.py:26-34` | SOURCED (code); MEL ruling *"The floor can never be listed"* (`REC:2073-2074`, operator *"A: MEL with Meyer levels"*) |
| named-not-enforced | floor members with no enforcement | `CCC:613-614`, `:847` | `_GATE5_NAMED_NOT_ENFORCED`, `invariants.py:57` | SOURCED |
| MX-aware | *"the control's code path reads `.gzkit/mx.json` today, whether directly, through the checkpoint, or through the alarms wrapper"* | `CCC:808-809` | readers listed `CCC:729-752` | SOURCED |
| demote / advisory / pinned | `checkpoint.resolve` *"pins any `GATE5_INVARIANTS` name to CRITICAL and demotes every other non-CRITICAL level to `Route.ADVISORY`"* | `CCC:19-21` | `src/gzkit/mx/checkpoint.py:17-31` | SOURCED |
| guidance (surface role) | label glossed by subtype: *"analysis or report"*, *"governed authoring"*, *"reconcile, sync or repair"* | `CMS:84-158`, counts `CMS:465-470` | none (census judgment) | SOURCED (census's own gloss; *"a reading and can be challenged"*, `CMS:40`) |
| gate procedure (surface role) | *"gate procedure — gate, ceremony, receipt, lock or mode transition"* | `CMS:90` and rows | none | SOURCED (gloss in the label) |
| routing (surface role) | *"routing — namespace router"*, *"routing — skill selector"* | `CMS:108`, `:125` | none | SOURCED (gloss in the label) |
| tripwire-by-instruction | used for rules `gh-cli`, `mx-mode`, `skill-surface-sync`, `token-block-discipline` and the MX banner (`CMS:189-201`, `:296`); never defined as a class | `CMS:467` (count 10) | none | UNSOURCED (read `CMS` whole; per-row glosses only, no class definition; its relation to the census's or RO-10's *tripwire* is unstated) |
| persona obligation (surface role) | applied to all seven personas (`CMS:204-210`); no class definition | `CMS:469` | `pipeline_dispatch._persona_frame` (delivery) | UNSOURCED as a class (nearest: Part 0 *"Position. An obligation and a role to fulfil it."*, quoted `REC:880-881`) |
| mixed (surface role) | applied to `AGENTS.md` alone | `CMS:470` | none | UNSOURCED |
| conditions / routes / mentions / false positive | *"*conditions* (the text tells the model to act differently when the marker is open), *routes* (sends the model to `gz-mx`), *mentions* (cross-reference or provenance only), or a false positive"* | `CMS:19-21` | none | SOURCED |
| reach unverified | rows whose reach to the model depends on Claude Code's published hook rule, not observed live | `CMS:44-47` | none | SOURCED |

## Domain 4: personas, positions and dispatch roles

### 4a. The kit's positions (RP-12)

Carried into the kit, `KIT:22`, verbatim: *"**Positions.** The operator, always the commander (A1). The
coordinator, the operator-facing session, which performs no work and holds the Authorizing Officer duty (A3).
One craftsman persona in two positions, repair and restoration (A4, A6). The Quality Assurance Inspector,
dispatched by the runtime and never by the coordinator, its findings reaching the operator unedited (A5). The
surveillant, dispatched by the operator only (A8)."*

Kit rulings 21 to 23, verbatim heads (`KIT:447-449`), all 2026-11-04, each operator *"A"*:
- 21: *"The term witness: terms declared and resolved, bodies scanned against the crosswalk's own strings"* — rejected synonyms *"(*repairer*, *restorer*, *task card*, *fix cycle*, *punch list*, *orchestrator* for the coordinator, among them)"*; scope *"the kit's personas and skill, as the operator's rider names them"*.
- 22: *"One skill, `gz-repair-pipeline`, run by the coordinator"*.
- 23: *"The surveillant has its own persona file ... The kit's persona files are then four, craftsman, Quality Assurance Inspector, coordinator and surveillant"*.

Measured: `.gzkit/personas/` holds seven files, none of the four kit personas; `.gzkit/skills/` holds no
`gz-repair-pipeline`; no crosswalk JSON exists (Domain 5). O8 (ruling 25, `KIT:462`) lands them and has not
been built. Witness-floor rows 3, 12 and 13 read *"Nothing"* (`KIT:50`, `:59`, `:60`).

| Term | Meaning as stated | Defined at | In code | Status |
|---|---|---|---|---|
| operator / commander | *"The human, in gzkit, is always the commander"*; *"No maintenance title is adopted for the human."* | `REC:1514-1534`; `MAT:35` (A1); `KIT:22` | `--attestor g0` and operator-words gates, e.g. Gate 5 at the order (`KIT:414`, ruling 73) | RULED: operator, 2026-10-25, *"actually, everywhere else, I am the operator and I am assumed to be gov zero (the human). The human, in gzkit, is always the commander"* (`REC:1525-1526`) |
| captain | Part 0: *"The same human, as the holder of the signature and the override."* | quoted `REC:878-879` from `docs/rnd/renewing-vows/doctrine-merge.md` Part 0 (not read in this gather) | none found | RULED (Part 0 *"Ratified 2026-10-10 (operator, verbatim: 'ratify Part 0')"*, quoted `REC:863-864`); untouched by A1 (`REC:1532-1534`) |
| coordinator | *"the operator-facing session and performs no work itself, it dispatches repairers and restorers as subagents"*; holds dispatch, sequencing, the AO duty, pen and ink, inspection requests, single writer; may not issue change orders, direct the inspector, dispatch surveillance, approve return to service | `REC:605-622`, `REC:1696-1723`; `MAT:37` (A3); `KIT:22` | its acts are unstamped calls: `gz wp tag issue`/`authorize` (ruling 114, `gzkit.mx.tag_out`), `gz wp order commence` (ruling 144), `gz wp dispatch --void` (`WPR:830-854`, *"Book that the coordinator abandoned a dispatch"*); no persona file | RULED: *"Book A as stated (Recommended)"* (`REC:1721`, 2026-10-26); mechanics *"A. yes ..."* (`REC:616-619`); ruling 114: *"the coordinator is never dispatched: it is the operator-facing session, which carries no stamp"* (`KIT:646`) |
| Authorizing Officer (duty) | TUM App B: *"The person with the authority to sign for issuing or clearing tags and labels."* | `MAT:37`; `REC:967-968`, `REC:1082-1094` | `gz wp tag issue`, `authorize` | RULED: operator *"A"*, 2026-10-25 (`REC:1088-1089`); ruling 6 *"**Issue** by the coordinator as Authorizing Officer"* (`KIT:431`) |
| craftsman | *"One **craftsman** persona carrying the trade ... Two **positions**, **repair** and **restoration**"*; JFMM: *"A mechanic or other individual trained in QA methods and procedures"* | `REC:1458-1490`; `MAT:38`, `:40`; `KIT:22` | `WPR:85-86` (comment), `WPR:98` `_CRAFTSMAN = frozenset({REPAIR, RESTORATION})`, `WPR:423-461` `_craftsman_subject`; no persona file | RULED: operator *"A"*, 2026-10-25 (`REC:1474`); ruling 109 *"A: two roles (Rec.)"*, 2026-11-16 (`KIT:634`). Open tension stated by ruling 175 (`KIT:770`): *"the record's craftsman performs the repair ... while the runtime gives the work after commencement to `Implementer`, a tension this ruling leaves standing"* |
| repair (position) | resists *"bias toward the present shape"* (`REC:1467`); dispatched on a frozen order to hang its tags (ruling 108) | `REC:1465-1467`; `KIT:632`, `:681` | `REPAIR = "Repair"` `WPR:83`; frozen order only `WPR:436-442` | RULED (rulings 108, 109, 131) |
| restoration (position) | resists *"green by the wrong route"*; clears tags on a commenced (or paused-carry) order | `REC:1467`; `KIT:683` | `RESTORATION = "Restoration"` `WPR:84`; `WPR:443-450` | RULED (rulings 109, 132, 187) |
| repair activity / Ship's Force (sides) | *"The sides keep the Navy's names, **repair activity** and **Ship's Force**"* | `REC:1469-1470`, `:1485-1486`; `MAT:38`, `:40` | none | RULED (with A, `REC:1474`); liberties marked `MAT:38`, `:40` |
| Quality Assurance Inspector (QAI) | JFMM: *"The designated individual(s) in FMA and ship work centers who inspect the work of other individuals, not their own work."*; gzkit's separated from the coordinator line | `REC:1492-1512`; `MAT:39` (A5); `KIT:22`; rulings 14 to 16 | **none**: no QAI role in `ROLES` (`WPR:87-94`); floor row 3 *"Nothing: `--role` is a value the caller supplies"* (`KIT:50`); `src/gzkit/events.py:2120` comment *"refused by the writer until O6's QAI dispatch"* | RULED: operator *"A"*, 2026-10-25 (`REC:1509`); not built (O6, O8) |
| inspector | the earlier name, *"one inspector whose standard is the job order and the lockout log"* | `REC:361-375`; the level table *"Coordinator, inspector, operator"* (`drydock-taxonomy.md:25`) | none | RULED (operator *"A"*, `REC:372`), its title then ruled QAI (A5) |
| surveillance / surveillant | *"a stop request from outside the chain becomes a runtime hold"*; *"the one who performs it is the **surveillant**"* | `REC:1667-1694`; `MAT:42` (A8); rulings 23, 24 (`KIT:449-450`) | tag source `surveillant-stop` only: `src/gzkit/events.py:2105`, `src/gzkit/cli/parser_wp_tag.py:132`; no dispatch, persona or hold (floor row 13 *"Nothing"*) | RULED: *"A: request becomes hold (Recommended)"*, 2026-10-26 (`REC:1682`); ruling 23 *"A"*, ruling 24 *"A"*, 2026-11-04 |
| affected party | operator, 2026-10-26: *"affected parties aee: the operator, plus all gzkit (or adopting system's) agents, control surfaces and rules designed to enforce system behavior, and, when applicable, all end users of an adopting system."* | `REC:1842-1866`; `MAT:41` (A7) | none | RULED (`REC:1848-1850`); departs from OSHA's *affected employee* (`REC:1830-1834`) |
| second person | *"an independent check by someone who neither did nor accompanied the work, which covers the pipeline's spec and quality reviewers"* | `REC:2414-2436`; `MAT:67` (C3) | none: *"a review carries no tier"* (floor row 11, `KIT:58`) | RULED: *"A: three tiers (Recommended)"*, 2026-10-26 (`REC:2430`) |
| (V) verification / (I) inspection | *"In gzkit, *verification* is the (V) tier and *inspection* is the (I) tier."* | `REC:2433-2436`; `MAT:67` | none (O6) | RULED (as above) |
| performer | the dispatch that books a maintenance-record entry; *"an `Implementer`, `SingleDriver` or `Restoration` dispatch on the order"* | rulings 167, 175 (`KIT:753`, `:770`) | `gzkit.mx.entries.record_entry_book` (per `KIT:420`) | RULED (ruling 175 *"A: Who did the work (Rec.)"*, 2026-11-20); see the SingleDriver contradiction |
| position | Part 0: *"Position. An obligation and a role to fulfil it. [...] Every agent is crew, the orchestrating session included."*; ruling 1: *"A position is told by its dispatch record"* | quoted `REC:880-881`; `KIT:426` | the dispatch record, `DispatchRecord` `WPR:138-150` (`role` field described *"The position dispatched"*, `WPR:145`) | RULED: Part 0 ratified (secondhand, as above); ruling 1 *"Dispatch record (Recommended)"* (`KIT:426`) |
| crew | Part 0: *"Crew. The actor implementing within the role's bounds and under its auspices."* | quoted `REC:1453-1454` | none | RULED (Part 0, secondhand) |
| dispatch / dispatch id | *"The runtime mints a dispatch id on `work_package_dispatched`, bound to the position, the subject and the intended root"* | ruling 1, `KIT:426` | `WPR:589-636` (`dispatch_id = f"D-{secrets.token_hex(8)}"`, `WPR:630`) | RULED (ruling 1) |

### 4b. The persona files and the dispatch role sets

`AGENTS.md` § Persona: *"Every agent frame MUST include a Persona. Default: `main-session`"*. No operator ruling
on any persona file's content was found in the files read (the kit and record discuss only the four kit personas
and the per-file cap, `REC:706-716`).

| Term | Meaning as stated | Defined at | In code | Maps to a kit position? | Status |
|---|---|---|---|---|---|
| main-session (persona) | *"the primary Claude Code session — the operator-facing agent that reads briefs, composes plans, executes pipelines, and maintains governance state"* | `.gzkit/personas/main-session.md:28-30` | named by `persona:` on skills (`CMS:204`) | **no ruling maps it.** Nearest: the coordinator, *"the operator-facing session"*; but the coordinator *"performs no work itself"* (`REC:608-609`) where main-session *"executes pipelines"* | SOURCED |
| implementer (persona) | *"operating in the Implementer role during pipeline dispatch"* | `.gzkit/personas/implementer.md:33-34` | `ROLE_PERSONA_MAP["Implementer"] = "implementer"` (`src/gzkit/pipeline_dispatch.py:30`) | no kit position; ruling 175 says repair work after commencement runs as an `Implementer` dispatch, against A4's craftsman (tension stated in the ruling) | SOURCED |
| spec-reviewer (persona) | *"operating in the Spec Reviewer role during pipeline dispatch"* | `.gzkit/personas/spec-reviewer.md:25-26` | `ROLE_PERSONA_MAP["Reviewer"] = "spec-reviewer"` (`pipeline_dispatch.py:31`) | the **second person** tier (C3: *"which covers the pipeline's spec and quality reviewers"*, `REC:2421-2422`) | SOURCED |
| quality-reviewer (persona) | *"operating in the Quality Reviewer role during pipeline dispatch"* | `.gzkit/personas/quality-reviewer.md:25-26` | `ROLE_PERSONA_MAP["QualityReviewer"]` (`pipeline_dispatch.py:32`) | second person (as above) | SOURCED |
| narrator (persona) | *"operating in the Narrator role during pipeline ceremony and evidence presentation"* | `.gzkit/personas/narrator.md:30-31` | `ROLE_PERSONA_MAP["Narrator"]` (`pipeline_dispatch.py:33`) | no kit position | SOURCED |
| pipeline-orchestrator (persona) | *"an agent orchestrating any structured governance ceremony with sequential-step semantics"* | `.gzkit/personas/pipeline-orchestrator.md:36-43` | named by `persona:` on skills (`CMS:91`) | no; ruled not the contractors (`REC:142-147`), and its word *orchestrator* is the coordinator's rejected synonym (ruling 21; `REC:597-598`) | SOURCED |
| flight-test-engineer (persona) | *"an agent flying a gzkit flight-test sortie against a target substrate"*; its verdicts belong to *"an independent Chase"* and the *"human test director"* | `.gzkit/personas/flight-test-engineer.md:36-41`, `:29-31` | named by `gz-flighttest` (`CMS:121`) | no kit position (its Chase and test director are its own) | SOURCED |
| Chase / test director | the independent verdict-reader; the human holding Go/No-Go and Gate 5 | `flight-test-engineer.md:29-31`, `:49` | none | n/a | SOURCED (persona-local) |
| dispatch roles (kit runtime), the closed set | **six**: `Implementer`, `SpecReviewer`, `QualityReviewer`, `SingleDriver`, `Repair`, `Restoration` | `WPR:81-94`; ruling 109 *"`gz wp dispatch --role` knows only `Implementer`, `SpecReviewer`, `QualityReviewer` and `SingleDriver`"* before Repair and Restoration were added (`KIT:634`) | `WPR:87-94`, refused outside it at `WPR:508-510` | n/a | **CONTRADICTED**: `drydock-taxonomy.md:77` *"Dispatch roles: `Implementer, SingleDriver, Repair, Restoration` (`work_package_run.py`)"* omits `SpecReviewer` and `QualityReviewer` |
| Implementer (dispatch role) | an implementing dispatch; counts toward the fix-cycle bound (`WPR:96`, `:611-620`) | `WPR:81`, `:96` | as stated | — | RULED (named in ruling 175, operator *"A: Who did the work (Rec.)"*, 2026-11-20) |
| SingleDriver (dispatch role) | *"A single-driver dispatch carries its reason, and only it does."* | `WPR:82`, `:513-517`; `DispatchRequest.reason` *"Why the run is single-driver"* (`WPR:133`) | refused on any repair package: `WPR:514-515` *"is a repair package: nobody inspects their own work."* | — | **CONTRADICTED**: ruling 175 (`KIT:770`) *"`_order_subject` gives every other role a commenced order and a REQ its freeze holds, so the repair work itself runs as an `Implementer` or `SingleDriver` dispatch. So `gz wp entry book` ... take a call stamped as an `Implementer`, `SingleDriver` or `Restoration` dispatch on the order"*. But `_check_role` runs before `_dispatch_subject` (`WPR:600-601`) and refuses `SingleDriver` on every repair package, and orders exist only on repair packages (`WPR:400-405`), so no SingleDriver dispatch on an order can be booked; the entry rule's SingleDriver arm is unreachable |
| SpecReviewer (dispatch role) | a reviewing dispatch; arms fix cycles (`WPR:97`, `:357-361`) | `WPR:89`, `:97` | as stated | second person | **CONTRADICTED** (naming): the pipeline calls the same role `"Reviewer"` (`ROLE_PERSONA_MAP`, `pipeline_dispatch.py:31`) and `src/gzkit/roles.py:130` `RoleName = Literal["Planner", "Implementer", "Reviewer", "Narrator"]`, where Reviewer holds *"Two sub-roles: Spec Compliance Reviewer ... and Code Quality Reviewer"*; the kit runtime spells `SpecReviewer` and treats QualityReviewer as a peer |
| QualityReviewer (dispatch role) | a reviewing dispatch | `WPR:90`, `:97` | as stated; `pipeline_dispatch.py:32` | second person | SOURCED (a sub-role, not a peer, in `roles.py`; see SpecReviewer) |
| Repair / Restoration (dispatch roles) | the craftsman's two positions as roles | `WPR:83-84`; ruling 109 | `_craftsman_subject` `WPR:423-461`; *"A Repair or Restoration dispatch is not a review and arms nothing"* `WPR:343-344` | repair, restoration | RULED (ruling 109, *"A: two roles (Rec.)"*, 2026-11-16) |
| Planner / Reviewer / Narrator (universal roles) | *"four universal agent roles — Planner, Implementer, Reviewer, Narrator"* | `src/gzkit/roles.py:3-4`, `:130-132` | as stated | Planner: no persona file and in no dispatch map | SOURCED (a third role vocabulary beside `ROLE_PERSONA_MAP` and `ROLES`) |
| agent definitions | five roles: `git-sync-repo`, `implementer`, `narrator`, `quality-reviewer`, `spec-reviewer` | `.gzkit/agents/roles.json`; `CMS:212-229` | `.claude/agents/*.md`, `.codex/agents/*.toml` | as the personas | SOURCED |

## Domain 5: the crosswalk, the matrix's terms and the rejected synonyms

**The crosswalk JSON has not landed.** Ruling 20 (`KIT:446`, operator *"A"*, 2026-11-04): *"Its rows live in
`data/maintenance_crosswalk.json` ... a page under `docs/governance/` renders them as a Layer 3 view"*.
Listed `data/` (63 entries) and `data/catalog/` (seven stores: `delivery_events`, `externals`, `families`,
`orders`, `outcomes`, `reqs`, `work_packages`); no crosswalk file. A text search of `data/`, `src/gzkit/` and
`.gzkit/` for *crosswalk* hits only five handoff files and `.gzkit/handoffs/rulings.jsonl` (not read). Until
it lands, the only row-by-row source is `MAT`, which says of itself (`MAT:7`): *"A view drafted by the agent.
It holds no authority and rules nothing."* `orders.json` and `reqs.json` hold empty arrays, read in full.

| Term | Meaning as stated | Defined at | In code | Status |
|---|---|---|---|---|
| crosswalk (vocabulary) | *"inside the hangar and drydock the maintenance vocabulary governs, Part 0 governs the force, one recorded crosswalk binds them row by row and is canon"* | `REC:1045-1053`; ruling 20 `KIT:446` | **absent** (`data/maintenance_crosswalk.json` does not exist) | RULED: *"D, yes."* (`REC:1050`); home ruling 20 *"A"*. Not built |
| crosswalk (pipeline) | *"a crosswalk in this record from each pipeline stage to the kit act it carries"* | `REC:3084-3117`; `REV:111-113` | none | RULED: operator *"A"* (`REC:3092`). A second thing under the same name (collision, below) |
| term witness | a `gz check` validator refusing an undeclared term, an unresolved declared term, and any rejected synonym, in the kit personas and skill | ruling 21, `KIT:447` | none (floor row 12 *"Nothing: no crosswalk or term witness exists"*, `KIT:59`) | RULED (ruling 21 *"A"*). Not built |
| the text's own term (rule) | *"the text's term wherever one exists, the operator's words kept only where the texts have none ... each departure recorded with its rejected synonym"* | `REC:589-603` | none | RULED: operator *"A"* (`REC:594`) |
| liberty (standing) | *"the term is taken with a departure from its source, and the departure is stated"* | `MAT:19`; standings ruled/held/proposed/contested/gap `MAT:15-20` | none | SOURCED (in a view) |
| ruled / sourced / contradicted / unsourced | the review's four markings of a name | `REV:5-6` | none | SOURCED; the draft taxonomy's § 9 reuses the four (`drydock-taxonomy.md:121`) |
| approval for return to service | *"bounded "only for the work performed""*; Part 0: *"Release. The captain's signature on what ships; in gzkit, Gate 5 attestation, which is return to service."* | `MAT:36` (A2); `REC:882-883` | none | **CONTRADICTED**: Part 0 and A2 make Gate 5 *the* return to service; RP-12 separates them: ruling 2 *"Gate 5 at the order. The package closes at return to service, the operator's separate act"* (`KIT:427`), ruling 14 *"Return to service at the package's close reads every order's final inspection and Gate 5"* (`KIT:439`), ruling 32 lists return to service among the operator's acts apart from Gate 5 (`KIT:479`) |
| contract | *"changes only by its own amendment, never through a repair order's specification"* | `MAT:48` (B1); `REC:2899-2913` | `mx_contract_amended` booking (`REC:2904-2905`) | RULED: operator *"A"*, 2026-10-27 (`REC:2906`) |
| work package | *"the bundle: its formal work package (B3), its objective quality evidence (B4), its task cards (B5); every package a controlled work package from opening"* | `MAT:49` (B2); `REC:1243-1289` | `data/catalog/work_packages.json` (`_doc`) | RULED: *"okay, A"* (`REC:1262`), CWP *"yes to your correction"* (`REC:1278`) |
| formal work package (FWP) | *"initial conditions (what is tagged out), procedure, test and inspection (the dock trial), system restoration"* | `MAT:50` (B3) | the store's four sections (`work_packages.json` `_doc`) | RULED (by construction, question 24 A) |
| objective quality evidence (OQE); controlled work package (CWP) | JFMM: *"Any statement of fact ... which can be verified"*; CWP = FWP + OQE | `MAT:51` (B4); `REC:1009-1017` | `oqe` field in the store | RULED (question 24); liberty: CWP for every package |
| task card | *"One slice sized to an agent's context: one commit, one trailer, the REQ ids it drives"* | `MAT:52` (B5) | `WP-01-astral-toolchain.procedure` *"Task cards: RO-9 tranches 1 to 7"* (`data/catalog/work_packages.json`) | **CONTRADICTED**: `MAT:52` *"ruled (2026-10-05)"*; `REV:120` lists *task card* under *"Ruled and sourced"*; `REC:1255-1256` the bundle ruling holds *"the procedure as task cards"*; but ruling 21 (`KIT:447`) lists *task card* among the crosswalk's rejected synonyms, and ruling 25 (`KIT:451`) reads *"what an act was is a task"*. No ruling read names the retirement of *task card* or its replacement |
| tag-out log; line item; Danger tag; Caution tag | TUM: *"An individual entry in a tag-out that details the isolation, hazards, and work required"*; Danger *"A red tag prohibiting operation"*; Caution *"A yellow tag"* | `MAT:53` (B6); `REC:1082-1094` | `gzkit.mx.tag_out`; `TAG_ID_PATTERN` (`events.py`); class `Danger \| Caution` | RULED: operator *"A"* (`REC:1088-1089`) |
| maintenance record | 14 CFR 43.9(a): description, date, performer, approver | `MAT:54` (B7); ruling 8 `KIT:433` | `gzkit.mx.entries`, `ENT-<NN>-<slug>` | RULED (ruling 8 *"A"*; ruling 166 *"A: Subsume (Rec.)"*) |
| re-entry control | offered as the Navy's name for work on a certified boundary | `MAT:54` | none | SOURCED (a *liberty*, not adopted as gzkit's name) |
| list of discrepancies; discrepancy | *"each line a **discrepancy**, graded *blocks return to service* or *due by a named event*"* | `MAT:55` (B8); `REC:1536-1563` | `gzkit.mx.discrepancies`, `DSC-<NN>-<slug>` | RULED: *"B′"*, 2026-10-25 (`REC:1558`) |
| alteration; configuration change; departure from specification (DFS); deviation; waiver | alteration *"the planned remodel, approved before work and accounted for at close as a **configuration change**"*; DFS *"only where the work cannot meet its own spec; a deviation (before) or waiver (after)"* | `MAT:56` (B9); `REC:1366-1394` | `departures` on packages; `gz wp change --rung alteration/departure` | RULED: *"okay, A is it"* (`REC:1381`) |
| change ladder: pen and ink, change order, attachment, supplement | the four rungs, change order the operator's alone | `MAT:57` (B10); `REC:1291-1329` | `gz wp change` rungs (`work_package_ledger.py`, per `KIT:61`) | RULED: *"B avoids collision and fits"* (`REC:1316`). (Rungs as terms are § 9 item 2's) |
| work package log | *"a view over the store and the issues"*, never edited | `MAT:58` (B11); `REC:2915-2931` | none built (*"its producer is diamond-2 work"*) | RULED: operator *"A"* (`REC:2921-2922`) |
| problem report; recorded, classified, resolved, closed | AC 00-71's states; *"the fix commit resolves, and only a review ... closes"* | `MAT:59` (B12); `REC:3059-3082` | none (diamond 2) | RULED: operator *"A"* (`REC:3073`); *GHI* and *write-up* kept |
| initiated; commencement of work | *"**initiated** ... is the operator's opening of the package; **commencement of work** is the coordinator's act once the tags hang"* | `MAT:65` (C1); `REC:2933-2949` | `gz wp initiate`; `gz wp order commence` (`_check_commenced`) | RULED: operator *"A"* (`REC:2941`) |
| issued; hanging (hung) | *"the tag-out line item **issued**, then **hanging**"* | `MAT:66` (C2) | `gz wp tag issue`, `hang` | RULED (`MAT:66`; ruling 6) |
| stop work | *"a recorded package event with a trigger from a closed list, routed to its resolver"* | `MAT:68` (C4); `REC:1769-1795` | none yet (O5; floor row 4 *"no stop or hold record exists"*) | RULED: *"A: routed by trigger (Recommended)"* (`REC:1787`) |
| rework; buy-back | *"**rework** for the repair activity's repeat, **buy-back** for the inspector's reinspection"* | `MAT:69` (C5); `REC:2951-2968` | none (O6; floor row 5 *"Partial"*) | RULED: operator *"A"* (`REC:2960`) |
| countermand | *"by the operator alone"* | `MAT:70` (C6) | none | RULED (`MAT:70`, sourced § 121.369(b)(8)) |
| work complete; clearance authorized; cleared; tags removed | the four clearing states | `MAT:71` (C7) | `gz wp tag authorize`, `clear` | RULED (`MAT:71`) |
| dock trial; sea trial | JFMM: *"Dock Trials are those ship trials conducted at the Industrial Activity to determine the ability of the ship ... to conduct Sea Trials safely."*; sea trial gates exit in two forms | `MAT:72-73` (C8, C9); `REC:633-679` | none | RULED: sea trial *"A"* (`REC:675`). (Drydock vocabulary is § 9 item 1's) |
| final inspection and acceptance; closed | *"the inspector's final inspection checks the record complete and every tag cleared, the operator's acceptance is Gate 5"* | `MAT:74` (C10); `REC:2970-2991` | `gz wp order accept`, `close` | RULED: operator *"b"* (`REC:2981`); moved to the order by ruling 14 (`KIT:439`) |
| shift turnover | *"the tag-out log reviewed at every relief"*; *"every hung tag transfers by name"* | `MAT:75` (C11); `REC:2993-3016` | none (O7; floor row 7 *"Nothing"*) | RULED: operator *"a"* (`REC:3007`); its transfer by name amended by ruling 3 |
| handback; transfer of custody | *"every open line item and every DFS enumerated, or *none* stated"* | `MAT:76` (C12); `REC:3018-3040` | none (floor row 15 *"Nothing"*) | RULED: operator *"A"* (`REC:3030`) |
| drydock | *"A drydock session is one `mx_session_opened` to `mx_session_closed` span with `mode: safe` and its contract"* | `MAT:77` (C13); `REC:3042-3057` | the marker's level | RULED (Part 0; doctrine) |
| suspension; reinstatement | the Navy analogue for entering and leaving safe mode | `MAT:78` (C14) | none | SOURCED (*"noted"*, not adopted) |
| standby | *"safe mode's command to modules to **reduce their level of operational compliance**"* | `REC:2251-2254` | none | RULED (in principle, `REC:2243`); *"Standby is still unsourced"* as a text term (`REC:2086-2087`) |
| Minimum Equipment List (MEL); (M) procedure; (O) limitation; placard | AC 91-67 ¶ 6r, 6t; one entry per control | `REC:2057-2096`, amended `REC:2119-2139`, `:2841-2859` | none (RP-13 F1) | RULED: *"A: MEL with Meyer levels (Recommended)"* (`REC:2079`) |
| accepted and lowered / not yet accepted | a control's state under the one condition | `REC:2461-2480` | none | RULED: *"A: one condition (Recommended)"* (`REC:2472`) |

### 5a. Rejected synonyms, with their rulings

| Rejected | Replaced by | Ruling (verbatim, place) | Still in live use? |
|---|---|---|---|
| *repairer* | craftsman, repair position | *"*Repairer* and *restorer* are retired as role names."* (`REC:1485`, ruling A, 2026-10-25); `MAT:38`; ruling 21 list | `ledger_producer_probe.py:1060` names a variable `restorer` (code, outside ruling 21's scope) |
| *restorer* | craftsman, restoration position | as above; `MAT:40` | `data/catalog/work_packages.json` WP-01 `system_restoration`: *"cleared by the restoration contractor"* |
| *task card* | not named | ruling 21 list (`KIT:447`) | **contradicts** `MAT:52`, `REV:120`, the store's WP-01 `procedure` (see CONTRADICTED row) |
| *fix cycle* | rework + buy-back | C5: *"**fix cycle** is retired for this record."* (`REC:2962`, operator *"A"*); `REV:133`; ruling 21 list | **yes, in the kit itself and the code**: ruling 57 (`KIT:530`) *"the fix-cycle bound counts against that subject"*, ruling 72 (`KIT:560`), ruling 132 (`KIT:683`); `WPR:336` `count_fix_cycles`, `WPR:618` refusal text *"fix cycles"*, `events.py:1793` *"The exits from the fix-cycle bound"*. C5's commission *"the pipeline's fix-cycle wording is drafted to the two terms"* (`REC:2966-2967`) is not carried out |
| *punch list* | list of discrepancies | *"B′"* (`REC:1558`); `MAT:55` *"*punch list* retired, unsourced"*; ruling 21 list | the safe-mode banner text, `src/gzkit/mx/awareness.py:20-24` (quoted `CMS:296`): *"what it breaks goes on the punch list"* |
| *orchestrator* (for the coordinator) | coordinator | *"rejected: *orchestrator*, which collides with `pipeline-orchestrator`"* (`REC:597-598`, the text's-own-term ruling *"A"*); ruling 21 list | allowed elsewhere: the `pipeline-orchestrator` persona; `src/gzkit/roles.py:7` *"the pipeline orchestrator"* |
| *job order* (as gzkit's name) | formal work package; kept as DFARS's term | *"*job order*, held since question 10, is superseded as gzkit's name"* (`REC:1324-1326`); `REV:131` | none found |
| *lockout*, *lockout log* | tag-out, tag-out log | *"Amends the names in questions 6, 19 and 20 (lockout → tag-out; lockout log → tag-out log)"* (`REC:1091`, operator *"A"*) | none found |
| *compliance register* | the three records | `REC:823-844` (operator *"A"*) | `REC:3213-3214`: the contract and brief still said *"§ Punch list (the compliance register)"* on 2026-10-27 (not re-measured here) |
| *register* (inside the hangar) | work package log | *"**register** is retired inside the hangar for this record."* (`REC:2924`, operator *"A"*) | not measured |
| *closeout review* | final inspection and acceptance | *"The matrix's *closeout review* is not taken"* (`REC:2983`, operator *"b"*) | none found |
| *position relief briefing* | shift turnover (handoff kept) | *"The Part 0 candidate *position relief briefing* is not taken."* (`REC:3009-3010`, operator *"a"*) | none found |
| *Contracting Officer* | the operator, the commander | *"*Contracting Officer*, held since question 13, is withdrawn."* (`REC:1531-1532`) | none found |
| *Commanding Officer*, *operational commander* | kept only as other texts' names in the crosswalk | `REC:1529-1531` | none |
| *integrator* (for the restorer) | not taken | *"*integrator* offered by the operator for the restorer, not taken"* (`REC:599`) | none |
| *restoration activity*, *resolution activity* | Ship's Force | *"*Restoration activity* is not adopted, and *Ship's Force* is the restoring side."* (`REC:1485-1486`) | none |
| *availability* | not taken | *"*Availability* is not taken: Volume V never defines it."* (`REC:3053`) | none |
| *factory floor* (as a signal value) | a control's *not yet accepted* state | *"The factory floor is no longer a value of the signal."* (`REC:2474-2476`, operator *"A: one condition"*); `REV:133-134` | none |
| *affected employee* (OSHA) | affected party (departure recorded) | `REC:1830-1834`, `MAT:41` | none |
| *work order* | work package (2026-10-16) | Part 0 as quoted `REC:1138-1139`: *"the term "work order" was retired on 2026-10-16 (verbatim: 'retire it, work package everywhere')"* | **contradicted** by the level table (`drydock-taxonomy.md:25`, *"Work order"* at the Order level) and ruling 43 (`KIT:501`, *"the same grammar serves a work order and a repair order"*) |

## Contradictions

1. **tripwire**: the code census defines it as *"any other blocking check"* (`CCC:70`); RP-10 defines it as a check that *"does not stop the work and does not ring; it records"* (`RO10:49`), and the record maps the Caution tag to *"a tripwire that records"* (`REC:1084-1085`, ruled *"A"*).
2. **alarm**: the census defines it as *"when it only announces or warns"* (`CCC:70-71`); RP-10 (`RO10:49`, *"An **alarm** stops the work."*), the doctrine's alarm test (`safe-mode-doctrine.md:28`) and the code's `gzkit.mx.alarms` (which switches off blocking hooks) all use the opposite sense. RO-13's retrofit order (*"Alarms, gates, then safeguards, monitors and tripwires"*, `harbor-ro13-mode-contract.md:54`) is ruled on the census's names, so the order rests on contested definitions.
3. **Dispatch roles**: the draft taxonomy lists four (`drydock-taxonomy.md:77`); `WPR:87-94` holds six (`SpecReviewer` and `QualityReviewer` omitted).
4. **SingleDriver on an order**: ruling 175 (`KIT:770`) says repair work runs as an `Implementer` or `SingleDriver` dispatch and admits SingleDriver entries; `WPR:514-515` refuses SingleDriver on every repair package before the order is read, so the arm cannot be reached.
5. **Reviewer role naming**: `SpecReviewer` (`WPR:89`) against `"Reviewer"` (`pipeline_dispatch.py:31`; `roles.py:130`, where Spec and Quality are sub-roles of one Reviewer). Three role vocabularies stand: `roles.py` (Planner, Implementer, Reviewer, Narrator), `ROLE_PERSONA_MAP` (Implementer, Reviewer, QualityReviewer, Narrator), `ROLES` (the six).
6. **task card**: ruled 2026-10-05 and *"Ruled and sourced"* (`MAT:52`, `REV:120`, `REC:1255-1256`, the WP-01 store), yet listed as a rejected synonym by kit ruling 21 (`KIT:447`), with no ruling naming its retirement or replacement.
7. **fix cycle**: retired (C5, `REC:2962`; ruling 21) yet used by the kit's own later rulings 57, 72 and 132 and by the runtime (`WPR:336`, `:618`; `events.py:1793`).
8. **Return to service**: Part 0 (`REC:882-883`) and matrix A2 (`MAT:36`) equate it with Gate 5; RP-12 rulings 2, 14 and 32 (`KIT:427`, `:439`, `:479`) separate it, Gate 5 at the order and return to service at the package's close as a separate operator act.
9. **work order**: retired 2026-10-16 (Part 0, quoted `REC:1138-1139`); reused at the Order level of the canon level table (`drydock-taxonomy.md:25`) and in ruling 43 (`KIT:501`).
10. **The craftsman and the repair work** (stated by the ruling itself, not resolved): A4 has the craftsman perform the repair (`REC:1463-1467`; `KIT:22`); ruling 175 (`KIT:770`) records that the runtime gives post-commencement repair work to `Implementer`, *"a tension this ruling leaves standing"*.

**Collisions (one word, two ruled senses; not contradictions):** *crosswalk* (the vocabulary crosswalk, ruling 20, against the pipeline-stage crosswalk, `REC:3084-3117`); *gate* (the census's control role against Gates 1 to 5 and the model census's *gate procedure*); *safeguard* (the census role against `.claude/rules/agent-failure-modes.md`'s *"Safeguard circumvention"*, a guardrail in general); *act* (ruling 25 maps an old act to a task, `KIT:451`, but the kit keeps *act* as a unit inside a task, e.g. ruling 54 *"Every act of O2 task 3"*, `KIT:524`; that is § 9 item 6's domain).

**Unmapped:** no ruling maps `main-session` (*"executes pipelines"*, `main-session.md:29-30`) to the coordinator (*"performs no work itself"*, `REC:608-609`), though both are *"the operator-facing"* session. `implementer`, `narrator`, `pipeline-orchestrator` and `flight-test-engineer` map to no kit position; `spec-reviewer` and `quality-reviewer` map to the second-person tier by C3 alone.

**Not built, though ruled:** the four kit personas (ruling 23), `gz-repair-pipeline` (ruling 22), the crosswalk JSON and its view (ruling 20), the term witness (ruling 21), the QAI dispatch (rulings 14 to 16), the surveillance dispatch (ruling 24). All are O6 or O8 (`KIT:460`, `:462`).

## Files read in full, with line counts

| File | Lines | How read |
|---|---|---|
| `docs/governance/drydock-taxonomy.md` | 149 | whole |
| `docs/rnd/contractor-kit/sources/census-code-controls.md` | 870 | whole, except the enforcement-claim table rows E1 to E134 (lines 473 to 606), read by tallying their role column (131 *"safeguard (negative control)"*, 3 *"safeguard (GATE5 NC)"*) and listing their claim ids, not row by row |
| `docs/rnd/contractor-kit/sources/census-model-surfaces.md` | 550 | whole; skill rows 141 to 158 read in their name, role and persona columns only |
| `docs/governance/harbor-ro12-contractor-kit.md` | 828 | whole |
| `docs/rnd/contractor-kit.md` | 3404 | whole |
| `docs/rnd/contractor-kit/vocabulary-matrix.md` | 105 | whole |
| `docs/rnd/contractor-kit/review.md` | 161 | whole |
| `docs/rnd/contractor-kit/defect-review.md` | 75 | whole |
| `docs/governance/harbor-ro10-safe-mode-classification.md` | 84 | whole (read for the alarm and tripwire definitions) |
| `.gzkit/personas/flight-test-engineer.md` | 57 | whole |
| `.gzkit/personas/implementer.md` | 52 | whole |
| `.gzkit/personas/main-session.md` | 43 | whole |
| `.gzkit/personas/narrator.md` | 47 | whole |
| `.gzkit/personas/pipeline-orchestrator.md` | 59 | whole |
| `.gzkit/personas/quality-reviewer.md` | 49 | whole |
| `.gzkit/personas/spec-reviewer.md` | 49 | whole |
| `src/gzkit/work_package_run.py` | 1108 | whole |
| `data/catalog/orders.json`, `data/catalog/reqs.json` | — | whole (both hold empty arrays) |

**Read in part (not counted as full reads):** `src/gzkit/pipeline_dispatch.py` lines 15 to 54 (`ROLE_PERSONA_MAP`,
`_persona_frame`); `src/gzkit/roles.py` lines 1 to 15 and 125 to 160, and its role definitions by text search
(338 lines); `data/catalog/work_packages.json` (first 2,500 characters, the WP-01 record); `.gzkit/agents/roles.json`
(first 40 lines); `docs/governance/harbor-ro13-mode-contract.md`, `docs/governance/safe-mode-doctrine.md` and
`.gzkit/rules/mx-mode.md` by text search for the role words only; listings of `data/`, `data/catalog/`,
`.gzkit/personas/`, `.agents/personas/`, `.gzkit/skills/`.

**Not read, and cited only as quoted elsewhere:** `docs/rnd/renewing-vows/doctrine-merge.md` Part 0 (its terms
*captain*, *position*, *crew*, *release*, *work order* are taken from the record's quotations, `REC:863-889`,
`:1138-1139`, `:1453-1454`); the RP-14 specification, where `SingleDriver` was ruled; `docs/governance/ieee/requirements-model.md`;
`.gzkit/handoffs/rulings.jsonl`; `docs/governance/chore-class-system.md` (whose line 585 uses *tripwire* in
OpenAI's sense). A ruling on any term above could sit in one of these; the statuses hold only for the files read.

## Gap-fill (2026-11-22, on the coordinator's request; still read-only)

Three gaps closed: (1) Part 0 read whole; (2) every term and rejected synonym queried in the settled-ruling
corpus; (3) the census's 134 claim rows and its skill rows read in every column. Requirements-model and RP-14
were left to other tracks, as asked.

### G1. Part 0 read in full

`docs/rnd/renewing-vows/doctrine-merge.md` (797 lines) read whole. Part 0 is lines 70 to 476, header *"Part 0 —
Ratified 2026-10-10 (operator, verbatim: "ratify Part 0")"* (`doctrine-merge.md:70`). Its line 72 says the
canonical `docs/governance/GovZero/command-doctrine.md` *"now carries the statement of command, the terms ..."*
and *"the glossary is held here"*, so the canonical file's § Terms (`command-doctrine.md:49-69`, read) was
compared too. The file header still reads *"DRAFT. Not canon."* (`:3`) and Part 0 still carries a *"Candidate,
not canon"* block (`:74-79`) under its *Ratified* banner; both are stale beside line 72.

Terms I had taken from the record's quotations, checked against the primary:

| Term | Primary text | Result |
|---|---|---|
| captain | `doctrine-merge.md:106-109` and `command-doctrine.md:51-54`: *"**Captain.** The same human, as the holder of the signature and the override. The operator is both and is not crew. *(Ruling of 2026-10-08: 'i am commander and shape intent, i am not crew, but i am captain, you are crew'.)*"* | **Confirmed RULED**; the verbatim ruling (2026-10-08) is now cited from the primary. The corpus holds it too: *"Commander, captain and crew (verbatim: "i am commander ...")"* |
| position | `doctrine-merge.md:110-115`, `command-doctrine.md:55-60`, ruling 2026-10-08 *"the position is an obligation and a role to fulfill the obligation, the crew is the actor implementing within the bounds and auspices of that role"* | **Confirmed RULED** |
| crew | same entry: *"**Crew.** The actor implementing within the role's bounds and under its auspices. Every agent is crew, the orchestrating session included."* | **Confirmed RULED** |
| approval for return to service (Release) | Part 0 **was amended in place 2026-11-03**, `doctrine-merge.md:125-129`: *"Gate 5 attests each work or repair order's work; **return to service** is the operator's separate act at the return to service package's close"* (operator *"Option A"*; corpus: *"Return to service is a separate operator act at the return to service package's close, apart from each order's Gate 5 (verbatim: "Option A")"*, booked 2026-11-03). The canonical file was **not** amended: `command-doctrine.md:68-69` still reads *"in gzkit, Gate 5 attestation, which is return to service"* | **Stays CONTRADICTED, citations corrected.** Part 0 now agrees with RP-12. The disagreement is between the canonical command doctrine (`command-doctrine.md:68-69`) and matrix A2 (`MAT:36`) on one side, and Part 0 as amended plus RP-12 rulings 2, 14 and 32 on the other. Contradiction 8 is restated below |
| work order | `doctrine-merge.md:141-142`: *"the term "work order" was retired on 2026-10-16 (verbatim: 'retire it, work package everywhere')"*, **not amended**, while the same Part 0's 2026-11-03 amendment four lines up writes *"each work or repair order's work"* (`:126-127`) | **Changed: rejected → RULED (reinstated).** The corpus holds a later ruling, booked 2026-11-03 from `20261103T071527Z-rnd-repair-work-organization-review-next.md`: *"The work order is the OBPI's successor and the work package groups orders for cohesion, a correction (verbatim: "I'm saying that the WO IS the OBPI, which is a correction")."* What stays retired is the `WO-1` to `WO-11` names for packages (corpus: *"The work order retired: verbatim "retire it, work package everywhere - change now: 'WO-1 to WO-11' to WP""*). Contradiction 9 is restated below |
| task card | Part 0 glossary, `doctrine-merge.md:435`: ladder *"pool ADR; feature ADR; OBPI; TASK; release → change proposal; engineering order; work package; task card; block — ruled 2026-10-05; "work package" and "task card" sourced (AC 120-16G)"* | **Confirmed CONTRADICTED** (contradiction 6): Part 0 holds the 2026-10-05 ruling. The corpus's only *task card* hit is the bundle ruling (*"procedure as task cards"*) |
| position relief briefing | Part 0 glossary `doctrine-merge.md:401`: *"handoff → position relief briefing; transfer of position responsibility — sourced: JO 7110.65BB App. A"*; Part III § 5 (`:657-664`) | Rejected-synonym row stands: C11 (2026-10-27, operator *"a"*) did not take it. The Part 0 glossary row is not updated (no status change) |
| sea trial | Part 0 `doctrine-merge.md:136`: *"**Sea trial.** One work package run on a fresh install of the released wheel."* | **Changed: RULED → CONTRADICTED** (new contradiction 12) |

New terms from Part 0 that bear on roles and positions (not in the first pass):

| Term | Meaning as stated | Defined at | In code | Status |
|---|---|---|---|---|
| role | *"What the position gives its holder to fulfil the obligation; it has bounds and auspices, and the holder has no authority apart from it."* | `doctrine-merge.md:110-113`; `command-doctrine.md:55-57` | `DispatchRecord.role` *"The position dispatched"* (`WPR:145`) conflates position and role | RULED (2026-10-08, as for position) |
| the eight roles (the crew) | *"mission planning, mission constraints, target planning, infiltration, ordnance delivery, exfiltration, decontamination, BDA"* | `doctrine-merge.md:405`, `:630-637` | none | RULED: *"ruled 2026-10-08 as the crew"*; corpus, booked 2026-10-08: *"the operator's eight roles as the crew (verbatim: "i want both")"*. A fourth role vocabulary, mapped to no kit position and no dispatch role |
| orchestrating session | *"Every agent is crew, the orchestrating session included."*; glossary *"orchestrating session → operations centre"* | `doctrine-merge.md:113-114`, `:390` | none | RULED (the term, 2026-10-08); collides with ruling 21's rejection of *orchestrator* for the coordinator, which is the same operator-facing session |
| interlocks (hooks) | *"hooks → interlocks — term"* | `doctrine-merge.md:427`; item 13 *"Keep as gzkit's own terms ...: ... interlocks"* (`:467`) | `.claude/hooks`, pre-commit hooks | RULED (item 13, *"it stands"*, 2026-10-10) as gzkit's own term, *"not cited as doctrine"*. A control-role name the census does not use |
| qualified tools (gating validators) | *"gating validators → qualified tools — sourced: DO-330"* | `doctrine-merge.md:426` | `gz validate` | SOURCED (candidate glossary) |
| standing orders (rules) | *"rules → standing orders — ruled by line 2 of the statement"* | `doctrine-merge.md:428` | `.gzkit/rules/` | RULED (statement of command line 2, *"it stands, add the seventh"*) |
| procedures (skills) | *"skills → procedures — sourced: AC 120-71B"* | `doctrine-merge.md:429` | `.gzkit/skills/` | SOURCED |
| sortie (dispatch) | *"dispatch → sortie — sourced: JP 3-30 ("an operational flight by one aircraft")"* | `doctrine-merge.md:393` | the dispatch record | SOURCED |
| second opinion (Step 4b adversary) | *"Step 4b adversary → second opinion — term; not IV&V as IEEE 1012 defines it"* | `doctrine-merge.md:397` | none | SOURCED (a *term*). It is not one of C3's three tiers (`REC:2414-2436`) |
| gates (dropped: *objectives*) | *"gates → gates (dropped: objectives) — ruled 2026-10-10"* | `doctrine-merge.md:424`, `:470` | Gates 1 to 5 | RULED. Fixes *gate* as Gates 1 to 5, which strengthens the collision with the census's *gate* role |

New rejected synonyms from Part 0, with their ruling (item 13, `doctrine-merge.md:465-474`, *"it stands"*, 2026-10-10, unless noted):

| Rejected | Replaced by | Ruling text |
|---|---|---|
| *pilot flying*, *pilot monitoring* (for implementer and reviewers) | the eight roles | `:406` *"dropped ... AC 120-71B: the monitor works concurrently"*; `:471` *""pilot", "assessor" and "briefer" for any agent role (the eight roles name the crew)"* |
| *assessor*, *briefer* | the eight roles | as above |
| *watch* (for session) | position | `:402`, `:468` *"Drop: "watch" and "duty officer" (the position is the noun)"* |
| *duty officer* | position | as above; `:391` |
| *hazard log* | failure-mode taxonomy | `:418`, `:469` |
| *objectives* (for gates) | gates | `:424`, `:470` |
| *prioritised target list* | the campaign order | `:383`, `:472-473` (renamed) |
| *maintenance planning document* (for the chore registry) | the maintenance schedule | `:410`, `:473-474` (renamed) |
| *lockout* as a mode signal | the tag-out log carries isolation of one surface | RP-13 ruling 10, `harbor-ro13-mode-contract.md:33`: *"**Lockout is dropped as a mode signal** (operator: *"A"*)"*, 2026-10-31; corpus *"Lockout is dropped as a mode signal; the tag-out log carries isolation of a surface (verbatim: "A")"*. This amends the record's three signals *"safe mode, standby, lockout"* (`REC:1911-1913`, `:2086`) |

### G2. The settled-ruling corpus

`uv run gz handoff rulings --help` states *"Read-only — rulings are booked by `gz handoff create`"*. I ran
`uv run gz handoff rulings --search "<term>"` once for each of 152 search strings: every term and rejected
synonym, plus split forms such as `QAI`, `MEL` and `single-driver`. Raw output and counts are in
`(gathering scratch) gapB/` (`counts.tsv`, `r001.txt` to `r152.txt`). The corpus holds 2,463
rulings. Dates below are the booking `ts` of `.gzkit/handoffs/rulings.jsonl`, read for the matching lines
only. Every hit was read, except those of eight broad strings: `gate` 155, `operator` 193, `position` 56,
`contract` 46, `drydock` 40, `routing` 29, `advisory` 22, `canary` 18. I scanned those for definitional
wording and found none beyond the hits below; that is a scan, not a full read. Zero hits for 31 strings,
among them `safeguard`, `GATE5_INVARIANTS`, `affected party`, `Authorizing Officer`, `final inspection`,
`shift turnover`, `work package log`, `SpecReviewer`, `QualityReviewer`, `Planner`, `main-session`,
`pipeline-orchestrator`, `flight-test-engineer`, `closeout review`, `Contracting Officer`, `integrator`,
`factory floor` and `affected employee`. A zero means no booked ruling carries the string, not that none
was ever given.

Rulings my table lacked:

| Term | Ruling found (verbatim, booked) | Effect |
|---|---|---|
| dispatcher | *"One control per distinct check, wherever reached; the entry sits at the implementation and dispatchers inherit it (verbatim: "A")."* (2026-10-31), RP-13 ruling 2, `harbor-ro13-mode-contract.md:24`: *"A step, hook line or twin that only dispatches to it inherits that entry."* | **SOURCED → CONTRADICTED** (new contradiction 13) |
| gate, safeguard, tripwire, alarm, monitor (as a role label) | RP-13 ruling 5, `harbor-ro13-mode-contract.md:26`: *"**The operator rules a default level per role** (operator: *"a"*). An entry at its default is written by the craftsman and inspected by the QAI, role label included."*; ruling 8, `:29`: *"Self-test intervals are defaults per role and kind, in JSON"* (both booked 2026-10-31) | No status change: the definitions stay unruled (tripwire and alarm stay CONTRADICTED). But the role is now a **ruled field of every MEL entry and the key of two default tables** (RP-13 T0, `:50`), so the unruled, contested definitions are load-bearing |
| alarm | *"The alarm test decides between the line and out of service (verbatim: "the alarm test decides, and I like it")."* (2026-11-03) | Stays CONTRADICTED. The doctrine's sense of *alarm* (lowering one takes work out of service) now has an operator ruling behind it; the census's sense has none |
| tripwire | *"Three kinds of protection: ... old-structure checks go off, cheap ones as tripwires (verbatim: "1. yes; 2. yes; 3. yes, off" and "tripwires for the cheap ones, long ones fully off")."* | Already cited (`RO10:21-22`); no change |
| self-test | *"Self-test intervals are defaults per role and kind in JSON; lengthening past a default is on the operator's word (verbatim: "a")."*; *"The self-test chore is admitted in the foundation, and gz check re-runs the self-tests of controls a change touches (verbatim: "a")."* (2026-10-31; RP-13 rulings 8, 9) | RULED, two rulings added |
| not yet accepted | *"A modification is profound when any fact in the entry stops being true; the control drops to not yet accepted (verbatim: "a")."* (2026-10-31; RP-13 ruling 6) | RULED, ruling added; it also answers the record's open *"threshold for profound modification"* (`REC:2091`) |
| SingleDriver | *"The single-driver route splits by kind (verbatim: "a")."* (2026-10-31, source `20261031T114023Z-ro14-specified-bound-landed.md`) | Stays CONTRADICTED. The code's refusal on repair packages (`WPR:514-515`) has an RP-14 ruling behind it, and ruling 175 (2026-11-20) contradicts it |
| problem report | *"Interim GHI close under B12: a reviewer subagent confirms, then the agent closes (verbatim choice: "Reviewer subagent (Recommended)")."* (2026-10-28); *"A finding above a chore's level leaves the run as a problem report (verbatim: "A")."* | RULED, rulings added |
| placard | *"The placard is a broad MX safe-mode design question, not part of gz wp (verbatim: "that is a broad indictation during mx safemode, not a normal part of gz wp")"* | RULED, ruling added |
| handback | *"Contract exit 8 clears only blocking lines; the rest transfer at handback"*; *"A deferred finding stays on the list of discrepancies while the hangar is open and is handed to its owning outcome at the handback"*; *"H8, the hangar exit waits on lines graded blocks return to service; the handback transfers the rest (verbatim: "A: Reword to doctrine")"* | RULED, rulings added |
| return to service (package) | *"The top repair row is the return to service package; out of service is a flag (verbatim: "it should be called a return to service package")."*; *"Every opening of the marker has a return to service package (verbatim: "a")."* (2026-11-03) | Bears on the draft's T6 (*"Return to service package: none"*): two operator rulings name it |
| feature package, work package (levels) | *"The feature package is the epic and the work package, the mADR's successor, is the story ... (verbatim: "A wins because you elevate the feature pack to epic and keep the WP (mADR) as a story")."* (2026-11-03) | Not my domain's terms; drives new contradiction 11 |
| demote / pinned | *"The Stage-2 production-code fence NEVER demotes inside an open hangar ... (verbatim: "Never demotes - fix vocabulary")"* (2026-08-22); *"gz check's pass line names every guard the hangar demoted (verbatim: "A")."* | SOURCED → still SOURCED for the general term; two specific rulings added |
| coordinator | *"The coordinator is a new orchestration role ... (verbatim: "Provisionally, I accept A, but let's delve.")."* | Already covered; the operator's own words call it an *orchestration* role |
| Gate 5 (location) | *"Gate 5 is attested once at the work package's close, and that close moves the outcome (verbatim: "A")."* (2026-10-30, `20261030T054212Z-ga-redraw-eleven-rulings.md`) | Superseded by Gate 5 at the order (RP-12 rulings 2, 30; 2026-11-03 *"Option A"*) but still in the corpus, unmarked; new contradiction 14 |
| --approver | *"--approver and --operator stay typed names, the limit staying on the discrepancy list and any fix taken up for every human-act verb together (verbatim: "A")."* (2026-11-02) | Superseded two days later by ruling 32 (`KIT:479`, *"It replaces the typed `--approver operator` `gz wp change` reads today"*), still in the corpus; contradiction 14 |
| punch list / compliance register | *"The punch list is the compliance register (verbatim: "yes, that is fine, it works well ...")"* (2026-10-25) | Superseded by question 20 and B8, still in the corpus; contradiction 14 |

No corpus hit contradicts a status in the first pass beyond those listed. Searches for the personas and the
dispatch role names returned only pipeline-procedure rulings (for example, *"NEVER work an OBPI without
running it through the `gz-obpi-pipeline` skill, including Stage 2's implementer dispatch and the two-stage
spec-reviewer plus quality-reviewer review"*), none of which defines a persona or maps it to a kit position.

### G3. The census rows, read in full

**The 134 enforcement-claim rows** (`CCC:473-606`) were read row by row in all six columns. Every row's
role reads *"safeguard (negative control)"*, except E106 `gate5-ledger`, E107 `gate5-attestation-absence`
and E108 `grader-gaming`, which read *"safeguard (GATE5 NC)"*. Exempts: 57 `none`, 55 *"UNDECLARED (None)"*,
22 naming a sibling claim. Canary: 38 *"yes"*, 96 *"no (grandfathered)"*. Entrypoints: E1 to E104 in
`_qc_nc_entrypoints.py`, the rest across 17 modules (E105 `qc_binding.py:198` to E134
`gate_population_claims.py:106`). These match the census summary (`CCC:461-469`, `:620-621`). No status
changes. Two labels were missing from the first pass: *GATE5 NC*, the negative control of a floor member;
and *grandfathered*, a claim disclosed on `data/guard_canary_grandfather.json` with no canary. Both are
SOURCED (`CCC:613-616`, `:621`).

**The skill rows** (`CMS:86-158`) were read in all eight columns. The `persona:` column names five
personas: main-session, pipeline-orchestrator, flight-test-engineer, spec-reviewer (`gz-health-audit`, a
router, and `gz-intent-trace`) and quality-reviewer (`gz-obpi-simplify`, `gz-tech-debt-review`). No skill
names `implementer` or `narrator`, which agrees with `CMS:206`, `:209`. The spec-reviewer persona frames a
routing skill and an analysis skill, uses outside the second-person tier C3 assigns it. The model census
calls `gz-mx` *"the mode's own operator"* (`CMS:134`), a third sense of *operator*, used once. No status
changes.

### Statuses changed

| Term | Before | After | Why |
|---|---|---|---|
| dispatcher | SOURCED | **CONTRADICTED** | RP-13 ruling 2 (contradiction 13) |
| sea trial | RULED | **CONTRADICTED** | Part 0's definition left unamended (contradiction 12) |
| work order (rejected-synonym table) | rejected, contradicted | **RULED, reinstated** | corpus, booked 2026-11-03: *"the WO IS the OBPI"*; Part 0's retirement sentence stale (contradiction 9 restated) |
| approval for return to service | CONTRADICTED | CONTRADICTED, citations corrected | Part 0 amended 2026-11-03; `command-doctrine.md:68-69` not (contradiction 8 restated) |
| captain, position, crew | RULED (secondhand) | RULED, confirmed from the primary | `doctrine-merge.md:106-115`, `command-doctrine.md:51-60` |
| 10 new terms (G1) | — | 6 RULED, 4 SOURCED | RULED: role, the eight roles, orchestrating session, interlocks, standing orders, gates. SOURCED: qualified tools, procedures, sortie, second opinion |

Note on the count: the first pass's Domain 5 row *"dock trial; sea trial"* is split by this change. *Dock trial*
stays RULED and *sea trial* becomes CONTRADICTED; the count treats them as one row moving, as before. Revised
totals over 104 term rows: **RULED 56, SOURCED 36, CONTRADICTED 9, UNSOURCED 3.** Rejected synonyms now
number 28: the 20 first-pass rows, less *work order* (reinstated), plus 9 new.

### Contradictions, restated and new

8. *(restated)* **Return to service**: the canonical `command-doctrine.md:68-69` and matrix A2 (`MAT:36`) still make Gate 5 *the* return to service. Part 0 as amended 2026-11-03 (`doctrine-merge.md:125-129`, *"Option A"*) and RP-12 rulings 2, 14 and 32 make it the operator's separate act at the return to service package's close.
9. *(restated)* **Work order**: Part 0 still says the term *"was retired on 2026-10-16"* (`doctrine-merge.md:141-142`), against its own 2026-11-03 amendment (*"each work or repair order's work"*, `:126-127`), the ruling booked 2026-11-03 (*"the WO IS the OBPI, which is a correction"*), the level table and kit ruling 43. Only the `WO-1` to `WO-11` names were retired.
11. **The ladder**: Part 0's glossary (`doctrine-merge.md:435`, *"ruled 2026-10-05"*) maps feature ADR → engineering order, OBPI → work package, TASK → task card. The rulings booked 2026-11-03 make the work order the OBPI's successor and the work package the mADR's successor (the story), with the feature package the epic.
12. **Sea trial**: Part 0 defines it as *"One work package run on a fresh install of the released wheel"* (`doctrine-merge.md:136`). The record ruled two approved forms, best and better (`REC:665-675`; corpus *"(verbatim: "Make the two an OR"; "A")"*). The matrix marks *"the Part 0 amendment is commissioned"* (`MAT:73`); it has not been made.
13. **Dispatcher**: the code census counts dispatchers as a control role (3 of 421, `CCC:760-771`) and counts twins and dispatching steps as separate controls. RP-13 ruling 2 (operator *"A"*, 2026-10-31, `harbor-ro13-mode-contract.md:24`): *"A step, hook line or twin that only dispatches to it inherits that entry"*, and R1: *"Twins collapse to one entry"* (`:54`). RP-13 F4 replaces the census counts (`:45`), but the role list the RP-13 rulings key on still carries *dispatcher*.
14. **The settled-ruling corpus keeps superseded rulings unmarked** under its banner *"settled rulings — do NOT re-open"*. Three instances: Gate 5 *"attested once at the work package's close"* (2026-10-30) beside Gate 5 at the order (2026-11-03; RP-12 rulings 2, 30); *"--approver and --operator stay typed names"* (2026-11-02) beside ruling 32 (2026-11-04); *"The punch list is the compliance register"* (2026-10-25) beside B8 *"B′"*.

**Collision added:** Part 0's ruled term *orchestrating session* (`doctrine-merge.md:113-114`) names the session the kit calls the *coordinator*, whose synonym *orchestrator* ruling 21 rejects. Ruling 21's exact-string scan would not catch *orchestrating*.

### Files read for the gap-fill

| File | Lines | How read |
|---|---|---|
| `docs/rnd/renewing-vows/doctrine-merge.md` | 797 | whole |
| `docs/governance/GovZero/command-doctrine.md` | 219 | lines 44 to 80 (§ Terms), plus a text search for the terms; not whole |
| `docs/governance/harbor-ro13-mode-contract.md` | 68 | lines 1 to 36 (header, scope, rulings 1 to 11), plus a text search for *role*; not whole |
| `docs/rnd/contractor-kit/sources/census-code-controls.md` | 870 | rows E1 to E134 (lines 473 to 606), every column; the rest whole in the first pass |
| `docs/rnd/contractor-kit/sources/census-model-surfaces.md` | 550 | skill rows (lines 86 to 158), every column; the rest whole in the first pass |
| `.gzkit/handoffs/rulings.jsonl` | 2464 | through `gz handoff rulings` (152 searches) and `--json`; the provenance fields read for 18 matching lines only |

## Gap-fill 2: the constitution (2026-11-22, read-only)

`docs/governance/GovZero/command-doctrine.md` read whole (219 lines). Its status line (`:5`): *"Part I of this
file, the statement of command and the ten articles, is the constitution: the root (operator rulings
2026-06-14, 2026-10-08 and 2026-10-10 ...)"*. It was ratified 2026-06-10 and amended 2026-10-10 by *"ratify
Part 0"* (`:6`). A term the constitution defines or uses under that ratification counts as RULED here. Gate
definitions are not the constitution's: `:7` *"The GovZero Charter (`charter.md`) remains the sole authority
for gate definitions"*. `docs/governance/GovZero/charter.md` was not read.

### What each part uses or defines (work, repair, level, role and record terms)

| Where | Terms used or defined | Against my tables and the draft's § 1 |
|---|---|---|
| Four P's (`:16-24`) | *policies*, *procedures*, *practices*; *"the five gates exist; a human attests before work ships"*; procedures are *"the gate definitions, the briefing template, the attestation record schema, the substitution rules"* | consistent; *gate* here is Gates 1 to 5 |
| Statement line 1 (`:28-30`) | commander, captain, *"one standing and does not divide"* | as Domain 4a (RULED) |
| Line 2 (`:31-33`) | **orders**: *"standing orders for every position, a tasking order for one work package. The order is what carries a role's auspices."* | **new contradiction 15** (the *Order* level) |
| Line 3 (`:34-36`) | obligation, position, *"every position leaves a record"*, crew | as Domain 4a |
| Line 4 (`:37-38`) | *"The commander holds positions too"* | consistent with `KIT:22` (the operator listed among the positions) |
| Line 6 (`:41-42`) | *"Work is assessed from records by someone who did not do it. Release is the captain's."* | assessment by a non-performer matches C3 and the QAI (A5); *Release*: contradiction 8 |
| Line 7 (`:43-45`) | *construction*, *release*, *product* | matches the level table's *Construction* column |
| § Terms (`:49-69`) | Commander, Captain, Position, Role, Crew (*"the orchestrating session included"*), Force, Doctrine, Campaign, **Order**, **Release** | as G1. *Release* is still *"Gate 5 attestation, which is return to service"* (`:68-69`), unamended (contradiction 8) |
| Article 1 (`:73-75`) | *"One human signs for the work"*; signature and override welded, *"Any proposal that separates them, in either direction, is rejected on its face"* | RP-12 keeps both with the operator (Gate 5 at the order, return to service at the package's close, ruling 32's operator acts), so it separates the acts, not the signature from the override; no contradiction found |
| Article 2 (`:77-79`) | *harness*; *"CI rules, file checks, diff gates, and halt conditions"*; *"If the harness does not enforce it, the doctrine does not contain it."* | the census's control roles have no counterpart here; *diff gates* is a generic use of *gate* |
| Article 3 (`:81-83`) | *"The model is crew, never in command"* (title amended 2026-10-10); *"An agent is crew: it fills a position, an obligation with a role to fulfil it"* | **new contradiction 16** (Part I's copy in `doctrine-merge.md`) |
| Article 4 (`:85-87`) | *run*, *scope manifest*, *"diff of delivered work against commanded scope"*, *annunciated* | the scope manifest is the brief's Allowed Paths today (Appendix A `:197`); *annunciate* is the census's *alarm* sense (*"only announces"*), not RP-10's |
| Article 5 (`:89-91`) | *attestation record* with *"served-model identity for every gated artifact"*; substitution *"the way airline dispatch handles inoperative equipment: by explicit prior relief"* | *dispatch* here is airline dispatch, not gzkit's subagent dispatch (collision); *inoperative equipment* under prior relief is the MEL concept RP-13 builds on. The served-model field is a gap (Appendix A `:198`) |
| Article 6 (`:93-95`) | *attestor*, *attestation*, *"a run is capped at the volume of change one attestation can honestly cover"*, *checkpoint cadence* | with Gate 5 at the order, the attestation unit is the order, so a run is capped by one order's attestation; no contradiction found. *Checkpoint* collides with `gzkit.mx.checkpoint` |
| Article 7 (`:97-99`) | evidence artifacts: *"the ADR, the failing-then-passing test, the diff, the Gherkin scenario, the recorded model identity, the scope-conformance report"* | consistent with OQE (B4) and the ledger; *ADR* stays an evidence artifact though it is no level in § 1 |
| Article 9 (`:105-107`) | *drift phase*, *"deliberate intervals of unassisted work, scheduled and logged"*, *safety-critical maintenance* | not built (Appendix A `:202`) |
| Article 10 (`:109-111`) | *"Every gate, check, and template"* traces to an article; the coherence audit *"is a task of the maintenance visit"* | **new contradiction 17** (a task directly under a package; the maintenance visit as a work package) |
| § What changes (`:113-115`) | the six worklist items carried by the campaign | none |
| § Reconciliation (`:117-140`) | *positions distinguished from assets*; *"A measurement with no position is a lapse"* | none |
| § Rhythm (`:142-178`) | session tier: *"The handoff is briefed as a transfer of position responsibility, in four parts ... The briefing gates nothing"*; maintenance tier: *"one named maintenance visit, a scheduled work package of the operator's own design"*, *"Each run of a chore is a ledger event; a finding is not"*; *"no tier gates"*; *sortie* (the airlock) | **new contradictions 17, 18 and 19** |
| § Glossary (`:180-182`) | names *"ratified in `docs/rnd/renewing-vows/doctrine-merge.md` Part 0"* | confirms G1's use of the Part 0 glossary |
| Appendix A (`:188-203`) | Article 3's row keeps the old title (*"Article 3's row reads its former title; the table is the June baseline"*, `:190`); Article 1's row is *"Universal OBPI attestation"* | the OBPI is the legacy order under § 1; the appendix predates the level table |

The draft's § 1 against the constitution: the constitution defines none of § 1's four levels (Epic, Story,
Order, Action) and none of its record names (feature package, return to service package, repair package, work
order, repair order). It uses *work package* (line 2; the maintenance visit), *order* in its command sense,
*run* and *task* (Article 10), and *Release* as Gate 5. § 1's *Who* column (*"Coordinator, inspector,
operator"*, *"Craftsman"*) uses kit positions the constitution does not name. The constitution's own position
vocabulary (commander, captain, crew, position, role) is not in § 1 at all.

### New terms from the constitution

| Term | Meaning as stated | Defined at | In code | Status |
|---|---|---|---|---|
| Order (standing order, tasking order) | *"How command reaches the work: a standing order binds every position; a tasking order binds one work package and carries the role's auspices."* | `command-doctrine.md:66-67`; line 2 `:31-33` | none (*"no tasking record does"*, `doctrine-merge.md:569`) | **CONTRADICTED** (contradiction 15) |
| tasking order | *"a tasking order for one work package"* | `:32`, `:66-67` | none | RULED (line 2, *"it stands, add the seventh"*, 2026-10-10) |
| maintenance visit | *"Due chores and issue triage are flown together as one named maintenance visit, a scheduled work package of the operator's own design (AC 120-16G § 6-1)"* | `:167-174` | none (*"Advisory until the board's signal is wired"*) | RULED (the rhythm, ratified 2026-10-10; the tier ruled 2026-10-07 *"Two slower tiers, signal-triggered"*) |
| chore run (a ledger event) | *"Each run of a chore is a ledger event; a finding is not (ruled 2026-10-07)."* | `:170-171` | none (*"the event is unbuilt"*, `doctrine-merge.md:578`) | RULED |
| transfer of position responsibility | *"The handoff is briefed as a transfer of position responsibility, in four parts: preview from the status displays, verbal briefing, assumption, review ... The briefing gates nothing"* | `:154-158` | the handoff system; `gz handoff decide` | RULED (session tier ratified 2026-07-18; rhythm 2026-10-10). The canonical name of the handoff's act; C11's rejection of *position relief briefing* left it standing |
| run | Article 6: *"a run is capped at the volume of change one attestation can honestly cover"*; Article 4: *"every run is preceded by a scope manifest"* | `:87`, `:95` (used, not defined) | `WPR:29-30` *"A package's run is in flight from commencement until it closes"*; `order_run_position` `WPR:288-317` | SOURCED (meaning from code; the constitution only rules on it) |
| attestation; attestor | *"An attestation that does not record which model produced the work attests less than it claims"*; *"The attestor still reviews at human speed"* | `:91`, `:95` | `gz obpi complete --attestation-text`; Gate 5 at the order (`KIT:414`) | RULED (Articles 5, 6) |
| signature; override | *"Whoever holds the signature holds override authority ... and whoever holds override authority holds the signature."* | `:75` | none as such | RULED (Article 1) |
| harness | *"Authority implemented in the harness, in CI rules, file checks, diff gates, and halt conditions, is the only kind the model actually answers to."* | `:79` | the controls of `CCC` | RULED (Article 2) |
| scope manifest | *"every run is preceded by a scope manifest"* | `:87` | brief Allowed Paths (Appendix A `:197`) | RULED (Article 4); partial |
| annunciation | *"every artifact outside the manifest is annunciated before the run can pass any gate"* | `:87` | none as such | RULED (Article 4) |
| attestation record; served-model identity | *"The attestation record therefore carries the served-model identity for every gated artifact"* | `:91` | none (*"Gap"*, `:198`) | RULED (Article 5); not built |
| scope-conformance report | named among the evidence artifacts | `:99`, `:115` | *"restored on completion receipts under GHI #1181"* (`:115`) | RULED (Articles 4, 7) |
| evidence artifacts | *"the ADR, the failing-then-passing test, the diff, the Gherkin scenario, the recorded model identity, the scope-conformance report"* | `:99` | ARB receipts, the ledger | RULED (Article 7) |
| proficiency log; drift phase | *"deliberate intervals of unassisted work, scheduled and logged"* | `:107`, `:115` | none (*"Gap"*, `:202`) | RULED (Article 9); not built |

### Statuses changed by Gap-fill 2

| Term | Before | After | Why |
|---|---|---|---|
| work package | RULED | **CONTRADICTED** | contradiction 17: the constitution's maintenance visit is *"a scheduled work package"*; the store admits only `kind` delivery or repair |
| maintenance record | RULED | **CONTRADICTED** | contradiction 18 |
| shift turnover | RULED | **CONTRADICTED** | contradiction 19 |
| captain, position, role, crew, orchestrating session | RULED (via Part 0) | RULED, confirmed in the constitution itself | `command-doctrine.md:51-60` |
| approval for return to service | CONTRADICTED | unchanged; the constitution's `:68-69` is the unamended side | contradiction 8 |
| 15 new terms (above) | — | 13 RULED, 1 SOURCED (run), 1 CONTRADICTED (Order) | — |

Revised totals over 119 term rows: **RULED 66, SOURCED 37, CONTRADICTED 13, UNSOURCED 3.** Rejected synonyms
unchanged at 28.

### New contradictions

15. **Order, the defined term against the level.** The constitution defines *Order* as *"How command reaches the work: a standing order binds every position; a tasking order binds one work package"* (`command-doctrine.md:66-67`, line 2 `:31-33`). The draft's § 1 (`drydock-taxonomy.md:25`, from the canon level table) uses *Order* for a level below the work package, the work or repair order, many to a package (RP-12 rulings 30, 43, 53). The constitution's one order binds the whole package; the level table's orders subdivide it.
16. **Part I's copy is not the ratified text.** `doctrine-merge.md` says its RATIFIED parts are *"copied byte for byte from the canonical file ... with no word changed"* (`doctrine-merge.md:11-12`) and marks Part I *"RATIFIED, unchanged"* (`:478`). Its Article 3 keeps the old title *"The model is a crew resource, not a crew member"* without the added sentence (`:490-492`), and its Article 10 keeps *"accumulated ritual, which retires now"* and *"The audit runs at every major model transition"* (`:520`). The constitution carries the 2026-10-10 amendments (`command-doctrine.md:81-83`, `:111`).
17. **The maintenance visit is a work package the store cannot hold.** The constitution's rhythm makes due chores and issue triage *"one named maintenance visit, a scheduled work package of the operator's own design"* (`command-doctrine.md:167-168`), with the coherence audit *"a task of the maintenance visit"* (`:111`). The work-package store admits only *"kind delivery (names its outcome) or repair"* (`data/catalog/work_packages.json` `_doc`). The level table (§ 1) has a construction and a repair column, no scheduled-maintenance one, and puts a task under an order, not directly under a package.
18. **The maintenance record entry, two meanings.** Part 0's glossary maps *"a chore run → maintenance record entry — sourced: 14 CFR § 43.9(a); ruled 2026-10-07 as a ledger event"* (`doctrine-merge.md:416`), and the constitution keeps the chore run as a ledger event (`command-doctrine.md:170-171`). The kit's maintenance record is `entry_booked` events, each booked by an `Implementer`, `SingleDriver` or `Restoration` dispatch on a commenced order under an open MX session (rulings 8, 167, 175; `KIT:420`). A chore run has no order, dispatch or MX session, so it cannot be such an entry.
19. **The handoff gates nothing, against the turnover's gate.** The constitution: *"The handoff is briefed as a transfer of position responsibility ... The briefing gates nothing"* and *"no tier gates: staleness announces"* (`command-doctrine.md:154-158`, `:176`). Kit ruling 19 (`KIT:444`, operator *"A"*, 2026-11-04): a hangar handoff *"whose turnover lacks a tag hung at that moment fails `gz check`"*, and C11 commissions *"the handoff's authoring gate refuses a hangar handoff whose turnover omits a tag the log shows hung"* (`REC:3015-3016`). Neither the kit nor the record cites the constitution's sentence or claims a drydock exception to it.

**Collisions added (not numbered):** *dispatch* (Article 5's airline dispatch against gzkit's subagent dispatch); *checkpoint* (Article 6's checkpoint cadence against `gzkit.mx.checkpoint`); *sortie*, now four senses (the airlock in the rhythm, `command-doctrine.md:150-153`; *dispatch → sortie* in the Part 0 glossary; the flight-test sortie; the weaponeering sorties *constraints, red, green*); *gate*, whose definitions the constitution reserves to `charter.md` (`:7`), which this gather has not read.

### File read for Gap-fill 2

| File | Lines | How read |
|---|---|---|
| `docs/governance/GovZero/command-doctrine.md` | 219 | whole |

`doctrine-merge.md` lines 488 to 492 and 518 to 520 were re-read to confirm contradiction 16. Not read:
`docs/governance/GovZero/charter.md`, named by the constitution as the sole authority for gate definitions.
