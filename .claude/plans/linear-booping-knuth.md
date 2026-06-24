# Plan: OBPI-0.0.74-15 — `@enforces` Declaration and Registry

**OBPI:** `OBPI-0.0.74-15-enforces-declaration-and-registry`
**Parent ADR:** `ADR-0.0.74-mx-mode-maintenance-hangar`
**Lane:** Heavy
**Item 15 (verbatim):** "The `@enforces(claim, fixture, entrypoint)` declaration + import-time registry — fail-closed at decoration on a typo / unknown claim (mirrors the `@covers` / `@advances` precedent in `src/gzkit/traceability.py`); registration metadata-only. (OBPI-15)"

## Context

The enforcement-claim meta-validator (§5 of ADR-0.0.74) needs a single claim-type-agnostic primitive for declaring "this claim is enforced by this violation-builder and this production callable." Today, qc_binding's NCs are authored ad-hoc in `_qc_negative_controls.py`; gate5 invariants and structural-fence REQs have no equivalent declaration surface. This OBPI ships the primitive — `@enforces` + `EnforcementClaimRecord` + import-time registry — that every enforcement claim routes through. Land order: 15 → 16 → 17+18 → 19.

## Precedent — Mirror exactly, don't invent

- `@covers` in `src/gzkit/traceability.py:201` — format check via `ReqId.parse()`, existence check via `_load_known_reqs()`, `set_known_reqs()` for test injection
- `@advances` in `src/gzkit/tasks.py:434` — format check via `TaskId.parse()`, existence check via `_load_known_task_reqs()`, `set_known_task_reqs()` for test injection
- `TaskAttributionRecord` in `src/gzkit/tasks.py:366` — `ConfigDict(frozen=True, extra="forbid")`, only string/int fields

## Files Created

- `src/gzkit/enforcement.py` — NEW: all implementation
- `tests/governance/test_enforces_registry.py` — NEW: all tests

(Allowed Paths only; no other files touched.)

## Design

### `EnforcementClaimRecord` (Pydantic model)

```python
class EnforcementClaimRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid", arbitrary_types_allowed=True)

    claim_id: str
    fixture: Callable[[], Any]     # violation-builder; runner (OBPI-16) calls fixture()
    entrypoint: Callable[..., Any] # production callable; runner calls entrypoint(fixture())
    source_fn: str                 # qualified name of entrypoint (for discovery/logging)
    source_file: str | None = None
    source_line: int | None = None
```

`arbitrary_types_allowed=True` is required because callables are not natively serializable Pydantic types. `frozen=True` makes fields immutable post-construction; the model need not be hashable (it lives in a `list`, not a `set`).

### Module-level registry and known-claims

```python
_ENFORCEMENT_REGISTRY: list[EnforcementClaimRecord] = []
_KNOWN_CLAIMS: frozenset[str] | None = None          # lazy-cached
_CLAIM_ID_RE = re.compile(r"^[a-z][a-z0-9-]*$")     # slug: lowercase, hyphens, no spaces
```

**Known-claims source:** `_PRODUCTION_NEGATIVE_CONTROLS.keys()` from
`gzkit.governance.trust_audits._qc_negative_controls` — lazy-loaded, no circular import
(that module imports only from `gzkit.core.validation_rules` and `gzkit.quality`).
Tests inject via `set_known_claims(frozenset(...))`.

### `@enforces(claim, fixture, entrypoint)` decorator

```python
def enforces(
    claim: str,
    fixture: Callable[[], Any],
    entrypoint: Callable[..., Any],
) -> Callable[[_EF], _EF]:
    # 1. Format check
    if not _CLAIM_ID_RE.match(claim):
        raise ValueError(f"Malformed claim id: {claim!r} — must match {_CLAIM_ID_RE.pattern!r}")
    # 2. Known-claims check
    known = _load_known_claims()
    if claim not in known:
        raise ValueError(f"Unknown claim: {claim!r} not in the registered known-claims set")
    # 3. Register
    def decorator(fn: _EF) -> _EF:
        ...record = EnforcementClaimRecord(claim_id=claim, fixture=fixture, entrypoint=entrypoint,
                                           source_fn=_qualified_fn_name(entrypoint), ...)
        _ENFORCEMENT_REGISTRY.append(record)
        return fn   # unchanged — metadata-only
    return decorator
```

**Note:** `@enforces` is used like `@covers`/`@advances` — it decorates the entrypoint in source, not the test. The test for REQ-15-03 will verify the decorated callable's return value is unchanged.

### Accessors

```python
def registered_claims() -> list[str]:          # REQ-15-01
    return [r.claim_id for r in _ENFORCEMENT_REGISTRY]

def get_enforcement_registry() -> list[EnforcementClaimRecord]:
    return list(_ENFORCEMENT_REGISTRY)

def reset_enforcement_registry() -> None:      # test teardown
    _ENFORCEMENT_REGISTRY.clear()

def set_known_claims(claims: frozenset[str]) -> None:   # test injection
    global _KNOWN_CLAIMS
    _KNOWN_CLAIMS = claims
```

## Implementation Steps (TDD, req_atomic — single implementation pass)

All four REQs are authored together (the brief carries `req_atomic:` for all four — each is one coherent increment inside a single new module):

**Step A — TDD RED:** Write `tests/governance/test_enforces_registry.py` for all four REQs. Tests must fail before any implementation exists.

**Step B — TDD GREEN:** Create `src/gzkit/enforcement.py` implementing `EnforcementClaimRecord`, `_ENFORCEMENT_REGISTRY`, `_load_known_claims()`, `set_known_claims()`, `@enforces`, `registered_claims()`, `get_enforcement_registry()`, `reset_enforcement_registry()`. All tests pass.

**Step C — Lint + typecheck:** `uv run ruff check . --fix && uv run ruff format .` + `uv run ty check .`

## Test Structure (REQ coverage)

| Test class | REQ | Mechanism |
|---|---|---|
| `TestEnforcesRegistration` | REQ-15-01 | `@enforces` records a `EnforcementClaimRecord`; `registered_claims()` returns it |
| `TestEnforcesFailClose` | REQ-15-02 | malformed slug → `ValueError`; unknown claim → `ValueError`; valid form + known claim → no error |
| `TestEnforcesMetadataOnly` | REQ-15-03 | decorated entrypoint returns original value unchanged; no kwargs pre-bound |
| `TestEnforcesStructuralFence` | REQ-15-04 | assert no `_PRODUCTION_NEGATIVE_CONTROLS`-style registry in `enforcement.py` (import check); assert `_ENFORCEMENT_REGISTRY` is the single surface |

Each test class decorated with `@covers("REQ-0.0.74-15-NN")` on the relevant methods.

## Quality Gates (Heavy Lane)

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_enforces_registry -v
uv run gz arb step --name unittest -- uv run -m unittest -q   # full suite
uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.74-15-enforces-declaration-and-registry --json  # parity gate
```

## Notes / Seam-pins (BI#7)

- `entrypoint` stored in record as the ORIGINAL callable — no `functools.partial`, no `lambda` pre-binding
- Tests assert entrypoint is `fn is original_fn` (identity check, not equality)
- `fixture` and `entrypoint` are stored as-is; the runner (OBPI-16) is the only invoker
