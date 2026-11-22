# Gather F — R&D, insights, GHI, work-package issue vocabulary, chores, receipt and run ids, handoff and ceremony files, the hexagon package map

Draft served: `docs/governance/drydock-taxonomy.md` § 9 items 10, 11, 12. Read-only gather, 2026-11-22.
Status key: **RULED** (operator verbatim + date + location), **SOURCED** (defined in canon or code, no operator
ruling quoted for it), **CONTRADICTED** (two sources disagree; both quoted), **UNSOURCED** (used, nowhere defined in
what was read). `Collision` notes mark a clash with the draft's work and repair vocabulary (order, package, repair,
work, task, run, gate, freeze, block, proceed).

---

## Domain 10a — R&D entry kinds, dispositions, states

| Term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| R&D run | "the activity — one governed exploratory session, possibly spanning several" | `docs/governance/rnd-discipline.md:18` | none (no code, no event) | RULED: record status "**Status: RULED.** Frame settled 2026-09-15 → 2026-09-17" (`rnd-discipline.md:3`) | **run**: one of six senses of "run" (see Contradictions C9) |
| R&D record, `docs/rnd/<slug>.md` | "that run's own document, one per run" | `rnd-discipline.md:19,80`; `.gzkit/skills/gz-rnd/SKILL.md:54` | path convention only; `<slug>` has no grammar or validator | RULED: operator *"maybe an area of docs that is rnd"* (`rnd-discipline.md:323`, edition 2026-09-15→17) | slug grammar UNSOURCED |
| R&D discipline record | "*this file* — the single doctrine document governing all runs" | `rnd-discipline.md:20` | — | RULED (same status line) | |
| diamond 1 / diamond 2 | "Discover and Define … ends with the problem defined and a plan"; "Producing those artifacts is diamond 2" | `gz-rnd/SKILL.md:18-21`; `rnd-discipline.md:24-30` | — | RULED (status line, 2026-09-15→17) | |
| entry kind `source` | "a primary source — **cited, never summarized**, with its verbatim quotation and when it was read" | `gz-rnd/SKILL.md:77-79`; `rnd-discipline.md:89-91`; template `assets/rnd-record-template.md:15,33` | heading convention `## source · <name>`; no parser | RULED: "**two entry kinds**, accreting … the section template smuggled compose-at-the-end and was retired" (`rnd-discipline.md:324`, 2026-09-17) | |
| entry kind `decision` | "something crystallized in session, the reasoning behind it, and, where the operator ruled it, the question, the options put and their verbatim words" | `gz-rnd/SKILL.md:80`; `rnd-discipline.md:92`; template `:16,41` | heading `## decision · <what>`; no parser | RULED (as above) | |
| `commissions:` field | "naming the disposition it warrants" | `gz-rnd/SKILL.md:82`; `rnd-discipline.md:94`; template `:46` | no parser | RULED (as above) | |
| plan item (rejected kind) | "There is no plan-item kind: that shape would let work be commissioned with no recorded reasoning" | `gz-rnd/SKILL.md:82-84`; `rnd-discipline.md:95-96` | — | RULED (as above) | |
| term (resolves outward) | "a **term** → the project glossary. Its home is unsettled … until then hold the term in this record as a `decision` entry" | `gz-rnd/SKILL.md:89-92`; `rnd-discipline.md:104-121` | no glossary store | RULED: Q8, operator *"We need option A to make up for this lapse."* (`rnd-discipline.md:118`); the 2026-09-17 `GLOSSARY.md` ruling was on a false premise and never created (`:116-117`) | glossary home pending the DDD-discipline run |
| insight (resolves outward) | "an **insight** → `gz insights remember`" | `gz-rnd/SKILL.md:93`; `rnd-discipline.md:109` | `gz insights remember` | RULED (status line) | |
| frontier | "every decision whose prerequisites are settled" | `gz-rnd/SKILL.md:103`; `rnd-discipline.md:249` | — | SOURCED (MPAS `grilling`); the one-at-a-time departure RULED: *"ask me the questions one at a time"* (`rnd-discipline.md:196`) | |
| disposition map, seven rows | "All seven rows are always present; an absent row is an unfinished run" | `gz-rnd/SKILL.md:150-161`; `rnd-discipline.md:123-136` | — | RULED: row 7 *"A, add row 7 further research"* (2026-11-03, `rnd-discipline.md:404-405`) | |
| row 1 "catalog, packages, orders and decision records" | "propose only — the operator admits each outcome and initiates each package, or not (IRON LAW)" | `gz-rnd/SKILL.md:155`; `rnd-discipline.md:130,435` | — | RULED: *"Commission row 4"* (2026-11-10), executed on *"gz-rnd label"* (2026-11-12) (`rnd-discipline.md:423-424`); prompted by *"this entire system is meant to be deprecated and superseded by the requirements catalog, the feature package, the work package, the work order, and the release package"* (`:427-429`) | **package, order** — row 1 names the level-table records |
| row 2 "GHI / direct fix" | "file via `ghi-author`" | `gz-rnd/SKILL.md:156` | — | RULED (status line) | |
| row 3 "chore" | "advise only" | `gz-rnd/SKILL.md:157` | — | RULED (status line) | |
| row 4 "control surface, rule, doc, skill, hook" | "draft"; includes Magna Carta, roadmap, backlog | `gz-rnd/SKILL.md:158,163-165` | — | RULED: *"rnd is our grill-me and I think acknowledging magna carta, roadmap, and backlog as valid additional docs changes strengthens gzkit's guidance to an agent."* (2026-09-27, `rnd-discipline.md:142-144`) | |
| row 5 "one-shot refactoring" | "propose a program" | `gz-rnd/SKILL.md:159` | — | RULED (status line) | |
| row 6 "no action" | "record it, with the reason" | `gz-rnd/SKILL.md:160` | — | RULED: "take-no-action is a disposition, not an exception" (`rnd-discipline.md:325`) | |
| row 7 "further research" | "name each follow-on R&D run the understanding opened: its subject and what opened it" | `gz-rnd/SKILL.md:161`; `rnd-discipline.md:413-418` | — | RULED (2026-11-03, above) | |
| state `commissioned` | one of two states | `gz-rnd/SKILL.md:167`; `rnd-discipline.md:146` | — | RULED: "There is deliberately no third `retained` state (ruled 2026-09-17)" (`rnd-discipline.md:146-147`) | used in `docs/rnd/check-outcome-reporting.md:365-371` |
| state `not pursued` | the other state; "the reason field carries the revisit condition" | same | — | RULED (same) | read by `ghi-author` Step 0 (`ghi-author/SKILL.md:170`) |
| `retained` (rejected state) | declined: "nothing would read the field and nothing would fire the revisit" | `rnd-discipline.md:146-158` | — | RULED (declined) | |
| challenge; "deliberately restated" | "satisfied by a restatement made on purpose at the close" | `gz-rnd/SKILL.md:183-185`; `rnd-discipline.md:61-62` | — | RULED (status line) | |
| review, `docs/rnd/<slug>/review.md` | "one readable account of the whole plan … It is a view over the record and holds no authority" | `gz-rnd/SKILL.md:188-192`; `rnd-discipline.md:365-368` | — | SOURCED: amendment is "Operator-directed, verbatim: *'step 1, and improve rnd skill'*. The four rules below are the agent's drafting … open to the operator's line-by-line correction" (`rnd-discipline.md:337-339`) | |
| sign-off: `kill` / `fund` | diamond 1's human close | `gz-rnd/SKILL.md:20,188`; template `:76` | — | RULED: "Sign-off is a beat, not a boundary (ruled 2026-09-17)" (`rnd-discipline.md:64`) | |
| sources dir `docs/rnd/<slug>/sources/` | research reports landed verbatim | `gz-rnd/SKILL.md:104,139`; `rnd-discipline.md:250` | — | SOURCED (MPAS departure table) | |
| R&D ledger events `opened`, `sign-off`, `run closed` | three events; a killed run "ends at two events" | `rnd-discipline.md:171-181` | **none** — "designed and unbuilt"; `gz-rnd/SKILL.md:221-222` forbids emitting | RULED: *"yes to ledger."* and *"yes, closes at sign-off."* (2026-09-16, `rnd-discipline.md:171,180-181`) | absence is by design |
| retired coinages `fan`, `pinch`, section template | "Each was a wrong model travelling under a new word" | `rnd-discipline.md:304-309` | — | RULED (status line) | |
| fence: `work order` | "a GHI is the work order and the receipt" | `rnd-discipline.md:301` | — | **CONTRADICTED** (C1) | **order** |
| fence: `freeze` | "lock-down … or set-aside … the source collides with itself; do not import it" | `rnd-discipline.md:300` | `frozen` package/order states | **CONTRADICTED** (C2) | **freeze** |
| fence: `gate` | "Gate 5 is OBPI/ADR completion attestation and nothing else" | `rnd-discipline.md:299` | — | **CONTRADICTED** (C3) | **gate** |
| run-state / subject-state (a term held in a record) | "**Subject-state**: what a check found about what it guards (passed, failed). **Run-state**: what happened to the check itself (not run, demoted, not observed)" | `docs/rnd/check-outcome-reporting.md:196-205` | none yet (RP-13 change order, proposed) | SOURCED (held as a `decision` pending the glossary home; not operator-ruled as a term) | **run** |

## Domain 10b — insight types (`gz insights remember`)

