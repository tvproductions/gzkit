---
id: OBPI-0.25.0-20-adr-governance-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 20
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-20: ADR Governance Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-20 — "Evaluate and absorb opsdev/lib/adr_governance.py (535 lines) — evidence audit and autolink management"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/adr_governance.py` (535 lines) against
gzkit's governance surface and determine: Absorb, Confirm, or Exclude. The
airlineops module covers evidence audit and autolink management. gzkit's
equivalent surface spans `commands/covers.py` (178 lines) and
`traceability.py` (418 lines) — approximately 600+ lines across 2+ modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/adr_governance.py` (535 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/commands/covers.py`, `src/gzkit/traceability.py` (~600+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's governance surface around airlineops's approach

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

### airlineops: `opsdev/lib/adr_governance.py` (535 lines)

Three capabilities consolidated from separate scripts into a single module.

- **`evidence_audit()`** (~120 lines): Scans ADR files for title, status, and
  evidence section presence. Reports completed ADRs missing evidence. Uses
  `@dataclass(AdrRecord)`, hardcoded `ADR_DIR`, regex-based title/status parsing,
  TSV and human format output.
- **`adr_autolink()`** (~100 lines): Regex-based `@covers` decorator and
  `# ADR:` comment parsing via `parse_test_file()`. Collects ADR→tests mapping
  via `collect_test_map()`. Can write Verification sections into ADR files via
  `write_into_adr()`. Uses numeric 4-digit ADR IDs via `id_fmt()`.
- **`verification_report()`** (~165 lines): Discovers `@covers` decorators via
  `discover_covers()` regex scanning. Updates ADR Verification sections.
  Writes covers-map JSONL ledger entries via `_write_covers_ledger()` using
  `CoversMapEntry` from `ledger_schema`.

### gzkit equivalent surface (~1010 lines across 3 modules)

| Module | Lines | Role |
|--------|-------|------|
| `traceability.py` | 418 | AST-based `@covers` scanning, `covers()` decorator with runtime REQ validation, Pydantic models (`CoverageEntry`, `CoverageRollup`, `CoverageReport`), multi-level rollups |
| `commands/covers.py` | 178 | `gz covers` CLI with human/JSON/plain output, filtering by ADR/OBPI |
| `commands/adr_audit.py` | 414 | `adr_audit_check()` brief content inspection + `adr_covers_check()` REQ traceability |

### Dimension comparison

| Dimension | airlineops | gzkit |
|-----------|-----------|-------|
| Parsing | Regex-based (`@covers`, `# ADR:` comments) | AST-based (`scan_test_tree()`) |
| Coverage model | Flat ADR-to-tests mapping | Multi-level rollup: ADR/OBPI/REQ |
| Data models | stdlib `@dataclass` (`AdrRecord`) | Pydantic `BaseModel` (`CoverageEntry`, `CoverageRollup`, `CoverageReport`) |
| Evidence audit | Title/status/evidence section presence check | Brief content inspection (Implementation Summary, Key Proof, Human Attestation) |
| Ledger integration | Local covers-map JSONL file | Central ledger graph (receipt events) |
| Auto-writing | Injects Verification sections into ADR files | Not used (OBPI briefs + `@covers` workflow) |
| Runtime validation | None | `covers()` decorator validates REQ exists at decoration time |
| Output formats | TSV / human text | Human / JSON / plain via `gz covers` CLI |

## DECISION: Confirm

gzkit's governance surface already surpasses the airlineops module across all
three capabilities. No absorption warranted.

### Rationale

1. **Parsing fidelity:** gzkit uses AST-based scanning (`scan_test_tree`)
   which correctly handles string expressions, nested decorators, and multi-line
   constructs. airlineops uses regex (`DECOR_RX`, `COMM_RX`, `RX_COVERS`),
   which is fragile against non-trivial formatting.

2. **Coverage depth:** gzkit computes three-level rollups (ADR, OBPI, REQ)
   with `compute_coverage()`. airlineops provides only a flat ADR-to-test-path
   mapping via `collect_test_map()` and `discover_covers()`.

3. **Evidence audit:** gzkit's `adr_audit_check()` inspects brief content
   sections (Implementation Summary, Key Proof, Human Attestation) via the
   central ledger graph. airlineops's `evidence_audit()` only checks for the
   presence of title, status, and an `## Evidence` heading via regex.

4. **Convention compliance:** airlineops uses stdlib `@dataclass(AdrRecord)`,
   hardcoded `ADR_DIR` paths, and regex parsing. gzkit uses Pydantic
   `BaseModel` with `ConfigDict`, `pathlib` throughout, and AST-based
   scanning — conforming to project data model and cross-platform policies.

5. **Auto-writing is workflow-specific:** airlineops's `write_into_adr()`
   and `adr_autolink(write=True)` inject Verification sections directly into
   ADR markdown files. gzkit's governance workflow uses OBPI briefs with
   `@covers` decorators and the `gz-adr-autolink` skill as a manual workflow
   instead. This is an intentional design choice, not a gap.

### Gate 4 (BDD): N/A

No operator-visible behavior change. The Confirm decision validates that
gzkit's existing governance surface is sufficient — no new commands, flags,
output formats, or behavioral changes are introduced.

## Acceptance Criteria

- [ ] REQ-0.25.0-20-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
- [ ] REQ-0.25.0-20-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
- [ ] REQ-0.25.0-20-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
- [ ] REQ-0.25.0-20-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
- [ ] REQ-0.25.0-20-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/adr_governance.py
# Expected: airlineops source under review exists

test -f src/gzkit/commands/covers.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-20-adr-governance-pattern.md
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



- Decision: Confirm — gzkit's governance surface already surpasses airlineops
- Modules compared: airlineops adr_governance.py (535 lines, 3 capabilities) vs gzkit traceability + covers + adr_audit (~1010 lines)
- Parsing: gzkit uses AST-based scanning, airlineops uses regex
- Coverage: gzkit provides multi-level ADR/OBPI/REQ rollups, airlineops provides flat mapping
- Evidence: gzkit inspects brief content sections, airlineops checks section presence only
- Auto-writing: airlineops-specific workflow, intentionally not used in gzkit
- No code absorbed — gzkit's existing implementation is sufficient and architecturally superior

### Key Proof



```bash
uv run -m unittest tests/test_adr_governance_confirm.py -v
# 4 tests pass — confirming gzkit governance surface covers airlineops capabilities
```

## Human Attestation

- Attestor: `Jeffry`
- Date: 2026-04-11
- Attestation: attest completed

## Closing Argument

**Confirm.** airlineops's `adr_governance.py` is a 535-line module providing
evidence audit, autolink, and verification report capabilities via regex-based
parsing, stdlib dataclass models, and auto-writing Verification sections into
ADR files. gzkit's governance surface (`traceability.py` + `covers.py` +
`adr_audit.py`, ~1010 lines) already covers and surpasses all three
capabilities: AST-based scanning instead of regex, Pydantic models with
runtime REQ validation instead of stdlib dataclass, multi-level coverage
rollups (ADR/OBPI/REQ) instead of flat mapping, and brief content inspection
via the central ledger graph instead of section-presence checks. The
auto-writing feature is specific to airlineops's older workflow and
intentionally not used in gzkit's OBPI-based governance model.
