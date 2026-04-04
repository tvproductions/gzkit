# Governance Chain Evaluation Framework

**Version:** 1.1
**Date:** 2026-04-04
**Scope:** The four mainstay processes of gzkit governance
**Companion:** `bilateral-intent-alignment-assessment.md` (strategic alignment)

---

## Preamble: Why This Framework Exists and Where It Fits

gzkit has two evaluation frameworks. They serve different purposes, run at different cadences, and answer different questions. Understanding which one to use -- and why both exist -- matters more than the frameworks themselves.

### The two-layer evaluation model

**This document (Layer 2: Enforcement Evaluation)** is a *depth* tool. It takes known-critical flows as given and evaluates how well they are enforced. It answers: "given that these flows matter, are they working?" It produces scores, systemic findings, red-team results, and actionable fix categories. It runs per-cycle -- before absorption waves, after significant hook/CLI changes, or when enforcement confidence needs refreshing.

**The Bilateral Intent-Alignment Assessment (Layer 1)** is a *wide-angle* tool. It compares what the PRD and Lodestar say gzkit should be against what the project's surfaces actually reveal it to be. It answers: "is what we built actually what we set out to build, and if not, who's right -- the plan or the reality?" It runs periodically at strategic inflection points.

### Why both are necessary

A project that has shipped 34 ADRs and 299 OBPIs is not a greenfield effort following a plan. It is a system shaped by hundreds of locally-rational design decisions that may have collectively shifted the project's center of gravity away from -- or beyond -- the original intent. The enforcement evaluation catches broken machinery. The bilateral assessment catches misaligned direction.

Neither subsumes the other:

- The bilateral assessment might discover that a fifth critical flow exists that the enforcement evaluation should cover. Or that one of the four flows isn't as critical as assumed.
- The enforcement evaluation might reveal that a stated-critical flow is poorly enforced, prompting the bilateral assessment to ask: "is it poorly enforced because it's actually not as important as we thought?"

### When to use which

| Situation | Framework |
|-----------|-----------|
| Before an absorption wave or major ADR cycle | Both (bilateral first, then enforcement) |
| After implementing hook/CLI hardening fixes | Enforcement only |
| After a strategic pivot or PRD revision | Bilateral only |
| Routine governance hygiene check | Enforcement only |
| Onboarding a new red-team evaluator | Bilateral first (validates assumptions), then enforcement |
| Project feels "off" but nothing specific is broken | Bilateral (it finds directional drift) |

---

## Part 1: Evaluation Framework

### Purpose

This framework evaluates the integrity and enforcement strength of the four-link governance chain that defines gzkit's core purpose:

1. **ADR/OBPI Authoring** -- design intent captured as architectural decisions and decomposed into implementable increments
2. **OBPI Pipeline Execution** -- governed implementation with plan-audit, locking, staged verification, and evidence presentation
3. **OBPI Outcomes Verification/Audit** -- evidence reconciliation, ledger proof, value demonstration, and lifecycle progression
4. **ADR/OBPI Closeout Ceremony** -- human-witnessed attestation, version bump, and release

The four links above were identified by the project operator as the mainstay processes of gzkit. The Bilateral Intent-Alignment Assessment (companion document) can validate or challenge whether these are the right four links by independently deriving critical flows from PRD/Lodestar intent.

Each link is evaluated against the same rubric. Findings are cross-referenced to existing architectural intent (pool ADRs, absorption-wave ADRs) and gaps are flagged where no intent exists.

### Enforcement Tier Model

Every capability in the chain is classified into one of three enforcement tiers:

| Tier | Label | Meaning | Bypass requires |
|------|-------|---------|-----------------|
| **T1** | Hard | Hook or CLI blocks execution (exit code 1 or 2) | Code change to hook/CLI |
| **T2** | Protocol | Skill narrative directs agent behavior | Agent ignoring instructions |
| **T3** | Human | Relies on operator judgment or attention | Human error or inattention |

A finding is a capability that should be T1 but is currently T2 or T3, or a capability at T2/T3 with known exploitation paths.

