---
id: OBPI-0.0.3-04-test-fakes-separation
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.3-04-test-fakes-separation: Test Fakes & Separation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #4 - "OBPI-0.0.3-04: Test Fakes & Separation"

**Status:** Draft

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

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests verify each fake satisfies its Protocol contract
- [ ] All existing tests still pass
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] N/A — Test infrastructure, no CLI surface changes

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] REQ-0.0.3-04-01: `tests/fakes/filesystem.py` contains InMemoryFileStore satisfying FileStore Protocol
- [ ] REQ-0.0.3-04-02: `tests/fakes/process.py` contains InMemoryProcessRunner satisfying ProcessRunner Protocol
- [ ] REQ-0.0.3-04-03: `tests/fakes/ledger.py` contains InMemoryLedgerStore satisfying LedgerStore Protocol
- [ ] REQ-0.0.3-04-04: `tests/fakes/config.py` contains InMemoryConfigStore satisfying ConfigStore Protocol
- [ ] REQ-0.0.3-04-05: `tests/unit/`, `tests/integration/`, `tests/policy/` directories exist with `__init__.py`
- [ ] REQ-0.0.3-04-06: Fakes import only from `gzkit.ports` and stdlib
- [ ] REQ-0.0.3-04-07: All existing tests pass unchanged
- [ ] REQ-0.0.3-04-08: Protocol conformance tests verify each fake

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

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
N/A — Test infrastructure only
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:<name>` — required (parent ADR is Heavy, Foundation series)
- Attestation: substantive attestation text required
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
