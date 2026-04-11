---
id: OBPI-0.25.0-18-adr-lifecycle-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 18
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-18: ADR Lifecycle Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-18 — "Evaluate and absorb opsdev/lib/adr.py (1603 lines) — ADR index generation, status tables, title normalization"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/adr.py` (1603 lines) against gzkit's ADR
lifecycle surface and determine: Absorb (airlineops has reusable patterns gzkit
lacks), Confirm (gzkit already covers this domain), or Exclude (domain-specific,
does not belong in gzkit). The airlineops module covers ADR index generation,
status tables, and title normalization. gzkit's equivalent surface spans
`registry.py` (220 lines), `sync.py` (361 lines), `commands/register.py`
(400 lines), and `core/models.py` (338 lines) — approximately 1300+ lines
across 4+ modules.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/adr.py` (1603 lines)
- **gzkit equivalent:** Distributed across `src/gzkit/registry.py`, `src/gzkit/sync.py`, `src/gzkit/commands/register.py`, `src/gzkit/core/models.py` (~1300+ lines total)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap — most will yield Absorb or Confirm rather than Exclude

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's ADR lifecycle around airlineops's monolithic module

## REQUIREMENTS (FAIL-CLOSED)

1. Read both implementations completely
1. Document comparison: feature completeness, error handling, cross-platform robustness, test coverage
1. Record decision with rationale: Absorb / Confirm / Exclude
1. If Absorb: adapt to gzkit conventions and write tests
1. If Confirm: document why gzkit's implementation is sufficient
1. If Exclude: document why the module is domain-specific

## DECISION

**Decision: Confirm** — gzkit's ADR lifecycle implementation is sufficient. No upstream absorption warranted.

**Rationale:** airlineops's `opsdev/lib/adr.py` (1603 lines) is a monolithic module that parses ADR state directly from markdown files using regex patterns, generates static markdown artifacts (`adr_index.md`, `adr_status.md`), normalizes H1 titles, and renders Rich Console status summaries. gzkit's ADR lifecycle surface (~1300+ lines across `registry.py`, `sync.py`, `commands/register.py`, `core/models.py`, plus `ledger.py`, `commands/common.py`, and `commands/adr_report.py`) is architecturally superior in a fundamental way: gzkit derives ADR state from an append-only **ledger** (JSONL event log) rather than parsing markdown files. This gives gzkit an authoritative state machine with 7 runtime states, ledger-based reconciliation with receipt verification, dynamic status views from ledger state, Pydantic-validated frontmatter via a content type registry, a 5-gate governance system with per-gate pass/fail tracking, and transactional OBPI completion with rollback. airlineops's regex-based markdown parsing approach is appropriate for its simpler governance model (AIRAC-cycle-based, 8 allowed statuses) but conflates discovery, parsing, rendering, and reconciliation in a single 1603-line module — concerns that gzkit correctly separates across focused modules.

## COMPARISON ANALYSIS

| Dimension | airlineops (1603 lines, 1 file) | gzkit (~1300+ lines, 4+ modules) | Winner |
|-----------|-------------------------------|----------------------------------|--------|
| State source | Markdown file parsing via regex (status, dates, titles) | Append-only ledger (JSONL event log) — derived state is rebuildable | gzkit |
| Architecture | Monolithic: discovery + parsing + rendering + reconciliation in one file | Distributed: `registry.py`, `sync.py`, `commands/register.py`, `core/models.py`, `ledger.py` | gzkit |
| ADR discovery | `discover_adrs()` scans filesystem, `discover_status_table_adrs()` filters by location | `scan_existing_artifacts()` in `sync.py` with rglob, content type registry with canonical path patterns | gzkit |
| Status model | 8 allowed statuses from config, regex extraction from markdown, `_normalize_status()` | Composite state machine: 7 runtime states, 4 proof states, 3 attestation states, lifecycle derived from ledger events | gzkit |
| Index/table generation | Static markdown files (`adr_index.md`, `adr_status.md`) generated from file scan | Dynamic views from `gz adr report` via ledger state — no static artifacts to drift | gzkit |
| Reconciliation | `ReconciliationResult` NamedTuple comparing parsed vs expected state within the same module | Ledger-based: `gz obpi reconcile` verifies receipt-to-brief coherence, anchor-based drift detection, validation anchors | gzkit |
| Metadata parsing | Regex patterns for status, dates, titles, superseded-by references from markdown body | YAML frontmatter parsing with Pydantic `AdrFrontmatter`/`ObpiFrontmatter` models, `parse_artifact_metadata()` | gzkit |
| Error handling | `sys.exit()` calls, bare `except Exception`, `_FALLBACK_STATUSES` hardcoded | Typed `GzCliError`/`GzkitError` hierarchy, 4-code exit map, transactional rollback in `obpi complete` | gzkit |
| Cross-platform | `pathlib.Path`, forward slash normalization in `_relpath()` | `pathlib.Path`, UTF-8 encoding, `PurePosixPath` for scope matching, forward-slash normalization | Tie |
| Title normalization | `normalize_title_line()`, `process_adr_file()` rewrites H1 headings in markdown | Not needed — gzkit uses frontmatter `id` field as canonical identifier, not H1 parsing | gzkit (by design) |
| Sort ordering | `_sort_key()` with semver tuple extraction and pool ADR handling | `canonicalize_id()` in ledger with semver normalization, semantic ordering enforced by convention | Tie |
| Test coverage | Covered by `test_adr.py` in airlineops test suite | Covered by `test_sync.py`, `test_registry.py`, `test_register.py`, `test_ledger.py` across focused test modules | Tie |

