# Census: chores against the alarm test

> Source for the R&D run [`repair-work-organization`](../../repair-work-organization.md). A dated
> record of the tree on 2026-11-02, not canon. It assigns no check level and recommends nothing.

- **Date:** 2026-11-02.
- **Population:** every entry in `.gzkit/chores/registry.json`, 41 chores.
- **Read in full:** 41 of 41 `CHORE.md`, and every `acceptance.json`.
- **Rung check:** repair 18, propose 17, operator-only-repair 6, matching the commission.
- **Band check:** `uv run gz chores status --json` gives overdue 31, unmeasured 3, current 7.

## Method

**Scripts read in full:** `check_reachability.py`, `check_ledger_inertness.py`, `check_debt_target.py`, `check_module_size.py`, `check_memory_drift.py`, `check_cross_reference_staleness.py`, `check_evidence.py`, `scan.py`, `eval_feedback_cluster_lib.py`, `eval_feedback_cluster_run.py`, `radar.py`, `correction_mining.py`, `failure_classes.py`, `tests/tools/test_health_profiler.py`, `scripts/check_proof_freshness.py`, and `src/gzkit/commands/chores_exec.py`. The skill `gz-deps-upgrade` was read in full because `dependency-currency` step 4 applies it.

**Controls read in full:** `.pre-commit-config.yaml`, `.claude/settings.json`, `src/gzkit/hooks/guards.py`, `src/gzkit/mx/invariants.py`, `checkpoint.py`, `alarms.py`, and the hooks `pipeline-gate`, `ledger-writer`, `post-edit-ruff`, `session-staleness-check`, `stop-turn-feedback` and `verifier-pipe-gate`.

**Read in part only, so weaker:** the `gz check` level table in `src/gzkit/commands/quality.py` (lines 62 to 148 and the step list), `frontmatter_coherence.py` (matched lines), `ruff_baseline.py` (matched lines), `complexity_advise.py` (lines 175 to 350), `data/waiver_ratchet_registry.json` (surface rows).

**Not read:** the hooks `obpi-completion-validator`, `plan-audit-gate`, `pipeline-router`, `pipeline-completion-reminder`, `ghi-triage-chat-silence`, `prefer-lsp`, `mx-awareness`, `session-exit-bookmark`. Nor were the skills a chore points at, other than `gz-deps-upgrade`. No chore was run. `gz chores status` was run once.

**Run data.** "Log" is the count of timestamped blocks in `proofs/CHORE-LOG.md`, then how many carry `Status: PASS`. "Pass" is `last_run` from `gz chores status --json`, shortened to its date. Hand-written log headings carry no time and are not in the counts. A run block records acceptance criteria only: `gz chores run` executes criteria, never a Workflow step (`docs/governance/chore-class-system.md` § Implementation order, step 3), so a block does not show when a repair was made.

**The verdict rule is the auditor's inference.** The ruled test asks whether the work can be done with every alarm on. Read literally, it separates almost nothing, because no procedure asks for an alarm to be lowered (§ Population findings, 1). So the rule below also applies the operator's second concern, a safeguard changed while armed:

| Verdict | Rule applied |
|---|---|
| **line** | The run writes proofs, reports or its own artifacts; or a subject no control takes as its standard; or only a shrink the armed ratchet itself demands |
| **out of service** | A declared step re-authors a control, or what a control judges by: a rule, canon, a threshold, a permission grant, a baseline rewritten wholesale, a test that binds a REQ, or the tool a gate runs. After that write the alarm judges by a different standard, so it cannot vouch for the change |
| **unclear** | The answer turns on the instance: the scope reaches control code with no fence, or the text and the declaration disagree |

"Control" here means a hook, a pre-commit guard, a `gz check` step or a `gz validate` scope. **Clear** and **judgment** in the table mark whether the control write is stated in the procedure or is a reading of its scope.

## Alarm reference

What fires on a repair chore's writes with the marker closed:

