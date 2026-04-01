---
id: OBPI-0.0.11-01-persona-research-synthesis
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 1
lane: Lite
status: Draft
---

# OBPI-0.0.11-01-persona-research-synthesis: Persona Research Synthesis

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #1 - "Research synthesis and design principles document"

**Status:** Draft

## Objective

`docs/design/research-persona-selection-agent-identity.md` synthesizes the
five cited persona studies into implementation-facing design principles,
anti-pattern guidance, and bibliography evidence for ADR-0.0.11.

## Lane

**Lite** - This OBPI is documentation and evidence authoring. It does not
change a runtime contract by itself.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md` — parent ADR for intent and rationale
- `docs/design/research-persona-selection-agent-identity.md` — primary research synthesis artifact
- `docs/governance/governance_runbook.md` — design-principle handoff surface
- `docs/design/adr/pool/ADR-pool.per-command-persona-context.md` — superseded design reference to mine for reusable ideas

## Denied Paths

- `src/gzkit/**` — implementation belongs to downstream OBPIs
- `tests/**` — validation infrastructure belongs to OBPI-0.0.11-06
- `features/**` — BDD ownership belongs to Heavy contract work
- `AGENTS.md` — template integration belongs to OBPI-0.0.11-04
- Paths not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The research document MUST summarize all five cited sources in
   ADR-0.0.11 and state why each source matters to gzkit's persona surface
1. REQUIREMENT: The synthesis MUST explain the PRISM result that generic
   expertise claims degrade accuracy and connect that result to the ADR's
   critical constraint
1. REQUIREMENT: The synthesis MUST translate research findings into
   implementation-facing design principles and explicit anti-patterns
1. NEVER: Invent empirical claims or causal guarantees not supported by the
   cited sources
1. ALWAYS: Preserve stable citations and cross-reference ADR-0.0.11 from the
   research document

> STOP-on-BLOCKERS: if cited research cannot be located or contradicts the ADR,
> print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [ ] Research target: `docs/design/research-persona-selection-agent-identity.md`
- [ ] Superseded pool reference: `docs/design/adr/pool/ADR-pool.per-command-persona-context.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/research-persona-selection-agent-identity.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/governance/governance_runbook.md`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Pattern to follow: `docs/design/research-persona-selection-agent-identity.md`
- [ ] Parent ADR integration points reviewed for local conventions
- [ ] Related persona ADRs reviewed: `ADR-0.0.12`, `ADR-0.0.13`

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Verification commands recorded in evidence with real outputs
- [ ] Repository checks stay green: `uv run gz lint`, `uv run gz typecheck`, `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Not required for Lite lane beyond the authored docs in Allowed Paths

### Gate 4: BDD (Heavy only)

- [ ] Not required for Lite lane

### Gate 5: Human (Heavy only)

- [ ] Not required for Lite lane

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/research-persona-selection-agent-identity.md
rg -n "PSM|Assistant Axis|PRISM|PERSONA|Persona Vectors" docs/design/research-persona-selection-agent-identity.md
rg -n "virtue-ethics|expert persona|expertise claims|anti-pattern" docs/design/research-persona-selection-agent-identity.md
```

## Acceptance Criteria

- [ ] REQ-0.0.11-01-01: The research document names and summarizes all five cited sources from ADR-0.0.11 with preserved links
- [ ] REQ-0.0.11-01-02: The synthesis states why expertise-claim personas are disallowed and why behavioral identity is required
- [ ] REQ-0.0.11-01-03: The document yields concrete design principles and anti-pattern guidance that downstream OBPIs can implement without re-running the literature review

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Verification commands executed and recorded
- [ ] **Code Quality:** Lint and type checks remain clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete citation-based example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Record command outputs here during execution.
```

### Code Quality

```text
# Record lint/typecheck output here during execution.
```

### Gate 3 (Docs)

```text
# Not required beyond authored docs in Allowed Paths.
```

### Gate 4 (BDD)

```text
# Not required for Lite lane.
```

### Gate 5 (Human)

```text
# Not required for Lite lane.
```

### Value Narrative

Before this OBPI, persona work was argued in the ADR body but not consolidated
into a reusable research artifact. After this OBPI, later persona-control and
persona-profile work can implement against a single evidence-backed synthesis.

### Key Proof

`rg -n "PSM|PRISM|PERSONA" docs/design/research-persona-selection-agent-identity.md`

### Implementation Summary

- Files created/modified:
- Tests added: none expected for this Lite documentation OBPI
- Date completed:
- Attestation status: n/a
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `n/a`
- Attestation: `n/a`
- Date: `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
