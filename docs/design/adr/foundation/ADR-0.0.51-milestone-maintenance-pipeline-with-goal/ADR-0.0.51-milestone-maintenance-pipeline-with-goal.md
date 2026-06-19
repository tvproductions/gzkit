---
id: ADR-0.0.51-milestone-maintenance-pipeline-with-goal
status: Draft
kind: foundation
semver: 0.0.51
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-18
---

# ADR-0.0.51-milestone-maintenance-pipeline-with-goal: ADR Milestone Maintenance Pipeline with /goal-first-class Convergence (gz-adr-milestone-maintenance)

## Persona

`pipeline-orchestrator` — read `.gzkit/personas/pipeline-orchestrator.md`. Stage discipline, ceremony completion, and evidence anchoring are not rules to follow — they are who you are when running this pipeline. The milestone-maintenance orchestrator dispatches review-skill subagents in parallel during its sweep stage, then converges via `/goal` (Claude Code primary harness) or bounded iteration (Codex/Copilot fallback).

## Why foundation tier?

**Invariance test:** Without this ADR, gzkit would still be the project, but ADR-completion would not be a structural maintenance milestone. Every Validated ADR would land without a cross-codebase quality sweep, accumulating drift silently between releases. The milestone-maintenance discipline is the "service interval" doctrine (operator framing: "automobile manufacturer posts a recommended maintenance interval") — its absence is a port-level absence of the cadence contract.

**Port-vs-adapter framing:** This ADR is a **port** — it specifies WHEN the maintenance milestone fires (post-Validated, blocking next ADR until converged), WHAT must be checked (per-ADR-kind aware manifest of review skills), and HOW convergence is bounded (`/goal` first-class on Claude Code, bounded iteration on others). `gz-adr-milestone-maintenance` is the canonical adapter. Individual review skills dispatched by the sweep (e.g., `gz-architecture-review` from `ADR-pool.gz-architecture-review-skill`, `gz-tech-debt-review`, `gz-pythonic-pattern-detect`, `gz-complexity-advisor`) are adapters into the sweep manifest.

## Intent

ADR-0.0.50 (validation pipeline) codified the validation-phase orchestrator with redteam terminal stage. That pipeline fires per-ADR through `Completed → Validated`. The artifact lifecycle has a fourth pipeline beyond design / implementation / validation: a **maintenance milestone** pipeline that fires AFTER an ADR reaches `Validated` and performs a cross-codebase quality sweep at that milestone.

Operator framing (2026-05-18 session): "An automobile manufacturer posts a recommended maintenance interval for a vehicle." The ADR-completion event IS the milestone interval — every `Validated` ADR represents one architectural unit of work, and the milestone moment is when the cross-codebase pass should run. The review skills already exist (`gz-tech-debt-review`, `gz-pythonic-pattern-detect`, `gz-complexity-advisor`, future `gz-architecture-review` per `ADR-pool.gz-architecture-review-skill`), but they are NOT systematically called — invocation is ad-hoc and skipped under operator fatigue.

This ADR delivers `gz-adr-milestone-maintenance` — the fourth pipeline orchestrator in the artifact lifecycle — with `/goal` as a first-class convergence primitive on the Claude Code primary harness.

Pipeline cohort context:

| # | Pipeline | Orchestrator skill | Redteam terminal | Status |
|---|---|---|---|---|
| 1 | Design | `gz-adr-plan-pipeline` | ✓ Required | Pool — `ADR-pool.adr-plan-pipeline-with-redteam` |
| 2 | Implementation | `gz-obpi-pipeline` | ✓ Required (retrofit) | Exists; retrofit pool — `ADR-pool.obpi-pipeline-redteam-retrofit` |
| 3 | Validation | `gz-adr-validation-pipeline` | ✓ Required | Canonical — ADR-0.0.50 |
| 4 | **Maintenance milestone** | **`gz-adr-milestone-maintenance` (THIS ADR)** | **✗ Not needed (findings routing, not state transitions)** | **Missing — this ADR delivers it** |
| 5 | Chores (ad hoc) | `gz-chore-runner` | ✗ Not needed | Exists |

## Decision

### Stage 1 — Milestone maintenance pipeline orchestrator

Create `gz-adr-milestone-maintenance` skill conforming to the multi-skill orchestrator contract:

