---
id: {id}
status: {status}
kind: {kind}
semver: {semver}
lane: {lane}
parent: {parent}
date: {date}
---

# {id}: {title}

## Persona

<!-- Describe the behavioral identity for agents working on this ADR.
     Frame as values and craftsmanship standards, not expertise claims.
     See .gzkit/personas/ for reusable persona definitions. -->

{persona}

{why_foundation_tier}## Intent

{intent}

## Decision

{decision}

## Consequences

### Positive

{positive_consequences}

### Negative

{negative_consequences}

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| Replace with an assertion that exercises this ADR's thesis against the real system. | uv run gz --version | 0 |

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

{decomposition_scorecard}

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps.
     The box is a ROW MARKER, never a status claim: leave it `- [ ]`. Completion
     lives in the ledger — read it with `uv run gz adr status`, never from this
     page. A `[x]` here is rejected by `gz validate --documents` (GHI #928). -->

{checklist}

## Q&A Transcript

<!-- Interview transcript preserved for context -->

{qa_transcript}

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

{alternatives}

## Forcing Functions

<!-- The seven techniques `gz-adr-create` SKILL.md declares non-negotiable, plus
     its closing question. Agent drafts each against session evidence; the
     operator audits, names what was missed, and confirms
     (AGENTS.md § OPERATOR ECONOMY OF EFFORT #4) — this is agent labor, not
     operator typing. -->

### Pre-Mortem

{pre_mortem}

### What Would Have to Be True

{wwhtbt}

### Constraint Archaeology

{constraint_archaeology}

### Assumption Surfacing

{assumption_surfacing}

### The 2am Operator Question

{operator_2am}

### Reversibility

{reversibility}

### Scope Minimization

{scope_minimization}

### Downstream Decisions Forced

{downstream_adrs}

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| {semver} | Pending | | | |
