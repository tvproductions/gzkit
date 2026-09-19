---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-19T23:35:20Z'
agent: codex
session_id: 01a0bbd3-bfe1-7501-a817-5704f31bc130
continues_from: .gzkit/handoffs/20260919T232754Z-three-pillars-corrections-delivered.md
---

## Current State Summary

VERIFIED delivery: three-pillars repairs and draft-only reconciliation landed and synced in cc5ed5bfa and 59c4af622; all ten repair issues closed with evidence. The operator has now placed #1028 on HOLD. This successor supersedes the predecessor advice to inspect for a qualifying run as an immediate next step. The campaign banner, dated amendment and named continuity entry carry the hold.

## Important Context

Campaign source: docs/governance/build-to-1.0-campaign-2026-08-16.md. Handoff front: this successor carries the new ruling. GHI front: #1028 is verified OPEN but explicitly HELD; no fresh queue-wide triage is claimed. ADR/OBPI front: TOPMOST ADR-0.35.0 and operator initiation remain unchanged; no OBPI is initiated. R&D front: no new work selected or re-audited. Broad proof currency remains retained; bounded impact remains pooled; ADR-0.36.0 remains unimplemented by this work.

## Decisions Made

- [operator-ruled] g0: "ok, we need to hold off on 1028. update handoff, update campaign."
- [agent-chose] Preserve #1028 as open with its existing exit criteria, but remove it from immediate executable work until the operator explicitly resumes it. A future qualifying run alone does not lift the hold.

## Immediate Next Steps

1. Carry the #1028 hold forward and await the operator's next work selection.
2. If the operator explicitly resumes #1028, recheck its evidence and qualifying-run condition before conducting the comparison.
3. Preserve campaign order and the standing no-pool-build and no-ADR-0.36.0-execution boundaries.

## Pending Work / Open Loops

GHI #1028: OPEN, HELD by the operator; not completed, cancelled, or selected for current execution. Resume only on explicit operator direction. The separately recorded scripts/check_proof_freshness.py stdout-capture finding remains in insights; this documentation update does not select its repair. No other repair from the enumerated three-pillars list remains open.

## Verification Checklist

The prior delivery passed 62 staged checks, 10,525 unit tests (four skipped), 432 BDD scenarios and 88.30% coverage, with receipts in the delivery account. Those are prior-delivery observations. Validate this new campaign/handoff update through the repository checks and guarded sync; do not infer any new production observation for #1028.

## Evidence / Artifacts

`docs/governance/build-to-1.0-campaign-2026-08-16.md`
`docs/evals/three-pillars-corrective-delivery-2026-09-19.md`
`.gzkit/handoffs/20260919T232754Z-three-pillars-corrections-delivered.md`

## Settled Rulings

964 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
