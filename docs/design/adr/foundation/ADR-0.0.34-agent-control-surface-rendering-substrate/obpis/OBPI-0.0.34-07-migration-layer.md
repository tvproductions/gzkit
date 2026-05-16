---
id: OBPI-0.0.34-07-migration-layer
parent: ADR-0.0.34-agent-control-surface-rendering-substrate
item: 7
lane: Heavy
status: Draft
---

# OBPI-0.0.34-07-migration-layer: Migration Layer

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- **Checklist Item:** #7 - "OBPI-0.0.34-07: Migration layer — Pydantic schema versioning so model refactors do not break rendered-output stability across releases"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Migration layer — Pydantic schema versioning so model refactors do not break rendered-output stability across releases.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/content/migration/__init__.py` — migration registry public entrypoint
- `src/gzkit/content/migration/registry.py` — `(content_type, from_version, to_version) → migration_callable` map and dispatcher
- `src/gzkit/content/models/base.py` — add `schema_version: int = 1` field on the content-model base class
- `src/gzkit/content/parse/markdown_parser.py` — invoke migration registry on parse when source `schema_version` differs from current
- `tests/content/test_migration_layer.py` — schema version detection, sequential migration application, unknown-version fail-closed
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-07-migration-layer.md` — this brief

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **`schema_version: int` on every content-model base.** Every model under `src/gzkit/content/models/` derives from a base that declares `schema_version: int = 1` at the class level; this field is rendered into the canonical-form output and parsed back on import.
2. REQUIREMENT: **Migration registry.** `src/gzkit/content/migration/registry.py` contains `MIGRATIONS: dict[tuple[str, int, int], Callable[[Model], Model]]` mapping `(content_type, from_version, to_version)` to a pure migration function. Each migration is total: it accepts a valid v_n model and returns a valid v_{n+1} model.
3. REQUIREMENT: **Auto-migration on parse.** OBPI-03's parser detects `schema_version` mismatch between source and current and applies registered migrations in sequence before instantiating the current model. NEVER silently drop fields; NEVER guess a migration when none is registered.
4. REQUIREMENT: **Rendered-output stability across version bumps.** Until a migration explicitly changes a model's rendered shape, re-rendering after the version bump produces byte-identical output. Verified by a fixture set of rendered files compared pre- and post-migration registration.

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

- [ ] **Prerequisite OBPI:** OBPI-0.0.34-01 (content model registry) — `schema_version` field is added to the registry's base class.
- [ ] **Prerequisite OBPI:** OBPI-0.0.34-03 (reverse-parse migration) — parser is the call-site for auto-migration; modification (not creation) of `markdown_parser.py`.
- [ ] **Soft co-dependency:** OBPI-0.0.34-02 (rendering pipeline) — renderer must include `schema_version` in canonical output. May land in either order.
- [ ] Should land last in the sequence — once OBPIs 01-06 stabilize, OBPI-07 is the schema-evolution backstop ensuring future model changes don't break rendered-output stability.

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI-0.0.34-01 complete: `from gzkit.content.models import CONTENT_MODELS` imports cleanly.
- [ ] OBPI-0.0.34-03 complete: `gz content import --help` exits 0.
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
uv run python -c "from gzkit.content.models import CONTENT_MODELS; assert all(getattr(m, 'schema_version', None) == 1 for m in CONTENT_MODELS.values()), {n: getattr(m, 'schema_version', None) for n, m in CONTENT_MODELS.items()}"
uv run python -c "from gzkit.content.migration import MIGRATIONS; assert isinstance(MIGRATIONS, dict)"
uv run python -m unittest tests.content.test_migration_layer -v
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.34-07-01: Given every model in the OBPI-01 registry, when `model.schema_version` is read on a freshly constructed instance, then it returns an integer ≥ 1 (default 1 at initial release).
- [ ] REQ-0.0.34-07-02: Given a test-fixture canonical file declaring an older `schema_version`, when `gz content import` parses it, then the appropriate registered migrations apply in sequence (1 → 2 → 3) and the produced model carries the current `schema_version`.
- [ ] REQ-0.0.34-07-03: Given a fixture set of rendered files at the current schema version, when no migrations are registered between current and a hypothetical next version, then re-rendering after introducing the migration registry produces byte-identical output (stability invariant).
- [ ] REQ-0.0.34-07-04: Given an unknown source `schema_version` (e.g. `schema_version: 999`), when parsing runs, then exit code is non-zero and the diagnostic names the unsupported version; NEVER guess or fall through to current.
- [ ] REQ-0.0.34-07-05: Given a registered migration callable, when called twice on the same input, then the output is equal (purity invariant — migrations are deterministic and side-effect-free).

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

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
