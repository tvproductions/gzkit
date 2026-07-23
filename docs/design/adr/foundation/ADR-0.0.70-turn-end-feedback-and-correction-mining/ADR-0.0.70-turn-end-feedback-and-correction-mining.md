---
id: ADR-0.0.70-turn-end-feedback-and-correction-mining
status: Validated
kind: foundation
semver: 0.0.70
lane: lite
parent: PRD-GZKIT-1.0.0
date: 2026-06-12
---

# ADR-0.0.70-turn-end-feedback-and-correction-mining: Turn-End Feedback and Ground-Truth Correction Mining

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
Treats governance not as overhead but as the discipline that keeps work honest.
The operative stance for this ADR: **the sensor goes where the failure happens,
not where the ceremony is convenient**. A check that fires at the gate catches
the defect after the agent already declared done; a check that fires at the turn
boundary catches it while the agent can still act. Likewise, a correction record
that depends on the corrected party's self-report is testimony, not evidence —
the work here is to read the ground truth instead.

## Why foundation tier?

Without turn-end feedback and ground-truth correction mining, gzkit's anti-vibing
identity is structurally incomplete: the system that exists to make stochastic LLM
vibing inert has no deterministic sensor at the one boundary where vibing exits —
the agent's turn end — and its correction-capture loop trusts the very stochastic
process it is supposed to audit. The invariance test resolves **yes**: gzkit IS the
governance harness; a harness whose sensors are all ceremony-gated and whose
feedback corpus is agent-authored narrative is not that project. Operator ruling at
interview (2026-06-12): foundation.

Port-vs-adapter: this ADR is a **port**. "Deterministic feedback fires at the
harness lifecycle boundary, and correction evidence is mined from the ground-truth
record, never solely self-reported" is the abstract contract; the Claude Code Stop
hook and the `~/.claude/projects` transcript miner are the first adapters behind
it (codex/copilot adapters are the named open question).

## Intent

gzkit's deterministic sensors fire only at ceremony boundaries: ARB receipts at gate/attestation time, validator scopes at `gz check`/commit/push, the per-edit `post-edit-ruff.py` hook at single-file granularity. Nothing fires at the harness lifecycle's turn boundary — the moment an agent declares a unit of work done. The harness-engineering appraisal (`docs/governance/harness-engineering-appraisal.md`) names this as gzkit's largest structural gap: 'agents work blind between gate transitions.' Separately, gzkit's correction-capture pipeline is entirely self-reported: Behavior Rule 11 requires the agent to append improvement records to `.gzkit/insights/agent-insights.jsonl` when the operator course-corrects, which means the corrections most likely to be lost — the ones an agent fails to recognize or vibes past — leave no record at all. The eval-feedback-cluster chore mines ledger events and the arb-pattern-extraction chore mines ARB receipts; both mine instrumented surfaces, neither mines the ground truth (the session transcripts under `~/.claude/projects/`).

Four independent practitioner theses now converge on exactly these two gaps: Böckeler ('Harness Engineering', martinfowler.com 2026), Greyling ('98% of Claude Code Is Not AI'), the CE compounding-leverage thesis, and now Florian Buetow (Xebia), interviewed on the Beyond Coding Podcast ('The Best Software Engineers Are Solving the Code Review Bottleneck Right Now', published 2026-06-10; companion site cracking-ai-engineering.com). Buetow's distinctive contributions are the two cheap mechanisms this ADR adopts: (1) wire deterministic guardrails into the harness's stop hook so the agent self-corrects in-flight without a human in the loop, and (2) data-mine session logs for patterns where the operator repeatedly reminded the model of the same thing, then promote each recurring pattern into a static check. Both mechanisms feed gzkit's existing machinery (ARB evidence channel; advisory-scorecard Promotable→Mechanical ladder) — they add the two sensor placements the current machinery cannot reach: the harness lifecycle and the un-instrumented transcript record.

