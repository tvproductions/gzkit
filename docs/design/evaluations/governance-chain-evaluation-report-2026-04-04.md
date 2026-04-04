# Governance Chain Evaluation Report

**Date:** 2026-04-04
**Evaluator:** Claude Opus 4.6 (dogfood run of framework v1.0)
**Repository state:** `555d7ec` on `main`
**Framework:** `docs/design/evaluations/governance-chain-evaluation.md` v1.0

---

## 1. Executive Summary

- **Chain score:** 1.71 (weakest link: Link 1, Authoring)
- **Findings by severity:** 2 High, 4 Medium, 4 Low
- **Coverage gaps:** 3 findings have no pool ADR coverage (S2, S5, S10)
- **Top 3 recommendations:**
  1. Add content-type awareness to `pipeline-gate.py` (S2 -- High, no pool coverage)
  2. Harden the authoring→lifecycle handoff with a hook that blocks Proposed status without evaluation scorecard (S1 -- High, pool coverage exists)
  3. Make product proof gate unconditional by removing the feature flag or defaulting to enforced (S5 -- Medium, no pool coverage)

**Headline finding:** The OBPI pipeline (Link 2) is materially stronger than the other three links. Its three hard-blocking hooks create real enforcement. The authoring link (Link 1) is the weakest -- entirely T2/T3 with no hard gates between draft quality and implementation entry.

---

## 2. Baseline State

| Category | Count |
|----------|-------|
| Foundation ADRs | 15 (10 Validated, 5 Pending) |
| Feature ADRs | 40 (24 Validated, 1 In Progress, 15 Pending) |
| Pool ADRs | 46 (all Pending/UNSCOPED) |
| **Total ADRs** | **101** |
| Completed OBPIs | 299 (across validated ADRs) |
| Pending OBPIs | ~237 (absorption wave 0.25.0-0.39.0) + 15 (foundation 0.0.13-0.0.15) |
| Validation status | `gz validate --documents --surfaces`: all passed |

---

## 3. Scorecard

### 3a. Scoring Matrix

| Dimension | Link 1: Authoring | Link 2: Pipeline | Link 3: Verification | Link 4: Closeout |
|-----------|:-:|:-:|:-:|:-:|
| **D1: Gate coverage** | 1 | 3 | 2 | 2 |
| **D2: Handoff integrity** | 1 | 3 | 2 | 2 |
| **D3: Scope enforcement** | 1 | 2 | 2 | 2 |
| **D4: Evidence fidelity** | 2 | 3 | 2 | 2 |
| **D5: Escape hatch governance** | 2 | 2 | 2 | 2 |
| **D6: Lifecycle coherence** | 2 | 3 | 3 | 3 |
| **D7: Observability** | 3 | 3 | 3 | 3 |
| **Mean** | **1.71** | **2.71** | **2.29** | **2.29** |

**Chain score (weakest link): 1.71**

### 3b. Per-Link Narratives

**Link 1: Authoring (1.71)** -- The interview→create→evaluate→specify sequence is well-designed and produces high-quality output *when followed faithfully*. The problem is that no T1 mechanism enforces this faithfulness. The evaluation skill produces GO/NO-GO verdicts but nothing blocks lifecycle progression on NO-GO. The interview is mandatory in skill prose but no hook checks for the interview JSON artifact. Observability is strong (scorecards, registry updates, ledger events).

**Link 2: Pipeline (2.71)** -- The strongest link by a significant margin. Three hard-blocking hooks (`plan-audit-gate`, `pipeline-gate`, `obpi-completion-validator`) create genuine enforcement barriers. The content-type blind spot (S2) and the unenforced Allowed Paths (S3) prevent a perfect score. The run-to-completion gap (S9) is real but low-probability given the hooks that *do* fire at Stage 5.

**Link 3: Verification (2.29)** -- The layered trust model (reconcile = L1 evidence, audit = L2 proof consumption) is architecturally sound. The `gz audit` CLI hard-blocks without prior attestation. Weaknesses: reconcile auto-promotes briefs on heuristic evidence (S4), and the 7-day staleness threshold is advisory. The @covers grep-based evidence detection is the single biggest fidelity concern.