| Surface | Fires on | Under an open marker |
|---|---|---|
| `gz lint`, pre-commit and pre-push | staged Python, whole tree at push | stays on, pinned CRITICAL |
| `complexity-ceiling`, `surface-fidelity-cheap` | commit | stays on, pinned |
| `forbid-pytest`, `post-authoring-src-commits`, `enforcement-floor` | commit, in `gzkit.hooks.guards` | stay on, pinned CRITICAL |
| `ledger`, `gate5-attestation` | commit | stay on, `GATE5_INVARIANTS` |
| `gitleaks`, `authorship`, `ty-check`, `ruff-format`, `uv-lock` | commit | stay on, never routed through the alarm switch |
| `skill-sync-drift` | commit, canonical skill or rule without its mirror | demotes |
| `pipeline-gate` | Write or Edit under `src/` or `tests/` with a governed OBPI armed | demotes |
| `gz-check-pre-push` | push | off at the drydock level |
| `validator-reachability-ratchet`, `ledger-vocabulary-inertness` hooks | commit | off at the drydock level |
| `gz check` steps at ERROR level, including `Waiver ratchet`, `Module size`, `Tautological debt`, `Invariant coherence`, `Rendition freshness`, `Test`, `CLI audit` | push | demote, and the push hook that runs them is off |
| `gz validate --commit-trailers` | a `src/` or `tests/` commit with no `Task:` trailer | inside the push gate above |

## Census

PL marks `projectLocal: true`. Staleness reads signal, then period where declared (`cd` content-delta, `et` elapsed-time, `aw` accumulated-work; grace is 7 days except `dependency-currency`, 1 day).

