---
id: OBPI-0.19.0-09-deprecate-manual-gz-attest-during-closeout-subsumed-by-closeout
parent: ADR-0.19.0-closeout-audit-processes
item: 9
lane: Lite
status: Completed
---

# OBPI-0.19.0-09: Deprecate Manual `gz attest` During Closeout (Subsumed by Closeout)

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`
- **Checklist Item:** #9 — "Deprecate manual `gz attest` during closeout (subsumed by closeout)"

**Status:** Completed

## Objective

Add conditional deprecation logic to the `attest()` function in `src/gzkit/commands/attest.py` so that when an operator invokes `gz attest` for an ADR that has an active `closeout_initiated` event in the ledger, a deprecation warning is printed advising them that `gz closeout` now manages attestation inline. The standalone `gz attest` command remains fully functional for ADRs outside the closeout pipeline (edge cases, manual overrides, pre-closeout attestation).

## Lane

**Lite** — No new CLI subcommands, flags, or output schema changes. The `gz attest` command continues to work but conditionally warns when closeout is active. This is internal workflow guidance, not an external contract change.

## Allowed Paths

- `src/gzkit/commands/attest.py` — `attest()` function to add closeout-active detection and deprecation warning
- `src/gzkit/cli.py` — only if the `attest` subcommand registration needs adjustment (unlikely)
- `tests/test_attest_deprecation.py` — new test verifying conditional deprecation behavior

## Denied Paths

- `src/gzkit/commands/attest.py` core attestation logic — `_check_obpi_completion()`, `_attest_verification_steps()`, ledger append, closeout form write all remain unchanged
- `src/gzkit/ledger.py` — `attested_event()` factory unchanged
- `src/gzkit/lifecycle.py` — lifecycle transitions unchanged (OBPI-07 scope)
- `.gzkit/ledger.jsonl` — never edited manually
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: When `gz attest ADR-X.Y.Z` is invoked and the ledger contains a `closeout_initiated` event for that ADR, the command MUST print a deprecation warning to stderr before proceeding with attestation.
1. REQUIREMENT: The deprecation warning MUST include the text "deprecated" and reference `gz closeout` as the replacement workflow.
1. REQUIREMENT: After the warning, `gz attest` MUST continue to execute the full attestation flow normally (write ledger event, generate closeout form, update ADR attestation block).
1. REQUIREMENT: When `gz attest ADR-X.Y.Z` is invoked and the ledger does NOT contain a `closeout_initiated` event for that ADR, NO deprecation warning is emitted.
1. REQUIREMENT: The closeout-active check MUST use `Ledger.get_artifact_graph()` to read the `closeout_initiated` flag, consistent with how `closeout_cmd` and `audit_cmd` check closeout state.
1. NEVER: Remove or disable the `gz attest` command — it must remain available for edge cases outside the closeout pipeline.
1. NEVER: Alter the attestation event schema, exit codes, or closeout form generation.
1. ALWAYS: Use `console.print("[yellow]...[/yellow]", ...)` for the deprecation message consistent with existing gzkit warning patterns.

> STOP-on-BLOCKERS: if `closeout_initiated` is not tracked in `Ledger.get_artifact_graph()`, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` or `CLAUDE.md` — agent operating contract
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.19.0-closeout-audit-processes/ADR-0.19.0-closeout-audit-processes.md`

**Context:**

- [ ] `src/gzkit/commands/attest.py` — full `attest()` function implementation
- [ ] `src/gzkit/ledger.py` lines 1142, 1210-1212 — `closeout_initiated` flag in artifact graph
- [ ] `src/gzkit/cli.py` lines 2494-2540 — `closeout_cmd()` which writes `closeout_initiated` events

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/attest.py` exists with `attest()` function
- [ ] `src/gzkit/ledger.py` `get_artifact_graph()` returns `closeout_initiated` boolean per ADR
- [ ] `closeout_initiated_event()` factory exists in `src/gzkit/ledger.py`

**Existing Code (understand current state):**

- [ ] Pattern to follow: `src/gzkit/cli.py` `audit_cmd()` line 2646-2647 — reads `closeout_initiated` from graph
- [ ] Test patterns: `tests/test_lifecycle.py` for test structure conventions

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

## Acceptance Criteria

- [x] REQ-0.19.0-09-01: Given an ADR with a `closeout_initiated` event in the ledger, when `gz attest ADR-X.Y.Z --status completed` is invoked, then a deprecation warning containing "deprecated" and "gz closeout" is printed to stderr before attestation proceeds.
- [x] REQ-0.19.0-09-02: Given an ADR without a `closeout_initiated` event in the ledger, when `gz attest ADR-X.Y.Z --status completed` is invoked, then no deprecation warning is printed and attestation proceeds normally.
- [x] REQ-0.19.0-09-03: Given an ADR with a `closeout_initiated` event, when `gz attest ADR-X.Y.Z --status completed` completes after the warning, then the `attested` ledger event, closeout form, and ADR attestation block are all written identically to pre-deprecation behavior.
- [x] REQ-0.19.0-09-04: Given `gz attest ADR-X.Y.Z --status completed --dry-run` with closeout active, when the command runs, then the deprecation warning is still shown but no ledger event is written (dry-run semantics preserved).

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest tests.test_attest_deprecation -v
```

## Completion Checklist (Lite)

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Unit tests pass
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
test_warning_shown_when_closeout_active ... ok
test_no_warning_without_closeout ... ok
test_attestation_recorded_after_warning ... ok
test_dry_run_shows_warning_no_ledger_write ... ok
Ran 4 tests in 0.536s — OK
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
uv run gz test — 1086 tests passed
```

### Value Narrative

**Before:** `gz attest` operates identically whether or not closeout has been initiated for an ADR. Operators who have already run `gz closeout` may redundantly invoke `gz attest` outside the closeout pipeline, creating duplicate attestation events or confusion about which workflow produced the attestation record.

**After:** `gz attest` detects when closeout is active for the target ADR and warns the operator that attestation is now managed by `gz closeout`. The command still executes for backward compatibility and edge cases, but the warning guides operators toward the canonical consolidated workflow, reducing duplicate attestation and workflow confusion.

### Key Proof

```bash
# After implementation, attest during active closeout produces:
$ uv run gz attest ADR-0.19.0 --status completed
[yellow]Deprecated:[/yellow] Closeout is active for ADR-0.19.0-closeout-audit-processes.
Attestation is now managed by `gz closeout ADR-0.19.0`. Standalone `gz attest`
during closeout is deprecated and will be removed in a future release.

Checking prerequisite gates...
Attestation recorded:
  ADR: ADR-0.19.0-closeout-audit-processes
  Term: Completed
  ...

# Without closeout active, no warning:
$ uv run gz attest ADR-0.18.0 --status completed
Checking prerequisite gates...
Attestation recorded:
  ADR: ADR-0.18.0-subagent-driven-pipeline-execution
  Term: Completed
  ...
```

### Implementation Summary

- Files created/modified: `src/gzkit/commands/attest.py`, `tests/test_attest_deprecation.py`
- Tests added: 4 (test_warning_shown_when_closeout_active, test_no_warning_without_closeout, test_attestation_recorded_after_warning, test_dry_run_shows_warning_no_ledger_write)
- Date completed: 2026-03-22
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: Jeff (human operator)
- Attestation: attest completed
- Date: 2026-03-22

---

**Brief Status:** Completed

**Date Completed:** 2026-03-22

**Evidence Hash:** -
