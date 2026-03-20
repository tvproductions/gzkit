---
id: OBPI-0.21.0-03-gz-covers-cli
parent: ADR-0.21.0-tests-for-spec
item: 3
lane: Heavy
status: Accepted
---

# OBPI-0.21.0-03: gz covers CLI

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #3 — "`gz covers` CLI with ADR/OBPI/REQ granularity and human/JSON/plain output"

**Status:** Accepted

## Objective

Expose requirement coverage reporting via `gz covers` CLI. Operators can query coverage at three levels: all (`gz covers`), by ADR (`gz covers ADR-0.20.0`), or by OBPI (`gz covers OBPI-0.20.0-01`).

## Lane

**Heavy** — New CLI command (external contract).

## Allowed Paths

- `src/gzkit/commands/covers.py` — CLI implementation
- `src/gzkit/cli.py` — register subcommand
- `tests/test_traceability.py` — CLI smoke tests
- `docs/user/commands/covers.md` — command documentation
- `features/test_traceability.feature` — BDD scenarios
- `features/steps/test_traceability_steps.py` — BDD steps

## Denied Paths

- `src/gzkit/traceability.py` — engine belongs to OBPIs 01-02
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz covers` with no arguments MUST show all-REQ coverage summary.
1. REQUIREMENT: `gz covers ADR-X.Y.Z` MUST show coverage for that ADR's REQs only.
1. REQUIREMENT: `gz covers OBPI-X.Y.Z-NN` MUST show coverage for that OBPI's REQs only.
1. REQUIREMENT: `--json` MUST output valid JSON to stdout.
1. REQUIREMENT: `--plain` MUST output one record per line.
1. REQUIREMENT: Exit code 0 always (coverage reporting is informational, not gating).
1. REQUIREMENT: `-h`/`--help` with description, usage, options, examples.

> STOP-on-BLOCKERS: OBPIs 01-02 must be complete.

## Acceptance Criteria

- [ ] REQ-0.21.0-03-01: Given `gz covers`, then shows coverage table with ADR-level rollup.
- [ ] REQ-0.21.0-03-02: Given `gz covers ADR-0.20.0`, then shows only REQs under that ADR.
- [ ] REQ-0.21.0-03-03: Given `gz covers --json`, then outputs valid JSON coverage report.
- [ ] REQ-0.21.0-03-04: Given `gz covers --help`, then shows description, usage, options, example.

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** Tests pass
- [ ] **Gate 3 (Docs):** Docs build, command docs created
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Attestation recorded
- [ ] **Code Quality:** Clean

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
