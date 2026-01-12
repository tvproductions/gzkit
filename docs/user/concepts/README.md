# Concepts

gzkit spans three concerns. Each has distinct characteristics and audiences.

## The Three Concerns

| Concern | Purpose | Primary Audience | Agent-Native? |
|---------|---------|------------------|---------------|
| [Specification](specification.md) | Invariants, constraints, acceptance criteria | Agent | Yes |
| [Methodology](methodology.md) | Phases, workflows, checkpoints | Process | Shared |
| [Governance](governance.md) | Authority, attestation, audit | Human | No |

## Why Three?

These concerns are often conflated, leading to:

- **Specification without governance** → Drift (no enforcement)
- **Governance without methodology** → Theater (no structure)
- **Methodology without specification** → Arbitrary (no grounding)

gzkit keeps them distinct but connected. Each gate touches all three:

| Gate | Specification | Methodology | Governance |
|------|---------------|-------------|------------|
| 1 ADR | Intent captured | Phase: plan | Decision recorded |
| 2 TDD | Tests pass | Phase: implement | Evidence generated |
| 3 Docs | Docs accurate | Phase: implement | Evidence generated |
| 4 BDD | Contracts verified | Phase: implement | Evidence generated |
| 5 Human | N/A | Phase: analyze | Authority exercised |

## For Agents

If you're an AI agent working in a gzkit project:

1. **Ground against specification** — Canon, ADRs, acceptance criteria are your constraints
2. **Follow methodology** — Gates sequence for a reason; don't skip ahead
3. **Respect governance** — Gate 5 is human-only; present evidence, don't decide

See [Specification](specification.md) for constraint patterns.

## For Humans

If you're a human working with AI agents:

1. **Define specification clearly** — Explicit constraints beat implicit conventions
2. **Trust methodology** — Gates catch drift; let them work
3. **Exercise governance** — Gate 5 is yours; observe and attest

See [Governance](governance.md) for attestation patterns.