| Chore | Class, rung | Stale | PL | What a run writes | Alarm crossed, marker closed | Bypass in procedure | Modifies a control | Runs | Verdict and reason |
|---|---|---|---|---|---|---|---|---|---|
| `arb-pattern-extraction` | mining, propose | et 30 | | Proof only: *"analysis only, no code changes"* | None | None | None | Log 6/5; last 10-10 FAIL (`gz arb validate`); pass 07-31; overdue | **line.** Report only |
| `cli-contract-governance` | conformance, op-only | cd | | Source and docs: *"land each breaking change the report names, updating manpages and runbooks"* | `Test`, `CLI audit`, trailers, lint | None | **Judgment.** A breaking change may move an exit code a hook or gate reads | Log 5/4; last 07-31 PASS; overdue | **unclear.** Step 4 is cosmetic; step 5 can change exit codes |
| `competitor-radar-currency` | currency, propose | et 30 | PL | Own reports: *"The scan writes only its own report"* | `radar.py validate` | None | None | Log 0; scan record 10-26, under the marker; current | **line.** Reports only. Steps that write the scan are staged `observe` |
| `complexity-reduction-xenon` | conformance, repair | cd | | Source and baselines: *"the lowered or deleted row, with `baseline_count` in `data/waiver_ratchet_registry.json`, is committed with the refactor"* | Ceiling, lint, `Test`, `Waiver ratchet`, trailers | Near-route: *"Pre-attest functions ... via the `@intrinsic_complexity` decorator"* | **Clear,** shrink of a gate baseline. **Judgment,** scope `src/gzkit` includes guards | Log 4/4; last 07-31 PASS; overdue | **unclear.** The shrink is what the ratchet demands; the decorator and the unfenced scope decide it |
| `config-paths-remediation` | conformance, repair | cd | | Source: *"Replace string literals with config-driven path construction."* | `gz check-config-paths`, lint, `Test`, trailers | None | **Judgment.** Surfaces include `.gzkit.json`, the manifest; scope reaches guards | Log 6/6; last 07-31 PASS; overdue | **unclear.** Config a gate reads is in scope, with no fence on control code |
| `control-surface-permission-consent-drift` | conformance, op-only | et 30 | PL | Proofs in steps 1 to 5; step 6 *"apply `proofs/settings-patch.md` to its source files"* | None for proofs. Step 6 reaches `.claude/settings.json` | None | **Clear.** Step 6 edits the permission surface | Log 6/5; last 10-10 PASS; scan 10-10 UTC 10-11; current. Patch is `DRAFT, not applied` | **out of service.** Step 6 only; steps 1 to 5 are line |
| `control-surface-rule-conflicts` | coherence, propose | cd | PL | Proofs: *"zero file edits outside"* its proofs | None | None | None | Log 16/12; last 10-10 PASS; overdue | **line.** Report only |
| `control-surface-rule-vs-check-drift` | coherence, propose | cd | PL | Proofs: *"zero edits to rules, validator, or source"* | None | None | None | Log 8/6; last 09-19 FAIL; pass 08-09; overdue | **line.** Report only |
| `control-surface-skill-rule-reachability` | coherence, propose | cd | PL | Proofs: *"zero edits to skills, rules, or source"* | None | None | None | Log 13/10; last 10-11 PASS; overdue | **line.** Report only |
| `control-surface-validator-reachability` | coherence, propose | cd | PL | Proofs: *"this chore never edits `src/gzkit/commands/validate*` or any check implementation"* | Its script is itself an alarm hook and a `gz check` step | None. `--report --write` exists, refuses growth, and is in no Workflow step | None by the procedure | Log 2/0; last 09-19 FAIL (freshness); never passed; overdue | **line.** Report only |
| `coverage-40pct` | conformance, repair | cd | | Tests: *"Table-driven, deterministic, no external dependencies."* | `Test`, lint, trailers | None | **Judgment.** Adds tests, a gate's subject | Log 6/5; last 07-31 PASS; overdue | **line.** Additive; no standard moves |
| `cross-platform-test-cleanup` | conformance, repair | cd | | Docs, skills, hooks, `.gitattributes`, source: *"normalize the file to LF (or add the missing `.gitattributes` rule), and rewrite the suppression"* | `--line-endings`, `--utf8-prefix`, `--type-ignores`, `skill-sync-drift`, `Test` | None | **Judgment.** `.gitattributes` is read by `--line-endings`; suppression comments are rewritten; surfaces include `.claude/hooks`, `.gzkit/skills` | Log 6/6; last 10-10 PASS; overdue | **unclear.** Reaches a validator's input and skills at rung repair |
| `decommission-tautological-tests` | conformance, repair | aw | | Tests and baseline: *"regenerate the baseline"*, then a raw `write_text` of `data/tautological_test_baseline.json` | `--tautological-test-audit`, `Waiver ratchet`, `Tautological debt`, `Test`, trailers | None | **Clear.** Rewrites tests and a registered gate baseline | Log 8/8; last 10-10 PASS; unmeasured | **out of service.** Re-authors tests and rewrites a gate baseline wholesale |
| `dependency-currency` | currency, repair | et 1 | | `pyproject.toml`, `uv.lock`, `.python-version`: *"Apply `.gzkit/skills/gz-deps-upgrade/SKILL.md` steps 3–10"* | `gz check --full`, `uv-lock`, `--astral-discipline`, lint, ty | None. A red bump is pinned, never lowered | **Clear.** Replaces the tools the gates run | Log 5/5; last 10-10 PASS; overdue. `b2010522e`, 10-27, landed under the marker with no log block | **out of service.** A gate's own tool changes |
| `doc-coverage` | conformance, repair | cd | | Docs, manifest: *"a new command also needs its entry there"* | Runner, `CLI audit`, `--cli-alignment` | None | **Judgment.** `config/doc-coverage.json` is the scanner's input; additions only | Log 4/4; last 07-31 PASS; overdue | **line.** Additive; removing a requirement is refused |
| `eval-feedback-cluster` | mining, propose | et 30 | | Proofs: *"only writes to its own proofs directory"* | None | None | None | Log 7/7; last 10-11 PASS; current | **line.** Report only |
| `evidence-integrity-audit` | conformance, propose | cd | | Proofs: *"Does not modify briefs or any files"* | None | None | None | Log 5/5; last 10-10 PASS; overdue | **line.** Report only |
| `exceptions-and-logging-rationalization` | conformance, repair | cd | | Source: *"Replace bare excepts with specific types. Add structured logging."* | `ruff E722`, lint, `Test`, trailers | None | **Judgment.** Scope `src/gzkit` holds fail-closed catches in guards | Log 5/5; last 10-10 PASS; overdue | **unclear.** A narrowed catch can change a guard's failure direction |
| `failure-class-index` | mining, propose | et 30 | | Proofs: *"Its output is a report plus run telemetry under `proofs/`."* | None | None | None | Log 1/1; last 10-10 PASS; current | **line.** Report only |
| `frontier-model-card-currency` | currency, op-only | et 30 | PL | Scan record; step 4 *"land the refresh as a direct doc fix, update the registry entry"*, and may extend `.gzkit/rules/agent-failure-modes.md` | Scan none. Step 4: `surface-fidelity-cheap`, `skill-sync-drift` | None | **Clear.** Rewrites doctrine and rule text | Log 10/10; last 10-10 PASS; current | **out of service.** Step 4 only; the scan is line |
| `frontmatter-ledger-coherence` | conformance, repair | cd | | ADR and OBPI frontmatter: *"Rewrites frontmatter and emits a receipt"* | `gate5-attestation` on a flip to Completed; `--frontmatter`; `ledger` not touched | None | **Judgment.** Writes brief status that the floor guard reads; derived from the ledger | Log 7/7; last 07-31 PASS; overdue | **unclear.** Derivable, yet the writes reach briefs, and the floor guard never lowers either way |
| `ghi-cross-reference-staleness` | coherence, propose | et 30 | PL | Proof, though Policy says *"it writes nothing"* | `--waiver-ratchet` on baseline growth | None | **Judgment.** Step 2's *Disclose* route points at `data/ghi_cross_reference_baseline.json` | Log 2/2; last 10-10 PASS; current | **line.** The ratchet refuses growth with the alarm on |
| `hardcoded-root-eradication` | conformance, repair | cd | | Source, tests, config: *"Determine if the config key already exists or must be added"* | `gz lint`, `gz check-config-paths`, `Config registry`, `Test`, trailers | Carve-out stated and fenced: `_AUDIT_SUBJECT_LITERALS` | **Judgment.** Adds config keys gates read; scope reaches guards | Log 5/5; last 07-31 PASS; overdue | **unclear.** Same shape as `config-paths-remediation`, plus new keys |
| `instructions-files-diet` | curation, op-only | aw | | Corpus, rules, skills, docs: *"Compression is therefore authored against corpus entries"*; *"Act only on items the operator ruled"* | `surface-fidelity-cheap`, `Rendition freshness`, `Invariant coherence`, `skill-sync-drift` | None | **Clear.** Canon, rules and skills; the 10-16 run moved a budget threshold | Log 13/9; hand entries to 10-16; unmeasured | **out of service.** Re-authors canon; steps 1 to 4 are line |
| `ledger-vocabulary-inertness` | coherence, propose | cd | PL | Proofs: *"this chore never edits the schema, the ledger, or any producer"* | Its script is itself an alarm hook and a `gz check` step | None. `--report --write` is described and refuses growth | None by the procedure | Log 1/0; last 09-12 FAIL (freshness); never passed; overdue | **line.** Report only |
| `memory-hygiene` | curation, op-only | cd | | Corpus, rules, skills, memory files: *"Apply the correction to that source"*, *"Remove the memory file"* | `Rendition freshness`, `Invariant coherence`, `skill-sync-drift` | None | **Clear.** Re-authors canon | Log 8/7; last 10-10 PASS; overdue | **out of service.** Step 3 only; scan and classify are line |
| `module-sloc-cap-radon` | conformance, repair | cd | | Source: *"Split modules by responsibility. Maintain backwards-compatible imports."* | `Module size`, lint, `Test`, trailers | None | **Judgment.** Measures all of `src/`, including control modules | Log 4/4; last 07-31 PASS; overdue | **unclear.** Line unless the module split is a control's. The grandfather list is empty today |
| `pep257-docstring-compliance` | conformance, repair | cd | | Docstrings: *"Add missing docstrings, fix style violations."* | `ruff D`, lint, trailers | None | None | Log 10/6; last 10-10 PASS; overdue | **line.** No behavior moves |
| `pool-triage` | curation, propose | aw | | Proof: *"The chore never writes to `docs/design/adr/pool/`, `.gzkit/ledger.jsonl`, or any governance artifact."* | None | None | None | Log 7/6; last 10-10 PASS; unmeasured | **line.** Report only |
| `pythonic-design-pattern-application` | conformance, repair | cd | | Source, tests, proofs: *"Apply the Pythonic rewrite"* | Ceiling, lint, `Test`, trailers | None. A shell-true suffix wraps report capture only, which `chores.md` permits | **Judgment.** Candidates come from a scan of all of `src` | Log 6/6; last 10-10 PASS; no `application-*` file in proofs; overdue | **unclear.** Depends on whether the candidate is control code |
| `pythonic-design-pattern-detection` | conformance, propose | cd | | Proofs: *"read-only scan, no contract change"* | None | None. A shell-true suffix on a report capture | None | Log 8/7; last 10-10 PASS; overdue | **line.** Report only |
| `pythonic-refactoring` | conformance, repair | cd | | Whole tree: `uv run gz lint --fix` then *"`uv run gz lint --ratchet` lowers `data/ruff_baseline.json`"* | `gz lint` (cannot be lowered), ty, `Test`, `Waiver ratchet`, `skill-sync-drift`, trailers | None | **Clear,** shrink of a gate baseline. **Judgment,** surfaces hold `.gzkit/skills` and `.gzkit/evidence` | Log 13/5; last 10-10 PASS; overdue | **unclear.** The ratchet shrink is line; the whole-tree fix reaches canon and evidence |
| `quality-check` | conformance, propose | cd | | Proof: *"Run the full gz quality gate set and capture deterministic evidence."* | It runs them | None. *"Never waive or suppress a gate to pass."* | None | Log 7/4; last 08-01 FAIL; pass 07-31; overdue | **line.** Reads the gates |
| `repository-structure-normalization` | conformance, repair | cd | | Moves: *"Fix structural issues (missing directories, misplaced files)."* | `--documents --surfaces`, `skill-sync-drift`, `Test` | None | **Judgment.** Its surfaces list `.claude/settings.json`, `.claude/hooks`, `.gzkit/rules`, the corpus's renditions | Log 5/5; last 10-10 PASS; overdue | **unclear.** A move of a misplaced hook or rule moves a control |
| `session-correction-mining` | mining, propose | et 30 | | Proofs: *"Read-only everywhere except this chore's `proofs/` directory"* | None | None | None | Log 4/4; last 10-10 PASS; current | **line.** Report only |
| `skill-authoring-quality` | conformance, propose | cd | | Proofs: *"skills are edited only by the operator"* | None | None | None | Log 4/4; last 07-31 PASS; overdue | **line.** Report only |
| `skill-command-doc-parity` | conformance, op-only | cd | | Docs in step 4; step 5 *"aligning the skill's SKILL.md with its command doc in `.gzkit/skills/`"* | `CLI audit`, `--cli-alignment`, `skill-sync-drift`, `Test` | None | **Clear.** Step 5 re-authors a skill | Log 5/5; last 07-31 PASS; overdue | **out of service.** Step 5 only; step 4 is line |
| `skill-trigger-testing` | conformance, propose | cd | | Proofs: *"This chore does NOT modify skills"* | None | None | None | Log 6/6; last 10-10 PASS; overdue | **line.** Report only |
| `test-consolidation-subtest-sweep` | conformance, repair | cd | PL | Tests: *"Surgical consolidation edits within § Scope."* | `Test`, lint, trailers | None | **Judgment.** Rewrites tests; scope 2 *"Wire `scripts/profile_unittest_modules.py`"* and decide a separate segment | Log 2/2; last 10-10 PASS; overdue | **unclear.** Scopes 1 and 3 keep the tests' claims; scope 2 can change what a gate runs |
| `test-isolation-compliance` | conformance, repair | cd | | Tests: *"Apply the lightest fix that addresses the root cause."* | Profiler, `gz smoke`, `Test`, trailers | Near-route: *"Thresholds are hardcoded in the profiler; adjust as suite grows"* | **Judgment.** Policy licenses a threshold move the registry's `nonAuthority` refuses | Log 9/5; last 10-10 FAIL (profiler); pass 08-01; overdue | **unclear.** Text and declaration disagree |
| `test-manpage-examples` | conformance, repair | cd | | Docs: *"Replace each example whose output no longer matches with output captured from a real run."* | `CLI audit`, `Test` | None | None | Log 4/4; last 07-31 PASS; overdue | **line.** Docs follow the code |

