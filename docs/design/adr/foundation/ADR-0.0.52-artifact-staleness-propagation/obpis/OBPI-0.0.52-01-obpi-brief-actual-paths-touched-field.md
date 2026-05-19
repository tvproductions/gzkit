---
id: OBPI-0.0.52-01-obpi-brief-actual-paths-touched-field
parent: ADR-0.0.52-artifact-staleness-propagation
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.52-01-obpi-brief-actual-paths-touched-field: OBPI brief actual_paths_touched field

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md`
- **Checklist Item:** #1 — "OBPI brief schema addition — `actual_paths_touched` array field populated by `gz obpi complete` from staged-file analysis (precondition for Tier 1 path-overlap detection)"

**Status:** Draft

## Objective

Add an `actual_paths_touched` array field to the OBPI brief JSON Schema; have `gz obpi complete` populate it from staged-file analysis at completion time. This field is the data source for Tier 1 path-overlap detection in OBPI-03 — without it, the propagation pipeline has no canon-side record of which files an OBPI's implementation modified, so Tier 1's path-overlap branch cannot fire.

## Lane

**Heavy** — Changes the OBPI brief JSON Schema (runtime contract) and the `gz obpi complete` ceremony (CLI behavior).

## Allowed Paths

- `src/gzkit/schemas/obpi.json` — **PRIMARY:** add `actual_paths_touched` field
- `src/gzkit/commands/obpi_complete.py` — populate field at completion from staged-file analysis
- `src/gzkit/governance/propagation/paths.py` — new helper module for staged-path collection (repo-relative POSIX normalization)
- `tests/test_obpi_schema.py` — schema validation tests covering the new field
- `tests/governance/test_obpi_complete_paths.py` — new completion-population tests
- `features/staleness_propagation.feature` — BDD scenario stubs (full coverage authored in OBPI-09)
- `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/ADR-0.0.52-artifact-staleness-propagation.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- Trigger wiring (deferred to OBPI-04)
- Detection algorithm (deferred to OBPI-03)
- New runtime dependencies

## Creates These Files

- `src/gzkit/governance/propagation/paths.py` — **CREATE** new helper module for staged-path collection
- `tests/test_obpi_schema.py` — **CREATE** schema validation tests covering the new field
- `tests/governance/test_obpi_complete_paths.py` — **CREATE** new completion-population tests
- `features/staleness_propagation.feature` — **CREATE** BDD scenario stubs (full coverage in OBPI-09)

Existing files modified (not created): `src/gzkit/schemas/obpi.json`, `src/gzkit/commands/obpi_complete.py`.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/schemas/obpi.json` MUST add `actual_paths_touched` as `array<string>`, optional at authoring time, populated at completion time.
2. REQUIREMENT: `gz obpi complete` MUST populate `actual_paths_touched` from `git diff --name-only` analysis of files staged for the completion commit, scoped to the OBPI's allowed paths.
3. REQUIREMENT: Path entries MUST be repo-relative POSIX strings (use `Path.relative_to(root).as_posix()` per `.claude/rules/cross-platform.md` Quick Reference).
4. REQUIREMENT: `gz validate --documents` MUST recognize the new field as a valid OBPI schema property; existing briefs without the field MUST continue to validate.
5. REQUIREMENT: When the completion commit stages zero files in the OBPI's allowed paths, `actual_paths_touched` MUST be absent (not `[]`) — distinguishes "no completion event yet" from "completed with no file changes."
6. REQUIREMENT: Path collection MUST refuse paths outside the OBPI's allowed-paths declaration — out-of-scope file staging at completion fails the ceremony (exit 3) rather than being silently recorded.

> STOP-on-BLOCKERS: if the OBPI schema's existing field set is unclear, read `src/gzkit/schemas/obpi.json` in full before adding the new field.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item** — Quote: *"`actual_paths_touched` populated by `gz obpi complete` from staged-file analysis (precondition for Tier 1 path-overlap detection)"*. This OBPI delivers the precondition; OBPI-03 consumes it.
- [ ] Parent ADR § Intent — the upstream-canon → downstream-canon loop that Tier 1 path-overlap closes.
- [ ] Parent ADR § Consequences/Negative item 8 — assumption #3 (`actual_paths_touched` as design-coupling proxy) and its detectability hook.

**Governance (read once, cache):**

- [ ] `.claude/rules/cross-platform.md` § Render relative paths via `.as_posix()` — binding for path normalization.
- [ ] `src/gzkit/schemas/obpi.json` — existing schema structure.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/schemas/obpi.json` exists and contains the current OBPI brief schema.
- [ ] `src/gzkit/commands/obpi_complete.py` exists and contains the completion command implementation.
- [ ] Parent ADR file exists.

**Existing Code (understand current state):**

- [ ] `gz obpi complete` completion flow reviewed — where the new field-population hook should sit relative to the existing completion ceremony.
- [ ] Adjacent schema-validation tests reviewed for patterns and assertion style.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated (deferred to OBPI-10)

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.test_obpi_schema tests.governance.test_obpi_complete_paths -v
```

## Demo

```bash
# Schema delta visible
git diff src/gzkit/schemas/obpi.json

# Complete an OBPI in dry-run; observe populated actual_paths_touched
uv run gz obpi complete OBPI-0.0.52-09-bdd-coverage-staleness-propagation --dry-run --json \
  | python -c "import json,sys; print(json.load(sys.stdin).get('actual_paths_touched'))"

# Negative case: staging a file outside allowed paths fails the ceremony
git add unrelated/file.py
uv run gz obpi complete OBPI-0.0.52-09-bdd-coverage-staleness-propagation
# Expected: exit 3, prescriptive error naming the out-of-scope path
```

## Acceptance Criteria

- [ ] REQ-0.0.52-01-01: Given the OBPI schema, when `actual_paths_touched` is added as optional `array<string>`, then existing briefs without the field continue to validate via `gz validate --documents`.
- [ ] REQ-0.0.52-01-02: Given a completion commit with staged files, when `gz obpi complete` runs, then `actual_paths_touched` is populated from `git diff --name-only` scoped to the OBPI's allowed paths.
- [ ] REQ-0.0.52-01-03: Given any platform (Windows, macOS, Linux), when paths are recorded, then entries are repo-relative POSIX strings (`Path.relative_to(root).as_posix()`).
- [ ] REQ-0.0.52-01-04: Given a completion with zero staged files in allowed paths, when `gz obpi complete` runs, then `actual_paths_touched` is absent from the brief frontmatter (not present as `[]`).
- [ ] REQ-0.0.52-01-05: Given a completion commit with a staged file outside the OBPI's allowed paths, when `gz obpi complete` runs, then the ceremony fails exit 3 with a prescriptive error naming the out-of-scope path.
- [ ] REQ-0.0.52-01-06: Given schema tests, when they execute, then all four shapes are covered: present-and-valid, absent-at-authoring, empty-array-rejected, invalid-path-shape-rejected.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

Before: OBPI completion produced no canon-side record of which files an OBPI's implementation modified, so any downstream surface wanting to reason about file-level coupling (Tier 1 path-overlap detection in OBPI-03) had no data source. Now: every OBPI completion records `actual_paths_touched` in the brief, scoped to allowed paths, normalized to POSIX strings — Tier 1 path-overlap can read this directly as the canon-side path manifest.

### Key Proof

```bash
$ uv run gz obpi complete OBPI-X.Y.Z-NN --json | jq '.actual_paths_touched'
[
  "src/gzkit/governance/propagation/detect.py",
  "tests/governance/test_propagation.py"
]
```

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
