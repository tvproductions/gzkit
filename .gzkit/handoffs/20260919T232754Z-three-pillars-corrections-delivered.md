---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-19T23:27:54Z'
agent: codex
session_id: 01a0bbd3-bfe1-7501-a817-5704f31bc130
continues_from: .gzkit/handoffs/20260919T223334Z-three-pillars-repairs-ruled-and-impact-pooled.md
---

## Current State Summary

VERIFIED: all enumerated corrective changes landed in cc5ed5bfa40a559f6f847f11cc961e7974309b7f. All 62 staged checks passed; 10,525 unit tests passed (four skipped), 432 BDD scenarios passed, canonical coverage and docs receipts passed. Final accounting is committed/synced by this session; verify remote refs and individual closure comments for delivery. The earlier five-row scope omitted retained repair leads; the corrective-delivery account now enumerates them.

## Important Context

Three-pillars corrections are direct GHI repairs, not OBPI work. ADR-0.35.0 remains the campaign front. ADR-0.36.0-07 received only an authorized draft reconciliation, not execution or activation. Broad currency remains retained and bounded impact remains pooled. Workflow fronts remain in docs/governance/build-to-1.0-campaign-2026-08-16.md; no fresh general triage, R&D, or whole-project health claim is made here.

## Decisions Made

- [operator-ruled] "NO do not start the pool. what else needs doing?"
- [operator-ruled] "DO NOT BUILD ANYTHING IN THAT adr! it is not active!!!"
- [operator-ruled] "then why don't you do these?" authorized the quoted seven-part corrective list, including draft-only reconciliation and verification/delivery.
- [agent-chose] Repair the reproduced source read/parse false success under GHI #1061; track the independent stdout-reconfiguration script defect in insights rather than expanding the repair.

## Immediate Next Steps

1. Verify the corrective commit, remote refs, and closure comments for #960, #1047, #1050 and #1055 through #1061 before relaying delivery.
2. For #1028, inspect for a qualifying normal operator-initiated post-treatment OBPI run; measure launches, proofs, reviews, rounds and exits only when such a run exists.
3. Carry the settled no-pool-build and no-ADR-0.36.0-execution rulings forward. Do not infer an OBPI initiation from this handoff.

## Pending Work / Open Loops

GHI #1028 remains open for production observation; the dated ledger census still has zero relevant post-treatment events. This does not prevent the selected defect repairs from being delivered. The independent scripts/check_proof_freshness.py stdout-capture robustness finding is recorded in insights at 2026-09-19T23:11:51.248631+00:00 and is not claimed fixed. No active OBPI locks were observed.

## Verification Checklist

Re-resolve live GHIs and remote refs. Validate the cited receipt IDs. All completed runtime checks and their environment correction are recorded in docs/evals/three-pillars-corrective-delivery-2026-09-19.md. No production observation is implied by tests or a clean tree.

## Evidence / Artifacts

`docs/evals/three-pillars-corrective-delivery-2026-09-19.md`
`docs/evals/three-pillars-implementation-plan-2026-09-19.md`
`tests/test_plan_audit_scope.py`
`tests/test_configured_path_consumers.py`
`tests/test_smoke_gate.py`

## Settled Rulings

961 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
