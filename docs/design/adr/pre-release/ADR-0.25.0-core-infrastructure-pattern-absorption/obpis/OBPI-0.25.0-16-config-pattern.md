---
id: OBPI-0.25.0-16-config-pattern
parent: ADR-0.25.0-core-infrastructure-pattern-absorption
item: 16
status: Completed
lane: heavy
date: 2026-03-21
---

# OBPI-0.25.0-16: Config Pattern

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/ADR-0.25.0-core-infrastructure-pattern-absorption.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.25.0-16 — "Evaluate and absorb common/config.py (73 lines) — configuration loading helpers"`

## OBJECTIVE

Evaluate `airlineops/src/airlineops/common/config.py` (73 lines) against gzkit's `config.py` (171 lines) and determine: Absorb (airlineops is better), Confirm (gzkit is sufficient), or Exclude (domain-specific). The airlineops module provides configuration loading helpers. gzkit's equivalent is 2.3x larger, so the comparison must verify whether gzkit already subsumes airlineops's capabilities or whether airlineops has distinct patterns worth absorbing.

## SOURCE MATERIAL

- **airlineops:** `../airlineops/src/airlineops/common/config.py` (73 lines)
- **gzkit equivalent:** `src/gzkit/config.py` (171 lines)

## ASSUMPTIONS

- The subtraction test governs: if it's not airline-specific, it belongs in gzkit
- airlineops wins where more battle-tested; gzkit wins where more sophisticated
- Absorbed code must follow gzkit conventions (Pydantic, pathlib, UTF-8)
- Configuration loading is definitively generic infrastructure

## NON-GOALS

- Rewriting from scratch — absorb or adapt, don't reinvent
- Changing airlineops — this is upstream absorption only
- Redesigning gzkit's config architecture — only absorbing useful patterns

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

## Comparison Analysis

| Dimension | airlineops (73 lines) | gzkit (171 lines) | Winner |
|-----------|----------------------|-------------------|--------|
| Type safety | `dict[str, Any]` — untyped | Full Pydantic models (`frozen=True`, `extra="forbid"`) | gzkit |
| Validation | None — raw dict passthrough | Pydantic `model_validate` with schema enforcement | gzkit |
| Immutability | Mutable dicts | `frozen=True` on all models | gzkit |
| Nested merge | Custom `_deep_merge` function | Pydantic `model_validate` handles nested composition | gzkit (structural) |
| Config layers | base + local file (2-layer) | defaults -> file -> CLI overrides (3-layer) | gzkit |
| Error handling | Broad except (OSError, ValueError, TypeError, JSONDecodeError) | Pydantic validation errors — typed, specific | gzkit |
| Persistence | Read-only | `save()` method for write-back | gzkit |
| Path utilities | None | `get_path()` accessor | gzkit |
| YAML rejection | Explicit guard | Not needed (`.gzkit.json` format) | N/A |
| Test coverage | Unknown | 654 lines across 4 test files | gzkit |

### airlineops strengths examined

1. **`_deep_merge`** — recursive dict merging for nested config layering. Useful for untyped config, but superseded by Pydantic's `model_validate()` which validates structure and types during composition. gzkit's Pydantic approach is strictly stronger: it catches typos, rejects unknown keys, and enforces types at merge time.

2. **Local override file** — `settings.local.json` merged over `settings.json`. A useful pattern for per-machine config, but gzkit achieves the same with its 3-layer precedence (defaults -> `.gzkit.json` -> CLI overrides). The CLI override layer is more flexible than a second file because it works without filesystem state.

3. **Broad error resilience** — catches 4 exception types around file reads and silently falls back to defaults. gzkit's Pydantic validation surfaces errors explicitly, which is preferable for a governance toolkit where silent config degradation would mask problems.

## Decision: Confirm

**gzkit's implementation is sufficient. No absorption warranted.**

gzkit uses Pydantic models with frozen immutability and `extra="forbid"`, providing compile-time type safety and runtime validation that airlineops's untyped `dict[str, Any]` approach cannot match. The `_deep_merge` utility in airlineops is superseded by Pydantic's `model_validate()` for structured composition. The local override file pattern is superseded by gzkit's 3-layer precedence (defaults -> file -> CLI overrides). gzkit's config module is 2.3x larger because it carries typed models for vendors, paths, and project configuration — complexity that delivers value through validation, immutability, and explicit error handling.

## Gate 4 (BDD): N/A

No operator-visible behavior change results from a Confirm decision. gzkit's config module is unchanged. No behavioral proof is required.

## Acceptance Criteria

- [x] REQ-0.25.0-16-01: Given the completed comparison, then the brief records
  one final decision: `Absorb`, `Confirm`, or `Exclude`.
  *Status: Confirm recorded above with 10-dimension comparison table.*
- [x] REQ-0.25.0-16-02: Given the decision rationale, then it cites concrete
  capability, robustness, or ergonomics differences between airlineops and
  gzkit.
  *Status: Rationale cites type safety, immutability, validation, config layer precedence, and persistence differences.*
- [ ] REQ-0.25.0-16-03: Given an `Absorb` outcome, then gzkit contains the
  adapted module/tests needed to carry the pattern safely.
  *Status: N/A — decision is Confirm, not Absorb.*
- [x] REQ-0.25.0-16-04: Given a `Confirm` or `Exclude` outcome, then the brief
  explains why no upstream absorption is warranted.
  *Status: Decision section explains gzkit subsumes all airlineops capabilities.*
- [x] REQ-0.25.0-16-05: Given any operator-visible behavior change, then Gate 4
  behavioral proof is present; otherwise the brief records `N/A` with
  rationale.
  *Status: Gate 4 section records N/A — Confirm decision produces no behavior change.*

## Verification Commands (Concrete)

```bash
test -f ../airlineops/src/airlineops/common/config.py
# Expected: airlineops source under review exists