| Term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| `defect` | "an observed problem" | `.gzkit/skills/gz-insights-remember/SKILL.md:32-33` | `InsightType`, `src/gzkit/insights/model.py:22`; argparse `choices`, `src/gzkit/commands/insights.py:113` | SOURCED (GHI #358 lock, `model.py:3-12`) | label `defect` is the GHI class of the same word |
| `defect-resolution` | "the fix outcome" | `gz-insights-remember/SKILL.md:34` | `model.py:22` | SOURCED | |
| `improvement` | "a post-correction lesson — the record `AGENTS.md` § Behavior Rules requires when the operator course-corrects in flight" | `gz-insights-remember/SKILL.md:34-36` | `model.py:22` | SOURCED (AGENTS.md Behavior Rules binds the use) | not `enhancement` (the GHI label) and not `correction` (the operator-doctrine term) |
| `discovery` | "a survey finding" | `gz-insights-remember/SKILL.md:36`; `model.py:7` "(GHI #502)" | `model.py:22` | SOURCED | |
| `--source operator\|agent` | "pass `operator` only for the operator's own words; an agent's reading of them stays `agent`" | `gz-insights-remember/SKILL.md:43-45` | `Source`, `src/gzkit/insights/ledger_ref.py:19`; `commands/insights.py:131-132` | RULED: operator *"what is the harm that the ledger notes that an insight was recorded and references it?"*, selected *"Pointer + 3 fields"* (2026-10-18, `ledger_ref.py:1-8`) | |
| `insight_recorded` (ledger event) | "naming its `ts`, a SHA-256 of its line …, whose words it carries, and an optional `supersedes`" | `ledger_ref.py:1-8`; skill `:67-69` | `ledger_ref.py:18,44-57` | RULED (same) | |
| insight identity = `ts` | ISO8601 with zone; `--supersedes <ts>` names an earlier record | `model.py:19-34`; skill `:46-47` | `_ISO8601_PATTERN`, `model.py:19` | SOURCED | the record's id is a timestamp, not an `IdKind` |
| `id` (optional record slug) | "Optional record slug" | `model.py:41` | no grammar | UNSOURCED (no source says when it is set; `append.py` never sets it from the CLI) | |
| `scope` | "Surface or skill the record names" | `model.py:38` | free text, `min_length=1` | SOURCED (open set) | the draft's "Insight scope `drydock-formalism`" is a free value |
| class of failure / recurrence chain | GHI `## Class of failure` section; chains of same-class citations | `src/gzkit/insights/failure_classes.py:1-17`; `ghi-author/SKILL.md:256-260` | `FailureClassEntry`, `RecurrenceChain` (`failure_classes.py:56-80`) | SOURCED | |

## Domain 10c — GHI labels (live set, 22 by `gh api --paginate .../labels`; `gh label list --limit 200` printed the same 22)

| Label | GitHub description | Defined in canon | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| `defect` | "Tracked defect discovered during implementation or governance work" | `ghi-author/SKILL.md:202` (primary class) | applied by `gh issue create` inside `ghi-author` Step 5 | SOURCED | |
| `enhancement` | "New feature or request" | `ghi-author/SKILL.md:203`: "Surface works as designed; the design could be tighter" | `gz chores propose-ghi` applies it (`src/gzkit/commands/chores_propose_ghi_cmd.py:100-101`) | **CONTRADICTED** (C10) | |
| `investigation` | "Unknown root cause; the GHI is to find it, not fix it (ghi-author Step 1)" | `ghi-author/SKILL.md:204` | — | SOURCED | |
| `runtime` | "Runtime-affecting change (eligible for patch release)" | `ghi-author/SKILL.md:210,215` | `src/gzkit/commands/patch_release.py:456,512` | SOURCED | |
| `tech-debt` | "Quality-of-implementation defect surfaced by gz-tech-debt-review or operator review" | `ghi-author/SKILL.md:211` | — | SOURCED | |
| `security` | "Security-sensitive surface or attack-surface dimension" | `ghi-author/SKILL.md:212` | — | SOURCED | |
| `eval-feedback` | "Authored from an evaluation-feedback loop event (ADR-0.0.26)" | `ghi-author/SKILL.md:213` | `chores_propose_ghi_cmd.py:102-103` | SOURCED | |
| `repair` | "Carried by a repair work package (RO-5)" | `docs/governance/harbor-ro5-work-packages.md:31` (ruling 7) | `REPAIR_LABEL`, `src/gzkit/work_package_github.py:16,63-83` | RULED: ruling 7 selection *"A"*; label created by the verb, operator *"Verb ensures it (Recommended)"* (2026-10-28, `work_package_github.py:6-7`) | **repair**: label, package kind, chore rung, dispatch role, REQ specialization |
| `chore` | "Maintenance, cleanup, and governance hygiene work" | none found in `ghi-author`, `ghi-close`, `gz-chore-runner`; `propose-ghi` applies `enhancement` + `eval-feedback`, not `chore` | — | UNSOURCED | |
| `session-handoff` | "End-of-session handoff pointer (consumed by orientation hook)" | not named in `gz-session-handoff/SKILL.md` (read whole) | a grep of `src/gzkit/hooks`, `.claude/hooks`, `.gzkit/hooks` found no reference (a search, not a read) | UNSOURCED (description claims a consumer not established) | |
| `emergency` | "5-alarm structural emergency …" | used only in 2026-05/06 handoffs and `docs/governance/return-to-health-plan-2026-05-30.md:320,537` (not read whole) | — | UNSOURCED in current skills | |
| `recovery-prerequisite` | "Cleanup required before the get-out-of-jail 14-day plan can execute" | none found | — | UNSOURCED | |
| `dependencies`, `python:uv` | Dependabot defaults | none | — | UNSOURCED | |
| `bug`, `documentation`, `duplicate`, `good first issue`, `help wanted`, `invalid`, `question`, `wontfix` | GitHub defaults | none (`ghi-close` dispositions spell `duplicate`, `won't-fix` as comment text, not labels) | — | UNSOURCED | `wontfix` label vs `won't-fix` disposition |

## Domain 10d — problem-report states and GHI close vocabulary

| Term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| problem report (the GHI's role); carrier names *GHI*, *write-up* | "The GitHub issue's role is a **problem report**. The carrier keeps its names" | `.gzkit/skills/ghi-close/references/problem-report-states.md:3-5`; `docs/rnd/contractor-kit.md:3059-3076` | none | RULED: decision B12, options A–D, operator *"A"* (`contractor-kit.md:3073`); date not stated in the entry, nearest earlier dated line 2026-10-17 (`:3049`); landed 2026-10-28 (`problem-report-states.md:39-40`) | |
| `recorded` | "documented using the problem reporting process" — filed through `ghi-author` | `problem-report-states.md:14` | none | RULED (B12) | |
| `classified` | "categorized in accordance with an established classification scheme" — its Step 1 class label | `:15` | none | RULED (B12) | |
| `resolved` | fix commit landed with `(GHI #N)`; "The commit SHA witnesses this state" | `:16` | none; GitHub knows only open/closed (`:28-29`) | RULED (B12) | |
| `closed` | "a review on record has confirmed the resolution" | `:17` | reviewer subagent stand-in, operator *"Reviewer subagent (Recommended)"* (2026-10-28, `:32-34`) | RULED (B12; review stand-in ruled 2026-10-28) | |
| close dispositions `fixed`, `superseded`, `withdrawn`, `duplicate`, `won't-fix` | table of meanings | `ghi-close/SKILL.md:348-354,359` | comment text only | SOURCED | `withdrawn`, `superseded` also name OBPI/outcome/REQ states |
| prescriptive shapes (single fix, dominant option, balanced, investigation, already-resolved, forward-reference tracker) | Phase 1 classification | `ghi-close/SKILL.md:248-257` | — | SOURCED | |
| closure contract: Invariant, Boundary, Acceptance, Exit | "Before implementation, record the closure contract" (GHI #980) | `ghi-close/SKILL.md:46-58`; `ghi-author/SKILL.md:262-268` | — | SOURCED | **Exit** also names `WorkPackageExit` and `gz mx exit` |
| repair assignment | "scope missed from a Validated ADR enters the in-flight ADR as a repair assignment" — "Only the operator opens it" | `ghi-close/references/repair-assignment.md:1-46` | — | SOURCED (cites "Operator ruling 2026-10-05", not quoted verbatim, `:28-30`) | **repair** |
| dead-letter | closing a GHI with no citable landing site | `ghi-close/SKILL.md:102-117` | — | SOURCED | |
| GHI as "work order" | `ghi-author` description "when a finding needs its own work order"; `ghi-close` "stop this work order" | `ghi-author/SKILL.md:4,27,106`; `ghi-close/SKILL.md:90,404` | — | **CONTRADICTED** (C1) | **order, work** |

## Domain 10e — work package (`gz wp`) issue-attachment vocabulary

| Term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| package kind `delivery` / `repair` | "A work package is `delivery` (it names one outcome) or `repair` (it names one or more GitHub issues and stores its lane)" | `.gzkit/skills/gz-wp/SKILL.md:21-22`; `harbor-ro5-work-packages.md:21` | `kind: Literal["delivery","repair"]`, `src/gzkit/models/catalog.py:204` | RULED for the kinds (ro5 ruling 1, selection *"A"*); the ruling's sentence "**A repair order is a work package**" is **CONTRADICTED** (C4) | **delivery** is not a word of the level table (§ 1 says "Work package"/"Feature package") |
| `issues` (a repair package's GitHub issues) | "The GitHub issues a repair package carries"; "each in one package only" | `catalog.py:208`; `harbor-ro5-work-packages.md:89` | store `data/catalog/work_packages.json` (WP-01 carries 1183, 1184) | RULED (ro5 ruling 1) | |
| `gz wp attach <WP> --issue <n>` | "labels it `repair` and comments the package id on it (ruling 7)" | `gz-wp/SKILL.md:31-35` | `tag_issues`, `work_package_github.py:72-83` (`gh issue edit --add-label`, `gh issue comment`) | RULED (ruling 7, *"A"*) but its `gh issue edit` is **CONTRADICTED** (C11) | "tagging scheme" vs tag-out `TAG-` |
| package mark `WP-<NN>-<slug> (RO-n, …)` | "the package id with its aliases, as ruling 7 spells it" | `harbor-ro5-work-packages.md:31`; `work_package_github.py:25-32` | `package_mark` | RULED (ruling 7) — its example id is **CONTRADICTED** (C12) | |
| `gz wp resolve <WP> <n> --commit <sha> --reviewer <r>` | "records each fixed issue against its repair package (ruling 10)"; "The last issue's close never closes the package" | `gz-wp/SKILL.md:45-47`; `ghi-close/SKILL.md:402` | (verb not read) | SOURCED (ruling 10 cited, its text not read) | |
| `--problem-report <n>` / `problem_report` | a repair REQ "answers an issue the package carries" | `gz-wp/SKILL.md:148-155`; `catalog.py:136` "(ruling 9)" | `catalog.py:136` | SOURCED | ties the GHI's role name (B12) into the REQ |
| "an issue is never a subject" | a repair package's run verbs name `--order`; never an issue | `gz-wp/SKILL.md:101-102` (ruling 64) | — | SOURCED | |
| `Task:` trailer from the package id | "starting with the lowercased package id, `TASK-wp-02-resume-#1185`" | `gz-wp/SKILL.md:66-67` | task trailer grammar `src/gzkit/tasks.py` (not read here) | SOURCED | **task**: a third spelling of the package id (lowercase) |
| OQE (objective quality evidence) | "Record each receipt, commit or path as the work produces it" | `gz-wp/SKILL.md:37-41` | `oqe`, `catalog.py:223` | SOURCED (amendment 1) | |

## Domain 11a — chores (registry `.gzkit/chores/registry.json`, 42 entries; skill `gz-chore-runner`)

Registered slugs (42): arb-pattern-extraction, cli-contract-governance, complexity-reduction-xenon,
config-paths-remediation, control-surface-permission-consent-drift, control-surface-rule-conflicts,
control-surface-rule-vs-check-drift, control-surface-skill-rule-reachability, control-surface-validator-reachability,
coverage-40pct, cross-platform-test-cleanup, decommission-tautological-tests, dependency-currency, doc-coverage,
eval-feedback-cluster, evidence-integrity-audit, exceptions-and-logging-rationalization, failure-class-index,
frontier-model-card-currency, frontmatter-ledger-coherence, ghi-cross-reference-staleness, hardcoded-root-eradication,
instructions-files-diet, ledger-vocabulary-inertness, memory-hygiene, module-sloc-cap-radon,
pep257-docstring-compliance, pool-triage, pythonic-design-pattern-application, pythonic-design-pattern-detection,
pythonic-refactoring, quality-check, repository-structure-normalization, session-correction-mining,
skill-authoring-quality, skill-command-doc-parity, skill-trigger-testing, test-consolidation-subtest-sweep,
test-isolation-compliance, test-manpage-examples, competitor-radar-currency, waiver-ratchet-drawdown. 11 declare
`projectLocal: true`. `.gzkit/chores/owasp-top10-2025-scan/` is a directory with no registry entry; the class-system
record names it "a non-chore data directory" (`docs/governance/chore-class-system.md:1513-1516`).

| Term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| chore | "chores are there to identify issues, provide an analysis, recommend a solution approach, and execute on solutions" | `chore-class-system.md:57-62` | registry + `gz chores` | RULED: operator verbatim (2026-09-12 20:30Z, `:57-62`) | |
| chore slug | registry key, dir `.gzkit/chores/<slug>/` | `registry.json` `project.choresDir` | no slug grammar found in `chores_declaration.py` | SOURCED (slug grammar UNSOURCED) | |
| class `conformance`, `coherence`, `curation`, `mining`, `currency` | "`class` answers *why the chore exists and what its staleness costs*" (table) | `chore-class-system.md:279-306` | `ChoreClass`, `src/gzkit/commands/chores_declaration.py:26` (in use: 25/6/4/4/3) | RULED: *"I ratify, with great enthusiasm, the entire plan."* (2026-09-12 21:10Z, `chore-class-system.md:101-104`) | |
| rung `observe`, `propose`, `repair`, `operator-only-repair` | "`rung` answers *where the chore stops*"; "carries the writing license" | `chore-class-system.md:310-323,490-497` | `ChoreRung`, `chores_declaration.py:27` (in use: propose 18, repair 18, operator-only-repair 6; `observe` 0) | RULED: *"rung + idempotent (Recommended)"* (2026-09-13, GHI #999, `:490-495`) | **repair** (rung) |
| `idempotent` | "carries the scheduling license" | `chore-class-system.md:493-495` | `chores_declaration.py:155` (all 42 true) | RULED (same) | |
| staleness signal `accumulated-work`, `content-delta`, `elapsed-time` | three of "Four signals, not interchangeable"; the fourth, heartbeat absence, proves "the *runner* lives, not the chore" | `chore-class-system.md:843-850` | `StalenessSignal`, `chores_declaration.py:28` (29/10/3) | SOURCED (four in the doc, three in code; heartbeat is not a chore signal) | |
| `periodDays`, `graceDays`, `surfaces`, `artifacts`, `paused` | staleness inputs | `chores_declaration.py:65-136` | same | SOURCED; "Every chore is due by date for now" RULED *"B for now until we have more maturity"* (`chore-class-system.md:837`) | |
| remediation category `vendor_fix`, `workaround`, `no_fix_planned`, `none_available` | "CSAF 2.0 remediation categories: 'no repair' is a declared value, never an absence" | `chores_declaration.py:29-30`; `chore-class-system.md:329-331` | in use: vendor_fix 26, no_fix_planned 16 | SOURCED | |
| check level `A`, `B`, `C`, `D` | "A inspects and reports; B repairs touching no control … C repairs that may reach a control; D re-authors a control or the standard" | `chore-class-system.md:831-839`; `chores_declaration.py:32-36` | `CheckLevel` (A 18, B 4, C 13, D 7) | RULED: *"yes, adopt the four levels - use the rich detail we found"* (2026-11-03, `chore-class-system.md:833`) | same scale as the tag's `check level C \| D` (draft § 5): shared, consistent |
| `provisional` | "True until the classification program confirms the level" | `chores_declaration.py:60-62` | all 42 true | RULED: *"A, admit as advised, marked provisional"* (`chore-class-system.md:838`) | |
| problem report / return to service package as a chore's exit | "A finding that needs more leaves the run as a problem report, for the next check at that level or a return to service package" | `chore-class-system.md:836` | — | RULED: operator *"A"* (same line) | the only source read that names the **return to service package** as a destination (T6) |
| chore lane `lite` / `heavy` | "lite: Gate-rigor: Gates 1, 2 required. Unit-tier only"; "heavy: All gates required" | `registry.json` `lanes` | lite 35, heavy 7 | **CONTRADICTED** (C13) | |
| `nonAuthority`, `governingRule` | "What it refuses to touch, and why"; "The .gzkit/rules clause served, or an explicit none" | `chores_declaration.py:158-166` | pattern `^(none\|\.gzkit/rules/…\.md( § .+)?)$` | SOURCED | |
| `frequency: per-release` (1 chore), `vendor: claude` (1 chore) | — | not in `DECLARATION_KEYS` (`chores_declaration.py:40-51`) | read elsewhere (not traced) | UNSOURCED | |
| run log `.gzkit/chores/{slug}/proofs/CHORE-LOG.md` | "Execution log" | `gz-chore-runner/SKILL.md:29`; `chores_declaration.py:115-119` | `proofsPattern` in `registry.json` | SOURCED | |
| `gz chores run` | "Execute the chore to log the result" | `gz-chore-runner/SKILL.md:77-81` | — | SOURCED | **run** |
| `gz chores propose-ghi` | "propose one using the chore's eval-feedback output" | `gz-chore-runner/SKILL.md:83-88` | calls `gh issue create` directly (`chores_propose_ghi_cmd.py:91-109`) | **CONTRADICTED** (C14) | |
| `record-processed --disposition <disposition>` | one ledger event per processed test file | `gz-chore-runner/SKILL.md:90-95` | values not traced | UNSOURCED (value set) | |

## Domain 11b — receipt ids and run ids

| Id / term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| `arb-ruff-<32 hex>` | ruff lint receipt | `.gzkit/skills/gz-arb/SKILL.md:38,79-81` | `src/gzkit/arb/ruff_reporter.py:190` | SOURCED | field is named `run_id` |
| `arb-step-<name>-<32 hex>`, name `[a-z][a-z0-9]*` | step receipt; name "must match the receipt-binding regex" | `gz-arb/SKILL.md:44-57`; `src/gzkit/arb/step_reporter.py:21-25` | `step_reporter.py:145`; `_CANONICAL_STEP_NAME_RE` `:25` | SOURCED | |
| canonical step names `typecheck`, `unittest`, `coverage`, `mkdocs` | the locked provenance table | `gz-arb/SKILL.md:33-49` | `CANONICAL_STEP_COMMANDS`, `src/gzkit/canonical_steps.py:50-128` | RULED per entry: *"features in ty scope"* (2026-10-24, `:58-59`); unittest parallel, operator re-ruling 2026-08-27 (`:66`); coverage *"parallel everywhere"* (2026-09-18, `:106-107`) | |
| reserved `security` (`arb-step-security-`) | "left empty until the toolchain feature ADR … fills it" | `canonical_steps.py:129-135` | empty list | SOURCED (unbuilt) | |
| `arb-meta-receipt-bind-<32 hex>` | "emitted internally when the receipt-binding gate fires" | `canonical_steps.py:136-142` | `src/gzkit/commands/obpi_complete.py:329` | **CONTRADICTED** (C15) | |
| `arb-red-<REQ>-<32 hex>`, `arb-red-commit-<sha12>-<32 hex>` | falsifiability receipts; `ghi-close` 7c: "cite that receipt id in the close comment" | `ghi-close/SKILL.md:321` | `src/gzkit/arb/red_reporter.py:47,75` | **CONTRADICTED** (C15) | |
| strict attestation id regex | `arb-(?:ruff\|step-[a-z][a-z0-9]*)-[a-f0-9]{32}` | — | `src/gzkit/governance/trust_audits/attestation_receipts.py:29` | SOURCED (see C15) | |
| loose archive id regex | `arb-[A-Za-z0-9.\-]+` "A receipt id as it appears in attestation evidence: the filename stem" | — | `src/gzkit/arb/archive.py:50-52` | SOURCED (see C15) | three receipt grammars |
| receipt store `artifacts/receipts/<run_id>.json`, `artifacts/receipts/archive/` | "receipt always emitted to `artifacts/receipts/<run_id>.json`"; "Move-not-delete" | `gz-arb/SKILL.md:67-72,93` | `src/gzkit/arb/paths.py:11-46` (`GZKIT_ARB_RECEIPTS_ROOT`, `config.arb.receipts_root`) | SOURCED | |
| proof id `proof-<32 hex>` | an acceptance proof | none found in what was read | `src/gzkit/acceptance_execution.py:617` | UNSOURCED | |
| acceptance "run id" = a `WP-` or `ORD-` id | "Say whether an acceptance id names a package or an order, never an OBPI" | `src/gzkit/acceptance_package.py:68-75` | `is_run_id` | **CONTRADICTED** (C9) | **run** |
| `gz wp runs` | "what the ledger says every run in flight, a package's or an order's, has reached" | `gz-wp/SKILL.md:294-295` (ruling 136) | (verb not read) | SOURCED | **run** = package or order in flight |
| `gz wp acceptance … review --receipt <run-id>` | here `<run-id>` is an ARB receipt id | `gz-wp/SKILL.md:68-69`; `acceptance_store.py:335-336` requires `arb-step-` | — | **CONTRADICTED** (C9) | |
| dispatch id `D-<16 hex>` | (draft § 3) | — | `src/gzkit/work_package_run.py:630` | (already in draft) | |
| flight-test sortie `S<N>` (S1 to S6) | "A sortie is one flight flown in a single sitting"; "one run = one sortie" | `.gzkit/skills/gz-flighttest/SKILL.md:16-19,90`; `docs/flighttest/manifest.md:16,49,70,95,120,146` | no machine id; record is the target's flight log | SOURCED | **run**; squawk, Chase, test director, card, campaign instance are SOURCED in the same skill (`:51-56,140-158`) |
| reuse receipt `.gzkit/cache/check-verified.json` | `gz check` pass for a staged tree | — | `src/gzkit/check_fingerprint.py:43` | SOURCED | "receipt" names both ARB evidence and a cache |

## Domain 11c — handoff file names and vocabulary

| Term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| handoff file `.gzkit/handoffs/<fs-ts>-<slug>.md` | "Handoff markdown file at `.gzkit/handoffs/{timestamp}-{slug}.md`" | `gz-session-handoff/SKILL.md:127,140,462` | `src/gzkit/handoff_api.py:1113` | SOURCED | store census: 1,205 `YYYYMMDDTHHMMSSZ-…`, 2 `YYYY-MM-DD-…`, 4 `OBPI-…` legacy names |
| `<fs-ts>` grammar | "The first 15 characters of the timestamp with `:`, `-` and `.` removed, suffixed with `Z`" → `YYYYMMDDTHHMMSSZ` | `handoff_api.py:322-333` | same; its docstring: "Local reimplementation of the module-private pattern in `handoff_validation`" | SOURCED | one grammar held in two modules |
| `<slug>` | "Short descriptor for filename (e.g. `create-workflow`)" | `gz-session-handoff/SKILL.md:118` | `--slug` required, free string (`src/gzkit/cli/parser_handoff.py:224`) | UNSOURCED (no grammar) | |
| mode `CREATE`, `RESUME`, `CHECKPOINT` | CHECKPOINT "is the mid-flight bookmark (GHI #756) … NOT a token surrender" | `gz-session-handoff/SKILL.md:146-147` | `HandoffFrontmatter.mode`, `src/gzkit/handoff_validation.py:197` | SOURCED | |
| decision `proceed`, `pause`, `hold`, `revert` | "`proceed` work the advised steps; `pause` / `hold` / `revert` do not"; "The grammar is borrowed from the airlock's `Decision`" | `gz-session-handoff/SKILL.md:362-371` | `src/gzkit/events.py:1501`; `parser_handoff.py:95`; airlock `Decision`, `src/gzkit/airlock/model.py:41-47` | SOURCED | **CONTRADICTED** across sets (C16): `proceed`, `pause`, `hold` |
| `handoff_resume_decided` | Layer-2 provenance event; "It **gates nothing**" | `gz-session-handoff/SKILL.md:60-64,103,106` | `events.py:1501` | SOURCED (gate retired: *"the handoff should be an advisor, not a gate-keeping nanny"*, 2026-08-15, `:334-340`, RULED) | |
| `[operator-ruled]` / `[agent-chose]` | attribution markers on Decisions Made | `gz-session-handoff/SKILL.md:157,163-178` | `_ATTRIBUTION_RE`, `handoff_api.py:443`; `handoff_validation.py:403` | SOURCED (GHI #696) | |
| staleness Fresh / Slightly Stale / Stale / Very Stale | < 24h, 24-72h, 72h-7d, > 7d | `gz-session-handoff/SKILL.md:274-280`; `assets/staleness-rules.md` (not read) | `classify_staleness` | SOURCED | |
| claim tags VERIFIED / STALE / UNVERIFIABLE | Claim Verification Gate | `gz-session-handoff/SKILL.md:290-296,422` | — | SOURCED | |
| rulings store `.gzkit/handoffs/rulings.jsonl`, `ruling_key` | append-only settled rulings | `gz-session-handoff/SKILL.md:194-203` | (not read) | SOURCED | |
| archive `.gzkit/handoffs/archive/` | move-not-delete | `gz-session-handoff/SKILL.md:64-67` | `src/gzkit/handoff_archive.py:144` | SOURCED | |
| transit / exchange / handoff | "transit is ecosystem movement through the airlock … exchange is one block's occupancy … handoff is session memory" | `gz-session-handoff/SKILL.md:34` | — | RULED (operator ruling, verbatim canon carried from `AGENTS.md`, 2026-09-17, `:32-36`) | **block** (token block) vs release "block" (C7) and `gz wp block` |
| shift turnover | "While `.gzkit/mx.json` is open … a session relief is a **shift turnover**" | `gz-session-handoff/SKILL.md:434` | not built (RP-12 ruling 19) | RULED: decision C11, operator *"a"* (`:434`) | |

## Domain 11d — ceremony file names (closeout and audit)

| Term / path | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| `ADR-CLOSEOUT-FORM.md` (ADR dir) | "Closeout ceremony workspace" | `gz-adr-closeout-ceremony/references/folder-structure.md:6` | `src/gzkit/commands/closeout_form.py:198`; 79 in store | SOURCED | |
| `closeout/CLOSEOUT.md` | evidence link collected for the audit report | — | `src/gzkit/commands/audit_cmd.py:124`; 0 in store | **CONTRADICTED** (C17) | |
| ceremony state file | skill: "ceremony state saved in `.gzkit/ceremonies/<ADR-ID>.json`" | `gz-adr-closeout-ceremony/SKILL.md:105,270,349,368` | `ceremony_state_path` → `<adr_id>.ceremony.json`, `src/gzkit/commands/ceremony_state.py:143-145`; 48 in store, all `.ceremony.json` | **CONTRADICTED** (C18) | |
| `<adr>.turn-lock`, `<adr>.hook-state.json` | turn lock; hook state | — | `ceremony_state.py:148-153` | SOURCED | |
| ceremony steps 1–11 (INITIALIZE, SUMMARY, DOCS_CHECK, WALKTHROUGH, EXECUTE, ATTESTATION, CLOSEOUT, ISSUES, RELEASE_NOTES, RELEASE, COMPLETE) | "Ceremony steps matching the audit-protocol.md ceremony" | — | `CeremonyStep`, `ceremony_state.py:25-38` | SOURCED | the skill's own Step 1–9 numbering differs from the CLI's 1–11 (it writes "CLI Step 6" beside "Step 5") |
| attestation values `Completed`, `Completed - Partial: [reason]`, `Dropped - [reason]` | Step 5 attestation | `gz-adr-closeout-ceremony/SKILL.md:188-191,330` | (`--attest` text) | SOURCED | |
| folder layout `docs/design/adr/adr-X.Y.x/ADR-X.Y.Z-{slug}/`, `briefs/`, `audit/AUDIT-ADR-X.Y.Z-COMPLETED.md` | "ADR Folder Structure (Canonical)" | `folder-structure.md:3-11` | store: `docs/design/adr/{foundation,pre-release,pool,meta}/`, 88 `obpis/`, 0 `briefs/`, 0 `AUDIT-ADR-*`; code reads `obpis/` (`audit_cmd.py:123`) | **CONTRADICTED** (C19) | |
| `audit/AUDIT_PLAN.md`, `audit/AUDIT.md`, `audit/proofs/*.txt` | plan scaffold; annotation shell; proof logs | `gz-adr-audit/SKILL.md:96-97,114,118,164-166,193`; templates `assets/AUDIT_PLAN.template.md:57-58`, `AUDIT.template.md:56-60` | `audit_cmd.py:156,203,41`; store 66 / 81 | SOURCED | |
| `logs/obpi-audit.jsonl` | per-ADR OBPI audit log | — | `src/gzkit/commands/obpi_audit_cmd.py:406,413`; 73 in store | SOURCED | |
| co-presence marker `.claude/plans/.pipeline-active-<adr-id>.json` | "writes the per-ADR co-presence marker"; "Do not hand-write the marker" | `gz-adr-audit/SKILL.md:234-240,283-285` | `src/gzkit/commands/adr_audit.py:1250`; OBPI form `:619` | SOURCED | |
| audit acceptance `accept audit` / `verify audit` | "the ADR audit-validation acceptance, **not** OBPI Gate-5 closeout"; then "The verbal ack IS the Gate-5 human-attestation event" | `gz-adr-audit/SKILL.md:241-251` | `gz adr emit-receipt --event validated` | SOURCED | **gate**: Gate 5 at ADR (see C3) |
| `docs/releases/RELEASE-v{version}.md` | in-flight release evidence written at bump | `gz-adr-closeout-ceremony/SKILL.md:245` | (not traced) | SOURCED | |
| `docs/user/operator_runbook.md` | "Runbook" reference | `gz-adr-closeout-ceremony/SKILL.md:415` | file does not exist; `docs/user/runbook.md` does | **CONTRADICTED** (C20) | |

## Domain 12 — the hexagonal architecture system package map

Table read in full: `pyproject.toml:104-126`. On disk: 29 top-level packages under `src/gzkit/` (airlock, arb, chores,
cli, commands, complexity, content, core, doc_coverage, eval, flags, foundation, governance, hooks, insights, justify,
kernel, knowledge, models, mx, ontology, personas, reporter, rules, schemas, skills, templates, validate_pkg,
validators) and 127 top-level modules. The map names two that exist (`gzkit.kernel`, `gzkit.cli`); the others it names
(`gzkit.core.domain`, `gzkit.core.ports.driving`, `gzkit.core.ports.driven`, `gzkit.core.handlers`,
`gzkit.configurator`) are not on disk. That is by design: "Regions name where code goes, whether or not the package
exists yet" (`pyproject.toml:110-111`); the checker refuses only a missing top-level package
(`src/gzkit/kernel/dependency_checker.py:266-270`).

| Term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|
| the hexagonal architecture system package map | "the list in `pyproject.toml` `[tool.py-gzkit]` that names each top-level package's part of the hexagon" | `docs/rnd/hexagonal-specification.md:830-842`; `docs/governance/hexagonal-architecture.md:95-96` | `[tool.py-gzkit.hexagon]`, `pyproject.toml:115`; `PackageMap`, `dependency_checker.py:126-133` | RULED: operator *"ok, i get it "hexagaonal architecture system package map" - pyproject.toml?"* (`hexagonal-specification.md:834-835`); "The table's key names are diamond 2's" (`:841-842`). Status **DRAFT**: "Its approval as a classic decision record waits on RP-6's identity crossover" (`pyproject.toml:109-110`; `harbor-ro15-project-structure.md:76-78`) | **package**: Python package vs work, repair, feature, return-to-service and Release packages (C21) |
| table name `[tool.py-gzkit]` vs `[tool.py-gzkit.hexagon]` | home settled by the house-style run; "named `[tool.py-gzkit]` because gzkit's distribution is `py-gzkit`" | `hexagonal-specification.md:825-828` | subtable `.hexagon` (`pyproject.toml:115`) | SOURCED (docs name the parent table, code the subtable; the key names were left to diamond 2, so not a contradiction) | |
| `package`, `source-root` | the import name and its directory | `dependency_checker.py:130-131,211` | `pyproject.toml:116-117` | SOURCED | |
| region `kernel` → `gzkit.kernel` | "one kernel package, a sibling of `core/` … stdlib and Pydantic only, and holds no gzkit governance concept" | `hexagonal-specification.md:975-1002`; `hexagonal-architecture.md:89-94` | `Region.KERNEL`, `dependency_checker.py:57`; package exists | RULED: operator *"ok"* (`hexagonal-specification.md:990`); name a draft: "The package lands as `gzkit.kernel`, flagged as a draft name" (`harbor-ro15-project-structure.md:92-93`) | "kernel" is not Evans' shared kernel (`hexagonal-architecture.md:93-94`) |
| region `domain` → `gzkit.core.domain` | entities, value objects, aggregates, domain services | `hexagonal-architecture.md:44,86-87`; `hexagonal-specification.md:844-857` | `Region.DOMAIN`; not on disk | RULED: *"Yes, rule it"* (`hexagonal-specification.md:846-847`); inner names "diamond 2's" | **core**: today `gzkit.core` holds legacy models, the identity seam among them (`core/models.py`), unmapped (C22) |
| region `driving-ports` → `gzkit.core.ports.driving` | the spec's "**input ports**: the use-case `Protocol`s" | `hexagonal-architecture.md:42`; ruling as above | `Region.DRIVING_PORTS`; not on disk | RULED (package design); the synonym pair input/driving is SOURCED only | |
| region `driven-ports` → `gzkit.core.ports.driven` | the spec's "**output ports**: the `Protocol`s the handlers call" | `hexagonal-architecture.md:45` | `Region.DRIVEN_PORTS`; not on disk | RULED (package design); output/driven synonym SOURCED | |
| region `handlers` → `gzkit.core.handlers` | "one per input port, orchestrating a use case" | `hexagonal-architecture.md:43` | `Region.HANDLERS`; checker rule `handler` | RULED (package design) | "handler" also names CLI handlers and hook handlers |
| region `driving-adapters` → `gzkit.cli` | "the CLI today, which turns a request into a command or query" | `hexagonal-architecture.md:41,88-89` | `Region.DRIVING_ADAPTERS`; package exists | RULED (package design) | |
| region `repository-adapters` → `[]` | "repository adapters: the domain, the kernel, their own library" | `hexagonal-architecture.md:115` | `Region.REPOSITORY_ADAPTERS` | SOURCED (the per-region-table ruling at `hexagonal-specification.md:1126` was not read in full) | |
| region `driven-adapters` → `[]` | "the code behind each output port (files, git, the ledger, GitHub)" | `hexagonal-architecture.md:46` | `Region.DRIVEN_ADAPTERS` | SOURCED | |
| region `configurator` → `gzkit.configurator` | "wires them at start-up"; "_Avoid_: composition root, bootstrap, assembly" | `hexagonal-architecture.md:48-50` | `Region.CONFIGURATOR`; may import every region; not on disk | RULED: operator *"configurator is better"* (`hexagonal-specification.md:645`) | |
| finding kinds `unmapped`, `import`, `base`, `handler` | four kinds of finding | `dependency_checker.py:7-23` | `Rule`, `:68-74` | SOURCED; "unmapped is a finding" RULED: *"A: unmapped is a finding"* (`harbor-ro15-project-structure.md:94-96`; `pyproject.toml:114`) | |
| kernel bases `ValueObject`, `Entity`, `DomainEvent`, `Command`, `Query`, `Dto` | each base and the regions a subclass may live in | `hexagonal-architecture.md:90`; `harbor-ro15-project-structure.md:72-75` | `BASE_REGIONS`, `dependency_checker.py:103-110` | SOURCED | |
| shrink-only baseline `data/hexagon_dependency_baseline.json` | today's findings held until migration | `pyproject.toml:112-114`; `hexagonal-architecture.md:255-273` | 177 at landing: 161 unmapped, 16 imports (`harbor-ro15-project-structure.md:113`) | SOURCED | |
| the domain's ubiquitous language | "the drydock's ruled names for its records, not today's legacy ones" | `hexagonal-architecture.md:250`; `hexagonal-specification.md:906-914` | — | **CONTRADICTED** (C5): the run names that ladder as "change proposal, engineering order, work package, task card, architecture decision record, block" | **order, package, task, block** |
| legacy mapping Port = foundation ADR, Adapter = feature ADR | "map Cockburn's port and adapter onto gzkit's ADR kinds" | `hexagonal-architecture.md:275-291` | — | SOURCED as legacy; the page itself records it "contradicts the specification above … reconciled by the house-style run's disposition row 4(c)" (`:279-281`) | |

---

## Contradictions

**C1. "work order".**
- `docs/governance/rnd-discipline.md:301`: "`work order` | a GHI is the work order and the receipt".
- `.claude/rules/agents-md-map-doctrine.md` § Attestation granularity: "the GHI is the work order and the receipt."
- `ghi-author/SKILL.md:4`: "file a GitHub issue when a finding needs its own work order"; `ghi-close/SKILL.md:404`: "stop this work order".
- against `rnd-discipline.md:432`: "work orders (the OBPI's successor)", and the draft § 1: "Order | Work order | Repair order | … **Gate 5**". The same discipline record holds both readings.

**C2. "freeze".** `rnd-discipline.md:300`: "`freeze` | … **the source collides with itself**; do not import it" — against `gz-wp/SKILL.md:59`: "**Freeze after the independent review.**" and the draft § 5 states `initiated → frozen → commenced …`.

**C3. Gate 5's level.** `rnd-discipline.md:299` and `agents-md-map-doctrine.md`: "Gate 5 is OBPI/ADR completion attestation (ADR-0.0.36) and nothing else" — against the draft § 1 (Gate 5 at the Order level) and `gz-wp/SKILL.md:80`: "**Close through Gate 5.**" for a work package, `:273`: "Gate 5 at the order closes it". `gz-adr-audit/SKILL.md:250`: "The verbal ack IS the Gate-5 human-attestation event" at the ADR. Gate 5 sits at three levels in live text.

**C4. "A repair order is a work package".** `docs/governance/harbor-ro5-work-packages.md:21`: "1. **A repair order is a work package** (selection *"A"*)" — against the draft § 1, where the repair order is the Order level and the work/repair package the Story level. Joins the draft's T10 list beside `safe-mode-doctrine.md:52,67`. Also `harbor-ro15-project-structure.md:8`: RP-15 is a "Repair order of the harbor pilotage contract".

**C5. The identifier ladder.** `docs/rnd/renewing-vows/identifier-migration-program.md:15-20` (ruled 2026-10-05, *'A', the artifact ladder*): "OBPI | work package | `WP-<NN>-<slug>`"; "feature ADR, the "(m)ADR" | engineering order | `EO-<semver>-<slug>`"; "pool ADR | change proposal | `ECP-<slug>`"; "TASK | task card"; "release | block". `hexagonal-specification.md:906-914` adopts that ladder as the domain's language. Against `rnd-discipline.md:430-433`: "work packages (the mADR's successor), work orders (the OBPI's successor), the Release Package", and the draft §§ 1–2 (`ORD-` orders, OBPI = legacy order). The 2026-10-05 ladder maps OBPI to *work package*; the 2026-11-12 reading maps it to *work order*. Neither source records that the later superseded the earlier. **Highest-consequence finding in this gather.**

**C6. "task card".** The 2026-10-05 ladder renames TASK to "task card"; `src/gzkit/models/catalog.py:218` describes a package's `procedure` as "The task cards, or NA" — against the draft § 1 Action level "Task".

**C7. "block".** `identifier-migration-program.md:20`: "release | block | no identifier" — against `gz-session-handoff/SKILL.md:34` "exchange is one block's occupancy" / "Token blocks", and `gz wp block` (`gz-wp/SKILL.md:116`), a stop at the fix-cycle bound.

**C8. Three closed sets reuse `proceed`, `pause`, `hold` with different meanings.** `events.py:1501` handoff decision `proceed | pause | hold | revert` (from airlock `Decision`, `airlock/model.py:41-47`); `events.py:1792` `WorkPackageDecision = proceed | redirect | pause | terminate` ("The Gate 5 decisions"); `events.py:1794` `WorkPackageExit = reopen | departure | hold | terminate`. `departure` also names a change-ladder rung and a departure from specification.

**C9. "run".** Six senses: the R&D run (`rnd-discipline.md:18`); `gz chores run`; the ARB receipt field `run_id`; the acceptance "run id" = a `WP-`/`ORD-` id (`acceptance_package.py:68-75`: "names a package or an order, never an OBPI"); `gz wp runs` (packages and orders in flight); "one run = one sortie" (`gz-flighttest/SKILL.md:90`). Inside one skill, `gz-wp/SKILL.md:68-69` writes `review --receipt <run-id>` for an ARB receipt while the code beneath calls the package id the run id.

**C10. `enhancement`.** GitHub label description: "New feature or request" — against `ghi-author/SKILL.md:203`: "Surface works as designed; the design could be tighter", and `AGENTS.md` § Operator Doctrine: "discovering that more is needed to fulfill the intent of a feature is not an enhancement, it is a correction".

**C11. `gh issue edit` in the attach verb.** `work_package_github.py:82`: `_gh("issue", "edit", str(issue), "--add-label", REPAIR_LABEL)` — against `.gzkit/rules/gh-cli.md:24-32` "Allowed commands" (list, close, comment, reopen, release create; no `edit`) and `ghi-author/SKILL.md:285-286`: "`gh issue edit` is outside `.gzkit/rules/gh-cli.md`'s allowed commands". Ruling 7 authorizes the label; the rule's allowed list was not amended.

**C12. The package-mark example.** `harbor-ro5-work-packages.md:31` and `work_package_github.py:5`: "`WP-07-astral-toolchain (RO-9)`" — against the store, `data/catalog/work_packages.json`: `WP-01-astral-toolchain`, aliases `['RO-9']`.

**C13. Chore lanes.** `gz-chore-runner/SKILL.md:23`: "`lane`: The configured lane reported by `gz chores show` (lite, medium, or heavy)" — against `registry.json` `lanes` (only `lite`, `heavy`) and `AGENTS.md` § Gate Covenant (two lanes).

**C14. `gz chores propose-ghi` bypasses `ghi-author`.** `chores_propose_ghi_cmd.py:91-109` runs `gh issue create … --label enhancement --label eval-feedback` — against `AGENTS.md` § Behavior Rules: "Author GHIs through `ghi-author`, whose prior-art lookup prevents duplicates", and `gh-cli.md:20`: "**`gh issue create` is forbidden as a direct agent invocation**". (A defect for tracking; this gather is read-only and filed nothing.)

**C15. Receipt-id grammar.** `step_reporter.py:21-25`: names must match the binding regex `arb-(?:ruff|step-[a-z][a-z0-9]*)-[a-f0-9]{32}`, else the gate rejects them "as `malformed_id`" — against the minters `obpi_complete.py:329` (`arb-meta-receipt-bind-…`; `canonical_steps.py:142` key `meta-receipt-bind`, hyphenated, outside `[a-z][a-z0-9]*`) and `red_reporter.py:47,75` (`arb-red-…`, `arb-red-commit-…`), which `ghi-close/SKILL.md:321` tells a close comment to cite. A third, loose grammar sits in `archive.py:52` (`arb-[A-Za-z0-9.\-]+`).

**C16.** Same as C8, handoff side: `gz-session-handoff/SKILL.md:362-366`: "The grammar is borrowed from the airlock's `Decision`; the records stay this layer's own."

**C17. Closeout form name.** `closeout_form.py:198`: `adr_file.parent / "ADR-CLOSEOUT-FORM.md"` (79 files) — against `audit_cmd.py:124`: `adr_file.parent / "closeout" / "CLOSEOUT.md"` (0 files). The audit report's evidence index can never include the closeout form (a code defect, untracked by this read-only gather).

**C18. Ceremony state file.** `gz-adr-closeout-ceremony/SKILL.md:105`: "ceremony state saved in `.gzkit/ceremonies/<ADR-ID>.json`" (also `:270,349,368`) — against `ceremony_state.py:145`: `f"{adr_id}.ceremony.json"` (all 48 files in the store).

**C19. ADR folder layout.** `gz-adr-closeout-ceremony/references/folder-structure.md:4-10`: `docs/design/adr/adr-X.Y.x/…`, `briefs/`, `audit/AUDIT-ADR-X.Y.Z-COMPLETED.md` — against the store (`foundation/`, `pre-release/`, `pool/`, `meta/`; 88 `obpis/`, 0 `briefs/`, 0 `AUDIT-ADR-*`, 81 `AUDIT.md`) and the code (`audit_cmd.py:123,156,203`).

**C20. Runbook path.** `gz-adr-closeout-ceremony/SKILL.md:415`: "Runbook: `docs/user/operator_runbook.md`" — the file does not exist; `.claude/rules/gate5-runbook-code-covenant.md` names `docs/user/runbook.md`.

**C21. "package"** (collision, not a contradiction between two sources): the hexagon's Python *package* and *package map* (`pyproject.toml:104-126`) share the word with the work package, repair package, feature package, return to service package and Release Package of the level table. The map's first key is literally `package = "gzkit"`.

**C22. The identity seam is outside every region.** The draft's T9 seam (`IdKind`, `src/gzkit/core/models.py`), the WP/ORD patterns (`src/gzkit/models/catalog.py`) and the TAG/ENT/DSC/D patterns (`src/gzkit/events.py`) all sit in modules the package map does not name (`gzkit.core` today is not `gzkit.core.domain`; `gzkit.models` and `events` are unmapped). The draft T9 states "No work, repair or drydock identifier resolves through it"; `harbor-ro5-work-packages.md:29` (ruling 6) states the `RO-n` names "stay as aliases resolved through RO-2's identity seam". Ruled intent and the code disagree, and the seam's future region is unassigned.

## Collisions with the draft's work and repair vocabulary (summary)

- **repair**: GHI label `repair`; package kind `repair`; chore rung `repair` and `operator-only-repair` (`chores_declaration.py:27`, 24 chores); dispatch role `Repair`; REQ specialization `repair`; GHI "repair assignment"; "Repair order" applied to packages (C4).
- **order**: "work order" = GHI (C1); level-table order; `EO-` engineering order (C5); `ORD-`.
- **package**: Python package / package map (C21); WP kind `delivery` (no level-table word); RP-n.
- **work**: "work order" (C1); "work package" = OBPI successor in 2026-10-05 ladder vs story level (C5).
- **task**: "task card" (C6); `TASK-wp-02-…` trailer spelling from a package id.
- **run**: six senses (C9).
- **gate**: Gate 5 at three levels (C3).
- **freeze**: fenced out by R&D, used as a package/order state (C2).
- **block**: release ladder, token block, `gz wp block` (C7).
- **proceed / pause / hold / departure / exit**: across three closed sets and the closure contract (C8).
- **check level C | D**: shared between chores and tags, consistently (no contradiction).

## Status counts (rows in the domain tables above)

| Domain | RULED | SOURCED | CONTRADICTED | UNSOURCED | Rows |
|---|---|---|---|---|---|
| 10a R&D | 25 | 4 | 3 | 0 | 32 |
| 10b insights | 2 | 7 | 0 | 1 | 10 |
| 10c GHI labels | 1 | 6 | 1 | 6 | 14 |
| 10d problem reports, close vocabulary | 5 | 5 | 1 | 0 | 11 |
| 10e `gz wp` issue vocabulary | 4 | 5 | 0 | 0 | 9 |
| 11a chores | 7 | 7 | 2 | 2 | 18 |
| 11b receipt and run ids | 1 | 9 | 4 | 1 | 15 |
| 11c handoff | 2 | 10 | 0 | 1 | 13 |
| 11d ceremony files | 0 | 9 | 4 | 0 | 13 |
| 12 hexagon map | 8 | 8 | 1 | 0 | 17 |
| **Total** | **55** | **70** | **16** | **11** | **152** |

(Tallied mechanically from each row's status cell, by its leading word.)

Notes on counting: a row whose term is ruled but whose example or adjacent claim is contradicted (`delivery`/`repair`
kinds, package mark, `gz wp attach`) is counted RULED; the contradiction is listed under Contradictions. The draft's
already-recorded `D-<16 hex>` row is not counted.

## Files read in full (line counts)

- `docs/governance/drydock-taxonomy.md` (149)
- `.gzkit/skills/gz-rnd/SKILL.md` (231); `.gzkit/skills/gz-rnd/assets/rnd-record-template.md` (81)
- `docs/governance/rnd-discipline.md` (454)
- `docs/rnd/check-outcome-reporting.md` (398)
- `.gzkit/skills/gz-insights-remember/SKILL.md` (97)
- `src/gzkit/insights/model.py` (54); `src/gzkit/insights/append.py` (66); `src/gzkit/insights/ledger_ref.py` (57)
- `.gzkit/skills/ghi-close/SKILL.md` (514); `references/problem-report-states.md` (40); `references/repair-assignment.md` (54)
- `.gzkit/skills/ghi-author/SKILL.md` (390); `references/examples.md` (51)
- `.gzkit/rules/gh-cli.md` (63)
- `.gzkit/skills/gz-wp/SKILL.md` (312)
- `src/gzkit/work_package_github.py` (83)
- `.gzkit/chores/registry.json` (1,340; read through a full JSON load of every entry and field)
- `src/gzkit/commands/chores_declaration.py` (194)
- `.gzkit/skills/gz-chore-runner/SKILL.md` (141)
- `.gzkit/skills/gz-arb/SKILL.md` (110)
- `src/gzkit/canonical_steps.py` (143); `src/gzkit/arb/paths.py` (49)
- `.gzkit/skills/gz-session-handoff/SKILL.md` (512)
- `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` (416); `references/cli-reference.md` (9); `references/folder-structure.md` (11)
- `.gzkit/skills/gz-adr-audit/SKILL.md` (387); `assets/AUDIT_PLAN.template.md` (64); `assets/AUDIT.template.md` (74)
- `pyproject.toml` (424)
- `docs/governance/harbor-ro15-project-structure.md` (141)

## Read in part (named so no absence claim rests on them)

- `docs/governance/chore-class-system.md` (1,600): lines 1-110, 279-508, 831-905, 1513-1517.
- `docs/governance/hexagonal-architecture.md` (388): lines 1-130, 212-300.
- `docs/rnd/hexagonal-specification.md` (2,646): entry headings; lines 638-651, 810-866, 894-916, 975-1004.
- `docs/rnd/renewing-vows/identifier-migration-program.md` (116): lines 1-30.
- `docs/rnd/contractor-kit.md`: lines 3059-3085 (decision B12).
- `docs/governance/harbor-ro5-work-packages.md`: lines 21, 25, 27, 29, 31, 51, 79, 83, 89-102 (by grep).
- `.gzkit/skills/gz-flighttest/SKILL.md` (178): lines 1-70, 114-178; `docs/flighttest/manifest.md` sortie headings.
- `src/gzkit/kernel/dependency_checker.py`: lines 1-135, 255-300.
- `src/gzkit/models/catalog.py`: lines 40-52, 195-246 and grep of enums.
- Code excerpts: `step_reporter.py:15-55`, `attestation_receipts.py:20-45`, `archive.py:40-60`, `acceptance_package.py:40-90`,
  `acceptance_store.py:325-340`, `acceptance_execution.py:600-625`, `handoff_api.py:322-334,1085-1125`,
  `handoff_validation.py:180-215`, `ceremony_state.py:25-62,130-155`, `audit_cmd.py:115-130`,
  `chores_propose_ghi_cmd.py:85-110`, `airlock/model.py:36-52`, `events.py:1501,1790-1800`.
- Live state: `gh label list --limit 200` (22) and `gh api --paginate …/labels` (22); `data/catalog/work_packages.json`;
  `.gzkit/handoffs/` name census (1,214 entries); `.gzkit/ceremonies/` (48); `docs/design/adr/` folder census.

Not read: `assets/staleness-rules.md`, `assets/handoff-template.md`, the `gz wp resolve` verb, `src/gzkit/tasks.py`,
`docs/governance/ieee/requirements-model.md`, RO-5 rulings 9, 10, 64 and 136 by their own text.

---

## Gap-fill (2026-11-22, second pass, read-only)

Closes the read gaps named above for four sources, each now read whole: `docs/rnd/hexagonal-specification.md`
(2,646 lines, paged 1-160, 160-639, 651-810, 810-866, 866-975, 975-1004, 1004-1303, 1303-1642, 1642-2041, 2039-2646),
`docs/governance/hexagonal-architecture.md` (388; the parts not read before, 128-213 and 296-388, now read),
`docs/governance/chore-class-system.md` (1,600; 110-279, 508-831, 905-1600 now read, with the earlier ranges) and
`src/gzkit/tasks.py` (701). Not re-read, by the coordinator's direction: `renewing-vows/identifier-migration-program.md`,
the other R&D records, `contractor-kit.md`, `harbor-ro5`, `requirements-model.md`.

### G1. Where hexagonal-specification.md adopts the 2026-10-05 ladder, and every later passage that bears on it

Adoption, in two entries:

1. `docs/rnd/hexagonal-specification.md:894-904`, **source · the identifier migration's ruled names** (read
   2026-11-08). It quotes the program's table: "pool ADR | change proposal | `ECP-<slug>` … feature ADR, the "(m)ADR" |
   engineering order | `EO-<semver>-<slug>` … OBPI | work package | `WP-<NN>-<slug>` … TASK | task card | `TASK-…` kept
   … ADR | architecture decision record | `ADR-<n>` … release | block | no identifier", and "Ruled 2026-10-05 ('A', the
   artifact ladder)".
2. `:906-914`, **decision · the domain's ubiquitous language is the drydock's ruled ladder, not today's names**. The
   operator's words: *"don't forget, the drydock will produce new names to replace mADR, OBPI, etc."* The entry then
   adds: "wherever this specification names gzkit's own domain, it uses the ruled ladder (change proposal, engineering
   order, work package, task card, architecture decision record, block), and today's names (feature ADR, OBPI) are
   treated as the legacy terms". The operator's sentence names neither the ladder nor any of its names. Binding the
   language to the 2026-10-05 ladder is the agent's reading, recorded as a decision with no question or options put.

The later passages, in record order:

3. `:1069-1071` (decision *entities are frozen*, 2026-11-09): the example states "were illustrative and will take the
   drydock ladder's names". It keeps the ladder in force without naming its terms.
4. `:1411-1421` (decision *every ledger event type belongs to an entity*): the operator quotes "a rename into the
   drydock vocabulary", then: *"we will NOT leave the ledger"*. The vocabulary is not specified.
5. `:2038`, disposition row 1, commissioned 2026-11-10 (*"Commission row 1"*). It maps the records the other way from
   the ladder: "(c) **Work packages**, the mADR's successors … grouping work orders"; "(d) **Work orders**, the OBPI's
   successors, each delivering REQs through its tasks"; "(e) **Release Packages**". Under the ladder a work package
   was the OBPI's successor and a release was a "block". "Task card" gives way to "tasks", "block" to Release Package,
   and engineering order and change proposal do not appear. **This is the first passage that supersedes the ladder in
   substance. It does not say so, and it does not cite the earlier entry.**
6. `:2041`, disposition row 4: "the specification worded in the new records' terms (outcomes, work packages, work
   orders), carrying no ADR or OBPI vocabulary forward."
7. `:2042`, disposition row 5: the routes are "a repair order in the drydock, a work order after return to service, or
   a GHI". That separates a work order from a GHI (see C25).
8. `:2046-2055`, **decision · row 1 is redrafted on the requirements catalog and the four levels (operator
   correction)**. Operator: *"this entire system is meant to be deprecated and superseded by the requirements catalog,
   the feature package, the work package, the work order, and the release package ==> "ADR and OBPI""*. "Row 5's
   routes were corrected in the same edit from *OBPI* to *a work order*."
9. `:2062-2094`, **source · how the old system maps onto the new records**. Operator verbatim: *"the work package is
   the old mADR, the work order is the old OBPI."* It cites the contract's ruling of 2026-10-30, "Amended 2026-11-03:
   the work package is the mADR's successor, the story; the work order the OBPI's; the feature package the epic,
   succeeding no earlier record." This is the clearest statement of the later mapping, and it rests on contract
   rulings of 2026-10-30 and 2026-11-03.
10. `:2101-2103` (resume, 2026-11-10): "Row 1 stands as redrafted … the commissioning is read as the operator's
    confirmation of it." The confirmation is inferred, not spoken.
11. `:2114-2116` and `:2131-2146`: "outcome row" collides with the catalog's Outcome, and the operator rules the term
    *variant* (*"A: variant"*). The Release/Outcome vocabulary of the requirements model is now the frame.
12. `:2542-2551` (row 4, sixth item, 2026-11-12, *"gz-rnd label"*): gz-rnd's row 1 is relabelled "catalog, packages,
    orders and decision records".
13. `:2632` (Close, restated challenge): "Every ledger event gets an owner and a name in the drydock's vocabulary." The
    vocabulary is not named.
14. `docs/governance/hexagonal-architecture.md:250`, the specification page the run produced: "The language of gzkit's
    own domain is the drydock's ruled names for its records, not today's legacy ones." It names no ladder.

**Finding.** After `:911`, no later passage in the record uses "engineering order", "change proposal", "task card",
"block", `EO-` or `ECP-` (a full read, confirmed by a search of the whole file). From `:2038` on, the record holds the
opposite mapping for "work package" (the mADR's successor, not the OBPI's) and replaces "block" with the Release Package.
Yet nothing withdraws or amends the `:906-914` decision. Both readings stand in one signed-off, funded record (C23).

### G2. Status changes to rows above

| Domain row | Was | Now | Ground |
|---|---|---|---|
| 11a staleness signal `accumulated-work`/`content-delta`/`elapsed-time` | SOURCED | RULED | the ratified field table, `chore-class-system.md:1087-1101` (ratification 2026-09-12, *"I ratify, with great enthusiasm, the entire plan."*, `:101-104`); `surfaces` ruled *"Declare content-delta (Recommended)"* (2026-09-14, `:1325-1327`) |
| 11a `periodDays`, `graceDays`, `surfaces`, `artifacts`, `paused` | SOURCED (part ruled) | RULED | same table, `:1095-1097` |
| 11a remediation category | SOURCED | RULED | same table, `:1098` |
| 11a `nonAuthority`, `governingRule` | SOURCED | RULED | same table, `:1099-1100` |
| 11a `frequency`, `vendor` | UNSOURCED | SOURCED | named as existing registry fields at the 2026-09-12 measurement (`:132-133`); no value set or meaning defined anywhere read |
| 12 region `repository-adapters` | SOURCED | RULED | per-region table, operator *"yes, and we strongly recommend adopters do this."* (`hexagonal-specification.md:1126-1143`) |
| 12 region `driven-adapters` | SOURCED | RULED | same ruling ("Other driven adapters import the driven ports, the kernel and their library") |
| 12 finding kinds `unmapped`/`import`/`base`/`handler` | SOURCED (unmapped ruled) | RULED | import: *"yes, fortify what gzkit already does."* (`:1119-1120`); base: *"yes: "does the kernel ship these base classes, with the test cross-checking each class's base against its region?""* (`:1334-1335`); handler: *"yes: "Shall I record A with that clarification …""* (`:1698-1699`) |
| 12 kernel bases | SOURCED | RULED | `:1327-1335` |
| 12 shrink-only baseline | SOURCED | RULED | `harbor-ro15-project-structure.md:94-96`, *"A: unmapped is a finding"* (held "in one shrink-only baseline") |
| 12 driving/driven ports, "synonym SOURCED only" note | note | note withdrawn | operator's own six parts, verbatim, name "input ports" and "output ports" (`hexagonal-specification.md:164-165`). The per-region ruling places commands, queries, results and use-case Protocols in `core.ports.driving` (`:1128-1131`), so input = driving and output = driven are ruled through that table |
| 12 the domain's ubiquitous language | CONTRADICTED | CONTRADICTED, sharpened | G1 and C23 |

### G3. New rows

| Domain | Term | Meaning as stated | Defined | Implemented | Status | Collision / note |
|---|---|---|---|---|---|---|
| 11a | chore status bands `overdue`, `due`, `unmeasured`, `paused`, `current` | `gz chores status` "renders every registered chore … and exits 0 in every band" | `chore-class-system.md:1315-1335`, `:906-915` | `gz chores status` (code not read) | RULED: *"indicators, chores shouldn't have a bunch of gates like the adr/obpi system"* (2026-09-12, `:945-948`) | |
| 11a | step stage `— <stage>` | "every `###` step under `## Workflow` ends `— <stage>` from the rung vocabulary" | `chore-class-system.md:1336-1349` | `audit_chore_rung_conformance` (cited, not read) | RULED: *"Declared step stages (Recommended)"* (2026-09-13, `:1340-1341`) | **stage** also names pipeline stages and the draft's § 9 "stages" |
| 11a | `chore` outside gzkit | commitlint: *"Other changes that don't modify src or test files"*; gzkit's chore "is a larger thing" | `chore-class-system.md:817-827` | `chore: … (gz git-sync)` commit subjects | SOURCED | "The shared word should not be read as a shared definition" (`:826-827`) |
| 11b | formal TASK id `TASK-<semver>-<NN>-<NN>-<NN>` | "`TASK-<semver>-<obpi_item>-<req_index>-<seq>`" | `src/gzkit/tasks.py:42-54` (ADR-0.22.0) | `TASK_ID_BODY`, `src/gzkit/core/models.py:72-75`; `TaskId.parse` | SOURCED | the field is named `obpi_item` |
| 11b | slug TASK id `TASK-<slug>[-#<ghi>]` | "the kebab slug-form `TASK-<kebab-slug>` with an OPTIONAL `-#<ghi>` anchor" | `tasks.py:255-266` | `TASK_SLUG_ID_BODY = r"TASK-[a-z][a-z0-9-]*(?:-#\d+)?"`, `core/models.py:79` | SOURCED: the anchor was "made optional by operator mandate (2026-06-01)" (`tasks.py:257`), a paraphrase with no verbatim words | `TASK-wp-02-resume-#1185` (gz-wp) matches this form, so the package id rides in a slug |
| 11b | TASK status `pending`, `in_progress`, `completed`, `blocked`, `escalated` | "TASK lifecycle states (exactly five)", with `_VALID_TRANSITIONS` | `tasks.py:102-120` | `TaskStatus` | SOURCED | `blocked` also names `gz wp block` |
| 11b | four-tier chain task → REQ → OBPI → ADR | "Resolve the four-tier traceability chain from a TASK identifier" | `tasks.py:1-8,537-553` | `resolve_task_chain` | **CONTRADICTED** (C24) | **order, task** |
| 11b | commit trailer set `Task:`, `Ceremony:`, `Eval-feedback-source:` | "The trailer set is CLOSED" | `.gzkit/rules/task-discovery.md` § Conventions | `tasks.py:253-266,469-534` | RULED: operator ruling 2026-09-01, verbatim *"never"* (task-discovery rule) | |
| 11d | `Ceremony:` trailer values (`gz-git-sync`, `adr-closeout`, `obpi-reconcile`) | "The value names the governing ceremony" | `tasks.py:472-481` | `_CEREMONY_TRAILER_RE` accepts any `\S+` | SOURCED (open set, examples only) | ceremony names with no closed set |
| 12 | `variant` | "one member of a hexagon handler's result union, the success value or one named error"; _Avoid_: scenario, outcome, outcome row, path, case | `hexagonal-specification.md:2131-2146`; `hexagonal-architecture.md:204-207` | none (needs a REQ `variants` field) | RULED: *"A: variant"* (2026-11-11) | ruled specifically to avoid a collision with the catalog **Outcome** |
| 12 | one distribution | "`uv_build` and uv workspaces take no part in boundary enforcement" | `hexagonal-specification.md:1706-1719`; `hexagonal-architecture.md:97` | `pyproject.toml` `[project]` | RULED: *"Keep one distribution"* (against the agent's recommendation) | |
| 12 | identifier value objects (`AdrId`, `ObpiId` today) | "a value object is a frozen Pydantic model created through `create(...) -> Self \| ValidationErrors` … a rule about the value is a method on its type"; "only adapters hold raw strings for a value with rules" | `hexagonal-specification.md:1004-1058`; `hexagonal-architecture.md:130-136` | `core/models.py:475-515` (per the record; "no module outside `core/models.py` names either type, and 449 fields … typed `adr_id: str` or `obpi_id: str`") | RULED: *"yes, A"* and *"yes"* (2026-11-09) | bears on T9: the ruled shape of every identifier in §§ 2-4 is a kernel `ValueObject`, and today they are `str` fields and regex constants |
| 12 | "the dependency rules" | "the may-and-must-not imports of each region"; _Avoid_: core purity, import purity | `hexagonal-specification.md:683-692` | `gz validate --hexagon-dependencies` | RULED: *"Yes, dependency rules"* | |

### G4. New contradictions

**C23. The ladder decision stands unretracted beside its opposite, inside one record.**
`docs/rnd/hexagonal-specification.md:910-911`: "it uses the ruled ladder (change proposal, engineering order, work
package, task card, architecture decision record, block)", in which an OBPI becomes a *work package*. Against
`:2038` (c)-(d): "**Work packages**, the mADR's successors … **Work orders**, the OBPI's successors", and the operator at
`:2066`: *"the work package is the old mADR, the work order is the old OBPI."* No entry withdraws the first, and the
record was signed off funded on 2026-11-11 with both in it. This sharpens C5: the 2026-10-05 ladder's own program page
(not re-read here) and this record's adoption of it are both unamended against the 2026-10-30/2026-11-03 mapping.

**C24. The TASK chain runs to the OBPI and ADR, never to an order.** `src/gzkit/tasks.py:1`: "TASK entity model for
fourth-tier governance (ADR-0.22.0)"; `:537-553` `resolve_task_chain` returns `task`, `req`, `obpi`, `adr`. Against the
draft § 1, where the Order holds "the REQ-to-task binding" and the Action level is the Task. No code binds a TASK to an
`ORD-` or `WP-` id. The package-derived trailer `TASK-wp-02-resume-#1185` (`gz-wp/SKILL.md:66-67`) is a slug form. It
is accepted only for presence (`_ANY_TASK_TRAILER_RE`, `tasks.py:266`) and skipped by `parse_task_trailers` ("slug-form
trailers are skipped", `:410-413`), so its link to the package is a naming convention with no parser.

**C25. "Work order" means a GHI and also something that is not a GHI.** These add to C1.
- `docs/governance/chore-class-system.md:620`: "Mining | decide whether a recurring pattern is worth a work order".
- `chore-class-system.md:1402`: "**Work orders.** GHI #936 covers step 2. Steps 1 and 3–6 are GHI #999".
- Against `hexagonal-specification.md:2042` (row 5): routes are "a repair order in the drydock, a work order after
  return to service, or a GHI", three distinct things.
- Against `:2038` (d): "Work orders, the OBPI's successors … with its freeze, inspection, buy-back and Gate 5".

**C26 (low; a dated record).** `chore-class-system.md:1289-1291` restates the CLI map as "`0` success, `1` user or
config error, `2` system or IO error, `3` policy breach", and `:1294-1301` records the parse-error exit 2 as a defect.
The live rule, `.claude/rules/cli.md` § Exit Codes, now reads "**2** | Usage or System/IO Error" and "every parse error
exits 2 — `StableArgumentParser.error`, attested REQ-0.0.4-02-03". The record is dated (2026-09-12, "design record"), so
it is not a live contradiction. It is listed so nobody cites the record's map as current.

**Refinement to C3 (not counted).** `hexagonal-specification.md:2038` (b) has the feature package's value "attested at
a work package's or Release Package's attestation". That is a fourth level carrying an attestation, beside Gate 5 at
the order (`:2038` (d)).

### G5. Revised status counts (165 rows)

| Domain | RULED | SOURCED | CONTRADICTED | UNSOURCED | Rows |
|---|---|---|---|---|---|
| 10a R&D | 25 | 4 | 3 | 0 | 32 |
| 10b insights | 2 | 7 | 0 | 1 | 10 |
| 10c GHI labels | 1 | 6 | 1 | 6 | 14 |
| 10d problem reports, close vocabulary | 5 | 5 | 1 | 0 | 11 |
| 10e `gz wp` issue vocabulary | 4 | 5 | 0 | 0 | 9 |
| 11a chores | 13 | 5 | 2 | 1 | 21 |
| 11b receipt, run and TASK ids | 2 | 12 | 5 | 1 | 20 |
| 11c handoff | 2 | 10 | 0 | 1 | 13 |
| 11d ceremony files | 0 | 10 | 4 | 0 | 14 |
| 12 hexagon map | 17 | 3 | 1 | 0 | 21 |
| **Total** | **71** | **67** | **17** | **10** | **165** |

(Domains 10a to 10e and 11c are unchanged. C26 is a dated-record note and is not counted as a row status.)