### Evaluation Dimensions

Each chain link is evaluated on these seven dimensions:

| # | Dimension | Question |
|---|-----------|----------|
| D1 | **Gate coverage** | Does every mandatory quality check have a hard gate (T1)? |
| D2 | **Handoff integrity** | Is the output of the upstream link validated before the downstream link consumes it? |
| D3 | **Scope enforcement** | Are declared constraints (paths, lanes, content types) enforced at runtime? |
| D4 | **Evidence fidelity** | Is evidence deterministic and schema-validated, or heuristic and grep-based? |
| D5 | **Escape hatch governance** | Do override mechanisms (--force, self-close, exception mode) have quality bars? |
| D6 | **Lifecycle coherence** | Do state transitions enforce prerequisite completion? |
| D7 | **Observability** | Can a post-hoc reviewer reconstruct what happened and why? |

### Scoring

Each dimension is scored per chain link:

| Score | Meaning |
|-------|---------|
| **3 -- Strong** | T1 enforcement or T2 with no known bypass path |
| **2 -- Adequate** | T2 enforcement with known but low-probability bypass paths |
| **1 -- Weak** | T2/T3 enforcement with known, exercisable bypass paths |
| **0 -- Absent** | No enforcement mechanism exists |

A chain link's overall score is the unweighted mean of its seven dimensions (0.0 -- 3.0 scale). The chain's overall score is the minimum of its four link scores (weakest link determines chain strength).

### Systemic Findings Registry

Findings are tracked with a stable identifier (S1, S2, ...) and classified:

| Field | Description |
|-------|-------------|
| **ID** | Stable reference (S1, S2, ...) |
| **Title** | One-line summary |
| **Severity** | High / Medium / Low |
| **Chain links affected** | Which of the four links |
| **Current tier** | T1, T2, T3, or Gap |
| **Target tier** | What it should be |
| **Pool coverage** | Which pool ADRs carry architectural intent for this finding |
| **Absorption coverage** | Which absorption-wave OBPIs would address, complicate, or are neutral |
| **Gap flag** | TRUE if no existing architectural intent covers the finding |

---

## Part 2: How to Run the Evaluation

### Prerequisites

- Access to the gzkit repository at HEAD
- Ability to run `uv run gz` commands
- Read access to `.claude/skills/`, `.claude/hooks/`, `.claude/settings.json`
- Read access to `AGENTS.md`, `.claude/rules/`, and `docs/design/adr/`

### Step 1: Establish Baseline State

Run these commands and capture output:

```bash
uv run gz adr status --table          # ADR lifecycle overview
uv run gz state --json                # Artifact graph state
uv run gz validate --documents --surfaces  # Structural validity
```

Record the total ADR count by state (Pending, In Progress, Completed, Validated) and the total OBPI count.

### Step 2: Inventory Enforcement Mechanisms

For each chain link, catalog every enforcement point:

**2a. Hard gates (T1):**

- Read `.claude/settings.json` and list all PreToolUse/PostToolUse hooks
- For each hook, read the hook script and record: trigger condition, what it blocks, exit code behavior
- Read CLI command source (`src/gzkit/commands/`) for programmatic validation: `closeout.py`, `attest.py`, `audit_cmd.py`, `validate_cmd.py`, `gates.py`, `lifecycle.py`
- Record every `sys.exit(1)`, `sys.exit(2)`, and raised exception that blocks a governance operation

**2b. Protocol enforcement (T2):**

- Read each skill's `SKILL.md` for the chain link being evaluated
- Extract every "must", "shall", "required", "mandatory", "prohibited" instruction
- For each, determine: is there a corresponding T1 mechanism? If not, classify as T2-only

**2c. Human judgment (T3):**

- Identify every point where the chain relies on human decision, attention, or confirmation
- Distinguish between intentional human gates (attestation decisions) and accidental human dependencies (noticing a missing doc)

### Step 3: Score Each Dimension

For each chain link, score D1-D7 using the scoring rubric (0-3). Provide evidence for each score:

