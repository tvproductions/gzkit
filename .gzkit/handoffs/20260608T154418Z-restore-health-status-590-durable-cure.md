---
mode: CREATE
adr_id: ADR-0.0.67
branch: main
timestamp: "2026-06-08T15:44:18Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260608T103030Z-restore-health-tier0-8th-reclose.md
---

<!-- Handoff document for ADR-0.0.67 — created by claude-code at 2026-06-08T15:44:18Z -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding from the first step: you
   advise; the operator rules; you note variance and stop.

Barreling into execution from this document is the exact failure this handoff
exists to prevent. The plan is the destination; operator authorization is the
ignition.

## Current State Summary

`main` is **26/26 GREEN** (`uv run gz check` → `GZ_CHECK_EXIT=0`, advisory
spec-test drift 1802 findings, non-blocking), tree clean except this handoff +
the plan edit it records, synced 0/0 to `origin/main`. HEAD is `04462322`.

This session opened on a `restore-health status?` query. Unlike the prior seven
resumes, **Tier 0 did NOT reopen** — no 9th reopening. The session's substantive
finding: the **durable cure for the Tier-0 *generator* had already landed** in
two commits that the 8th-reclose handoff (predecessor) did not yet know about,
because they were authored *after* it. **GHI #590 (CLOSED)** wired the
`task-envelope-coherence` validator (Signatures a/b/c) into the `gz obpi complete`
chokepoint, fail-closed (exit 3), right after the REQ-coverage gate — so a
`seq=01`-only-without-`req_atomic:` completion can no longer pass completion and
redden `gz check` on the next session. That seq-residue was the generator of the
8× Tier-0 reopenings (C→E→G→J→K→L→M→N).

This session's *own* work was: (1) verify the live health state with observed
commands; (2) verify and characterize the #590 commits from primary source
(`git show`, `gh issue view 590`); (3) record the #590 development into the
canonical recovery plan with an advisor-corrected, **scoped** claim; (4) write
this handoff. No code was changed this session.

## Important Context

- **The #590 claim is SCOPED — do not overstate it.** #590 mechanizes the
  completion-chokepoint cure for the **Task-envelope-coherence family only** —
  the single most frequent offender (fired at C/E/G/L/M/N). The plan names **four**
  recurring completion-residue families; the other three — **Preflight** (orphan
  plan-audit receipts: C/G/J), **Format** (un-`ruff format`'d completion files:
  E/L), and **Behave** (stale fixtures: K/M) — remain **ungated at the
  chokepoint**. Recurrence is *reduced*, not eliminated. A 9th reopening from a
  Preflight/Format/Behave residue is still possible. The advisor flagged the
  unqualified "stopped the generator" phrasing as a V.I.B.E.S. overclaim; the
  plan now carries the scoped version.
- **#590 is a *third* cure mechanism, better than the two prior snapshots named.**
  Prior snapshots framed the durable cure as "auto-emit `req_atomic` on atomic-REQ
  completions" or "witnessed gate retirement." #590 is neither: it is the
  *chokepoint-superset* approach (completion gate = superset of every OBPI-scoped
  `gz check` gate). It is better than auto-emit because it forces the honest
  atomic-or-subdivide decision at completion rather than reflexively greening the
  gate. This pattern is the **template** for closing the other three offender
  families.
- **#590 landed between the predecessor handoff and this session, not in it.**
  Commits `46f72a02` (13:37Z) and `04462322` (15:13Z) postdate the 10:30Z
  8th-reclose handoff. They were authored in an un-handoffed session earlier today.
  This session *verified* them; it did not author them. Keep that attribution
  straight — do not credit this session with the #590 work.
- **No active OBPI lock** (`uv run gz obpi lock` shows none; the session
  orientation confirmed no active locks). This handoff is a restore-health
  status/recording handoff, not a lock-release register entry, so
  `gz validate --lock-handoff-coupling` does not fire on it.
- **Commits land directly on `main`** (no feature branch); the gate is
  `gz check` / `gz git-sync --lint --test` run before push, not per-commit hooks
  (deliberately off, operator-confirmed).
- **The throughline tension is STILL UNRESOLVED and is the operator's call.** The
  handoff chain's advised remaining work
  (`OBPI-0.0.67-01-recursive-verb-path-enumeration`) is more foundation work
  *outside* the #519 throughline — continuing it deepens the V.I.B.E.S. wandering.
  The competing pull is the open #519 emergency. Surface this; do not resolve it
  unilaterally.

## Decisions Made

- **Decision:** Record the #590 development by folding a `2026-06-08 (PM)`
  development entry into the existing Snapshot-N live baseline, rather than
  minting a new Snapshot O.
  **Rationale:** No `gz check` RED→GREEN transition happened this session (main
  has been green since Snapshot N), so the snapshot-per-transition convention does
  not warrant a new snapshot. The plan's "one orientable baseline, not a growing
  snapshot log" doctrine favors folding. Snapshot N's RED→GREEN prose (with its
  specific commits) was left intact as the historical record.
  **Alternatives rejected:** (a) mint Snapshot O — grows the snapshot log with no
  gz-check transition to anchor it; (b) rewrite Snapshot N's bullets — would
  destroy the historical RED→GREEN record and its commit references.
