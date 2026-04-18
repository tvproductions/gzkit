---
id: OBPI-0.25.0-11-hooks-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 11
status: in_progress
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-11: Hooks Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-11 — "Evaluate and absorb core/hooks.py (34 lines) — hook dispatch system"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/core/hooks.py` (34 lines) against gzkit's `hooks/core.py` (482 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides a hook dispatch system with lifecycle callbacks. gzkit's equivalent is 14x larger and likely far more sophisticated, but the comparison must verify whether airlineops has any dispatch patterns or simplifications worth incorporating.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/core/hooks.py` (34 lines)
- **gzkit equivalent:** `src/gzkit/hooks/core.py` (482 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- gzkit's 14x larger implementation strongly suggests Confirm is the likely outcome
- airlineops's 34-line module may represent a simpler pattern that gzkit evolved beyond

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Simplifying gzkit's hook system to match airlineops's brevity

## DECISION

**Decision: Exclude** — the module is airline-domain-specific. No upstream absorption warranted.

**Rationale:** airlineops's `core/hooks.py` (34 lines) is a minimal callback registry for dataset-specific post-load pipeline hooks in the airline data warehouse. It provides two functions — `register_hook(dataset, name, fn)` and `get_hook(dataset, name)` — backed by a module-level dict keyed by `(dataset_name, hook_name)`. The module is used exclusively in `warehouse/ingest/loader/load_operations.py` for optional post-load callbacks during airline dataset curation.

gzkit's `hooks/` package (10 files, 482 lines in `core.py` alone) is a comprehensive governance enforcement system: artifact edit recording with ledger integration, OBPI completion validation gates, evidence enrichment with scope audit and git-sync state, hook script generation for Claude Code and Copilot agents, policy guards (`guards.py`), pipeline gates (`scripts/pipeline.py`), and routing dispatch (`scripts/routing.py`). These modules share a filename but serve fundamentally different domains — airline data loading callbacks versus governance lifecycle enforcement.

The airlineops pattern is trivially generic Python (register/get from a dict) and is not infrastructure worth absorbing. gzkit's hook system serves an entirely different purpose and is 14x larger with genuine architectural sophistication.

## COMPARISON ANALYSIS

| Dimension | airlineops `core/hooks.py` (34 lines) | gzkit `hooks/` package (10 files, 482+ lines) | Assessment |
|-----------|----------------------------------------|------------------------------------------------|------------|
| Purpose | Dataset-specific post-load callbacks for airline data warehouse | Governance enforcement: ledger recording, OBPI validation, evidence enrichment, agent hook scripts | **Different domains entirely** |
| Architecture | Module-level dict registry — `_HOOKS[dataset][hook_name] = callable` | Multi-module package: core logic, OBPI validation, policy guards, agent scripts, pipeline gates | gzkit is architecturally sophisticated |
| Scale | 34 lines, 2 functions, 1 dict | 10 files, 482 lines in core.py alone, full package structure | gzkit is 14x larger in core.py alone |
| Hook dispatch | Simple dict lookup — `get_hook()` returns callable or None | Event-driven ledger recording, validation chains, receipt emission, script generation | gzkit has structured lifecycle dispatch |
| Error handling | None — silent None return on missing hook | Structured validation with `RuntimeError` on OBPI transition failures, `OSError` handling for ledger writes | gzkit has governance-grade error handling |
| Type safety | `TYPE_CHECKING` import for `Callable` type hint | Full type annotations, Pydantic models in related modules | Both adequate for their scope |
| Cross-platform | N/A (no file I/O) | Path normalization (`\\` to `/`), UTF-8 encoding, `pathlib.Path` throughout | gzkit is cross-platform-aware |
| Test coverage | No tests found in airlineops for this module | gzkit hooks tested via integration with ledger and validation suites | gzkit has coverage |
| Domain coupling | `dataset` parameter, `"post_load"` hook name — airline data warehouse concepts | Governance artifacts, ADR/OBPI patterns, ledger events — governance domain | Both domain-specific, different domains |
| Reusable patterns | Dict-based callback registry (trivially generic Python, not worth extracting) | Artifact pattern matching, ledger integration, evidence enrichment, script generation | No reusable patterns in airlineops beyond basic Python |

### Subtraction Test

Removing gzkit from airlineops's `core/hooks.py` leaves: a two-level dict registry keyed by `(dataset_name, hook_name)` that stores and retrieves `Callable[[Any], None]` hooks for the airline data warehouse load pipeline. The only documented hook name is `"post_load"`, invoked in `warehouse/ingest/loader/load_operations.py` after dataset curation and ledger append. Every usage context is airline data loading — the `dataset` parameter refers to airline datasets (BTS, FAA), and the hook lifecycle is tied to the warehouse ingest pipeline. The pattern itself (register/get from a dict) is trivially generic Python, not a reusable infrastructure piece. The subtraction test fails: this module is pure airline domain code.

## GATE 4 BDD: N/A Rationale

An Exclude decision produces no code changes and no operator-visible behavior changes. No behavioral proof is required. The existing gzkit test suite remains green. Gate 4 is recorded as N/A per the parent ADR's lane definition: "a brief may record BDD as N/A only when the final decision is Confirm or Exclude with no external-surface change."

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

- [x] REQ-0.25.0-11-01: [doc] Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`. — **Exclude** recorded in Decision section.
- [x] REQ-0.25.0-11-02: [doc] Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit. — Ten-dimension comparison table in Comparison Analysis section.
- [x] REQ-0.25.0-11-03: [doc] Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely. — N/A (Exclude decision).
- [x] REQ-0.25.0-11-04: [doc] Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted. — Subtraction test and rationale in Decision and Comparison Analysis sections.
- [x] REQ-0.25.0-11-05: [doc] Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale. — N/A recorded in Gate 4 BDD section.

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/core/hooks.py
# Expected: airlineops source under review exists

test -f src/gzkit/hooks/core.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/briefs/OBPI-0.25.0-11-hooks-pattern.md
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

Before this OBPI, there was no documented evaluation of whether airlineops's `core/hooks.py` contained reusable hook dispatch patterns for gzkit. The ADR description listed this as a "hook dispatch system" — and after reading the actual source completely, the module is indeed a hook dispatch system, but a minimal one (34 lines) serving an entirely different domain. It provides a two-level dict registry (`register_hook`/`get_hook`) for optional post-load callbacks in the airline data warehouse ingest pipeline. gzkit already has `src/gzkit/hooks/` — a 10-file governance enforcement package with artifact edit recording, OBPI completion validation, evidence enrichment, agent hook script generation, policy guards, and pipeline gates. The comparison is not close: gzkit's hook infrastructure is 14x larger in core.py alone and architecturally sophisticated, while airlineops's module is a trivially generic Python pattern (dict-based callback lookup) tied to airline data loading semantics. The subtraction test is decisive: the entire airlineops module is airline domain code with no reusable hook patterns to absorb.

### Key Proof


- Decision: Exclude
- Comparison: ten-dimension analysis in Comparison Analysis section
- airlineops core/hooks.py: 34 lines, dataset-specific callback registry for airline data warehouse
- Module exports: `register_hook(dataset, name, fn)` and `get_hook(dataset, name)` — airline dataset hooks
- Hook names used: `"post_load"` — invoked in warehouse/ingest/loader/load_operations.py
- gzkit hooks/: 10 files, 482 lines in core.py — governance enforcement system
- gzkit hooks include: ledger recording, OBPI validation, evidence enrichment, script generation, policy guards
- Subtraction test: entire module is airline domain — fails completely

### Implementation Summary


- Decision: Exclude — airlineops core/hooks.py (34 lines) is airline-domain-specific
- Module: minimal callback registry for dataset post-load pipeline hooks in airline data warehouse
- Subtraction test: removing gzkit leaves a dict-based register/get pattern for airline dataset hooks
- gzkit already ahead: hooks/ package (10 files, 482+ lines) has governance-grade hook infrastructure
- Files created: none
- Files modified: this brief only (Exclude decision with ten-dimension comparison analysis)
- Tests added: none (no code changes)
- Date: 2026-04-10

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed
- Date: `2026-04-10`

## Closing Argument

airlineops's `core/hooks.py` (34 lines) is a minimal callback registry for dataset-specific post-load pipeline hooks in the airline data warehouse. The module provides two functions — `register_hook(dataset, name, fn)` and `get_hook(dataset, name)` — backed by a module-level dict keyed by `(dataset_name, hook_name)`. Its only documented usage is in `warehouse/ingest/loader/load_operations.py`, where the `"post_load"` hook runs optional callbacks after airline dataset curation and ledger append. The `dataset` parameter refers to airline datasets (BTS, FAA), and the hook lifecycle is tied to the warehouse ingest pipeline.

gzkit's `hooks/` package (10 files, 482 lines in `core.py` alone) is a comprehensive governance enforcement system providing artifact edit recording with ledger integration, OBPI completion validation gates, evidence enrichment with scope audit and git-sync state, hook script generation for Claude Code and Copilot agents, policy guards, and pipeline gates. These modules share a filename but serve fundamentally different domains — airline data loading callbacks versus governance lifecycle enforcement. The airlineops pattern (register/get from a dict) is trivially generic Python, not infrastructure worth absorbing. The subtraction test is unambiguous: every usage context in airlineops is tied to airline data loading semantics. There are no reusable hook patterns to absorb. **Decision: Exclude.**