- **Stages**: sweep-dispatch (parallel) → findings-collect → findings-route → convergence-check
- **Driver persona**: `pipeline-orchestrator`
- **Runtime engine**: `src/gzkit/milestone_maintenance_runtime.py`
- **Trigger**: `validation_pipeline_completed` ledger event (ADR-0.0.50 emits this; this pipeline consumes it as its trigger)
- **Per-stage receipts** at `.gzkit/receipts/milestone-maintenance-<ADR-ID>-<iso>.json`
- **Unified ledger event**: `milestone_maintenance_completed` on terminal-stage success
- **`--from=<stage>`** resume points (sweep-dispatch, findings-collect, findings-route, convergence-check)
- **No redteam terminal stage** — this pipeline's output is findings routing (GHIs filed, trivial fixes applied), not state transitions. Findings themselves get reviewed by humans through their normal GHI/fix lifecycle.

### Stage 2 — `/goal` as first-class convergence primitive (Claude Code primary)

Convergence — "every review skill has been invoked once, every finding has a tracked destination (fixed-in-place / GHI / accepted-deferred), zero outstanding findings" — is bounded by Claude Code's `/goal` primitive (https://code.claude.com/docs/en/goal) when the harness is Claude Code v2.1.139+:

- **Goal condition shape**: Up to 4,000 chars. Names: every skill in the manifest, finding-count + disposition for each, "stop after 8 turns and report final state regardless."
- **Evaluator constraint**: `/goal`'s evaluator only sees what the agent surfaced in the conversation. This forces the sweep skill to **explicitly state** every finding and its disposition — exactly the anti-vibing posture (the agent cannot vibe its way through; it must surface evidence the evaluator can read).
- **Iron Law**: "Milestone maintenance pipeline is not complete until convergence-check returns PASS — every review skill invoked, every finding routed, or operator-bypassed via `--accept-maintenance-deferred`."
- **Fallback (Codex / Copilot harnesses)**: Bounded iteration loop in the runtime engine — max 8 iterations, exit on zero-outstanding-findings or iteration-cap with final-state report. Same canonical skill body branches on harness detection (ADR-0.0.31 distribution invariant satisfied).

### Stage 3 — Sweep manifest (per-ADR-kind aware)

`data/milestone_maintenance_skills.json` declares which review skills the sweep dispatches, structured by ADR kind:

```json
{
  "by_kind": {
    "foundation": ["gz-architecture-review", "gz-tech-debt-review", "gz-pythonic-pattern-detect", "gz-complexity-advisor", "gz-validate --advisory-scorecard"],
    "feature":    ["gz-tech-debt-review", "gz-complexity-advisor"]
  },
  "always": ["gz-check --all"]
}
```

Rationale: `foundation` ADRs codify invariants — they get the heavier sweep (architecture review + advisory scorecard audit). `feature` ADRs ship capabilities — lighter sweep focused on code-tier quality. The `always` block runs regardless of kind.

Per-skill manifest entries also declare **mechanical-routability** metadata: which findings the skill auto-routes via existing thresholds (trivial fix-in-place, GHI filing), vs. which require operator decision. Sweep stage uses this to know what to handle autonomously vs. what to surface.

### Stage 4 — Fail-closed gating

`gz check` blocks merge when:
- An ADR is `Validated` but lacks a `milestone_maintenance_completed` ledger event newer than the `validation_pipeline_completed` event (`gz validate --milestone-maintenance-receipts`).
- A maintenance run produced findings that were neither fixed nor routed (`gz validate --milestone-maintenance-findings-routed`).

Bypass paths (each writes an auditable ledger event):
- `gz check --accept-maintenance-deferred <ADR-ID> --reason <REASON>` — operator-attested deferral. Defers the maintenance pass for one ADR's cycle (next ADR's milestone re-runs the manifest including any deferred concerns).
- No bypass for missing receipts. If the maintenance run didn't happen, run it.

### Stage 5 — `gz-architecture-review` skill (canonical first sweep candidate)

Per `ADR-pool.gz-architecture-review-skill`, the architecture-tier review (Matt Pocock-inspired, adapted for gzkit) is the canonical first dispatched skill in the sweep manifest's `foundation` block. Promotion of that pool ADR is a follow-on after this ADR's pipeline lands; until then, the manifest names the future skill and the sweep handles its absence gracefully (skips with a warning until the skill is promoted).

