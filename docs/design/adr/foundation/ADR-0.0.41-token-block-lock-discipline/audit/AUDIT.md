# ADR-0.0.41 Audit — Token-Block Lock Discipline

**Lifecycle transition:** COMPLETED → VALIDATED
**Audit date:** 2026-06-12
**Driver persona:** pipeline-orchestrator

## Feature Demonstration (Step 3 — mandatory)

### What the operator can do now that they could not before

Before ADR-0.0.41 the OBPI lock was a mutex with no audit trail: a token
(lock) could be surrendered with no register entry (handoff), which is the
asymmetry GHI #410 surfaced (5 surrenders / 0 register entries in 24h). After
this ADR:

1. **Lock-release is coupled to a register entry.** `gz obpi lock release`
   fails closed (exit 3) without a handoff document or an explicit
   `--abandon <category>:<reason>` — a token cannot be surrendered without a
   register entry (OBPI-02 staging → OBPI-03 fail-closed).
2. **Reaping is auditable.** `reap_expired_locks` writes an
   `abandoned_by_reaper` register entry and emits an `obpi_lock_released`
   event with `handoff_path` *before* deleting the lock — fail-closed on write
   or unlink failure (OBPI-03).
3. **The coupling is mechanically enforced.** `gz validate
   --lock-handoff-coupling` replays the ledger and fail-closes on any
   post-cutover release lacking a valid `handoff_path` or violating the
   Sub-Invariant 2 minimum-information rule — wired into the **default**
   `gz check` pipeline so the audit floor cannot be skipped (OBPI-04).
4. **The doctrine is canon.** `.gzkit/rules/token-block-discipline.md`
   specifies the five binding sub-invariants (abandon categories, min-info,
   reaping, TTL, release precondition) (OBPI-01).

### Commands + representative output

See `audit/proofs/value-demonstration.txt`. Highlights:

- `gz validate --lock-handoff-coupling` → exit 0 (live ledger clean).
- `gz check --json` → `Lock-handoff coupling: True` in the default pipeline.
- `gz obpi lock list --json` → `{"locks":[],"reaped":[],"count":0}`.
- Negative: release with no register entry → exit 3 FAIL-CLOSED.

Value demonstration was run live during the closeout ceremony walkthrough
(Step 4); per the gz-adr-audit skill that satisfies this audit's Step 3.

## Step 2 — Ledger Proof (Layer-2 trust)

`uv run gz adr audit-check ADR-0.0.41-token-block-lock-discipline` → **PASS**
(exit 0): "All linked OBPIs are completed with evidence" for OBPI-01/02/03/04.
17 REQs without `@covers` are **Advisory / non-blocking** — SUPPORT REQs
(proof = `artifact_edited` + structural validator), the STRUCTURAL-FENCE
REQ-04-08 (parent-ADR Boundary Invariants anchor), and OBPI-05's REQs
(withdrawn, superseded by ADR-0.0.65). Every BEHAVIOR REQ has a real `@covers`
test (`gz covers` behavior_uncovered = 0 across the active OBPIs).

OBPI-05 was operator-withdrawn (`obpi_withdrawn` event, 2026-06-11): its
handoff-surface REQs are superseded by ADR-0.0.65; its lock-lifecycle
warn-then-reap piece carried to GHI #603.

## Independent Verification Verdicts

Two fresh-context subagents (dispatched during the closeout ceremony):

### spec-reviewer → **PASS**

Every BEHAVIOR REQ backed by a real `@covers` test; every SUPPORT REQ has an
`artifact_edited` event; STRUCTURAL-FENCE REQ-04-08 anchored verbatim in the
parent ADR. Two cosmetic brief-path-drift notes (stated test path ≠ actual
location) — not coverage gaps.

### quality-reviewer → **COHERENT (closeable)**

The four increments compose a coherent end-to-end capability (canon →
primitives → fail-closed enforcement → audit validator); validator green on
the live ledger; cutover logic (`_find_cutover_ts` = latest OBPI-02/03 receipt)
correct against the live ledger. Architecture clean (frozen `LockData`,
`_LedgerSink` Protocol, fail-closed reap ordering).

## Step 5 — Shortfalls (all NON-BLOCKING; tracked)

| # | Finding | Disposition |
|---|---------|-------------|
| F1 | Normal-release handoff schema not self-serve (validator min-info fields vs `HandoffFrontmatter` `extra="forbid"`; handoff dir split-brain GHI #529) | OBPI-05 / ADR-0.0.65 (withdrawn surface work) |
| F2 | TTL default contradiction: canon 24h vs CLI `--ttl` 120m | Recommend Phase-E GHI (OBPI-01↔OBPI-02 drift) |
| F3 | SessionStart warn-then-reap not implemented | GHI #603 (Phase E) |
| — | closeout_proof didn't honor `obpi_withdrawn`/waived REQs | **Fixed in flight** — `fix(closeout-proof)` commit `e1a32cf1`, TDD |

## Summary Table

| Dimension | Result |
|-----------|--------|
| Completeness | 4/4 OBPIs attested_completed; OBPI-05 withdrawn (superseded) |
| Integrity | Validator green on live ledger; `gz check` green |
| Alignment | Code ↔ canon ↔ manpages ↔ parent-ADR Boundary Invariants consistent |
| Value demonstrated | Yes — closeout walkthrough + proofs/value-demonstration.txt |
| Shortfalls | 3 non-blocking (homed to ADR-0.0.65 / #603 / Phase-E); 1 fixed in flight |

## Attestation

- **Agent (audit):** pipeline-orchestrator — audit verification complete; ledger
  proof PASS; value demonstrated; no blocking shortfalls.
- **Human (Gate 5):** operator audit acceptance relayed into the `validated`
  receipt `attestation_text` (see ledger).
