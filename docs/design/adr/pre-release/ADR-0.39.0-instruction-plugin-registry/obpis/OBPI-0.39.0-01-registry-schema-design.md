---
id: OBPI-0.39.0-01-registry-schema-design
parent: ADR-0.39.0-instruction-plugin-registry
item: 1
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.39.0-01: Registry Schema Design

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/ADR-0.39.0-instruction-plugin-registry.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.39.0-01 — "Registry schema design — define the plugin manifest format with JSON Schema validation"`

## OBJECTIVE

Design the plugin manifest format for the instruction registry. The manifest must be JSON Schema-validated, support versioning, declare dependencies between instruction sets, and clearly distinguish canonical instructions from project extensions. The schema must be strict enough to prevent malformed registrations but flexible enough to support diverse instruction types (rules, policies, conventions, toolchain guidance).

## SOURCE MATERIAL

- **Inspiration:** Python entry_points, VS Code extension manifests, Terraform provider schemas
- **gzkit patterns:** `.gzkit/manifest.json` (existing manifest format), `data/schemas/` (existing JSON Schemas)
- **Current instructions:** `.claude/rules/*.md` — the instruction files that will be registered

## ASSUMPTIONS

- The manifest must be machine-parseable (JSON) and human-readable
- Each instruction plugin declares: id, version, type (canonical/extension), scope (path globs), dependencies
- The schema must support both single-file instructions and multi-file instruction sets
- Versioning must use semantic versioning for compatibility checking
- The schema must be extensible for future instruction types without breaking existing manifests

## NON-GOALS

- Implementing the registry runtime — only the schema/manifest format
- Building the validation engine — that is OBPI-0.39.0-04
- Designing the UI/CLI for manifest editing — declarative JSON only

## REQUIREMENTS (FAIL-CLOSED)

1. Design the JSON Schema for the instruction plugin manifest
1. Define required fields: id, version, type, scope, description
1. Define optional fields: dependencies, conflicts, metadata, author
1. Write the JSON Schema in `data/schemas/instruction_plugin.schema.json`
1. Create a Pydantic BaseModel mirroring the schema for runtime validation
1. Write unit tests validating both valid and invalid manifests against the schema
1. Document the schema with field-by-field descriptions and examples

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.39.0-01-01: Design the JSON Schema for the instruction plugin manifest
- [x] REQ-0.39.0-01-02: Define required fields: id, version, type, scope, description
- [x] REQ-0.39.0-01-03: Define optional fields: dependencies, conflicts, metadata, author
- [x] REQ-0.39.0-01-04: Write the JSON Schema in `data/schemas/instruction_plugin.schema.json`
- [x] REQ-0.39.0-01-05: Create a Pydantic BaseModel mirroring the schema for runtime validation
- [x] REQ-0.39.0-01-06: Write unit tests validating both valid and invalid manifests against the schema
- [x] REQ-0.39.0-01-07: Document the schema with field-by-field descriptions and examples


## ALLOWED PATHS

- `src/gzkit/instructions/` — new module package
- `data/schemas/` — JSON Schema files
- `tests/` — unit tests
- `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Schema documented with examples
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
