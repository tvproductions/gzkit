---
id: OBPI-0.25.0-19-adr-audit-ledger-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 19
status: in_progress
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-19: ADR Audit Ledger Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-19 — "Evaluate and absorb opsdev/lib/adr_audit_ledger.py (249 lines) — OBPI audit ledger consumption for Gate 5"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines) against
gzkit's audit ledger surface and determine: Absorb, Confirm, or Exclude. The
airlineops module covers OBPI audit ledger consumption for Gate 5 verification.
gzkit's equivalent surface spans `commands/obpi_audit_cmd.py` (423 lines) and
`validate_pkg/ledger_check.py` (379 lines) — approximately 800+ lines across
2+ modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/adr_audit_ledger.py` (249 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/commands/obpi_audit_cmd.py`, `src/gzkit/validate_pkg/ledger_check.py` (~800+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's audit ledger around airlineops's approach

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

- [ ] Intent recorded in this brief

### Gate 2: TDD

- [ ] Comparison-driven tests pass: `uv run gz test`
- [ ] If `Absorb`, adapted gzkit module/tests are added or updated

### Gate 3: Docs

- [ ] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [ ] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [ ] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated
- [ ] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## COMPARISON ANALYSIS

### airlineops: `opsdev/lib/adr_audit_ledger.py` (249 lines)

Layer 2 Gate 5 completeness checker. Reads an ADR-local `obpi-audit.jsonl`
ledger to determine if all OBPIs have passing proof before attestation.

- **Data model:** `LedgerCheckResult` (stdlib `dataclass`) with fields for
  missing, incomplete, and complete brief lists.
- **Core function:** `check_ledger_completeness(adr_id)` — resolves ADR
  folder via `adr_recon` helpers, parses the OBPI table from ADR markdown,
  reads ledger entries, classifies each brief as missing/incomplete/complete.
- **Formatter:** `format_ledger_check_report()` — renders a markdown report
  with summary table, categorized brief lists, and recommendations.
- **Dependencies:** `adr_recon` module (ADR folder/ledger/markdown resolution,
  OBPI table parsing, ledger entry reading).

### gzkit equivalent surface (~800+ lines across 3 modules)

| Module | Lines | Role |
|--------|-------|------|
| `commands/adr_audit.py` | 415 | `adr_audit_check()` — completeness check + REQ coverage |
| `validate_pkg/ledger_check.py` | 379 | JSONL ledger schema validation |
| `commands/obpi_audit_cmd.py` | 423 | Evidence gathering: test discovery, execution, coverage |

**`adr_audit_check()`** resolves the ADR via the central ledger graph
(not a local audit file), collects OBPI files via
`_collect_obpi_files_for_adr()`, and inspects each brief with
`_inspect_obpi_brief()` — checking frontmatter status, Implementation
Summary, Key Proof sections, and Human Attestation fields. Additionally
verifies `@covers` REQ traceability annotations.

### Dimension comparison

| Dimension | airlineops | gzkit |
|-----------|-----------|-------|
| Purpose | Gate 5 pre-attestation completeness | Same, plus REQ traceability |
| Data source | ADR-local `obpi-audit.jsonl` | Central ledger graph + brief file inspection |
| Result model | `LedgerCheckResult` (stdlib dataclass) | Dict-based + Rich console output |
| Completeness check | missing/incomplete/complete classification | findings-based (gaps vs complete) |
| Evidence depth | Reads ledger status values only | Inspects brief content sections |
| REQ coverage | Not present | `@covers` annotation verification |
| Cross-platform | pathlib + encoding (good) | pathlib + encoding (equivalent) |
| Error handling | Early returns with error field | `GzCliError` + `SystemExit` |

## DECISION: Confirm

gzkit's audit surface already surpasses the airlineops module. No absorption
warranted.

### Rationale

1. **Architecture (State Doctrine):** gzkit reads the central ledger graph
   (Layer 1/2 source of truth), not a local `obpi-audit.jsonl` file. This
   is architecturally superior — single source of truth, no local cache
   divergence risk.

2. **Evidence depth:** gzkit's `_inspect_obpi_brief()` checks brief file
   content (Implementation Summary, Key Proof, Human Attestation sections),
   not just ledger status values. This catches evidence gaps that ledger
   entries alone cannot detect.

3. **REQ traceability:** `adr_audit_check()` also verifies `@covers`
   annotations — a verification dimension airlineops does not check at all.

4. **Convention compliance:** airlineops uses stdlib `dataclass` for
   `LedgerCheckResult`, which violates gzkit's Pydantic model policy.
   Absorbing would require a full rewrite to Pydantic `BaseModel` with
   `ConfigDict`, defeating the purpose of pattern absorption.

5. **Dependency isolation:** airlineops module depends on `adr_recon`
   helpers (`find_adr_folder`, `find_adr_ledger_path`, `normalize_adr_id`,
   `parse_obpi_table`, `read_ledger_entries`). gzkit has its own ADR
   resolution pipeline (`resolve_adr_file`, `resolve_adr_ledger_id`,
   ledger graph queries).

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Confirm decision validates that
gzkit's existing audit surface is sufficient — no new commands, flags,
output formats, or behavioral changes are introduced.

## Acceptance Criteria

- [ ] REQ-0.25.0-19-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-19-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-19-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-19-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-19-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/adr_audit_ledger.py
# Expected: airlineops source under review exists

test -f src/gzkit/commands/obpi_audit_cmd.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-19-adr-audit-ledger-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Decision rationale completed
- [ ] **Gate 4 (BDD):** Behavioral proof present or `N/A` recorded with rationale
- [ ] **Gate 5 (Human):** Attestation recorded

### Implementation Summary


- Decision: Confirm — gzkit's audit surface already surpasses airlineops
- Modules compared: airlineops adr_audit_ledger.py (249 lines) vs gzkit adr_audit + validate_ledger + obpi_audit_cmd (~800+ lines)
- Architecture: gzkit uses central ledger graph (State Doctrine L1/L2), airlineops uses local obpi-audit.jsonl
- Evidence depth: gzkit inspects brief content sections, airlineops reads status values only
- REQ traceability: gzkit verifies @covers annotations, airlineops does not
- No code absorbed — gzkit's existing implementation is sufficient and architecturally superior

### Key Proof


```bash
uv run -m unittest tests/test_adr_audit_ledger_confirm.py -v
# 4 tests pass — confirming gzkit audit surface covers airlineops capabilities
```

## Human Attestation

- Attestor: `Jeffry`
- Date: 2026-04-11
- Attestation: attest completed

## Closing Argument

**Confirm.** airlineops's `adr_audit_ledger.py` is a 249-line Layer 2
Gate 5 completeness checker that reads a local `obpi-audit.jsonl` to
classify briefs as missing, incomplete, or complete. gzkit's audit surface
(`adr_audit_check` + `validate_ledger` + `obpi_audit_cmd`, ~800+ lines)
already covers this capability and surpasses it: central ledger graph
instead of local audit file, brief content inspection instead of status-only
checks, and `@covers` REQ traceability verification. The airlineops module
uses stdlib `dataclass` and depends on `adr_recon` helpers — absorbing it
would require a full rewrite with no net capability gain.
