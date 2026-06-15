---
session_id: main-2026-06-15
handoff_time: 2026-06-15T09:52:00Z
timestamp: "2026-06-15T09:52:00+00:00"
obpi_id: OBPI-0.0.37-25-bullet-retention-tier-scoped-validator
agent: claude-code
status: completed
branch_state: "main, governance edits staged for git-sync"
last_commit_sha: 41466f82e4e9
lock_claim_event_ts: "2026-06-15T09:32:44+00:00"
---

# OBPI-0.0.37-25 Handoff — Bullet-Retention Tier-Scoped Validator

## Decision Context

`gz validate --bullet-retention` was flipped from a whole-surface verbatim grep to tier-aware enforcement, realizing the ADR-0.0.33 § Amendment (2026-06-03) in the same commit-window as the coupled amendment. Invariant-tier content keeps the Era-1 verbatim contract; compressible-tier retention is witnessed by the latest `rendition_advisor_verdict` event for the surface + its `arb-step-judge-*` receipt (`exit_status==0`, prefix-guarded). Unknown-tier bullets fall back to invariant (conservative). The booked decisions (surface-level witness; unknown→invariant fallback) were honored.

This was the ADR-0.0.33 Invariant-1 amendment's Gate-5 attestation point (foundation/heavy); the realizer mis-citation (OBPI-18→OBPI-25) was corrected and the amendment recorded attested in ADR-0.0.33's Attestation Block.

## Branch State

- **Current**: main; `gz obpi complete` governance edits present, awaiting git-sync #1
- **Commit (pre-sync)**: 41466f82e4e9

## Status

Completed and operator-attested ("attest completed", g0, 2026-06-15).

- Validator tier-aware; 28 bullet-retention tests pass (10 new + 18 preserved)
- Full suite 6178/6178; lint/typecheck/mkdocs all exit 0
- Live canon stays green (the one compressible corpus entry backs no enforced bullet)
- `gz covers` behavior_uncovered_reqs=0; spec-reviewer PASS + quality-reviewer COHERENT
- Coupled ADR-0.0.33 amendment landed (realizer cite + Attestation Block row)

## In-flight fixes applied

- Insights-schema defect: an appended `improvement` record had `evidence` as a string; `InsightRecord` requires `list[str]` — fixed both this session's improvement records.
- Brief staleness adjustments (gate-friction loop): discovery-checklist placeholder paths corrected (Stage 1); `trust_audits/__init__.py` declared as a READ-coupled re-export surface in the allowlist (Stage 5).

## Pending Work / Open Loops

- Parent ADR-0.0.37 (Magna Carta campaign B.1): remaining OBPIs in the constitutional-invariant-composition build-out. Per the most-recent campaign state, B.1 was 16/19 verified; this OBPI advances item #25.
- No blockers. Next: confirm git-sync #1/#2 clean and the parent ADR-0.0.37 view reflects OBPI-25 completion.