### Stage 6 — Claude Code primary harness, Codex/Copilot fallback

Same posture as ADR-0.0.50 § Stage 5 (Claude Code as primary vendor harness):

- **First-class for Claude Code**: `/goal`, parallel `Agent` subagent dispatch for review skills, inline Codex calls (consumed by review skills like `gz-architecture-review` for cross-vendor deep-module judgment if its design adopts that pattern).
- **Fallback for Codex/Copilot**: bounded-iteration semantics, sequential sub-skill invocation if parallel dispatch is not supported, per-harness branching in the skill body's `## Harness Detection` section.
- **ADR-0.0.31 distribution invariant satisfied**: single canonical SKILL.md, executes one branch based on detected harness.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| The skill catalog and its mirrors are aligned — the review-skill surface this maintenance pipeline's sweep manifest dispatches. | uv run gz validate --skill-alignment | 0 |
| The Fidelity Assertions block is parseable by the fidelity gate. | uv run gz adr fidelity ADR-0.0.51-milestone-maintenance-pipeline-with-goal --check | 0 |

## Consequences

### Positive

- ADR completion becomes a structural maintenance milestone, not just a release marker. Drift between ADRs gets surfaced and routed at the natural cadence (per architectural unit of work), not deferred to a future "tidy" session that never happens.
- `/goal` as first-class convergence primitive exploits Claude Code's strongest harness mechanism for the bounded-loop-with-exit-condition pattern. Replaces ad-hoc agent-driven iteration with a goal-evaluator that sees the conversation and judges convergence independently — anti-vibing structurally.
- Review skills (`gz-tech-debt-review`, `gz-pythonic-pattern-detect`, `gz-complexity-advisor`, future `gz-architecture-review`) gain a systematic invocation cadence. The "skills exist but aren't systematically called" defect (named in the 2026-05-18 design conversation) is closed by mechanical enforcement.
- Per-ADR-kind sweep manifest respects the kind taxonomy — foundation ADRs (invariants) get heavier scrutiny than feature ADRs (capabilities). Sweep weight matches stakes.
- `gz check` fail-closed gate prevents the next ADR from landing while a previous ADR's maintenance is overdue. "Maintenance debt" becomes mechanically tracked, not socially negotiated.

### Negative

- Increased latency between ADRs. Operator can no longer push the next ADR forward until the previous ADR's maintenance milestone completes. Mitigated by `--accept-maintenance-deferred` bypass with ledger-recorded reason — deferrals are visible, not silent.
- `/goal` requires Claude Code v2.1.139+. Older Claude Code versions (and Codex / Copilot) fall back to bounded iteration — weaker convergence guarantee, but still bounded. The fallback path is canonical, not an afterthought.
- Sweep manifest is doctrine that ages. As gzkit evolves and review skills change, the manifest needs maintenance of its own. Validator (`gz validate --milestone-maintenance-manifest`) enforces structural integrity; semantic freshness is a tech-debt concern owned by `gz-tech-debt-review` (recursive, but well-bounded — the manifest is a small, stable surface).
- Coupling to ADR-0.0.50: this pipeline consumes `validation_pipeline_completed` as its trigger. If ADR-0.0.50 doesn't land, this pipeline has no trigger. Cohort sequencing: 0.0.50 lands first, then 0.0.51.

## Decomposition Scorecard

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

- [ ] OBPI-0.0.51-01: `gz-adr-milestone-maintenance` skill + `src/gzkit/milestone_maintenance_runtime.py` runtime engine; stages sweep-dispatch → findings-collect → findings-route → convergence-check; `--from=<stage>` resume; consumes `validation_pipeline_completed` as trigger
- [ ] OBPI-0.0.51-02: `data/milestone_maintenance_skills.json` manifest schema (per-ADR-kind aware with `by_kind` and `always` blocks); per-skill mechanical-routability metadata; `gz validate --milestone-maintenance-manifest` structural validator
- [ ] OBPI-0.0.51-03: `/goal`-first-class convergence on Claude Code (goal-condition templating, evaluator-readable surfacing of findings); bounded-iteration fallback (max 8) for Codex/Copilot harnesses; harness detection utility shared with ADR-0.0.50
- [ ] OBPI-0.0.51-04: `gz validate --milestone-maintenance-receipts` + `gz validate --milestone-maintenance-findings-routed` validators (fail-closed in `gz check`); `--accept-maintenance-deferred` bypass with ledger-recorded operator attestation
- [ ] OBPI-0.0.51-05: `gz status --next-action` extension naming `gz-adr-milestone-maintenance` when an ADR is `Validated` without a fresher `milestone_maintenance_completed` event; integration with ADR-0.0.50's `--next-action` patch (no duplicate code paths)

