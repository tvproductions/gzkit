---
id: ADR-0.0.33-agent-control-surface-fidelity
status: Validated
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

## Why foundation tier?

Without this ADR, every other gzkit pillar's binding-rule assumption is unprovable — if AGENTS.md and the per-turn agent surface diverge, no rule mechanically enforces anything, and the entire governance contract collapses to honor-system.

This ADR authors a port: the agent-control-surface fidelity contract (canonical = rendered = per-turn) that every rendering substrate must honor.

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
   `gz validate --bullet-retention`. **(Amended 2026-06-03 — tier-scoped; see § Amendment below.)**
2. **Surface weight regression** — direction-binding (no growth past current
   snapshot) is fail-closed. Warning bands: green ≤ 3000, yellow 3001–3400
   (waiver required), red > 3400 (fail closed). Recalibration cadence: 6 months
   minimum, against operational evidence; an override is legitimate only when
   recorded as a `surface_weight_recalibrated` event. Validator:
   `gz validate --surface-weight`. Producer:
   `gz validate --surface-weight --recalibrate`. Snapshot file:
   `data/surface_weight_floor.json`. **(Amended 2026-08-11 — bands recalibrated
   from the original 1800/2200 and the unrecorded 2600/3000; ceremony given a
   producer. See § Amendment (2026-08-11).)**
3. **Pointer integrity** — every `> See [...](path#anchor)` lift pointer in
   the per-turn surface resolves to an existing destination heading anchor;
   every lifted-pedagogy page carries a `<!-- lifted-from: <path>#<anchor> -->`
   back-pointer. Validator: `gz validate --pointer-anchors`.
4. ~~**Loading-scenario reachability** — every Mechanical/Promotable bullet is
   reachable from at least one declared loading scenario in
   `data/agent-control-surface-scenarios.json`. Advisory until ADR-0.0.34
   substrate work lands the registry. Validator:
   `gz validate --scenario-reachability`.~~ **RETIRED 2026-07-25 — see
   § Amendment (2026-07-25): Invariant 4 is retired.**

Composite scope: `gz validate --surface-fidelity` runs the three live
invariants and wires into `gz check`. The cheap structural subset (1, 2, 3)
runs in pre-commit; with Invariant 4 retired the subset is now the whole set.

The doctrine is **substrate-invariant**: it governs the rendered output's
fidelity to its declared invariants, not the composition method. Validators
evolve across eras (hand-authored Era 1 → Pydantic+Jinja2 Era 2 →
progressive disclosure Era 3); the invariants don't change.

The doctrine names the failure pattern (D2 framing); the audit names the
historical instances. Specific drift findings on ADR-0.14.0 and ADR-0.16.0
are tracked as separate GHIs, not embedded in this ADR's body.

### Amendment (2026-06-03): Invariant 1 is tier-scoped

Authored under ADR-0.0.37's § Decision Re-Alignment (2026-06-03), which makes the
agent control surface **composed from an append-only corpus by setpoint-driven,
authoring-time compression** rather than a fixed full-fidelity render. Under
compression, a `compressible`-tier bullet may legitimately be combined or reworded
in a rendered surface, so the Era-1 "present verbatim in the rendered surface"
test would fail-close on exactly the behavior the corpus model is designed to
produce.

**Amended Invariant 1 (tier-scoped):**

- **Invariant tier** (`tier: invariant` corpus entries — e.g. PRIME DIRECTIVE,
  DO IT RIGHT, NEVER PYTEST): the verbatim-presence contract is unchanged and
  fail-closed. These render verbatim at every setpoint; `--bullet-retention`
  asserts their exact presence.
- **Compressible tier**: retention is satisfied by the **advisor-QC
  information-retention receipt + operator attestation** for the committed
  rendition (per ADR-0.0.39 and the universal Gate 5), **not** by verbatim-bullet
  substring presence. The invariant being preserved is *no binding information is
  lost*, witnessed by the QC receipt + attestation, not *every byte is identical*.

The canonical-source verbatim contract (the corpus / the fat tier) is unchanged:
nothing is lost from source; compression governs only the *rendered* compressed
tiers.

