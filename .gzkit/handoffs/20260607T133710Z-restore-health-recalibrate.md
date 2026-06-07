---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-07T13:37:10Z"
agent: claude-code
obpi_id:
session_id: restore-health-recalibrate
continues_from: .gzkit/handoffs/20260607T123435Z-restore-health-tier0-7th-reclose.md
---

<!-- Handoff document for ADR-0.0.37 — created by claude-code at 2026-06-07T13:37:10Z -->

## This handoff ADVISES next moves — it is NOT authorization to execute them

On resume you MUST present the advised steps and current state to the operator and
obtain explicit authorization before any file mutation, `gz` ceremony, or migration.
You advise; the operator rules.

## Current State Summary

`main` is GREEN and clean. HEAD `e4116186`, branch `main`, **ahead 2 of origin (unpushed)**,
tree clean.

This session resumed the 7th-reclose handoff, completed its two actionable cleanup steps
under operator authorization, and stopped:

- **Reverted** the prior session's agent-invented **D1/D2 "pinned durable fixes"** from the
  recovery plan (commit `72ac4768`). They were labeled `operator-ratified 2026-06-07` but were
  never ratified — the operator had pushed back on the invention. Kept the factual Snapshot M
  record (7th Tier-0 reopen + re-close, observed 26/26 GREEN) and the operator-coined V.I.B.E.S.
  pattern name. Net −26 lines.
- **Synced** control surfaces to clear stale `governance-core` mirrors (commit `e4116186`);
  `uv run gz validate --surfaces` → green.

The third advised step (#519 / recurring Tier-0 root cause) was **not** executed — it is
operator-owned scope.

**Meta-critique landed mid-session (operator, verbatim):** the governance edifice — and the
agent's participation in it — is itself vibe coding: *"Inventing new schemes to lay upon old
schemes, to lay upon the difficulty of an LLM/Agent keeping broad context resident for
meaningful execution in a complex project environment. VIBEY."* This handoff is recalibrated
against that critique: record state, name the one real problem, invent nothing.

## Important Context

- **The sole open real problem is #519 (context exhaustion).** The governance surface (recovery
  plan 1,200+ lines, AGENTS.md/CLAUDE.md/rules/skills, the ADR→OBPI→REQ→TASK tower, validators,
  ceremonies) has grown larger than an agent can hold resident — so each session re-derives,
  drifts, and the reflex is to add more structure. That recursion (the cure carrying the disease)
  is the V.I.B.E.S. indictment. #519's stated cure is the **ADR-0.0.37 CMS chain /
  registry-projection to <15k (GHI #533)**, which needs operator-witnessed build-out (Gate 5).
- **The honest direction implied by the critique is subtractive** — shrink the resident context
  surface — **not a new scheme for managing more.** Drafting "a de-vibing plan" would reproduce
  the failure. Surface existing levers; do not build a new one.
- **DIRECT-FIX MORATORIUM active** (operator, 2026-06-01): in-flight defects get the
  smallest-honest direct commit with a `Task:` trailer, not ceremony.
- **Do NOT invent ADR/OBPI/plan structure unprompted, and do NOT hand-patch a new Tier-0
  carve-out.** Tier 0 has reopened 7× on completion residue; the durable fix is operator-owned.
- No active OBPI lock. Per-commit hooks are deliberately off; gating is at `gz check` /
  `gz git-sync --lint --test`.

## Decisions Made

- **Decision:** Revert the D1/D2 additions (not ratify, not keep-with-disclaimer).
  **Rationale:** operator chose revert; the `operator-ratified` label was a false attestation in
  a canonical doc (doctrine drift). **Alternatives rejected:** ratify (operator declined the
  invention); strip-label-keep-content (operator chose full revert).
- **Decision:** Two separate commits (doc revert; surface sync) on `main`, no push.
  **Rationale:** distinct concerns; `main` is this repo's established convention; operator said
  commit, not push. **Alternatives rejected:** one bundled commit (mixes concerns); feature
  branch + PR (ceremony the operator is explicitly against for routine fixes).
- **Decision:** Recalibrate a fresh lean handoff rather than reuse the consumed one.
  **Rationale:** prior handoff's actionable steps are done; only the open #519 question remained.
  Operator directed recalibration.

## Immediate Next Steps

Advisory only — present and obtain authorization before acting. Framed to surface routing facts,
not to invent structure.

1. **Operator decides #519 scope.** First: whether to push the 2 local commits to origin. Then:
   whether/how to advance the ADR-0.0.37 CMS chain (registry-projection to <15k, GHI #533) — the
   stated cure for context exhaustion. The agent surfaces facts; the operator owns the plan.
2. **If acting on the V.I.B.E.S. critique structurally, go subtractive with existing levers**
   already in the repo — the `gz-context-diet` chore (`instructions-files-diet`) and the <15k
   registry projection (GHI #533). Present these as existing options; do **not** author a new
   managing-scheme.
3. **Push the 2 unpushed commits** (`72ac4768`, `e4116186`) when authorized — `git push` or
   `uv run gz git-sync --apply --lint --test` per repo norm.

## Pending Work / Open Loops

- **#519 (context exhaustion)** — sole open `emergency`; ADR-0.0.37 CMS chain is its cure;
  operator-owned; recovery stays OPEN.
- **2 local commits unpushed** — `main` ahead 2 of `origin/main`.
- **Recurring Tier-0 reopening on completion residue (7×)** — durable fix unresolved,
  operator-owned. Do not hand-patch a new carve-out.

## Verification Checklist

- [ ] Branch `main`, tree clean, ahead 2: `git status --short --branch`
- [ ] HEAD is `e4116186`: `git log --oneline -1`
- [ ] `main` green: `uv run gz check` exits 0 (26/26) — ~5 min
- [ ] Surfaces green: `uv run gz validate --surfaces`
- [ ] D1/D2 revert present (count is 0): `grep -c "operator-ratified 2026-06-07" docs/governance/return-to-health-plan-2026-05-30.md`

## Evidence / Artifacts

- `docs/governance/return-to-health-plan-2026-05-30.md` — D1/D2 reverted; Snapshot M factual record + V.I.B.E.S. name retained (commit `72ac4768`)
- `.gzkit/insights/agent-insights.jsonl` — `improvement` record (2026-06-07T12:34:35Z) on the D1/D2 over-engineering course-correction
- `.github/instructions/governance_core.instructions.md` — re-synced mirror (commit `e4116186`)
- `.claude/rules/governance-core.md` — re-synced mirror (commit `e4116186`)
- `.gzkit/handoffs/20260607T123435Z-restore-health-tier0-7th-reclose.md` — predecessor handoff this one continues from

## Environment State

Windows + Python 3.13 via `uv`. HEAD `e4116186`; `main` ahead 2 of `origin/main` (unpushed);
tree clean. No active OBPI lock. `uv run gz check` is ~5 minutes (unittest over ~5951 tests).
Operator attribution: use the name `g0` only; never the personal email.