Operator ratification (2026-06-12, verbatim): 'do max improvement from Florian Buetow's practices. ensure this becomes aware of this addition: docs/governance/build-to-1.0-campaign-2026-06-10.md'. Kind ruled foundation by operator at interview; the campaign amendment lands as item B.0 in the Magna Carta via OBPI-0.0.70-04 (REQ-0.0.70-04-02).

## Decision

Adopt the Buetow practices as four surfaces, decomposed 1:1 into four OBPIs:

**1. Stop-hook turn-end deterministic feedback (`.claude/hooks/stop-turn-feedback.py` + `Stop` wiring in `.claude/settings.json`).** At every agent turn end, the hook runs the cheapest deterministic check tier — `ruff check` over session-dirty Python files (git working-tree dirty `.py` paths) — under a hard sub-2-second budget (subprocess timeout). On findings, the hook blocks the stop with agent-actionable natural-language feedback (the violation, why it is forbidden, the governed next step), so the agent self-corrects before declaring done. Loop protection: the hook honors the harness's `stop_hook_active` input flag and never blocks twice in one turn. Operator off-switch: a documented one-line disable (environment variable honored by the script, plus the settings.json entry itself). Telemetry: each block appends one line to a bounded local sensor log at `.gzkit/sensors/stop-turn-feedback.jsonl` so the fence's catch-rate is observable rather than silent (the 'fence with no recorded intrusions' decay class from the validator load-bearing baseline). The `.gzkit/sensors/` home is a deliberate new runtime-state class: gitignored and local, distinct from committed `.gzkit/insights/` (governance narrative) and per-chore `proofs/` (chore-scoped runtime state) — hook telemetry is local, non-governance, and not chore-owned. The hook is the mechanical backstop for Behavior Rules Never #5 — an agent cannot end a turn on 'implementation complete' while the cheap tier is red. Design explicitly structures the check tier for extension (future graduation candidates: ty, fast unittest subsets) without committing to them here.

**2. Session-correction-mining chore (`session-correction-mining` under `.gzkit/chores/`, stdlib miner in `src/gzkit/insights/`).** A read-only chore, modeled on eval-feedback-cluster's shape (CHORE.md + acceptance criteria + test-driven module + registry entry), that walks the Claude Code session transcripts under `~/.claude/projects/<project>/` and detects operator-correction patterns: user messages bearing corrective markers following an assistant action. Patterns recurring >= 3 times (threshold configurable) across distinct sessions emit structured proposal records into the chore's `proofs/` directory — candidates for the advisory-scorecard Promotable→Mechanical ladder, exactly as eval-feedback-cluster's proposals are. Privacy invariants are binding: proposals quote at most one line of operator text, scrub email addresses, and the operator-PII rule (no personal email in any repo-bound artifact) applies to every emitted record. The miner fails soft: unparseable or absent transcripts yield zero proposals, never a crashed chore. Output is candidates only — nothing auto-promotes.

**3. Guardrail-feedback-prose rule (`.gzkit/rules/guardrail-feedback-prose.md`).** A binding rule: every fail-closed hook and validator emits agent-actionable natural-language recovery text — what failed, why it is forbidden, and the governed next step — because the feedback text IS the prompt a human would otherwise have typed (Buetow: 'the feedback encodes the prompt that you would write as a human'). The new Stop hook is the rule's first enforcement consumer, landing in the same ADR. The rule carries the body-level rule-version marker per skill-surface-sync and is propagated by `gz agent sync control-surfaces`; an advisory-rules-audit scorecard entry classifies it.

**4. Fourth-source doctrine triangulation (docs).** Append a Buetow section to `docs/governance/harness-engineering-appraisal.md` following the doc's established per-thesis pattern (Böckeler, Greyling, CE), recording what converges (architecture tests, risk-tiered lanes, TDD-as-feedback, preloaded-guardrail templates, ownership vs cognitive surrender — all already gzkit canon) and what was adopted (the two new sensor placements + the prose bar). Cross-link the campaign B.0 amendment.

**Reversibility: two-way door.** One settings entry + one script; one chore directory + one registry row; one versioned rule file; one doc section. All removable in one commit. No new gz CLI verb, no schema change, no new ledger event type.

