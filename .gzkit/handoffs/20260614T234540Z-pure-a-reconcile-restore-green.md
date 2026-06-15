---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-14T23:45:40Z"
agent: claude-code
obpi_id:
session_id:
continues_from: .gzkit/handoffs/20260614T223440Z-ADR-0.0.65-0.0.72-handoff-campaign-session.md
---

<!-- Supersedes the off-campaign 0.0.65/0.0.72 "FULL SEND" handoff — created by claude-code at 2026-06-14T23:45:40Z under operator ruling pure A -->

## ⚠️ This handoff ADVISES next moves — it is NOT authorization to execute them

**Read this before anything else.** A handoff records a *proposed* plan and its
context. It is **NOT** a clearance to unilaterally execute that plan. On resume —
at **every** freshness level, Fresh included — you MUST:

1. Present the advised next steps and current state to the operator.
2. **Obtain explicit operator authorization before executing any of them** — no
   file mutation, no `gz` ceremony, no migration until the operator says go.
3. Treat the human-as-final-witness doctrine as binding: you advise; the
   operator rules; you note variance and stop.

The campaign governs what is pulled next; this handoff only advises.

## Current State Summary

This handoff **supersedes** `.gzkit/handoffs/20260614T223440Z-ADR-0.0.65-0.0.72-handoff-campaign-session.md`
and records the operator ruling **pure A** (Magna Carta amendment 2026-06-14)
that reconciles a prior off-campaign "build BOTH ADR-0.0.65 + ADR-0.0.72, FULL
SEND" session back to the campaign. Working tree clean, `origin/main` synced,
HEAD `145ed78d`, **no active OBPI lock**, no in-progress ADR pipeline.

