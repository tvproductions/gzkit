---
id: OBPI-0.0.3-05-config-precedence-injection
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.3-05-config-precedence-injection: Config Precedence & Injection

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #5 - "OBPI-0.0.3-05: Config Precedence & Injection (ENV-Optional)"

**Status:** Draft

## Objective

Refactor `src/gzkit/config.py` to implement an ENV-optional precedence chain (defaults → config file → environment → CLI args), a single `load_config()` entry point, constructor injection for all consumers, and a Pydantic-based immutable config model satisfying the ConfigStore port Protocol.

## Lane

**Heavy** — Changes the configuration contract surface and introduces constructor injection pattern.

## Allowed Paths

- `src/gzkit/config.py` — Config model refactor (precedence chain, Pydantic model)
- `src/gzkit/adapters/config.py` — ConfigStore adapter implementation
- `src/gzkit/core/__init__.py` — Update if config types needed in core
- `tests/test_config.py` — Update existing config tests
- `tests/test_config_precedence.py` — New tests for precedence chain
- `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-05-config-precedence-injection.md` — This brief

## Denied Paths

- `src/gzkit/cli.py` — CLI wiring of config injection is incremental/future
- `src/gzkit/commands/**` — Command-level injection migration is incremental
- `src/gzkit/ports/interfaces.py` — Port definitions are OBPI-01 (already exists)
- `docs/design/**` — ADR changes out of scope
- New dependencies (beyond Pydantic, already in use)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Config precedence chain is: defaults → config file → environment → CLI args (later wins)
2. REQUIREMENT: Single `load_config()` function is the only entry point for config loading
3. REQUIREMENT: Config model uses Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")`
4. REQUIREMENT: The config adapter satisfies the `ConfigStore` port Protocol
5. REQUIREMENT: Services receive config via constructor injection — never read ENV directly
6. REQUIREMENT: Only `NO_COLOR`, `FORCE_COLOR`, and `TERM` are allowed ENV reads (presentation concerns)
7. NEVER: Read `os.environ` or `os.getenv()` outside the config loading layer (except allowlisted vars)
8. NEVER: Use mutable config state — config is frozen after load
9. ALWAYS: Config model fields use type hints (`str | None`, not `Optional[str]`)
10. ALWAYS: All existing config tests continue to pass

> STOP-on-BLOCKERS: if OBPI-0.0.3-01 skeleton is not complete, halt.

## Discovery Checklist

**Prerequisites (STOP if missing):**

- [ ] `src/gzkit/ports/interfaces.py` exists with ConfigStore Protocol (OBPI-01)
- [ ] `src/gzkit/adapters/__init__.py` exists (OBPI-01)

**Existing Code:**

- [ ] `src/gzkit/config.py` — Current config implementation
- [ ] `tests/test_config.py` — Current config tests
- [ ] Grep for `os.environ` and `os.getenv` across `src/gzkit/` to find scattered ENV reads

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests verify precedence chain (each layer overrides previous)
- [ ] Tests verify config immutability
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] N/A — Config is internal infrastructure, no CLI command surface change

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
python -c "from gzkit.config import load_config; c = load_config(); print(f'Config loaded: frozen={c.model_config.get(\"frozen\", False)}')"
uv run -m unittest tests.test_config_precedence -v
```

## Acceptance Criteria

- [ ] REQ-0.0.3-05-01: `load_config()` implements defaults → file → env → CLI precedence
- [ ] REQ-0.0.3-05-02: Config model uses `ConfigDict(frozen=True, extra="forbid")`
- [ ] REQ-0.0.3-05-03: Config adapter satisfies ConfigStore Protocol
- [ ] REQ-0.0.3-05-04: No `os.environ`/`os.getenv` outside config loader (except allowlist)
- [ ] REQ-0.0.3-05-05: Config model uses modern type hints (`str | None`)
- [ ] REQ-0.0.3-05-06: Existing config tests pass unchanged
- [ ] REQ-0.0.3-05-07: Precedence chain tests cover all four layers

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
N/A — Config infrastructure
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
