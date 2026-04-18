---
id: OBPI-0.0.3-04-test-fakes-separation
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 4
lane: Heavy
status: attested_completed
---

# OBPI-0.0.3-04-test-fakes-separation: Test Fakes & Separation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #4 - "OBPI-0.0.3-04: Test Fakes & Separation"

**Status:** Completed

## Objective

Create `tests/fakes/` directory with in-memory implementations of the four port Protocols (FileStore, ProcessRunner, LedgerStore, ConfigStore), and establish `tests/unit/`, `tests/integration/`, and `tests/policy/` directories for test separation.

## Lane

**Heavy** — Introduces new test infrastructure packages and establishes architectural test boundaries.

## Allowed Paths

- `tests/fakes/__init__.py` — Fakes package init, re-exports all fakes
- `tests/fakes/filesystem.py` — In-memory FileStore implementation
- `tests/fakes/process.py` — In-memory ProcessRunner (canned results)
- `tests/fakes/ledger.py` — In-memory LedgerStore (list-backed)
- `tests/fakes/config.py` — In-memory ConfigStore (dict-backed)
- `tests/unit/__init__.py` — Unit test package init
- `tests/integration/__init__.py` — Integration test package init
- `tests/policy/__init__.py` — Policy test package init
- `tests/test_fakes.py` — Tests verifying fakes satisfy Protocol contracts
- `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-04-test-fakes-separation.md` — This brief

## Denied Paths

- `src/gzkit/**` — No source changes (test infrastructure only)
- `tests/test_*.py` (existing) — Do not move or modify existing tests
- `tests/commands/**` (existing) — Do not move or modify existing command tests
- `docs/design/**` — ADR changes out of scope
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Each fake satisfies its corresponding Protocol via structural subtyping (duck typing) — no inheritance from the Protocol class
2. REQUIREMENT: `tests/fakes/` imports only from `gzkit.ports` and stdlib
3. REQUIREMENT: `InMemoryFileStore` stores content in a `dict[str, str]` keyed by path string
4. REQUIREMENT: `InMemoryProcessRunner` returns configurable canned `(exit_code, stdout, stderr)` tuples
5. REQUIREMENT: `InMemoryLedgerStore` uses a `list[dict]` as backing store
6. REQUIREMENT: `InMemoryConfigStore` uses a `dict` as backing store
7. REQUIREMENT: All existing tests in `tests/` and `tests/commands/` continue to pass unchanged
8. NEVER: Move existing test files — this OBPI creates new directories only
9. NEVER: Import from `cli/`, `commands/`, or `adapters/` in fakes
10. ALWAYS: Fakes are deterministic — no randomness, no I/O, no side effects

> STOP-on-BLOCKERS: if `src/gzkit/ports/interfaces.py` does not exist (OBPI-01), halt.

## Discovery Checklist

**Prerequisites (STOP if missing):**

- [ ] `src/gzkit/ports/interfaces.py` exists with four Protocol definitions (OBPI-01 completed)

**Context:**

- [ ] Parent ADR — Test directory structure and import rules
- [ ] `.claude/rules/tests.md` — Test policy (stdlib unittest, no pytest, DB isolation)

**Existing Code:**

- [ ] `tests/` — Current flat test layout
- [ ] `tests/commands/` — Current command test layout
- [ ] `src/gzkit/ports/interfaces.py` — Protocol signatures to implement

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests verify each fake satisfies its Protocol contract
- [x] All existing tests still pass
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [x] N/A — Test infrastructure, no CLI surface changes

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
python -c "from tests.fakes import InMemoryFileStore, InMemoryProcessRunner, InMemoryLedgerStore, InMemoryConfigStore; print('All fakes importable')"
uv run -m unittest tests.test_fakes -v
```

## Acceptance Criteria

- [x] REQ-0.0.3-04-01: `tests/fakes/filesystem.py` contains InMemoryFileStore satisfying FileStore Protocol
- [x] REQ-0.0.3-04-02: `tests/fakes/process.py` contains InMemoryProcessRunner satisfying ProcessRunner Protocol
- [x] REQ-0.0.3-04-03: `tests/fakes/ledger.py` contains InMemoryLedgerStore satisfying LedgerStore Protocol
- [x] REQ-0.0.3-04-04: `tests/fakes/config.py` contains InMemoryConfigStore satisfying ConfigStore Protocol
- [x] REQ-0.0.3-04-05: [doc] `tests/unit/`, `tests/integration/`, `tests/policy/` directories exist with `__init__.py`
- [x] REQ-0.0.3-04-06: Fakes import only from `gzkit.ports` and stdlib
- [x] REQ-0.0.3-04-07: [doc] All existing tests pass unchanged
- [x] REQ-0.0.3-04-08: Protocol conformance tests verify each fake

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief

### Gate 2 (TDD)

```text
Ran 1187 tests in 14.190s — OK
60 new Protocol conformance tests in tests/test_fakes.py
1127 existing tests unchanged
```

### Code Quality

```text
uv run gz lint — All checks passed
uv run gz typecheck — All checks passed
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict — Documentation built in 0.96 seconds
```

### Gate 4 (BDD)

```text
N/A — Test infrastructure only, no CLI surface changes
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" — 2026-03-23
```

### Value Narrative

Before this OBPI, tests could only verify behavior through real I/O or `mock.patch` on implementation internals, coupling tests to adapter details and making refactoring fragile. Now, four deterministic in-memory fakes satisfy the port Protocols via structural subtyping, enabling unit tests against domain logic without touching filesystem, processes, or configuration files.

### Key Proof

```bash
$ uv run -m unittest tests.test_fakes -v
test_write_then_read_round_trip ... ok
test_exists_returns_true_after_write ... ok
test_registered_response_is_returned ... ok
test_append_then_read_all_round_trip ... ok
test_save_then_load_round_trip ... ok
test_config_store_protocol_methods ... ok
test_file_store_protocol_methods ... ok
test_ledger_store_protocol_methods ... ok
test_process_runner_protocol_methods ... ok
... (60 tests total)
Ran 60 tests in 0.001s — OK

$ uv run python -c "from tests.fakes import InMemoryFileStore, InMemoryProcessRunner, InMemoryLedgerStore, InMemoryConfigStore; print('All fakes importable')"
All fakes importable
```

### Implementation Summary

- Files created: `tests/fakes/__init__.py`, `tests/fakes/filesystem.py`, `tests/fakes/process.py`, `tests/fakes/ledger.py`, `tests/fakes/config.py`, `tests/unit/__init__.py`, `tests/integration/__init__.py`, `tests/policy/__init__.py`, `tests/test_fakes.py`
- Tests added: 60 Protocol conformance tests across 6 test classes
- Date completed: 2026-03-23
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-23

---

**Brief Status:** Completed

**Date Completed:** 2026-03-23

**Evidence Hash:** -