**Link 4: Closeout (2.29)** -- The ceremony design is philosophically strong (passive presenter, human judges). `gz closeout` re-runs all quality gates in real-time with no `--force` override, which is excellent. The product proof gate being feature-flagged (S5) and the self-close batch burden (S7) prevent a higher score. Lifecycle coherence is strong: `gz closeout` is the only path to version bump.

---

## 4. Systemic Findings

### S1: No Hard Gate Between Authoring Quality and Lifecycle Progression

- **Severity:** High
- **Chain links:** 1→2
- **Current tier:** T2 | **Target tier:** T1
- **Evidence:** `gz-adr-evaluate` SKILL.md mandates GO/NO-GO verdict. No hook in `.claude/settings.json` blocks ADR state change on NO-GO. No hook checks for `EVALUATION_SCORECARD.md` existence before `gz-obpi-pipeline` starts.
- **Pool coverage:** `agent-reliability-framework` (DIRECT -- AR levels formalize graduated quality), `skill-behavioral-hardening` (PARTIAL)
- **Absorption coverage:** ADR-0.34.0-07 plan-audit-gate (ADDRESS), ADR-0.25.0-12 admission-pattern (ADDRESS), ADR-0.26.0-04 adr-governance (ADDRESS)
- **Gap flag:** FALSE

### S2: Content-Type Blind Spot in Pipeline Enforcement

- **Severity:** High
- **Chain links:** 2
- **Current tier:** Gap | **Target tier:** T1
- **Evidence:** `pipeline-gate.py` line 58: `if rel_path is None or not rel_path.startswith(("src/", "tests/")): sys.exit(0)`. Doc-only edits exit the hook without any pipeline check. A doc-only OBPI has zero T1 enforcement.
- **Pool coverage:** None
- **Absorption coverage:** ADR-0.34.0-11 dataset-guard (ADDRESS), ADR-0.35.0-09/17 markdown hooks (ADDRESS)
- **Gap flag:** TRUE

### S3: Allowed Paths Constraint Is Decoration

- **Severity:** Medium
- **Chain links:** 2, 3
- **Current tier:** Gap (edit-time) / T2 (completion-time) | **Target tier:** T1
- **Evidence:** No hook reads the brief's Allowed Paths. `pipeline-gate.py` checks pipeline activation, not path scope. `hooks/obpi.py:build_scope_audit()` records `out_of_scope_files` at completion time but does not block. `plan_audit_cmd.py:_extract_allowed_paths()` checks plan alignment but not runtime edits.
- **Pool coverage:** `agent-reliability-framework` (DIRECT)
- **Absorption coverage:** ADR-0.25.0-12 admission-pattern (ADDRESS), ADR-0.35.0-07 (ADDRESS), ADR-0.39.0-04/05 (ADDRESS)
- **Gap flag:** FALSE

### S4: Reconcile Auto-Promotion on Heuristic Evidence

- **Severity:** Medium
- **Chain links:** 3
- **Current tier:** T2 | **Target tier:** T1
- **Evidence:** `gz-obpi-reconcile` Phase 2 auto-marks briefs Completed based on grep-based `@covers` detection and test results. No human confirmation. False-positive in tag detection → incorrect promotion → audit trusts the ledger.
- **Pool coverage:** `agent-reliability-framework` (PARTIAL)
- **Absorption coverage:** ADR-0.27.0 OBPIs 03/05/11/12 ARB receipts (ADDRESS), ADR-0.26.0-07/08 traceability/validation-receipt (ADDRESS)
- **Gap flag:** FALSE

### S5: Product Proof Gate Is Feature-Flagged

- **Severity:** Medium
- **Chain links:** 4
- **Current tier:** T1 (conditional) | **Target tier:** T1 (unconditional)
- **Evidence:** `closeout.py` calls `get_decisions().product_proof_enforced()`. When the flag is off, `check_product_proof()` findings are advisory warnings, not blockers.
- **Pool coverage:** None
- **Absorption coverage:** ADR-0.35.0-13/14/15 pre-commit hooks (ADDRESS), ADR-0.31.0-08/10 (ADDRESS)
- **Gap flag:** TRUE

