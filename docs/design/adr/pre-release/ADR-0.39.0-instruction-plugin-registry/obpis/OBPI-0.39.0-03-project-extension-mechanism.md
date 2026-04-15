---
id: OBPI-0.39.0-03-project-extension-mechanism
parent: ADR-0.39.0-instruction-plugin-registry
item: 3
status: Pending
lane: heavy
date: 2026-03-21
---

# OBPI-0.39.0-03: Project Extension Mechanism

## ADR ITEM — Level 1 WBS Reference

- Source ADR: `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/ADR-0.39.0-instruction-plugin-registry.md`
- OBPI Entry (Level 1 WBS): `OBPI-0.39.0-03 — "Project extension mechanism — how projects register domain-specific specializations"`

## OBJECTIVE

Design and implement the mechanism by which downstream projects register domain-specific instruction extensions. Extensions must be explicitly registered through the plugin manifest — no ad-hoc instruction files are permitted. The mechanism must support three extension types: additions (new instructions for domains gzkit does not cover), specializations (narrowing a canonical instruction for a specific domain), and supplements (adding domain-specific guidance to a canonical instruction without contradicting it).

## SOURCE MATERIAL

- **Registry schema:** Output of OBPI-0.39.0-01 (plugin manifest format)
- **Canonical set:** Output of OBPI-0.39.0-02 (canonical instruction catalog)
- **Inspiration:** Python namespace packages, Django app configs, Terraform module registries

## ASSUMPTIONS

- Projects must explicitly opt-in to extensions — silence means canonical-only
- The three extension types (addition, specialization, supplement) cover all legitimate use cases
- Extensions must declare which canonical instruction they extend (for specializations/supplements)
- Additions must declare their scope (path globs) and must not overlap with canonical scopes without explicit registration
- The extension mechanism must work without network access (local-only)

## NON-GOALS

- Implementing conformance validation — that is OBPI-0.39.0-04
- Implementing contradiction detection — that is OBPI-0.39.0-05
- Building a remote extension marketplace or distribution network
- Supporting runtime instruction composition (instructions are static files)

## REQUIREMENTS (FAIL-CLOSED)

1. Define the three extension types: addition, specialization, supplement
1. Design the registration mechanism in the project manifest
1. Implement extension discovery: scan registered paths, validate against manifest
1. Implement extension loading: merge canonical + extensions into the active instruction set
1. Enforce that unregistered instruction files are flagged as violations
1. Write unit tests for each extension type and for unregistered file detection
1. Document the extension mechanism with examples for each type

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox carries a deterministic REQ ID: REQ-<semver>-<obpi_item>-<criterion_index>.
Backfilled 2026-04-15 under GHI #160 Phase 3 from REQUIREMENTS prose above.
-->

- [x] REQ-0.39.0-03-01: Define the three extension types: addition, specialization, supplement
- [x] REQ-0.39.0-03-02: Design the registration mechanism in the project manifest
- [x] REQ-0.39.0-03-03: Implement extension discovery: scan registered paths, validate against manifest
- [x] REQ-0.39.0-03-04: Implement extension loading: merge canonical + extensions into the active instruction set
- [x] REQ-0.39.0-03-05: Enforce that unregistered instruction files are flagged as violations
- [x] REQ-0.39.0-03-06: Write unit tests for each extension type and for unregistered file detection
- [x] REQ-0.39.0-03-07: Document the extension mechanism with examples for each type


## ALLOWED PATHS

- `src/gzkit/instructions/` — extension mechanism implementation
- `tests/` — unit tests
- `docs/design/adr/pre-release/ADR-0.39.0-instruction-plugin-registry/` — this ADR and briefs

## QUALITY GATES (Heavy)

- [ ] Gate 1 (ADR): Intent recorded in this brief
- [ ] Gate 2 (TDD): `uv run gz test` passes
- [ ] Gate 3 (Docs): Extension mechanism documented with examples
- [ ] Gate 5 (Attestation): Human attestation required (Heavy lane)

## Closing Argument

*To be authored at completion from delivered evidence.*
