---
id: OBPI-0.9.0-03-gzkit-breadth-parity-intake-tranche-plan
parent: ADR-0.9.0-airlineops-surface-breadth-parity
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.9.0-03-gzkit-breadth-parity-intake-tranche-plan: Gzkit breadth parity intake and tranche plan

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- **Checklist Item:** #3 — "OBPI-0.9.0-03: Produce `.gzkit/**` breadth parity intake and tranche plan with explicit import/defer/exclude rationale."

**Status:** Draft

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

- [ ] `.github/discovery-index.json` — repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/ADR-0.9.0-airlineops-surface-breadth-parity.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Canonical `.gzkit` source exists: `../airlineops/.gzkit/`
- [ ] Local `.gzkit` target exists: `.gzkit/`

**Existing Code (understand current state):**

- [ ] Previous parity evidence: `docs/design/briefs/REPORT-airlineops-parity-scan.md`
- [ ] Control surface manifest: `.gzkit/manifest.json`

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run -m unittest discover tests`
- [ ] Coverage maintained: `uv run coverage run -m unittest && uv run coverage report`

### Code Quality

- [ ] Lint clean: `uvx ruff check src tests`
- [ ] Format clean: `uvx ruff format --check .`
- [ ] Type check clean: `uvx ty check src`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uvx mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Human runs these at closeout. -->

```bash
# Gate 2: Tests
uv run -m unittest discover tests

# Specific verification for this OBPI
uv run gz parity scan
uv run gz agent sync control-surfaces
uv run gz status --table
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.9.0-03-01: Given canonical `.gzkit/**` parity deltas, when OBPI-03 completes, then each targeted path is classified as import, defer, or exclude.
- [ ] REQ-0.9.0-03-02: Given deferred or excluded paths, when intake evidence is reviewed, then each decision includes explicit rationale and follow-up owner.
- [ ] REQ-0.9.0-03-03: Given mirror surfaces affected by parity imports, when sync is run, then generated control surfaces are refreshed and status remains coherent.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:

---

**Brief Status:** Draft

**Date Completed:** —

**Evidence Hash:** —
