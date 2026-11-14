# RP-7 change order of 2026-11-08 — placement: gate, chore or rule

A dated record of the change order the operator issued on RP-7, the context cut, on 2026-11-08, and
of the session that led to it. The contract carries the ruling, the order's row, its list-of-discrepancies
lines and the passage-log rows (`harbor-pilotage-candidate-2026-10-15.md`); this page holds the
detail they point to. **Grades in § Findings are proposed for the operator's review and are binding only
once the operator rules them.**

## The operator's words, in order

1. *"i think gzkit is bloated with the files and affordances of these kinds: https://code.claude.com/docs/en/memory"*
2. *"what gets loaded into the agent's context each session"*
3. *"too bloated, we need an audit, what does anthropic say? November 2026?"*, then *"All six sources"*.
4. The auto-memory band, one ruling at a time: *"Band C, auto memory"*, *"Yes, archive all 27"*, *"Yes, archive all 16"*, *"A: skill plus GHI"*, *"A: trust doctrine T4"*, *"A: amend the persona"*, *"they should, that is a shortcoming"* (personas carry no version), *"a"*, *"A: Stage 1 step"*, *"gz-plan-audit instead"*.
5. The rules band: *"Band B, rules"*, *"Approve all eight"*, then *"i question whether hexagonal-architecture is even needed on every python file - many of these are likely ill-conceived."*, *"Yes, re-audit first"*, *"Yes, policy first"*, *"Yes, retire it"*, *"A: stub, core glob"*, *"Yes, all unblocked"*.
6. *"there are many of these rules we'd want to closely review, I am not certain they are all still valid."*, *"Stop them"*, *"we just want to review all of these rules, how many are still useful and valid?"*, *"for that matter, we might have asked the same question of the hexagonal-architecture rule"*, *"yes, restore it so it can be reviewed"*.
7. *"review each "batch" - the keeps, the keeps in part, the retires. fix what is stale. review the outcomes with me"*
8. *"but what will these rules do? the filter is when the agent touches a python file, will the agent read the rules and behave accordingly? I wonder if everything should be chore based - just sweep through and correct that agents' bad habits?"*
9. *"we need to triage these rules and either: 1) gate, 2) keep as rule, 3) go to (or enhance existing) chore. Then, we need something that governs this decision in the future. Perhaps even a chore that evaluates all of the above and decides if they are placed correctly."*
10. *"chores and gates are strong, rules and memory files are weak"*
11. *"place this work into dry dock"*, then *"place the entire endeavor into the existing and ongoing drydock"*.
12. *"yes, I want to make sure we capture this well. Also, clean up leftover worktrees, that is sloppy."*

## Why this is RP-7's change order

The work scope is frozen at induction, so a finding *"is graded, not added"* and enters *"under its
owning order or a change order the operator issues"* (contract § Repair orders). RP-7 owns the control-plane
cut, rules first (stage 1, GHI #1246), and its own § Leads already carries the operator's *"if we had a
mature progressive disclosure system, most of these rules would not be needed"*.

## The change order

**Principle (operator, verbatim):** *"chores and gates are strong, rules and memory files are weak"*.

1. **Placement replaces stage 1's "no binding clause is removed or reworded" for rules.** Every clause
   found TRUE and NEEDED is placed in one of three homes:
   - a **gate**, when a check can detect a violation: the check runs on a gate (a `gz check` step, a
     hook, CI or pre-commit), and its failure message names the fix;
   - a **chore**, new or an existing one enhanced, when a periodic sweep can detect it after the fact;
   - a **rule**, only for judgment needed at edit time that neither a gate nor a chore can catch, with
     a glob that fires where the clause binds.

   A clause leaves a rule only for a named gate or chore, never into nothing; a STALE clause is
   corrected; a REDUNDANT or NO-OP clause is retired under `skill-surface-sync.md` § Retirement policy.
2. **The placement doctrine is captured in canon** so every future clause is placed by it, in the same
   home as the scorecard's Mechanical / Promotable / Judgment classes it extends (one home per meaning:
   Mechanical ≈ gate, Promotable ≈ a gate to build, Judgment ≈ chore or rule).
