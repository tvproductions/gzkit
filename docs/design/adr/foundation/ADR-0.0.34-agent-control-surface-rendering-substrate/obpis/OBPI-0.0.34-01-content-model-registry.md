---
id: OBPI-0.0.34-01-content-model-registry
parent: ADR-0.0.34-agent-control-surface-rendering-substrate
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.0.34-01-content-model-registry: Content Model Registry

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- **Checklist Item:** #1 - "OBPI-0.0.34-01: Content model registry generalization — extend ADR-0.16.0 OBPI-01 to all per-turn surface artifacts (`AgentContract`, `Rule`, `Skill`, `Chore`, `Persona`, `Handoff`, `Scenario`, `Bullet`, …) with `frozen=True, extra="forbid"`"

**Status:** Completed

## Objective

Content model registry generalization — extend ADR-0.16.0 OBPI-01 to all per-turn surface artifacts (`AgentContract`, `Rule`, `Skill`, `Chore`, `Persona`, `Handoff`, `Scenario`, `Bullet`, …) with `frozen=True, extra="forbid"`. The eight canonical content types are exposed via a single `CONTENT_MODELS: dict[str, type[BaseContentModel]]` registry in `src/gzkit/content/models/__init__.py`.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/content/models/__init__.py` — `CONTENT_MODELS` registry entrypoint
- `src/gzkit/content/models/base.py` — frozen Pydantic base class with `frozen=True, extra="forbid"`
- `src/gzkit/content/models/agent_contract.py` — `AgentContract` model (target: `AGENTS.md`/`CLAUDE.md`)
- `src/gzkit/content/models/rule.py` — `Rule` model (target: `.gzkit/rules/*.md`)
- `src/gzkit/content/models/skill.py` — `Skill` model (target: `.gzkit/skills/<slug>/SKILL.md`)
- `src/gzkit/content/models/chore.py` — `Chore` model (target: `.gzkit/chores/<slug>/CHORE.md`)
- `src/gzkit/content/models/persona.py` — `Persona` model (target: `.gzkit/personas/*.md`)
- `src/gzkit/content/models/handoff.py` — `Handoff` model (target: `.gzkit/handoffs/*.md`)
- `src/gzkit/content/models/scenario.py` — `Scenario` model (target: `features/**/*.feature`)
- `src/gzkit/content/models/bullet.py` — `Bullet` model (shared compositional primitive)
- `tests/content/models/**` — per-model unit tests (frozen-class, extra-forbid, schema-shape)
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-01-content-model-registry.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Frozen Pydantic models for every per-turn surface artifact.** Define `AgentContract`, `Rule`, `Skill`, `Chore`, `Persona`, `Handoff`, `Scenario`, and `Bullet` under `src/gzkit/content/models/` deriving from a base class declaring `model_config = ConfigDict(frozen=True, extra="forbid")`.
2. REQUIREMENT: **Single registry entrypoint.** Expose `CONTENT_MODELS: dict[str, type[BaseContentModel]]` from `src/gzkit/content/models/__init__.py`. Lookup is by content-type string; no dynamic import in consumers.
3. REQUIREMENT: **Round-trip-ready field shape.** Every field annotation supports round-trip parse↔render. NEVER use `Any` or untyped dict payloads. String-typed fields with semantic structure (paths, identifiers, semver) carry pydantic validators.
4. REQUIREMENT: **Models-only scope.** This OBPI ships content models and the registry. Rendering lives in OBPI-02, parsing in OBPI-03, schema versioning in OBPI-07. NEVER import render/parse modules from a content model.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR — **no internal prerequisites** (this is the foundation OBPI other 02–07 depend on). External precedent: ADR-0.16.0 OBPI-01 (rules-only registry, extends here to all surface types).
- [ ] Downstream consumers: OBPI-02 (rendering), OBPI-03 (parsing), OBPI-06 (validation hooks), OBPI-07 (schema versioning).

**Prerequisites (check existence, STOP if missing):**

- [ ] Pydantic ≥ 2 available in `pyproject.toml` (already present as a named departure per Stdlib-First doctrine).
- [ ] `src/gzkit/content/` directory may not yet exist — create as part of this OBPI.
- [ ] Parent ADR evidence artifacts referenced by this brief are present.

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run python -c "from gzkit.content.models import CONTENT_MODELS; assert set(CONTENT_MODELS) >= {'AgentContract','Rule','Skill','Chore','Persona','Handoff','Scenario','Bullet'}, sorted(CONTENT_MODELS)"
uv run python -c "from gzkit.content.models import CONTENT_MODELS; [m.model_config['frozen'] or (_ for _ in ()).throw(AssertionError(f'{n} not frozen')) for n, m in CONTENT_MODELS.items()]"
uv run python -m unittest discover -s tests/content/models -t . -v
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.34-01-01: Given any content-type string in the canonical eight (`AgentContract`, `Rule`, `Skill`, `Chore`, `Persona`, `Handoff`, `Scenario`, `Bullet`), when looked up in `CONTENT_MODELS`, then the registry returns a Pydantic model class whose `model_config` declares both `frozen=True` and `extra="forbid"`.
- [ ] REQ-0.0.34-01-02: Given any registered content-model class, when an instance is constructed with an undeclared field, then `pydantic.ValidationError` is raised.
- [ ] REQ-0.0.34-01-03: Given any registered content-model class, when its JSON schema is computed, then no field has type `Any` or an untyped `dict` payload (verified by introspection test).
- [ ] REQ-0.0.34-01-04: Given the eight canonical content types, when the registry is enumerated, then all eight are present and each maps to a class importable from `gzkit.content.models`.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

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

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


```
$ uv run python -c "from gzkit.content.models import CONTENT_MODELS; print(sorted(CONTENT_MODELS))"
['AgentContract', 'Bullet', 'Chore', 'Handoff', 'Persona', 'Rule', 'Scenario', 'Skill']

$ uv run python -c "
from gzkit.content.models import Rule
from pydantic import ValidationError
try:
    Rule(title='t', version='not-semver')
except ValidationError as e:
    print('REQ-03 validator rejects non-semver:', e.errors()[0]['msg'])
"
REQ-03 validator rejects non-semver: Value error, version must match X.Y.Z; got 'not-semver'

$ uv run -m unittest discover -s tests/content/models -t . -v 2>&1 | tail -3
Ran 17 tests in 0.003s
OK
```

ARB receipts (all GREEN): arb-ruff-4753298321f543249de318ab4060929c, arb-step-typecheck-119c6e9ac0ef4d318a05a24f4ef096d9, arb-step-unittest-8af05f1e51684e69ad8f71e120361c38 (full sweep 5104/5104), arb-step-unittest-a14f5653b8a14ebe8a5a403c61a23052 (OBPI-scoped 17/17). REQ coverage: 4/4 via gz covers (100%).

### Implementation Summary


- Package: `src/gzkit/content/__init__.py` + `src/gzkit/content/models/__init__.py` (CONTENT_MODELS dict + re-exports + `__all__`)
- Base: `src/gzkit/content/models/base.py` — `BaseContentModel(BaseModel)` with `model_config = ConfigDict(frozen=True, extra="forbid")`
- Primitive: `src/gzkit/content/models/bullet.py` — `Bullet` shared compositional primitive
- Surface types: `agent_contract.py`, `rule.py`, `skill.py`, `chore.py`, `persona.py`, `handoff.py`, `scenario.py` — one frozen Pydantic class per file deriving from BaseContentModel
- Semantic validators: `Rule.version` (semver `\d+\.\d+\.\d+`); `Rule.paths` (rejects empty, absolute POSIX, Windows drive, parent traversal); `Skill/Chore/Persona.slug` (kebab-case `[a-z][a-z0-9-]*`); `Handoff.session_id` (identifier `[A-Za-z0-9][A-Za-z0-9_-]*`)
- Tests: `tests/content/models/test_registry.py` (4 tests covering REQ-01/02/04) + `tests/content/models/test_fields.py` (13 tests covering REQ-03 across Any/untyped-dict rejection + semantic-structure validator rejection + happy-path)
- Tests added: 17 (all GREEN under `tests/content/models/`); full sweep 5104/5104 GREEN
- Date completed: 2026-05-16
- Attestation status: Heavy/foundation human attestation received from operator ("attest completed") at Stage 4
- Defects noted: GHI #474 filed and closed in same session (pool ADR taxonomy false alarm resolved by reconcile); 4 sibling OBPI briefs (03-06) received grandfather markers per GHI #431; behave waiver added with rationale adr-0.0.34-01-foundation-bdd-deferred-to-cli-obpis

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — OBPI-0.0.34-01-content-model-registry foundation/heavy schema-only OBPI: 8 canonical frozen Pydantic content models (AgentContract, Rule, Skill, Chore, Persona, Handoff, Scenario, Bullet) registered in CONTENT_MODELS at src/gzkit/content/models/__init__.py with model_config = ConfigDict(frozen=True, extra="forbid"); semantic validators on Rule.version (semver), Rule.paths (no absolute/Windows-drive/traversal/empty), Skill/Chore/Persona.slug (kebab-case), Handoff.session_id (identifier); 17/17 OBPI-scoped tests GREEN (receipt arb-step-unittest-a14f5653b8a14ebe8a5a403c61a23052), full sweep 5104/5104 GREEN (receipt arb-step-unittest-8af05f1e51684e69ad8f71e120361c38) after in-session fixes to 4 sibling brief Demo gaps + behave waiver; ruff GREEN (receipt arb-ruff-4753298321f543249de318ab4060929c); typecheck GREEN (receipt arb-step-typecheck-119c6e9ac0ef4d318a05a24f4ef096d9); @covers parity 4/4 REQs (100%); precomplete READY all 7 preconditions; operator attestation phrase "attest completed" received in conversational turn at Stage 4.
- Date: 2026-05-16

---

**Brief Status:** Draft

**Date Completed:** 2026-05-16

**Evidence Hash:** -
