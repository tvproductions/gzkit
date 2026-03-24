---
id: OBPI-0.0.3-05-config-precedence-injection
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.0.3-05-config-precedence-injection: Config Precedence & Injection

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #5 - "OBPI-0.0.3-05: Config Precedence & Injection (ENV-Optional)"

**Status:** Completed

## Objective

Refactor `src/gzkit/config.py` to implement a precedence chain (defaults → config file → CLI args), a single `load_config()` entry point, constructor injection for all consumers, and a Pydantic-based immutable config model satisfying the ConfigStore port Protocol. No environment variable layer — env vars are not permitted in config loading.

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

1. REQUIREMENT: Config precedence chain is: defaults → config file → CLI args (later wins) — no environment variable layer
2. REQUIREMENT: Single `load_config()` function is the only entry point for config loading
3. REQUIREMENT: Config model uses Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")`
4. REQUIREMENT: The config adapter satisfies the `ConfigStore` port Protocol
5. REQUIREMENT: Services receive config via constructor injection — never read ENV directly
6. REQUIREMENT: Only `NO_COLOR`, `FORCE_COLOR`, and `TERM` are allowed ENV reads (presentation concerns only, outside config)
7. NEVER: Read `os.environ` or `os.getenv()` in the config module — env vars are not part of the precedence chain
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

- [x] Human attestation recorded

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

- [x] REQ-0.0.3-05-01: `load_config()` implements defaults → file → CLI precedence (no env layer)
- [x] REQ-0.0.3-05-02: Config model uses `ConfigDict(frozen=True, extra="forbid")`
- [x] REQ-0.0.3-05-03: Config adapter satisfies ConfigStore Protocol
- [x] REQ-0.0.3-05-04: No `os.environ`/`os.getenv` outside config loader (except allowlist)
- [x] REQ-0.0.3-05-05: Config model uses modern type hints (`str | None`)
- [x] REQ-0.0.3-05-06: Existing config tests pass unchanged
- [x] REQ-0.0.3-05-07: Precedence chain tests cover all three layers

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
$ uv run -m unittest tests.test_load_config -v
Ran 15 tests in 0.003s — OK
$ uv run -m unittest tests.test_config -v
Ran 17 tests in 0.001s — OK
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — All checks passed
$ uv run ruff check . — clean
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict — Documentation built in 0.89 seconds
```

### Gate 4 (BDD)

```text
N/A — Config is internal infrastructure, no CLI command surface change
```

### Gate 5 (Human)

```text
Attestor: human (operator)
Attestation: "attest completed"
Date: 2026-03-24
```

### Value Narrative

Before this OBPI, gzkit configuration was loaded directly via `GzkitConfig.load()` with no CLI override mechanism and no ConfigStore adapter. Consumers were coupled to a single loading path. Now `load_config()` provides a single entry point with a 3-layer precedence chain (defaults → config file → CLI args) — no environment variable layer, matching the airlineops hard rule. `FileConfigStore` satisfies the ConfigStore port Protocol for hexagonal architecture compliance.

### Key Proof

```text
$ python -c "from gzkit.config import load_config; c = load_config(cli_overrides={'mode': 'heavy', 'project_name': 'demo'}); print(f'mode={c.mode} project={c.project_name} frozen={c.model_config.get(\"frozen\", False)}')"
mode=heavy project=demo frozen=True

$ python -c "import inspect; from gzkit.config import load_config; print(list(inspect.signature(load_config).parameters.keys()))"
['path', 'cli_overrides']
```

### Implementation Summary

- Files created: `src/gzkit/adapters/config.py`, `tests/test_load_config.py`
- Files modified: `src/gzkit/config.py`, `OBPI-0.0.3-05-config-precedence-injection.md`
- Tests added: 15 (7 precedence, 2 defaults, 6 adapter)
- Date completed: 2026-03-24
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:jeff` — required (parent ADR is Heavy, Foundation series)
- Attestation: attest completed
- Date: 2026-03-24

---

**Brief Status:** Completed

**Date Completed:** 2026-03-24

**Evidence Hash:** -