### Patterns Worth Noting (But Not Absorbing)

- airlineops's `_sort_key()` handles both legacy 4-digit ADR IDs (`ADR-0001`) and semver IDs (`ADR-0.1.0`) with pool ADR sorting. gzkit's `canonicalize_id()` in the ledger handles the same concern via semver normalization.
- airlineops's `_normalize_status()` coerces variant status strings to canonical forms. gzkit doesn't need this because status is derived from ledger events, not parsed from variable markdown formatting.
- airlineops's static index generation (`build_index()`, `generate_adr_index()`) is a different architectural choice — generating static markdown files from file scans. gzkit deliberately avoids static derived artifacts to prevent drift (Architectural Boundary #6: "Do not let derived views silently become source-of-truth").
- airlineops's `ReconciliationResult` NamedTuple is a clean pattern for capturing discrepancies, but gzkit's ledger-based reconciliation is more comprehensive with receipt verification and anchor-based drift detection.

## GATE 4 BDD: N/A Rationale

A Confirm decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## ALLOWED PATHS

- `src/gzkit/` — target for absorbed modules
- `tests/` — tests for absorbed modules
- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/` — this ADR and briefs

## QUALITY GATES (Heavy)

### Gate 1: ADR

- [x] Intent recorded in this brief

### Gate 2: TDD

- [x] Comparison-driven tests pass: `uv run gz test`
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Confirm decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Confirm decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-18-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Confirm** recorded in Decision section.
- [x] REQ-0.25.0-18-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Twelve-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-18-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Confirm decision).
- [x] REQ-0.25.0-18-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Rationale in Decision section: gzkit's ledger-based state derivation is architecturally superior to airlineops's regex-based markdown parsing.
- [x] REQ-0.25.0-18-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/adr.py
# Expected: airlineops source under review exists

test -f src/gzkit/registry.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-18-adr-lifecycle-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Confirm)
- [x] **Gate 3 (Docs):** Decision rationale completed
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Confirm, no behavior change)
- [ ] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

- Existing gzkit test suite passes — no new tests needed for a Confirm decision
- Verification: `uv run gz test`

### Code Quality

- No code changes — Confirm decision is documentation-only
- Verification: `uv run gz lint`, `uv run gz typecheck`

### Value Narrative

Before this OBPI, there was no documented comparison between airlineops's monolithic `opsdev/lib/adr.py` (1603 lines) and gzkit's distributed ADR lifecycle surface. The airlineops module combines ADR discovery, index generation, status table generation, title normalization, reconciliation, and Rich Console rendering in a single file that derives state from regex-based markdown parsing. gzkit's ADR lifecycle is architecturally superior: state is derived from an append-only ledger rather than parsed from variable markdown formatting, concerns are separated across focused modules (`registry.py`, `sync.py`, `commands/register.py`, `core/models.py`), and the governance model is richer (7 runtime states, 5-gate system, transactional OBPI completion). No absorption is warranted — gzkit's approach embodies Architectural Boundary #6: "Do not let derived views silently become source-of-truth."

### Key Proof


- Decision: Confirm
- Comparison: twelve-dimension analysis in Comparison Analysis section
- airlineops `opsdev/lib/adr.py`: 1603 lines, monolithic, regex-based markdown parsing for state
- gzkit ADR lifecycle: ~1300+ lines across 4+ modules, ledger-based state derivation
- Fundamental architectural difference: gzkit derives state from ledger events, airlineops parses markdown files
- gzkit state machine: 7 runtime states, 4 proof states, 3 attestation states vs airlineops's 8 config-driven statuses
- gzkit avoids static derived artifacts (adr_index.md, adr_status.md) — dynamic views prevent drift

### Implementation Summary


- Decision: Confirm
- Files created: none
- Files modified: this brief only
- Tests added: none (no code changes)
- Date: 2026-04-11

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: 2026-04-11

## Closing Argument

airlineops's `opsdev/lib/adr.py` (1603 lines) is a monolithic module that combines ADR discovery, index generation, status table generation, title normalization, reconciliation, drift detection, and Rich Console rendering. It derives ADR state from regex-based markdown file parsing — extracting status, dates, titles, and superseded-by references from markdown body text and generating static artifacts (`adr_index.md`, `adr_status.md`). gzkit's ADR lifecycle surface (~1300+ lines across `registry.py`, `sync.py`, `commands/register.py`, `core/models.py`, `ledger.py`, and `commands/adr_report.py`) is architecturally superior in a fundamental way: state is derived from an append-only ledger (JSONL event log), not parsed from variable markdown formatting. This gives gzkit a composite state machine with 7 runtime states, ledger-based reconciliation with receipt verification, dynamic status views that cannot drift from source-of-truth, Pydantic-validated frontmatter via a content type registry, a 5-gate governance system with per-gate tracking, and transactional OBPI completion with rollback. The monolithic airlineops module conflates discovery, parsing, rendering, and reconciliation — concerns that gzkit correctly separates. airlineops's static index generation directly contradicts gzkit's Architectural Boundary #6: "Do not let derived views silently become source-of-truth." **Decision: Confirm.**