### S6: --force Attestation Has No Quality Bar

- **Severity:** Low (revised from Medium after red-team probe)
- **Chain links:** 4
- **Current tier:** T3 | **Target tier:** T2
- **Evidence:** `attest.py` accepts any non-empty `--reason` string with `--force`. No format, length, or content validation. **However:** `gz closeout` is independent -- it re-runs all gates in real-time, has no `--force` flag, and does not consume prior attestation state. A forced attestation does NOT shortcut closeout. The forced attestation is a standalone ledger record. Severity lowered because the bypass path to release (closeout→version-bump) is not reachable via `--force` alone.
- **Pool coverage:** `agent-reliability-framework` (DIRECT), `attestation-advisory-agent` (PARTIAL)
- **Absorption coverage:** ADR-0.25.0-01, ADR-0.26.0-04, ADR-0.32.0-11/13 (all ADDRESS)
- **Gap flag:** FALSE

### S7: Self-Close Exception Defers Review

- **Severity:** Medium
- **Chain links:** 2→4
- **Current tier:** T2→T3 | **Target tier:** T2 with proportional review
- **Evidence:** `gz-obpi-pipeline` Stage 4 exception mode writes evidence template and marks brief Completed without human gate. The `obpi-completion-validator` hook still fires (checks Implementation Summary, Key Proof, ledger evidence) so there IS a T1 check -- but not a human-review check. Deferred verification accumulates until closeout.
- **Pool coverage:** `graduated-oversight-model` (DIRECT -- Standard tier adds spot-check sampling)
- **Absorption coverage:** ADR-0.34.0-01 (ADDRESS), ADR-0.32.0-11 (ADDRESS)
- **Gap flag:** FALSE

### S8: Lane Classification Is Write-Once

- **Severity:** Low
- **Chain links:** 1→all
- **Current tier:** T3 | **Target tier:** T2
- **Evidence:** Lane is read from ledger `adr_created` events. No mechanism re-evaluates lane as scope evolves. A lite ADR that adds a CLI subcommand stays lite.
- **Pool coverage:** `heavy-lane` (PARTIAL)
- **Absorption coverage:** ADR-0.26.0-04 (ADDRESS), ADR-0.25.0-08 (COMPLICATE)
- **Gap flag:** FALSE (weakly covered)

### S9: Run-to-Completion Is Narrative-Only

- **Severity:** Low
- **Chain links:** 2
- **Current tier:** T2 | **Target tier:** T1
- **Evidence:** No hook prevents stopping after Stage 2. However, the `obpi-completion-validator` hook blocks marking the brief Completed without evidence, and `pipeline-completion-reminder` warns before commit. The practical risk is medium: an abandoned pipeline leaves markers that the session-staleness-check will flag.
- **Pool coverage:** `skill-behavioral-hardening` (DIRECT), `agent-reliability-framework` (DIRECT), `structured-blocker-envelopes` (PARTIAL)
- **Absorption coverage:** ADR-0.34.0-06/08 (ADDRESS)
- **Gap flag:** FALSE

### S10: Interview Artifact Persistence Unchecked

- **Severity:** Low
- **Chain links:** 1
- **Current tier:** T3 | **Target tier:** T2
- **Evidence:** `gz-adr-create` Step 0 mandates `gz interview adr --from <file>.json`. No hook checks the JSON file exists in the ADR directory after creation. The artifact could be lost.
- **Pool coverage:** None (`pre-planning-interview` pool ADR exists but addresses interview process, not artifact persistence)
- **Absorption coverage:** None
- **Gap flag:** TRUE

---

## 5. Architectural Intent Map

### 5a. Pool ADR Coverage Matrix

