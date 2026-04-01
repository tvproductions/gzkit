---
id: OBPI-0.0.11-03-trait-composition-model
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 3
lane: Lite
status: Draft
---

# OBPI-0.0.11-03-trait-composition-model: Trait Composition Model

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #3 - "Trait composition model (orthogonal combination rules)"

**Status:** Draft

## Objective

Persona traits, anti-traits, and composition rules are documented and, where
needed, implemented so multi-trait persona frames combine predictably without
regressing to generic expert framing.

## Lane

**Lite** - This OBPI defines internal composition rules and helper logic. It
does not introduce a new external contract by itself.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Dependencies

- **Depends on:** OBPI-0.0.11-02 (persona directory, file format, and schema
  must exist before composition rules can be documented or exemplars created)
- **Blocks:** None directly (ADR-0.0.12 consumes composition rules)

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md` — parent ADR for composition intent
- `docs/governance/governance_runbook.md` — operator-facing composition rules
- `.gzkit/personas/` — exemplar persona files exercising composition
- `src/gzkit/personas.py` — composition helper module when implementation is needed
- `tests/test_persona_composition.py` — focused composition regression tests

## Denied Paths

- `src/gzkit/cli/**` — CLI surface belongs to OBPI-0.0.11-02
- `AGENTS.md` — context-frame template work belongs to OBPI-0.0.11-04
- `docs/design/adr/pool/ADR-pool.per-command-persona-context.md` — supersession belongs to OBPI-0.0.11-05
- `tests/test_persona_schema.py` — structural validation belongs to OBPI-0.0.11-06
- Paths not listed in Allowed Paths

## Concrete Composition Example

Given a persona file with these frontmatter fields:

```yaml
name: implementer
traits:
  - meticulous: "Reads the full file before editing. Plans the complete change
    before writing the first line. Treats every edit as a coherent unit —
    imports, usage, and tests land together."
  - systems-thinker: "Sees the file as part of a larger system. Checks callers,
    tests, and docs before modifying a function signature. Traces consequences
    before acting."
anti-traits:
  - token-minimizer: "Never optimizes for fewer tokens at the cost of
    correctness. Does not split edits to reduce diff size. Does not skip
    context-reading to save time."
grounding: |
  You write code the way a careful craftsperson builds furniture — measure
  twice, cut once. Every change is complete before you move on. You would
  rather take longer and be right than be fast and leave breakage behind.
```

**Composition operation:** Each trait's prose is concatenated into the persona
frame's behavioral identity section, separated by paragraph breaks. Anti-traits
are concatenated into a "What this persona does NOT do" section. The grounding
text is emitted verbatim as the opening behavioral anchor.

**Resulting persona frame (deterministic output):**

```text
[grounding text verbatim]

You are meticulous: [meticulous trait text]

You are a systems-thinker: [systems-thinker trait text]

What this persona does NOT do:
- token-minimizer: [token-minimizer anti-trait text]
```

**Orthogonality rule:** Traits compose by concatenation because the PERSONA/ICLR
research shows personality traits are approximately orthogonal directions in
activation space. Adding a trait does not interfere with existing traits — each
activates an independent behavioral dimension. If two traits conflict (e.g.,
"move-fast" vs "meticulous"), the anti-trait mechanism rejects the conflicting
trait at validation time rather than attempting runtime resolution.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Trait composition MUST be documented as orthogonal combination,
   not ad-hoc prompt concatenation — the concrete example above defines the
   canonical composition operation
1. REQUIREMENT: Anti-traits MUST define what conflicting behavior is suppressed
   or rejected during persona assembly
1. REQUIREMENT: Composition rules MUST remain deterministic enough that two
   implementers would derive the same resulting persona frame — the template
   above is the reference format
1. NEVER: Reintroduce expertise-claim language as a substitute for trait
   composition
1. ALWAYS: Keep composition guidance aligned with the PERSONA/ICLR framing cited
   by ADR-0.0.11

> STOP-on-BLOCKERS: if composition rules depend on unresolved control-surface
> decisions, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [ ] Research basis: `docs/design/research-persona-selection-agent-identity.md`
- [ ] Downstream profile ADR: `docs/design/adr/foundation/ADR-0.0.12-agent-role-persona-profiles/ADR-0.0.12-agent-role-persona-profiles.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/governance/governance_runbook.md`
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/personas/`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Pattern to follow: `.gzkit/personas/`
- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Not required for Lite lane

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
test -d .gzkit/personas
test -f docs/governance/governance_runbook.md
uv run -m unittest tests/test_persona_composition.py -v
rg -n "anti-trait|orthogon|compose" docs/governance/governance_runbook.md src/gzkit/personas.py
```

## Acceptance Criteria

- [ ] REQ-0.0.11-03-01: Composition rules define how multiple traits combine without changing the intended behavioral identity
- [ ] REQ-0.0.11-03-02: Anti-traits define what conflicting persona behavior is suppressed or rejected
- [ ] REQ-0.0.11-03-03: Tests or documented examples demonstrate deterministic composition outcomes for at least one multi-trait persona case

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Record test output here during execution.
```

### Code Quality

```text
# Record lint/typecheck output here during execution.
```

### Gate 3 (Docs)

```text
# Not required for Lite lane.
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

Before this OBPI, the ADR claimed orthogonal composition but did not define how
traits and anti-traits combine operationally. After this OBPI, downstream
persona profile work can assemble traits against a deterministic model.

### Key Proof

`uv run -m unittest tests/test_persona_composition.py -v`

### Implementation Summary

- Files created/modified:
- Tests added:
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
