---
id: ADR-0.0.42-storybook-doctrine
status: Draft
kind: foundation
semver: 0.0.42
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-05-10
---

# ADR-0.0.42-storybook-doctrine: Storybook Doctrine

## Persona

`main-session` — craftsperson, governance-aware, whole-file-reasoning, direct.
This ADR introduces a value-narrative surface companion to the runbook; the
agent who advances it must respect the Layer-3/Layer-1 separation as
identity-shaping (the deriver refreshes anchors, never narrative; the validator
catches drift but never authors prose) and treat the storybook's gap-detection
as a first-class output, not a side effect. Anti-vibing mantra applies:
narrative authoring is human judgment, never LLM-paraphrase of frontmatter;
the smallest-vibing-surface framing decides every authoring choice.

## Why foundation tier?

Without this ADR, storybook artifacts are honor-system — scenario narratives drift from CLI behavior without a validator to catch the divergence, and the storybook surface accumulates aspirational prose instead of runnable demonstrations.

This ADR authors a port: the storybook doctrine and validator contract (scenarios bind to executable verbs) every story authoring surface must honor.

## Intent

gzkit operators have manpages (CLI verb contracts), a runbook (procedural workflow), and 73 ADRs (decision records), but no surface that narrates the value-flow that emerges when these compose. A downstream consumer governing their own product with gzkit cannot see end-to-end value without synthesizing the entire artifact graph themselves. The graph is rich; the value-narrative layer is absent. Worse, there is no mechanical signal when the artifact graph drifts away from any coherent operator-facing model — cohesion failure is invisible until someone notices the system no longer composes. Three real cohesion gaps surfaced during a single strawman authoring exercise (filed as GHI #428, #429, #430), demonstrating that the gap-detection mechanic works before any doctrine even lands. This ADR codifies the Storybook as a value-narrative companion to the runbook for downstream gzkit consumers, with built-in cohesion-failure signaling as a second-order benefit.

## Decision

Introduce a Storybook doctrine — a hybrid Layer-3-derived / Layer-1-authored narrative surface at `docs/user/storybook/`. Three arc types (`journey`, `capability-bundle`, `capability-family`) carry different narrative shapes over a constant skeleton (audience claim + Layer-3 anchors + Layer-1 narrative + WIP dependencies + filed-GHIs gaps + provenance footer).

**Layer separation discipline.** A `gz storybook derive` command refreshes the Layer-3 anchor block bounded by `<!-- BEGIN ANCHOR BLOCK -->` ... `<!-- END ANCHOR BLOCK -->` HTML markers but never touches the Layer-1 narrative. The deriver reads ADR title/status from on-disk ADR frontmatter directly (one Layer-1 hop) — never from `docs/governance/GovZero/adr-status.md` (which is itself Layer 3, would chain derived-on-derived staleness). Per-ADR `STORY.md` stubs live co-located inside the ADR package directory and are scaffolded by `gz-adr-create`. Pool ADRs are exempt from STORY.md (pool stubs already capture intent at value-claim altitude).

**Validators and CLI surface.** `gz validate --storybook-fresh` fails closed on (a) stale anchor block, (b) missing per-ADR STORY.md (non-pool only), (c) missing or invalid `arc-type` frontmatter; wired into `gz check`. CLI surface: `gz storybook list/show/derive/new`. v0/v1 split named in OBPI-02: `derive --arc <slug>` and `list` are v0; `show`, `new`, `--dry-run`, `--all`, `--accept-stale-storybook` are v1 and may defer if scope pressure surfaces.

**Operator-invoked refresh discipline.** `derive` is operator-invoked, never auto-derived on commit; silent derive runs would hide the cohesion-failure signal the doctrine exists to surface. Cohesion-failure during derivation surfaces as candidate GHIs — the storybook is designed to keep generating gap signals.

**2am operator affordances** (added during interview Tier 2.5): `--accept-stale-storybook <slug> --accept-stale-reason <REASON>` bypass with ledger event `storybook_freshness_waived`; deriver error format names arc + anchor + recovery path; `gz storybook status` diagnoses what changed since last derive; `gz storybook validate --arc <slug>` separates structural validation from freshness; atomic write-temp-then-rename for deriver; `gz adr create --skip-story-scaffold` emergency flag with ledger event `story_scaffold_skipped`.

**Architectural posture: emergence-guided.** The pre-mortem surfaced eight plausible failure modes (authoring abandonment, STORY.md fatigue, derive/narrative race, cohesion-as-noise, arc-type proliferation, Layer-3/Layer-1 boundary erosion, wrong audience, doctrine-vs-tooling drift). Rather than pre-engineering against each, this doctrine commits to letting emergence guide — the storybook itself is a drift-detection mechanism, and responses to surfaced drift are themselves part of the design's iterative scope.

**OBPI decomposition (4 briefs co-created):**

- OBPI-0.0.42-01 — Doctrine + directory contract + initial canon. Lands `docs/user/storybook/` shape, `arc-type` frontmatter schema, three template skeletons, revises strawman to match doctrine, authors a second arc (capability-bundle on the receipts capability: `gz arb` + ledger + ADR-0.0.24 + attestation matrix) as load-test for the bundle template — *authored fresh against locked doctrine, not co-evolved* (mitigates Assumption E survivorship-bias risk surfaced at Tier 2.4). Adds runbook cross-link.
- OBPI-0.0.42-02 — `gz storybook` CLI surface. Implements `list`/`show`/`derive`/`new` verbs; emits `storybook_derived` ledger events; v0 minimum is `derive --arc <slug>` + `list`; remainder may defer.
- OBPI-0.0.42-03 — `gz validate --storybook-fresh` validator + `gz storybook validate --arc` structural validator. Wires into `gz check`.
- OBPI-0.0.42-04 — `gz-adr-create` integration: per-ADR `STORY.md` stub scaffolding co-located inside ADR package directory; `--skip-story-scaffold` emergency flag.

**Lane: Heavy.** New CLI verbs, new validator scope, new directory contract, new schema, new `gz-adr-create` integration. Heavy by AGENTS.md definition.

**Kind: Foundation.** Adds an identity-shaping doctrine about how value is narrated, how derive-vs-author authority composes, how cohesion drift is detected. Identity-shaping per ADR-0.0.18.

**Sensitivity: absent.** No security surface.

**Reversibility:** two-way door. Most surfaces additive (CLI, validator, schema, directory). Single door-jamb is per-ADR STORY.md proliferation; reversal is 1 retirement ADR + 1 cleanup OBPI + scripted stub removal (~2 days at current ~73-ADR scale).

## Fidelity Assertions

<!-- Runnable commands that exercise this ADR's thesis against the real system.
     `gz adr fidelity <ADR-ID>` runs each row and compares observed vs expected exit. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| WEAK: the named gz validate --storybook-fresh validator and the gz storybook verb are unlanded (ADR is Draft); the sibling Layer-3 derived-view freshness gate this doctrine parallels holds green. | uv run gz validate --adr-status-fresh | 0 |

## Consequences

### Positive

1. Downstream gzkit consumers gain a value-narrative entry point distinct from procedural runbook and CLI manpages. The storybook tells operators *why* the chain of decisions matters, not just *what* each verb does.
2. Cohesion drift between artifact graph and operator-facing model becomes a mechanical signal (validator failure, missing STORY.md, candidate GHIs surfaced during derive). Three real gaps already filed (#428/#429/#430) demonstrate the gap-detection mechanic works before doctrine even lands.
3. Per-ADR STORY.md stubs accumulate raw material for arc authoring without forcing eager arc composition. The corpus grows organically as ADRs land.
4. Format supports linear journeys, capability bundles, and capability families — extensible by adding new `arc-type` enum values when justified (cross-cutting-concern arc-type reserved for future).
5. Layer-3/Layer-1 separation discipline is mechanically enforced via marker comments and validator scope. The deriver cannot silently mutate authored canon; the validator catches anchor staleness without touching narrative.
6. The 2am-operator affordances (bypass flag, error format, status command, structural validator, skip-flag) match gzkit's existing fail-closed-with-escape-hatches pattern (`--accept-uncovered`, `--dry-run`). Operational continuity preserved.
7. The strawman at `docs/user/storybook/from-init-to-first-attested-release.md` is already operator-reviewed and serves as canonical first-arc evidence the format produces real value (and surfaces real gaps).
8. Reversal cost is bounded (~2 days, scripted). Doctrine sits in the easier-to-reverse tier of foundation ADRs, allowing scope-evolution inside OBPI-01 without ceremony if the doctrine needs revision during load-test arc authoring.

### Negative

1. Adds a new documentation surface requiring authoring discipline. Layer-1 narrative is authored canon, not regenerable. Voice quality is operator-dependent — a weak storybook is worse than no storybook (LLM-paraphrase failure mode operator was explicit about avoiding).
2. Adds a new validator scope to `gz check` (small CI cost; meaningful failure modes when artifacts move).
3. `gz-adr-create` complexity grows — STORY.md stubs land alongside the ADR + closeout + OBPIs. New skill template integration.
4. Operator must remember to run `gz storybook derive` when anchored artifacts change; the validator catches drift but adds friction. Operator-invoked discipline is deliberate (silent auto-derive would hide cohesion-failure signal) but is real recurring cost.
5. Per-ADR STORY.md may become forcing-function fatigue. Risk of tokenistic stubs if every ADR demands meaningful value-claim content. Mitigation: stubs are short (100–200-word hint, soft constraint not validator-enforced) and value-claim-shaped, not full narratives. Plumbing-class ADRs may use "plumbing for capability X, see [arc-X]" stub shape per Assumption B.
6. Format relies on operator-chosen anchors. A poorly-anchored arc will not be flagged by the validator — only operator review during `derive` catches misalignment between anchors and narrative.
7. **Architectural posture commitment: emergence-guided.** Rather than pre-engineering against the eight plausible failure modes surfaced in the pre-mortem, this doctrine commits to responding to drift as it surfaces. Cost: some failure modes will land before mitigation is built. Benefit: avoids over-engineering against imagined failure modes that may not materialize.
8. **Strawman-fits-doctrine fallback (Tier 2.3 Constraint #11):** If the strawman fundamentally doesn't fit final doctrine, archive it (`docs/user/storybook/archive/`) and author a fresh first arc. Don't force a poor fit. OBPI-01 must surface this option if the revision proves intractable.
9. **Survivorship-bias risk (Assumption E):** The strawman was authored knowing the doctrine being built. The second arc (OBPI-01 capability-bundle) is the real format-survival test — must be authored against locked doctrine, not co-evolved. Author selection: agent drafts, operator reviews, per Operator Economy doctrine.
10. **Forced downstream commitments:** PRD-GZKIT-1.0.0 amendment (small) to acknowledge the storybook surface; eventual reconciliation with `ADR-pool.universal-agent-onboarding` when promoted (overlap on first-time-using-gzkit surface); eventual capability-family registry when corpus warrants.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 1
- Logic/Engine: 2
- Interface: 2
- Observability: 1
- Lineage: 1
- Dimension Total: 7
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 4

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.42-01: Doctrine + directory contract + initial canon — Lands `docs/user/storybook/` shape, `arc-type` frontmatter schema, three template skeletons (journey, capability-bundle, capability-family), revises strawman to match doctrine, authors second arc fresh (capability-bundle on receipts capability), adds runbook cross-link.
- [ ] OBPI-0.0.42-02: `gz storybook` CLI surface — Implements list/show/derive/new verbs with v0 minimum (`derive --arc` + `list`) and v1 deferrable surfaces (show, new, --dry-run, --all, --accept-stale-storybook). Emits `storybook_derived` ledger events.
- [ ] OBPI-0.0.42-03: `gz validate --storybook-fresh` + structural validator — Anchor staleness check + per-ADR STORY.md presence (non-pool only) + arc-type frontmatter validation. Separate `gz storybook validate --arc <slug>` for structural issues distinct from freshness. Wires into `gz check`.
- [ ] OBPI-0.0.42-04: `gz-adr-create` STORY.md scaffolding integration — Per-ADR STORY.md stub scaffolded inside ADR package directory at ADR creation time. Pool ADRs exempt. `--skip-story-scaffold` emergency flag with `story_scaffold_skipped` ledger event.

## Q&A Transcript

*Interview conducted: 2026-05-10. Full transcript captured in `adr-interview.json` (co-located with this ADR). Tier 2 forcing-function dialogue (pre-mortem, WWHTBT, constraint archaeology, assumption surfacing, 2am-operator, reversibility, scope minimization) is recorded in the parent session transcript and summarized in the Decision and Consequences sections above. The forcing functions surfaced the emergence-guided architectural posture (Negative consequence #7), the strawman-fallback (Negative #8), the survivorship-bias mitigation (Negative #9), the 2am operator affordances (Decision section), and the forced downstream commitments (Negative #10).*

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/storybook/`, `tests/cli/test_storybook.py`, `tests/governance/test_storybook_freshness.py`
- [ ] Docs: `docs/user/storybook/`, `docs/user/manpages/gz-storybook*`, `docs/user/runbook.md` (cross-link)
- [ ] Schema: `src/gzkit/schemas/storybook.json`
- [ ] Strawman: [docs/user/storybook/from-init-to-first-attested-release.md](../../../../user/storybook/from-init-to-first-attested-release.md) (becomes canonical first journey arc under OBPI-01)
- [ ] Surfaced gaps: [GHI #428](https://github.com/tvproductions/gzkit/issues/428), [GHI #429](https://github.com/tvproductions/gzkit/issues/429), [GHI #430](https://github.com/tvproductions/gzkit/issues/430)

## Alternatives Considered

1. **Layer-1-only authored canon (no derive step).** REJECTED: source corpus is 73 ADRs and 60+ skills; manual freshness is a maintenance trap. Operator was explicit during design dialogue: "definitely derived first." Surfacing during Tier 2.2 WWHTBT confirmed: even if titles are stable, statuses change frequently as ADRs cycle through Draft/Validated/Pending — manual maintenance becomes a per-arc burden every status transition.

2. **Layer-3-only fully-generated narrative.** REJECTED: value-claim extraction is non-trivial generation. An LLM paraphrase of frontmatter is exactly what the operator said the storybook should NOT be. Voice and value-claim altitude require human judgment. The hybrid Layer-3-anchors-plus-Layer-1-narrative split preserves human authorship of the parts that need it while automating the parts that don't.

3. **Single arc-type (linear-only).** REJECTED during design dialogue: bundles and families are non-linear and must compose. "Init to release" is naturally linear, but capability bundles (e.g., the receipts capability — `gz arb` + ledger + ADR-0.0.24 + attestation matrix) and capability families (e.g., agent-governance, evidence-binding) have no inherent ordering. Forcing linearity would either exclude these arc shapes or distort them into false sequences. Three-type enum (journey / capability-bundle / capability-family) covers the cases identified; reserved namespace for future cross-cutting-concern arc-type.

4. **Bury arc files inside ADR packages (no separate `docs/user/storybook/` directory).** REJECTED: arcs cross many ADRs by design; co-location forces an arbitrary primary-ADR assignment. Runbook-sibling positioning (`docs/user/runbook.md` ↔ `docs/user/storybook/`) would lose meaning. The per-ADR STORY.md stub IS co-located inside the ADR package, but full arcs live at the cross-ADR altitude.

5. **Auto-derive on commit (post-commit hook).** REJECTED: silent derive runs would hide the cohesion-failure signal we want surfaced loudly. The whole architectural value of the storybook's gap-detection mechanic depends on operator awareness when artifact-graph drift breaks an arc. Operator-invoked derive + fail-closed validator + 2am bypass-with-ledger-event preserves both gap-detection value and operational continuity. Surfaced explicitly as Pre-mortem failure mode F (Layer-3/Layer-1 boundary erosion) — auto-derive would be the on-ramp to that failure.

6. **Embed storybook narrative in PRD or constitution rather than separate surface.** Considered during Tier 2.4 Assumption Surfacing (Assumption G). REJECTED: PRD captures project-level intent; constitution captures invariants; runbook captures procedure; manpages capture verb contracts. Value-narrative across multiple decisions is genuinely a different altitude — embedding it in any existing surface conflates concerns. The storybook is positioned as runbook-sibling because both are operator-consumption surfaces (procedural vs narrative) at the same altitude.

7. **Defer the doctrine; iterate freely on the strawman as a one-off documentation artifact.** Considered. REJECTED: without doctrine, the strawman is a one-off and the format doesn't propagate. The cohesion-failure signal mechanic depends on more than one arc existing. Locking doctrine now lets the second arc (OBPI-01 receipts bundle) test format-generality with the doctrine as the contract.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.42 | Pending | | | |