| Finding | agent-reliability-framework | skill-behavioral-hardening | graduated-oversight-model | attestation-advisory-agent | heavy-lane | structured-blocker-envelopes | Others |
|---------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| S1 | DIRECT | PARTIAL | -- | -- | -- | -- | constraint-library: TANGENTIAL |
| S2 | -- | -- | -- | -- | -- | -- | **NONE** |
| S3 | DIRECT | -- | -- | -- | -- | -- | constitution-invariants: TANGENTIAL |
| S4 | PARTIAL | -- | -- | -- | -- | -- | adr-amendment-tracking: TANGENTIAL |
| S5 | -- | -- | -- | -- | -- | -- | **NONE** |
| S6 | DIRECT | -- | PARTIAL | PARTIAL | -- | -- | -- |
| S7 | -- | -- | DIRECT | -- | -- | -- | channel-agnostic-human-triggers: TANGENTIAL |
| S8 | -- | -- | -- | -- | PARTIAL | -- | -- |
| S9 | DIRECT | DIRECT | -- | -- | -- | PARTIAL | -- |
| S10 | -- | -- | -- | -- | -- | -- | **NONE** |

**Gaps (no DIRECT pool coverage):** S2, S4, S5, S10

### 5b. Absorption Wave Intersection (Key ADRs)

| Absorption ADR | Findings it ADDRESSes | Findings it COMPLICATEs |
|---------------|----------------------|------------------------|
| **ADR-0.34.0** (claude-hooks) | S1, S2, S4, S7, S9 (via OBPIs 01/06/07/08/11) | S2 (OBPI-05 reinforces Python-only pattern) |
| **ADR-0.35.0** (pre-commit hooks) | S2, S3, S5 (via OBPIs 07/09/13/14/15/17) | -- |
| **ADR-0.27.0** (ARB receipts) | S4 (via OBPIs 03/05/11/12) | -- |
| **ADR-0.26.0** (governance lib) | S1, S3, S4, S6, S8 (via OBPIs 04/06/07/08) | S4 (OBPI-03 may entrench grep patterns) |
| **ADR-0.25.0** (core infra) | S1, S3, S6 (via OBPIs 01/12) | S8 (OBPI-08 may entrench write-once) |
| ADR-0.32.0 (CLI comparison) | S6, S7, S9 (via OBPIs 09/11/13) | -- |
| ADR-0.31.0 (new CLI) | S5 (via OBPIs 08/10) | -- |
| ADR-0.39.0 (instruction plugins) | S2, S3 (via OBPIs 04/05) | -- |

**Highest-value absorption ADR:** ADR-0.34.0 (claude-hooks-absorption) addresses 5 of 10 findings and is the single most consequential ADR for governance chain enforcement.

### 5c. Coverage Gaps

| Finding | Gap Status | Recommended Action |
|---------|-----------|-------------------|
| **S2** (content-type blind spot) | No pool ADR | Option A: Expand `pipeline-gate.py` path filter now (hook change, no ADR needed). Option B: Create pool ADR `content-type-aware-pipeline-enforcement` for a principled design. **Recommend A** -- this is a 2-line hook change. |
| **S5** (product proof feature-flagged) | No pool ADR | Remove the feature flag or default to enforced. This is a config change in `FeatureDecisions`, not an architectural concern. No ADR needed. |
| **S10** (interview artifact persistence) | No pool ADR | Add a check in `gz validate --documents` that ADR directories with briefs also contain an interview JSON. Low priority. |

---

## 6. Red-Team Results

| # | Challenge | Finding | Result | Detail |
|---|-----------|---------|--------|--------|
| RT-1 | Edit `docs/user/runbook.md` without active pipeline | S2 | **PASSED** | `pipeline-gate.py` line 58 exits 0 for non-`src/`/`tests/` paths. No hook fired. |
| RT-2 | Check if `--force` on `gz attest` creates bypass to `gz closeout` | S6 | **BLOCKED** | `gz closeout` is independent: re-runs all gates in real-time, has no `--force`, does not consume prior attestation. Forced attestation is a dead-end ledger entry. |
| RT-3 | Edit file outside OBPI's Allowed Paths during active pipeline | S3 | **PASSED** | No hook reads the brief's Allowed Paths. `pipeline-gate.py` checks pipeline activation only. `build_scope_audit()` records violations post-hoc but does not block. |
| RT-4 | Check if `gz-adr-evaluate` NO-GO blocks progression | S1 | **PASSED** | No hook checks for evaluation scorecard existence or verdict. An ADR with NO-GO can proceed to `gz-obpi-pipeline` without obstacle. |
| RT-5 | Check plan-audit gate enforcement | S1 (partial) | **BLOCKED** | `plan-audit-gate.py` hook hard-blocks ExitPlanMode without valid receipt. This is T1 enforcement for the plan→pipeline handoff specifically. |
| RT-6 | Check obpi-completion-validator for self-close | S7 | **WARNED** | Hook fires on brief status change, checks Implementation Summary and Key Proof. Self-close evidence template satisfies structural checks. Human attestation NOT required for lite lane. |

