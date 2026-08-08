---
id: ADR-pool.systematic-debugging-discipline
status: Pool
lane: heavy
parent: PRD-GZKIT-1.0.0
---

# ADR-pool.systematic-debugging-discipline: Systematic Debugging Discipline

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. This ADR is rule and doctrine work; the work is the work, not theater for an unseen reviewer. Treats the new `investigator` persona as a dispatchable subagent peer to the existing implementer/spec-reviewer/quality-reviewer triad under ADR-0.18.0's subagent-driven model; treats the new `gz-systematic-debug` skill as methodology (like `gz-design`), not CLI ceremony; treats the precondition-form Iron Law as a structural witness sibling to the existing two completion/flow-form Iron Laws, sharing typography and rationalization-prevention shape but addressing a distinct failure axis. Refuses to propose fixes from training-corpus pattern-matching without root-cause evidence captured as an ARB step receipt; refuses to bundle a fourth fix attempt when three prior attempts have failed — that is the architectural-pause signal.

## Why foundation tier?

Without this ADR, systematic debugging is an unnamed principle inside PRIME DIRECTIVE / DO IT RIGHT — agents pattern-match plausible-looking fixes from training-corpus memory (the `Skipped cheap verification` shape codified in `.gzkit/rules/agent-failure-modes.md`), bundle multi-patch attempts past the architectural-pause signal, and have no structural sequencing rule that forces root-cause evidence before fix proposal. The recurring shape across gzkit's own history is visible in GHIs #263, #290, #309.

This ADR authors a port: the precondition-form Iron Law (*"NO FIX MAY BE PROPOSED UNTIL ROOT-CAUSE EVIDENCE IS CAPTURED AS AN ARB STEP RECEIPT"*), the 3+-failed-fixes-architecture-pause rule, and the `investigator` persona + `gz-systematic-debug` skill + GHI-skill cross-link surfaces every agent-binding contract reaches for when a bug, test failure, or unexpected behavior surfaces. The structural witness is the ARB step receipt cited in the fix-proposal commit message — the same class of structural defense `gz obpi complete` applies to ceremony attestation, applied at the debugging surface.

## Intent

gzkit's PRIME DIRECTIVE and DO IT RIGHT pillars name the principle of root-cause investigation but provide no structural sequencing rule that forces it before a fix is proposed. The result is a class of failure already named in `.gzkit/rules/agent-failure-modes.md`: agents pattern-match a plausible-looking fix from training-corpus memory (`Skipped cheap verification`), commit it, watch it fail, then propose a second fix on top of the first, then a third — never recognizing that the third failure is no longer about the next patch but about wrong architecture. The recurring shape across gzkit's own history is visible in GHIs #263 (skipped-verification regression), #309 (cosmetic @covers backfill that silenced audit-check without re-derived semantics), and the multi-fix-attempt patterns that motivated the defect-fix routing thresholds in AGENTS.md.

The operator named the gap explicitly: *"I think PRIME DIRECTIVE and DO IT RIGHT could be meaningfully assisted by how superpowers handles systematic debugging."* The [superpowers systematic-debugging skill](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) supplies an empirically-tested Iron Law (precondition form: *"NO FIX MAY BE PROPOSED UNTIL ROOT-CAUSE EVIDENCE IS CAPTURED"*), a four-phase procedure (Root Cause / Pattern / Hypothesis / Implementation), a three-failed-fixes-architecture-pause rule, and supporting techniques (`root-cause-tracing`, `defense-in-depth`, `condition-based-waiting`). The shape mirrors gzkit's existing two Iron Laws — `gz-obpi-pipeline` (*"THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES"*) and `gz-patch-release` (*"ONCE THE OPERATOR APPROVES, THE CEREMONY FLOWS TO COMPLETION"*) — on a different axis: precondition rather than completion, but identical typography, all-caps fenced-block opening line, and rationalization-prevention table downstream.

