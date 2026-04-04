---
id: OBPI-0.0.15-02
parent: ADR-0.0.15-ghi-driven-patch-release-ceremony
item: 2
lane: Lite
status: Draft
---

# OBPI-0.0.15-02: GHI Discovery and Cross-Validation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- **Checklist Item:** #2 - "GHI discovery: find issues closed since last tag via `gh issue list`" and #3 - "Cross-validation engine: runtime label AND `src/gzkit/` diff for each GHI"

**Status:** Draft

## Objective

`gz patch release --dry-run` discovers GHIs closed since the last git tag,
cross-validates each against the `runtime` label and `src/gzkit/` diff evidence,
and reports qualification status with disagreements surfaced as warnings.

## Lane

**Lite** - Internal discovery logic; no external contract change.

## Allowed Paths

- `src/gzkit/commands/patch_release.py`
- `tests/adr/test_patch_release.py`

## Denied Paths

- `src/gzkit/commands/closeout.py`
- `.gzkit/ledger.jsonl`
- `RELEASE_NOTES.md`

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Discovery MUST use `gh issue list --state closed --search ...`
   to find GHIs closed after the most recent git tag date
2. REQUIREMENT: Cross-validation MUST check both the `runtime` label AND
   whether commits referencing the GHI modified files under `src/gzkit/`
3. REQUIREMENT: When label and diff disagree, the GHI MUST be flagged with a
   warning — NEVER silently included or excluded
4. REQUIREMENT: `--dry-run` output MUST show each GHI with its qualification
   status (qualified / label-only / diff-only / excluded)
5. REQUIREMENT: Discovery MUST gracefully handle repos with no tags (treat all
   closed GHIs as candidates)

> STOP-on-BLOCKERS: if `gh` CLI is not authenticated, print a clear error.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.15-ghi-driven-patch-release-ceremony/ADR-0.0.15-ghi-driven-patch-release-ceremony.md`
- [ ] OBPI-0.0.15-01 (prerequisite: CLI scaffold)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/patch_release.py` exists (from OBPI-01)
- [ ] `gh` CLI available

**Existing Code (understand current state):**

- [ ] `gh issue list` output format and filtering options
- [ ] `git log` commit-to-GHI linkage patterns (e.g., "Fixes #N", "GHI #N")

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
uv run gz patch release --dry-run
```

## Acceptance Criteria

- [ ] REQ-0.0.15-02-01: Discovers GHIs closed since last tag
- [ ] REQ-0.0.15-02-02: Cross-validates runtime label against src/gzkit/ diff
- [ ] REQ-0.0.15-02-03: Surfaces label/diff disagreement as warning
- [ ] REQ-0.0.15-02-04: `--dry-run` shows qualification status per GHI
- [ ] REQ-0.0.15-02-05: Handles no-tag repos gracefully

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