3. **A placement-audit chore**, new or folded into the control-surface audit chores
   (`control-surface-rule-vs-check-drift`, `control-surface-validator-reachability`), periodically
   checks that every clause in rules, skills, auto memory and `AGENTS.md` sits in its right home.
4. **The other sources of the six-source audit are placed by the same test:** root `AGENTS.md` (still
   cut only by the operator, stage 7), hooks and the session orientation, and the skill listing (its
   demotions still one list the operator rules, ruling 3).
5. **The work already landed is accounted here** (§ Landed) and measured under RP-1's protocol from
   this point (stage order, contract § Repair orders RP-7).

**Departure disclosed.** The stale-clause corrections of 2026-11-08 reworded binding clauses in 18 rules
under the operator's *"fix what is stale"*, before this change order, against stage 1's *"no binding clause
is removed or reworded"* (#1246). The session did not surface the conflict before landing them. This change
order supersedes that sentence for rules; the corrections stand, each listed in § Landed.

## Change order of 2026-11-12 — the hexagon test gates

**Authority.** The R&D run [`hexagonal-specification`](../rnd/hexagonal-specification.md) landed `.gzkit/rules/tests.md`
`0.28.0` § Hexagon tests on 2026-11-12; four of its clauses are scored Promotable, *"a gate to build"* in this change
order's own terms (item 2). Placed here by the operator, verbatim: *"A: RP-15 plus RP-7"* (contract § Rulings of
2026-11-12); the hexagon's structures are RP-15's tranche 6.

**Placed as gates**, each a check on a per-change gate whose failure names the fix, today's violations on a
shrink-only baseline, each declaring its two-way mode contract (`.gzkit/rules/mode-contract.md`):

| Clause | Scorecard row | Gate |
|---|---|---|
| Fakes only, inside the hexagon | tests-policy #91 | a test module covering a hexagon region imports no `unittest.mock`; the outer-edge exception read from the region the test covers |
| Given, when, then labels | tests-policy #91a | each hexagon unit test carries the three comments in order, read with `tokenize` |
| Every hexagon test names its REQ | tests-policy #91b | each hexagon test method carries `@covers`, fake-adapter tests exempt by declaration |
| One test per REQ and variant | tests-policy #91c | no two tests share a REQ and a variant, and none proves an undeclared variant |

