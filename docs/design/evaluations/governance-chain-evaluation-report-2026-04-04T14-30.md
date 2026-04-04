# Governance Chain Evaluation Report

## Date, Evaluator, Repository State

| Field | Value |
|-------|-------|
| **Date** | 2026-04-04 |
| **Evaluator** | Codex GPT-5 (framework v1.1) |
| **Commit SHA** | `d5985c04` on `main` |
| **Framework** | `governance-chain-evaluation.md` v1.1 |

---

## 1. Executive Summary

- **Chain score (weakest-link):** 1.71 (Link 2: Pipeline Execution)
- **Findings by severity:** 3 High, 4 Medium, 3 Low
- **Coverage gaps:** 3 (`gap_flag: TRUE` -- S2, S5, S10)
- **Top 3 recommendations:**
  1. **[Category A]** Expand `pipeline-gate.py` path scope beyond `src/` and `tests/` (S2 -- High, gap)
  2. **[Category A]** Add NO-GO verdict check to `plan-audit-gate.py` (S1 -- High)
  3. **[Category B]** Prioritize ADR-0.34.0 (Claude Hooks Absorption) first in the absorption wave -- highest ADDRESS density across systemic findings

**Headline finding:** The pipeline has strong handoff integrity (plan-audit gate is T1) but weak scope enforcement -- content-type blindness (S2) and unenforced Allowed Paths (S3) mean the pipeline gates *activation* but not *scope*. The authoring-to-pipeline handoff lacks a quality gate (S1), and the Iron Law has zero mechanical backstop (S9).

---

## 2. Baseline State

### ADR Counts by State

| State | Foundation | Feature | Absorption (0.25-0.40) | Pool | Total |
|-------|:---------:|:-------:|:---------------------:|:----:|:-----:|
| Pending | 5 | 0 | 16 | 46 | 67 |
| In Progress | 0 | 0 | 0* | 0 | 0 |
| Validated | 10 | 24 | 0 | 0 | 34 |
| **Total** | **15** | **24** | **16** | **46** | **101** |

*ADR-0.40.0 has 1/5 OBPIs in progress but ADR lifecycle is Pending.

### OBPI Counts

- **Total OBPIs in the state graph:** 430
- **Completed OBPIs with ledger completion receipts:** 187
- **OBPIs without completion receipts:** 243
- **Pending absorption-wave OBPIs:** 210 (ADR-0.25.0 through ADR-0.40.0)
- **Pool ADRs with OBPIs**: 0 (all unscoped)

### Validation Output

```
Validated: surfaces, documents
All validations passed (2 scopes).
```

No structural defects at baseline.

---

## 3. Scorecard

### 3a. Scoring Matrix

| Dimension | Link 1: Authoring | Link 2: Pipeline | Link 3: Verification | Link 4: Closeout |
|-----------|:-:|:-:|:-:|:-:|
| **D1: Gate coverage** | 2 | 2 | 2 | 3 |
| **D2: Handoff integrity** | 2 | 3 | 2 | 2 |
| **D3: Scope enforcement** | 1 | 1 | 2 | 2 |
| **D4: Evidence fidelity** | 2 | 2 | 2 | 2 |
| **D5: Escape hatch governance** | 2 | 1 | 2 | 1 |
| **D6: Lifecycle coherence** | 2 | 2 | 3 | 3 |
| **D7: Observability** | 2 | 1 | 2 | 2 |
| **Mean** | **1.86** | **1.71** | **2.14** | **2.14** |

**Chain score (weakest link): 1.71**

### 3b. Per-Link Narratives

**Link 1 -- Authoring (1.86):** The interview-create-evaluate-specify sequence produces high-quality output when followed faithfully. `gz-adr-evaluate` produces GO/NO-GO verdicts but no T1 mechanism blocks lifecycle progression on NO-GO (S1, D1=2). The handoff to pipeline is partially gated: `plan-audit-gate.py` validates plan-audit receipts (T1), but does not check evaluation scorecard verdict (D2=2). Allowed Paths declared in OBPI briefs are unenforced at authoring time (D3=1). Interview artifact persistence is unchecked (S10). Observability is adequate: scorecards and ledger events exist but interview artifacts may be lost (D7=2).