## Q&A Transcript

Design dialogue conducted 2026-05-18 via `/gz-design`, immediately following the booking of ADR-0.0.50 (validation pipeline). Key decisions:

- **Fourth pipeline in the artifact-lifecycle cohort** — not in the three-ADR redteam cohort. This pipeline's output is findings routing, not state transitions; redteam terminal is not required (per operator's framing: "after above — architecture review and maintenance milestone pipeline (no redteam needed)").
- **`/goal` as first-class** — Claude Code is the primary vendor harness; design optimally for its strongest primitives. Codex / Copilot harnesses fall back to bounded iteration in the same canonical skill body (ADR-0.0.31 invariant preserved).
- **Trigger via ledger event** — `validation_pipeline_completed` event from ADR-0.0.50 triggers this pipeline (not a separate `validated` event; the validation pipeline's terminal receipt IS the trigger). Cohort sequencing makes 0.0.50 a hard dependency.
- **Per-ADR-kind aware manifest** — foundation ADRs get heavier sweep than feature ADRs; weights match stakes.
- **`gz-architecture-review` skill** booked as pool ADR (`ADR-pool.gz-architecture-review-skill`) — Pocock-inspired highlights adapted for gzkit. Canonical first dispatched skill in the foundation-block sweep. Promotion is a follow-on after this pipeline lands.

Origin: operator's invocation of Matt Pocock's `improve-codebase-architecture` as a candidate for adoption, expanding into the broader "service interval" doctrine for ADR-completion milestones.

## Evidence

- [ ] Tests: `tests/test_milestone_maintenance_runtime.py`, `tests/test_milestone_maintenance_manifest_validator.py`, `tests/test_goal_first_class_convergence.py`, `tests/test_milestone_maintenance_fail_closed_gates.py`
- [ ] Docs: `docs/user/runbook.md` § Milestone maintenance pipeline, `docs/governance/governance_runbook.md` § Sweep manifest doctrine, `docs/user/manpages/gz-adr-milestone-maintenance.md`

## Alternatives Considered

- **Bundle milestone-maintenance into validation pipeline** (earlier session proposal) — rejected per operator framing on 2026-05-18: "after above — architecture review and maintenance milestone pipeline." The two are sequenced, not bundled. Validation pipeline is per-ADR state-transition (`Completed → Validated`); maintenance pipeline is per-ADR codebase-wide sweep triggered by validation completion. Different scopes, different operator moments, different fail-closed semantics.
- **Add redteam terminal to maintenance pipeline** — rejected per operator framing: "no redteam needed" for pipelines #4 and #5. Maintenance pipeline emits findings routed to GHIs / fixes / accepted-deferrals, not state transitions. Redteam verifies state transitions; findings get reviewed through their own GHI/fix lifecycles (each of which is its own pipeline run).
- **Trigger maintenance on calendar cadence (weekly) rather than per-ADR** — rejected. Calendar fires on cold repos with no recent work; event-cadence (per Validated ADR) ties maintenance to actual architectural delta. Operator framing of "service interval" aligns with vehicle-mileage (event-cadence), not calendar.
- **Manifest as flat list (no per-kind awareness)** — rejected. Foundation ADRs codify invariants and merit heavier scrutiny (architecture-review, advisory-scorecard audit); feature ADRs ship capabilities and need lighter scrutiny (code-tier quality). Flat manifest applies same weight to both, which is wrong on both ends — too heavy for features, too light for foundations.
- **Build `/goal` equivalent natively in gzkit runtime** — rejected. `/goal` is a harness primitive that already exists (Claude Code v2.1.139+). Reimplementing it in gzkit duplicates harness work and breaks the Claude-Code-primary posture. Bounded iteration fallback for non-Claude-Code harnesses is enough.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.51 | Pending | | | |