**Kept as a rule:** *one recipe per artifact* (tests-policy #91d, Judgment).

**Depends on** RP-15 tranche 6: the gates learn which tests are hexagon tests from the package map.

**Held for the operator (H15).** The variant gate (#91c) reads each hexagon REQ's declared variants, and the
catalog's REQ schema (RP-3, closed) has no such field; `data/catalog/reqs.json` is empty. Either the field is added
under RP-5's tranche 6 (the catalog verbs after entry) and the gate lands with it, or #91c is regraded *due by the
first hexagon REQ admitted*. Recommended: regrade, since a count over zero REQs witnesses nothing. **Ruled
2026-11-12**, operator, verbatim: *"Yes, regrade"*.

**Grade.** #91, #91a and #91b block return to service, by the timing ruling; #91c is due by the first hexagon REQ
admitted (H15).

**Rulings of 2026-11-13**, each from options put with measurements (operator, verbatim):

- *"Regions incl. adapters"*: the gates hold every test module covering the domain, either port package, the handlers
  or an adapter region, over inner regions only. Today that is the 164 modules importing `gzkit.cli`.
- *"Exclude the kernel"*: `tests.md`'s list of regions, over the checker's `INNER` set, which includes it.
- *"Per patch target"*: an inner-region test imports no `unittest.mock`; an adapter test may patch only targets
  outside the package, and a bare double is a finding. Over judging by region alone, which would hold no CLI test.
- *"Module comment marker"*: a fake adapter's test module declares `# hexagon-test: fake-adapter` to leave the
  `@covers` gate, over a class attribute.

**Landed 2026-11-13.**

| What | Where | Commit |
| --- | --- | --- |
| The checker, three gates | `gzkit.governance.trust_audits.hexagon_tests`; 21 tests in `tests/governance/test_audit_hexagon_tests.py` | `f8d1a8f14` |
| The independent review's repairs | the inner `unittest.mock` reach, keyword patch targets, the missing doubles, an adapter-patch breach planted in `NC:hexagon-tests`, undecodable modules | the commit after `eb76acdd5` |
| The scope, baseline and controls | `gz validate --hexagon-tests` in the default tier; `data/hexagon_test_baseline.json` (6,136 findings: 3,540 labels, 2,295 covers, 301 mock), a registered shrink-ratchet; `NC:hexagon-tests`, `NC:hexagon-tests-baselined` | `d6eb328eb` |

**Mode contract** (`.gzkit/rules/mode-contract.md`), stated here until RP-13 builds the declaration shapes.

| Control | Operational | Hangar | Drydock | MEL entry | Self-test |
| --- | --- | --- | --- | --- | --- |
| `gz validate --hexagon-tests` | on (exit 3) | advisory, demoted by the MX checkpoint | advisory, demoted by the MX checkpoint | (M) none needed: an advisory run still prints every finding; (O) a new finding can land while the hangar is open; placard: the `[MX advisory]` line; restore: the exit re-run at full strength; accepted state: findings no more than the baseline holds | `NC:hexagon-tests` and `NC:hexagon-tests-baselined`, run on every `gz check` by its *Enforcement floor* step |

## Landed (2026-11-08)

| What | Where | Commit |
|---|---|---|
| Six-source audit: recommendation, rules, hooks/orientation/skills tables | `.gzkit/chores/instructions-files-diet/proofs/` | `aca557bbf` (swept into an RP-12 commit); the chore log in `5a0bfb85e` |
| Auto memory: 27 duplicate and 16 stale files archived, index 7,798 → 428 B | `~/.claude/projects/…gzkit/memory/_archive/` (outside the repository, restorable) | — |
| Rule 1 of 5: commit subjects say what changed | `git-sync` skill 1.5.0; GHI #1313 | `df08d2a00` |
| Rule 2 of 5: no silent skip or drop | `trust-doctrine.md` Invariant T4 | `02745c673` |
| Rule 3 of 5: ceremonies are design occasions | `pipeline-orchestrator` persona; GHI #1314 | `b7b788144` |
| Rule 4 of 5: markdown at rest, XML at the LLM boundary | rendering-substrate § Prompt markup; GHI #1315 | `77c3fed6e` |
| Rule 5 of 5: stop when an objective is already met | `gz-plan-audit` 6.6.0 Step 3a | `c6f350e6a` |
| Rule retirement policy | `skill-surface-sync.md` 0.14.0, scorecard row 33d; GHIs #1316, #1317 | `6e6d35134` |
| hexagonal-architecture stub, then restored for review | 0.4.0, reverted to 0.3.1 | `532a071b9`, `31372200c` |
| Validity review of all 27 rules (455 clauses) | `proofs/rules-validity-{A,B,C,D}-2026-11-08.md` | `f3469d334` |
| Stale clauses corrected, batch C | agent-failure-modes, security-sensitivity, complexity-doctrine, complexity-thresholds | `f3469d334` |
| Stale clauses corrected, batch A | pythonic, models, cli, hexagonal-architecture 0.4.1 | `a45dcb505` |
| Stale clauses corrected, batch D | chores, mx-mode, model-selection, skill-surface-sync, agents-md-map-doctrine | `200c7dc02` |
| Stale clauses corrected, batch B; rows 28, 37, 38, 39 Mechanical → Promotable | tests, task-discovery, token-block-discipline, tool-skill-runbook-alignment, adr-audit; mechanical-witness grandfather 65 → 61 | `e4fa52776` |

The validity verdicts: **KEEP 2** (mode-contract, skill-authoring), **KEEP-PARTIAL 21**, **RETIRE 4**
(gate5-runbook-code-covenant, weaponeering, brief-heading-conventions, agents-md-map-doctrine). Of 455
clauses, about 368 TRUE, 39 STALE, 48 UNVERIFIABLE; about 160 NEEDED, 239 REDUNDANT, 48 NO-OP. These
verdicts are the input to placement, not its output.

## Held for the operator's ruling

Doctrine the code contradicts, where correcting the text would re-rule doctrine. Each is in the batch's
validity table with its evidence.

| # | Clause | The conflict | Recommended |
|---|---|---|---|
| H1 | hexagonal rule 1, *"Any third-party import … is confined to an adapter module behind a port"* | yaml in 21 modules, rich in 65, jsonschema in 7 (`governance/`, `ontology/okf.py`) behind no port; the witness covers `src/gzkit/core/` only; row 64 scores the universal sentence Mechanical | narrow to the core plus new heavy dependencies through an adapter Bears on this, recorded 2026-11-12: the R&D run `docs/rnd/hexagonal-specification.md` ruled a per-region dependency table that bounds every region, adapters included, enforced by the dependency-rules test widened from `core/` to every region of the package map with a shrink-only baseline; that is the universal reading, against this row's recommendation. Not ruled here; H1 stays the operator's. **Ruled 2026-11-13:** *"A: Universal"*; rule 1 stays universal, and the per-region dependency table through `gz validate --hexagon-dependencies` is its witness |
| H2 | pythonic principle 9, *"<=50 lines/function, <=600 lines/module"* | the canonical table blocks at 37.0 and 3130.24; a second threshold authority | cite the table, keep <=300 for classes. **Ruled 2026-11-13:** *"A: Cite the table"* |
| H3 | complexity-thresholds, *"none of them owns its own thresholds"* | Ruff max-complexity 20 and cognitive 15 gate while the table blocks `lizard_ccn` at 11 | the gates read the table. **Ruled 2026-11-13:** *"A: Gates read table"*; the build is F23 |
| H4 | security-sensitivity § Heightened walkthrough | the checklist heading the code reads does not exist, so the checklist renders empty; the `security` scanner slot is empty; the co-presence gate was removed (GHI #1308) | add the checklist section now; route the scanner and renderer to work. **Ruled 2026-11-13:** *"A: Add checklist now"*; the section landed in `security-sensitivity.md` 0.7.0, the scanner slot stays F3's build |
| H5 | security-sensitivity, *"returns ADVISORY and the exit-3 errors above are dropped"* | `--sensitivity`'s own handler never consults the checkpoint | the handler honours the checkpoint. **Ruled 2026-11-13:** *"A: Handler honours it"*; repaired in the same commit, test-first |
| H6 | scorecard row 48, Mechanical on `--sensitivity` | no `gz check` step runs the scope; two live floor violations (OBPI-0.39.0-01, -02) go unseen | wire `--sensitivity` into `gz check`. **Ruled 2026-11-13:** *"A: Wire into gz check"*; default tier, the two briefs on RP-7's list |
| H7 | complexity-doctrine, *"(e.g. p90 = 7)"* | radon's figure; Lizard's p90 is 8; `test_citation.py` (REQ-0.0.27-05-02) pins the string | change it and loosen the test to the pairing the REQ requires. **Ruled 2026-11-13:** *"A: Fix and loosen"* |
| H8 | mx-mode, *"Do not exit the hangar while any detectable defect remains unfixed"* | `safe-mode-doctrine.md` § The instruments 5: the exit clears blockers and the handback transfers the rest; hangar and drydock are synonyms (2026-11-03) | reword to the doctrine. **Ruled 2026-11-13:** *"A: Reword to doctrine"* |
| H9 | model-selection, *"never on the dispatch call"* | the Agent tool now has a per-call `effort` input | operator's choice. **Ruled 2026-11-13:** *"A: Definition only"*; claim 4 stands, and the definitions' `effort:` is F24 |
| H10 | scorecard rows 31 and 32, Mechanical | their notes claimed version comparison that does not exist; only version presence is enforced | operator's choice. **Ruled 2026-11-13:** *"A: Re-score row 32"*; row 31 stays Mechanical, row 32 Promotable |
| H11 | scorecard row 26, Mechanical | `audit_pydantic_models` checks only that `model_config` exists | re-score Promotable, or extend the audit |
| H12 | brief-heading-conventions, `### Closing Argument` *"by H3 heading match"* | `commands/common.py:578` matches H2 only, while 136 briefs use H3, so the Defense Brief gets no closing argument | fix the code |
| H13 | agents-md-map-doctrine, verdict RETIRE | `test_agents_md_map_doctrine.py` (REQ-0.0.54-01-01) asserts the file exists | operator's choice under the attested-REQ rule |
| H14 | root `AGENTS.md` (Band A) | 98 % of its entry bytes are `tier: invariant`; the 2026-10-16 ruling declined re-tiering | operator retires or re-tiers named entries (stage 7) |
| H15 | tests-policy #91c, the variant gate (change order of 2026-11-12) | the catalog's REQ schema has no `variants` field and no REQ is admitted | regrade *due by the first hexagon REQ admitted*. **Ruled 2026-11-12:** *"Yes, regrade"* |

## Findings, graded (proposed)

The list's grades: **blocks** (blocks return to service), **due** (due by the named event), **deferred**
(carried into civil rule with a holder and a revisit condition). GHIs #1313 to #1317 are already filed.

| # | Finding | Grade (proposed) |
|---|---|---|
| F1 | `gz content compose AGENTS.md --consumer root` fails its invariant-floor check on `corpus-governance-doctrine-surfaces-2026-10-18…`, though the text is verbatim at `AGENTS.md:239` | due by RP-7 stage 7 |
| F2 | five `gz validate` scopes canon calls witnesses run on no gate: `--cli-alignment`, `--skill-alignment`, `--test-tiers`, `--brief-headings`, `--behave-req-tags`; `--sensitivity` was explicit-only too (default tier since 2026-11-13, H6), so `AGENTS.md`'s *"`uv run gz check` runs every registered validator"* is false | blocks (change order item 1: a gate's check runs on a gate) |
| F3 | the security Gate 5 walkthrough renders an empty checklist and no scanner runs (H4) | blocks |
| F4 | two live sensitivity-floor violations, OBPI-0.39.0-01 and -02, unseen (H6) | blocks |
| F5 | the Defense Brief gets no closing argument from any H3 brief (H12) | due by RP-12's close |
| F6 | `prefer-lsp` blocks text searches of command output or filenames as "Python symbols" (eight false blocks in this session); a repeat always passes, so it enforces nothing | due by change order item 4 |
| F7 | hook messages name skills that do not exist, `/gz-obpi-audit` and `/prior-art`, also in the generator templates `src/gzkit/hooks/scripts/` | due by change order item 4 |
| F8 | `obpi-completion-validator` still branches on Heavy/Foundation lane for human attestation; Gate 5 is universal | due by RP-14 tranche 2 |
| F9 | the session orientation changes state on every run (fetch, lock reaping, ledger rows), runs again on PreCompact whose output is not injected, takes about 20 s and exceeds its 4 KB budget | due by change order item 4 |
| F10 | `plan-audit-gate` reads the global `~/.claude/plans/`; `stop-turn-feedback` lints every git-dirty `.py` with a 2 s timeout; four advisory hooks may never reach the model (stderr, exit 0; unverified) | due by change order item 4 |
| F11 | RP-7 ruling 1, nested `AGENTS.md` no longer generated, is not landed: sync still writes them | due by RP-7 stage 2 (the order's own) |
| F12 | rule globs that miss where their clauses bind: cli (misses `src/gzkit/cli/`, 608 of 674 `add_argument(` calls), agents-md-map-doctrine and model-selection (generated mirrors, not canon), guardrail-feedback-prose (includes the generated hooks mirror); gh-cli, task-discovery and mx-mode bind at shell, commit or session time, where a path rule never loads | due by change order item 1 |
| F13 | `tests/commands/test_knowledge.py:33,64,149` call `shutil.rmtree` in `tearDown`, against tests.md | deferred (holder: RP-7 placement of tests.md; revisit: the tests rule's placement) |
| F14 | stale comments and docstrings: `obpi_complete.py:1511` "TTL reaping"; `check_module_size.py` band figures; `guards.py:582-584` post-authoring pin; `validate_commit_trailers.py:110` cites a nonexistent `AGENTS.md` § Workflow; `obpi_precomplete.py:621` git-sync claim; `.pre-commit-config.yaml:15` and `safe-mode-doctrine.md` name the retired `mode: safe`; `hexagonal-architecture.md` lists the retired `FileConfigStore` and `tests/fakes/`; `cli-standards-v3.md` marks the live `tests/policy/` Superseded; `gz-adr-audit` describes a marker proof nothing reads; the gz-obpi-pipeline stage-5 reference says "left for TTL reaping" (inventory-rendered, RP-14) | deferred (holder: RP-6, contradicted canon; revisit: RP-6's close) |
| F15 | `_DATACLASS_WAIVERS` keeps a dead waiver for `obpi_precomplete.py::CheckResult`, now a BaseModel | deferred (holder: RP-7 placement of models; revisit: same) |
| F16 | `storage-tiers.md` forbids environment variables in config while feature flags read `GZKIT_FLAG_*` (`flags/service.py:93`) | deferred (holder: RP-6; revisit: RP-6's close) |
| F17 | `gz-obpi-pipeline` § When to Use lists "After exiting plan mode for an OBPI", which may invite self-initiation against `AGENTS.md` § OBPI Acceptance Protocol | due by RP-14 tranche 2 |
| F18 | CLI shape drift no check holds: `mx` both leaf and group, 15 bare-root collisions, 73 of 180 leaves without `--json`, 91 help lines over 80 characters | deferred (holder: the CLI rule's placement; revisit: item 1 for cli.md) |
| F19 | the agent-definition budget measures whole files, though only the descriptions (~650 B) reach the main session | due by RP-7 stage 5 |
| F20 | another session's `git add -A` swept this session's proof files into its commit `aca557bbf` under an unrelated subject; the same class as #708 and #1313 | deferred (holder: GHI #1313; revisit: its fix) |
| F21 | eight subagent worktrees and branches were left on disk after their work stopped or landed (removed 2026-11-08, insight recorded) | cleared 2026-11-08 |
| F22 | the hexagonal rule's one gate, `tests/policy/test_import_boundaries.py` (core imports stdlib and Pydantic only), runs in no per-change `gz check`: `_select_changed_tests` (`src/gzkit/commands/quality.py:1382`) selects tests by a changed module's filename stem and the test carries no `@smoke`, so a third-party import added to `src/gzkit/core/` passes locally and fails only under `gz check --full` or CI after the push. Found 2026-11-08 reading the code in answer to the operator's question whether a hexagonal chore exists (none does; gz-skills' read-only `gzs-hexagonal-architecture-audit` is the nearest candidate for one); recorded on the operator's word, *"Yes, record both"* | due by change order item 1 for `hexagonal-architecture.md`, with H1 (proposed) |
| F23 | the cyclomatic gates own their threshold: Ruff `C901` and `gz validate --complexity-ceiling` stop at `[tool.ruff.lint.mccabe] max-complexity` (20) while the table blocks `lizard_ccn` at its own value; measured 2026-11-13, 77 functions in `src/gzkit` exceed the table's block value and none exceed 20. Repair, by H3 (operator, *"A: Gates read table"*): both gates read the table's `lizard_ccn` block band, the functions over it held in a shrink-only baseline; the cognitive ceiling (`.gzkit.json` `complexity.cognitive_ceiling`) stays a declared exception until a distillation pass gives the table a cognitive metric | due by RP-7's close (proposed) |
| F24 | `model-selection.md`'s effort allocation by role is advisory: every definition under `.claude/agents/` carries `model: inherit` and no `effort:`, so every subagent runs at the session's effort. Repair, by H9 (operator, *"A: Definition only"*): effort stays on the definition, never the dispatch call, so each role in the allocation table gets a definition carrying its `effort:`, one per role and effort band where the bands differ | due by RP-7's close (proposed) |
