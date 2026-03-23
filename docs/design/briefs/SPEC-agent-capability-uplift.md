# SPEC: Agent Capability Uplift

**Date:** 2026-03-23
**Status:** Draft
**Purpose:** Capability matrix and prioritized spec for absorbing best practices from superpowers, spec-kit, and GSD into gzkit natively.

**Effort legend:** Low = 1-2 OBPIs. Medium = 3-5 OBPIs. High = 6+ OBPIs.

---

## 1. Problem Statement

gzkit's execution pipeline (5-stage, subagent-dispatched, gate-enforced) is mature and ahead of comparable tools. But three areas lose value:

1. **Pre-pipeline:** Work starts before intent is fully explored. ADRs and OBPI briefs are created without structured design exploration, ambiguity resolution, or decision locking. Requirements enter the pipeline under-examined.
2. **In-pipeline:** Agents make avoidable mistakes during execution. No per-task verification, no stall detection, no graduated deviation handling, no context budget awareness. Quality gates run post-batch rather than per-task.
3. **Cross-cutting:** Agent orientation is slow after session boundaries. No systematic user adaptation. No standalone TDD, debugging, or code review disciplines outside the pipeline. Requirements traceability is manual.

## 2. Competitive Analysis Sources

| Tool | Philosophy | Strongest Differentiators vs gzkit |
|---|---|---|
| **superpowers** (obra) | Methodology layer — TDD discipline, anti-rationalization, evidence-before-claims | Brainstorming gate, universal anti-rationalization tables, 5-step evidence protocol, systematic debugging, standalone code review |
| **spec-kit** (GitHub) | Specification engine — specs govern code, not reverse | Ambiguity markers with resolution enforcement, cross-artifact consistency analysis, constitution-as-executable-gate, specification quality checklist |
| **GSD** (gsd-build) | Execution orchestrator — context-fresh parallel waves | Decision locking (D-01/D-02), task-level `<verify>`, 4-level artifact verification, plan-checker adversarial loop, user profiling, context budget discipline, analysis paralysis guard |

## 3. Capability Matrix

### 3.1 Pre-Pipeline: Intent Capture and ADR Quality

These capabilities enrich `gz-adr-create` and `gz-plan` — the ADR is the design exploration artifact.

#### CAP-01: Structured Design Exploration in ADR Creation

**Source:** superpowers (brainstorming), GSD (discuss phase)
**Gap:** gzkit jumps from PRD to ADR without structured design exploration. No approach comparison, no section-by-section approval, no spec review loop.
**Proposed change:** Enrich `gz-adr-create` with a structured design exploration phase, leveraging existing `gz-interview` for the questioning stage:
- Context scan (~10% context budget) before any design decisions
- `gz-interview` conducts domain-adaptive clarification (one question at a time, multiple-choice preferred)
- 2-3 approach exploration with trade-offs and recommendation
- Section-by-section design presentation with incremental approval
- Adversarial spec review (subagent, max 3 iterations) before ADR is finalized
**Relationship to existing skills:** `gz-interview` provides the questioning engine. `gz-specify` generates OBPI briefs from the ADR. This capability enriches the ADR creation step between them — not a new artifact layer.
**Pool ADR:** Subsumes `ADR-pool.pre-planning-interview` (structured questioning aspect).
**GovZero fit:** The ADR remains the artifact. This improves its input quality. No new artifact type.
**Priority:** P1 — directly improves every downstream OBPI brief.

#### CAP-02: Decision Locking with Formal IDs

**Source:** GSD (discuss phase)
**Gap:** Decisions are implicit in ADR/brief prose. No formal IDs. No downstream enforcement. No explicit `locked` / `discretion` / `deferred` classification.
**Proposed change:**
- ADR decisions get formal IDs (D-01, D-02) with status: `locked`, `discretion`, `deferred`
- Locked decisions become hard constraints in OBPI briefs (referenced by ID)
- Deferred decisions explicitly forbidden from plans
- `gz-plan-audit` validates that every locked decision has a corresponding task
- Pipeline implementers reference decision IDs in commit messages
**Schema sketch:** Decisions are captured in the ADR markdown under a `## Decisions` section:
```markdown
## Decisions

| ID | Decision | Status | Rationale |
|---|---|---|---|
| D-01 | Use structlog for logging | locked | Consistency with existing infrastructure |
| D-02 | Logging format (JSON vs text) | discretion | Agent chooses based on context |
| D-03 | Centralized log aggregation | deferred | Future ADR scope |
```
Decision status is ADR-local metadata (not a ledger event). OBPI briefs reference locked decisions by ID in their constraints section. `gz-plan-audit` parses the ADR's decision table to validate downstream coverage.
**Pool ADR:** Complements `ADR-pool.spec-delta-markers` (delta markers make decision drift visible).
**GovZero fit:** Strengthens the ADR → OBPI traceability chain. Decision IDs are governance metadata.
**Priority:** P1 — prevents scope creep and intent drift across the ADR-to-implementation span.

