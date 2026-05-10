# AUDIT PLAN (Gate-5) — ADR-0.0.31 Distribution Invariant Doctrine

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.0.31-distribution-invariant-doctrine |
| ADR Title | Distribution Invariant (T0 Doctrine) |
| SemVer | 0.0.31 |
| Kind / Lane | foundation / lite |
| ADR Dir | `docs/design/adr/foundation/ADR-0.0.31-distribution-invariant-doctrine/` |
| Audit Date | 2026-05-10 |
| Auditor(s) | Claude Opus 4.7 (agent) + g0 (operator attestation) |

## Purpose

Confirm ADR-0.0.31 doctrine deliverables are present, citable, and self-consistent. This ADR authors **doctrine only** (no mechanical enforcement) — the audit verifies the three doctrine surfaces named in the ADR's Decision section, the cross-link graph, and the scorecard registration.

**Audit Trigger:** Standalone Gate-5 validation. All three OBPIs (`OBPI-0.0.31-01`, `-02`, `-03`) are `attested_completed` per `gz adr report`.

## Scope & Inputs

**Doctrine surfaces authored by this ADR:**

- `docs/governance/trust-doctrine.md` — T0 paragraph + extended layer table (T0/T1/T2/T3) — OBPI-0.0.31-01
- `docs/governance/advisory-rules-audit.md` — T0 scorecard entry classified **Promotable**, citing ADR-0.0.32 — OBPI-0.0.31-02
- `docs/governance/distribution_invariant_catalog.md` — T0 failure-mode catalog with worked examples + decision tree — OBPI-0.0.31-03

**Cross-link graph the ADR claims:**

- ADR Evidence section → `trust-doctrine.md` layer table
- `trust-doctrine.md` T0 paragraph → ADR-0.0.31 (Doctrine source) and ADR-0.0.32 (mechanical enforcement)
- `trust-doctrine.md` → `distribution_invariant_catalog.md` (See also)
- `advisory-rules-audit.md` row 57 → ADR-0.0.31 + ADR-0.0.32 + OBPI-0.0.32-07 promotion target

**Mechanical scope explicitly EXCLUDED (owned by ADR-0.0.32):** wheel package-data extension, scaffolders, `gz init --update`, `gz validate --distribution`, build-then-install smoke test.

## Planned Checks

| # | Check | Command / Method | Expected Signal |
|---|-------|------------------|-----------------|
| 1 | Ledger proof (Layer-2 trust) | `uv run gz adr audit-check ADR-0.0.31` | PASS — all 3 OBPIs completed with evidence |
| 2 | ADR lifecycle pre-state | `uv run gz adr report ADR-0.0.31` | Lifecycle=Completed, OBPI 3/3, QC=READY |
| 3 | Trust-doctrine T0 paragraph present | grep `T0` in `docs/governance/trust-doctrine.md` | T0 layer row + dedicated section + verbatim failure-mode quote |
| 4 | Advisory-scorecard T0 entry registered | grep `T0` in `docs/governance/advisory-rules-audit.md` | Row 57 classified Promotable, cites ADR-0.0.31 + ADR-0.0.32 + OBPI-0.0.32-07 |
| 5 | Catalog file authored | filesystem check + heading scan | File exists; contains worked examples + "Is This a T0 Breach?" decision tree |
| 6 | Advisory-scorecard self-test | `uv run gz validate --advisory-scorecard` | Pass (Layer-3 freshness invariant holds) |
| 7 | Document validity | `uv run gz validate --documents` | Pass — frontmatter + schema for all governance docs |
| 8 | CLI surface coverage | `uv run gz cli audit` | "94/94 commands fully covered" |

## Risk Focus

- **Doctrine drift risk.** T0 is an upstream invariant; if the layer-table phrasing in `trust-doctrine.md` ever falls out of sync with the ADR's Decision section, downstream ADR-0.0.32 mechanical enforcement loses its citable referent. The audit verifies the verbatim failure-mode quote is present.
- **Promotable→Mechanical handoff.** Scorecard row 57 must cite OBPI-0.0.32-07 by name; without that pointer the Promotable→Mechanical promotion convention is broken.
- **Coverage advisory.** `gz adr audit-check` reports 14 REQs without `@covers` traceability (advisory, non-blocking). For a doctrine-only foundation ADR with no mechanical surface, REQ→test coverage is intentionally out of scope; the deliverables ARE the documentation surfaces themselves. Documented as expected, not a shortfall.

## Acceptance Criteria

- All Planned Checks executed; results recorded in `audit/AUDIT.md` with ✓/✗/⚠.
- Proof logs saved under `audit/proofs/` and referenced in `AUDIT.md`.
- ADR lifecycle transitions Completed → Validated after operator's verbal `accept audit` ack and `emit-receipt --event validated`.
- No mechanical changes proposed (doctrine-only ADR; mechanics owned by ADR-0.0.32).

## Attestation Placeholder

Operator verbal ack required between `audit-begin` and `emit-receipt`. Operator: g0. Final attestation captured in `AUDIT.md` § Attestation.