## Counts

| Verdict | Count | operator-only-repair | repair | propose |
|---|---|---:|---:|---:|
| line | 21 | 0 | 4 | 17 |
| unclear | 13 | 1 | 12 | 0 |
| out of service | 7 | 5 | 2 | 0 |
| **Total** | **41** | **6** | **18** | **17** |

## Population findings

1. **No procedure addresses the condition.** A search of all 41 `CHORE.md` for the marker's vocabulary hits five files. Three are other meanings of *marker*. `frontier-model-card-currency` names a future drydock kit. `ledger-vocabulary-inertness` names the hangar as background. `gz-chore-runner` and `.gzkit/chores/README.md` hit only on suppression markers. So no chore says to enter or avoid the hangar, and none tells the agent to bypass an alarm. That search is a search, but it is backed by the full reads above. Read literally, the test therefore puts every chore on the line by default, because nothing states a need to lower an alarm.
2. **No recorded chore run happened out of service.** All 253 timestamped log blocks across the 41 chores fall outside every `mx_session_opened` to `mx_session_closed` span. No file under any `proofs/` directory has been committed since the drydock opened on 2026-10-17T08:36Z. The chore program stopped when the drydock began.
3. **The chores that did run wrote controls with the marker closed.** See § Writes made with the marker closed.
4. **Going out of service removes the ratchets some of these writes rely on.** `Waiver ratchet` emits ERROR, so it demotes, and the push hook that runs it is off at the drydock level. It is what refuses growth in `data/tautological_test_baseline.json` and `data/ruff_baseline.json`. *Inference:* the hangar lowers the guard on the write it would be sheltering. `gz lint`, the ceiling and the two Gate-5 guards do not lower at all, so the hangar gives those chores nothing.
5. **Five written statements do not match the mechanism.**
   - `docs/governance/GovZero/command-doctrine.md` says *"Each run of a chore is a ledger event (ruled 2026-10-07)"*. `src/gzkit/commands/chores.py` and `chores_exec.py` write no ledger event, and the ledger holds no chore-run event type.
   - `decommission-tautological-tests` § Overview says it *"emits `chore_decommission_processed` ledger events per processed item"*. LSP finds the event builder referenced only by a test. The ledger's five such events end 2026-05-27, and no Workflow step emits one, while `42edb2a56` retired seven ops on 2026-10-10.
   - `dependency-currency` declares a 1-day period, and its last run block is 2026-10-10.
   - `dependency-currency` says it edits three files, but its inventory covers hook and action pins, and the pre-commit file says the uv hook rev moves *"in each `gz-deps-upgrade` pass (step 1)"* while the chore applies steps 3 to 10.
   - `data/waiver_ratchet_registry.json` lists `data/module_size_grandfather.json` at `baseline_count` 5, and that file's list is empty.