#### CAP-03: Ambiguity Resolution Protocol

**Source:** spec-kit (clarify command), GSD (gray area surfacing)
**Gap:** Ambiguities hide in ADR/brief prose. No structured markers, no resolution enforcement, no taxonomy.
**Proposed change:**
- `[NEEDS CLARIFICATION]` markers in ADR and OBPI brief templates
- Maximum 3 unresolved markers allowed before brief can enter pipeline
- Domain-adaptive gray area surfacing during `gz-interview` (concrete questions, not generic categories)
- Resolved markers converted to locked decisions (D-xx)
**GovZero fit:** Fail-closed — unresolved ambiguity blocks pipeline entry. Consistent with gate philosophy.
**Priority:** P2 — high value but requires template changes across ADR and OBPI brief formats.

#### CAP-04: Specification Quality Validation

**Source:** spec-kit (checklist + analyze commands)
**Gap:** `gz validate` checks schema validity, not requirements quality. No completeness/clarity/consistency scoring. No cross-artifact conflict detection.
**Proposed change:**
- `gz validate --requirements` mode that checks:
  - Every OBPI brief requirement is independently testable
  - No duplicate or conflicting requirements across sibling OBPIs
  - Acceptance criteria are measurable (not subjective)
  - Evidence sections reference actual verification commands
- Severity classification: CRITICAL / HIGH / MEDIUM / LOW
- Constitution alignment check (see CAP-12)
**Validation mechanism:** This is LLM-assessed (advisory), not rule-based (enforceable). The checks require semantic judgment ("is this requirement independently testable?") that cannot be reduced to regex or AST rules. Therefore this belongs in a skill (`gz-spec-quality`), not in `gz validate`. The skill produces a quality report with findings; it does not gate pipeline entry. Rule-based checks (duplicate REQ IDs, missing evidence commands) can be added to `gz validate` separately.
**GovZero fit:** Advisory skill, not a fail-closed gate. Complements schema-driven `gz validate`.
**Priority:** P2 — substantial but builds on existing validation infrastructure.

#### CAP-05: Plan-Audit Adversarial Loop

**Source:** GSD (plan-checker), superpowers (spec review loop)
**Gap:** `gz-plan-audit` is single-pass. No iteration, no dimension-specific fixes, no blocker/warning classification.
**Proposed change:**
- `gz-plan-audit` gains iterative mode (max 3 passes)
- 10 verification dimensions (adapted from GSD): requirement coverage, task completeness, dependency correctness, wiring coverage, scope sanity, verification derivation, decision compliance, test coverage (Nyquist), cross-plan conflicts, constitution alignment
- Issues classified as Blocker (must fix) / Warning (should fix) / Info (suggestion)
- Surgical revision guidance per dimension (not full replan)
- Blockers prevent pipeline entry
**GovZero fit:** Tightens the existing plan-audit gate. Same artifact, deeper check.
**Priority:** P1 — directly prevents plans with gaps from entering execution.

---

### 3.2 In-Pipeline: Execution Intelligence

These capabilities enhance `gz-obpi-pipeline` stages 2 and 3.

#### CAP-06: Per-Task Verification Stanzas

**Source:** GSD (XML task format with `<verify>` and `<done>`)
**Gap:** Plans lack per-task verification commands. Gates run post-batch (Stage 3), not per-task (Stage 2). Failures are caught late.
**Proposed change:**
- Plans produced by `gz-plan` include `verify:` and `done:` fields per task
- Pipeline Stage 2 runs verification after each implementer subtask completes
- Nyquist Rule: if a task has no verification command, a prerequisite task creating the test must exist
- Verification failure triggers fix cycle (existing max-2 bound) before advancing
**GovZero fit:** Tightens the feedback loop within existing Stage 2. No new stage.
**Priority:** P1 — catches failures per-task instead of post-batch. Direct quality improvement.

