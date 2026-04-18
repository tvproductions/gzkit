---
id: OBPI-0.0.16-06-validator-pool-skip-parity
parent: ADR-0.0.16
item: 6
lane: Lite
status: Draft
---

# OBPI-0.0.16-06-validator-pool-skip-parity: Validator Pool Skip Parity

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- **Checklist Item:** #6 - "OBPI-0.0.16-06: Restore validator-chore parity by skipping pool ADRs in `gz validate --frontmatter` — the chore library `frontmatter_coherence.py` already skips pool ADRs (and its source comment names this exact contract), but the validator was authored without the filter. Surfaced by OBPI-04 dogfooding 2026-04-18 (GHI #192). Lite lane; ~5-line filter + TDD; unblocks OBPI-04 REQ-04."

**Status:** Draft

## Objective

Add a pool-ADR skip filter to `src/gzkit/commands/validate_frontmatter.py` so the validator stops emitting false-positive errors on pool artifacts that have no per-artifact ledger entry to compare against. The chore library `src/gzkit/governance/frontmatter_coherence.py` already implements pool detection (`_is_pool_artifact` at line 214) and explicitly comments at line 300 that *"validator should not emit errors for pool ADRs (no ledger entry to compare against)"* — OBPI-01 shipped the validator without honoring that contract. OBPI-04 dogfooding (live backfill receipt `artifacts/receipts/frontmatter-coherence/20260418T100437Z.json`) cleared 100% of active-surface drift but `gz validate --frontmatter` then exited 3 with 56 pool-only errors, blocking OBPI-04 REQ-04. This OBPI imports the chore library's pool helper, applies it before the validator's per-file comparison loop, and pins the behavior with TDD. Lite lane; ~5-line implementation diff + 2 unit tests (positive: pool skipped; negative: active drift still reported). Done means: `gz validate --frontmatter` exits 0 against the post-backfill repo, OBPI-04 can re-run REQ-04 and REQ-05 cleanly, and the validator's `--explain` mode handles pool input without emitting drift output.

## Lane

**Lite** - This OBPI remains internal to the promoted ADR implementation scope.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/validate_frontmatter.py` — add pool-skip filter to the validator's per-file iteration loop
- `tests/commands/test_validate_frontmatter.py` — TDD test asserting pool ADRs are skipped and active drift is still reported
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/obpis/OBPI-0.0.16-06-validator-pool-skip-parity.md` — record evidence in this brief
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-CLOSEOUT-FORM.md` — add OBPI-06 row to OBPI Status table

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: ALWAYS reuse `_is_pool_artifact` (or the public alias of it) from `gzkit.governance.frontmatter_coherence` as the single source of truth for pool detection. NEVER reimplement the pool-path or pool-id check in the validator.
2. REQUIREMENT: ALWAYS apply the pool-skip filter in the validator's per-file iteration loop BEFORE any frontmatter-vs-ledger field comparison. Skip pool ADRs silently — no error, no warning, no diff line in human or `--json` output.
3. REQUIREMENT: NEVER add a `--include-pool` (or equivalent) bypass flag. Pool ADRs have no per-artifact ledger entry by design (the chore library's line-300 comment is canonical: *"validator should not emit errors for pool ADRs (no ledger entry to compare against)"*).
4. REQUIREMENT: ALWAYS keep `--explain <ADR-ID>` pool-aware. If `--explain` is invoked on a pool ADR, exit 0 with an informational line ("ADR-pool.X is a pool artifact; no ledger entry to compare against") rather than emitting drift output.
5. REQUIREMENT: NEVER change behavior for non-pool ADRs. After OBPI-04's live backfill the active surface had 0 validator errors; that property MUST hold post-fix.
6. REQUIREMENT: TDD-Red — author the failing test FIRST in `tests/commands/test_validate_frontmatter.py`. The red test asserts `validate_frontmatter` returns no errors when given a pool-only fixture (or the live post-backfill repo). The test MUST fail against pre-fix `validate_frontmatter.py`.
7. REQUIREMENT: TDD-Green — implement the smallest change that makes the red test pass. Re-use the chore library's pool helper; do not introduce a new constant or path string.
8. REQUIREMENT: Maintain coverage floor ≥40%. Cover the pool-skip code path with at least one positive test (pool ADR skipped) and one negative test (active ADR with drift IS reported).
9. REQUIREMENT: Lite-lane gates apply: `gz lint`, `gz typecheck`, `gz test --obpi OBPI-0.0.16-06-validator-pool-skip-parity` all pass before completion. No BDD required (Lite lane).
10. REQUIREMENT: This OBPI does NOT extend the validator beyond pool-skip. Anything else (refactoring, error-message rewording, new --flags) is out of scope.
11. REQUIREMENT: After OBPI-06 attests, OBPI-04 REQ-04 and REQ-05 are re-runnable and MUST pass cleanly. Resume of OBPI-04 is the next operator action; this OBPI's evidence section MUST cite the resume protocol in `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/handoffs/2026-04-18-OBPI-0.0.16-04-paused-pending-OBPI-06.md`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md`
- [ ] Required path exists or is intentionally created in this OBPI: `frontmatter_coherence.py`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
# Smoke
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.16-06-validator-pool-skip-parity

# OBPI-specific — the load-bearing post-fix assertion (was failing pre-fix)
uv run gz validate --frontmatter; echo "EXIT=$?"   # MUST be 0

# Coverage parity (REQ → @covers gate)
uv run gz covers OBPI-0.0.16-06-validator-pool-skip-parity --json   # uncovered_reqs == 0
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.16-06-01: Given the live repo (post-OBPI-04 backfill state), when `gz validate --frontmatter` runs, then exit code is 0 and 0 errors are emitted.
- [ ] REQ-0.0.16-06-02: Given a fixture (or the live repo) containing a pool ADR with frontmatter `status` disagreeing from ledger, when `validate_frontmatter` iterates files, then the pool ADR is skipped silently (no error in human or `--json` output).
- [ ] REQ-0.0.16-06-03: Given an active (non-pool) ADR with frontmatter drift, when the validator runs, then the drift IS reported as an error (regression-guard — the pool-skip must not over-broaden to skip active drift).
- [ ] REQ-0.0.16-06-04: Given `gz validate --frontmatter --explain ADR-pool.X` invoked on a pool ADR, when it runs, then exit code is 0 and an informational line names the file as a pool artifact (no drift diff).
- [ ] REQ-0.0.16-06-05: Given the implementation, when reading `validate_frontmatter.py`, then `_is_pool_artifact` (or its alias) is imported from `gzkit.governance.frontmatter_coherence` rather than reimplemented locally.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
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
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
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

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