6. **The verdict follows the rung, and the rung does not separate the 18.** All 17 propose chores are line, and 5 of 6 operator-only-repair chores are out of service. Of the 18 repair chores, 4 are line, 12 unclear and 2 out of service. `chore-class-system.md` says *"A repair that touches operator-authored canon — a skill, a rule, the corpus, model-sourced doctrine, a permission grant — is declared `operator-only-repair`"*, which covers canon and not baselines, tests, tools or `src/gzkit` control code.

## Writes made with the marker closed

Open MX spans on the ledger: `d3c16ae0`, 2026-08-21 to 08-22, *"repair ledger ts-order deadlock on OBPI-0.35.0-09 completion"*, no chore. Then `696ca9a4`, `e6800367` and `57346836`, from 2026-10-17T08:36Z, the last still open. Everything below predates 10-17 unless noted. Operator rulings stand behind several of these, so *in flight* here says where the write happened and nothing about authorization.

| Commit | Date (UTC offset as committed) | What changed | Link to a chore |
|---|---|---|---|
| `e0dab8ee4` | 2026-10-16T01:06-05:00 | `data/instructions_files_budget.json`, `AGENTS.md` 20000 to 25000 | Stated: `instructions-files-diet` log, *"§ 4 ruling received; § 5 edit made"*, ruling *'A, record the budget at the invariant floor'* |
| `64f35c53e`, `f4d7ef495` | 2026-10-10 | `.gzkit/corpus/AGENTS.md.jsonl`, renditions, `AGENTS.md` | *Inference:* same-day visits A and E; the commits are `gz git-sync` rollups and name no chore |
| `42edb2a56` | 2026-10-10T05:04-05:00 | `data/tautological_test_baseline.json`, three test files, `src/gzkit/eval/datasets.py` | Stated: *"retire seven ops at maintenance visit B"* |
| `2fcf78eef` | 2026-10-10T06:14-05:00 | `data/ghi_cross_reference_baseline.json` entries removed, `data/waiver_ratchet_registry.json` | *Inference:* a shrink in the same visit; `ghi-cross-reference-staleness` is rung propose |
| `d7dc3c4c6` | 2026-10-10T20:21-05:00 | `.gzkit/rules/model-selection.md` and mirrors | Stated: `rule-version-history.md`, *"maintenance visit E, rule-conflict audit"* |
| `04fda99d3` | 2026-10-11T01:40-05:00 | Ten skills and mirrors | *Inference:* subject matches the skill chores; no chore named |
| `6396fb3cc` | 2026-10-05 | Python pin, `uv.lock` | *Inference:* the dependency procedure; then rung propose |

