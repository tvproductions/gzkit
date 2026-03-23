---
id: OBPI-0.0.3-01-hexagonal-skeleton
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.3-01-hexagonal-skeleton: Hexagonal Skeleton

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #1 - "OBPI-0.0.3-01: Hexagonal Skeleton"

**Status:** Draft

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

- [ ] REQ-0.0.3-01-01: `src/gzkit/ports/interfaces.py` exists and defines FileStore Protocol
- [ ] REQ-0.0.3-01-02: `src/gzkit/ports/interfaces.py` defines ProcessRunner Protocol
- [ ] REQ-0.0.3-01-03: `src/gzkit/ports/interfaces.py` defines LedgerStore Protocol
- [ ] REQ-0.0.3-01-04: `src/gzkit/ports/interfaces.py` defines ConfigStore Protocol
- [ ] REQ-0.0.3-01-05: `src/gzkit/ports/__init__.py` re-exports all four Protocols
- [ ] REQ-0.0.3-01-06: `src/gzkit/core/__init__.py` exists (empty, structural)
- [ ] REQ-0.0.3-01-07: `src/gzkit/adapters/__init__.py` exists (empty, structural)
- [ ] REQ-0.0.3-01-08: `ports/` imports only `typing` and `pathlib` — no external dependencies
- [ ] REQ-0.0.3-01-09: All files pass lint and type check
- [ ] REQ-0.0.3-01-10: Unit tests verify Protocol definitions are importable and structurally correct

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
N/A — No CLI surface changes
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
