---
id: OBPI-0.0.11-01-persona-research-synthesis
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 1
lane: Lite
status: attested_completed
---

# OBPI-0.0.11-01-persona-research-synthesis: Persona Research Synthesis

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #1 - "Research synthesis and design principles document"

**Status:** Completed

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

## Dependencies

- **Depends on:** None (fully independent; first in the critical path)
- **Blocks:** OBPI-0.0.11-02 (design principles inform control surface),
  OBPI-0.0.11-05 (pool ADR review feeds supersession)

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

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [x] Research target: `docs/design/research-persona-selection-agent-identity.md`
- [x] Superseded pool reference: `docs/design/adr/pool/ADR-pool.per-command-persona-context.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists or is intentionally created in this OBPI: `docs/design/research-persona-selection-agent-identity.md`
- [x] Required path exists or is intentionally created in this OBPI: `docs/governance/governance_runbook.md`
- [x] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [x] Pattern to follow: `docs/design/research-persona-selection-agent-identity.md`
- [x] Parent ADR integration points reviewed for local conventions
- [x] Related persona ADRs reviewed: `ADR-0.0.12`, `ADR-0.0.13`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Verification commands recorded in evidence with real outputs
- [x] Repository checks stay green: `uv run gz lint`, `uv run gz typecheck`, `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Not required for Lite lane beyond the authored docs in Allowed Paths

### Gate 4: BDD (Heavy only)

- [x] Not required for Lite lane

### Gate 5: Human (Heavy only)

- [x] Not required for Lite lane (human attestation provided via parent ADR Heavy lane inheritance)

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

- [x] REQ-0.0.11-01-01: The research document names and summarizes all five cited sources from ADR-0.0.11 with preserved links
- [x] REQ-0.0.11-01-02: The synthesis states why expertise-claim personas are disallowed and why behavioral identity is required
- [x] REQ-0.0.11-01-03: The document yields concrete design principles and anti-pattern guidance that downstream OBPIs can implement without re-running the literature review

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Verification commands executed and recorded
- [x] **Code Quality:** Lint and type checks remain clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete citation-based example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run gz lint → All checks passed
uv run gz typecheck → All checks passed
uv run gz test → 2304 tests passed (33.3s)
```

### Code Quality

```text
uv run gz lint → All checks passed, ADR path contract check passed
uv run gz typecheck → All checks passed
```

### Gate 3 (Docs)

```text
Not required beyond authored docs in Allowed Paths.
Research document and governance runbook updated within Allowed Paths.
```

### Gate 4 (BDD)

```text
Not required for Lite lane.
```

### Gate 5 (Human)

```text
Human attestation received via parent ADR Heavy lane inheritance.
Attestor: jeff
Date: 2026-04-01
```

### Value Narrative

Without this synthesis, the natural first attempt at a persona file would be
"You are an expert Python developer" — which PRISM measured at -3.6pp accuracy.
The synthesis names 5 specific anti-patterns that would make persona framing
counterproductive and provides the research-backed corrective for each. It is
the load-bearing argument for every design decision in the remaining 5 OBPIs:
OBPI-02's schema, OBPI-03's composition model, and OBPI-04's anti-expertise
constraint all depend on this research foundation.

### Key Proof

Without the anti-patterns section, an implementer writing
`.gzkit/personas/implementer.md` would likely produce job-description framing
("Senior Python developer with 10 years experience in governance systems").
The PSM personality-inference finding explains why this backfires: the model
infers "what sort of person has this resume?" and activates an unpredictable
trait cluster including credential-consciousness and risk aversion. The
synthesis redirects to behavioral identity ("Reads the full file before
editing. Plans the complete change before writing the first line.") which
activates the meticulous trait cluster directly.

### Implementation Summary

- Files modified: `docs/design/research-persona-selection-agent-identity.md` (added Anti-Patterns section with 5 named anti-patterns), `docs/governance/governance_runbook.md` (added Persona Design Principles section)
- Tests added: none expected for this Lite documentation OBPI
- Date completed: 2026-04-01
- Attestation status: human attestation received
- Defects noted: GHI #78 — pipeline ceremony template produced shallow-compliance output; fixed in-session

## Tracked Defects

- GHI #78: Pipeline Stage 4 ceremony template produces shallow-compliance output (fixed in-session, closed)

## Human Attestation

- Attestor: `jeff`
- Attestation: `attest completed`
- Date: `2026-04-01`

---

**Brief Status:** Completed

**Date Completed:** 2026-04-01

**Evidence Hash:** -
