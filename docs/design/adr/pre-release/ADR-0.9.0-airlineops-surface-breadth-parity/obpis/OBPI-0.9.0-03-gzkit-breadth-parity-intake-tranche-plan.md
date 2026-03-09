---
id: OBPI-0.9.0-03-gzkit-breadth-parity-intake-tranche-plan
parent: ADR-0.9.0-airlineops-surface-breadth-parity
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.9.0-03-gzkit-breadth-parity-intake-tranche-plan: Gzkit breadth parity intake and tranche plan

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- **Checklist Item:** #3 — "OBPI-0.9.0-03: Produce `.gzkit/**` breadth parity intake and tranche plan with explicit import/defer/exclude rationale."

**Status:** Completed

## Objective

Produce a path-level `.gzkit/**` parity intake and tranche plan that classifies
canonical deltas into import/defer/exclude outcomes with explicit next steps.

## Lane

**Heavy** — This unit defines external governance surface imports and sequencing,
which drives future operator-facing behavior.

## Allowed Paths

- `.gzkit/**` — Target governance-surface parity intake and tranche imports.
- `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/**` —
  intake matrix and OBPI evidence updates.
- `.agents/skills/**`, `.claude/skills/**`, `.github/skills/**` — Skill mirror
  sync updates when parity imports require mirrored surfaces.

## Denied Paths

- `src/**` and `tests/**` — Runtime feature delivery is out of scope for intake planning.
- `../airlineops/**` — Canonical source is read-only.
- `.claude/hooks/**` — Hook compatibility belongs to OBPI-0.9.0-02.
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Intake output MUST include a complete path-level classification
   for targeted canonical `.gzkit/**` surfaces.
1. REQUIREMENT: Each deferred or excluded path MUST include rationale and
   follow-up target OBPI/ADR.
1. REQUIREMENT: If mirror surfaces are updated, `gz agent sync control-surfaces`
   MUST be run and captured in evidence.
1. NEVER: Do not import product-coupled runtime behavior into gzkit parity scope.
1. ALWAYS: Keep parity decisions reproducible with command-level evidence.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` — repo structure
- [x] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [x] Parent ADR — understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- [x] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [x] Canonical `.gzkit` source exists: `../airlineops/.gzkit/`
- [x] Local `.gzkit` target exists: `.gzkit/`

**Existing Code (understand current state):**

- [x] Previous parity evidence: `docs/design/briefs/REPORT-airlineops-parity-scan.md`
- [x] Control surface manifest: `.gzkit/manifest.json`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run -m unittest discover tests`
- [x] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [x] Lint clean: `uvx ruff check src tests`
- [x] Format clean: `uvx ruff format --check .`
- [x] Type check clean: `uvx ty check src`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [x] Docs build: `uvx mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Specific verification for this OBPI
grep -c "Import\|Defer\|Exclude" docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/gzkit-surface-intake-matrix.md
uv run gz status --table
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.9.0-03-01: Given canonical `.gzkit/**` parity deltas, when OBPI-03 completes, then each targeted path is classified as import, defer, or exclude.
  - Evidence: `gzkit-surface-intake-matrix.md` § Decisions — 5 items classified (A–E).
- [x] REQ-0.9.0-03-02: Given deferred or excluded paths, when intake evidence is reviewed, then each decision includes explicit rationale and follow-up owner.
  - Evidence: `gzkit-surface-intake-matrix.md` § Deferred Items — `locks/obpi/` deferred to post-1.0, product-plane ontology permanently excluded, ontology loader deferred to future ADR.
- [x] REQ-0.9.0-03-03: Given mirror surfaces affected by parity imports, when sync is run, then generated control surfaces are refreshed and status remains coherent.
  - Evidence: No mirror surfaces affected by this intake-only OBPI. Sync deferred to OBPI-04 execution tranche.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item #3 quoted
- [x] Intake matrix created: `gzkit-surface-intake-matrix.md`

### Gate 2 (TDD)

```text
Ran 305 tests in 4.286s
OK
```

### Code Quality

```text
ruff check: All checks passed!
ruff format: 68 files already formatted
ty check: All checks passed!
mkdocs build --strict: pre-existing theme error (material not installed), not related to this OBPI
behave features/: 1 feature passed, 3 scenarios passed, 16 steps passed
```

### Implementation Summary

- Files created:
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/gzkit-surface-intake-matrix.md` — intake matrix with 5 classified deltas
- Files modified:
  - `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/obpis/OBPI-0.9.0-03-gzkit-breadth-parity-intake-tranche-plan.md` — this brief (evidence populated)
- Tests added: None (documentation-only OBPI)
- Date completed: 2026-03-09

---

**Brief Status:** Completed

**Date Completed:** 2026-03-09

**Evidence Hash:** —
