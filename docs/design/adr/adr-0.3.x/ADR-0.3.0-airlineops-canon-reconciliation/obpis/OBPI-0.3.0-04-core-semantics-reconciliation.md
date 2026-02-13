---
id: OBPI-0.3.0-04-core-semantics-reconciliation
parent: ADR-0.3.0
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.3.0-04-core-semantics-reconciliation: Core Semantics Reconciliation

## ADR Item

- **Source ADR:** `docs/design/adr/adr-0.3.x/ADR-0.3.0-airlineops-canon-reconciliation/ADR-0.3.0-airlineops-canon-reconciliation.md`
- **Checklist Item:** #4 — "Reconcile charter/lifecycle/linkage/closeout semantics and relink concept overlays."

**Status:** Draft

## Objective

Align gzkit semantic overlays with canonical charter/lifecycle/linkage/closeout obligations while keeping canonical docs authoritative.

## Lane

**Heavy** — External governance parity surface and operator contract impact.

## Allowed Paths

- `docs/user/reference/charter.md`
- `docs/user/concepts/lifecycle.md`
- `docs/user/concepts/obpis.md`
- `docs/user/concepts/closeout.md`
- `docs/user/index.md`

## Denied Paths

- `docs/governance/GovZero/*.md (canonical text edits)`
- `src/gzkit/**`
- `/Users/jeff/Documents/Code/airlineops/**`

## Requirements (FAIL-CLOSED)

1. MUST treat canonical GovZero docs as authoritative references.
1. MUST convert gzkit concept pages into additive overlays that cite canonical sections.
1. MUST resolve lifecycle status terminology conflicts where present.
1. NEVER encode contradictory gate or attestation authority semantics.
1. ALWAYS preserve human-attestation sovereignty from canonical charter.

> STOP-on-BLOCKERS: if canonical source, required paths, or baseline artifacts are unavailable, stop and report blockers.

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests pass: `uv run -m unittest discover tests`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Format clean: `uv run gz format --check` (or equivalent non-mutating check)
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs lint/build checks pass for changed docs

### Gate 4: BDD (Heavy only)

- [ ] Contract-level behavior checks executed or explicitly marked N/A with rationale

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
rg -n "canonical|GovZero" docs/user/concepts docs/user/reference/charter.md
uv run gz validate --documents
uv run -m unittest discover tests
```

## Acceptance Criteria

- [ ] Concept and reference pages explicitly point to canonical GovZero docs for normative behavior.
- [ ] Known lifecycle/linkage/closeout semantic drift findings are closed or explicitly deferred.
- [ ] No contradictory language remains in user-facing governance concept docs.

## Evidence

### Implementation Summary

- Files created/modified:
- Validation commands run:
- Date completed:

---

**Brief Status:** Draft