**Link 2 -- Pipeline (1.71):** The plan-audit gate provides strong handoff integrity from authoring (D2=3). However, `pipeline-gate.py` only gates `src/` and `tests/` writes -- documentation, configuration, and governance artifact OBPIs have zero pipeline enforcement (S2, D1=2, D3=1). The Iron Law (all 5 stages must complete) has no mechanical backstop (S9, D7=1) -- an agent can stop after Stage 2 with no hook detecting abandonment. The `--force` attestation bypass has no quality bar (S6, D5=1). `pipeline-completion-reminder.py` is advisory only (exit 0).

**Link 3 -- Verification (2.14):** `gz-obpi-reconcile` and `gz-adr-audit` provide structured evidence evaluation. The `obpi-completion-validator.py` hook enforces ledger evidence before brief status transitions (D6=3). Reconciliation uses grep-based `@covers` tag detection that can produce false positives (S4, D4=2). The `gz audit` CLI hard-blocks without prior attestation. Scope enforcement is adequate: `build_scope_audit()` records violations post-hoc (D3=2).

**Link 4 -- Closeout (2.14):** The `gz closeout` CLI provides strong lifecycle gating (D6=3) -- it enforces OBPI completion, quality gates (test/lint/typecheck/docs), and attestation recording atomically with no `--force` flag. Gate coverage is the strongest of any link (D1=3). Weaknesses: product proof enforcement is feature-flagged (S5, D5=1), and the `--force` attestation on `gz attest` has no quality bar (S6). Observability is adequate: ceremony protocol exists but script adherence is agent-dependent (D7=2).

### 3c. Chain-Level Assessment

The chain's weakest link is Pipeline Execution (1.71). Two gaps dominate: content-type-blind pipeline enforcement (S2) and the absence of a run-to-completion backstop (S9). These are compounded by Allowed Paths being unenforced (S3). The verification and closeout links have solid foundations with strong lifecycle coherence. The authoring link sits between -- adequate but lacking a hard gate between quality evaluation and lifecycle progression.

---

## 4. Systemic Findings

### S1: No Hard Gate Between Authoring Quality and Lifecycle Progression

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Chain links** | 1 -> 2 |
| **Current tier** | T2 |
| **Target tier** | T1 |
| **Evidence** | `gz-adr-evaluate` SKILL.md mandates GO/NO-GO verdict. No hook in `.claude/settings.json` checks this verdict before ADR state progression or pipeline entry. `plan-audit-gate.py` validates plan-audit receipt presence and freshness but does not check for `EVALUATION_SCORECARD.md` existence or verdict. An agent can produce a thin ADR, receive NO-GO, and proceed to `gz-obpi-specify` and pipeline execution. |
| **Pool coverage** | `agent-reliability-framework` (DIRECT), `skill-behavioral-hardening` (PARTIAL), `constraint-library` (TANGENTIAL) |
| **Absorption coverage** | ADR-0.34.0 OBPIs 01/07/08 (ADDRESS), ADR-0.25.0-12 admission-pattern (ADDRESS), ADR-0.26.0-04 adr-governance (ADDRESS) |
| **Gap flag** | FALSE |

### S2: Content-Type Blind Spot in Pipeline Enforcement

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Chain links** | 2 |
| **Current tier** | Gap |
| **Target tier** | T1 |
| **Evidence** | `pipeline-gate.py:58` -- `if rel_path is None or not rel_path.startswith(("src/", "tests/")):` returns early (exit 0) for any path outside `src/` and `tests/`. Documentation-only OBPIs (e.g., ADR-0.24.0), config-only OBPIs, and governance artifact OBPIs have zero pipeline enforcement. Grep of `.claude/hooks/` for `docs/` or `config/` in pipeline-gate confirms no broader path matching. |
| **Pool coverage** | None |
| **Absorption coverage** | ADR-0.34.0-11 dataset-guard (ADDRESS), ADR-0.35.0-09/17 markdown hooks (ADDRESS), ADR-0.34.0-05 post-edit-ruff (COMPLICATE -- reinforces Python-only pattern) |
| **Gap flag** | TRUE |

