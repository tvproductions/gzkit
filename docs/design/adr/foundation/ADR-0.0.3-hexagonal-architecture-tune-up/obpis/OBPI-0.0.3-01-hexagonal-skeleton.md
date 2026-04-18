---
id: OBPI-0.0.3-01-hexagonal-skeleton
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 1
lane: Heavy
status: in_progress
---

# OBPI-0.0.3-01-hexagonal-skeleton: Hexagonal Skeleton

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #1 - "OBPI-0.0.3-01: Hexagonal Skeleton"

**Status:** Completed

## Objective

Create the three-layer directory skeleton (`src/gzkit/ports/`, `src/gzkit/core/`, `src/gzkit/adapters/`) with `__init__.py` files and define the four port Protocol interfaces (FileStore, ProcessRunner, LedgerStore, ConfigStore) in `src/gzkit/ports/interfaces.py`.

## Lane

**Heavy** — Creates new package structure and public Protocol interfaces that all subsequent OBPIs depend on.

## Allowed Paths

- `src/gzkit/ports/__init__.py` — New package init
- `src/gzkit/ports/interfaces.py` — Four Protocol definitions
- `src/gzkit/core/__init__.py` — New package init (empty, structure only)
- `src/gzkit/adapters/__init__.py` — New package init (empty, structure only)
- `tests/test_ports.py` — Protocol interface tests
- `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-01-hexagonal-skeleton.md` — This brief

## Denied Paths

- `src/gzkit/cli.py` — Existing CLI (not this OBPI)
- `src/gzkit/commands/**` — Existing commands (not this OBPI)
- `src/gzkit/config.py` — Config refactor is OBPI-05
- `src/gzkit/ledger.py` — Adapter extraction is OBPI-02
- `src/gzkit/lifecycle.py` — Domain extraction is OBPI-02
- `src/gzkit/validate.py` — Domain extraction is OBPI-02
- `src/gzkit/decomposition.py` — Domain extraction is OBPI-02
- `src/gzkit/core/models.py` — Domain extraction is OBPI-02
- `src/gzkit/core/exceptions.py` — Exception hierarchy is OBPI-03
- `tests/fakes/` — Test fakes are OBPI-04
- `docs/design/**` — ADR changes out of scope
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `src/gzkit/ports/interfaces.py` defines exactly four Protocol classes: FileStore, ProcessRunner, LedgerStore, ConfigStore
2. REQUIREMENT: All four Protocols use `typing.Protocol` for structural subtyping — adapters satisfy them implicitly via duck typing
3. REQUIREMENT: `ports/` imports only `typing` and stdlib type annotations (`pathlib.Path`)
4. REQUIREMENT: Each Protocol method has a type-annotated signature matching the ADR specification
5. REQUIREMENT: `src/gzkit/core/__init__.py` and `src/gzkit/adapters/__init__.py` are created but empty (structure only)
6. REQUIREMENT: `src/gzkit/ports/__init__.py` re-exports all four Protocol classes
7. NEVER: Import from `cli/`, `commands/`, `adapters/`, `rich`, `argparse`, or any external library in `ports/`
8. NEVER: Add concrete implementations in `ports/` — protocols only
9. NEVER: Modify any existing module — this OBPI creates new files only
10. ALWAYS: All new files pass `uv run gz lint` and `uv run gz typecheck`

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` — Agent operating contract
- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`

**Context:**

- [ ] ADR Port Interfaces section — exact Protocol signatures
- [ ] ADR Layer Import Rules section — boundary constraints
- [ ] ADR Target Project Structure section — directory layout

**Existing Code (understand current state):**

- [ ] `src/gzkit/ledger.py` — Current ledger I/O patterns (informs LedgerStore Protocol)
- [ ] `src/gzkit/config.py` — Current config I/O patterns (informs ConfigStore Protocol)
- [ ] `src/gzkit/lifecycle.py` — Current file I/O patterns (informs FileStore Protocol)
- [ ] `src/gzkit/quality.py` — Current subprocess patterns (informs ProcessRunner Protocol)

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written for Protocol interface contracts
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] N/A — No CLI/API surface changes in this OBPI

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
python -c "from gzkit.ports import FileStore, ProcessRunner, LedgerStore, ConfigStore; print('All protocols importable')"
uv run -m unittest tests.test_ports -v
```

## Acceptance Criteria

- [x] REQ-0.0.3-01-01: `src/gzkit/ports/interfaces.py` exists and defines FileStore Protocol
- [x] REQ-0.0.3-01-02: `src/gzkit/ports/interfaces.py` defines ProcessRunner Protocol
- [x] REQ-0.0.3-01-03: `src/gzkit/ports/interfaces.py` defines LedgerStore Protocol
- [x] REQ-0.0.3-01-04: `src/gzkit/ports/interfaces.py` defines ConfigStore Protocol
- [x] REQ-0.0.3-01-05: `src/gzkit/ports/__init__.py` re-exports all four Protocols
- [x] REQ-0.0.3-01-06: `src/gzkit/core/__init__.py` exists (empty, structural)
- [x] REQ-0.0.3-01-07: `src/gzkit/adapters/__init__.py` exists (empty, structural)
- [x] REQ-0.0.3-01-08: `ports/` imports only `typing` and `pathlib` — no external dependencies
- [x] REQ-0.0.3-01-09: [doc] All files pass lint and type check
- [x] REQ-0.0.3-01-10: Unit tests verify Protocol definitions are importable and structurally correct

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
$ uv run -m unittest tests.test_ports -v
Ran 19 tests in 0.001s — OK
Tests cover: Protocol imports, method signatures, boundary constraints, directory structure
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — All checks passed
$ uv run gz test — 1079 tests pass
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict — Documentation built successfully
```

### Gate 4 (BDD)

```text
N/A — No CLI surface changes
```

### Gate 5 (Human)

```text
Attestor: human (operator)
Attestation: "attest completed"
Date: 2026-03-23
```

### Value Narrative

Before this OBPI, gzkit had a flat module layout with no architectural boundaries — domain
logic, I/O, and CLI concerns were mixed freely across modules. Now, three-layer hexagonal
skeleton exists (ports/, core/, adapters/) with four Protocol interfaces that define I/O
boundaries via structural subtyping, enabling subsequent OBPIs to extract domain logic and
create test fakes.

### Key Proof

```text
$ uv run python -c "from gzkit.ports import FileStore, ProcessRunner, LedgerStore, ConfigStore; print('All protocols importable')"
All protocols importable

$ uv run -m unittest tests.test_ports -v
test_filestore_importable ... ok
test_processrunner_importable ... ok
test_ledgerstore_importable ... ok
test_configstore_importable ... ok
test_has_read_text ... ok
test_has_write_text ... ok
test_has_exists ... ok
test_has_iterdir ... ok
test_has_run ... ok
test_has_append ... ok
test_has_read_all ... ok
test_has_load ... ok
test_has_save ... ok
test_ports_interfaces_imports_only_stdlib ... ok
test_ports_init_imports_only_from_ports ... ok
test_adapters_init_exists ... ok
test_core_init_exists ... ok
test_ports_init_exists ... ok
test_ports_interfaces_exists ... ok
Ran 19 tests in 0.001s — OK
```

### Implementation Summary

- Files created/modified: src/gzkit/ports/__init__.py, src/gzkit/ports/interfaces.py, src/gzkit/core/__init__.py, src/gzkit/adapters/__init__.py, tests/test_ports.py
- Tests added: tests/test_ports.py (19 tests)
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
