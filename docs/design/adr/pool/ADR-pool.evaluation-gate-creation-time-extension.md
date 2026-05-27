---
id: ADR-pool.evaluation-gate-creation-time-extension
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: GHI #517
---

# ADR-pool.evaluation-gate-creation-time-extension: Evaluation Gate Creation-Time Extension

## Status

Pool

## Intent

The `evaluate_adr` quality gate exists at `src/gzkit/commands/adr_promote.py:381-394` and correctly blocks non-GO promotion with `SystemExit(3)`. But the gate fires in exactly one of five+ ADR lifecycle paths: pool → canonical promotion via `gz adr promote`. ADR creation (`gz plan create --kind {foundation,pool,feature}`) bypasses it entirely; foundation lifecycle Pending → Validated via `gz audit` does not consult it; the `--write-scorecard` flag defaults to false so the scorecard markdown the SKILL prose assumes exists may not exist.

Backlog impact (per `gz status --table`, 2026-05-26): ~35 of 62 currently-Pending foundation ADRs were created without an eval verdict ever being computed. The remediation downstream (closeout proof-binding, audit ledger taxonomy) cannot reach prior creation events; gating creation-time stops the bleeding upstream.

Surfaced by cross-analyst diagnosis in GHI #517. Originally framed by the Lead Architect (`artifacts/reports/ghi-517-lead-architect-diagnosis.md`); narrowed and re-grounded after Codex disputed Lead's F4 line range and primary-source verification revealed the gate exists at `:381-394` (not `:55-200`). See `artifacts/reports/ghi-517-cross-analyst-reconciliation.md` § Dispute D1.

### Absorbed findings

| ID | Surface | Defect | Severity |
|---|---|---|---|
| P3-r1 | `src/gzkit/commands/plan.py` (430 lines) | Zero `evaluate_adr` references — creation does not run the eval gate at any `--kind` | 4 |
| P3-r4 | `audit_cmd.py:329` | Pending → Validated transition gates on `failures==0` only; no `evaluate_adr` consultation in the path | 4-5 |
| P3-r3 | `adr_promote.py:414-417` | `--write-scorecard` defaults to False; downstream SKILL prose assumes the scorecard exists | 2 |

(P3-r2 — `--force` bypass discipline — is scoped to the sibling pool ADR `ADR-pool.adr-promote-force-bypass-attestation`.)

## Decision

1. **Extend `evaluate_adr` to `gz plan create`.** Run the eval at creation time for all `--kind` values. Lane behavior: Pending creation emits a *warning* receipt on non-GO verdict; Validated promotion remains fail-close.
2. **Gate Pending → Validated transition on most-recent eval verdict.** `audit_cmd.py:329` must consult `evaluate_adr` (or read the most recent `adr_evaluation_event` from the ledger for the target ADR) before emitting `validated`. Non-GO verdict blocks lifecycle transition even when audit `failures==0`.
3. **Default `--write-scorecard` to True.** The scorecard markdown is referenced by closeout templates and SKILL prose; making it opt-in for canonical promotions creates Layer-3 derived-view drift (state-doctrine violation per `.claude/rules/governance-core.md`).
4. **Backfill scope is out of scope.** This pool ADR does not retroactively evaluate the ~35 Pending foundation ADRs created without eval. A sibling pool ADR or chore handles backfill if operator chooses; the immediate decision is to gate forward creation/promotion.

## Alternatives Considered

1. **Run eval inside `gz audit` only (not at creation).** Smaller diff; centralizes the gate. **Rejected:** moves the source-control wedge downstream, doesn't prevent the backlog accumulation that motivated the pool ADR.
2. **Treat `gz plan create` as taxonomy-scaffold-only, run eval as a separate `gz adr evaluate --before-promote` step.** Preserves current command shape. **Rejected:** Codex's source-control rationale (D7 partial) — gate as close to the point of artifact creation as practical, not as a separate operator-remembered step.

## Patterns surfaced

- **Prose-vs-mechanics.** The `evaluate_adr` function exists and is well-tested; only the wiring at lifecycle boundaries was prose-prescribed (in SKILL files) rather than mechanically enforced. The fix replaces prose assumption with CLI gate calls.

## Origin

`artifacts/reports/ghi-517-cross-analyst-reconciliation.md` § Revised P3 findings.
