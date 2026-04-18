---
id: OBPI-0.25.0-21-adr-reconciliation-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 21
status: attested_completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-21: ADR Reconciliation Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-21 — "Evaluate and absorb opsdev/lib/adr_recon.py (607 lines) — OBPI table sync with ledger proof"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/adr_recon.py` (607 lines) against gzkit's
reconciliation surface and determine: Absorb, Confirm, or Exclude. The
airlineops module covers OBPI table sync with ledger proof. gzkit's equivalent
surface spans `ledger_semantics.py` (547 lines) and `ledger_proof.py`
(112 lines) — approximately 660+ lines across 2+ modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/adr_recon.py` (607 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/ledger_semantics.py`, `src/gzkit/ledger_proof.py` (~660+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's reconciliation engine around airlineops's approach

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Confirm decision)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Comparison

### airlineops `adr_recon.py` (607 lines)

| Function | Lines | Assessment |
|----------|-------|-----------|
| `normalize_adr_id()` | 73-84 | ADR ID normalization; gzkit uses `resolve_adr_file()` with config-aware resolution |
| `find_adr_folder()` | 87-119 | Series-based directory lookup (`adr-0.0.x/`); airlineops-specific layout convention |
| `find_adr_markdown()` | 203-221 | ADR markdown file search; gzkit uses `resolve_adr_file()` |
| `read_ledger_entries()` | 142-200 | Per-ADR JSONL parsing (`obpi-audit.jsonl`); gzkit uses central event-sourced ledger |
| `parse_obpi_table()` | 224-291 | OBPI Decomposition table extraction from markdown; gzkit has `parse_wbs_table()` in `core/scoring.py` |
| `detect_drift()` | 294-346 | Table vs ledger status comparison (drift/missing/match); gzkit derives richer state via `derive_obpi_semantics()` |
| `update_obpi_table()` | 349-401 | Rewrites markdown Status column from ledger; **violates gzkit state doctrine** (L3→L1) |
| `adr_recon()` | 422-489 | Batch orchestration across all phases; gzkit uses `_build_adr_status_result()` for ADR-level aggregation |
| `format_recon_report()` | 526-607 | Markdown reconciliation report; gzkit uses `adr_status_cmd` with `--json`/human output modes |
| `_populate_obpi_drift()` | 404-419 | Per-OBPI anchor drift via external `drift_detection`; gzkit has built-in `_derive_anchor_analysis()` |

### gzkit reconciliation surface

| Module | Lines | Capabilities |
|--------|-------|-------------|
| `src/gzkit/ledger_semantics.py` | 547 | Per-OBPI state derivation: anchor analysis, scope drift, attestation validation, issue collection |
| `src/gzkit/ledger_proof.py` | 112 | REQ-proof input normalization and summary |
| `src/gzkit/commands/status.py` `obpi_reconcile_cmd` | ~50 | Per-OBPI reconciliation with auto-fix of brief frontmatter from ledger truth |
| `src/gzkit/commands/status.py` `_build_adr_status_result` | ~55 | ADR-level aggregation: lifecycle, closeout readiness, gate statuses, OBPI rows |
| `src/gzkit/core/scoring.py` `parse_wbs_table` | ~35 | OBPI Decomposition table parsing from ADR markdown |

### Capability Comparison

| Dimension | airlineops | gzkit | Winner |
|-----------|-----------|-------|--------|
| Ledger architecture | Per-ADR local JSONL (`obpi-audit.jsonl`) | Central event-sourced ledger graph | gzkit |
| State derivation | Simple table→ledger status comparison | Rich semantics: anchor analysis, scope drift, attestation, issues | gzkit |
| ADR table parsing | `parse_obpi_table()` (regex on markdown) | `parse_wbs_table()` in `core/scoring.py` (regex on markdown) | Equivalent |
| ADR-level aggregation | `adr_recon()` batch orchestration | `_build_adr_status_result()` + `_adr_obpi_status_rows()` | gzkit (richer) |
| Per-OBPI reconciliation | None (batch only) | `obpi_reconcile_cmd` with auto-fix | gzkit |
| Table status rewrite | `update_obpi_table()` writes to markdown | Not done — derived views are L3, not L1 | gzkit (by design) |
| Drift reporting | `format_recon_report()` markdown report | `adr_status_cmd` with JSON/human output | gzkit (mode-aware) |
| Anchor drift | Imports from `drift_detection` (external) | Built-in `_derive_anchor_analysis()` in `ledger_semantics.py` | gzkit |
| Convention compliance | stdlib dataclass, typing.Literal | Pydantic, pathlib, UTF-8 everywhere | gzkit |

## Decision: Confirm

gzkit's existing reconciliation surface is architecturally more sophisticated and already covers all functional capabilities provided by airlineops `adr_recon.py`. No absorption is warranted.

**Rationale:**

1. **Central ledger vs distributed JSONL**: gzkit uses a single event-sourced ledger graph. airlineops reads per-ADR `obpi-audit.jsonl` files — a distributed model that requires per-ADR filesystem traversal. gzkit's central model is more coherent and queryable.
2. **Rich state derivation**: gzkit's `derive_obpi_semantics()` (547 lines) produces per-OBPI state with anchor analysis, scope drift detection, attestation validation, and issue collection. airlineops's `detect_drift()` performs only a shallow table-vs-ledger status string comparison.
3. **Per-OBPI reconciliation**: gzkit provides `obpi_reconcile_cmd` which auto-fixes brief frontmatter from ledger truth. airlineops has no per-OBPI reconciliation — it operates only at the batch ADR level.
4. **State doctrine compliance**: airlineops's `update_obpi_table()` writes ledger-derived status back to ADR markdown tables, making L3 derived state look like L1 source-of-truth. This violates gzkit's state doctrine: "Do not let derived views silently become source-of-truth." gzkit's approach (compute views on demand from the central ledger) is architecturally correct.
5. **ADR-level aggregation**: gzkit's `_build_adr_status_result()` provides richer ADR-level state than airlineops's `adr_recon()`: lifecycle status, closeout readiness, gate statuses, and per-OBPI runtime state — all derived from the central ledger.
6. **Convention compliance**: airlineops uses stdlib `dataclass` and `typing.Literal`; gzkit uses Pydantic `BaseModel`, `pathlib.Path`, and UTF-8 encoding throughout — consistent with the project's data model policy.

### Gate 4 (BDD): N/A

No operator-visible behavior change. This is a Confirm decision — no code was added, removed, or modified. The existing reconciliation infrastructure continues to function identically.

## Acceptance Criteria

- [x] REQ-0.25.0-21-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [x] REQ-0.25.0-21-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [x] REQ-0.25.0-21-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [x] REQ-0.25.0-21-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [x] REQ-0.25.0-21-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/adr_recon.py
# Expected: airlineops source under review exists

test -f src/gzkit/ledger_semantics.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-21-adr-reconciliation-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (no code changes — Confirm decision)
- [x] **Gate 3 (Docs):** Decision rationale completed with side-by-side comparison
- [x] **Gate 4 (BDD):** N/A — Confirm decision, no operator-visible behavior change
- [ ] **Gate 5 (Human):** Attestation recorded

## Closing Argument

gzkit's reconciliation surface (`ledger_semantics.py`, `ledger_proof.py`, `obpi_reconcile_cmd`, `_build_adr_status_result`, and `parse_wbs_table`) already surpasses airlineops's `adr_recon.py` on every dimension that matters for a governance toolkit: central event-sourced ledger architecture, rich per-OBPI state derivation with anchor analysis and scope drift, per-OBPI auto-fix reconciliation, and ADR-level aggregation with lifecycle and closeout readiness. The airlineops module's signature capability — writing ledger-derived status back to ADR markdown tables — would violate gzkit's state doctrine by making derived views (L3) masquerade as source-of-truth (L1). gzkit's design computes views on demand from the central ledger, which is architecturally correct and more maintainable. No absorption is warranted; gzkit's implementation is the stronger pattern.

### Implementation Summary


- **Decision:** Confirm — gzkit's existing reconciliation surface is sufficient
- **Patterns evaluated:** 10 airlineops `adr_recon.py` functions (607 lines)
- **gzkit equivalents:** `ledger_semantics.py` (547 lines) + `ledger_proof.py` (112 lines) + `obpi_reconcile_cmd` (~50 lines) + `_build_adr_status_result` (~55 lines) + `parse_wbs_table` (~35 lines)
- **Ledger architecture:** gzkit uses central event-sourced graph; airlineops uses distributed per-ADR JSONL
- **State derivation:** gzkit derives rich semantics (anchor, scope, attestation); airlineops compares status strings
- **Table rewrite:** airlineops writes derived state to markdown (L3→L1 violation); gzkit computes on demand
- **Code changes:** None — Confirm decision, no absorption warranted

### Key Proof


```bash
rg -n 'Decision: Confirm' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-21-adr-reconciliation-pattern.md
# Expected: "## Decision: Confirm"
```

### Human Attestation

- Attestor: `Jeffry`
- Date: 2026-04-11
- Attestation: attest completed