**Mechanical coupling.** This amendment is realized by **OBPI-0.0.37-25**, which
flips `gz validate --bullet-retention` from whole-surface verbatim grep to
tier-aware enforcement. The amendment and the validator change land in the same
commit-window (the validator must stay wired into `--surface-fidelity` / `gz check`
throughout — Anti-Pattern #1). This amendment is **attested at OBPI-0.0.37-25's
Gate 5** (foundation/heavy); until then Invariant 1 enforces the original Era-1
contract.

> **Realizer correction (OBPI-0.0.37-25, 2026-06-15).** This paragraph
> originally cited OBPI-0.0.37-18 as the realizer and Gate-5 attestation point.
> That was a mis-citation: OBPI-0.0.37-18 delivered the append-only corpus
> *model* and did not flip `--bullet-retention` (the validator on disk remained
> the Era-1 whole-surface grep). The actual realizer is **OBPI-0.0.37-25** per
> ADR-0.0.37 Checklist item #25; the citation above is corrected accordingly.

### Amendment (2026-07-25): Invariant 4 is retired

**Invariant 4 (loading-scenario reachability) is retired. It is not deferred,
not pending, and not advisory-until-later. The `gz validate
--scenario-reachability` scope, its validator module, and its covering tests
are removed by the same commit that records this amendment.**

Invariant 4 never executed once. Its validator took the Era-1 skip branch on
every run for two months because its precondition,
`data/agent-control-surface-scenarios.json`, was never authored. The deferral
in § Consequences named ADR-0.0.34 as the unblocking condition and
`OBPI-0.0.33-04` assigned the deliverable there explicitly — *"registry
creation is owned by ADR-0.0.34; this OBPI consumes the registry when present
but does NOT bootstrap it"*. ADR-0.0.34 then closed `Validated` with 8/8 OBPIs
attested and zero references to the registry anywhere in its package. The
obligation was inherited and dropped; the named unblocking condition was
satisfied and attested while the artifact it existed to produce was never
built.

Retirement rather than construction, on three grounds. Building the registry
requires deciding *what the scenarios are* — a design judgment about gzkit's
own control-surface model, not a mechanical fill-in; guessing it would produce
a registry that turns the invariant green while proving nothing, which is the
reported failure wearing its opposite face. The campaign's Movement C is
*Reduce the accretion*, and this is accretion that never carried load. And
dead enforcement is worse than absent enforcement: a scope that exits 0 by
construction reads as coverage on every `gz check` run, which is precisely how
the advisory came to be read as ambient noise.

Retirement does not forbid the capability. If a scenario model is later wanted,
it lands under its own ADR carrying its own registry, as designed work rather
than as an inherited debt no package claimed. Tracked at GHI #716, closed
`withdrawn` against this amendment.

### Amendment (2026-08-11): Invariant 2 bands recalibrated, and its ceremony given a producer

**Invariant 2's warning bands become green ≤ 3000, yellow 3001–3400 (waiver
required), red > 3400.** The prior generation — green ≤ 2600, yellow 2601–3000 —
is superseded. Witnessed by a `surface_weight_recalibrated` ledger event
attested by g0, the first such event ever emitted.

**Two prior band changes went unrecorded here, and that is the deeper finding.**
This section still read *"green ≤ 1800, yellow 1801–2200"* until this amendment,
while `_GREEN_CEILING` had been 2600 since 2026-06-30. The source comment
accompanying that change asserted *"ADR-0.0.33 Decision is amended to match"* —
an amendment that was never written. § Anti-Patterns item 3 forbids exactly
this: *"Band changes are ledger events, not config tweaks."*

