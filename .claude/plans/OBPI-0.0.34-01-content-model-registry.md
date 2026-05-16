# Plan: OBPI-0.0.34-01-content-model-registry

## Context

OBPI-0.0.34-01 implements the content model registry for gzkit's agent control
surface rendering substrate. The brief requires eight frozen Pydantic models
(AgentContract, Rule, Skill, Chore, Persona, Handoff, Scenario, Bullet) and a
`CONTENT_MODELS` registry dict exposed from `src/gzkit/content/models/__init__.py`.

Parent ADR Decision item #1:
> Content model registry generalization — extend ADR-0.16.0 OBPI-01 to all
> per-turn surface artifacts (AgentContract, Rule, Skill, Chore, Persona,
> Handoff, Scenario, Bullet, …) with frozen=True, extra="forbid"

Pydantic ≥ 2 is already declared in pyproject.toml.
`src/gzkit/content/` does not yet exist — this OBPI creates it.

## Files

- `src/gzkit/content/__init__.py` — package marker
- `src/gzkit/content/models/__init__.py` — `CONTENT_MODELS` registry + re-exports
- `src/gzkit/content/models/base.py` — `BaseContentModel` with `frozen=True, extra="forbid"`
- `src/gzkit/content/models/agent_contract.py` — `AgentContract` model
- `src/gzkit/content/models/rule.py` — `Rule` model
- `src/gzkit/content/models/skill.py` — `Skill` model
- `src/gzkit/content/models/chore.py` — `Chore` model
- `src/gzkit/content/models/persona.py` — `Persona` model
- `src/gzkit/content/models/handoff.py` — `Handoff` model
- `src/gzkit/content/models/scenario.py` — `Scenario` model
- `src/gzkit/content/models/bullet.py` — `Bullet` model
- `tests/__init__.py` — may need content sub-package
- `tests/content/__init__.py` — new test sub-package
- `tests/content/models/__init__.py` — new test module
- `tests/content/models/test_registry.py` — REQ-01, REQ-02, REQ-04
- `tests/content/models/test_base.py` — REQ-01, REQ-02
- `tests/content/models/test_fields.py` — REQ-03 (no Any, round-trip-ready)

## Steps

### Step 1: TDD — Write failing tests for all four REQs

Write tests under `tests/content/models/` that cover:
- REQ-0.0.34-01-01: All 8 content types in CONTENT_MODELS have `frozen=True` and `extra="forbid"` in model_config
- REQ-0.0.34-01-02: Extra-field construction raises `ValidationError` for each model
- REQ-0.0.34-01-03: JSON schema for each model contains no `Any` or untyped dict
- REQ-0.0.34-01-04: CONTENT_MODELS keys exactly equal the canonical 8 content-type strings; each value is importable from `gzkit.content.models`

Use `unittest.TestCase`. Add `@covers("REQ-0.0.34-01-NN")` decorators from `gzkit.core` (or inline docstring form if decorator is unavailable — check existing test pattern first).

Run: `uv run -m unittest discover -s tests/content/models -t . -v` — expect failures (RED).

### Step 2: Create package skeleton

Create:
- `src/gzkit/content/__init__.py` (empty package marker)
- `src/gzkit/content/models/__init__.py` (stub: `CONTENT_MODELS = {}`)
- `src/gzkit/content/models/base.py` (`BaseContentModel` with `model_config = ConfigDict(frozen=True, extra="forbid")`)

Run tests — still failing on content type checks (partial GREEN).

### Step 3: Implement BaseContentModel and Bullet

Create `src/gzkit/content/models/base.py`:
```python
from pydantic import BaseModel, ConfigDict

class BaseContentModel(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
```

Create `src/gzkit/content/models/bullet.py` — `Bullet` is the shared compositional primitive:
```python
class Bullet(BaseContentModel):
    text: str  # The bullet text
    indent: int = 0  # Nesting level (0 = top-level)
```

### Step 4: Implement the six surface-type models

