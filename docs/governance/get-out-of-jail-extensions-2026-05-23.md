# Post-Recovery Extensions — Sidecar to Get-Out-of-Jail Plan (2026-05-23)

> **Read this only after [`get-out-of-jail-plan-2026-05-23.md`](get-out-of-jail-plan-2026-05-23.md) closes.** This file captures three GSD-derived capability deltas surfaced during the 2026-05-23 recovery diagnosis that are deliberately **out of 14-day scope**. They presuppose the structural moves (router, context-loader, AGENTS.md shrink, typed skill contracts, closeout-on-spine) have already shipped. Acting on them before then is a tripwire — they will be cheaper, smaller, and structurally honest once Moves 1–5 close.

## Provenance

Surfaced during 2026-05-23 reconnaissance of [`open-gsd/get-shit-done-redux`](https://github.com/open-gsd/get-shit-done-redux) against current gzkit state, in the same session as the get-out-of-jail plan. The recovery plan addresses the *structural* deficit (load-bearing surface, mechanical spine, broken ceremony). These three are *capability* deltas that emerge as actionable only after that structure ships.

Captured to a sidecar (not pool ADRs, not a new doctrine page, not GHIs) to avoid:

- Pool sprawl during the 14-day window
- Doctrine-page proliferation (anti-temptation tripwire #5 in the plan)
- Premature foundation churn

This sidecar matches the existing precedent of Footnote 1 in the plan (Deferred taxonomy review). It is a trace, not doctrine.

## Extension 1 — Per-agent model profiles

**Concept (GSD):** `.planning/config.json` carries a `profile` selector (`quality` / `balanced` / `budget`) that controls which model each agent class invokes. Researcher tier, executor tier, planner tier — bound by *tier*, not by per-skill frontmatter.

**Current gzkit shape:** Every persona/skill picks its model inline (or defers to harness default). No tier abstraction; no project-level cost-vs-quality knob.

**Right venue:** Pool ADR after Move 4 (typed skill contracts). Reason: without typed `inputs:` / `outputs:` on skills, a "balanced vs. quality" toggle has no per-stage hook to bind to. The contract is the seat the profile picker sits in.

**Suggested naming:** `ADR-pool.model-profiles-per-agent-tier`.

## Extension 2 — Multi-runtime schema transformer

**Concept (GSD):** `bin/install.js` ships `convertClaudeToOpencodeFrontmatter` and analogous transformers. The installer reads canonical Claude-Code source (`agents/`, `commands/`) and *mutates* frontmatter shape per target runtime (e.g., OpenCode strips `tools:`, requires semantic colors; Gemini has its own constraints). Single canonical source, N transformed surfaces.

**Current gzkit shape:** `gz agent sync control-surfaces` mirrors canonical `.gzkit/skills/` to `.claude/skills/`, `.agents/skills/`, `.github/skills/` — file copy, no schema transformation. Works today only because Claude / Codex / Copilot accept the same shape. Bites the moment a fourth runtime needs different frontmatter.

**Right venue:** Pool ADR after Move 3 (AGENTS.md shrink completes the per-surface load story; without that, there is no structurally varied surface worth transforming). Nearest existing neighbor is [`ADR-pool.ai-runtime-foundations`](../design/adr/pool/ADR-pool.ai-runtime-foundations.md), but Architectural Boundary 1 in [`AGENTS.md`](../../AGENTS.md) parks that one post-1.0 and the scope is broader.

**Suggested naming:** `ADR-pool.control-surface-schema-transformer`.

## Extension 3 — Verification-as-agent-loop

**Concept (GSD):** `/gsd-verify-work` dispatches a dedicated debug agent against failed acceptance tests; the agent diagnoses, generates a fix plan, returns it to the orchestrator for re-execution. Verification is a phase with iterative fix planning, not a one-shot pass/fail gate.

**Current gzkit shape:** `gz attest` and Gate 5 are CLI verification surfaces; `quality-reviewer` / `spec-reviewer` personas exist as subagents but don't loop into a diagnose → fix-plan → re-execute orchestration. Closest primitive is `gz-tech-debt-review` (diagnostic only, routes to chore / GHI / in-flight).

**Right venue:** Pool ADR after Move 5 (closeout-on-spine ships `CeremonyStore` + structured `ReqEvidence`). Reason: the loop requires structured failure data to consume; building it before the spine would be building it on the broken pillar Move 5 exists to fix.

**Suggested naming:** `ADR-pool.verification-agent-loop-on-ceremony-store`.

## Triage trigger

Read this file when the plan's "Recovery closeout" section is appended (target: Day 14+). At that point, for each of the three extensions:

1. If still relevant — file as a pool ADR via `uv run gz adr promote --kind … --pool …` per current promotion conventions.
2. If made moot by the post-recovery shape — record the moot finding in the plan's closeout block and **delete this file**.

This sidecar self-disposes on triage. It is not durable doctrine. If it is still present 30 days after recovery closes, that is itself a defect — file a GHI to retire it.
