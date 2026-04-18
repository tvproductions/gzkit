---
id: OBPI-0.0.18-02-runbook-prd-to-adr
parent: ADR-0.0.18
item: 2
lane: Lite
status: Draft
---

# OBPI-0.0.18-02-runbook-prd-to-adr: runbook PRD → ADR derivation guidance

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- **Checklist Item:** #2 — "Runbook: PRD → ADR derivation guidance"

**Status:** Draft

## Objective

Expand `docs/user/runbook.md` with a section that answers: "I have a PRD, I have a Constitution — how do I decide what ADRs to write, what kinds they should be, and what to defer into the pool?" The section is prescriptive, grounded in the concepts page (OBPI-01), and names the decision points where an operator consults the doctrine.

## Lane

**Lite** — documentation.

## Allowed Paths

- `docs/user/runbook.md` (section addition)
- `docs/governance/governance_runbook.md` (parallel guidance if warranted)
- Nothing else.

## Denied Paths

- Concepts page (OBPI-01 already covers the what/why)
- Skill prompts (OBPI-05)
- Pool curation mechanics (OBPI-03)
- Epic grouping (OBPI-04)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The new runbook section names the derivation question explicitly: "Given a PRD and a Constitution, how do I decide which ADRs to write?"
2. REQUIREMENT: The section documents the foundation-vs-feature heuristic: foundation = app/system invariant or identity-shaping semantic; feature = named capability shipping to users; pool = noted but not committed.
3. REQUIREMENT: The section walks a worked example end-to-end — taking a sample PRD statement and showing which ADRs fall out, each classified as foundation / feature / pool with rationale.
4. REQUIREMENT: The section explicitly addresses the "foundation first, features on top" anti-pattern: foundation ADRs should not be created defensively or speculatively to "establish the layer" — they should name invariants that actual feature work needs to rely on.
5. REQUIREMENT: The section names the pool's role explicitly: the pool is the answer to "I can see the concern but I can't commit to it yet." Cross-links to OBPI-03 (pool curation policy) for the deeper policy.
6. REQUIREMENT: The section links to `docs/user/concepts/adr-taxonomy.md` at the first mention of each kind.
7. REQUIREMENT: `mkdocs build --strict` passes.

## Verification

```bash
uv run mkdocs build --strict
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Evidence

- Runbook diff
- Worked example as a standalone reading test (operator unfamiliar with gzkit should be able to trace the PRD→ADR decomposition from the example alone)
- ARB receipt

## REQ Coverage

- REQ-0.0.18-02-01 through REQ-0.0.18-02-07