Implement one file per type. Each derives from `BaseContentModel`. Fields must:
- Use concrete types (str, int, bool, list[str], list[Bullet], etc.) — no `Any`
- Use semantic validators for structured strings (paths, identifiers, semver)
- Support round-trip parse↔render (no computed fields with side effects)

Model field shapes (minimal, round-trip-ready):

**AgentContract** (target: AGENTS.md/CLAUDE.md):
- `name: str` — project/agent name
- `purpose: str` — one-sentence purpose
- `tech_stack: list[str]` — technology identifiers
- `rules: list[Bullet]` — behavioral rules as bullets

**Rule** (target: .gzkit/rules/*.md):
- `title: str`
- `version: str` — semver string; validator: must match `\d+\.\d+\.\d+`
- `paths: list[str]` — glob patterns scoping the rule
- `body: list[Bullet]`

**Skill** (target: .gzkit/skills/<slug>/SKILL.md):
- `slug: str` — kebab-case identifier; validator: must match `[a-z][a-z0-9-]*`
- `title: str`
- `purpose: str`
- `steps: list[Bullet]`

**Chore** (target: .gzkit/chores/<slug>/CHORE.md):
- `slug: str` — kebab-case identifier
- `title: str`
- `cadence: str` — e.g. "monthly", "weekly", "on-demand"
- `steps: list[Bullet]`

**Persona** (target: .gzkit/personas/*.md):
- `slug: str` — kebab-case identifier
- `role: str`
- `traits: list[str]`

**Handoff** (target: .gzkit/handoffs/*.md):
- `session_id: str`
- `state_summary: str`
- `open_items: list[Bullet]`
- `resume_point: str`

**Scenario** (target: features/**/*.feature):
- `feature: str` — feature title
- `scenario: str` — scenario name
- `given: list[str]`
- `when: list[str]`
- `then: list[str]`

### Step 5: Populate CONTENT_MODELS registry

Update `src/gzkit/content/models/__init__.py`:
```python
from .base import BaseContentModel
from .agent_contract import AgentContract
from .rule import Rule
from .skill import Skill
from .chore import Chore
from .persona import Persona
from .handoff import Handoff
from .scenario import Scenario
from .bullet import Bullet

CONTENT_MODELS: dict[str, type[BaseContentModel]] = {
    "AgentContract": AgentContract,
    "Rule": Rule,
    "Skill": Skill,
    "Chore": Chore,
    "Persona": Persona,
    "Handoff": Handoff,
    "Scenario": Scenario,
    "Bullet": Bullet,
}

__all__ = [
    "CONTENT_MODELS",
    "BaseContentModel",
    "AgentContract",
    "Rule",
    "Skill",
    "Chore",
    "Persona",
    "Handoff",
    "Scenario",
    "Bullet",
]
```

### Step 6: Run tests to GREEN

Run `uv run -m unittest discover -s tests/content/models -t . -v` — expect all passing.
Run `uv run gz arb ruff` and `uv run gz arb typecheck` — fix any issues.

### Step 7: Run @covers parity gate

Run `uv run gz covers OBPI-0.0.34-01-content-model-registry --json` and confirm
`uncovered_reqs == 0`. Add `@covers` decorators where missing.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q

uv run python -c "from gzkit.content.models import CONTENT_MODELS; assert set(CONTENT_MODELS) >= {'AgentContract','Rule','Skill','Chore','Persona','Handoff','Scenario','Bullet'}, sorted(CONTENT_MODELS)"
uv run python -c "from gzkit.content.models import CONTENT_MODELS; [m.model_config['frozen'] or (_ for _ in ()).throw(AssertionError(f'{n} not frozen')) for n, m in CONTENT_MODELS.items()]"
uv run -m unittest discover -s tests/content/models -t . -v
```

## Notes

- Destination-in-mind: BaseContentModel base → per-type files → CONTENT_MODELS dict
- Rejected: single flat models.py; auto-scan registry; Any-typed fields; render imports in models
- OBPI-02 (rendering) is the downstream consumer — no render imports here
- `src/gzkit/content/` directory does not exist; create from scratch
- Use `covers` decorator pattern from existing tests (check `tests/` for `@covers` usage first)