Under the marker: `b2010522e` (2026-10-27) brought dependencies current as `dependency-currency` became a repair chore. `competitor-radar-currency` scanned on 2026-10-26. Neither left a run block.

## Chores judged out of service or unclear

### Out of service

**`instructions-files-diet`.** § 5: *"Move Judgment-class narrative paragraphs"*; § 5a: *"Compression is therefore authored against corpus entries, not prose"*; § 5d: *"Bump `metadata.skill-version` and `last_reviewed` together"*. Its acceptance runs `--invariant-coherence`, and `run_rendition_freshness_audit` *"Fails closed (exit 3) when the corpus has mutated after the committed rendition"*, while manual check 11 requires that *"`gz content commit` has NOT been run by the chore"*. *Inference:* a retired or added entry leaves that gate red until the operator promotes, which is the one place an armed alarm stops the procedure mid-way. The log entry for 2026-10-16 is the strongest single instance of a threshold moved in flight.

**`dependency-currency`.** *"Apply `.gzkit/skills/gz-deps-upgrade/SKILL.md` steps 3–10"*. The skill: *"Bump pinned (`==`) deps in `pyproject.toml` to current PyPI latest"*, *"`uv python pin <newest patch>`; that one line moves every consumer."* Ruff, ty and unittest-parallel are `pyproject.toml` dev dependencies, so a pass replaces what the alarms execute, and the gate that judges the pass runs on the new tools. The rung moved to repair on 2026-10-27, and the period is one day.

