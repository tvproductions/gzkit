---
id: OBPI-0.0.43-01-prd-section-schema-scaffolder
parent: ADR-0.0.43-ddd-domain-cascade
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.43-01-prd-section-schema-scaffolder: PRD strategic schema + scaffolder + Pydantic foundation

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`
- **Checklist Item:** #1 — "PRD § 2.1 / 2.2 / 2.3 schema + scaffolder + Pydantic — `UbiquitousLanguageTerm`, `BoundedContextDeclaration`, `ContextMapEntry` models; `gz prd` scaffolder appends three sections; `src/gzkit/templates/prd.md` updated; `src/gzkit/schemas/{glossary_term,bounded_context,context_map_entry}.json`."

**Status:** Draft

## Objective

Land the foundational Pydantic surface for the cascade's strategic layer (`UbiquitousLanguageTerm`, `BoundedContextDeclaration`, `ContextMapEntry`), the corresponding JSON Schemas, and extend the `gz prd` scaffolder so every new PRD ships with `## 2.1 Ubiquitous Language`, `## 2.2 Bounded Contexts`, `## 2.3 Context Map` sections in canonical form. This OBPI is the foundation every subsequent cascade OBPI imports from; no behavior beyond the strategic schema layer ships here.

## Lane

**Heavy** — introduces new Pydantic models in the public governance surface (`src/gzkit/governance/domain_models.py`), three new JSON Schema files in `src/gzkit/schemas/`, and a CLI scaffolder contract change (`gz prd <slug>` now emits three additional sections). External-contract changes per AGENTS.md § Lane Rules.

## Allowed Paths

- `src/gzkit/governance/domain_models.py` — NEW module; this OBPI seeds it with `UbiquitousLanguageTerm`, `BoundedContextDeclaration`, `ContextMapEntry`, and the `RelationType` enum (Evans-7 + Vernon Partnership + Big-Ball-of-Mud)
- `src/gzkit/schemas/glossary_term.json` — NEW; validates `UbiquitousLanguageTerm`
- `src/gzkit/schemas/bounded_context.json` — NEW; validates `BoundedContextDeclaration`
- `src/gzkit/schemas/context_map_entry.json` — NEW; validates `ContextMapEntry`
- `src/gzkit/templates/prd.md` — EXTEND; insert `## 2.1`, `## 2.2`, `## 2.3` section skeletons after `## 2. Overview`
- `src/gzkit/cli/prd.py` — EXTEND; scaffolder honors new template; no flag changes
- `tests/governance/domain/test_strategic_models.py` — NEW
- `tests/governance/domain/test_strategic_schemas.py` — NEW
- `tests/cli/test_prd_scaffolds_domain_sections.py` — NEW

## Denied Paths

- `src/gzkit/governance/domain_models.py::DomainModel,Aggregate,Entity,ValueObject,DomainEvent,ImplementationSurface,InboundContract,OutboundContract` — DM tactical surface is OBPI-02 scope (this OBPI MAY introduce the file; OBPI-02 extends it)
- `src/gzkit/schemas/domain_model.json` — OBPI-02 scope
- `src/gzkit/schemas/legacy_mapping.json` — OBPI-07 scope
- `src/gzkit/schemas/adr.json` / `ghi.json` / `obpi.json` — OBPI-04 frontmatter cascade keys
- `src/gzkit/cli/domain.py` and `src/gzkit/domain/**` — OBPI-03 CLI scope
- `src/gzkit/governance/trust_audits/domain_cascade.py` — OBPI-06 validator scope
- `src/gzkit/ledger/**` — OBPI-05 ledger event scope
- `docs/design/prd/PRD-GZKIT-1.0.0.md` content — OBPI-13 first-cascade-authoring scope (this OBPI may NOT populate the existing PRD with content)
- `.gzkit/skills/**` — OBPI-08 / 09 / 10 skill scopes
- `docs/user/**` and `docs/governance/**` — OBPI-12 documentation scope
- Runtime dependencies, lockfiles, CI configuration

## Requirements (FAIL-CLOSED)

