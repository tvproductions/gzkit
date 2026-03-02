---
applyTo: "src/**/*.py"
---

# Data Model Policy (canonical)

- Use **Pydantic `BaseModel`** for all data models; no stdlib `dataclasses`.
- Use `ConfigDict(frozen=True, extra="forbid")` for immutable models.
- Use `Field(...)` with descriptions for required fields; `Field(None, ...)` for optional.
- Use type hints (`str | None`, `list[str]`) — not `Optional`, `List`.

## Why Pydantic Over Dataclasses

| Feature | Pydantic | dataclasses |
|---------|----------|-------------|
| Validation | Built-in, declarative | Manual |
| Serialization | `.model_dump()`, `.model_dump_json()` | Manual |
| Immutability | `frozen=True` with clear errors | `frozen=True` with cryptic errors |
| Extra fields | `extra="forbid"` rejects typos | Silent ignore or manual check |
| Defaults | `Field(default_factory=...)` | `field(default_factory=...)` |
| Error messages | Structured, actionable | AttributeError |

## Pattern: Immutable Domain Model

```python
from pydantic import BaseModel, ConfigDict, Field

class WorldState(BaseModel):
    """Immutable snapshot with content-addressable identity."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    world_state_hash: str = Field(..., description="SHA-256 of stable content")
    contract_hash: str | None = Field(None, description="Contract fingerprint hash")
    computed_at: str = Field(default_factory=_utc_now_iso, description="ISO 8601 timestamp")
```

## Pattern: Warehouse Manifest (Existing Example)

```python
from pydantic import BaseModel, ConfigDict, Field

class Manifest(BaseModel):
    """Warehouse fulfillment record for a single dataset."""

    model_config = ConfigDict(extra="forbid")

    dataset_id: str = Field(..., description="Dataset key (e.g., db1b)")
    contract_hash: str = Field(..., description="Hash of generating contract")
    periods: list[str] = Field(default_factory=list, description="Covered periods")
    status: str = Field("unknown", description="Fulfillment status")
```

## When to Use `frozen=True`

| Use Case | Frozen? | Rationale |
|----------|---------|-----------|
| Snapshots (WorldState, ContractFingerprint) | Yes | Content-addressable identity |
| Registrar entries | Yes | Immutable once registered |
| Manifest (warehouse record) | No | Updated during fulfillment |
| Configuration (loaded once) | Yes | Prevent accidental mutation |

## Anti-Patterns (DO NOT USE)

```python
# ❌ WRONG: stdlib dataclass
from dataclasses import dataclass

@dataclass(frozen=True)
class WorldState:
    world_state_hash: str
    contract_hash: str | None = None

# ❌ WRONG: Pydantic without ConfigDict
class WorldState(BaseModel):
    world_state_hash: str  # No Field(), no description

# ❌ WRONG: Optional/List instead of | and list[]
from typing import Optional, List
contract_hash: Optional[str]  # Use: str | None
periods: List[str]            # Use: list[str]
```

## Validation

```python
# Pydantic validates on construction
state = WorldState(world_state_hash="abc123")  # OK
state = WorldState()  # ValidationError: world_state_hash required

# frozen=True prevents mutation
state.world_state_hash = "new"  # ValidationError: instance is frozen

# extra="forbid" catches typos
state = WorldState(world_state_hash="abc", typo_field="x")  # ValidationError
```

## Existing Pydantic Models (Reference)

| Module | Model | Frozen? |
|--------|-------|---------|
| `warehouse.manifest` | `Manifest`, `PackageSpec` | No |
| `core.world_state` | `WorldState` | Yes |
| `config.schema` | Settings models | No |

## Run

- `uv run ruff check . --fix && uv run ruff format .`
- `uv run -m unittest -v`

## Verify

- All models extend `BaseModel` (not `@dataclass`)
- All models have `model_config` with at least `extra="forbid"`
- Immutable snapshots use `frozen=True`