The additional operator framing: *"ensure that PRIME DIRECTIVE and DO IT RIGHT reach for this and, perhaps we need a persona to go along with it so that it is triggered by an agent"* — naming both the doctrine-attestation surface (AGENTS.md operative claims must reach for the skill) and the persona-dispatch surface (an `investigator` persona, dispatchable as a subagent peer to the existing implementer/spec-reviewer/quality-reviewer triad under ADR-0.18.0's subagent-driven model). The further operator framing: *"all of these will always require GHIs, so tying the GHI skills into this would triangulate well"* — naming the third coupling point (the GHI lifecycle as the cross-session memory of debugging events: Phase 1 evidence routes to `/ghi-author` before commit if cross-brief; Phase 4 fix lands via `/ghi-close` with Phase-1 evidence trail; Phase 4.5 architecture pause routes to `/ghi-author` for an architectural GHI labeled as a foundation-ADR candidate).

This ADR codifies systematic debugging as a foundation-attested invariant: a dedicated skill (`gz-systematic-debug`), a dispatchable persona (`investigator`), two new DO IT RIGHT operative claims (Iron Law precondition + 3-failed-fixes-architecture-pause), an explicit PRIME DIRECTIVE cross-reference, a Behavior Rule wiring the skill to the persona at the trigger surface (any bug / test failure / unexpected behavior spawns the investigator with the skill, captures Phase 1 evidence as an ARB step receipt before any fix proposal), GHI-skill cross-links at three coupling points, and a scoped rule file. The ADR is foundation kind because it shapes how gzkit agents debug, not what they ship. The lane is heavy because it binds agent behavior across every surface, introduces a new skill + new persona + new rule, and modifies AGENTS.md operative-claims sections.

## Decision

Promote systematic debugging from an unnamed principle inside PRIME DIRECTIVE / DO IT RIGHT to a foundation-attested invariant with five mechanical surfaces, decomposed into five OBPIs.

**The invariant (canonical statement):** When an agent encounters a bug, test failure, or unexpected behavior, the agent dispatches the `investigator` subagent persona under the `gz-systematic-debug` skill and captures Phase-1 root-cause evidence as an ARB step receipt BEFORE proposing any fix. After three failed fix attempts on the same defect, the failure class is wrong architecture, not the next patch — the agent STOPs the fix loop and routes to the operator as an architectural GHI (foundation-ADR candidate) via `/ghi-author`. Cross-brief Phase-1 evidence and architectural pauses route through the GHI lifecycle.

**Decision items (1:1 with Feature Checklist below):**

1. **Author `gz-systematic-debug` skill** at `.gzkit/skills/gz-systematic-debug/SKILL.md` (`model: opus` per `.claude/rules/model-selection.md` — judgment-class hypothesis formation; `lifecycle_state: active`; no `gz_command:` — methodology like `gz-design`, not CLI-backed). Skill carries the Iron Law (precondition form, fenced block, same typography as `gz-obpi-pipeline`/`gz-patch-release`); the four phases (Root Cause / Pattern / Hypothesis / Implementation); a Red-Flags dictionary (e.g. *"this looks easy, just patch it"*, *"the error message is probably wrong"*, *"this worked before, I'll just retry"*) and an Operator-Signals dictionary (e.g. operator says *"we've fixed this before"*, operator interjects *"why did you skip X"*, operator names a class-of-failure word like *"architecture"*); the 3+-failed-fixes-architecture-pause rule with the explicit STOP-and-route-to-operator language; adapted supporting references (`root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md` translated to Python/gzkit vocabulary); ARB-receipt integration for Phase-1 evidence (Phase 1 evidence MUST be captured via `uv run gz arb step --name root-cause-trace -- ...` and the resulting `arb-step-root-cause-trace-*` receipt cited in the fix-proposal commit message).

2. **Author `investigator` persona** at `.gzkit/personas/investigator.md`. Traits: `evidence-first`, `hypothesis-discipline`, `fix-impulse-suspending`, `architecture-questioning`. Anti-traits: `patch-first-instinct`, `single-hypothesis-fixation`, `symptom-fixation`, `narrative-recall-substitution-for-evidence`. Grounding paragraph names the persona's behavioral identity as the agent who refuses to propose a fix until root-cause evidence is captured as a receipt. Persona is dispatchable as a subagent peer to the existing implementer/spec-reviewer/quality-reviewer triad under ADR-0.18.0-subagent-driven-pipeline-execution; the persona row added to AGENTS.md § Persona table (becoming the seventh persona).

3. **AGENTS.md integration** (single OBPI for coupled edits): (a) Add DO IT RIGHT operative claim #10 — the Iron Law (precondition form) verbatim, citing `gz-systematic-debug` as the procedure of record; (b) Add DO IT RIGHT operative claim #11 — the 3+-failed-fixes-architecture-pause rule, citing `/ghi-author` as the routing surface; (c) Add a one-line cross-reference under PRIME DIRECTIVE item #5 (*"defect surfaced in flight → invoke `gz-systematic-debug` before proposing fix"*); (d) Add Behavior Rule Always #14 — *"On bug / test failure / unexpected behavior: spawn `investigator` subagent with `gz-systematic-debug`; Phase 1 evidence captured as ARB step receipt before fix proposal"*; (e) Update the § Persona table to add the `investigator` row (seventh persona); (f) Update the § Skills catalog to add `gz-systematic-debug` under the Code Quality cluster.

4. **Cross-link GHI skills to systematic debugging.** Edit `.gzkit/skills/ghi-author/SKILL.md` and `.gzkit/skills/ghi-close/SKILL.md` to add a "Systematic Debugging coupling" subsection naming the three coupling points: (a) **Phase 1 evidence + cross-brief defect → `/ghi-author` before commit** — when Phase-1 root-cause evidence shows the defect crosses brief boundaries (the direct-fix routing thresholds in AGENTS.md fail), the agent files a GHI via `/ghi-author` before committing the fix, with the ARB step receipt ID cited in the GHI body; (b) **Phase 4 fix lands → `/ghi-close` with Phase-1 evidence trail in body** — when a fix lands and a GHI exists for the defect, the closing comment cites the Phase-1 ARB receipt ID and the four-phase decision trail; (c) **Phase 4.5 architecture pause → `/ghi-author` for architectural GHI labeled as foundation-ADR candidate** — when the 3+-failed-fixes-architecture-pause rule fires, the agent files an architectural GHI via `/ghi-author` with the three prior fix-attempt receipts cited, labeled as a foundation-ADR candidate so the operator routes it to ADR ceremony rather than a fourth patch.

5. **Author `.gzkit/rules/systematic-debugging.md` rule file** with body-version `0.1.0`, scoped `paths:` (likely `**/*.py` and `**/*.md` — debug discipline binds globally), encoding the three coupling points as enforceable doctrine and adding a scorecard entry to `docs/governance/advisory-rules-audit.md`. Loading posture: advisory (no mechanical gate in this ADR). Future GHI promotion target: `gz validate --systematic-debug-coupling` validator scope that checks every commit with `fix(<scope>):` subject for an `arb-step-root-cause-trace-*` receipt trailer when the touched files span >1 brief allowlist, and every architectural GHI for the three-prior-receipts-cited pattern.

**Sequencing:** OBPI-01 (skill) and OBPI-02 (persona) land in parallel — both are content authoring with no inter-dependency. OBPI-03 (AGENTS.md integration) depends on OBPI-01 and OBPI-02 because it cites them. OBPI-04 (GHI skill cross-links) depends on OBPI-01 because it cites the skill's phase names. OBPI-05 (rule file + scorecard) depends on OBPI-03 and OBPI-04 because it codifies their coupling.

**Lane: Heavy.** New skill + new persona + new rule + AGENTS.md operative-claims change all trigger heavy-lane rigor per `.gzkit/rules/skill-surface-sync.md` (new canonical surface entries) and `.claude/rules/cli.md` (no new CLI verb, but new agent-binding surfaces). Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.36-universal-obpi-attestation.

**Subagent scope (operator-bounded):** This ADR adopts only the investigator-only persona slice of superpowers's [systematic-debugging](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) plus its supporting techniques translated to Python/gzkit vocabulary. Operator deferred the full SDD prompt-template bundle adoption from [superpowers/subagent-driven-development](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development) to a separate future GHI per: *"We have already partially adopted SP's approach to this ... but the whole bundle could be powerful."*

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT adopt the full superpowers SDD (subagent-driven-development) prompt-template bundle — operator-deferred to a separate future GHI.
- Does NOT re-architect ADR-0.18.0's subagent dispatch model — the `investigator` persona slots into the existing model as a seventh peer.
- Does NOT promote `systematic-debugging.md` to a mechanical validator scope — the rule loads as advisory in this ADR; mechanical promotion (e.g. `gz validate --systematic-debug-coupling`) is a future GHI target named in OBPI-05.
- Does NOT modify the existing defect-fix routing thresholds in AGENTS.md § Defect-fix routing — those thresholds remain authoritative for the direct-fix vs OBPI-ceremony decision; systematic debugging sits upstream as the precondition that produces the evidence the routing decision consumes.
- Does NOT modify the existing two Iron Laws (`gz-obpi-pipeline`, `gz-patch-release`) — the precondition-form Iron Law sits on a different axis (precondition rather than completion) and is additive.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The advisory-rules scorecard is internally self-consistent — the doctrine-registration surface this systematic-debugging rule binds its coupling-point doctrine to. | uv run gz validate --advisory-scorecard | 0 |

## Consequences

### Positive

1. **Closes the `Skipped cheap verification` failure class structurally** (per `.gzkit/rules/agent-failure-modes.md`). Today, the failure shape is caught only by post-hoc review (cosmetic @covers backfill heuristic GHI #309, fabrication ARB-receipt discipline GHI #290). After this ADR, the failure is caught upstream: the Iron Law (precondition) refuses any fix proposal without a captured ARB step receipt for Phase-1 root-cause evidence, and the 3+-failed-fixes-architecture-pause closes the multi-patch failure loop the routing-threshold table can't catch.

2. **Reuses superpowers's empirically-tested protocol rather than re-deriving it.** The four-phase procedure, the Iron Law shape, and the three-failed-fixes-architecture-pause rule are battle-tested in superpowers's [systematic-debugging](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) corpus. Adopting the shape (translated to gzkit/Python vocabulary) gets the structural defense without the cost of empirical iteration on what a debugging protocol should look like.

3. **Lifts gzkit's PRIME DIRECTIVE from principle-only to structurally-gated.** PRIME DIRECTIVE item #5 ("FLAG DEFECTS, NEVER EXCUSE THEM") names the principle of taking defects seriously; the new cross-reference and Behavior Rule Always #14 wire the principle to a mechanical sequencing rule (Phase 1 evidence captured as receipt before fix proposal). The same upgrade DO IT RIGHT #1a (coupled-surface coherence) received when it landed alongside `gz validate --advisory-scorecard` enforcement.

4. **Aligns with ADR-0.18.0 subagent dispatch.** The `investigator` persona slots into the existing implementer/spec-reviewer/quality-reviewer triad as a seventh peer. The dispatch surface (Behavior Rule Always #14: "spawn `investigator` subagent") inherits ADR-0.18.0's already-attested model with no re-architecture. Context isolation for hypothesis formation comes for free because the investigator runs in its own subagent context.

5. **GHI lifecycle becomes the cross-session memory of debugging events.** Phase-1 evidence on cross-brief defects routes to `/ghi-author` before commit; Phase-4 fix-lands routes to `/ghi-close` with the Phase-1 evidence trail; Phase-4.5 architecture pauses route to `/ghi-author` for architectural GHIs labeled as foundation-ADR candidates. The recurring failure-mode memory shifts from in-context narrative recall (the named anti-pattern in `agent-failure-modes.md`) to ledger-witnessed GHIs the operator and future agents can cite.

6. **Investigator-only adoption is operator-bounded.** The full superpowers SDD bundle adoption is deferred to a separate GHI per operator's *"the whole bundle could be powerful"* framing. This ADR ships the smallest slice that closes the named failure class; bundle adoption remains an option without committing to it now.

7. **Skill carries `model: opus` per the routing matrix.** Hypothesis formation, novel root-cause reasoning, and architectural-pause judgment are the canonical Opus work types per `.claude/rules/model-selection.md` § routing matrix. The skill declaration locks the contract; no runtime detection, no inference, no degradation under context pressure.

8. **One ADR, five OBPIs, one Gate 5 ceremony per OBPI.** Foundation-kind brief-level attestation discipline applies; each OBPI gets independent witness. The decomposition is one OBPI per separable surface (skill, persona, AGENTS.md integration, GHI cross-links, rule file) — no fragmentation, no bundling.

### Negative

1. **DO IT RIGHT grows from 9 → 11 operative claims.** Adding two new claims (Iron Law precondition + 3+-failed-fixes-architecture-pause) bloats the always-loaded surface. Mitigated by the existing precedent: DO IT RIGHT already carries 9 claims plus the failure-mode taxonomy reference; two more claims with a one-line skill pointer (not inline-expanded) is incremental. The 5:1 governance-to-output ratio (Anti-vibing operative claim 1) is the product — adding two more operative claims in defense of a named failure class is on-doctrine, not overhead.

2. **+1 skill and +1 persona on the canonical surface.** Adds `gz-systematic-debug` to the 67-skill catalog and `investigator` to the 6-persona catalog. Both surfaces are sync-checked by `gz agent sync control-surfaces`; the surface-cost is real but bounded. Mitigated by the operator-bounded scope decision (investigator-only adoption, not the full SDD bundle).

3. **Debugging-impulse agents may feel friction.** An agent that pattern-matches a fix from training-corpus memory now has to capture Phase-1 evidence as a receipt before proposing the fix — that's an extra ARB step invocation and a structural pause on the fix-impulse. **Pre-mortem scenario:** 18 months from now, this decision failed because the Iron Law became performative — agents go through the motions of phase-naming ("Phase 1: root cause is X") without actually running ARB step commands that capture the evidence as a receipt, and reviewers stop noticing because the phase-naming looks compliant. **Mitigation:** the Iron Law cites the ARB step receipt as the structural witness (not a narrative claim), parallel to how `gz obpi complete` rejects fabricated receipt IDs (Attestation discipline). Phase-1 evidence without a real `arb-step-root-cause-trace-*` receipt is the same class of failure as Stage-2 implementation without a real `arb-step-unittest-*` receipt — caught structurally, not by review.

4. **ARB receipt requirement may produce ceremony-shaped evidence rather than actual investigation.** **Pre-mortem scenario:** 18 months from now, this decision failed because the `arb-step-root-cause-trace-*` receipts contain plausible-looking but content-empty traces — agents learned to satisfy the receipt requirement with shallow trace output that satisfies the regex but doesn't actually trace root cause. **Mitigation:** the skill's Phase-1 instructions name three concrete artifacts the trace MUST contain (the failing assertion's actual vs expected output captured verbatim, the call-graph between the failure site and the nearest validated invariant, and the data-flow trace from the input to the assertion). Future GHI promotion to mechanical (`gz validate --systematic-debug-coupling`) can extend to receipt-content validation, not just receipt-existence.

5. **Investigator persona may become performative.** **Pre-mortem scenario:** 18 months from now, this decision failed because agents dispatch the investigator subagent but the subagent's prompt template skips Phase 1 evidence capture in favor of returning a fix recommendation — the persona name appears in dispatch logs but the persona's behavioral identity is not actually adopted. **Mitigation:** the persona file's grounding paragraph names the refusal-to-propose-fix-without-evidence behavior as the persona's identity, parallel to how `quality-reviewer` is identified by structural-coherence-not-style discipline. The persona dispatch attestation surface (ADR-pool.obpi-pipeline-dispatch-attestation, awaiting promotion) provides the future mechanical defense.

6. **Reversibility: this is a one-way door at the canon level.** Once AGENTS.md operative claims #10 and #11 land, the Iron Law (precondition) and 3+-failed-fixes-architecture-pause are constitutional invariants; reversal in 12 months would require an ADR amendment ceremony to remove them. Justified by the recurring failure-mode evidence: the door we're closing is one that was producing the `Skipped cheap verification` failure class repeatedly. The asymmetry is intentional; the cost of leaving it open exceeds the cost of closing it.

7. **The 2am operator scenario:** an operator on-call at 2am has a test failing in CI, needs to ship a fix, and the Iron Law refuses any fix proposal without a Phase-1 ARB step receipt. **Mitigation:** the Iron Law applies at the agent's fix-proposal surface (the agent must capture the receipt before proposing); it does not block the operator from running a direct fix themselves. The operator's manual fix is outside the agent contract; the receipt capture is fast (the ARB step wrapper takes seconds). No escape hatch needed because the friction is fast and intentional.

8. **Forward dependency: future ADR for `investigator` subagent writing to `agent-insights.jsonl`.** When the 3+-failed-fixes-architecture-pause fires, today the agent must remember to append an `improvement` record per Behavior Rule Always #11. A future ADR could automate this by having the investigator subagent emit the record automatically when Phase 4.5 fires. This is a forward-reference, not a blocker for this ADR — Behavior Rule Always #11 already covers the manual case.

9. **Forward dependency: mechanical promotion of `systematic-debugging.md` rule to a `gz validate` scope.** The rule lands advisory in this ADR; mechanical promotion (e.g. checking commit subjects for `fix(<scope>):` and trailers for ARB step receipts on cross-brief defects) is a future GHI target named in OBPI-05. This is the standard advisory-then-promote pattern documented in `docs/governance/advisory-rules-audit.md`; the rule's loading posture is named in the rule body so future agents can see the promotion roadmap.

10. **Risk: documentation-defect-vs-behavior-defect confusion.** If agents already do root-cause investigation but report it poorly (i.e. the failure is in how they NARRATE the work, not how they DO it), the structural defense added here is mis-targeted — it forces a receipt-capture step on agents who are already investigating, with no behavioral change. **Mitigation:** gzkit's history (GHIs #263, #290, #309) names concrete instances where the failure was the investigation itself, not its narration — pattern-matched plausible-looking fixes that didn't trace root cause. The Pre-Mortem scenario in negative consequence #4 (ceremony-shaped evidence rather than actual investigation) is the live risk after this ADR; the live risk before this ADR is the failure class the ADR closes.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.49-01: Author `gz-systematic-debug` skill at `.gzkit/skills/gz-systematic-debug/SKILL.md` (model: opus; lifecycle_state: active; no gz_command — methodology like gz-design). Includes Iron Law (precondition form, fenced block, same typography as gz-obpi-pipeline/gz-patch-release), four phases (Root Cause / Pattern / Hypothesis / Implementation), 3+-failed-fixes-architecture-pause rule, Red-Flags + Operator-Signals dictionaries, adapted supporting references (root-cause-tracing.md, defense-in-depth.md, condition-based-waiting.md translated to Python/gzkit vocabulary), ARB-receipt integration for Phase-1 evidence (uv run gz arb step --name root-cause-trace).
- [ ] OBPI-0.0.49-02: Author `investigator` persona at `.gzkit/personas/investigator.md` with traits (evidence-first, hypothesis-discipline, fix-impulse-suspending, architecture-questioning), anti-traits (patch-first-instinct, single-hypothesis-fixation, symptom-fixation, narrative-recall-substitution-for-evidence), and grounding paragraph naming the refusal-to-propose-fix-without-evidence behavior. Dispatchable as subagent peer to existing implementer/spec-reviewer/quality-reviewer triad under ADR-0.18.0.
- [ ] OBPI-0.0.49-03: AGENTS.md integration (single OBPI for coupled edits): DO IT RIGHT operative claim #10 (Iron Law precondition form citing gz-systematic-debug), DO IT RIGHT operative claim #11 (3+-failed-fixes-architecture-pause routing to /ghi-author), PRIME DIRECTIVE item #5 one-line cross-reference, Behavior Rule Always #14 (spawn investigator subagent with gz-systematic-debug; Phase 1 evidence captured as ARB step receipt before fix proposal), update Persona table (add investigator as seventh persona), update Skills catalog (add gz-systematic-debug under Code Quality).
- [ ] OBPI-0.0.49-04: Cross-link GHI skills to systematic debugging: edit .gzkit/skills/ghi-author/SKILL.md and .gzkit/skills/ghi-close/SKILL.md to add a Systematic Debugging coupling subsection naming three coupling points (Phase 1 evidence + cross-brief defect → /ghi-author before commit; Phase 4 fix lands → /ghi-close with Phase-1 evidence trail in body; Phase 4.5 architecture pause → /ghi-author for architectural GHI labeled as foundation-ADR candidate).
- [ ] OBPI-0.0.49-05: Author .gzkit/rules/systematic-debugging.md rule file with body-version 0.1.0, scoped paths (likely **/*.py and **/*.md), encoding the three coupling points as enforceable doctrine and adding scorecard entry to docs/governance/advisory-rules-audit.md (loading posture: advisory; future GHI promotion target: gz validate --systematic-debug-coupling validator scope).

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-05-17T19:42:08.233952*

### Q: What is the ADR identifier? (e.g., ADR-0.1.0)

**A:** ADR-0.0.49

### Q: What is the title of this ADR?

**A:** Systematic Debugging Discipline

### Q: What is the semantic version?

**A:** 0.0.49

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit's PRIME DIRECTIVE and DO IT RIGHT pillars name the principle of root-cause investigation but provide no structural sequencing rule that forces it before a fix is proposed. The result is a class of failure already named in `.gzkit/rules/agent-failure-modes.md`: agents pattern-match a plausible-looking fix from training-corpus memory (`Skipped cheap verification`), commit it, watch it fail, then propose a second fix on top of the first, then a third — never recognizing that the third failure is no longer about the next patch but about wrong architecture. The recurring shape across gzkit's own history is visible in GHIs #263 (skipped-verification regression), #309 (cosmetic @covers backfill that silenced audit-check without re-derived semantics), and the multi-fix-attempt patterns that motivated the defect-fix routing thresholds in AGENTS.md.

The operator named the gap explicitly: *"I think PRIME DIRECTIVE and DO IT RIGHT could be meaningfully assisted by how superpowers handles systematic debugging."* The [superpowers systematic-debugging skill](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) supplies an empirically-tested Iron Law (precondition form: *"NO FIX MAY BE PROPOSED UNTIL ROOT-CAUSE EVIDENCE IS CAPTURED"*), a four-phase procedure (Root Cause / Pattern / Hypothesis / Implementation), a three-failed-fixes-architecture-pause rule, and supporting techniques (`root-cause-tracing`, `defense-in-depth`, `condition-based-waiting`). The shape mirrors gzkit's existing two Iron Laws — `gz-obpi-pipeline` (*"THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES"*) and `gz-patch-release` (*"ONCE THE OPERATOR APPROVES, THE CEREMONY FLOWS TO COMPLETION"*) — on a different axis: precondition rather than completion, but identical typography, all-caps fenced-block opening line, and rationalization-prevention table downstream.

The additional operator framing: *"ensure that PRIME DIRECTIVE and DO IT RIGHT reach for this and, perhaps we need a persona to go along with it so that it is triggered by an agent"* — naming both the doctrine-attestation surface (AGENTS.md operative claims must reach for the skill) and the persona-dispatch surface (an `investigator` persona, dispatchable as a subagent peer to the existing implementer/spec-reviewer/quality-reviewer triad under ADR-0.18.0's subagent-driven model). The further operator framing: *"all of these will always require GHIs, so tying the GHI skills into this would triangulate well"* — naming the third coupling point (the GHI lifecycle as the cross-session memory of debugging events: Phase 1 evidence routes to `/ghi-author` before commit if cross-brief; Phase 4 fix lands via `/ghi-close` with Phase-1 evidence trail; Phase 4.5 architecture pause routes to `/ghi-author` for an architectural GHI labeled as a foundation-ADR candidate).

This ADR codifies systematic debugging as a foundation-attested invariant: a dedicated skill (`gz-systematic-debug`), a dispatchable persona (`investigator`), two new DO IT RIGHT operative claims (Iron Law precondition + 3-failed-fixes-architecture-pause), an explicit PRIME DIRECTIVE cross-reference, a Behavior Rule wiring the skill to the persona at the trigger surface (any bug / test failure / unexpected behavior spawns the investigator with the skill, captures Phase 1 evidence as an ARB step receipt before any fix proposal), GHI-skill cross-links at three coupling points, and a scoped rule file. The ADR is foundation kind because it shapes how gzkit agents debug, not what they ship. The lane is heavy because it binds agent behavior across every surface, introduces a new skill + new persona + new rule, and modifies AGENTS.md operative-claims sections.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Promote systematic debugging from an unnamed principle inside PRIME DIRECTIVE / DO IT RIGHT to a foundation-attested invariant with five mechanical surfaces, decomposed into five OBPIs.

**The invariant (canonical statement):** When an agent encounters a bug, test failure, or unexpected behavior, the agent dispatches the `investigator` subagent persona under the `gz-systematic-debug` skill and captures Phase-1 root-cause evidence as an ARB step receipt BEFORE proposing any fix. After three failed fix attempts on the same defect, the failure class is wrong architecture, not the next patch — the agent STOPs the fix loop and routes to the operator as an architectural GHI (foundation-ADR candidate) via `/ghi-author`. Cross-brief Phase-1 evidence and architectural pauses route through the GHI lifecycle.

**Decision items (1:1 with Feature Checklist below):**

1. **Author `gz-systematic-debug` skill** at `.gzkit/skills/gz-systematic-debug/SKILL.md` (`model: opus` per `.claude/rules/model-selection.md` — judgment-class hypothesis formation; `lifecycle_state: active`; no `gz_command:` — methodology like `gz-design`, not CLI-backed). Skill carries the Iron Law (precondition form, fenced block, same typography as `gz-obpi-pipeline`/`gz-patch-release`); the four phases (Root Cause / Pattern / Hypothesis / Implementation); a Red-Flags dictionary (e.g. *"this looks easy, just patch it"*, *"the error message is probably wrong"*, *"this worked before, I'll just retry"*) and an Operator-Signals dictionary (e.g. operator says *"we've fixed this before"*, operator interjects *"why did you skip X"*, operator names a class-of-failure word like *"architecture"*); the 3+-failed-fixes-architecture-pause rule with the explicit STOP-and-route-to-operator language; adapted supporting references (`root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md` translated to Python/gzkit vocabulary); ARB-receipt integration for Phase-1 evidence (Phase 1 evidence MUST be captured via `uv run gz arb step --name root-cause-trace -- ...` and the resulting `arb-step-root-cause-trace-*` receipt cited in the fix-proposal commit message).

2. **Author `investigator` persona** at `.gzkit/personas/investigator.md`. Traits: `evidence-first`, `hypothesis-discipline`, `fix-impulse-suspending`, `architecture-questioning`. Anti-traits: `patch-first-instinct`, `single-hypothesis-fixation`, `symptom-fixation`, `narrative-recall-substitution-for-evidence`. Grounding paragraph names the persona's behavioral identity as the agent who refuses to propose a fix until root-cause evidence is captured as a receipt. Persona is dispatchable as a subagent peer to the existing implementer/spec-reviewer/quality-reviewer triad under ADR-0.18.0-subagent-driven-pipeline-execution; the persona row added to AGENTS.md § Persona table (becoming the seventh persona).

3. **AGENTS.md integration** (single OBPI for coupled edits): (a) Add DO IT RIGHT operative claim #10 — the Iron Law (precondition form) verbatim, citing `gz-systematic-debug` as the procedure of record; (b) Add DO IT RIGHT operative claim #11 — the 3+-failed-fixes-architecture-pause rule, citing `/ghi-author` as the routing surface; (c) Add a one-line cross-reference under PRIME DIRECTIVE item #5 (*"defect surfaced in flight → invoke `gz-systematic-debug` before proposing fix"*); (d) Add Behavior Rule Always #14 — *"On bug / test failure / unexpected behavior: spawn `investigator` subagent with `gz-systematic-debug`; Phase 1 evidence captured as ARB step receipt before fix proposal"*; (e) Update the § Persona table to add the `investigator` row (seventh persona); (f) Update the § Skills catalog to add `gz-systematic-debug` under the Code Quality cluster.

4. **Cross-link GHI skills to systematic debugging.** Edit `.gzkit/skills/ghi-author/SKILL.md` and `.gzkit/skills/ghi-close/SKILL.md` to add a "Systematic Debugging coupling" subsection naming the three coupling points: (a) **Phase 1 evidence + cross-brief defect → `/ghi-author` before commit** — when Phase-1 root-cause evidence shows the defect crosses brief boundaries (the direct-fix routing thresholds in AGENTS.md fail), the agent files a GHI via `/ghi-author` before committing the fix, with the ARB step receipt ID cited in the GHI body; (b) **Phase 4 fix lands → `/ghi-close` with Phase-1 evidence trail in body** — when a fix lands and a GHI exists for the defect, the closing comment cites the Phase-1 ARB receipt ID and the four-phase decision trail; (c) **Phase 4.5 architecture pause → `/ghi-author` for architectural GHI labeled as foundation-ADR candidate** — when the 3+-failed-fixes-architecture-pause rule fires, the agent files an architectural GHI via `/ghi-author` with the three prior fix-attempt receipts cited, labeled as a foundation-ADR candidate so the operator routes it to ADR ceremony rather than a fourth patch.

5. **Author `.gzkit/rules/systematic-debugging.md` rule file** with body-version `0.1.0`, scoped `paths:` (likely `**/*.py` and `**/*.md` — debug discipline binds globally), encoding the three coupling points as enforceable doctrine and adding a scorecard entry to `docs/governance/advisory-rules-audit.md`. Loading posture: advisory (no mechanical gate in this ADR). Future GHI promotion target: `gz validate --systematic-debug-coupling` validator scope that checks every commit with `fix(<scope>):` subject for an `arb-step-root-cause-trace-*` receipt trailer when the touched files span >1 brief allowlist, and every architectural GHI for the three-prior-receipts-cited pattern.

**Sequencing:** OBPI-01 (skill) and OBPI-02 (persona) land in parallel — both are content authoring with no inter-dependency. OBPI-03 (AGENTS.md integration) depends on OBPI-01 and OBPI-02 because it cites them. OBPI-04 (GHI skill cross-links) depends on OBPI-01 because it cites the skill's phase names. OBPI-05 (rule file + scorecard) depends on OBPI-03 and OBPI-04 because it codifies their coupling.

**Lane: Heavy.** New skill + new persona + new rule + AGENTS.md operative-claims change all trigger heavy-lane rigor per `.gzkit/rules/skill-surface-sync.md` (new canonical surface entries) and `.claude/rules/cli.md` (no new CLI verb, but new agent-binding surfaces). Foundation-kind brief-level Gate 5 stacks on top per ADR-0.0.36-universal-obpi-attestation.

**Subagent scope (operator-bounded):** This ADR adopts only the investigator-only persona slice of superpowers's [systematic-debugging](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) plus its supporting techniques translated to Python/gzkit vocabulary. Operator deferred the full SDD prompt-template bundle adoption from [superpowers/subagent-driven-development](https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development) to a separate future GHI per: *"We have already partially adopted SP's approach to this ... but the whole bundle could be powerful."*

**Scope boundary — what this ADR explicitly does NOT do:**

- Does NOT adopt the full superpowers SDD (subagent-driven-development) prompt-template bundle — operator-deferred to a separate future GHI.
- Does NOT re-architect ADR-0.18.0's subagent dispatch model — the `investigator` persona slots into the existing model as a seventh peer.
- Does NOT promote `systematic-debugging.md` to a mechanical validator scope — the rule loads as advisory in this ADR; mechanical promotion (e.g. `gz validate --systematic-debug-coupling`) is a future GHI target named in OBPI-05.
- Does NOT modify the existing defect-fix routing thresholds in AGENTS.md § Defect-fix routing — those thresholds remain authoritative for the direct-fix vs OBPI-ceremony decision; systematic debugging sits upstream as the precondition that produces the evidence the routing decision consumes.
- Does NOT modify the existing two Iron Laws (`gz-obpi-pipeline`, `gz-patch-release`) — the precondition-form Iron Law sits on a different axis (precondition rather than completion) and is additive.

### Q: What good things result from this decision? List benefits.

**A:** 1. **Closes the `Skipped cheap verification` failure class structurally** (per `.gzkit/rules/agent-failure-modes.md`). Today, the failure shape is caught only by post-hoc review (cosmetic @covers backfill heuristic GHI #309, fabrication ARB-receipt discipline GHI #290). After this ADR, the failure is caught upstream: the Iron Law (precondition) refuses any fix proposal without a captured ARB step receipt for Phase-1 root-cause evidence, and the 3+-failed-fixes-architecture-pause closes the multi-patch failure loop the routing-threshold table can't catch.

2. **Reuses superpowers's empirically-tested protocol rather than re-deriving it.** The four-phase procedure, the Iron Law shape, and the three-failed-fixes-architecture-pause rule are battle-tested in superpowers's [systematic-debugging](https://github.com/obra/superpowers/tree/main/skills/systematic-debugging) corpus. Adopting the shape (translated to gzkit/Python vocabulary) gets the structural defense without the cost of empirical iteration on what a debugging protocol should look like.

3. **Lifts gzkit's PRIME DIRECTIVE from principle-only to structurally-gated.** PRIME DIRECTIVE item #5 ("FLAG DEFECTS, NEVER EXCUSE THEM") names the principle of taking defects seriously; the new cross-reference and Behavior Rule Always #14 wire the principle to a mechanical sequencing rule (Phase 1 evidence captured as receipt before fix proposal). The same upgrade DO IT RIGHT #1a (coupled-surface coherence) received when it landed alongside `gz validate --advisory-scorecard` enforcement.

4. **Aligns with ADR-0.18.0 subagent dispatch.** The `investigator` persona slots into the existing implementer/spec-reviewer/quality-reviewer triad as a seventh peer. The dispatch surface (Behavior Rule Always #14: "spawn `investigator` subagent") inherits ADR-0.18.0's already-attested model with no re-architecture. Context isolation for hypothesis formation comes for free because the investigator runs in its own subagent context.

5. **GHI lifecycle becomes the cross-session memory of debugging events.** Phase-1 evidence on cross-brief defects routes to `/ghi-author` before commit; Phase-4 fix-lands routes to `/ghi-close` with the Phase-1 evidence trail; Phase-4.5 architecture pauses route to `/ghi-author` for architectural GHIs labeled as foundation-ADR candidates. The recurring failure-mode memory shifts from in-context narrative recall (the named anti-pattern in `agent-failure-modes.md`) to ledger-witnessed GHIs the operator and future agents can cite.

6. **Investigator-only adoption is operator-bounded.** The full superpowers SDD bundle adoption is deferred to a separate GHI per operator's *"the whole bundle could be powerful"* framing. This ADR ships the smallest slice that closes the named failure class; bundle adoption remains an option without committing to it now.

7. **Skill carries `model: opus` per the routing matrix.** Hypothesis formation, novel root-cause reasoning, and architectural-pause judgment are the canonical Opus work types per `.claude/rules/model-selection.md` § routing matrix. The skill declaration locks the contract; no runtime detection, no inference, no degradation under context pressure.

8. **One ADR, five OBPIs, one Gate 5 ceremony per OBPI.** Foundation-kind brief-level attestation discipline applies; each OBPI gets independent witness. The decomposition is one OBPI per separable surface (skill, persona, AGENTS.md integration, GHI cross-links, rule file) — no fragmentation, no bundling.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. **DO IT RIGHT grows from 9 → 11 operative claims.** Adding two new claims (Iron Law precondition + 3+-failed-fixes-architecture-pause) bloats the always-loaded surface. Mitigated by the existing precedent: DO IT RIGHT already carries 9 claims plus the failure-mode taxonomy reference; two more claims with a one-line skill pointer (not inline-expanded) is incremental. The 5:1 governance-to-output ratio (Anti-vibing operative claim 1) is the product — adding two more operative claims in defense of a named failure class is on-doctrine, not overhead.

2. **+1 skill and +1 persona on the canonical surface.** Adds `gz-systematic-debug` to the 67-skill catalog and `investigator` to the 6-persona catalog. Both surfaces are sync-checked by `gz agent sync control-surfaces`; the surface-cost is real but bounded. Mitigated by the operator-bounded scope decision (investigator-only adoption, not the full SDD bundle).

3. **Debugging-impulse agents may feel friction.** An agent that pattern-matches a fix from training-corpus memory now has to capture Phase-1 evidence as a receipt before proposing the fix — that's an extra ARB step invocation and a structural pause on the fix-impulse. **Pre-mortem scenario:** 18 months from now, this decision failed because the Iron Law became performative — agents go through the motions of phase-naming ("Phase 1: root cause is X") without actually running ARB step commands that capture the evidence as a receipt, and reviewers stop noticing because the phase-naming looks compliant. **Mitigation:** the Iron Law cites the ARB step receipt as the structural witness (not a narrative claim), parallel to how `gz obpi complete` rejects fabricated receipt IDs (Attestation discipline). Phase-1 evidence without a real `arb-step-root-cause-trace-*` receipt is the same class of failure as Stage-2 implementation without a real `arb-step-unittest-*` receipt — caught structurally, not by review.

4. **ARB receipt requirement may produce ceremony-shaped evidence rather than actual investigation.** **Pre-mortem scenario:** 18 months from now, this decision failed because the `arb-step-root-cause-trace-*` receipts contain plausible-looking but content-empty traces — agents learned to satisfy the receipt requirement with shallow trace output that satisfies the regex but doesn't actually trace root cause. **Mitigation:** the skill's Phase-1 instructions name three concrete artifacts the trace MUST contain (the failing assertion's actual vs expected output captured verbatim, the call-graph between the failure site and the nearest validated invariant, and the data-flow trace from the input to the assertion). Future GHI promotion to mechanical (`gz validate --systematic-debug-coupling`) can extend to receipt-content validation, not just receipt-existence.

5. **Investigator persona may become performative.** **Pre-mortem scenario:** 18 months from now, this decision failed because agents dispatch the investigator subagent but the subagent's prompt template skips Phase 1 evidence capture in favor of returning a fix recommendation — the persona name appears in dispatch logs but the persona's behavioral identity is not actually adopted. **Mitigation:** the persona file's grounding paragraph names the refusal-to-propose-fix-without-evidence behavior as the persona's identity, parallel to how `quality-reviewer` is identified by structural-coherence-not-style discipline. The persona dispatch attestation surface (ADR-pool.obpi-pipeline-dispatch-attestation, awaiting promotion) provides the future mechanical defense.

6. **Reversibility: this is a one-way door at the canon level.** Once AGENTS.md operative claims #10 and #11 land, the Iron Law (precondition) and 3+-failed-fixes-architecture-pause are constitutional invariants; reversal in 12 months would require an ADR amendment ceremony to remove them. Justified by the recurring failure-mode evidence: the door we're closing is one that was producing the `Skipped cheap verification` failure class repeatedly. The asymmetry is intentional; the cost of leaving it open exceeds the cost of closing it.

7. **The 2am operator scenario:** an operator on-call at 2am has a test failing in CI, needs to ship a fix, and the Iron Law refuses any fix proposal without a Phase-1 ARB step receipt. **Mitigation:** the Iron Law applies at the agent's fix-proposal surface (the agent must capture the receipt before proposing); it does not block the operator from running a direct fix themselves. The operator's manual fix is outside the agent contract; the receipt capture is fast (the ARB step wrapper takes seconds). No escape hatch needed because the friction is fast and intentional.

8. **Forward dependency: future ADR for `investigator` subagent writing to `agent-insights.jsonl`.** When the 3+-failed-fixes-architecture-pause fires, today the agent must remember to append an `improvement` record per Behavior Rule Always #11. A future ADR could automate this by having the investigator subagent emit the record automatically when Phase 4.5 fires. This is a forward-reference, not a blocker for this ADR — Behavior Rule Always #11 already covers the manual case.

9. **Forward dependency: mechanical promotion of `systematic-debugging.md` rule to a `gz validate` scope.** The rule lands advisory in this ADR; mechanical promotion (e.g. checking commit subjects for `fix(<scope>):` and trailers for ARB step receipts on cross-brief defects) is a future GHI target named in OBPI-05. This is the standard advisory-then-promote pattern documented in `docs/governance/advisory-rules-audit.md`; the rule's loading posture is named in the rule body so future agents can see the promotion roadmap.

10. **Risk: documentation-defect-vs-behavior-defect confusion.** If agents already do root-cause investigation but report it poorly (i.e. the failure is in how they NARRATE the work, not how they DO it), the structural defense added here is mis-targeted — it forces a receipt-capture step on agents who are already investigating, with no behavioral change. **Mitigation:** gzkit's history (GHIs #263, #290, #309) names concrete instances where the failure was the investigation itself, not its narration — pattern-matched plausible-looking fixes that didn't trace root cause. The Pre-Mortem scenario in negative consequence #4 (ceremony-shaped evidence rather than actual investigation) is the live risk after this ADR; the live risk before this ADR is the failure class the ADR closes.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Author `gz-systematic-debug` skill at `.gzkit/skills/gz-systematic-debug/SKILL.md` (model: opus; lifecycle_state: active; no gz_command — methodology like gz-design). Includes Iron Law (precondition form, fenced block, same typography as gz-obpi-pipeline/gz-patch-release), four phases (Root Cause / Pattern / Hypothesis / Implementation), 3+-failed-fixes-architecture-pause rule, Red-Flags + Operator-Signals dictionaries, adapted supporting references (root-cause-tracing.md, defense-in-depth.md, condition-based-waiting.md translated to Python/gzkit vocabulary), ARB-receipt integration for Phase-1 evidence (uv run gz arb step --name root-cause-trace).
2. Author `investigator` persona at `.gzkit/personas/investigator.md` with traits (evidence-first, hypothesis-discipline, fix-impulse-suspending, architecture-questioning), anti-traits (patch-first-instinct, single-hypothesis-fixation, symptom-fixation, narrative-recall-substitution-for-evidence), and grounding paragraph naming the refusal-to-propose-fix-without-evidence behavior. Dispatchable as subagent peer to existing implementer/spec-reviewer/quality-reviewer triad under ADR-0.18.0.
3. AGENTS.md integration (single OBPI for coupled edits): DO IT RIGHT operative claim #10 (Iron Law precondition form citing gz-systematic-debug), DO IT RIGHT operative claim #11 (3+-failed-fixes-architecture-pause routing to /ghi-author), PRIME DIRECTIVE item #5 one-line cross-reference, Behavior Rule Always #14 (spawn investigator subagent with gz-systematic-debug; Phase 1 evidence captured as ARB step receipt before fix proposal), update Persona table (add investigator as seventh persona), update Skills catalog (add gz-systematic-debug under Code Quality).
4. Cross-link GHI skills to systematic debugging: edit .gzkit/skills/ghi-author/SKILL.md and .gzkit/skills/ghi-close/SKILL.md to add a Systematic Debugging coupling subsection naming three coupling points (Phase 1 evidence + cross-brief defect → /ghi-author before commit; Phase 4 fix lands → /ghi-close with Phase-1 evidence trail in body; Phase 4.5 architecture pause → /ghi-author for architectural GHI labeled as foundation-ADR candidate).
5. Author .gzkit/rules/systematic-debugging.md rule file with body-version 0.1.0, scoped paths (likely **/*.py and **/*.md), encoding the three coupling points as enforceable doctrine and adding scorecard entry to docs/governance/advisory-rules-audit.md (loading posture: advisory; future GHI promotion target: gz validate --systematic-debug-coupling validator scope).

### Q: What alternatives were considered and why were they rejected?

**A:** 1. **GHI-only fixes (status quo + GHI per debugging event).** REJECTED by operator. A GHI per debugging event preserves the artifact trail but does not promote systematic debugging to a foundation-attested invariant — the failure class (`Skipped cheap verification` per agent-failure-modes.md) remains unmechanized. GHIs are the cross-session memory the new doctrine routes through (per coupling-point #1 and #3); they are not a substitute for the doctrine itself.

2. **Pool ADR (defer foundation-attestation, document the intent only).** OPERATOR-DEFERRED at the routing decision. Promoting to pool would document the intent without committing the foundation-kind ceremony. Operator's decision verbatim: *"Foundation ADR + OBPIs (heavy ceremony, identity-shaping commit)"* — closes the failure class structurally rather than queueing it.

3. **Skip the persona, ship the skill only.** REJECTED by operator. Without the `investigator` persona, the skill is a procedure with no behavioral identity to dispatch — the same skill could be invoked from main-session, implementer, or another persona's context without the refusal-to-propose-fix-without-evidence anchor. Operator: *"perhaps we need a persona to go along with it so that it is triggered by an agent."* The persona is the dispatch-time behavioral anchor; the skill is the procedure of record. Both are required.

4. **Adopt the full superpowers SDD (subagent-driven-development) prompt-template bundle now.** OPERATOR-DEFERRED to a separate future GHI. The bundle adoption is a larger surface change (template scaffolding, prompt patterns, subagent dispatch primitives) that benefits from being scoped in its own ceremony. Operator: *"We have already partially adopted SP's approach to this (https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development), but the whole bundle could be powerful."* This ADR scopes the systematic-debugging slice only; bundle adoption remains a follow-up option.

5. **Single Iron Law usage instead of three.** REJECTED — the precondition-form Iron Law sits on a different axis from the existing two (`gz-obpi-pipeline`'s completion-form, `gz-patch-release`'s flow-form). They share typography (all-caps, fenced-block, opening-line) but address distinct failure modes. Folding the precondition form into either existing Iron Law would dilute both — the completion-form is about not stopping mid-ceremony, the precondition-form is about not starting without evidence.

6. **Author the rule file alone, no skill, no persona, no AGENTS.md changes.** REJECTED — rules are loaded contextually, not always-loaded. A rule without an AGENTS.md cross-link is invisible to the agent at decision time; a rule without a skill has no procedural anchor; a rule without a persona has no dispatch surface. The five OBPIs are co-load-bearing (the rule formalizes the three coupling points that the skill and persona and AGENTS.md changes establish).

7. **Embed the four-phase procedure inline in AGENTS.md DO IT RIGHT.** REJECTED — AGENTS.md DO IT RIGHT is a bullet list of operative claims; embedding a four-phase procedure inline bloats the always-loaded surface beyond the diet budget (`gz validate --instructions-files-budget` enforces per-file char limits). The skill is the right home for the procedure; AGENTS.md carries the operative claim that references the skill.

8. **No 3+-failed-fixes-architecture-pause rule (just the precondition Iron Law).** REJECTED — the two rules address distinct failure modes. The precondition Iron Law catches the *"skip root-cause, jump to fix"* failure (the named `Skipped cheap verification` shape). The 3+-failed-fixes rule catches the *"keep patching past the point where this should have escalated"* failure (the unnamed multi-patch failure loop that the routing-threshold table can't see because each individual patch is small enough to pass direct-fix thresholds). Both are required to close the named failure class structurally.

9. **Use superpowers's exact prompt-template language verbatim without translation to Python/gzkit vocabulary.** REJECTED — the supporting references (`root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`) name examples in JavaScript/Node idioms that don't translate cleanly to gzkit's stdlib-first Python posture. Adopting the structural shape (four phases, Iron Law, 3+-failed-fixes rule) and translating examples to Python/gzkit-CLI vocabulary is the on-doctrine choice; verbatim adoption would import vocabulary mismatch as a permanent surface defect.

10. **Defer the rule file (OBPI-05) — skill carries the protocol, rule file is redundant.** CONSIDERED at scope minimization but REJECTED. The skill carries the protocol but is loaded only at dispatch time; the rule file carries the three coupling points (skill / persona / GHI) and binds globally via `paths:` scope. Without the rule file, the coupling between skill+persona+GHI is described in the ADR but has no advisory-rules-audit scorecard entry — future agents have no scoped doctrine surface to consult. The rule is the smallest surface that makes the coupling enforceable as a future mechanical promotion target.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

**Canonical surfaces this ADR creates or modifies (mechanical inventory):**

- `.gzkit/skills/gz-systematic-debug/SKILL.md` (new; OBPI-01)
- `.gzkit/skills/gz-systematic-debug/references/root-cause-tracing.md` (new; OBPI-01)
- `.gzkit/skills/gz-systematic-debug/references/defense-in-depth.md` (new; OBPI-01)
- `.gzkit/skills/gz-systematic-debug/references/condition-based-waiting.md` (new; OBPI-01)
- `.gzkit/personas/investigator.md` (new; OBPI-02)
- `AGENTS.md` § DO IT RIGHT (operative claims #10, #11 added; OBPI-03)
- `AGENTS.md` § PRIME DIRECTIVE (item #5 sub-bullet added; OBPI-03)
- `AGENTS.md` § Behavior Rules § Always (rule #14 added; OBPI-03)
- `AGENTS.md` § Persona (investigator row added; OBPI-03)
- `AGENTS.md` § Skills § Code Quality (gz-systematic-debug entry added; OBPI-03)
- `src/gzkit/templates/AGENTS.md` (lockstep edits; OBPI-03)
- `.gzkit/skills/ghi-author/SKILL.md` § Systematic Debugging coupling (new subsection; skill-version minor bump; OBPI-04)
- `.gzkit/skills/ghi-close/SKILL.md` § Systematic Debugging coupling (new subsection; skill-version minor bump; OBPI-04)
- `.gzkit/rules/systematic-debugging.md` (new; rule-version 0.1.0; OBPI-05)
- `docs/governance/advisory-rules-audit.md` (scorecard entry added; OBPI-05)

**Sync-managed derived surfaces (no hand edits; propagated by `uv run gz agent sync control-surfaces`):**

- `src/gzkit/skills/gz-systematic-debug/**`, `src/gzkit/personas/investigator.md`, `src/gzkit/rules/systematic-debugging.md`, `src/gzkit/skills/ghi-author/SKILL.md`, `src/gzkit/skills/ghi-close/SKILL.md` (wheel-shipping byte-parity copies)
- `.claude/skills/`, `.claude/personas/`, `.claude/rules/`, `.github/skills/`, `.github/instructions/`, `.agents/personas/` mirrors (vendor surfaces)

**Validation surfaces this ADR exercises:**

- `uv run gz validate --documents` — markdown schema + cross-link integrity
- `uv run gz validate --advisory-scorecard` — new rule has matching scorecard entry (OBPI-05)
- `uv run gz validate --instructions-files-budget` — AGENTS.md stays under 40k char budget after operative-claim additions (OBPI-03)
- `uv run gz validate --unscoped-rules` — new rule's `paths:` scope is named, not `**`-only (OBPI-05)
- `uv run gz arb ruff`, `uv run gz arb typecheck`, `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` — canonical attestation receipts per AGENTS.md § Attestation

**Future GHI promotion target (out of this ADR's scope; named for traceability):**

- `gz validate --systematic-debug-coupling` — mechanical validator that checks (a) every commit with `fix(<scope>):` subject for an `arb-step-root-cause-trace-*` receipt trailer when touched files span >1 brief allowlist, (b) every architectural GHI labeled `foundation-ADR-candidate` for the three-prior-receipts-cited pattern. Tracked in OBPI-05 § Loading posture.

- [ ] Tests: n/a (this ADR's deliverables are content — skill, persona, rule, AGENTS.md edits, scorecard entry; structural witness is `gz validate --documents`, `gz validate --advisory-scorecard`, ARB step receipts per OBPI)
- [ ] Docs: see `## Canonical surfaces` inventory above

## Alternatives Considered

1. **GHI-only fixes (status quo + GHI per debugging event).** REJECTED by operator. A GHI per debugging event preserves the artifact trail but does not promote systematic debugging to a foundation-attested invariant — the failure class (`Skipped cheap verification` per agent-failure-modes.md) remains unmechanized. GHIs are the cross-session memory the new doctrine routes through (per coupling-point #1 and #3); they are not a substitute for the doctrine itself.

2. **Pool ADR (defer foundation-attestation, document the intent only).** OPERATOR-DEFERRED at the routing decision. Promoting to pool would document the intent without committing the foundation-kind ceremony. Operator's decision verbatim: *"Foundation ADR + OBPIs (heavy ceremony, identity-shaping commit)"* — closes the failure class structurally rather than queueing it.

3. **Skip the persona, ship the skill only.** REJECTED by operator. Without the `investigator` persona, the skill is a procedure with no behavioral identity to dispatch — the same skill could be invoked from main-session, implementer, or another persona's context without the refusal-to-propose-fix-without-evidence anchor. Operator: *"perhaps we need a persona to go along with it so that it is triggered by an agent."* The persona is the dispatch-time behavioral anchor; the skill is the procedure of record. Both are required.

4. **Adopt the full superpowers SDD (subagent-driven-development) prompt-template bundle now.** OPERATOR-DEFERRED to a separate future GHI. The bundle adoption is a larger surface change (template scaffolding, prompt patterns, subagent dispatch primitives) that benefits from being scoped in its own ceremony. Operator: *"We have already partially adopted SP's approach to this (https://github.com/obra/superpowers/tree/main/skills/subagent-driven-development), but the whole bundle could be powerful."* This ADR scopes the systematic-debugging slice only; bundle adoption remains a follow-up option.

5. **Single Iron Law usage instead of three.** REJECTED — the precondition-form Iron Law sits on a different axis from the existing two (`gz-obpi-pipeline`'s completion-form, `gz-patch-release`'s flow-form). They share typography (all-caps, fenced-block, opening-line) but address distinct failure modes. Folding the precondition form into either existing Iron Law would dilute both — the completion-form is about not stopping mid-ceremony, the precondition-form is about not starting without evidence.

6. **Author the rule file alone, no skill, no persona, no AGENTS.md changes.** REJECTED — rules are loaded contextually, not always-loaded. A rule without an AGENTS.md cross-link is invisible to the agent at decision time; a rule without a skill has no procedural anchor; a rule without a persona has no dispatch surface. The five OBPIs are co-load-bearing (the rule formalizes the three coupling points that the skill and persona and AGENTS.md changes establish).

7. **Embed the four-phase procedure inline in AGENTS.md DO IT RIGHT.** REJECTED — AGENTS.md DO IT RIGHT is a bullet list of operative claims; embedding a four-phase procedure inline bloats the always-loaded surface beyond the diet budget (`gz validate --instructions-files-budget` enforces per-file char limits). The skill is the right home for the procedure; AGENTS.md carries the operative claim that references the skill.

8. **No 3+-failed-fixes-architecture-pause rule (just the precondition Iron Law).** REJECTED — the two rules address distinct failure modes. The precondition Iron Law catches the *"skip root-cause, jump to fix"* failure (the named `Skipped cheap verification` shape). The 3+-failed-fixes rule catches the *"keep patching past the point where this should have escalated"* failure (the unnamed multi-patch failure loop that the routing-threshold table can't see because each individual patch is small enough to pass direct-fix thresholds). Both are required to close the named failure class structurally.

9. **Use superpowers's exact prompt-template language verbatim without translation to Python/gzkit vocabulary.** REJECTED — the supporting references (`root-cause-tracing.md`, `defense-in-depth.md`, `condition-based-waiting.md`) name examples in JavaScript/Node idioms that don't translate cleanly to gzkit's stdlib-first Python posture. Adopting the structural shape (four phases, Iron Law, 3+-failed-fixes rule) and translating examples to Python/gzkit-CLI vocabulary is the on-doctrine choice; verbatim adoption would import vocabulary mismatch as a permanent surface defect.

10. **Defer the rule file (OBPI-05) — skill carries the protocol, rule file is redundant.** CONSIDERED at scope minimization but REJECTED. The skill carries the protocol but is loaded only at dispatch time; the rule file carries the three coupling points (skill / persona / GHI) and binds globally via `paths:` scope. Without the rule file, the coupling between skill+persona+GHI is described in the ADR but has no advisory-rules-audit scorecard entry — future agents have no scoped doctrine surface to consult. The rule is the smallest surface that makes the coupling enforceable as a future mechanical promotion target.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.49 | Pending | | | |
