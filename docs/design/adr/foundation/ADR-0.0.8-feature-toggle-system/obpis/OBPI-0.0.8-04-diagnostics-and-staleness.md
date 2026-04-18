---
id: OBPI-0.0.8-04-diagnostics-and-staleness
parent: ADR-0.0.8-feature-toggle-system
item: 4
lane: Heavy
status: attested_completed
---

# OBPI-0.0.8-04: Diagnostics and Staleness

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.8-feature-toggle-system/ADR-0.0.8-feature-toggle-system.md`
- **Checklist Item:** #6 — "Stale flag detection and health reporting" and #7 — "Time-bomb CI test for expired flags"

**Status:** Completed

## Objective

Implement stale flag detection, flag health reporting, the `explain` output
for individual flags, integration with `gz check` for flag health validation,
and the standing `test_no_expired_flags` time-bomb test that fails CI when
any flag outlives its `remove_by` date.

## Lane

**Heavy** — Changes `gz check` output (operator-facing contract). The
time-bomb test is a new CI enforcement mechanism.

## Dependencies

- **Upstream:** OBPI-01 (registry models with date fields), OBPI-02 (FlagService for resolved values).
- **Downstream:** OBPI-05 (CLI surfaces the diagnostics this OBPI computes).
- **Parallel:** OBPI-03 (FeatureDecisions — no dependency in either direction).

## Allowed Paths

- `src/gzkit/flags/diagnostics.py` — Stale detection, health checks, explain logic
- `src/gzkit/flags/__init__.py` — Public API updates
- `src/gzkit/commands/check.py` — Integration point for `gz check` flag health
- `tests/test_flag_diagnostics.py` — Diagnostics unit tests
- `tests/test_no_expired_flags.py` — Standing time-bomb test

## Denied Paths

- `src/gzkit/flags/service.py` — Read-only; belongs to OBPI-02
- `src/gzkit/commands/flags.py` — CLI belongs to OBPI-05
- `.gzkit/ledger.jsonl` — Never edit manually

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `get_stale_flags(registry, as_of=date)` MUST return flags past their `remove_by` or `review_by` dates.
1. REQUIREMENT: `get_flag_health(registry, as_of=date)` MUST return a summary: total flags, stale count, flags approaching deadline (within 14 days), per-category counts.
1. REQUIREMENT: `explain_flag(key, service)` MUST return: flag metadata, current resolved value, resolution source, days until review/removal, staleness status.
1. REQUIREMENT: `gz check` MUST include flag health in its output, reporting stale flags as warnings.
1. REQUIREMENT: `test_no_expired_flags` MUST load the actual `data/flags.json` and fail if any flag is past `remove_by`. This test runs in CI.
1. REQUIREMENT: `test_no_expired_flags` MUST be a standalone test file, not mixed with other flag tests, so CI failure messages are unambiguous.
1. NEVER: Modify flag values or registry entries — diagnostics are read-only.
1. ALWAYS: Date comparisons use `datetime.date` not timestamps.

> STOP-on-BLOCKERS: OBPI-01 and OBPI-02 must be complete.

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist items #6 and #7 referenced

### Gate 2: TDD

- [x] Unit tests validate stale detection with flags past remove_by
- [x] Unit tests validate stale detection with flags past review_by
- [x] Unit tests validate non-stale flags pass cleanly
- [x] Unit tests validate health summary counts
- [x] Unit tests validate explain output includes all expected fields
- [x] Unit tests validate time-bomb test catches expired flags
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [x] Module docstring in diagnostics.py

### Gate 5: Human (Heavy)

- [x] Human attestation recorded

## Acceptance Criteria

- [x] REQ-0.0.8-04-01: Given a flag with `remove_by: 2026-03-01` and today is `2026-03-30`, when `get_stale_flags` runs, then the flag appears in the stale list.
- [x] REQ-0.0.8-04-02: Given no expired flags, when `test_no_expired_flags` runs, then the test passes.
- [x] REQ-0.0.8-04-03: Given an expired flag in the registry, when `test_no_expired_flags` runs, then the test fails with a message naming the expired flag.
- [x] REQ-0.0.8-04-04: Given `explain_flag("ops.product_proof", service)`, when called, then output includes: key, category, default, current value, source, review_by, days remaining.
- [x] REQ-0.0.8-04-05: Given `gz check` is run with stale flags present, when output is examined, then flag health warnings appear.

## Verification Commands

```bash
# Diagnostics tests
uv run -m unittest tests.test_flag_diagnostics -v

# Time-bomb test (standalone)
uv run -m unittest tests.test_no_expired_flags -v
# Expected: PASS (no expired flags in current registry)

# gz check integration
uv run gz check
# Expected: flag health section appears in output

# Full suite regression
uv run gz test

# Code quality
uv run gz lint
uv run gz typecheck
```

## Evidence

### Implementation Summary

- Files created: `src/gzkit/flags/diagnostics.py`, `tests/test_flag_diagnostics.py`, `tests/test_no_expired_flags.py`
- Files modified: `src/gzkit/flags/__init__.py`, `src/gzkit/commands/quality.py`
- Validation: 17 OBPI-specific tests pass, 2146 full suite tests pass, lint clean, typecheck clean, 99% coverage on diagnostics.py
- Date completed: 2026-03-30

### Key Proof

```bash
$ uv run -m unittest tests.test_flag_diagnostics tests.test_no_expired_flags -v
# 17/17 pass — stale detection, health summary, explain, time-bomb all verified
```

## Human Attestation

- **Attestor:** jeff
- **Date:** 2026-03-30
- **Attestation:** attest completed

---

**Brief Status:** Completed
**Date Completed:** 2026-03-30
