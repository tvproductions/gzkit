---
id: OBPI-0.21.0-03-gz-covers-cli
parent: ADR-0.21.0-tests-for-spec
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.21.0-03: gz covers CLI

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.21.0-tests-for-spec/ADR-0.21.0-tests-for-spec.md`
- **Checklist Item:** #3 — "`gz covers` CLI with ADR/OBPI/REQ granularity and human/JSON/plain output"

**Status:** Completed

## Objective

Expose requirement coverage reporting via `gz covers` CLI. Operators can query coverage at three levels: all (`gz covers`), by ADR (`gz covers ADR-0.20.0`), or by OBPI (`gz covers OBPI-0.20.0-01`).

## Lane

**Heavy** — New CLI command (external contract). Requires docs, BDD, and human attestation.

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

- [x] REQ-0.21.0-03-01: Given `gz covers`, then shows coverage table with ADR-level rollup.
- [x] REQ-0.21.0-03-02: Given `gz covers ADR-0.20.0`, then shows only REQs under that ADR.
- [x] REQ-0.21.0-03-03: Given `gz covers --json`, then outputs valid JSON coverage report.
- [x] REQ-0.21.0-03-04: Given `gz covers --help`, then shows description, usage, options, example.

## Verification Commands (Concrete)

```bash
uv run gz covers --help
# Expected: description, usage, options, and example are present

uv run gz covers ADR-0.20.0 --json
# Expected: valid JSON coverage report for ADR-0.20.0 only

uv run gz covers OBPI-0.20.0-01 --plain
# Expected: one record per line for the target OBPI

uv run -m unittest tests.test_traceability -v
# Expected: CLI smoke tests pass for human/JSON/plain modes

uv run -m behave features/test_traceability.feature
# Expected: covers CLI BDD scenarios pass

uv run mkdocs build --strict
# Expected: command docs render cleanly

uv run gz lint
uv run gz typecheck
# Expected: CLI surface remains lint/type clean
```

## Completion Checklist (Heavy)

- [x] **Gate 1 (ADR):** Intent recorded
- [x] **Gate 2 (TDD):** Tests pass (49/49)
- [x] **Gate 3 (Docs):** Docs build, command docs created
- [x] **Gate 4 (BDD):** Acceptance scenarios pass (5/5)
- [x] **Gate 5 (Human):** Attestation recorded
- [x] **Code Quality:** Clean (lint, typecheck, 96% coverage)

---

### Implementation Summary

- Command: `gz covers [TARGET] [--json|--plain]` reports REQ coverage from `@covers` annotations
- Filtering: `_filter_report()` scopes results to a single ADR or OBPI by REQ-ID prefix matching
- Output: human tables via Rich console, JSON via `CoverageReport.model_dump_json()`, plain tab-delimited
- Registration: argparse subcommand in `cli/main.py`, manifest entry in `doc-coverage.json`
- Tests: 16 new CLI smoke tests in `tests/test_traceability.py`, 5 BDD scenarios
- Docs: `docs/user/commands/covers.md` manpage, mkdocs nav entry

### Key Proof

```bash
uv run gz covers --help
# Shows description, usage, options, examples
uv run gz covers --json
# Valid JSON CoverageReport with by_adr, by_obpi, entries, summary
uv run -m behave features/test_traceability.feature
# 5/5 scenarios pass
```

**Brief Status:** Completed

**Date Completed:** 2026-03-27

**Evidence Hash:** -
