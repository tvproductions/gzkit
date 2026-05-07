---
id: ADR-0.0.33-agent-control-surface-fidelity
status: Draft
kind: foundation
semver: 0.0.33
lane: heavy
parent:
date: 2026-04-26
---

# ADR-0.0.33-agent-control-surface-fidelity: Agent Control Surface Fidelity Doctrine

## Persona

`main-session` (craftsperson, governance-aware, whole-file-reasoning, direct).
This ADR codifies an invariant that every other gzkit pillar rests on; the
authoring posture is doctrine-author, not feature-implementer. Agents working
on this ADR must treat the four invariants as binding constraints whose
mechanical defenses are non-negotiable, not as advisory targets to soften.

## Intent

> **Agent = Model + Harness + Intent.** The Agent Control Surface is the
> per-turn corpus the harness loads on the model's behalf — `AGENTS.md`,
> `CLAUDE.md`, `.claude/rules/**`, skill bodies, the chore registry, persona
> files, handoffs. **gzkit is control surfaces and tools designed so that
> operator intent makes the model's intrinsic weaknesses and negative
> tendencies inert.**

This ADR canonizes the doctrine that governs that surface's fidelity to its
declared rules. The full doctrine lives at
[`docs/governance/agent-control-surface-fidelity-doctrine.md`](../../../../governance/agent-control-surface-fidelity-doctrine.md);
this ADR is the lifecycle anchor that lands its mechanical defenses.

The originating signal is GHI #327: a diet pass on `AGENTS.md` and
`CLAUDE.md` surfaced the empirical question *"how do we know we didn't
reduce blindly?"* Today's gzkit cannot answer that question structurally.
A silently-missing rule is invisible to PRIME DIRECTIVE, DO IT RIGHT, and
the anti-vibing mantra — all three pillars assume the rule is loaded. This
ADR is the structural backstop for that assumption.

## Decision

**The Agent Control Surface preserves every binding rule from its canonical
sources to its rendered output. Surface weight does not regress past tested
floors. Pointers resolve. Bullets are reachable from the loading scenarios
they should fire in. Drift in the rendered surface is detectable at compile
time, not at audit time.**

Four invariants, mechanically validated:

1. **Bullet retention** — every bullet on `docs/governance/advisory-rules-audit.md`
   classified Mechanical or Promotable is present verbatim in the per-turn
   surface (Era 1) or registered as a `Bullet` instance in the canonical
   Pydantic content model (Era 2 onward, per ADR-0.0.34). Validator:
   `gz validate --bullet-retention`.
2. **Surface weight regression** — direction-binding (no growth past current
   snapshot 1768 lines) is fail-closed. Provisional warning bands grounded in
   2026 literature: green ≤ 1800, yellow 1801–2200 (waiver required), red
   > 2200 (fail closed). Recalibration cadence: 6 months minimum, against
   operational evidence. Validator: `gz validate --surface-weight`. Snapshot
   file: `data/surface_weight_floor.json`.
3. **Pointer integrity** — every `> See [...](path#anchor)` lift pointer in
   the per-turn surface resolves to an existing destination heading anchor;
   every lifted-pedagogy page carries a `<!-- lifted-from: <path>#<anchor> -->`
   back-pointer. Validator: `gz validate --pointer-anchors`.
4. **Loading-scenario reachability** — every Mechanical/Promotable bullet is
   reachable from at least one declared loading scenario in
   `data/agent-control-surface-scenarios.json`. Advisory until ADR-0.0.34
   substrate work lands the registry. Validator:
   `gz validate --scenario-reachability`.

Composite scope: `gz validate --surface-fidelity` runs all four invariants
and wires into `gz check`. Cheap structural subset (1, 2, 3) runs in
pre-commit; reachability is CI-only Era-1.

The doctrine is **substrate-invariant**: it governs the rendered output's
fidelity to its declared invariants, not the composition method. Validators
evolve across eras (hand-authored Era 1 → Pydantic+Jinja2 Era 2 →
progressive disclosure Era 3); the invariants don't change.

The doctrine names the failure pattern (D2 framing); the audit names the
historical instances. Specific drift findings on ADR-0.14.0 and ADR-0.16.0
are tracked as separate GHIs, not embedded in this ADR's body.

## Comparator Uplift (2026-05-07)

Competitors with polished workflows still depend on agents correctly reading
their loaded context. This ADR should treat comparator-inspired workflow
surfaces as fidelity-critical: if a borrowed workflow adds a section, marker,
role, or command promise to an agent-loaded surface, the fidelity validators
must prove the rendered surface preserves it and rejects partial mirrors.

## Consequences

### Positive

- A silently-missing binding bullet becomes detectable at compile time, not
  audit time. Closes the GHI #327 class of failure.
