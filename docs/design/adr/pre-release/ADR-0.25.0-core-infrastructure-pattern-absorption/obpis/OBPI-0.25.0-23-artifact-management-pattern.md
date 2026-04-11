---
id: OBPI-0.25.0-23-artifact-management-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 23
status: Completed
lane: heavy
date: 2026-04-09
---

# OBPI-0.25.0-23: Artifact Management Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-23 — "Evaluate and absorb opsdev/lib/artifacts.py (232 lines) — artifact scanning and registry cleanup"`

## OBJECTIVE

Evaluate `airlineops/src/opsdev/lib/artifacts.py` (232 lines) against gzkit's
artifact management surface and determine: Absorb, Confirm, or Exclude. The
airlineops module covers artifact scanning and registry cleanup. gzkit's
equivalent surface spans `registry.py` (220 lines) and related artifact
resolution in `commands/common.py`.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/opsdev/lib/artifacts.py` (232 lines)
- **gzkit equivalent:** `src/gzkit/registry.py` (220 lines) and artifact resolution utilities

## DECISION

**Decision: Exclude** — the module is domain-specific to airlineops's physical `artifacts/` directory convention. No upstream absorption warranted.

**Rationale:** airlineops's `opsdev/lib/artifacts.py` (232 lines) provides two capabilities: (1) regex-based scanning of Python source files for `artifacts/` path references and `.sqlite` file references, with usage classification as read/write/mkdir/other; and (2) artifact directory cleanup based on a JSON registry allowlist (`config/artifacts_registry.json`). gzkit's artifact management surface (`registry.py`, 220 lines) provides governance content type metadata — Pydantic-modeled type definitions (ADR, OBPI, PRD, Rule, Skill, etc.) with frontmatter validation, lifecycle states, and canonical path patterns. The `sync.py` module adds governance artifact discovery via `scan_existing_artifacts()` (rglob for markdown files) and `parse_artifact_metadata()` (frontmatter extraction). These modules solve fundamentally different problems: airlineops manages physical file paths in an `artifacts/` directory tree; gzkit manages governance document types in a `docs/design/` + `.gzkit/` hierarchy. There is zero functional overlap. Additionally, the airlineops module uses `@dataclass` (gzkit requires Pydantic), `shutil.rmtree(ignore_errors=True)` (violates gzkit cross-platform policy), and hardcoded domain-specific preserved files (`live_ingest_report.json`, `attestations/`). The subtraction test is decisive.

## COMPARISON ANALYSIS

| Dimension | airlineops (232 lines) | gzkit equivalent | Assessment |
|-----------|----------------------|-----------------|------------|
| Purpose | Physical file management — scan code for `artifacts/` path refs, clean directories | Governance content type metadata — Pydantic models, frontmatter validation, lifecycle | Fundamentally different concerns |
| Scanning approach | Regex-based (`artifacts[\\/]`, `.sqlite`) scanning of `.py` source files | `rglob("ADR-*.md")` scanning of governance markdown files | Different targets, different methods |
| Data model | `Hit` dataclass with file/line/kind/literal/call | `ContentType` Pydantic model with name/schema/lifecycle/path pattern | No overlap |
| Classification | read/write/mkdir/other based on `open()`, `Path()`, `os.makedirs()`, `shutil.*` | N/A — gzkit doesn't classify file operations | Airline-specific housekeeping |
| Inventory reports | JSON + Markdown reports of artifact path usages | N/A — gzkit has no source-code usage scanning | Domain-specific reporting |
| Registry/allowlist | JSON registry of allowed artifact buckets (`config/artifacts_registry.json`) | Content type registry with Pydantic validation and vendor rendering rules | Different registry concepts |
| Cleanup | `clean_artifacts()` removes unrecognized dirs from `artifacts/`; preserves `.gitkeep`, `README.md`, `live_ingest_report.json`, `attestations/` | No physical directory cleanup — gzkit has stale mirror detection via `find_stale_mirror_paths()` | Hardcoded airline-specific preserved files |
| Convention compliance | `@dataclass`, `shutil.rmtree(ignore_errors=True)`, bare `print()` | Pydantic `BaseModel`, context managers, structured errors | airlineops violates gzkit conventions |

### Subtraction Test

Removing gzkit from airlineops leaves: regex-based scanning of Python source for `artifacts/` directory path references, usage classification by file operation type, inventory report generation, JSON registry loading for artifact bucket allowlists, and directory cleanup with airline-specific preserved files. Every capability is tied to airlineops's physical `artifacts/` directory convention and its `config/artifacts_registry.json` structure. gzkit has no `artifacts/` directory, no source-code scanning use case, and no registry-based directory cleanup need. The subtraction result is pure airlineops domain code.

## GATE 4 BDD: N/A Rationale

An Exclude decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- Neither codebase is assumed superior — comparison is evidence-based across concrete dimensions
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Phase 2 modules target governance tooling with high functional overlap

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Restructuring gzkit's registry around airlineops's artifact patterns

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
- [x] If `Absorb`, adapted gzkit module/tests are added or updated — N/A (Exclude decision, no code changes)

### Gate 3: Docs

- [x] Completed brief records a final `Absorb` / `Confirm` / `Exclude`
  decision
- [x] Comparison rationale names concrete capability differences and the chosen
  outcome

### Gate 4: BDD

- [x] If the chosen path changes operator-visible behavior,
  `features/core_infrastructure.feature` or module-specific behavioral proof is
  updated — N/A (Exclude decision, no operator-visible behavior change)
- [x] Otherwise the brief records `N/A` rationale for no external-surface
  change

### Gate 5: Human

- [ ] Human attestation required (Heavy lane)

## Acceptance Criteria

- [x] REQ-0.25.0-23-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-23-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Eight-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-23-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-23-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-23-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/opsdev/lib/artifacts.py
# Expected: airlineops source under review exists

test -f src/gzkit/registry.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-23-artifact-management-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing suite, no code changes for Exclude)
- [x] **Gate 3 (Docs):** Decision rationale completed with comparison table
- [x] **Gate 4 (BDD):** N/A recorded with rationale (Exclude, no behavior change)
- [ ] **Gate 5 (Human):** Attestation recorded

## Evidence

### Gate 1 (ADR)

- Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

- Existing gzkit test suite passes — no new tests needed for an Exclude decision
- Verification: `uv run gz test`

### Code Quality

- No code changes — Exclude decision is documentation-only
- Verification: `uv run gz lint`, `uv run gz typecheck`

### Value Narrative

Before this OBPI, there was no documented evaluation of whether airlineops's `opsdev/lib/artifacts.py` contained reusable patterns for gzkit. After reading the full 232-line module, every capability is tied to airlineops's physical `artifacts/` directory convention: regex-based scanning of Python source for `artifacts/` path references (`ART_RX`, `QUOTED_SQLITE_RX`), classification of file operations by context (`open()`, `Path()`, `os.makedirs()`, `shutil.*`), inventory report generation, JSON registry loading for artifact bucket allowlists, and directory cleanup with hardcoded preserved files (`live_ingest_report.json`, `attestations/`). gzkit's artifact management surface (`registry.py` + `sync.py`) solves a fundamentally different problem: governance content type metadata with Pydantic models, frontmatter validation, and lifecycle states. Zero functional overlap exists. The subtraction test is decisive.

### Key Proof


- Decision: Exclude
- Comparison: eight-dimension analysis in Comparison Analysis section
- airlineops artifacts.py: 232 lines, physical file management (regex scanning + directory cleanup)
- gzkit registry.py: 220 lines, governance content type metadata (Pydantic models + frontmatter validation)
- Subtraction test: entire module is airlineops domain — fails completely
- Convention violations: `@dataclass` (not Pydantic), `shutil.rmtree(ignore_errors=True)` (not cross-platform safe)

### Implementation Summary


- Decision: Exclude
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

airlineops's `opsdev/lib/artifacts.py` (232 lines) provides two capabilities: (1) regex-based scanning of Python source files for `artifacts/` path references and `.sqlite` file references, with usage classification as read/write/mkdir/other via context-aware pattern matching (`open()`, `Path()`, `os.makedirs()`, `shutil.*`); and (2) artifact directory cleanup based on a JSON registry allowlist (`config/artifacts_registry.json`) with hardcoded preserved files (`live_ingest_report.json`, `attestations/`). gzkit's artifact management surface (`registry.py`, 220 lines, + `sync.py` scanning utilities) provides governance content type metadata — Pydantic-modeled type definitions with frontmatter validation, lifecycle states, and canonical path patterns — plus governance artifact discovery via rglob and frontmatter extraction. The modules solve fundamentally different problems with zero functional overlap. The airlineops module uses `@dataclass` (gzkit requires Pydantic) and `shutil.rmtree(ignore_errors=True)` (violates gzkit cross-platform policy). The subtraction test is unambiguous: removing gzkit from airlineops leaves physical file management tied to airlineops's `artifacts/` directory convention. **Decision: Exclude.**