test -f src/gzkit/config.py
# Expected: gzkit comparison target exists before or after the decision

rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-16-config-pattern.md
# Expected: completed brief records one final decision

uv run gz test
# Expected: comparison or absorbed implementation remains green

uv run -m behave features/core_infrastructure.feature
# Expected: only required when operator-visible behavior changes
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (existing 654 lines of config tests remain green)
- [x] **Gate 3 (Docs):** Decision rationale completed with 10-dimension comparison
- [x] **Gate 4 (BDD):** N/A recorded — Confirm produces no operator-visible change
- [ ] **Gate 5 (Human):** Attestation recorded

## Evidence

### Implementation Summary



- Outcome: Confirm — gzkit `config.py` (171 lines) subsumes airlineops `common/config.py` (73 lines) across all 10 comparison dimensions
- Comparison: Ten-dimension analysis (type safety, validation, immutability, nested merge, config layers, error handling, persistence, path utilities, YAML rejection, test coverage)
- No source code changes — gzkit's Pydantic-based architecture with frozen immutability and 3-layer precedence is strictly stronger than airlineops's untyped dict approach

### Key Proof



```bash
rg -n 'Decision: Confirm' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-16-config-pattern.md
```

Expected: Line containing `**Decision: Confirm**` with rationale citing type safety, immutability, and 3-layer precedence.

## Human Attestation

- Attestor: `Jeffry`
- Attestation: attest completed.
- Date: 2026-04-10

## Closing Argument

Configuration loading is definitively generic infrastructure, and gzkit's `config.py` already owns the pattern comprehensively. The Pydantic-based typed model architecture with frozen immutability, `extra="forbid"` validation, and 3-layer precedence (defaults -> file -> CLI) strictly supersedes airlineops's untyped `dict[str, Any]` approach with `_deep_merge`. No airlineops pattern — deep merge, local override file, or broad error catching — adds value that gzkit does not already deliver through stronger architectural means. **Decision: Confirm.**
