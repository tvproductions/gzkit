---
id: OBPI-0.0.3-09-policy-tests
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 9
lane: Heavy
status: in_progress
---

# OBPI-0.0.3-09-policy-tests: Policy Tests (Architectural Enforcement)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #9 - "OBPI-0.0.3-09: Policy Tests (Architectural Enforcement)"

**Status:** Completed

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

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

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

- [x] REQ-0.0.3-09-01: [doc] `test_import_boundaries.py` exists and verifies core/ import rules via AST scanning
- [x] REQ-0.0.3-09-02: [doc] `test_import_boundaries.py` verifies ports/ import rules via AST scanning
- [x] REQ-0.0.3-09-03: [doc] `test_env_usage.py` exists and detects `os.getenv`/`os.environ` outside allowlist
- [x] REQ-0.0.3-09-04: [doc] `test_naming_conventions.py` exists and verifies snake_case module naming
- [x] REQ-0.0.3-09-05: [doc] All policy tests discoverable via `uv run gz test`
- [x] REQ-0.0.3-09-06: [doc] Policy tests import zero modules from `src/gzkit/`

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

- [x] Intent and scope recorded in brief objective and requirements sections

### Gate 2 (TDD)

```text
$ uv run -m unittest discover -s tests/policy -v
Ran 22 tests in 0.128s — OK
(10 import boundary + 7 env usage + 5 naming convention tests)
```

### Code Quality

```text
$ uv run gz lint → All checks passed!
$ uv run gz typecheck → All checks passed!
$ uv run gz test → Ran 1306 tests — OK
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict → Documentation built in 0.93 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
3 features passed, 0 failed, 0 skipped
35 scenarios passed, 0 failed, 0 skipped
164 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Attestor: human (jeff)
Attestation: "attest completed"
Date: 2026-03-24
```

### Value Narrative

Before this OBPI, hexagonal architecture layer boundaries were enforced only by convention and code review. A developer could add `import rich` to a core module with no automated guard. Now, AST-scanning policy tests machine-verify import boundaries, env var discipline, and naming conventions on every test run.

### Key Proof

```bash
$ uv run -m unittest discover -s tests/policy -v
# 22 tests verify: core/ import boundaries, ports/ type-only imports,
# env var allowlist compliance, and snake_case naming — all via AST scanning
# with zero application code imports.
```

### Implementation Summary

- Files created/modified: tests/policy/test_import_boundaries.py, tests/policy/test_env_usage.py, tests/policy/test_naming_conventions.py
- Tests added: 22 (10 import boundary, 7 env usage, 5 naming convention)
- Date completed: 2026-03-24
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

## Human Attestation

- Attestor: `human:jeff`
- Attestation: attest completed
- Date: 2026-03-24

---

**Brief Status:** Completed

**Date Completed:** 2026-03-24

**Evidence Hash:** -