- **Decision:** Write the #590 claim as scoped to the Task-envelope-coherence
  family, explicitly naming Preflight/Format/Behave as still-ungated.
  **Rationale:** The advisor (full-transcript review) flagged the unqualified
  "stopped the generator of the 8× reopenings" as an overclaim that contradicts
  the plan's own four-family offender table and would blindside the next session
  when a Format/Preflight residue reopens Tier 0.
  **Alternatives rejected:** the unqualified headline — a V.I.B.E.S. overclaim the
  recovery regime exists to catch.

## Immediate Next Steps

<!-- ADVISORY ONLY — present and await operator authorization before acting. -->

1. **Commit + sync the plan edit and this handoff** (operator authorization
   required — push is outward-facing). Stage
   `docs/governance/return-to-health-plan-2026-05-30.md` and this handoff file,
   commit (`docs(restore-health): record GHI #590 durable cure + session handoff`
   with a `Task:` trailer), then `uv run gz git-sync --apply --lint --test`. The
   #590 fix commits (`46f72a02`, `04462322`) are already on `origin/main`; only
   the plan/handoff edits remain uncommitted.
2. **Decide the throughline question** (operator call): resume the chain's advised
   `OBPI-0.0.67-01-recursive-verb-path-enumeration`, OR pivot to the open #519
   emergency (the sole `emergency`, Tier 1 topmost). These compete; the operator
   must rule.
3. **(If recurrence-cure appetite) extend the #590 chokepoint pattern to the other
   three offender families.** #590 is the template: make `gz obpi complete` a
   superset of the OBPI-scoped Preflight / Format / Behave gates too, so their
   completion-residue also cannot reach `main`. This is the structural close of the
   recurrence loop that #590 began — scope it as its own GHI/OBPI per defect-fix
   routing; it crosses more than the task-envelope surface.

## Pending Work / Open Loops

- **#519 (emergency, OPEN):** durable 258K-window cure needs the <15k
  registry-projected surface (GHI #533) + ADR-0.0.37 build-out + Gate 5. Interim
  byte relief already landed (root AGENTS.md under Codex's 32,768 B cap).
  Definition-of-Healthy is not all-true while #519 is open.
- **Tier-0 recurrence — partially cured.** Task-envelope-coherence family now
  fail-closed at the completion chokepoint (#590). Preflight / Format / Behave
  completion-residue remain ungated — the live subtraction/mechanization
  candidates (see plan § Recurring Tier-0 offenders → Chokepoint-gating status).
- **ADR-0.0.67:** OBPI-02/-03 attested-complete; OBPI-01 (recursion keystone) is
  the chain's advised remaining work, pending the throughline decision.
- **38 open GHIs** homed in the plan's GHI Register (Phase 2: 1 · Phase 3: 17 ·
  Phase 4: 7 · T2: 7 · Parked: 1, per last triage); #590 closed today.

## Verification Checklist

- [ ] `uv run gz check` → 26/26 GREEN (`GZ_CHECK_EXIT=0`)
- [ ] `uv run gz validate --task-envelope-coherence` → All validations passed
- [ ] Branch matches: `git branch --show-current` → `main`
- [ ] `git status --short` clean after the Step-1 commit+sync
- [ ] `gh issue view 590 --json state` → CLOSED
- [ ] `gh issue list --state open --label emergency` → only #519
- [ ] Plan § Live baseline + § Recurring Tier-0 offenders carry the scoped #590 note

## Evidence / Artifacts

- `docs/governance/return-to-health-plan-2026-05-30.md` — #590 development recorded (live-baseline block, Snapshot-N PM entry, Recurring-offenders chokepoint-gating note, GHI Register #563/#590 rows)
- `.gzkit/handoffs/20260608T103030Z-restore-health-tier0-8th-reclose.md` — predecessor handoff (chain parent)
- `src/gzkit/commands/validate_task_envelope.py` — `pending_obpi_task_envelope_errors` composes the scoped Sig a/b/c gate (#590)
- `src/gzkit/commands/obpi_complete.py` — `_enforce_task_envelope_gate` fail-closed at the completion chokepoint (#590)
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — v6.19.1: Stage 2 subdivide-or-declare-atomic discipline; Step-0 enumeration broadened to Sig a/b/c (#590)

## Environment State

- Python 3.13+ via `uv`; platform darwin. HEAD `04462322`; #590 fix commits already
  on `origin/main`. Plan + handoff edits pending commit (Immediate Next Step 1).
- Last lock-event: none active (no OBPI lock held this session). Branch state:
  `main`, 0 ahead / 0 behind `origin/main` at handoff-write time (the two pending
  edits are uncommitted working-tree changes, not unpushed commits).