**Sequencing:** OBPI-01 and OBPI-02 are independent; OBPI-03's rule is enforced against OBPI-01's hook so 01 precedes or lands with 03; OBPI-04 documents all three and lands last.

**Scope boundary — what this ADR explicitly does NOT do:** Does NOT build the in-session sensor sidecar (`gz harness watch`) — the Stop hook is the cheap experiment whose telemetry will inform that pool-track decision; the sidecar is not displaced. Does NOT add a `gz validate` scope for prose conformance — the rule binds via authoring discipline and the scorecard; mechanical promotion is a named future candidate once the rule has catch evidence. Does NOT wire mining proposals into a CLI surface — the `gz insights` verb (GHI #575, campaign Phase E) is the future surfacing home. Does NOT add codex/copilot hook parity — hooks are a Claude Code vendor surface today; parity is a named open question. Does NOT add any third-party dependency — both scripts are stdlib-only (json, pathlib, subprocess, collections, re).

**Forced downstream decisions (interview closing question):** which checks graduate into the Stop-hook tier (ty, fast unittest subsets); the sidecar pool decision is settled by Stop-hook telemetry rather than taste; mining proposals eventually surface via the `gz insights` verb (GHI #575, Phase E); vendor hook parity for codex/copilot mirrors. Tier-2 forcing functions (pre-mortem, WWHTBT, constraint archaeology, assumption surfacing, 2am operator, reversibility, scope minimization) were agent-drafted against session evidence and operator-audited 2026-06-12 per AGENTS.md § Operator Economy claim 4 ('Proceed as drafted'); their content is folded into intent/consequences/alternatives.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The turn-end Stop-hook deterministic-feedback sensor behaves per spec (loop guard via stop_hook_active, fail-open on its own errors, documented off-switch). | uv run -m unittest tests.hooks.test_stop_turn_feedback | 0 |

## Consequences

### Positive

1. **In-flight steering closes the blind-between-gates gap.** The appraisal's #1 named weakness gets its first mechanical sensor at the harness lifecycle, at hook-script cost rather than live-sidecar cost.

2. **Never #5 gains a mechanical backstop.** Premature 'implementation complete' turn-ends cannot pass a red cheap-tier check; the block feedback re-enters the loop and the agent self-corrects without operator intervention.

3. **Correction capture becomes compliance-independent.** Transcript mining catches the corrections Behavior Rule 11 self-reporting misses — precisely the ones an agent failed to recognize — and adds cross-session recurrence visibility no per-session mechanism can have.

4. **The promotion ladder gains a third sensor feed.** eval-feedback-cluster (ledger), arb-pattern-extraction (receipts), and now session-correction-mining (ground-truth transcripts) triangulate the same Promotable→Mechanical pipeline from three independent surfaces.

5. **Guardrail feedback quality becomes a named contract.** 'Engineer the failure text as the prompt' stops being folklore and becomes a versioned rule with a first enforcement consumer.

6. **The sidecar decision gets evidence.** Stop-hook block-count telemetry replaces taste as the input to the pooled `gz harness watch` question — Buetow's cheap mechanism funds the expensive decision.

7. **Doctrinal convergence is recorded, not vibed.** Four independent practitioner theses landing on gzkit's existing equilibrium is itself evidence the heavy-harness bet is correct; the appraisal section makes that auditable.

### Negative

1. **Per-turn latency.** Every agent turn-end pays the hook's cost; bounded by the sub-2s subprocess timeout and the dirty-files-only scope, but real. Mitigation: lint tier only; timeout fails open (never blocks on its own slowness).

2. **False-positive block risk.** A noisy block annoys and, at worst, loops. Mitigations: `stop_hook_active` guarantees at most one block per turn; scope is deterministic lint findings only; documented one-line off-switch for the 2am case.

3. **Decay risk — the pre-mortem failure.** The hook could be disabled-and-forgotten, mining proposals could pile untriaged, the prose rule could join the unenforced advisory pile (the 'fence with no recorded intrusions' class). Mitigations booked in-ADR: block telemetry makes the hook's catch-rate observable; the chore is homed to the triage cadence in CHORE.md; the rule lands with its first enforcement consumer rather than as floating doctrine.

4. **Privacy surface.** Mining reads operator conversation data. Mitigations are binding invariants, not advice: read-only miner, <=1-line quotes, email scrubbing, operator-PII rule applies to every emitted artifact; proposals live in proofs/ (runtime-state class), and any promotion to a committed surface passes human review.

5. **Heuristic noise.** Lexical correction-detection will produce false candidates. Absorbed by design: output is candidates-only; the scorecard ladder's human/agent review is the filter; nothing auto-promotes.

6. **Vendor coupling.** The Stop hook depends on Claude Code's hook contract (`stop_hook_active`, block semantics) and the miner on the transcript JSONL layout. Both are defensive: unknown input shapes fail open (hook) or fail soft to zero proposals (miner). Codex/copilot have no hook parity today — named open question, not silent drift.

7. **Shakiest WWHTBT condition.** If Behavior Rule 11 self-reporting is already near-complete, mining yields nothing. Acceptable: the chore is read-only and its first run is itself the experiment that answers the question.

## Boundary Invariants

1. **A turn can always end.** The Stop hook honors `stop_hook_active` (at most one
   block per turn) and fails open on its own errors and timeouts — the hook's own
   malfunction never traps an agent in a blocked-stop loop, and the documented
   off-switch disables it in one line.
   (REQ-0.0.70-01-07: STRUCTURAL-FENCE — verified at ADR closeout via this invariant)
2. **The miner is read-only outside its proofs directory, and no emitted record
   carries operator PII.** Transcript mining writes only to
   `.gzkit/chores/session-correction-mining/proofs/`; emitted proposals quote at
   most one line of operator text and scrub email addresses (the operator-PII
   rule binds every artifact).
   (REQ-0.0.70-02-07: STRUCTURAL-FENCE — verified at ADR closeout via this invariant; OBPI-02)
3. **Both scripts are stdlib-only.** Neither the Stop hook nor the miner imports
   any third-party package (Stdlib-First doctrine); ruff is invoked as a
   subprocess of the existing toolchain, not imported.
4. **Mining output is candidates, never canon.** No proposal record mutates the
   ledger, a rule, or a validator scope; promotion always passes the
   advisory-scorecard ladder with human review.
   (REQ-0.0.70-02-07: STRUCTURAL-FENCE — verified at ADR closeout via this invariant; OBPI-02)

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 6
- Baseline Range: 3-3
- Baseline Selected: 3
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] Stop-hook turn-end deterministic feedback — `.claude/hooks/stop-turn-feedback.py` + `Stop` matcher wiring in `.claude/settings.json`; ruff over session-dirty Python files; sub-2s budget; `stop_hook_active` loop guard; off-switch; block telemetry line; agent-actionable block prose; unit tests
- [ ] Session-correction-mining chore — stdlib miner over `~/.claude/projects` transcripts in `src/gzkit/insights/`; corrective-marker heuristics; recurrence >= 3 clustering; PII-scrubbed proposal records to `.gzkit/chores/session-correction-mining/proofs/`; CHORE.md + acceptance criteria + registry entry; `gz validate --chores-layout` green; unit tests
- [ ] Guardrail-feedback-prose rule — `.gzkit/rules/guardrail-feedback-prose.md` with rule-version marker; binding bar (what failed / why forbidden / governed next step) for fail-closed hooks and validators; Stop hook as first enforcement consumer; advisory-rules-audit scorecard entry; `gz agent sync control-surfaces`
- [ ] Fourth-source doctrine triangulation — Buetow section appended to `docs/governance/harness-engineering-appraisal.md` per the established per-thesis pattern (citation: Beyond Coding Podcast, 2026-06-10); campaign B.0 cross-link; `mkdocs build --strict` green

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-06-12T02:14:32.239044*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.0.70-turn-end-feedback-and-correction-mining

### Q: What is the title of this ADR?

**A:** Turn-End Feedback and Ground-Truth Correction Mining

### Q: What is the semantic version?

**A:** 0.0.70

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** lite

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's deterministic sensors fire only at ceremony boundaries: ARB receipts at gate/attestation time, validator scopes at `gz check`/commit/push, the per-edit `post-edit-ruff.py` hook at single-file granularity. Nothing fires at the harness lifecycle's turn boundary — the moment an agent declares a unit of work done. The harness-engineering appraisal (`docs/governance/harness-engineering-appraisal.md`) names this as gzkit's largest structural gap: 'agents work blind between gate transitions.' Separately, gzkit's correction-capture pipeline is entirely self-reported: Behavior Rule 11 requires the agent to append improvement records to `.gzkit/insights/agent-insights.jsonl` when the operator course-corrects, which means the corrections most likely to be lost — the ones an agent fails to recognize or vibes past — leave no record at all. The eval-feedback-cluster chore mines ledger events and the arb-pattern-extraction chore mines ARB receipts; both mine instrumented surfaces, neither mines the ground truth (the session transcripts under `~/.claude/projects/`).

Four independent practitioner theses now converge on exactly these two gaps: Böckeler ('Harness Engineering', martinfowler.com 2026), Greyling ('98% of Claude Code Is Not AI'), the CE compounding-leverage thesis, and now Florian Buetow (Xebia), interviewed on the Beyond Coding Podcast ('The Best Software Engineers Are Solving the Code Review Bottleneck Right Now', published 2026-06-10; companion site cracking-ai-engineering.com). Buetow's distinctive contributions are the two cheap mechanisms this ADR adopts: (1) wire deterministic guardrails into the harness's stop hook so the agent self-corrects in-flight without a human in the loop, and (2) data-mine session logs for patterns where the operator repeatedly reminded the model of the same thing, then promote each recurring pattern into a static check. Both mechanisms feed gzkit's existing machinery (ARB evidence channel; advisory-scorecard Promotable→Mechanical ladder) — they add the two sensor placements the current machinery cannot reach: the harness lifecycle and the un-instrumented transcript record.

Operator ratification (2026-06-12, verbatim): 'do max improvement from Florian Buetow's practices. ensure this becomes aware of this addition: docs/governance/build-to-1.0-campaign-2026-06-10.md'. Kind ruled foundation by operator at interview; campaign amendment recorded as item B.0 in the Magna Carta.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Adopt the Buetow practices as four surfaces, decomposed 1:1 into four OBPIs:

**1. Stop-hook turn-end deterministic feedback (`.claude/hooks/stop-turn-feedback.py` + `Stop` wiring in `.claude/settings.json`).** At every agent turn end, the hook runs the cheapest deterministic check tier — `ruff check` over session-dirty Python files (git working-tree dirty `.py` paths) — under a hard sub-2-second budget (subprocess timeout). On findings, the hook blocks the stop with agent-actionable natural-language feedback (the violation, why it is forbidden, the governed next step), so the agent self-corrects before declaring done. Loop protection: the hook honors the harness's `stop_hook_active` input flag and never blocks twice in one turn. Operator off-switch: a documented one-line disable (environment variable honored by the script, plus the settings.json entry itself). Telemetry: each block appends one line to a bounded local sensor log so the fence's catch-rate is observable rather than silent (the 'fence with no recorded intrusions' decay class from the validator load-bearing baseline). The hook is the mechanical backstop for Behavior Rules Never #5 — an agent cannot end a turn on 'implementation complete' while the cheap tier is red. Design explicitly structures the check tier for extension (future graduation candidates: ty, fast unittest subsets) without committing to them here.

**2. Session-correction-mining chore (`session-correction-mining` under `.gzkit/chores/`, stdlib miner in `src/gzkit/insights/`).** A read-only chore, modeled on eval-feedback-cluster's shape (CHORE.md + acceptance criteria + test-driven module + registry entry), that walks the Claude Code session transcripts under `~/.claude/projects/<project>/` and detects operator-correction patterns: user messages bearing corrective markers following an assistant action. Patterns recurring >= 3 times (threshold configurable) across distinct sessions emit structured proposal records into the chore's `proofs/` directory — candidates for the advisory-scorecard Promotable→Mechanical ladder, exactly as eval-feedback-cluster's proposals are. Privacy invariants are binding: proposals quote at most one line of operator text, scrub email addresses, and the operator-PII rule (no personal email in any repo-bound artifact) applies to every emitted record. The miner fails soft: unparseable or absent transcripts yield zero proposals, never a crashed chore. Output is candidates only — nothing auto-promotes.

**3. Guardrail-feedback-prose rule (`.gzkit/rules/guardrail-feedback-prose.md`).** A binding rule: every fail-closed hook and validator emits agent-actionable natural-language recovery text — what failed, why it is forbidden, and the governed next step — because the feedback text IS the prompt a human would otherwise have typed (Buetow: 'the feedback encodes the prompt that you would write as a human'). The new Stop hook is the rule's first enforcement consumer, landing in the same ADR. The rule carries the body-level rule-version marker per skill-surface-sync and is propagated by `gz agent sync control-surfaces`; an advisory-rules-audit scorecard entry classifies it.

**4. Fourth-source doctrine triangulation (docs).** Append a Buetow section to `docs/governance/harness-engineering-appraisal.md` following the doc's established per-thesis pattern (Böckeler, Greyling, CE), recording what converges (architecture tests, risk-tiered lanes, TDD-as-feedback, preloaded-guardrail templates, ownership vs cognitive surrender — all already gzkit canon) and what was adopted (the two new sensor placements + the prose bar). Cross-link the campaign B.0 amendment.

**Reversibility: two-way door.** One settings entry + one script; one chore directory + one registry row; one versioned rule file; one doc section. All removable in one commit. No new gz CLI verb, no schema change, no new ledger event type.

**Sequencing:** OBPI-01 and OBPI-02 are independent; OBPI-03's rule is enforced against OBPI-01's hook so 01 precedes or lands with 03; OBPI-04 documents all three and lands last.

**Scope boundary — what this ADR explicitly does NOT do:** Does NOT build the in-session sensor sidecar (`gz harness watch`) — the Stop hook is the cheap experiment whose telemetry will inform that pool-track decision; the sidecar is not displaced. Does NOT add a `gz validate` scope for prose conformance — the rule binds via authoring discipline and the scorecard; mechanical promotion is a named future candidate once the rule has catch evidence. Does NOT wire mining proposals into a CLI surface — the `gz insights` verb (GHI #575, campaign Phase E) is the future surfacing home. Does NOT add codex/copilot hook parity — hooks are a Claude Code vendor surface today; parity is a named open question. Does NOT add any third-party dependency — both scripts are stdlib-only (json, pathlib, subprocess, collections, re).

**Forced downstream decisions (interview closing question):** which checks graduate into the Stop-hook tier (ty, fast unittest subsets); the sidecar pool decision is settled by Stop-hook telemetry rather than taste; mining proposals eventually surface via the `gz insights` verb (GHI #575, Phase E); vendor hook parity for codex/copilot mirrors. Tier-2 forcing functions (pre-mortem, WWHTBT, constraint archaeology, assumption surfacing, 2am operator, reversibility, scope minimization) were agent-drafted against session evidence and operator-audited 2026-06-12 per AGENTS.md § Operator Economy claim 4 ('Proceed as drafted'); their content is folded into intent/consequences/alternatives.

### Q: What good things result from this decision? List benefits.

**A:** 1. **In-flight steering closes the blind-between-gates gap.** The appraisal's #1 named weakness gets its first mechanical sensor at the harness lifecycle, at hook-script cost rather than live-sidecar cost.

2. **Never #5 gains a mechanical backstop.** Premature 'implementation complete' turn-ends cannot pass a red cheap-tier check; the block feedback re-enters the loop and the agent self-corrects without operator intervention.

3. **Correction capture becomes compliance-independent.** Transcript mining catches the corrections Behavior Rule 11 self-reporting misses — precisely the ones an agent failed to recognize — and adds cross-session recurrence visibility no per-session mechanism can have.

4. **The promotion ladder gains a third sensor feed.** eval-feedback-cluster (ledger), arb-pattern-extraction (receipts), and now session-correction-mining (ground-truth transcripts) triangulate the same Promotable→Mechanical pipeline from three independent surfaces.

5. **Guardrail feedback quality becomes a named contract.** 'Engineer the failure text as the prompt' stops being folklore and becomes a versioned rule with a first enforcement consumer.

6. **The sidecar decision gets evidence.** Stop-hook block-count telemetry replaces taste as the input to the pooled `gz harness watch` question — Buetow's cheap mechanism funds the expensive decision.

7. **Doctrinal convergence is recorded, not vibed.** Four independent practitioner theses landing on gzkit's existing equilibrium is itself evidence the heavy-harness bet is correct; the appraisal section makes that auditable.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **Per-turn latency.** Every agent turn-end pays the hook's cost; bounded by the sub-2s subprocess timeout and the dirty-files-only scope, but real. Mitigation: lint tier only; timeout fails open (never blocks on its own slowness).

2. **False-positive block risk.** A noisy block annoys and, at worst, loops. Mitigations: `stop_hook_active` guarantees at most one block per turn; scope is deterministic lint findings only; documented one-line off-switch for the 2am case.

3. **Decay risk — the pre-mortem failure.** The hook could be disabled-and-forgotten, mining proposals could pile untriaged, the prose rule could join the unenforced advisory pile (the 'fence with no recorded intrusions' class). Mitigations booked in-ADR: block telemetry makes the hook's catch-rate observable; the chore is homed to the triage cadence in CHORE.md; the rule lands with its first enforcement consumer rather than as floating doctrine.

4. **Privacy surface.** Mining reads operator conversation data. Mitigations are binding invariants, not advice: read-only miner, <=1-line quotes, email scrubbing, operator-PII rule applies to every emitted artifact; proposals live in proofs/ (runtime-state class), and any promotion to a committed surface passes human review.

5. **Heuristic noise.** Lexical correction-detection will produce false candidates. Absorbed by design: output is candidates-only; the scorecard ladder's human/agent review is the filter; nothing auto-promotes.

6. **Vendor coupling.** The Stop hook depends on Claude Code's hook contract (`stop_hook_active`, block semantics) and the miner on the transcript JSONL layout. Both are defensive: unknown input shapes fail open (hook) or fail soft to zero proposals (miner). Codex/copilot have no hook parity today — named open question, not silent drift.

7. **Shakiest WWHTBT condition.** If Behavior Rule 11 self-reporting is already near-complete, mining yields nothing. Acceptable: the chore is read-only and its first run is itself the experiment that answers the question.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Stop-hook turn-end deterministic feedback — `.claude/hooks/stop-turn-feedback.py` + `Stop` matcher wiring in `.claude/settings.json`; ruff over session-dirty Python files; sub-2s budget; `stop_hook_active` loop guard; off-switch; block telemetry line; agent-actionable block prose; unit tests
2. Session-correction-mining chore — stdlib miner over `~/.claude/projects` transcripts in `src/gzkit/insights/`; corrective-marker heuristics; recurrence >= 3 clustering; PII-scrubbed proposal records to `.gzkit/chores/session-correction-mining/proofs/`; CHORE.md + acceptance criteria + registry entry; `gz validate --chores-layout` green; unit tests
3. Guardrail-feedback-prose rule — `.gzkit/rules/guardrail-feedback-prose.md` with rule-version marker; binding bar (what failed / why forbidden / governed next step) for fail-closed hooks and validators; Stop hook as first enforcement consumer; advisory-rules-audit scorecard entry; `gz agent sync control-surfaces`
4. Fourth-source doctrine triangulation — Buetow section appended to `docs/governance/harness-engineering-appraisal.md` per the established per-thesis pattern (citation: Beyond Coding Podcast, 2026-06-10); campaign B.0 cross-link; `mkdocs build --strict` green

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **Full in-session sensor sidecar (`gz harness watch`) now.** REJECTED for this ADR: a live process observing edits is the heaviest build on the improvement plan and was never drafted past Wave-2 intent. The Stop hook delivers the largest share of the in-flight value at hook-script cost and generates the telemetry evidence the sidecar decision actually needs. The sidecar remains a pool-track candidate; this ADR funds its decision, it does not displace it.

2. **Wire the Stop hook to full `gz check`.** REJECTED: minutes-per-turn is unusable; turn-end checks must be sub-2s lint-tier. The check tier is structured for graduated extension instead.

3. **Rely on existing insights + ARB (the operator's own challenge, 2026-06-12).** REJECTED with evidence: ARB is agent-invoked at ceremony boundaries and cannot reach the harness lifecycle by construction; `agent-insights.jsonl` is agent-authored narrative whose blind spot is exactly the unrecognized correction. Both remain the landing machinery; neither is the sensor.

4. **semgrep for pattern rules.** REJECTED per Stdlib-First: ruff plus the existing AST policy-test surface (`tests/policy/`) covers the class; a third-party pattern engine adds a dependency without naming what stdlib cannot do.

5. **Emit mining results as ledger events instead of proofs.** REJECTED: the ledger is the governance system-of-record; heuristic candidates are ephemera until a human promotes them. Proofs-directory output (runtime-state class) matches eval-feedback-cluster's precedent and keeps Layer-2 clean.

6. **Author the prose rule with a mechanical `gz validate` conformance scope in the same ADR.** REJECTED for now: a validator that grades prose quality is inferential, not computational; promoting the rule to a mechanical scope is a named future candidate once catch evidence exists. Shipping the rule with a real enforcement consumer (the hook) beats shipping a weak validator.

7. **One OBPI bundling all four surfaces.** REJECTED: four separable deliverables with four distinct proof shapes under one Gate 5 witness obscures exactly the per-increment accountability the decomposition matrix exists to protect.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

1. **Full in-session sensor sidecar (`gz harness watch`) now.** REJECTED for this ADR: a live process observing edits is the heaviest build on the improvement plan and was never drafted past Wave-2 intent. The Stop hook delivers the largest share of the in-flight value at hook-script cost and generates the telemetry evidence the sidecar decision actually needs. The sidecar remains a pool-track candidate; this ADR funds its decision, it does not displace it.

2. **Wire the Stop hook to full `gz check`.** REJECTED: minutes-per-turn is unusable; turn-end checks must be sub-2s lint-tier. The check tier is structured for graduated extension instead.

3. **Rely on existing insights + ARB (the operator's own challenge, 2026-06-12).** REJECTED with evidence: ARB is agent-invoked at ceremony boundaries and cannot reach the harness lifecycle by construction; `agent-insights.jsonl` is agent-authored narrative whose blind spot is exactly the unrecognized correction. Both remain the landing machinery; neither is the sensor.

4. **semgrep for pattern rules.** REJECTED per Stdlib-First: ruff plus the existing AST policy-test surface (`tests/policy/`) covers the class; a third-party pattern engine adds a dependency without naming what stdlib cannot do.

5. **Emit mining results as ledger events instead of proofs.** REJECTED: the ledger is the governance system-of-record; heuristic candidates are ephemera until a human promotes them. Proofs-directory output (runtime-state class) matches eval-feedback-cluster's precedent and keeps Layer-2 clean.

6. **Author the prose rule with a mechanical `gz validate` conformance scope in the same ADR.** REJECTED for now: a validator that grades prose quality is inferential, not computational; promoting the rule to a mechanical scope is a named future candidate once catch evidence exists. Shipping the rule with a real enforcement consumer (the hook) beats shipping a weak validator.

7. **One OBPI bundling all four surfaces.** REJECTED: four separable deliverables with four distinct proof shapes under one Gate 5 witness obscures exactly the per-increment accountability the decomposition matrix exists to protect.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.70 | Completed | g0 | 2026-06-13 | Completed |
| 0.0.70 | Validated | g0 | 2026-06-13 | accept audit (Phase-2 audit ceremony; see audit/AUDIT.md) |