#### CAP-07: Universal Evidence Protocol

**Source:** superpowers (verification-before-completion)
**Gap:** Evidence requirements exist in the pipeline but are not formalized as a universal protocol. Other skills (chore-runner, debugging, standalone review) lack equivalent rigor.
**Proposed change:**
- Formalize the evidence discipline that ARB already provides (`gz-arb` wraps commands, checks exit codes, produces JSON receipts) as a universal skill section template:
  1. Identify the command that proves the assertion
  2. Execute fresh (not cached) — use `gz-arb` when receipt is needed
  3. Read full output and check exit code
  4. Verify output matches the claimed result
  5. THEN make the claim
- **What's new vs ARB:** ARB handles the execution/receipt layer. This CAP adds the *discipline protocol* — the 5-step sequence that prevents claims without evidence — as a standard section in every governance skill. ARB is the mechanism; this is the mandate.
- Weasel-word detection: "should," "probably," "likely" in completion claims trigger re-verification
- Template provided for skill authors to include in new skills
**Pool ADR:** Aligns with `ADR-pool.skill-behavioral-hardening` (evidence discipline as skill enrichment).
**GovZero fit:** Extends ARB receipt philosophy to all skills. Evidence-first is already core GovZero.
**Priority:** P1 — universal application of an existing principle.

#### CAP-08: Graduated Deviation Rules

**Source:** GSD (executor deviation rules)
**Gap:** Implementer agent has binary lane compliance — in-lane or breach. No gradient between "auto-fix a typo" and "restructure the module."
**Proposed change:**
- Four-tier deviation model for implementer agents:
  - **Tier 1 — Auto-fix:** Bugs, type errors, missing validation, broken imports. Fix and note in commit message.
  - **Tier 2 — Note and continue:** Style improvements, minor refactors within file scope. Fix, log finding, continue.
  - **Tier 3 — Pause and ask:** Scope changes, new dependencies, file additions outside allowed paths. Escalate to orchestrator.
  - **Tier 4 — Hard stop:** Architectural changes, schema changes, security decisions. Abort task, create handoff.
- Tier classification rules embedded in implementer agent prompt
- Tier 3/4 events recorded in pipeline marker for audit trail
**Pool ADR:** Complements `ADR-pool.graduated-oversight-model` (oversight at ADR level) and `ADR-pool.controlled-agency-recovery` (agent autonomy boundaries). This CAP operates at task level; those pool ADRs operate at ADR/OBPI level. They compose — oversight model determines which ADRs get which tier defaults.
**GovZero fit:** Compatible with lane system. Tiers 1-2 stay within lane. Tiers 3-4 trigger existing escalation paths.
**Priority:** P2 — improves agent autonomy for safe deviations while maintaining governance.

#### CAP-09: Goal-Backward Verification

**Source:** GSD (verifier agent)
**Gap:** Stage 3 verification checks pass/fail of gates. Does not assess whether artifacts are substantive, wired, or receiving real data. A stub file that passes lint is "verified."
**Proposed change:**
- Stage 3 verification subagents gain 4-level artifact assessment:
  - **Level 1 — Exists:** File present at expected path
  - **Level 2 — Substantive:** Not a stub (detect TODO/FIXME, placeholder text, empty returns, functions <5 lines for complex tasks)
  - **Level 3 — Wired:** Imported and used by other modules (grep for import statements)
  - **Level 4 — Data flows:** Dynamic data actually passes through (not hardcoded empty values)
- Artifact assessment matrix included in Stage 4 evidence presentation
- Levels 1-2 are automated (grep-based). Levels 3-4 are automated where possible, flagged for human review otherwise.
- VERIFIED / ORPHANED / HOLLOW / STUB / MISSING classification per artifact
**GovZero fit:** Deepens existing verification without changing gate structure. Evidence quality improvement.
**Priority:** P2 — meaningful but requires new verification logic in subagents.

#### CAP-10: Analysis Paralysis Guard

**Source:** GSD (executor agent)
**Gap:** Implementer agents can spin on reads without writing. No detection or forced decision.
**Proposed change:**
- Implementer agent prompt includes stall detection rule:
  - N consecutive Read/Grep/Glob calls (configurable, default 5) without any Edit/Write/Bash action → forced checkpoint
  - Agent must: state in one sentence why no code has been written, then either write code or declare a specific blocker
  - Blocker declaration triggers Tier 3 escalation (CAP-08)
