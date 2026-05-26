---
id: models
paths:
  - "src/**/*.py"
description: Pydantic data model policy
---

<!-- rule-version: 0.1.0 -->

# Data Model Policy (canonical)

> **Rule version:** `0.1.0` — initial shape conformance pass; renamed prohibited heading (OBPI-0.0.54-04).

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

## Pattern: Immutable Domain Model

```python
from pydantic import BaseModel, ConfigDict, Field

class WorldState(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    world_state_hash: str = Field(..., description="SHA-256 of stable content")
    contract_hash: str | None = Field(None, description="Contract fingerprint hash")
```

## Do Not

- stdlib `dataclass` for governance data
- Pydantic without `ConfigDict`
- `Optional`/`List` instead of `| None` and `list[]`

## Verify

- All models extend `BaseModel` (not `@dataclass`)
- All models have `model_config` with at least `extra="forbid"`
- Immutable snapshots use `frozen=True`