- The fidelity doctrine becomes the structural backstop the upstream pillars
  (PRIME DIRECTIVE, DO IT RIGHT, anti-vibing mantra, OPERATOR ECONOMY) rest
  on. They assume the rule is loaded; this ADR makes that assumption
  observable.
- Forward-compatible with the substrate doctrine (ADR-0.0.34): the Era-2
  bullet-retention check upgrades from substring grep to canonical-model
  diff without invalidating Era-1 evidence.
- Composite + narrow validator scopes match gzkit's existing
  `gz validate --<scope>` pattern; CI signal is granular.

### Negative

- Adds five new validator scopes the project must maintain. Per the
  anti-vibing mantra ("lighter ceremony is not a tradeoff axis"), this is
  the product, not overhead.
- Provisional warning bands in Invariant 2 may need recalibration before
  the 6-month cadence if operational evidence shows the bands are
  miscalibrated. The recalibration is itself a doctrine artifact.
- Invariant 4 (scenario reachability) is advisory until ADR-0.0.34 lands
  the loading-scenarios registry. Era-1 fidelity is incomplete by design.
- Behavioral fidelity (the layer that asserts the agent complies with the
  rule when the surface is loaded) is deferred to a follow-up GHI; the four
  invariants are *structural*, not behavioral. Structural-without-behavioral
  is not full fidelity, but the inverse is worse.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 5

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.33-01: Bullet-retention validator (`gz validate --bullet-retention`) — read advisory scorecard, assert Mechanical/Promotable bullets present verbatim in per-turn surface, exit 3 on missing
- [ ] OBPI-0.0.33-02: Surface-weight validator (`gz validate --surface-weight`) — snapshot file, waiver schema, fail-closed direction-binding, provisional warning bands, recalibration commitment
- [ ] OBPI-0.0.33-03: Pointer-integrity validator (`gz validate --pointer-anchors`) — parse `> See [...]` blockquotes, resolve anchors, reverse-check `<!-- lifted-from: -->` back-pointers, exit 3 on unresolved
- [ ] OBPI-0.0.33-04: Scenario-reachability validator (`gz validate --scenario-reachability`) — advisory Era-1; reads loading-scenarios registry once ADR-0.0.34 lands it; warns on orphan bullets
- [ ] OBPI-0.0.33-05: Composite scope + CI wiring — `gz validate --surface-fidelity` runs all four; wired into `gz check`; cheap subset (1, 2, 3) in pre-commit; tests under `tests/governance/` per per-rule-file naming and the eval-awareness corollary

## Q&A Transcript

<!-- Interview transcript preserved for context -->

The doctrine page is the canonical Q&A capture. See
[`docs/governance/agent-control-surface-fidelity-doctrine.md`](../../../../governance/agent-control-surface-fidelity-doctrine.md)
for the derivation from upstream pillars, the levers-vs-constraints
framing, the substrate-invariance argument, and the deferred behavioral
test layer.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/governance/test_bullet_retention.py`, `tests/governance/test_surface_weight.py`, `tests/governance/test_pointer_integrity.py`, `tests/governance/test_scenario_reachability.py`
- [ ] Docs: `docs/governance/agent-control-surface-fidelity-doctrine.md`
- [ ] Validators: `src/gzkit/governance/trust_audits.py` (or successor module per existing pattern)
- [ ] Snapshot data: `data/surface_weight_floor.json`, `data/surface_weight_waivers.json`, `data/agent-control-surface-scenarios.json` (Era-2)
- [x] Historical-instance audits (cite-targets for first audit sweep): `artifacts/audits/adr-0.14.0-closeout-drift-2026-04-26.md` (GHI #331 — formal acknowledgement-of-historical-drift); `artifacts/audits/adr-0.16.0-closeout-drift-2026-04-26.md` (GHI #332 — formal acknowledgement; partial-prior generalized into ADR-0.0.34).

## Alternatives Considered

- **A — Behavioral-only fidelity (golden-dataset + LLM-as-judge first).**
  Rejected: behavioral testing without a structural layer tests against a
  corpus that may have already silently lost rules. Structural is the
  foundation; behavioral is the deferred follow-up.
- **B — Embed the four invariants as runtime hooks rather than `gz validate`
  scopes.** Rejected: gzkit's existing pattern is composite + narrow
  validator scopes; runtime hooks are the wrong architectural layer for
  compile-time fidelity.
- **C — Fix the Era-1 instances directly (ADR-0.14.0, ADR-0.16.0 closeout
  drift) without authoring the doctrine.** Rejected per DO IT RIGHT #1: fix
  the class of failure, not the instances. Specific findings file as
  separate GHIs (b, c in the follow-up cluster).
- **D — Wait for the substrate doctrine (ADR-0.0.34) before authoring
  fidelity.** Rejected: the doctrine is substrate-invariant by design;
  authoring it now lets Era-1 validators ship while the substrate is
  authored, and the validators upgrade in place when Era 2 lands.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.33 | Pending | | | |