- Stall events recorded in pipeline marker
**GovZero fit:** Operational hygiene. No governance impact.
**Priority:** P3 — useful but lower impact than per-task verification or evidence protocol.

#### CAP-11: Context Budget Annotations

**Source:** GSD (context engineering), Claude best practices
**Gap:** Plans have no context cost estimates. No budget tracking during execution. No compaction awareness.
**Proposed change:**
- Plans include advisory context cost per task (light/medium/heavy annotation based on file count and estimated complexity — not token-counted, since no token counting API exists in Claude Code agent dispatch)
- AGENTS.md gains compaction-awareness guidance: save progress to handoff before context limits, don't stop tasks early, save state before compaction
- Interface extraction: plans include key interface signatures in task context blocks to reduce redundant codebase exploration by implementers
**Limitation:** Context budget tracking is advisory, not enforced. There is no programmatic way to measure token consumption during a Claude Code session. The annotations guide human and agent judgment but cannot gate execution.
**Pool ADR:** Complements `ADR-pool.progressive-context-disclosure` (context tier system) and `ADR-pool.focused-context-loader` (per-ADR context payloads).
**GovZero fit:** Operational efficiency. No governance artifact changes.
**Priority:** P3 — important for long sessions but not a governance gap.

---

### 3.3 Cross-Cutting: Orientation, Discipline, Adaptation

Capabilities that span the agent lifecycle.

#### CAP-12: Constitution as Executable Gate

**Source:** spec-kit (constitutional articles)
**Gap:** gzkit's constitution exists as a reference document but isn't checked programmatically during planning. Violations are caught by human review, not automated gates.
**Proposed change:**
- Constitution principles are encoded as machine-checkable rules (not just prose)
- `gz-plan-audit` checks plan against constitution principles (in addition to brief alignment)
- Constitution violations are automatic CRITICAL severity in the plan-audit loop (CAP-05)
- `gz validate --constitution` mode for standalone checking
**Pool ADR:** Subsumes `ADR-pool.constitution-invariants` (which proposes `gz constitute` and optional `gz check --constitution`). This CAP extends that pool ADR by making constitution checks a mandatory input to `gz-plan-audit`, not just a standalone command.
**GovZero fit:** Constitution already exists in governance hierarchy. This makes it enforceable, not just advisory.
**Priority:** P2 — requires encoding constitutional principles as rules, which is design work.

#### CAP-13: Session-Start Orientation Protocol