**The ceremony was unperformable, which is why nobody performed it.**
`OBPI-0.0.33-02` REQ 4 named `gz adr emit-receipt` as the event's producer. That
verb's `--event` is a closed enum of `{completed, validated, closed}` and cannot
accept `surface_weight_recalibrated`; no other registered verb could emit it,
and hand-writing the ledger is forbidden (`AGENTS.md` Never #2). The ledger
carried zero such events across the project's life. Anti-pattern 3 was therefore
not a discipline anyone violated — it was a discipline nothing could satisfy.
Diagnosed and closed under GHI #791, which lands
`gz validate --surface-weight --recalibrate` as the producer: it re-snapshots
`data/surface_weight_floor.json` and appends the witnessing event in one
fail-safe-ordered transaction, floor first.

A self-concealing property made this durable. `_check_floor_drift` returns clean
when zero recalibration events exist, so the gate was silent *exactly while its
producer was missing* and would only have begun speaking after the first event
landed. A check that fails open until its own producer exists cannot report that
producer's absence.

**Operational evidence for the raise.** The corpus stood at exactly 2600 of 2600,
so the next rule edit adding one line would have failed `gz check` closed with no
available remedy: the largest live waiver covers 340 against a delta of 742, and
the shrink-only waiver ratchet (ADR-0.0.73 BI#8, `baseline_count: 6`) forbids
adding a seventh entry. Measured growth was 1859 → 2600 over 88 days (~8.4
lines/day), so +400 buys roughly 47 days. The 400-line yellow-band width is
preserved from both prior generations.

**The 6-month recalibration cadence was explicitly overridden**, 42 days after
the 2026-06-30 change, by the canon owner who also set the prior bands by
directive. The override is recorded rather than silent — which is the entire
function of the event this amendment now makes emittable. It is not a precedent
for silent adjustment; it is the first time the discipline has had a mechanism.

**Enforcement followed the producer, as its own cut (GHI #792).** Building the
emitter made compliance possible without making non-compliance detectable: the
band values rode on the event, and nothing read them back. `gz validate
--surface-weight` now fail-closes when the live constants disagree with the bands
on the most recent recalibration event. It compares STATE rather than detecting
an edit — a diff-watcher would need git awareness, would fire only at commit
time, and would be defeated by any path bypassing that hook, whereas
disagreement is a standing property checkable on a fresh clone or in CI. The
recovery is self-healing: `--recalibrate` emits an event carrying the current
constants, restoring agreement. Only the newest event binds; a superseded band
generation is history, not drift.

## Comparator Uplift (2026-05-07)

Competitors with polished workflows still depend on agents correctly reading
their loaded context. This ADR should treat comparator-inspired workflow
surfaces as fidelity-critical: if a borrowed workflow adds a section, marker,
role, or command promise to an agent-loaded surface, the fidelity validators
must prove the rendered surface preserves it and rejects partial mirrors.

## Anti-Patterns

What "wrong" looks like — explicit failure shapes the validators are built to
catch. Implementing agents must recognize these as defects, not as acceptable
shortcuts:

1. **Adding a `gz validate --<scope>` without wiring it into `--surface-fidelity`.** A
   narrow scope that lives outside the composite is invisible to `gz check`
   and to pre-commit; the four invariants are a set, not a menu. New scopes
   in this family MUST register into the composite at the same commit they
   land.
2. **Editing `AGENTS.md` or `CLAUDE.md` without re-running `--bullet-retention`.** A
   diet pass, lift-to-rationale, or reword that drops a Mechanical/Promotable
   bullet from the rendered surface is the GHI #327 regression class. The
   validator is the compile-time gate; agent goodwill is not.
3. **Recalibrating warning bands silently.** Adjusting the surface-weight
   green/yellow/red thresholds without an attested recalibration event
   reproduces the doctrine-drift failure the ADR exists to prevent. Band
   changes are ledger events, not config tweaks. **Mechanical since 2026-08-12
   (GHI #791 producer, GHI #792 witness):** emit the event with
   `gz validate --surface-weight --recalibrate`, and `gz validate
   --surface-weight` fail-closes when the live constants disagree with the bands
   recorded on the most recent event. Before that pair this clause was enforced
   by agent goodwill — the posture item 2 rejects by name — and it was violated
   on 2026-06-30 for 42 undetected days.
4. **Treating Era-1 advisory checks as optional.** Scenario reachability is
   advisory in Era 1 because the registry isn't authored yet — not because
   the invariant is soft. An orphan bullet warning that's ignored is a
   silently-failing bullet retention; the advisory mode exists for
   bootstrap, not for permanent dispensation.
5. **Lifting pedagogy without back-pointers.** `<!-- lifted-from: -->` is the
   reverse half of the pointer-integrity contract. Lifting prose to a
   rationale page without stamping the back-pointer breaks bidirectional
   trace and is the same class of failure as a broken `> See [...]` anchor.
6. **Bypassing pre-commit with `--no-verify`.** The cheap fidelity subset
   (invariants 1, 2, 3) is fast enough to run pre-commit precisely so the
   gate cannot be excused as friction. A `--no-verify` against a fidelity
   failure is a doctrine-drift event.

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| All four agent-control-surface fidelity invariants pass via the composite scope wired into gz check. | uv run gz validate --surface-fidelity | 0 |

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
- ~~Invariant 4 (scenario reachability) is advisory until ADR-0.0.34 lands
  the loading-scenarios registry. Era-1 fidelity is incomplete by design.~~
  **Superseded 2026-07-25:** ADR-0.0.34 landed `Validated` 8/8 without ever
  carrying the registry, so this deferral never discharged. Invariant 4 is
  retired rather than left pending — see § Amendment (2026-07-25).
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
| 0.0.33 | Completed | g0 | 2026-05-15 | Completed — attest completed — 5/5 OBPIs attested_completed; 27/27 REQs covered by 71 REQ-derived tests (spec-reviewer CLEAN, independent persona dispatch); quality-reviewer verdict COHERENT (composite is thin orchestrator, CLI dispatch uniform, Era-1/Era-2 contract honored); ARB receipts arb-ruff-49f51bb527354bc796e0f4baf769c6fa, arb-step-typecheck-3be8b030fa1c4b4d9029be8ac78c083d, arb-step-unittest-05c79d3dce8942148542f1c7a2da4062 (5087 tests), arb-step-mkdocs-9e42f8eac90c4506b2a0a535e6e48c9d all exit 0; in-flight fixes applied for Blocker A (fold-test BUCKET_3_ROOTS self-perpetuation) and Blocker B / GHI #473 (pointer_anchors + scenario_reachability exit-code drift) with 4 new GREEN tests pinning REQ-vs-runtime contract |
| Invariant 1 amendment (tier-scoped) | Attested | g0 | 2026-06-15 | Amends Invariant 1 to tier-scoped enforcement (§ Amendment 2026-06-03): invariant tier keeps the verbatim contract; compressible tier satisfies retention by a valid advisor-QC receipt + operator attestation, not verbatim substring. Realized by OBPI-0.0.37-25 (the `--bullet-retention` whole-surface-grep → tier-aware flip), landed in the same commit-window, staying wired into `--surface-fidelity` / `gz check` (Anti-Pattern #1). Attested at OBPI-0.0.37-25's Gate 5 — attestation text + ARB receipt IDs recorded in OBPI-0.0.37-25's completion receipt and Gate-5 evidence. |