### S3: Allowed Paths Constraint Is Decoration

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Chain links** | 2, 3 |
| **Current tier** | Gap |
| **Target tier** | T1 |
| **Evidence** | Grep of `.claude/hooks/` for `allowed_paths` and `denied_paths` returns zero results. OBPI briefs declare Allowed/Denied Paths but no hook reads or enforces them. The pipeline gate checks pipeline activation status only, not whether the file being edited falls within the OBPI's declared scope. `build_scope_audit()` records `out_of_scope_files` at completion time but does not block. An agent can edit any file in `src/` or `tests/` regardless of OBPI scope declaration. |
| **Pool coverage** | `agent-reliability-framework` (DIRECT -- AR2 requires scope-checked output), `constitution-invariants` (TANGENTIAL) |
| **Absorption coverage** | ADR-0.25.0-12 admission-pattern (ADDRESS), ADR-0.35.0-07 (ADDRESS), ADR-0.38.0-10 (ADDRESS), ADR-0.39.0-04/05 (ADDRESS) |
| **Gap flag** | FALSE |

### S4: Reconcile Auto-Promotion on Heuristic Evidence

| Field | Value |
|-------|-------|
| **Severity** | Medium |
| **Chain links** | 3 |
| **Current tier** | T2 |
| **Target tier** | T1 |
| **Evidence** | `gz-obpi-reconcile` Phase 2 uses grep-based `@covers` tag detection and test result parsing to auto-mark briefs Completed. A false-positive `@covers` match (e.g., a comment referencing another OBPI's tag) could trigger incorrect promotion. Downstream audit trusts ledger proof from reconciliation. |
| **Pool coverage** | `agent-reliability-framework` (PARTIAL), `adr-amendment-tracking` (TANGENTIAL) |
| **Absorption coverage** | ADR-0.27.0 OBPIs 03/05/11/12 ARB receipts (ADDRESS), ADR-0.26.0-07/08 traceability/validation-receipt (ADDRESS), ADR-0.32.0-17 autolink-sync (ADDRESS), ADR-0.26.0-03 adr-recon (COMPLICATE -- may entrench grep patterns) |
| **Gap flag** | FALSE |

### S5: Product Proof Gate Is Feature-Flagged

| Field | Value |
|-------|-------|
| **Severity** | Medium |
| **Chain links** | 4 |
| **Current tier** | T1 (conditional) |
| **Target tier** | T1 (unconditional) |
| **Evidence** | `closeout.py:569` -- `enforce_proof = decisions.product_proof_enforced()`. When `ops.product_proof` flag is disabled, missing runbook/manpage/docstring coverage produces advisory warning at `closeout.py:596` instead of raising SystemExit. The flag exists in `gzkit/flags/decisions.py:19`. |
| **Pool coverage** | None |
| **Absorption coverage** | ADR-0.35.0 OBPIs 13/14/15 pre-commit hooks (ADDRESS), ADR-0.31.0-08/10 validate-manpages/interrogate (ADDRESS), ADR-0.30.0-02 config-doctrine (COMPLICATE -- may normalize feature-flagged gates) |
| **Gap flag** | TRUE |

### S6: --force Attestation Has No Quality Bar

| Field | Value |
|-------|-------|
| **Severity** | Medium |
| **Chain links** | 4 |
| **Current tier** | T3 |
| **Target tier** | T1 or T2 |
| **Evidence** | `attest.py:70` requires `--force` when OBPIs incomplete; `attest.py:124` requires `--reason` when `--force` bypasses gates. Reason is free-text with no minimum length, structure, or secondary approval. Ledger records `forced: true` but no downstream audit distinguishes forced from normal attestation in severity. **Mitigating factor:** `gz closeout` is independent -- re-runs all gates in real-time with no `--force` flag. A forced attestation does not shortcut the closeout path. |
| **Pool coverage** | `agent-reliability-framework` (DIRECT -- AR3 attestation quality), `attestation-advisory-agent` (PARTIAL), `graduated-oversight-model` (PARTIAL) |
| **Absorption coverage** | ADR-0.25.0-01 attestation-pattern (ADDRESS), ADR-0.26.0-04 adr-governance (ADDRESS), ADR-0.32.0-11/13 (ADDRESS) |
| **Gap flag** | FALSE |

### S7: Self-Close Exception Defers Review

| Field | Value |
|-------|-------|
| **Severity** | Medium |
| **Chain links** | 2 -> 4 |
| **Current tier** | T2 -> T3 |
| **Target tier** | T2 with proportional review |
| **Evidence** | OBPIs using exception-mode self-close record `attestation_type: "self-close-exception"` in the ledger. The `obpi-completion-validator` hook fires and checks Implementation Summary and Key Proof (structural T1 check), but no human review occurs until ADR closeout ceremony. A large batch of self-closed OBPIs creates ceremony verification burden that may encourage rubber-stamping. |
| **Pool coverage** | `graduated-oversight-model` (DIRECT -- Standard tier adds spot-check sampling), `channel-agnostic-human-triggers` (TANGENTIAL) |
| **Absorption coverage** | ADR-0.34.0-01 obpi-completion-validator (ADDRESS), ADR-0.32.0-11 closeout comparison (ADDRESS) |
| **Gap flag** | FALSE |

### S8: Lane Classification Is Write-Once

| Field | Value |
|-------|-------|
| **Severity** | Low |
| **Chain links** | 1 -> all |
| **Current tier** | T3 |
| **Target tier** | T2 |
| **Evidence** | `resolve_adr_lane()` reads lane from `adr_created` ledger event and falls back to `config.mode`. No mechanism re-evaluates lane when ADR scope evolves. A lite ADR that later touches CLI contracts remains lite unless manually corrected. |
| **Pool coverage** | `heavy-lane` (PARTIAL -- addresses detection/enforcement but not reclassification) |
| **Absorption coverage** | ADR-0.26.0-04 adr-governance (ADDRESS), ADR-0.25.0-08 ledger-pattern (COMPLICATE -- may entrench write-once) |
| **Gap flag** | FALSE (weakly covered) |

### S9: Run-to-Completion Is Narrative-Only

| Field | Value |
|-------|-------|
| **Severity** | Low |
| **Chain links** | 2 |
| **Current tier** | T2 |
| **Target tier** | T1 |
| **Evidence** | Grep of `.claude/hooks/` for "stage", "completion", "iron law", and "run to completion" returns zero results. The Iron Law is enforced entirely through `gz-obpi-pipeline` skill narrative. `pipeline-completion-reminder.py` warns before commits with incomplete pipelines (advisory, exit 0). An agent can stop after Stage 2 or 3 with no mechanical detection. **Mitigating factor:** `obpi-completion-validator` blocks marking the brief Completed without evidence, and session-staleness-check flags stale markers. |
| **Pool coverage** | `skill-behavioral-hardening` (DIRECT), `agent-reliability-framework` (DIRECT), `structured-blocker-envelopes` (PARTIAL) |
| **Absorption coverage** | ADR-0.34.0 OBPIs 06/08 pipeline-router/pipeline-gate (ADDRESS), ADR-0.32.0-09 gates comparison (ADDRESS), ADR-0.37.0-10 (COMPLICATE -- may describe enforcement without implementing it) |
| **Gap flag** | FALSE |

### S10: Interview Artifact Persistence Unchecked

| Field | Value |
|-------|-------|
| **Severity** | Low |
| **Chain links** | 1 |
| **Current tier** | T3 |
| **Target tier** | T2 |
| **Evidence** | Grep of `.claude/hooks/` and `src/gzkit/commands/` for "interview" returns zero results. The structured interview is mandatory in `gz-adr-create` Step 0 but no gate verifies the interview JSON artifact was saved alongside the ADR. The artifact could be lost or never written. |
| **Pool coverage** | None |
| **Absorption coverage** | None |
| **Gap flag** | TRUE |

---

## 5. Architectural Intent Map

### 5a. Pool ADR Coverage Matrix

| Finding | agent-reliability-framework | skill-behavioral-hardening | constraint-library | graduated-oversight-model | heavy-lane | attestation-advisory-agent | constitution-invariants | adr-amendment-tracking | structured-blocker-envelopes | channel-agnostic-human-triggers |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| S1 | DIRECT | PARTIAL | TANGENTIAL | -- | -- | -- | -- | -- | -- | -- |
| S2 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| S3 | DIRECT | -- | -- | -- | -- | -- | TANGENTIAL | -- | -- | -- |
| S4 | PARTIAL | -- | -- | -- | -- | -- | -- | TANGENTIAL | -- | -- |
| S5 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| S6 | DIRECT | -- | -- | PARTIAL | -- | PARTIAL | -- | -- | -- | -- |
| S7 | -- | -- | -- | DIRECT | -- | -- | -- | -- | -- | TANGENTIAL |
| S8 | -- | -- | -- | -- | PARTIAL | -- | -- | -- | -- | -- |
| S9 | DIRECT | DIRECT | -- | -- | -- | -- | -- | -- | PARTIAL | -- |
| S10 | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |

**Gaps (no DIRECT pool coverage):** S2, S4, S5, S10

### 5b. Absorption Wave Intersection

| Absorption ADR | Findings it ADDRESSes | Findings it COMPLICATEs |
|---------------|----------------------|------------------------|
| **ADR-0.34.0** (claude-hooks) | S1, S2, S7, S9 (via OBPIs 01/06/07/08/11) | S2 (OBPI-05 reinforces Python-only) |
| **ADR-0.35.0** (pre-commit hooks) | S2, S3, S5 (via OBPIs 07/09/13/14/15/17) | -- |
| **ADR-0.27.0** (ARB receipts) | S4 (via OBPIs 03/05/11/12 -- deep coverage) | -- |
| **ADR-0.26.0** (governance lib) | S1, S3, S4, S6, S8 (via OBPIs 03/04/07/08) | S4 (OBPI-03 may entrench grep patterns) |
| **ADR-0.25.0** (core infra) | S1, S3, S6 (via OBPIs 01/12) | S8 (OBPI-08 may entrench write-once) |
| ADR-0.32.0 (CLI comparison) | S6, S7, S9 (via OBPIs 09/11/13) | -- |
| ADR-0.31.0 (new CLI) | S5 (via OBPIs 08/10) | -- |
| ADR-0.39.0 (instruction plugins) | S3 (via OBPIs 04/05) | -- |
| ADR-0.38.0 (templates/scaffolds) | S3 (via OBPI-10) | -- |
| ADR-0.37.0 (methodology docs) | -- | S9 (OBPI-10 may describe without implementing) |
| ADR-0.30.0 (config schema) | -- | S5 (OBPI-02 may normalize feature-flagged gates) |

**COMPLICATE items requiring design attention:**

1. **ADR-0.34.0-05 (post-edit-ruff) -> S2:** Reinforces the Python-centric pipeline pattern. When implementing content-type-aware gating, ensure this OBPI does not further entrench `src/`-only enforcement.
2. **ADR-0.26.0-03 (adr-recon) -> S4:** May entrench grep-based evidence patterns. Should follow ADR-0.27.0 (ARB receipts) so reconciliation can consume schema-validated receipts rather than deepening grep heuristics.
3. **ADR-0.30.0-02 (config-doctrine) -> S5:** May normalize feature-flagged gates as an acceptable pattern. Ensure config doctrine treats product-proof enforcement as a deployment concern, not a permanent toggle.
4. **ADR-0.25.0-08 (ledger-pattern) -> S8:** May further entrench write-once lane classification. Ensure ledger pattern design includes event types for lane reclassification.
5. **ADR-0.37.0-10 (architectural-enforcement) -> S9:** Risk of documenting the run-to-completion requirement without implementing a mechanical backstop.

### 5c. Coverage Gaps

| Finding | Gap Status | Recommended Action |
|---------|-----------|-------------------|
| **S2** (content-type blind spot) | TRUE -- no pool ADR | **Category A fix first** (expand `pipeline-gate.py` path filter), then absorb broader content-type awareness into ADR-0.34.0 scope. Alternatively, expand `agent-reliability-framework` scope to include content-type-aware pipeline enforcement under AR2. No new pool entry needed. |
| **S5** (product proof feature-flagged) | TRUE -- no pool ADR | **Accept risk with timeline.** Set version cutoff: after ADR-0.30.0 config-doctrine executes, `ops.product_proof` becomes unconditionally `true`. Alternatively, Category A fix now (remove flag or default to enforced). No new pool entry needed. |
| **S10** (interview artifact unchecked) | TRUE -- no pool or absorption | **Accept risk.** Low severity. Interview artifacts are consumed immediately during ADR creation and their absence is detectable during `gz-adr-evaluate` exemplar comparison. Creating architectural intent is disproportionate. Add validation check to `gz validate --documents` as a low-priority Category A item. |

---

## 6. Red-Team Results

| # | Finding | Challenge | Expected | Actual | Result |
|---|---------|-----------|----------|--------|--------|
| RT-1 | S2 | Read `pipeline-gate.py:58` -- trace execution for `docs/` path | Should block | Early return (exit 0) for non-`src/`/`tests/` paths | **PASSED** |
| RT-2 | S3 | Grep `.claude/hooks/` for `allowed_paths` enforcement | Should find path-scope checking | Zero results | **PASSED** |
| RT-3 | S5 | Read `closeout.py:569` -- trace product-proof flag | Should unconditionally enforce | `decisions.product_proof_enforced()` gates; advisory when off | **PASSED** |
| RT-4 | S6 | Read `attest.py:124` -- check `--force` reason validation | Should require structured reason | Accepts any non-empty string | **PASSED** |
| RT-5 | S9 | Grep `.claude/hooks/` for stage/completion/iron-law | Should find completion detector | Zero results | **PASSED** |
| RT-6 | S10 | Grep hooks + CLI commands for interview artifact check | Should find validation | Zero results | **PASSED** |
| RT-7 | S1 | Read `plan-audit-gate.py` -- check for evaluate verdict | Should block on NO-GO | Checks plan-audit receipt only, not evaluate verdict | **PASSED** |
| RT-8 | S8 | Read `resolve_adr_lane()` -- check for re-evaluation | Should find reclassification | Reads `adr_created` event only; no re-evaluation | **PASSED** |
| RT-9 | S4 | Run `gz validate --documents --surfaces` | Should pass | Passed -- structural validation sound | **BLOCKED** |
| RT-10 | S7 | Run `gz closeout ADR-0.24.0 --dry-run` | Should show ceremony structure | Showed 5/5 OBPIs with product proof status | **BLOCKED** |

**Summary:** 8 PASSED (bypass path confirmed), 2 BLOCKED (enforcement held).

### Bypass Path Narratives

**RT-1 (S2):** `pipeline-gate.py` line 58 explicitly early-returns for any path not starting with `src/` or `tests/`. A documentation-only OBPI (e.g., writing to `docs/user/runbook.md`) proceeds with zero pipeline enforcement.

**RT-2 (S3):** No hook in `.claude/hooks/` reads or references `allowed_paths` or `denied_paths` from OBPI briefs. The constraint is purely decorative -- skill narrative that no T1 mechanism enforces.

**RT-4 (S6):** `attest.py:124` requires `--reason` when `--force` is used but accepts any string. `gz attest ADR-X.Y.Z --status completed --force --reason "."` would be accepted. No minimum length, structure, or secondary approval. **Mitigating factor:** `gz closeout` is independent with its own real-time gate execution, so forced attestation does not shortcut the release path.

**RT-5 (S9):** No hook detects pipeline abandonment. `pipeline-completion-reminder.py` only fires on commit attempts and is advisory (exit 0). An agent that stops after Stage 2 and never commits faces zero mechanical resistance.

**RT-7 (S1):** `plan-audit-gate.py` validates plan-audit receipt presence and freshness. It does not check `gz-adr-evaluate` verdict. An ADR with a NO-GO evaluation can enter pipeline execution with a valid plan-audit receipt.

---

## 7. Actionable Outcomes

### 7a. Category A -- Immediate Infrastructure Hardening

No ADR required. Implement before the next ADR/OBPI cycle.

| # | Recommendation | Finding(s) | Scope | Severity |
|---|---------------|-----------|-------|----------|
| A1 | Expand `pipeline-gate.py` path filter to include `docs/`, `config/`, `.gzkit/` when pipeline marker exists. Simplest approach: drop the `src/`/`tests/` filter and gate ALL writes during active pipeline. | S2 | `.claude/hooks/pipeline-gate.py` | High |
| A2 | Add NO-GO verdict check to `plan-audit-gate.py`: check for `EVALUATION_SCORECARD.md` with non-NO-GO verdict before issuing plan-audit receipt. Chains authoring quality into the pipeline entry gate. | S1 | `.claude/hooks/plan-audit-gate.py` | High |
| A3 | Add `--force` reason quality bar: minimum 20 characters, must not be single-word. | S6 | `src/gzkit/commands/attest.py` | Medium |
| A4 | Make `pipeline-completion-reminder.py` blocking (exit 2) for commits when pipeline stage < 5. | S9 | `.claude/hooks/pipeline-completion-reminder.py` | Low |
| A5 | Add interview artifact check to `gz validate --documents`: verify ADR directories with OBPIs also contain an interview JSON artifact. | S10 | CLI validation scope | Low |

**Sequencing:** A1 and A2 are high-severity and should be implemented before the next ADR/OBPI cycle. A3-A5 can follow.

### 7b. Category B -- ADR Sequencing Guidance

**Recommended absorption-wave priority order (governance-chain ADDRESS density):**

| Rank | ADR | ADDRESS Count | Key Findings Addressed |
|------|-----|:---:|----------------------|
| 1 | **ADR-0.34.0** (Claude Hooks) | 4 | S1, S2, S7, S9 |
| 2 | **ADR-0.25.0** (Core Infrastructure) | 3 | S1, S3, S6 |
| 3 | **ADR-0.26.0** (Governance Library) | 5 | S1, S3, S4, S6, S8 |
| 4 | **ADR-0.35.0** (Pre-commit Hooks) | 3 | S2, S3, S5 |
| 5 | **ADR-0.27.0** (ARB Receipts) | 1 (deep) | S4 |
| 6 | **ADR-0.32.0** (Overlapping CLI) | 3 | S6, S7, S9 |
| 7+ | Remaining absorption ADRs | 0-1 each | Tangential or neutral |

**Justification:** ADR-0.34.0 has the highest governance-chain impact -- it directly addresses hook enforcement gaps (S1 verdict gate, S2 content-type awareness, S7 completion validator, S9 pipeline enforcement). Executing it first means every subsequent ADR benefits from a stronger chain.

**COMPLICATE sequencing:** ADR-0.27.0 (ARB receipts) should execute before ADR-0.26.0 (governance lib) to prevent OBPI-0.26.0-03 (adr-recon) from entrenching grep-based evidence patterns before schema-validated receipts are available.

### 7c. Category C -- New Architectural Intent

| Finding | Gap Status | Recommended Action | Detail |
|---------|-----------|-------------------|--------|
| **S2** | TRUE | **Expand scope + Category A fix** | Category A fix (A1) addresses immediate enforcement gap. Expand `agent-reliability-framework` AR2 scope to include content-type-aware pipeline enforcement for the principled long-term design. No new pool entry needed. |
| **S5** | TRUE | **Accept risk with timeline** | Set version cutoff: after ADR-0.30.0 config-doctrine executes, `ops.product_proof` becomes unconditionally `true`. No new pool entry needed. |
| **S10** | TRUE | **Accept risk** | Low severity. Interview artifacts consumed immediately. Absence detectable during `gz-adr-evaluate`. Category A fix (A5) adds validation check. No new pool entry needed. |

---

## 8. Next Actions

### Category A -- Proposed for Immediate Implementation

| Item | Severity | Decision required |
|------|----------|------------------|
| A1: Expand pipeline-gate path scope | High | Operator approval |
| A2: Add NO-GO verdict check to plan-audit-gate | High | Operator approval |
| A3: Add --force reason quality bar | Medium | Operator approval |
| A4: Make pipeline-completion-reminder blocking | Low | Operator approval |
| A5: Add interview artifact check to gz validate | Low | Operator approval |

### Category B -- Sequencing Decisions

| Decision | Status |
|----------|--------|
| Prioritize ADR-0.34.0 first in absorption wave | Recommended -- operator to accept/defer |
| Follow with ADR-0.25.0 then ADR-0.26.0 | Recommended -- operator to accept/defer |
| Sequence ADR-0.27.0 before ADR-0.26.0 (COMPLICATE mitigation) | Recommended -- operator to accept/defer |
| Flag 5 COMPLICATE OBPIs for design attention | Recommended -- operator to acknowledge |

### Category C -- Gap Decisions

| Finding | Recommended | Status |
|---------|------------|--------|
| S2 | Expand agent-reliability-framework scope | Operator approval |
| S5 | Accept risk with version cutoff | Operator approval |
| S10 | Accept risk | Operator approval |

### Next Evaluation

Re-evaluate after:
- Category A items A1 and A2 are implemented, OR
- ADR-0.34.0 (Claude Hooks Absorption) execution completes, OR
- 90 days (2026-07-03), whichever comes first.

Run the companion Bilateral Intent-Alignment Assessment before beginning the absorption wave.

---

## Appendix: Evaluation Method Notes

This report was produced by running the framework defined in `governance-chain-evaluation.md` v1.1, Steps 1-8 sequentially.

- **Step 1:** `uv run gz status`, `uv run gz state --json`, `uv run gz validate --documents --surfaces`, `git rev-parse HEAD`
- **Step 2:** Parallel research agents inventoried all hooks (`.claude/hooks/`, `.claude/settings.json`), CLI gate commands (`src/gzkit/commands/closeout.py`, `attest.py`, `audit_cmd.py`, `validate_cmd.py`, `gates.py`), and skill SKILL.md files (13 skills across 4 chain links)
- **Step 3:** Scoring based on T1/T2/T3 classification with specific file/line citations
- **Step 4:** Findings carried forward from Appendix B baseline (v1.1 framework) with updated evidence
- **Step 5:** Pool ADR scope review (10 pool ADRs) and absorption-wave ADR mapping (16 ADRs, key OBPIs)
- **Step 6:** Red-team challenges used code-path analysis (reading hook source, tracing execution) supplemented by live dry-run probes where non-destructive
- **Step 7-8:** Classification per framework Categories A/B/C

### Framework Drift Notes

- **Step 1 command drift:** framework v1.1 says `uv run gz adr status --table`, but at commit `d5985c04` the `gz adr status` CLI requires a positional ADR and no longer supports `--table`. The evaluation used `uv run gz status` for the lifecycle overview and confirmed the drift with `uv run gz adr status --help`.
- **Baseline counts corrected from live graph:** the state graph at `d5985c04` contains 101 ADRs and 430 OBPIs. Earlier draft counts in this file overstated both totals.

### Scoring Rationale Notes

- **S3 rated High:** Allowed Paths unenforcement spans both Pipeline (Link 2) and Verification (Link 3), making it a cross-link finding with systemic impact.
- **S6 rated Medium:** Although `gz closeout` is independent of forced attestation, the quality bar absence is a governance hygiene issue -- forced attestation with reason `"."` should not be possible.
- **Link 2 weakest link (not Link 1):** Pipeline has both a Gap-tier finding (S2, score 0) and the Iron Law enforcement absence (S9). Authoring has weaker scores across more dimensions but no Gap-tier findings.
