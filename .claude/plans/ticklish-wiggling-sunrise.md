# Plan: OBPI-0.25.0-15 — Manifests Pattern Evaluation

## Context

OBPI-0.25.0-15 is part of ADR-0.25.0 (Core Infrastructure Pattern Absorption), which evaluates airlineops common modules for potential absorption into gzkit. This OBPI evaluates `airlineops/src/airlineops/common/manifests.py` (89 lines) against gzkit's existing manifest handling. The brief requires an Absorb/Confirm/Exclude decision with rationale.

**Pre-analysis conclusion: Exclude.** The airlineops manifests module is a demand-run artifact writer tightly coupled to airlineops's workflow (`load_config`, `airlineops.manifest.v1` schema, `artifacts/_artifacts/{run_id}/`). gzkit's manifests serve governance purposes — completely different domain. The generic primitives (SHA256 + deterministic JSON) are trivial and already available inline where needed. OBPI-0.25.0-03 previously Excluded the signature pattern on the same reasoning.

## Tasks

### Task 1: Update OBPI brief with comparison analysis and decision

**File:** `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-15-manifests-pattern.md`

Add the following sections to the brief (following the established pattern from completed OBPIs like 0.25.0-01 and 0.25.0-03):

1. **`## COMPARISON ANALYSIS`** — Side-by-side table comparing:
   - Feature completeness: airlineops has `write_manifest()` for demand runs; gzkit has `validate_manifest()` + `DocCoverageManifest` Pydantic models for governance
   - Error handling: airlineops uses `contextlib.suppress`; gzkit uses structured `ValidationError` returns
   - Cross-platform robustness: airlineops uses `Path` + `encoding="utf-8"` (good); gzkit same
   - Test coverage: gzkit has validation tests; airlineops coverage unknown from brief scope
   - Subtraction test: removing airline-specific concerns (config loading, run IDs, `airlineops.manifest.v1` schema) leaves only ~13 lines of SHA256 + JSON serialization — trivial utility, not a module

2. **`## DECISION`** — `**Decision: Exclude** — The manifests module is domain-specific to airlineops's demand-run artifact workflow and has no governance analog in gzkit.`
   - Rationale: Different purposes (run artifacts vs governance validation), tight coupling to airlineops config/schema, generic remnants are trivial utilities already handled inline

3. **`## CLOSING ARGUMENT`** — Summary of delivered evidence

4. **Gate 4 (BDD):** Mark as `N/A` — no operator-visible behavior change (Exclude = no code changes)

5. Update frontmatter `status: Pending` (leave as Pending — pipeline Stage 5 handles completion)

### Task 2: Verify quality gates pass

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run mkdocs build --strict
```

No code changes are made (Exclude decision), so these should pass unchanged.

### Task 3: Stage 4 ceremony (Human attestation — Heavy lane)

Present evidence template with:
- Value narrative (what was evaluated, what was decided)
- Key proof (grep showing decision recorded in brief)
- Evidence table (all quality checks)
- REQ coverage table (all 5 REQs mapped)

### Task 4: Stage 5 sync and accounting

- `gz obpi complete` with attestation
- Lock release, marker cleanup
- Two git-sync cycles
- Reconcile confirmation

## Verification

```bash
# Decision is recorded
rg -n 'Absorb|Confirm|Exclude' docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-15-manifests-pattern.md

# Quality gates
uv run gz test
uv run gz lint
uv run gz typecheck
```

## Critical Files

- `docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-15-manifests-pattern.md` — the only file modified
- `../airlineops/src/airlineops/common/manifests.py` — source material (read-only)
- `src/gzkit/validate_pkg/manifest.py` — gzkit comparison target (read-only)
- `src/gzkit/doc_coverage/manifest.py` — gzkit comparison target (read-only)
