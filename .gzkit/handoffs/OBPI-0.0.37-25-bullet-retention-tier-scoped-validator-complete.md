---
mode: CREATE
adr_id: ADR-0.0.37
branch: main
timestamp: "2026-06-15T09:52:00+00:00"
agent: claude-code
obpi_id: OBPI-0.0.37-25-bullet-retention-tier-scoped-validator
session_id: main-2026-06-15
last_lock_event_timestamp: "2026-06-15T09:32:44+00:00"
last_commit_sha: a88c0d1bb737524996a0e98a6692c18b8a707e98
---

# OBPI-0.0.37-25 Handoff — Bullet-Retention Tier-Scoped Validator

## Current State Summary

OBPI-0.0.37-25 is **completed and operator-attested** ("attest completed", g0, 2026-06-15; foundation/heavy). `gz validate --bullet-retention` was flipped from a whole-surface verbatim grep to tier-aware enforcement, realizing the ADR-0.0.33 § Amendment (2026-06-03) in the same commit-window as the coupled amendment. Branch `main`, governance edits committed (commit a88c0d1bb737524996a0e98a6692c18b8a707e98); awaiting git-sync push.

## Important Context

Invariant-tier content keeps the Era-1 verbatim contract; compressible-tier retention is witnessed by the latest `rendition_advisor_verdict` event for the surface + its `arb-step-judge-*` receipt (`exit_status==0`, prefix-guarded). Unknown-tier bullets fall back to invariant (conservative). Booked decisions (surface-level witness; unknown→invariant fallback) honored. Live canon stays green because the one live compressible corpus entry backs no enforced scorecard bullet — all enforced bullets route through the invariant verbatim path, so no regression.

## Decisions Made

- Implemented tier resolution from `.gzkit/corpus/*.jsonl` with first-match-wins substring containment; unknown tier → invariant (conservative, preserves Era-1 contract).
- Compressible witness = latest `rendition_advisor_verdict` event for the surface + receipt `exit_status==0`, with an `arb-step-judge-` prefix guard (added after both independent reviewers flagged the documented-but-unenforced prefix).
- Corrected the ADR-0.0.33 § Amendment realizer mis-citation (OBPI-18→OBPI-25) and recorded the tier-scoped amendment row in ADR-0.0.33's Attestation Block — this OBPI's Gate 5 IS that amendment's attestation point.
- Two brief staleness adjustments via the gate-friction loop: discovery-checklist placeholder paths (Stage 1); `trust_audits/__init__.py` declared as a READ-coupled re-export surface in the allowlist (Stage 5).

## Immediate Next Steps

- Complete git-sync push (push blocked twice on the pre-push `gz check` handoff-frontmatter gate; this handoff was reshaped to the canonical `HandoffFrontmatter` schema to clear it).
- Run `gz obpi reconcile` and `gz adr status ADR-0.0.37`, then git-sync #2.

## Pending Work / Open Loops

- Parent ADR-0.0.37 (Magna Carta campaign B.1, constitutional-invariant-composition build-out): remaining OBPIs beyond #25. No blockers.

## Verification Checklist

- Full unittest 6178/6178 (`arb-step-unittest-3c19e2972bda40e39427c559497700e2`)
- Lint (`arb-ruff-92d5ec92e457494fb938df41d51c76ba`), typecheck (`arb-step-typecheck-a84e2c556dcf4acfa0e63087102c4ca5`), mkdocs --strict (`arb-step-mkdocs-46be5634cb064aa8880c773d166884b3`) all exit 0
- `gz validate --bullet-retention / --surface-fidelity / --documents / --cli-alignment` clean
- `gz covers` behavior_uncovered_reqs=0; spec-reviewer PASS + quality-reviewer COHERENT

## Evidence / Artifacts

- Validator: `src/gzkit/governance/trust_audits/bullet_retention.py`
- Tests: `tests/governance/test_bullet_retention.py` (28 tests: 10 new tier-scoped + 18 preserved)
- Coupled amendment: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md`
- Docs: `docs/user/manpages/validate.md`; waiver `data/behave_coverage_waivers.json`
- Completion receipt + ADR-level audit ledger entry for OBPI-0.0.37-25 (attested_completed)