**Source:** superpowers (session-start hook), GSD (state loading)
**Gap:** Agent orientation is honor-system ("read AGENTS.md before starting work"). No automated state synthesis. No hook enforcement.
**Proposed change:**
- `gz status --orientation` command that produces a compact orientation document:
  - Active ADRs and their pipeline state
  - Active OBPI locks (who's working on what)
  - Recent ledger events (last 24h)
  - Unresolved blockers
  - Current session's pipeline markers
- Optional session-start hook that runs `gz status --orientation` and injects output as context
- Orientation document is ephemeral (not persisted) — generated from authoritative sources on demand
**Pool ADR:** Subsumes `ADR-pool.universal-agent-onboarding` (`gz onboard` command). This CAP proposes `gz status --orientation` as the implementation vehicle — a subcommand of existing `gz status` rather than a new top-level command. The pool ADR's `--vendor` and `--resume` flags remain valid extensions.
**GovZero fit:** No new persistent state. Derived from existing ledger/status infrastructure.
**Priority:** P1 — directly reduces wasted tokens on orientation across every session.

#### CAP-14: Operator Profile

**Source:** GSD (user profiler, 8 dimensions)
**Gap:** Memory captures individual feedback rules but no systematic profile. Agent behavior isn't adaptive to operator characteristics.
**Proposed change:**
- Lightweight profile in `memory/user_profile.md` with 4 dimensions:
  - **Communication style:** terse / conversational / detailed (affects explanation depth)
  - **Decision speed:** fast-intuitive / deliberate / research-first (affects how many options to present)
  - **Domain expertise:** per-domain ratings (affects assumed knowledge in explanations)
  - **Frustration triggers:** specific patterns to avoid (populated from feedback memories)
- Skills consult profile when choosing response verbosity, option count, and explanation depth
- Profile is user-reviewable and editable (not hidden)
- Auto-populated from existing feedback memories on first creation (e.g., `no-double-print`, `no-raw-json`, `just-run-skills` already capture communication style preferences)
**GovZero fit:** Memory-based, user-controlled. No governance artifact.
**Priority:** P3 — nice-to-have. Existing feedback memories cover most cases.

#### CAP-15: Native TDD Skill

**Source:** superpowers (test-driven-development)
**Gap:** Test policy exists in `.claude/rules/tests.md`. TDD is mandated in implementer agent. But no standalone TDD skill with enforcement rigor, rationalization prevention, or red-green-refactor cycle management.
**Proposed change:**
- Native `gz-tdd` skill absorbing superpowers' discipline:
  - Strict RED → GREEN → REFACTOR cycle
  - One behavior per test, descriptive naming
  - Anti-rationalization table (common invalid excuses for skipping tests)
  - Red flags requiring restart: code preceding tests, tests passing on first run without implementation
  - Integration with `gz-arb` for test receipt generation
- Applies to all work (pipeline and ad-hoc), not just pipeline Stage 2
- Replaces current thin `test` skill
**Pool ADR:** Subsumed by `ADR-pool.skill-behavioral-hardening` (test skill rewrite is explicitly scoped there).
**GovZero fit:** Strengthens Gate 2. Test evidence is already governance-required.
**Priority:** P2 — the test policy rule provides baseline; this adds enforcement depth.

#### CAP-16: Native Systematic Debugging Skill

**Source:** superpowers (systematic-debugging)
**Gap:** Error recovery paths documented in pipeline. No systematic debugging methodology for ad-hoc or diagnostic work.
**Proposed change:**
- Native `gz-debug` skill with 4-phase workflow:
  1. **Root cause investigation** — reproduce the failure, trace data flow backward, NO fixes without root cause
  2. **Pattern analysis** — locate similar working code, compare differences, check recent changes
  3. **Hypothesis and testing** — form hypothesis, design minimal test, verify
  4. **Implementation** — fix with evidence, verify fix, verify no regression
- Anti-rationalization: "If 3+ fixes fail, question the architecture, not the patches"
- Integration with `gz-arb` for diagnostic receipt generation
**Pool ADR:** Subsumed by `ADR-pool.skill-behavioral-hardening` (`gz-debug` is explicitly scoped there).
**GovZero fit:** Produces evidence artifacts. Compatible with defect tracking requirement.
**Priority:** P2 — fills a real gap for non-pipeline diagnostic work.

#### CAP-17: Standalone Code Review Skills

**Source:** superpowers (requesting-code-review, receiving-code-review)
**Gap:** Code review is embedded in pipeline Stage 2. No standalone review for PR work, ad-hoc changes, or work done outside the pipeline.
**Proposed change:**
- `gz-review-request` skill: dispatch spec + quality reviewer subagents on any code change (not just pipeline tasks). Produce structured findings with severity (Critical/Important/Suggestion).
- `gz-review-receive` skill: when receiving review feedback, verify suggestions before implementing. Push back on suggestions that break functionality, violate YAGNI, or contradict architecture. "Actions speak — just fix it" over performative agreement.
- Both skills integrate with existing spec-reviewer and quality-reviewer agents
- Findings produce `gz-arb` receipts for audit trail
**Pool ADR:** Subsumed by `ADR-pool.skill-behavioral-hardening` (`gz-review-response` is explicitly scoped there).
**GovZero fit:** Extends existing reviewer agents to new contexts. Evidence-producing.
**Priority:** P2 — valuable for PR workflows and ad-hoc governance.

#### CAP-18: Requirements Traceability

**Source:** spec-kit (cross-artifact consistency)
**Gap:** OBPI requirements exist but no automated REQ → code → test mapping. Gap detection is manual.
**Proposed change:**
- Extend `gz-adr-autolink` to map REQ IDs in OBPI briefs to:
  - `@covers` decorators in test files
  - Implementation modules referenced in brief's allowed-paths
- `gz validate --traceability` surfaces unlinked requirements (REQs with no test coverage, tests with no REQ reference)
- Gap report included in Stage 4 evidence presentation
**Prerequisite:** The `@covers` decorator convention must be established and existing tests migrated. This is already scoped in `ADR-pool.tests-for-spec` (promoted to ADR-0.21.0). CAP-18 depends on that ADR's completion.
**Pool ADR:** Extends ADR-0.21.0 (tests-for-spec) with cross-brief conflict detection. The traceability infrastructure comes from that ADR; this CAP adds the validation surface.
**GovZero fit:** Extends existing autolink infrastructure. Strengthens the evidence chain.
**Priority:** P3 — valuable but depends on ADR-0.21.0 completion and consistent REQ ID usage across briefs.

#### CAP-19: Anti-Rationalization Standard Section

**Source:** superpowers (embedded in every skill)
**Gap:** Pipeline skill has one anti-rationalization table. Other skills have none. Agents can rationalize shortcuts outside the pipeline.
**Proposed change:**
- Standard skill template section: `## Invalid Excuses` with common rationalizations for that skill's domain
- Required in every skill that involves completion claims or quality assertions
- Template with domain-specific examples provided for skill authors
- `gz-adr-eval` checks for presence of anti-rationalization section in skills it scores
**GovZero fit:** Discipline infrastructure. No governance artifact changes.
**Priority:** P2 — low effort, high leverage across all skills.

---

## 4. Priority Summary

### P1 — Direct quality improvement, low structural risk

| ID | Capability | Source | Effort |
|---|---|---|---|
| CAP-01 | Structured design exploration in ADR creation | superpowers + GSD | Medium |
| CAP-02 | Decision locking with formal IDs | GSD | Medium |
| CAP-05 | Plan-audit adversarial loop | GSD + superpowers | Medium |
| CAP-06 | Per-task verification stanzas | GSD | Low |
| CAP-07 | Universal evidence protocol | superpowers | Low |
| CAP-13 | Session-start orientation protocol | superpowers + GSD | Low |

### P2 — Meaningful uplift, requires more design

| ID | Capability | Source | Effort |
|---|---|---|---|
| CAP-03 | Ambiguity resolution protocol | spec-kit + GSD | Medium |
| CAP-04 | Specification quality validation | spec-kit | High |
| CAP-08 | Graduated deviation rules | GSD | Low |
| CAP-09 | Goal-backward verification | GSD | Medium |
| CAP-12 | Constitution as executable gate | spec-kit | High |
| CAP-15 | Native TDD skill | superpowers | Medium |
| CAP-16 | Native systematic debugging skill | superpowers | Medium |
| CAP-17 | Standalone code review skills | superpowers | Medium |
| CAP-19 | Anti-rationalization standard section | superpowers | Low |

### P3 — Operational hygiene, lower urgency

| ID | Capability | Source | Effort |
|---|---|---|---|
| CAP-10 | Analysis paralysis guard | GSD | Low |
| CAP-11 | Context budget annotations | GSD + Claude best practices | Medium |
| CAP-14 | Operator profile | GSD | Medium |
| CAP-18 | Requirements traceability | spec-kit | Medium |

---

## 5. ADR Packaging Guidance

This spec is designed to map to ADRs. Suggested boundaries:

**ADR candidate A: Pre-Pipeline Intelligence**
CAP-01 + CAP-02 + CAP-03 + CAP-05
*Enriches ADR creation and plan quality. All changes target gz-adr-create, gz-plan, gz-plan-audit, and gz-interview.*
Subsumes pool ADRs: `pre-planning-interview`. Complements: `spec-delta-markers`.

**ADR candidate B1: Per-Task Verification and Evidence Protocol**
CAP-06 + CAP-07
*Tightens the execution feedback loop. Both P1, both low effort, tightly coupled — verification stanzas need the evidence protocol to be meaningful.*
Complements pool ADR: `task-level-governance` (ADR-0.22.0, already promoted).

**ADR candidate B2: Agent Execution Intelligence**
CAP-08 + CAP-09 + CAP-10
*Enhances agent decision-making during execution. Mixed priority (P2/P3), moderate effort, independent of B1.*
Complements pool ADRs: `graduated-oversight-model`, `controlled-agency-recovery`.

**ADR candidate C: Skill Behavioral Hardening** (extends existing pool ADR)
CAP-15 + CAP-16 + CAP-17 + CAP-19
*Native skills for TDD, debugging, code review, and anti-rationalization. New skills, no existing skill modification.*
Subsumes pool ADR: `skill-behavioral-hardening` (this spec adds competitive analysis context and concrete source attribution that the pool ADR lacks).

**ADR candidate D: Orientation and Adaptation**
CAP-13 + CAP-14 + CAP-11
*Session-start protocol, operator profile, context budget. Changes to AGENTS.md, gz-status, memory system.*
Subsumes pool ADR: `universal-agent-onboarding`. Complements: `focused-context-loader`, `progressive-context-disclosure`.

**ADR candidate E1: Constitution as Executable Gate**
CAP-12
*Machine-checkable constitutional principles integrated into gz-plan-audit.*
Subsumes pool ADR: `constitution-invariants`.

**ADR candidate E2: Specification Quality and Traceability**
CAP-04 + CAP-18
*Advisory quality analysis + requirements traceability. CAP-18 depends on ADR-0.21.0 (tests-for-spec) completion.*
Complements pool ADR: ADR-0.21.0 (tests-for-spec, already promoted).

### Dependency graph between ADR candidates

```
A (Pre-Pipeline) ─────────► B1 (Verification + Evidence)
       │                            │
       │                            ▼
       └──► CAP-05 references ► E1 (Constitution Gate)
                                    │
B2 (Execution Intelligence)         │ [independent]
       │                            │
       └── CAP-10 references ► CAP-08 (within B2)

C (Skill Hardening) ──► CAP-19 template consumed by ──► B1, B2, D

D (Orientation) [independent]

E2 (Quality + Traceability) ◄── depends on ── ADR-0.21.0 (external)
```

**Recommended execution order:** A → B1 → C → D → B2 → E1 → E2

---

## 6. Pool ADR Reconciliation

This spec overlaps with existing pool ADRs. Dispositions:

| Pool ADR | Disposition | CAP Items | Notes |
|---|---|---|---|
| `pre-planning-interview` | **Subsumed by CAP-01** | CAP-01 | CAP-01 is broader (approach exploration + spec review, not just questioning) |
| `constitution-invariants` | **Subsumed by CAP-12** | CAP-12 | CAP-12 extends it by integrating into `gz-plan-audit` loop |
| `graduated-oversight-model` | **Complements CAP-08** | CAP-08 | Pool ADR operates at ADR level; CAP-08 at task level. Both needed. |
| `universal-agent-onboarding` | **Subsumed by CAP-13** | CAP-13 | `gz status --orientation` replaces proposed `gz onboard`. Pool ADR's `--vendor`/`--resume` flags remain valid extensions. |
| `skill-behavioral-hardening` | **Subsumed by CAP-15, -16, -17, -19** | CAP-15, -16, -17, -19 | This spec adds competitive source attribution and design rationale the pool ADR lacks |
| `task-level-governance` (→ ADR-0.22.0) | **Complements CAP-06** | CAP-06 | Already promoted. CAP-06 adds per-task verify stanzas within that framework. |
| `tests-for-spec` (→ ADR-0.21.0) | **Prerequisite for CAP-18** | CAP-18 | Already promoted. CAP-18 extends with cross-brief validation surface. |
| `spec-delta-markers` | **Complements CAP-02** | CAP-02 | Delta markers make decision drift visible. Orthogonal but synergistic. |
| `controlled-agency-recovery` | **Complements CAP-08** | CAP-08 | Recovery policies and escalation complement deviation tiers. |
| `focused-context-loader` | **Complements CAP-13** | CAP-13 | Per-ADR context payload complements session-wide orientation. |
| `progressive-context-disclosure` | **Complements CAP-11, CAP-13** | CAP-11, CAP-13 | Context tier system is the architectural layer; CAPs are specific features. |
| `agent-reliability-framework` | **Overarching** | All | ARF is the meta-framework governing how all CAPs are deployed. Not subsumed; it governs. |
| `session-productivity-metrics` | **Complements CAP-14** | CAP-14 | Metrics enable profile data collection. Orthogonal. |
| `structured-blocker-envelopes` | **Complements CAP-10** | CAP-10 | Structured blockers enable stall detection escalation. |
| `evaluation-infrastructure` | **Independent** | — | Eval infrastructure is foundational but not addressed by any CAP. |

**Action required before ADR creation:** Pool ADRs marked "Subsumed" should be closed with a reference to the corresponding ADR candidate from this spec. Pool ADRs marked "Complements" remain active and may be promoted independently.

---

## 7. What Was Explicitly Not Absorbed

| Capability | Source | Reason for exclusion |
|---|---|---|
| Wave-based parallel task execution | GSD | gzkit's pipeline already parallelizes at Stage 2 (concurrent review) and Stage 3 (worktree-isolated verification). Adding wave-level parallelism would complicate the pipeline without proportional benefit. |
| 18 specialized agent types | GSD | gzkit's 5 subagent roles (implementer, spec reviewer, quality reviewer, narrator, git-sync) cover the governance pipeline. Adding researchers, profilers, and UI auditors would be scope creep without demand signal. |
| Agent-agnostic adapter layer | spec-kit | gzkit is Claude-primary (memory: 2026-03-15). Multi-agent adapters add complexity for a need that doesn't exist. |
| Full 8-dimension user profiling | GSD | Over-engineered for a governance tool. 4 dimensions (CAP-14) captures the behavioral signal that changes agent output. |
| Template-driven spec generation | spec-kit | gzkit's OBPI brief format is already structured and schema-driven. Spec-kit's template approach solves a problem gzkit doesn't have. |
| Visual companion / browser mockups | superpowers | gzkit is a CLI governance tool. Visual brainstorming is out of domain. |
| `STATE.md` as persistent cross-session state | GSD | gzkit's ledger + handoff system is architecturally superior (event-sourced, auditable). A mutable STATE.md would be a governance regression. The orientation command (CAP-13) derives equivalent value from authoritative sources. |
| Prefilled commit messages in plans | GSD | gzkit's git-sync skill handles commit conventions. Plans shouldn't dictate commit messages. |
| Stale-branch abort | GSD | gzkit's handoff system preserves work state across sessions. Aborting stale branches would discard governed work-in-progress without attestation. |
| Skill-authoring TDD | superpowers | Valuable discipline but meta-level — gzkit's skill evolution is governance-driven (pool ADR → promotion), not test-driven. Could be adopted later if skill count grows. |
| Codebase mapping agent | GSD | gzkit agents explore via Glob/Grep/Read. A dedicated mapping agent adds overhead without proportional benefit for a governance-focused tool. |

---

## 8. Competitive Position After Absorption

| Dimension | Before | After | Parity with |
|---|---|---|---|
| Pre-implementation design | Minimal (PRD → ADR with `gz-interview` available but not integrated into ADR creation flow) | Strong (structured exploration + decision locking + adversarial review) | superpowers, GSD |
| Plan quality gates | Adequate (single-pass `gz-plan-audit`) | Strong (iterative 10-dimension audit with blocker classification) | GSD |
| Per-task verification | Partial (pipeline Stage 2 runs two-stage review per task, but no per-task verification *commands* in plans) | Strong (verify stanzas + Nyquist rule baked into plan format) | GSD |
| Evidence discipline | Strong in pipeline (ARB receipts available), not mandated in other skills | Universal (5-step protocol mandated in all completion-claiming skills) | superpowers |
| Agent deviation handling | Binary (in/out lane) | Graduated (4-tier model composing with lane system) | GSD |
| Artifact verification depth | Gate pass/fail (lint/test/typecheck) | 4-level (exists/substantive/wired/flows) | GSD |
| Session orientation | Convention-based ("read AGENTS.md") with no automated state synthesis | Automated (`gz status --orientation` + optional hook) | superpowers, GSD |
| TDD discipline | Policy-based (rules/tests.md + implementer mandate) | Skill-enforced with anti-rationalization and red-green-refactor cycle | superpowers |
| Debugging methodology | Error recovery paths in pipeline, no standalone methodology | Systematic 4-phase workflow with root-cause mandate | superpowers |
| Code review (standalone) | Embedded in pipeline Stage 2 (spec + quality reviewers), not available standalone | Standalone + pipeline | superpowers |
| Requirements quality | Schema validation (`gz validate`) | Schema + advisory quality analysis + traceability | spec-kit |
| Anti-rationalization | Pipeline skill has extensive table; other skills have none | All completion-claiming skills | superpowers |
| Context budget | No formal tracking (subagent dispatch provides implicit budget isolation) | Advisory annotations + compaction awareness guidance | GSD |
| User adaptation | Feedback memories (13 rules capturing style/workflow preferences) | Structured profile + adaptive behavior | GSD (lighter) |

**Retained advantages over all three tools:**
- 5-gate covenant with lane-based rigor (none of the three have this)
- Append-only ledger with event-sourced state (GSD uses mutable STATE.md)
- OBPI brief as governance unit with fail-closed requirements (unique to gzkit)
- ARB receipt middleware for deterministic QA evidence (unique to gzkit)
- Human attestation gate (Gate 5) with parent-lane inheritance (unique to gzkit)