### Red-Team Outcomes Summary

| Result | Count | Findings |
|--------|-------|----------|
| BLOCKED | 2 | S6 (force-attest→closeout), S1 (plan-audit gate) |
| WARNED | 1 | S7 (self-close structural check passes) |
| PASSED | 3 | S2 (doc-only bypass), S3 (allowed paths unenforced), S1 (no eval scorecard gate) |

---

## 7. Actionable Outcomes

### 7a. Category A -- Immediate Infrastructure Hardening

No ADR required. Implement before the next ADR/OBPI cycle.

| # | Recommendation | Finding(s) | Scope | Severity |
|---|---------------|-----------|-------|----------|
| R1 | Expand `pipeline-gate.py` path filter to include `docs/`, `config/`, `.gzkit/` when an OBPI pipeline is active. Simplest approach: drop the `src/`/`tests/` filter entirely and gate ALL writes during active pipeline. | S2 | 1 hook file | High |
| R2 | Add evaluation scorecard gate: enhance `plan-audit-gate.py` to check for `EVALUATION_SCORECARD.md` with a non-NO-GO verdict before issuing a plan-audit receipt. Chains authoring quality into the pipeline entry gate. | S1 | 1 hook file + possible skill update | High |
| R3 | Make product proof gate unconditional: remove the `product_proof_enforced()` feature flag check in `closeout.py` or default the flag to `True`. The infrastructure exists; the flag just allows bypassing it. | S5 | 1 code file | Medium |
| R7 | Add interview artifact check to `gz validate --documents`: verify ADR directories with OBPIs also contain an interview JSON artifact. | S10 | 1 CLI file | Low |

### 7b. Category B -- ADR Sequencing Guidance

The analysis shows governance-chain ADDRESS density varies significantly across the absorption wave. Recommended priority reordering for maximum chain hardening per ADR:

| Priority | ADR | ADDRESS density | Rationale |
|----------|-----|----------------|-----------|
| 1 | **ADR-0.34.0** (claude-hooks) | 5 findings (S1, S2, S4, S7, S9) | Highest intersection. Pipeline-gate, completion-validator, and pipeline-router OBPIs directly harden the three weakest enforcement points. All subsequent ADRs benefit. |
| 2 | **ADR-0.35.0** (pre-commit hooks) | 3 findings (S2, S3, S5) | Commit-blocking hooks for markdown validation, manpage validation, and docstring coverage convert feature-flagged checks into hard gates. |
| 3 | **ADR-0.27.0** (ARB receipts) | 1 finding (S4), but deep | Schema-validated receipts replace grep-based @covers heuristics. Fundamental evidence fidelity upgrade. |
| 4 | **ADR-0.26.0** (governance lib) | 5 findings (S1, S3, S4, S6, S8) | Broad coverage but COMPLICATE risk on S4 (may entrench grep patterns if absorbed uncritically). Should follow ARB receipt work. |
| 5+ | Remaining absorption ADRs | 0-2 findings each | Lower chain impact. Sequence by other priorities (feature need, dependency order). |

**Current plan comparison:** No explicit absorption ordering exists yet. This recommendation establishes governance-chain impact as the primary sequencing criterion for the first 4 ADRs.

**COMPLICATE warnings:** ADR-0.26.0-03 (adr-recon) risks entrenching grep-based evidence if absorbed before ADR-0.27.0 establishes receipt schemas. ADR-0.25.0-08 (ledger-pattern) may further entrench write-once lane classification. ADR-0.30.0-02 (config-doctrine) may normalize the pattern of feature-flagging governance gates.

### 7c. Category C -- New Architectural Intent

