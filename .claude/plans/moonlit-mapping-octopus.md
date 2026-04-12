# Plan: OBPI-0.25.0-24 — CLI Audit Pattern (Confirm Decision)

## Context

OBPI-0.25.0-24 compares airlineops `opsdev/lib/cli_audit.py` (238 lines) against gzkit's CLI audit surface. After reading both implementations completely, these are **fundamentally different tools** solving different problems:

- **airlineops**: low-level argparse parser introspection — walks `parser._actions` (private API) to check naming conventions, help text completeness, and cross-command option conflicts. 1 test (26 lines).
- **gzkit**: high-level documentation coverage validation — AST-driven 5-surface coverage (manpage, index_entry, operator_runbook, governance_runbook, docstring), manifest-driven obligations for 50+ commands, README Quick Start validation, orphan detection. 76 tests across 3 files.

**Decision: Confirm.** gzkit's CLI audit + doc_coverage subsystem (1,067+ lines across 5 modules, 76 tests) is architecturally superior. The airlineops module's unique capabilities (naming convention checking, option conflict detection) solve a narrower problem that gzkit's documentation-coverage approach already subsumes in practice, and rely on fragile `parser._actions` private API introspection.

## Implementation Steps

This is a documentation-only OBPI (Confirm decision, no code changes). The sole deliverable is the completed OBPI brief.

### Step 1: Update the OBPI brief

**File:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-24-cli-audit-pattern.md`

Following the completed Confirm-decision brief structural pattern, add/update these sections:

1. **Frontmatter**: Change `status: Pending` to `status: Completed`

2. **Comparison section** (insert after NON-GOALS, before REQUIREMENTS): Side-by-side analysis with:
   - airlineops function-level breakdown (5 functions + data models)
   - gzkit module-level breakdown (5 modules)
   - Capability comparison table across 12 dimensions:
     - Command discovery approach
     - Coverage model
     - Naming convention checks
     - Help text validation
     - Cross-command option conflicts
     - Manifest-driven obligations
     - Orphan detection
     - README validation
     - Data model quality
     - Test coverage (76 vs 1)
     - Output format
     - Convention compliance

3. **Decision section** with rationale citing concrete differences:
   - AST-based vs private API introspection
   - 5-surface documentation coverage vs parser structural checks
   - Manifest-driven 50+ command obligations vs ad-hoc checks
   - Pydantic models vs untyped dicts
   - 76 tests vs 1 test
   - Subtraction test: remaining airlineops capabilities (naming checks, option conflicts) rely on `parser._actions` private API, unsuitable for gzkit's AST-based approach

4. **Gate 4 BDD: N/A** — Confirm decision, no operator-visible behavior change

5. **Gate checkboxes**: Mark Gates 1-4 as `[x]` (Gate 5 stays `[ ]`)

6. **Acceptance criteria**: Mark all 5 REQs as `[x]` with annotations

7. **Completion checklist**: Mark Gates 1-4 as `[x]`

8. **Closing argument**: One-paragraph summary citing key evidence

9. **Implementation Summary + Key Proof**: Following completed Confirm-decision brief pattern

### Step 2: Run verification commands

```bash
test -f ../airlineops/src/opsdev/lib/cli_audit.py
test -f src/gzkit/commands/cli_audit.py
rg -n 'Absorb|Confirm|Exclude' docs/design/adr/.../OBPI-0.25.0-24-cli-audit-pattern.md
uv run gz test
uv run gz lint
uv run gz typecheck
```

### Step 3: Pipeline Stage 4 — Present evidence for human attestation

## Critical Files

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-24-cli-audit-pattern.md` (only file modified)
- `src/gzkit/commands/cli_audit.py` (read-only reference — gzkit side)
- `src/gzkit/doc_coverage/scanner.py` (read-only reference — gzkit side)
- `../airlineops/src/opsdev/lib/cli_audit.py` (read-only reference — airlineops side)

## Verification

- `uv run gz test` — all existing tests pass (no code changes)
- `uv run gz lint` — no regressions
- `uv run gz typecheck` — no regressions
- `rg 'Confirm'` in the brief — decision recorded
- Brief follows completed Confirm-decision structural pattern