1. **REQUIREMENT (`UbiquitousLanguageTerm` model).** Pydantic class with `term: str` (non-empty, slugifiable), `scope: Literal["cross-cutting"] | str` (BC slug when not cross-cutting), `definition: str` (≥10 characters), `provenance: list[str]` (ADR IDs, may be empty). `extra="forbid"`. Slugified form of `term` (lowercase, hyphenated) MUST be exposed as `slug` property — the validator constructs the `gz-glossary-<slug>` marker from this property.
2. **REQUIREMENT (`BoundedContextDeclaration` model).** Pydantic class with `slug: str` (kebab-case, validates against `^[a-z][a-z0-9-]*$`), `purpose: str` (≥10 characters), `owner_persona: str` (must match a registered persona under `.gzkit/personas/`), `lifecycle_state: Literal["active", "deprecated", "retired"]`, `dm_ref: str | None` (DM artifact id when DM exists), `introduced_in: str` (PRD or ADR id). `extra="forbid"`.
3. **REQUIREMENT (`ContextMapEntry` model + `RelationType` enum).** Pydantic class with `from_: str` (BC slug, aliased from `from` per Python keyword conflict), `to: str` (BC slug), `type: RelationType`, `description: str` (≥10 words — word count enforced, not character count). `RelationType` enum is exhaustive: `shared-kernel`, `customer-supplier`, `conformist`, `anticorruption-layer`, `separate-ways`, `open-host-service`, `published-language`, `partnership`, `big-ball-of-mud`. `extra="forbid"`.
4. **REQUIREMENT (JSON Schema files).** Three schemas under `src/gzkit/schemas/`: `glossary_term.json`, `bounded_context.json`, `context_map_entry.json`. Each MUST validate the corresponding Pydantic model's serialized form. Schema files MUST declare `"additionalProperties": false` to mirror Pydantic's `extra="forbid"`. The schemas are the canonical contract surface for non-Python consumers (validators, ledger events, future tooling).
5. **REQUIREMENT (PRD template scaffold).** `src/gzkit/templates/prd.md` MUST insert three new sections after `## 2. Overview`:
    - `## 2.1 Ubiquitous Language` — placeholder list with one example term entry (commented out, operator-fills)
    - `## 2.2 Bounded Contexts` — placeholder list with one example BC entry
    - `## 2.3 Context Map` — placeholder list with one example context-map entry
   Template sections MUST carry HTML-comment authoring hints naming the schema each list conforms to.
6. **REQUIREMENT (scaffolder regression).** Existing PRDs (e.g., `PRD-GZKIT-1.0.0.md`) MUST NOT be touched by this OBPI's scaffolder run. The scaffolder only emits new sections when authoring a fresh PRD via `gz prd <slug>`. OBPI-13 handles the in-place amendment of the existing PRD as a separate concern.
7. **REQUIREMENT (no downstream coupling).** Nothing in this OBPI's scope may presuppose OBPI-02's DM artifact, OBPI-03's `gz domain` CLI, OBPI-06's cascade validator, or OBPI-07's legacy mapping. The strategic schemas must be standalone-usable and standalone-testable.

> STOP-on-BLOCKERS: if existing PRD schema (`src/gzkit/schemas/prd.json`) has section ordering that conflicts with inserting `## 2.1 / 2.2 / 2.3` after `## 2. Overview`, halt and surface; do not silently renumber prior sections.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into Implementation Summary
- [ ] Parent ADR § Intent — the why-frame
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/ADR-0.0.43-ddd-domain-cascade.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read.

**Governance:**

- [ ] `AGENTS.md` § Lane Rules and § Behavior Rules
- [ ] `.gzkit/rules/governance-core.md` — invariant order
- [ ] `.gzkit/rules/models.md` — Pydantic-as-named-departure doctrine
- [ ] `docs/governance/state-doctrine.md` — Layer 1 canon discipline

**Context:**

- [ ] Existing schema authoring conventions in `src/gzkit/schemas/`
- [ ] Existing Pydantic surface in `src/gzkit/governance/`
- [ ] Existing PRD template at `src/gzkit/templates/prd.md`
- [ ] Persona registry at `.gzkit/personas/` (for `owner_persona` validation)

**Prerequisites:**

- [ ] Parent ADR exists at `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/`
- [ ] `src/gzkit/schemas/` directory exists and contains existing schemas (parity authoring)
- [ ] `src/gzkit/templates/prd.md` exists

**Existing Code:**

- [ ] `src/gzkit/schemas/prd.json` reviewed for section-ordering interaction
- [ ] `src/gzkit/cli/prd.py` reviewed for scaffolder integration point
- [ ] Existing Pydantic `extra="forbid"` patterns reviewed for consistency

## Quality Gates

### Gate 1: ADR

- [ ] Parent ADR checklist item #1 quoted in Implementation Summary
- [ ] Intent and scope recorded in this brief

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Model validation tests cover (a) valid input (b) missing required field (c) extra field rejected (d) enum out-of-range rejected (e) word-count enforcement on `description`
- [ ] Schema validation tests cover the same scenarios via JSON Schema
- [ ] Scaffolder integration test: `gz prd test-prd --dry-run` produces output containing `## 2.1`, `## 2.2`, `## 2.3` section headers
- [ ] Existing PRD untouched: integration test asserts `docs/design/prd/PRD-GZKIT-1.0.0.md` byte-equal before/after `gz prd <other-slug>` invocation
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build clean: `uv run mkdocs build --strict`
- [ ] No new operator-facing manpages required (CLI surface unchanged; OBPI-12 handles cascade doctrine docs)

### Gate 4: BDD (Heavy only)

