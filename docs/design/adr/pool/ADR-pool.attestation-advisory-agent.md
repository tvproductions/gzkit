---
id: ADR-pool.attestation-advisory-agent
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: ADR-0.18.0-subagent-driven-pipeline-execution
---

# ADR-pool.attestation-advisory-agent: Attestation Advisory Agent

## Status

Pool

## Date

2026-03-21

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Gate 5 attestation today is human-only with no independent agent advisory input. The two-stage review protocol (ADR-0.18.0, OBPI-03) validates implementation quality, but nothing validates attestation readiness independently. An attestation advisor agent — running with fresh context (and optionally a different model) — would review evidence, audit artifacts, and produce a structured recommendation before the human decides. This provides a "second opinion" that strengthens the human's attestation decision without replacing it.

## Design Tensions

These are the key architectural questions to resolve during promotion:

| Tension | Option A | Option B |
|---------|----------|----------|
| **Enforcement level** | Required gate (Gate 5a) — attestation blocked without advisor pass | Optional tool — human can invoke or skip at will |
| **Model diversity** | Same model as orchestrator (cheaper, simpler) | Cross-model (e.g., orchestrator=opus, advisor=sonnet or vice versa) for genuine diversity of perspective |
| **Timing** | Pre-attestation advisory — runs before human decides | Post-attestation audit reconciliation — runs after human attests, flags discrepancies |
| **Scope** | ADR-level only (reviews all OBPIs holistically) | OBPI-level + ADR-level (advisory at each OBPI ceremony and at closeout) |

## Potential OBPI Decomposition (Sketch)

1. Attestation advisor role definition and agent file (extends ADR-0.18.0 role taxonomy)
2. Evidence review protocol: what the advisor checks, structured output format
3. Advisory dispatch integration into closeout ceremony skill
4. Cross-model routing: model selection strategy for advisor vs. orchestrator
5. CLI surface: `gz advise ADR-X.Y.Z` or integration into `gz closeout`

## Dependencies

- ADR-0.18.0 (subagent dispatch infrastructure, role taxonomy)
- Closeout ceremony skill (`gz-adr-closeout-ceremony`)
- Audit protocol (`docs/governance/GovZero/audit-protocol.md`)

## Consequences (if promoted)

- Gate 5 ceremony gains an optional or required advisory step
- Closeout ceremony skill updated with advisor dispatch
- New agent file: `.claude/agents/attestation-advisor.md`
- Cross-model dispatch may require model routing config extension from ADR-0.18.0

## Origin

Identified during ADR-0.18.0 closeout ceremony (2026-03-21) when the human observed that no mechanism exists for an agent to independently validate attestation readiness before the human commits their attestation.
