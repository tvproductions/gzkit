---
id: OBPI-0.0.3-09-policy-tests
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 9
lane: Heavy
status: Draft
---

# OBPI-0.0.3-09-policy-tests: Policy Tests (Architectural Enforcement)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #9 - "OBPI-0.0.3-09: Policy Tests (Architectural Enforcement)"

**Status:** Draft

## Objective

AST-scanning tests in `tests/policy/` that enforce import boundaries, ENV usage restrictions, and naming conventions — ensuring hexagonal layer rules are machine-verified, not just prose.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `tests/policy/` - Policy test files (AST scanners)
- `tests/policy/__init__.py` - Package init
- `tests/policy/test_import_boundaries.py` - Import boundary enforcement
- `tests/policy/test_env_usage.py` - ENV usage enforcement
- `tests/policy/test_naming_conventions.py` - Naming convention enforcement

## Denied Paths

- `src/gzkit/**` - No source changes (policy tests scan, don't modify)
- `docs/design/**` - ADR changes out of scope
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Policy tests use `ast` module to scan source — they NEVER import or execute application code
2. REQUIREMENT: Import boundary test verifies `core/` does not import from `cli/`, `adapters/`, `rich`, `argparse`
3. REQUIREMENT: Import boundary test verifies `ports/` imports only `typing` and stdlib type annotations
4. REQUIREMENT: ENV usage test scans for `os.getenv()` / `os.environ.get()` outside allowlist (`NO_COLOR`, `FORCE_COLOR`, `TERM`)
5. ALWAYS: Policy tests run on every `uv run gz test` invocation and CI run
6. NEVER: Policy tests import from `src/gzkit/` — they scan files, not execute them

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- [ ] Design spec: `docs/superpowers/specs/2026-03-15-hexagonal-architecture-tuneup-design.md` § Design Decision #7 (Policy Tests)
- [ ] Related OBPIs: OBPI-0.0.3-01 (skeleton creates `tests/policy/` directory)

**Prerequisites (check existence, STOP if missing):**

- [ ] `tests/policy/__init__.py` exists (created in OBPI-0.0.3-01)
- [ ] `src/gzkit/core/` directory exists (created in OBPI-0.0.3-01)
- [ ] `src/gzkit/ports/` directory exists (created in OBPI-0.0.3-01)

**Existing Code (understand current state):**

- [ ] Pattern to follow: existing `tests/` test structure
- [ ] Python `ast` module documentation for Import/ImportFrom node visitors

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run -m unittest discover -s tests/policy -v
```

## Acceptance Criteria

- [ ] REQ-0.0.3-09-01: `test_import_boundaries.py` exists and verifies core/ import rules via AST scanning
- [ ] REQ-0.0.3-09-02: `test_import_boundaries.py` verifies ports/ import rules via AST scanning
- [ ] REQ-0.0.3-09-03: `test_env_usage.py` exists and detects `os.getenv`/`os.environ` outside allowlist
- [ ] REQ-0.0.3-09-04: `test_naming_conventions.py` exists and verifies snake_case module naming
- [ ] REQ-0.0.3-09-05: All policy tests discoverable via `uv run gz test`
- [ ] REQ-0.0.3-09-06: Policy tests import zero modules from `src/gzkit/`

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

## Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

## Key Proof

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

## Human Attestation

- Attestor: `human:<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