`uv run gz check` is **RED solely on the Behave stage** — the other 30 gates
pass (including the now-live Lock-handoff-coupling and Handoff-documents gates
that OBPI-0.0.72-02 wired). The single red is 3 fixture failures in
`features/constitutional_invariants.feature` (GHI #621). The immediate next work
is **restore the green floor, then open B.1 (CMS)** — not the 7 OBPIs the
superseded handoff advised.

## Important Context

- **Magna Carta governs** (`docs/governance/build-to-1.0-campaign-2026-06-10.md`):
  work the topmost unchecked item whose gate is met. This handoff ADVISES; the
  campaign rules. The 2026-06-14 pure-A amendment records this reconciliation.
- **ADR-0.0.72 is a COLLAPSED tombstone — DO NOT IMPLEMENT** (2026-06-13,
  "you cannot audit your way out of over-auditing"). Its real bugs are Phase E
  GHIs #612/#575/#581. The one landed Gate-5 piece, OBPI-0.0.72-02
  (HandoffFrontmatter reconcile), is credited to **#612** and flagged for closure
  at next triage. Do NOT resume OBPI-0.0.72-03/04/01.
- **ADR-0.0.65 is deferred to C.4** (MOTD continuity build) — Phase A note: "do
  not 'fix' this omission." Do NOT build OBPI-0.0.65-02/03/04/05 standalone; C.4
  *redesigns* the handoff system, so the standalone API would be throwaway.
- **Green-first**: no phase opens while `gz check` is red. Restoring green (#621)
  precedes B.1.
- **cp1252 trap**: do NOT diagnose `gz check`/behave via redirected stdout on
  Windows — it triggers the U+2713 `UnicodeEncodeError` (#582) that MASKS the
  real failures (GHI #589). Reproduce the real failures with
  `PYTHONIOENCODING=utf-8 uv run -m behave features/constitutional_invariants.feature`.
- The hand-authored-handoff jank the operator caught IS the disease ADR-0.0.65
  cures (vaporware `create_handoff`/`scaffold_handoff`); until C.4, route handoffs
  through `gz-session-handoff` + `validate_handoff_document` (as this one was).

## Decisions Made

- **Decision:** Pure A — hold the Magna Carta line; do not resequence 0.0.65/0.0.72.
  **Rationale:** Campaign-wins tie-breaker (§ Cadence); #612 already landed; the
  handoff-validation gates are live and green; C.4 owns the rest; building
  0.0.65's standalone API now would be throwaway (C.4 redesigns it).
  **Alternatives rejected:** (B) amend Magna Carta to sanction the override and
  un-collapse 0.0.72 — rejected against the collapse rationale and C.4 absorption;
  resequencing 0.0.65 ahead of CMS — rejected on fork-risk.
- **Decision:** File the three deferred blockers as real GHIs (#621, #622, and a
  cross-link comment on #582), not prose.
  **Rationale:** Operator authorized; untracked = nonexistent (AGENTS.md); the
  superseded handoff's numberless "tracked" prose was the jank being corrected.
- **Decision:** OBPI-0.0.37-23 (invariant-tier) is recognized as legitimate B.1
  progress; B.1 advanced 13/19 → 16/19.
  **Rationale:** It is CMS tier work per the disclosure-tier amendment, not part
  of the off-script override.

## Immediate Next Steps

ADVISORY ONLY — present to the operator and await authorization before acting.

1. **Restore the green floor — GHI #621.** Read
   `features/steps/constitutional_invariants_steps.py` for the 3 failing
   scenarios (`features/constitutional_invariants.feature:57`, `:66`, `:156`),
   repair the drifted step expectations (the production
   `gz validate --invariant-coherence` scope itself passes — this is BDD-coverage
   drift), reproduce green with
   `PYTHONIOENCODING=utf-8 uv run -m behave features/constitutional_invariants.feature`,
   then `uv run gz check` green. Close #621 `fixed` with the receipt.
2. **Optionally fix the cp1252 masker (#582 sibling)** — force UTF-8 for the
   behave subprocess in the `gz test --bdd` runner so future failures stop being
   masked under redirected stdout.
3. **Confirm `gz check` green**, then **open B.1 — ADR-0.0.37 CMS build-out
   (16/19 → terminal)** per Magna Carta. `uv run gz adr report ADR-0.0.37` lists
   the remaining OBPIs.
4. **Direct-fix #622** (`lock_manager.list_locks` rsplit) when next touching
   locks — a slug-aware fix mirroring `_write_reaping_handoff` plus a
   `tests/test_lock_manager.py` case; close `fixed` citing the SHA.
5. **At next triage**: close #612 citing OBPI-0.0.72-02; regenerate the Magna
   Carta GHI register from `gh issue list`.

## Pending Work / Open Loops

- GHI **#621** (green-floor blocker, Phase B), **#622** (lock_manager rsplit,
  Phase E), **#582** (cp1252 behave masker, Phase E) — all open with blocker
  comments naming the next concrete action.
- GHI **#612** (HandoffFrontmatter) — substantially addressed by OBPI-0.0.72-02;
  close at next triage.
- ADR-0.0.72 closeout: N/A (collapsed). ADR-0.0.65: awaits C.4. ADR-0.0.37 (B.1):
  16/19 → terminal once green is restored.

## Verification Checklist

- [ ] `git status --short` empty; `git branch --show-current` → main; `ahead=0 behind=0`
- [ ] `uv run gz obpi lock list` → no active locks
- [ ] `uv run gz adr report ADR-0.0.72` → Lifecycle Pending, OBPI-02 attested_completed; ADR collapsed (do not implement remaining OBPIs)
- [ ] `uv run gz adr report ADR-0.0.37` → 16/19
- [ ] `PYTHONIOENCODING=utf-8 uv run -m behave features/constitutional_invariants.feature` → reproduces the 3 #621 failures (do NOT use redirected stdout — it masks them)
- [ ] `gh issue view 621` and `gh issue view 622` → open with blocker comments

## Evidence / Artifacts

- `.gzkit/handoffs/20260614T223440Z-ADR-0.0.65-0.0.72-handoff-campaign-session.md` — the superseded off-campaign handoff this continues from
- `docs/governance/build-to-1.0-campaign-2026-06-10.md` — Magna Carta; carries the 2026-06-14 pure-A reconciliation amendment and the B.1 16/19 refresh
- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md` — the collapsed tombstone (do not implement)
- `docs/design/adr/foundation/ADR-0.0.65-handoff-system-consolidation/ADR-0.0.65-handoff-system-consolidation.md` — deferred to C.4
- `src/gzkit/lock_manager.py` — `list_locks` rsplit bug (#622) at the `adr_filter` branch
- `features/constitutional_invariants.feature` — the 3 failing #621 scenarios

## Environment State

Python 3.13, uv-managed. Platform win32, branch `main`, HEAD `145ed78d`, synced
with `origin/main`. `uv run gz check` red solely on the Behave stage (#621); the
full unittest sweep was green at the prior session boundary (6157 pass / 1 skip).
No active OBPI lock.