| Finding | Gap Status | Recommended Action | Detail |
|---------|-----------|-------------------|--------|
| **S2** (content-type blind spot) | No pool ADR | **Accept risk after Category A fix** | R1 (Category A) addresses the immediate enforcement gap with a hook change. The broader architectural question of content-type-aware governance can be absorbed into ADR-0.34.0 scope when it executes. No new pool entry needed. |
| **S5** (product proof feature-flagged) | No pool ADR | **Accept risk after Category A fix** | R3 (Category A) removes the flag. If a principled feature-flag governance policy is desired, expand `ADR-pool.heavy-lane` scope to include "which gates may be feature-flagged." |
| **S10** (interview artifact persistence) | No pool ADR | **Accept risk** | Low severity. R7 (Category A) adds a validation check. Full lifecycle governance for interview artifacts can be scoped into `ADR-pool.pre-planning-interview` if that pool item is ever promoted. |

## 8. Next Actions

### Category A: Approved for immediate implementation

- [ ] **R1** -- Expand pipeline-gate path filter (S2, High)
- [ ] **R2** -- Add evaluation scorecard gate (S1, High)
- [ ] **R3** -- Make product proof gate unconditional (S5, Medium)
- [ ] **R7** -- Add interview artifact check to gz validate (S10, Low)

*Decision required: Operator approves or defers each item.*

### Category B: Sequencing decisions

- [ ] Accept recommended absorption priority order (0.34.0 → 0.35.0 → 0.27.0 → 0.26.0 → rest)?
- [ ] Note COMPLICATE warnings for ADR-0.26.0-03 and ADR-0.25.0-08 -- sequence ADR-0.27.0 before ADR-0.26.0 to avoid entrenching grep patterns?

*Decision required: Operator accepts, modifies, or defers the reordering.*

### Category C: Gap decisions

- [ ] S2 gap: Accept risk after R1 implementation? Or create pool entry?
- [ ] S5 gap: Accept risk after R3 implementation? Or expand heavy-lane scope?
- [ ] S10 gap: Accept risk? Or expand pre-planning-interview scope?

*Decision required: Operator decides per finding.*

### Next evaluation

Recommend re-evaluation after Category A items are implemented and the first absorption-wave ADR (0.34.0) is completed. This will show whether the chain score improved and whether the COMPLICATE risks materialized.

---

## Appendix: Evaluation Method Notes

This report was produced by dogfooding the framework defined in `governance-chain-evaluation.md`. The evaluator followed Steps 1-8 sequentially:

- **Step 1** used `gz status --table`, `gz validate --documents --surfaces`, and `git rev-parse HEAD`
- **Step 2** was performed by parallel research agents reading all hook scripts, CLI sources, skill files, AGENTS.md, and rule files
- **Step 3** scoring was based on the T1/T2/T3 classification from Step 2, with specific file/line citations
- **Step 4** findings were identified from the gap between stated policy and actual enforcement mechanisms
- **Step 5** mapping used parallel agents reading all pool ADR files and absorption-wave OBPI briefs
- **Step 6** red-team challenges were non-destructive probes: reading hook source to trace execution paths rather than actually attempting bypasses against live artifacts
- **Step 7** classified recommendations into Categories A/B/C per the framework
- **Step 8** synthesis was performed after all prior steps completed

### Framework Observations from Dogfooding

1. **Step 6 worked better as code analysis than live probes.** Reading the hook source and tracing execution paths was more informative than attempting actual bypasses, because the hooks block with exit code 2 which would require creating test artifacts. Future evaluations should specify "code-path analysis" as the primary red-team method, with live probes reserved for ambiguous cases.

2. **The absorption-wave mapping (Step 5b) was the most time-intensive step.** 206 OBPIs across 15 ADRs required reading brief objectives and mapping to findings. Future evaluations should pre-filter by ADR relevance before deep-diving briefs.

3. **S6 severity was revised downward during red-teaming.** The initial assessment assumed `--force` could shortcut closeout. The probe revealed `gz closeout` is independent with its own real-time gate execution. This demonstrates the value of red-teaming: assumptions about bypass paths are often wrong.
