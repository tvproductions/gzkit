---
id: ADR-pool.lightweight-pre-implementation-challenger
status: Pool
parent: PRD-GZKIT-1.0.0
lane: lite
enabler: null
---

# ADR-pool.lightweight-pre-implementation-challenger: Lightweight pre-implementation challenger agent

## Status

Pool

## Intent

gzkit's adversarial / red-team evaluation surface lives inside the
heavyweight `gz-adr-evaluate` skill (10 structured red-team challenges,
8-dimension scoring). That weight is correct **at ADR authoring** but
disproportionate for the smaller question that fires more often:
*"before exiting plan mode for an OBPI, has this plan been challenged on
feasibility, scope, and design lens?"* `gz-plan-audit` covers
brief-vs-plan alignment but not adversarial challenge.

EveryInc ships three lightweight cross-corpus exemplars — the
`ce-feasibility-reviewer`, `ce-design-lens-reviewer`, and
`ce-scope-guardian-reviewer` agents — invoked at plan-authoring time
without forcing a full evaluation ceremony. They challenge the plan,
they don't score it.

A gzkit-shaped equivalent — a single `pre-implementation-challenger`
subagent invoked by `gz-plan-audit` (or as a sibling skill) — would
front-run plan exit on three named axes (feasibility, scope-creep,
design-blind-spots) without duplicating `gz-adr-evaluate`'s heavier
ceremony.

## Decision

_[To be filled at promotion time]_

Sketch:

- New subagent `pre-implementation-challenger` under `.gzkit/personas/`
  (or `.claude/agents/` mirror), composed from existing `quality-reviewer`
  + `spec-reviewer` traits with adversarial framing added.
- Invoked **once** before plan-mode exit, on three named axes:
  feasibility (will this approach survive contact with reality?),
  scope-creep (does the plan exceed the brief's allowed paths?),
  design-blind-spots (what interaction states / failure paths are
  unnamed?).
- Output is a structured findings block with explicit verdict per axis;
  operator decides accept/revise/reject. Findings do **not** auto-block
  — same shape as `gz-plan-audit`'s advisory output.
- Findings are appended to the OBPI brief's evidence section so the
  Gate-5 attestation chain has access to the pre-implementation
  challenge record.

## Alternatives Considered

1. **Always run `gz-adr-evaluate`'s 10 red-team challenges before
   plan-exit.** Rejected — disproportionate for OBPI-level plans;
   evaluator is calibrated for ADR-level intent, not increment-level
   execution.
2. **Add another flag to `gz-plan-audit`.** Plausible alternative;
   evaluate at promotion time. Tradeoff: keeps the surface flat but
   couples adversarial challenge to alignment audit, which may
   conflate two different judgment shapes.
3. **Three separate agents (one per axis), as EveryInc does.**
   Rejected as initial shape — multiplies the agent surface without
   evidence the axes need to be parallelizable. Single agent with
   three named verdicts is the smaller-vibing-surface choice.
4. **Do nothing; rely on operator judgment at plan exit.** Rejected —
   operator-judgment-only at plan-exit is the named gap that allowed
   GHI #195 (default-to-ceremony intuition without precedent count)
   and similar drifts. The mantra: *"every option framed by smallest-
   vibing-surface."*

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