- [ ] No new behave scenarios required (no operator workflow change; OBPI-13 handles the operator-facing first-cascade-authoring scenario)

### Gate 5: Human (Heavy + Foundation)

- [ ] Human attestation recorded (foundation kind + heavy lane forces attestation per AGENTS.md OBPI Acceptance Protocol matrix)

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/governance/domain_models.py
test -f src/gzkit/schemas/glossary_term.json
test -f src/gzkit/schemas/bounded_context.json
test -f src/gzkit/schemas/context_map_entry.json
uv run python -c "from gzkit.governance.domain_models import UbiquitousLanguageTerm, BoundedContextDeclaration, ContextMapEntry, RelationType; print('imports OK')"
uv run -m unittest tests.governance.domain.test_strategic_models -v
uv run -m unittest tests.governance.domain.test_strategic_schemas -v
uv run -m unittest tests.cli.test_prd_scaffolds_domain_sections -v
grep -q '^## 2.1 Ubiquitous Language' src/gzkit/templates/prd.md
grep -q '^## 2.2 Bounded Contexts' src/gzkit/templates/prd.md
grep -q '^## 2.3 Context Map' src/gzkit/templates/prd.md
```

## Demo

```bash
# Scaffold a fresh PRD and confirm the three new strategic sections land
uv run gz prd demo-ddd-cascade --title "Demo: DDD Cascade Sections"
grep -A 3 '^## 2.1 Ubiquitous Language' docs/design/prd/PRD-DEMO-DDD-CASCADE-*.md
grep -A 3 '^## 2.2 Bounded Contexts' docs/design/prd/PRD-DEMO-DDD-CASCADE-*.md
grep -A 3 '^## 2.3 Context Map' docs/design/prd/PRD-DEMO-DDD-CASCADE-*.md

# Round-trip a strategic model through Pydantic and the schema
uv run python -c "
from gzkit.governance.domain_models import BoundedContextDeclaration
bc = BoundedContextDeclaration(slug='experimentation', purpose='A/B test design and statistical analysis.', owner_persona='main-session', lifecycle_state='active', dm_ref='DM-experimentation', introduced_in='PRD-GZKIT-1.0.0')
print(bc.model_dump_json(indent=2))
"

# Cleanup demo artifact
rm docs/design/prd/PRD-DEMO-DDD-CASCADE-*.md
```

## Acceptance Criteria

- [ ] REQ-0.0.43-01-01: Given `UbiquitousLanguageTerm` is imported, when constructed with valid fields, then the model serializes/deserializes round-trip and the `slug` property produces the expected hyphenated form (`change` → `change`; `customer event` → `customer-event`)
- [ ] REQ-0.0.43-01-02: Given `UbiquitousLanguageTerm` is imported, when constructed with `definition` shorter than 10 characters, then a `ValidationError` is raised
- [ ] REQ-0.0.43-01-03: Given `BoundedContextDeclaration` is imported, when constructed with a `slug` violating `^[a-z][a-z0-9-]*$`, then a `ValidationError` is raised
- [ ] REQ-0.0.43-01-04: Given `BoundedContextDeclaration` is imported, when `owner_persona` does not match any file under `.gzkit/personas/`, then a `ValidationError` is raised
- [ ] REQ-0.0.43-01-05: Given `ContextMapEntry` is imported, when constructed with `type` outside the `RelationType` enum, then a `ValidationError` is raised
- [ ] REQ-0.0.43-01-06: Given `ContextMapEntry` is imported, when `description` contains fewer than 10 whitespace-separated words, then a `ValidationError` is raised
- [ ] REQ-0.0.43-01-07: Given any of the three strategic models is constructed with an unknown keyword, then `extra="forbid"` raises a `ValidationError`
- [ ] REQ-0.0.43-01-08: Given `src/gzkit/schemas/glossary_term.json`, `bounded_context.json`, `context_map_entry.json`, when validated against a generated instance via `jsonschema`, then validation passes; and when validated against an instance with an unknown field, then validation fails
- [ ] REQ-0.0.43-01-09: Given a fresh PRD scaffold via `gz prd <slug>`, when the output is inspected, then `## 2.1 Ubiquitous Language`, `## 2.2 Bounded Contexts`, `## 2.3 Context Map` appear in order after `## 2. Overview`
- [ ] REQ-0.0.43-01-10: Given an existing PRD at `docs/design/prd/PRD-GZKIT-1.0.0.md`, when `gz prd <other-slug>` is invoked, then the existing PRD is byte-equal before/after invocation

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** mkdocs build --strict clean
- [ ] **Gate 5 (Human):** Attestation recorded (foundation kind + heavy lane)
- [ ] **Value Narrative:** Problem-before vs capability-now documented
- [ ] **Key Proof:** One concrete usage example included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
# N/A — no new operator-facing scenarios in this OBPI
```

### Gate 5 (Human)

```text
# Record attestation text here
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

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
