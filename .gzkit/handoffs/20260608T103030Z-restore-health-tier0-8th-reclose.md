---
mode: CREATE
adr_id: ADR-0.0.67
branch: main
timestamp: "2026-06-08T10:30:30Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260608T003555Z-adr0067-obpi03-complete.md
---

<!-- Handoff document for ADR-0.0.67 — created by claude-code at 2026-06-08T10:30:30Z -->

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

`main` is **26/26 GREEN** (`uv run gz check` → `GZ_CHECK_EXIT=0`), tree clean,
synced 0/0 to `origin/main`. This session opened on a `restore-health status?`
query and found **Tier 0 reopened (8th time)**: `gz check` was RED on
**Task-envelope-coherence** (2 errors). Root cause — a prior session's
**ADR-0.0.67** completions (OBPI-02 orphan-verb-wiring, OBPI-03 lock-alias
deletion) closed `seq=01`-only across all REQs with no `req_atomic:` exemption
(signature b). Completion residue, not a real defect — and foundation work
outside the open-#519 throughline (the wandering the operator named V.I.B.E.S.).

Re-closed via brief-side `req_atomic:` frontmatter with per-REQ rationale on both
briefs (commit `40cc3e57`, pushed via `gz git-sync --apply --lint --test`). The
return-to-health plan was then updated to record **Snapshot N** as the live
baseline (M demoted to a one-line history row). **The plan + handoff edits in
this session are uncommitted at the moment this handoff is written** — see
Immediate Next Steps.

Recovery stays **OPEN**: **#519** ("context surface exhausts 258K window") is
still the sole open `emergency`; Definition-of-Healthy is not all-true.

## Important Context

- **`req_atomic:` is the validator's OWN named mechanism, not a carve-out.** The
  task-envelope validator's error text literally instructs: "declare `req_atomic:`
  in brief frontmatter with inline rationale." This reclose used the brief-side
  declaration (precedent: OBPI-0.0.37-13 at Snapshots D/E/L). It is categorically
  distinct from a *validator-code* carve-out (e.g. Snapshot M's 4th manpage
  band-aid) and does **not** extend the carve-out treadmill the plan warns about.
- **Each REQ was verified atomic against its Implementation Summary** before
  writing the exemption — one indivisible contract per REQ, no shared
  coarse-default bucket masking finer labor. The rationale is honest per-REQ, not
  boilerplate. Do not treat `req_atomic:` as a reflexive green-the-gate move on
  future OBPIs without that same verification.
- **The recurrence IS the disease.** This is the 8th Tier-0 reopening
  (C→E→G→J→K→L→M→N); Task-envelope-coherence on completion residue fired at
  C/E/G/L/M/N. The durable cure is operator-gated (see Pending Work).
- **Commits land directly on `main` here** (no feature branch); the gate is
  `gz check` / `gz git-sync --lint --test` run before push, not per-commit hooks
  (deliberately off, operator-confirmed).
- **The handoff chain's advised next step** (`OBPI-0.0.67-01-recursive-verb-path-enumeration`)
  is MORE foundation work outside the #519 throughline. Continuing it before
  the operator reconciles green-first vs. throughline-focus would deepen the
  exact pattern just recorded. Surface this tension; do not resolve it unilaterally.

## Decisions Made

- **Decision:** Clear Tier 0 via brief-side `req_atomic:` exemptions on
  OBPI-0.0.67-02 and -03.
  **Rationale:** Operator chose "Clear Tier 0 first" (green-first, Operating Rule
  2). The REQs are genuinely atomic; `req_atomic:` is the sanctioned mechanism.
  **Alternatives rejected:** (a) subdivide TASKs retroactively on attested,
  completed briefs — dishonest (labor wasn't actually subdivided); (b) a
  validator-code carve-out — the band-aid the plan flags as the disease;
  (c) continue ADR-0.0.67-01 and leave Tier 0 red — violates green-first.
- **Decision:** Record Snapshot N as the live baseline; demote M to a one-line
  history row.
  **Rationale:** Operator said "update plan, I want to focus." Keeps the plan's
  "one orientable baseline, not a growing snapshot log" doctrine; file stays
  roughly flat.
  **Alternatives rejected:** appending N as full prose while leaving M's full
  prose in place — grows the snapshot log the plan deliberately compacts.

## Immediate Next Steps

<!-- ADVISORY ONLY — present and await operator authorization before acting. -->

1. **Commit the plan + handoff edits and sync.** Stage
   `docs/governance/return-to-health-plan-2026-05-30.md` and this handoff file,
   commit (`docs(restore-health): record Snapshot N (8th Tier-0 reclose)` with a
   `Task:` trailer), then `uv run gz git-sync --apply --lint --test`. (The
   `40cc3e57` req_atomic fix is already pushed; only the plan/handoff remain.)
2. **Decide the throughline question** (operator call): resume the handoff
   chain's advised `OBPI-0.0.67-01-recursive-verb-path-enumeration`, OR pivot
   back to the open #519 emergency (the only `emergency`, Tier 1 topmost). These
   compete; the operator must rule.
3. **(If durable-cure appetite) scope the recurrence fix:** auto-emit
   `req_atomic` for atomic-REQ OBPIs at closeout, or witnessed retirement of the
   Task-envelope gate. This is the 8th-reopening structural fix; it needs an
   operator Boundary-1 decision, not another manual reclose next session.

## Pending Work / Open Loops

- **#519 (emergency, OPEN):** durable 258K-window cure needs the <15k
  registry-projected surface (GHI #533) + ADR-0.0.37 build-out + Gate 5. Interim
  byte relief already landed (root AGENTS.md under Codex's 32,768 B cap).
- **Tier-0 recurrence (8×):** durable cure for completion-residue reopenings is
  unbuilt and operator-gated (subtraction-candidate gates: Preflight,
  Task-envelope-coherence, Format, Behave — all fire on completion residue).
- **38 open GHIs**, homed in the plan's GHI Register (Phase 2: 1 · Phase 3: 17 ·
  Phase 4: 7 · T2: 7 · Parked: 1, per last triage).
- **ADR-0.0.67** itself: OBPI-02/-03 attested-complete; OBPI-01 (recursion
  keystone) is the chain's advised remaining work.

## Verification Checklist

- [ ] `uv run gz check` → 26/26 GREEN (`GZ_CHECK_EXIT=0`)
- [ ] `uv run gz validate --task-envelope-coherence` → All validations passed
- [ ] Branch matches: `git branch --show-current` → `main`
- [ ] `git status --short` clean after the Step-1 commit+sync
- [ ] `gh issue list --state open --label emergency` → only #519
- [ ] Snapshot N is the live baseline in `docs/governance/return-to-health-plan-2026-05-30.md`

## Evidence / Artifacts

- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-02-wire-orphan-verbs-into-skills.md` — `req_atomic:` exemption added (REQ-01…06)
- `docs/design/adr/foundation/ADR-0.0.67-tool-skill-invariant1-enforcement/obpis/OBPI-0.0.67-03-delete-deprecated-lock-aliases.md` — `req_atomic:` exemption added (REQ-01…03)
- `docs/governance/return-to-health-plan-2026-05-30.md` — Snapshot N recorded as live baseline; M demoted to history row
- `.gzkit/handoffs/20260608T003555Z-adr0067-obpi03-complete.md` — predecessor handoff (chain parent)

## Environment State

- Python 3.13+ via `uv`; platform darwin. Fix `40cc3e57` already on `origin/main`;
  plan + handoff edits pending commit (Immediate Next Step 1).