**`decommission-tautological-tests`.** Step 2: *"rewrite the operation as a behavior test"*; step 4: *"After each sweep wave, regenerate the baseline"*, by an inline `Path('data/tautological_test_baseline.json').write_text(...)` with no direction check. The registry says *"Never re-baselines upward"*, and only `Waiver ratchet` holds that. `42edb2a56` shows the sweep also reaching `src/`.

**`control-surface-permission-consent-drift`.** Step 6: *"Only in a run the operator started: apply `proofs/settings-patch.md` to its source files"*. The patch proposes new `permissions.deny` rules and reads *"DRAFT, not applied"*. So the verdict is on the step, and that step has not run. The generator emits no `permissions` key and the sync merge preserves user keys; `detect_claude_settings_drift`, which would report an extra key, has no source caller beyond its re-export.

**`frontier-model-card-currency`.** Step 4: *"land the refresh as a direct doc fix, update the registry entry"*, *"New failure-mode patterns extend `.gzkit/rules/agent-failure-modes.md`"*. Step 3b holds model assignments out of the run: *"never change one inside the run"*.

**`memory-hygiene`.** Step 3: *"Apply the correction to that source — never to a rendered surface"*, routed to the corpus, `.gzkit/rules/` or `.gzkit/skills/`, then *"Remove the memory file"*, which is machine-local and unrecoverable from git.

**`skill-command-doc-parity`.** Step 5: *"resolve **Drift** and **Overlap** findings by aligning the skill's SKILL.md with its command doc in `.gzkit/skills/`"*. Step 4 is documentation and is line by itself.

### Unclear

**`complexity-reduction-xenon`.** Step 3: *"Pre-attest functions whose complexity is irreducibly algorithmic via the `@intrinsic_complexity` decorator (ADR-0.0.29 OBPI-07) rather than refactoring them artificially"*. `complexity_advise.py`: *"A function attested by a literal `@intrinsic_complexity` in source or by an `intrinsic-complexity-attestation` ledger event is short-circuited before the engine call"*. The ledger path refuses headless use; `--attest-intrinsic` *"requires an interactive TTY"*. *Inference:* a literal decorator with its `attestor` field does not pass through that path, so the step routes an agent to an exemption from the advisor, while `chores.md` holds that *"A chore never discharges a finding by suppression."* I found no use of it in the ceiling gate's measuring module, so it was not seen to exempt the ceiling itself.