| Link | D1 | D2 | D3 | D4 | D5 | D6 | D7 | Mean |
|------|----|----|----|----|----|----|----|----|
| 1. Authoring | | | | | | | | |
| 2. Pipeline | | | | | | | | |
| 3. Verification | | | | | | | | |
| 4. Closeout | | | | | | | | |

For each score, cite the specific hook, CLI check, skill instruction, or absence thereof.

### Step 4: Identify Systemic Findings

A systemic finding is a weakness that:

- Spans multiple chain links, OR
- Creates a bypass path through a single link that undermines the chain, OR
- Represents a gap where no enforcement exists for a declared policy

For each finding, populate the fields in the Systemic Findings Registry (Part 1).

### Step 5: Map to Architectural Intent

For each finding:

**5a. Check pool ADRs:**

- Read `docs/design/adr/pool/` for ADRs whose scope overlaps the finding
- Classify coverage as DIRECT (the pool ADR's stated scope addresses the finding), PARTIAL (related but incomplete), or TANGENTIAL (touches the area but does not address the finding)

**5b. Check absorption-wave ADRs (0.25.0 -- 0.39.0):**

- Read the ADR and its OBPI briefs
- For each relevant OBPI, classify as ADDRESS (would fix/strengthen), COMPLICATE (would entrench or worsen), or NEUTRAL
- Flag any COMPLICATE relationships -- these require design attention before absorption proceeds

**5c. Flag coverage gaps:**

- If a finding has no DIRECT pool coverage and no ADDRESS absorption OBPI, mark `gap_flag: TRUE`
- These gaps need new architectural intent (new pool ADR or scope expansion of existing ADR)

### Step 6: Red-Team Challenges

For each systemic finding, construct a concrete challenge that an agent can execute:

- State the finding being tested
- Describe the exact sequence of commands or actions
- State the expected behavior (what should happen) vs. the predicted behavior (what will actually happen)
- Execute the challenge and record the actual behavior
- Classify the result: BLOCKED (T1 prevented it), WARNED (T2 flagged it), PASSED (nothing stopped it)

Challenges should be designed to be reproducible and non-destructive. Use `--dry-run` flags where available. Prefer read-only probes over state-mutating tests.

### Step 7: Classify Actionable Outcomes

Every recommendation must be classified into one of three action categories. The categories determine sequencing, not priority -- a Category A fix and a Category C ADR can both be high-severity, but they follow different paths to resolution.

**Category A -- Immediate Infrastructure Hardening**

Fixes to the governance engine itself (hooks, CLI validation, config flags) that require no ADR and no OBPI. These strengthen the chain for all future work.

- Scope: 1-3 file changes in `.claude/hooks/`, `src/gzkit/commands/`, or `config/`
- Sequencing: Execute before the next ADR/OBPI cycle begins. Every future OBPI benefits from a stronger chain.
- Governance: These are internal tooling changes. If they change external CLI behavior (exit codes, new flags), they require an ADR per the lane classification rules. If they only change hook behavior, they are lite-lane maintenance.
- Decision gate: The evaluator proposes Category A items. The operator approves or defers. Approved items are implemented in the current session or the next.

**Category B -- ADR Sequencing Guidance**

Findings that are already captured as absorption-wave OBPIs or pool ADRs but whose priority should be adjusted based on governance-chain impact.

- Scope: No new work created -- existing planned work is reordered
- Sequencing: Apply reordering before the next absorption-wave ADR begins execution
- Decision gate: The evaluator produces a recommended priority order with justification. The operator decides whether to accept the reordering or keep the current plan.
- Key question: Which absorption ADRs have the highest density of ADDRESS relationships to systemic findings? Those should execute first because they harden the chain that all subsequent ADRs flow through.

**Category C -- New Architectural Intent**

Findings with `gap_flag: TRUE` -- no existing pool ADR or absorption OBPI carries intent for the finding. These require a decision:

- **Accept the risk:** The finding is low-severity or the bypass path is theoretical. Document the acceptance in the report and revisit at next evaluation.
- **Expand existing scope:** An existing pool ADR or absorption ADR can absorb the finding with minor scope expansion. Update the ADR/pool-entry description.
- **Create new pool entry:** The finding represents a genuine architectural gap that warrants its own ADR. Create via `gz-design` or direct pool entry.
- Decision gate: The evaluator recommends one of the three options per gap. The operator decides.

**Classification rules:**

1. If the fix is a hook or config change with no external contract impact → Category A
2. If the finding maps to an existing ADR/OBPI with DIRECT or ADDRESS coverage → Category B
3. If the finding has `gap_flag: TRUE` → Category C
4. If the finding maps to existing intent but only PARTIAL or TANGENTIAL → evaluator judgment: is the existing intent sufficient (Category B) or does the gap need explicit coverage (Category C)?

### Step 8: Synthesis

Produce:

1. The completed scorecard (Step 3)
2. The systemic findings registry with all fields populated (Step 4)
3. The architectural intent map showing coverage and gaps (Step 5)
4. The red-team results matrix (Step 6)
5. The actionable outcomes table (Step 7) with category, severity, and sequencing for each recommendation
6. A clear statement of what should happen next: which Category A items to implement now, which Category B reordering to apply, and which Category C decisions to make

---

## Part 3: How to Report Results

### Report Structure

The evaluation report is a single markdown file with these sections:

```
# Governance Chain Evaluation Report
## Date, Evaluator, Repository State

## 1. Executive Summary
- Chain score (weakest-link score)
- Number of findings by severity
- Number of coverage gaps
- Top 3 recommendations

## 2. Baseline State
- ADR counts by state
- OBPI counts by state
- Validation output summary

## 3. Scorecard
- 4x7 scoring matrix with evidence citations
- Per-link narrative (2-3 sentences explaining the scores)
- Chain-level assessment

## 4. Systemic Findings
- One subsection per finding (S1, S2, ...)
- Each contains: title, severity, affected links, current/target tier,
  evidence, pool coverage, absorption coverage, gap flag

## 5. Architectural Intent Map
### 5a. Pool ADR Coverage Matrix
- Finding x Pool ADR matrix (DIRECT / PARTIAL / TANGENTIAL / none)
- Gaps highlighted

### 5b. Absorption Wave Intersection
- Finding x Absorption ADR matrix (ADDRESS / COMPLICATE / NEUTRAL)
- COMPLICATE items called out with risk assessment

### 5c. Coverage Gaps
- Findings with gap_flag: TRUE
- Recommended action for each (new pool ADR, scope expansion, or accept risk)

## 6. Red-Team Results
- Challenge x Result matrix (BLOCKED / WARNED / PASSED)
- Narrative for each PASSED result (the bypass path that worked)

## 7. Actionable Outcomes
### 7a. Category A -- Immediate Infrastructure Hardening
- Table: recommendation, finding(s), scope (files changed), severity
- These require no ADR. Implement before next ADR/OBPI cycle.

### 7b. Category B -- ADR Sequencing Guidance
- Recommended absorption-wave priority order with justification
- Which ADRs have highest governance-chain ADDRESS density?
- Comparison to current plan order (if any)

### 7c. Category C -- New Architectural Intent
- Table: finding, gap status, recommended action (accept risk / expand scope / new pool entry)
- For "expand scope": which existing ADR absorbs it and what changes
- For "new pool entry": proposed title and one-line scope

## 8. Next Actions
- Specific Category A items approved for immediate implementation
- Category B reordering decisions (accepted / deferred / modified)
- Category C decisions (per finding: accept / expand / create)
- Date for next evaluation (if recurring)
```

### Evidence Standards

- Every score must cite a specific file path and line number, CLI command, or hook name
- "Works because the skill says so" is not sufficient evidence for a score of 3
- Red-team challenges that result in PASSED must include the exact command sequence that bypassed enforcement
- Coverage assessments must quote the relevant pool ADR scope statement or absorption OBPI objective

### Versioning

- Each evaluation is dated and tied to a specific git commit SHA
- Re-evaluations after remediation reference the prior report and note which findings changed
- The systemic findings registry (S-IDs) is stable across evaluations -- new findings get new IDs, resolved findings are marked RESOLVED with the commit that fixed them

### Delivery

The completed report is written to `docs/design/evaluations/` with the naming convention:

```
governance-chain-evaluation-report-YYYY-MM-DD.md
```

The framework document (this file) is not modified by individual evaluations. If the framework itself needs updating (new dimensions, revised scoring), that is a separate change with its own review.

---

## Appendix A: Chain Link Skill Inventory

### Link 1: ADR/OBPI Authoring

| Skill | Role in chain |
|-------|--------------|
| `gz-design` | Upstream entry: design dialogue, overlap detection, approach selection |
| `gz-adr-create` | ADR file creation with mandatory interview (Step 0), OBPI co-creation (Step 10) |
| `gz-adr-evaluate` | Post-authoring quality scoring (8 dimensions), red-team challenges, GO/NO-GO verdict |
| `gz-obpi-specify` | OBPI brief decomposition with semantic authoring and authored-readiness validation |

### Link 2: OBPI Pipeline Execution

| Skill | Role in chain |
|-------|--------------|
| `gz-plan-audit` | Pre-flight alignment: ADR intent vs OBPI brief vs plan |
| `gz-obpi-pipeline` | 5-stage execution: load context, implement, verify, present evidence, sync+account |
| `gz-obpi-lock` | Multi-agent coordination: claim/release work locks |
| `gz-obpi-simplify` | Post-implementation code review scoped to brief's Allowed Paths |

### Link 3: OBPI Outcomes Verification/Audit

| Skill | Role in chain |
|-------|--------------|
| `gz-obpi-reconcile` | 4-phase reconciliation: audit evidence, fix briefs, sync ADR table, report |
| `gz-adr-audit` | Gate 5 audit: ledger completeness, value demonstration, validation receipt |
| `gz-gates` | Lane-appropriate gate execution |
| `gz-implement` | Gate 2 verification and result recording |

### Link 4: ADR/OBPI Closeout Ceremony

| Skill | Role in chain |
|-------|--------------|
| `gz-adr-closeout-ceremony` | Human-witnessed ceremony: passive presenter, runbook walkthrough, attestation |
| `gz closeout` (CLI) | Atomic operation: quality gates + attestation + version bump |
| `gz attest` (CLI) | Attestation recording with prerequisite validation |
| `gz audit` (CLI) | Post-attestation validation and lifecycle transition |

### T1 Hooks Relevant to the Chain

| Hook | Chain links | Enforcement |
|------|-------------|-------------|
| `plan-audit-gate.py` | 1→2 handoff | Blocks ExitPlanMode without valid plan-audit receipt |
| `pipeline-gate.py` | 2 | Blocks src/tests writes without active pipeline |
| `obpi-completion-validator.py` | 2→3 handoff | Blocks brief completion without evidence + attestation |
| `ledger-writer.py` | 2, 3 | Records governance artifact edits; conditional block |
| `post-edit-ruff.py` | 2 | Auto-formats Python; removes unused imports |
| `session-staleness-check.py` | 2 | Advisory: warns about stale pipeline markers |
| `pipeline-completion-reminder.py` | 2→3 | Advisory: warns before commit with incomplete pipeline |
| `pipeline-router.py` | 1→2 | Routes agent to pipeline after plan approval |
| `instruction-router.py` | 2 | Surfaces relevant constraints during edits |
| `control-surface-sync.py` | all | Auto-syncs control surfaces after governance file edits |

## Appendix B: Systemic Findings Reference (Baseline)

The following findings were identified in the initial evaluation (2026-04-04). They serve as the starting registry for subsequent evaluations.

### S1: No Hard Gate Between Authoring Quality and Lifecycle Progression

- **Severity:** High
- **Chain links:** 1→2
- **Current tier:** T2
- **Target tier:** T1
- **Description:** `gz-adr-evaluate` produces a GO/CONDITIONAL-GO/NO-GO verdict, but no hook blocks ADR state progression on a NO-GO score. An agent could produce a thin ADR with shallow interview answers and proceed to implementation.
- **Pool coverage:** `agent-reliability-framework` (DIRECT), `skill-behavioral-hardening` (PARTIAL), `constraint-library` (TANGENTIAL)
- **Absorption coverage:** ADR-0.34.0 OBPIs 01/07/08 (ADDRESS), ADR-0.25.0-12 admission-pattern (ADDRESS), ADR-0.26.0-04 adr-governance (ADDRESS)
- **Gap flag:** FALSE (covered by agent-reliability-framework)

### S2: Content-Type Blind Spot in Pipeline Enforcement

- **Severity:** High
- **Chain links:** 2
- **Current tier:** Gap
- **Target tier:** T1
- **Description:** `pipeline-gate.py` only gates writes to `src/` and `tests/`. Documentation, configuration, governance artifacts, and other non-code files can be edited without pipeline activation. Doc-only or config-only OBPIs have zero pipeline enforcement.
- **Pool coverage:** None
- **Absorption coverage:** ADR-0.34.0-11 dataset-guard (ADDRESS), ADR-0.35.0-09/17 markdown hooks (ADDRESS), ADR-0.34.0-05 post-edit-ruff (COMPLICATE -- reinforces Python-only pattern)
- **Gap flag:** TRUE (no pool ADR carries intent for content-type-aware pipeline enforcement)

### S3: Allowed Paths Constraint Is Decoration

- **Severity:** Medium
- **Chain links:** 2, 3
- **Current tier:** Gap
- **Target tier:** T1
- **Description:** OBPI briefs declare Allowed/Denied Paths but no hook checks whether file edits fall within the declared scope. The pipeline gate checks that the pipeline is *active*, not that the file is *in scope*.
- **Pool coverage:** `agent-reliability-framework` (DIRECT -- AR2 requires scope-checked output), `constitution-invariants` (TANGENTIAL)
- **Absorption coverage:** ADR-0.25.0-12 admission-pattern (ADDRESS), ADR-0.35.0-07 protect-copilot-instructions (ADDRESS), ADR-0.38.0-10 guards-layout-verify (ADDRESS), ADR-0.39.0-04/05 conformance/contradiction (ADDRESS)
- **Gap flag:** FALSE (covered by agent-reliability-framework)

### S4: Reconcile Auto-Promotion on Heuristic Evidence

- **Severity:** Medium
- **Chain links:** 3
- **Current tier:** T2
- **Target tier:** T1
- **Description:** `gz-obpi-reconcile` Phase 2 auto-marks briefs Completed if grep-based `@covers` tag detection and test results pass. A false positive in evidence detection could promote a brief incorrectly, and downstream audit trusts the ledger proof.
- **Pool coverage:** `agent-reliability-framework` (PARTIAL), `adr-amendment-tracking` (TANGENTIAL)
- **Absorption coverage:** ADR-0.27.0 OBPIs 03/05/11/12 ARB receipts (ADDRESS), ADR-0.26.0-08 validation-receipt (ADDRESS), ADR-0.26.0-07 adr-traceability (ADDRESS), ADR-0.32.0-17 autolink-sync (ADDRESS), ADR-0.26.0-03 adr-recon (COMPLICATE -- may entrench grep patterns)
- **Gap flag:** FALSE (strong absorption coverage)

### S5: Product Proof Gate Is Feature-Flagged

- **Severity:** Medium
- **Chain links:** 4
- **Current tier:** T1 (conditional)
- **Target tier:** T1 (unconditional)
- **Description:** `check_product_proof()` in closeout is gated by `FeatureDecisions.product_proof_enforced()`. When the flag is off, missing runbook/manpage/docstring coverage is advisory only at closeout.
- **Pool coverage:** None
- **Absorption coverage:** ADR-0.35.0 OBPIs 13/14/15 pre-commit hooks (ADDRESS), ADR-0.31.0-08/10 validate-manpages/interrogate (ADDRESS), ADR-0.30.0-02 config-doctrine (COMPLICATE -- may normalize feature-flagged gates)
- **Gap flag:** TRUE (no pool ADR carries intent for unconditional product proof enforcement)

### S6: --force Attestation Has No Quality Bar

- **Severity:** Medium
- **Chain links:** 4
- **Current tier:** T3
- **Target tier:** T1 or T2
- **Description:** `gz attest --force --reason "..."` bypasses prerequisite gates with a free-text reason. No minimum quality standard on the reason, no secondary approval, no audit trail distinction between forced and normal attestation.
- **Pool coverage:** `agent-reliability-framework` (DIRECT -- AR3 defines attestation quality requirements), `attestation-advisory-agent` (PARTIAL), `graduated-oversight-model` (PARTIAL)
- **Absorption coverage:** ADR-0.25.0-01 attestation-pattern (ADDRESS), ADR-0.26.0-04 adr-governance (ADDRESS), ADR-0.32.0-11/13 closeout/attest comparison (ADDRESS)
- **Gap flag:** FALSE (covered by agent-reliability-framework)

### S7: Self-Close Exception Defers Review

- **Severity:** Medium
- **Chain links:** 2→4
- **Current tier:** T2→T3
- **Target tier:** T2 with proportional review
- **Description:** OBPIs that use exception-mode self-close accumulate without human review until the ADR closeout ceremony. If many OBPIs self-close, the ceremony carries a large batch verification burden.
- **Pool coverage:** `graduated-oversight-model` (DIRECT -- Standard tier adds spot-check sampling), `channel-agnostic-human-triggers` (TANGENTIAL)
- **Absorption coverage:** ADR-0.34.0-01 obpi-completion-validator (ADDRESS), ADR-0.32.0-11 closeout comparison (ADDRESS)
- **Gap flag:** FALSE (covered by graduated-oversight-model)

### S8: Lane Classification Is Write-Once

- **Severity:** Low
- **Chain links:** 1→all
- **Current tier:** T3
- **Target tier:** T2
- **Description:** Lane (lite/heavy/foundation) is set at `adr_created` event time and never re-validated. A lite ADR whose scope evolves to touch CLI contracts remains lite unless manually corrected.
- **Pool coverage:** `heavy-lane` (PARTIAL -- addresses detection/enforcement but not reclassification)
- **Absorption coverage:** ADR-0.26.0-04 adr-governance (ADDRESS), ADR-0.25.0-08 ledger-pattern (COMPLICATE -- may further entrench write-once)
- **Gap flag:** FALSE (weakly covered, but heavy-lane pool ADR exists)

### S9: Run-to-Completion Is Narrative-Only

- **Severity:** Low
- **Chain links:** 2
- **Current tier:** T2
- **Target tier:** T1
- **Description:** The pipeline's "Iron Law" (run all 5 stages to completion) has no mechanical backstop. An agent can stop after Stage 2 or 3. The skill acknowledges this as the most common failure mode.
- **Pool coverage:** `skill-behavioral-hardening` (DIRECT), `agent-reliability-framework` (DIRECT), `structured-blocker-envelopes` (PARTIAL)
- **Absorption coverage:** ADR-0.34.0 OBPIs 06/08 pipeline-router/pipeline-gate (ADDRESS), ADR-0.32.0-09 gates comparison (ADDRESS), ADR-0.37.0-10 architectural-enforcement (COMPLICATE -- may describe enforcement without implementing it)
- **Gap flag:** FALSE (well-covered)

### S10: Interview Artifact Persistence Unchecked

- **Severity:** Low
- **Chain links:** 1
- **Current tier:** T3
- **Target tier:** T2
- **Description:** The structured interview is mandatory in `gz-adr-create` Step 0, but no gate verifies the interview JSON artifact was actually saved alongside the ADR. The artifact could be lost without detection.
- **Pool coverage:** None
- **Absorption coverage:** None
- **Gap flag:** TRUE (no architectural intent exists for interview artifact lifecycle governance)