**`exceptions-and-logging-rationalization`.** *"Replace bare excepts with specific types."* with scope `src/gzkit`. `guards.py` line 578: `except Exception:  # noqa: BLE001 - an unreadable checkpoint must never demote a guard`, and `_guard_grounds` documents *"Fails CLOSED."* The chore carves out the CLI boundary and not fail-closed guards, though its registry entry refuses to widen a catch and to change behavior.

**`config-paths-remediation`, `hardcoded-root-eradication`.** Both scope `src/gzkit`, `.gzkit.json` and the manifest. `hardcoded-root-eradication` step 2: *"Determine if the config key already exists or must be added"*. `Config registry` gates that surface against three shrink-ratchet files. No step fences `src/gzkit/hooks` or `src/gzkit/mx`.

**`module-sloc-cap-radon`.** Step 3: *"Split modules by responsibility."* `_measure` walks all of `src/`. No module is over the band today, so the question waits for one.

**`pythonic-design-pattern-application`.** Step 4: *"Apply the Pythonic rewrite"*. Detection runs `--root src`. No `application-*` evidence file exists, so no rewrite has been recorded under the chore.

**`pythonic-refactoring`.** Workflow: *"`uv run gz lint --fix` applies Ruff's safe fixes; then `uv run gz lint --ratchet` lowers `data/ruff_baseline.json`"*. `lint_against_baseline` falls back to `["."]` when given no paths. `.pre-commit-config.yaml` records why the fixing hook left: *"a fixing hook rewrote every held finding in any file a commit touched, dated evidence included (operator, 2026-10-24: 'do 1')"*. The chore's quick-fix command takes no path, and its surfaces list `.gzkit/skills` and `.gzkit/evidence`. `pyproject.toml` excepts a named rule list for evidence scripts, not all rules; whether a safe fix would fire on one was not run. A rung-repair chore touching `.gzkit/skills` also meets the canon sentence quoted in finding 6.

**`cross-platform-test-cleanup`.** Step 2: *"normalize the file to LF (or add the missing `.gitattributes` rule), and rewrite the suppression in a form `ty` honors"*. `.gitattributes` is what `--line-endings` reads, and the surfaces include `.claude/hooks` and `.gzkit/skills`.

**`cli-contract-governance`.** Step 5: *"land each breaking change the report names"*, with *"Exit code changes"* named as breaking. `AGENTS.md` § Defect-fix routing: *"Work that crosses briefs, changes a CLI, schema or runtime contract, or is new feature work is OBPI work, which the operator initiates."* The chore's step is operator-initiated too, so the two routes disagree on the ceremony, and neither text mentions the condition.

**`frontmatter-ledger-coherence`.** Step 2: *"Rewrites frontmatter and emits a receipt"*. `gz frontmatter reconcile` is a Bash call, so no Write or Edit hook sees it. `forbid_unattested_obpi_completion_commits` reads the staged brief at commit and never demotes. `AGENTS.md` § OBPI Acceptance Protocol lists edits to briefs among acts only the operator initiates, and the chore's rung is repair. `reconcile_frontmatter` carries a refusal path for invalid transitions; only its matching lines were read. Its last pass was 2026-07-31.

**`repository-structure-normalization`.** *"Fix structural issues (missing directories, misplaced files)."* Its 24 declared surfaces include `.claude/settings.json`, `.claude/hooks`, `.gzkit/rules`, `.gzkit/renditions` and `.codex/hooks.json`. The registry says *"never edits a validator to accept a deviation"*, which fences content and not location.

**`test-consolidation-subtest-sweep`.** Scope 2: *"Wire `scripts/profile_unittest_modules.py` so the slow tail is ranked and visible, then decide whether the tail belongs in a separate segment."* A separate segment would change what `Test` runs. The registry refuses `CANONICAL_STEP_COMMANDS` changes and not a change of membership. The file's own § Measured baseline still states scope 2 is open.

**`test-isolation-compliance`.** § Policy: *"Thresholds are hardcoded in the profiler; adjust as suite grows"*. Registry `nonAuthority`: *"Never masks a slow test with sleep or clock hacks, or loosens a profiler threshold to pass."* `tests/tools/test_health_profiler.py` also carries `KNOWN_E2E_TESTS`, an allowlist in the gate's own file: *"NOT a threshold relaxation"*. The last run failed that profiler.
