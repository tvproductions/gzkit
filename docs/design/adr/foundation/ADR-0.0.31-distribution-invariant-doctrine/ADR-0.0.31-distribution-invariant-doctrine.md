---
id: ADR-0.0.31-distribution-invariant-doctrine
status: Validated
kind: foundation
semver: 0.0.31
lane: lite
parent:
date: 2026-04-25
---

# ADR-0.0.31-distribution-invariant-doctrine: Distribution Invariant (T0 Doctrine)

## Persona

Governance-aware craftsperson who treats the wheel as a contract surface, not
an artifact of the build system. Sees that "what an agent reads at runtime"
and "what `pip install` delivers to a fresh project" must be the same set,
and that any divergence is invariant drift, not a packaging convenience.
Writes doctrine that downstream invariants and audits can stand on without
re-litigating the premise.

## Intent

Codify a **T0 distribution invariant** in `docs/governance/trust-doctrine.md`
alongside the existing T1/T2/T3 layers. T0 governs the contract between the
wheel's package data and the canonical surfaces an operator receives from a
fresh `pip install py-gzkit && gz init`.

The invariant exists because gzkit develops itself against this repo's own
`.gzkit/` content (61 hand-authored skills, 14 hand-authored rules, plus
hooks/templates/personas), and the dogfood loop concealed for the entire
pre-1.0 cycle that none of that canonical content ships in the wheel. The
self-hosting blindness was surfaced 2026-04-25 by the first external
greenfield consumer (GHI #318): `pip install py-gzkit && gz init` in a
greenfield project produces zero rule files and one-line skill stubs that
bear no resemblance to the canonical content this repo uses to govern
itself. T0 names the class so future surface promotions cannot drift
silently again.

**Target state (testable).** A T0-passing build produces a wheel that, when
installed into a fresh venv and run through `gz init`, yields a project
whose canonical surfaces (skills, rules, hooks, templates, chores,
personas) are byte-equivalent — modulo path resolution and project-name
substitution — to a frozen baseline manifest derived from this repo's
`.gzkit/` content. The doctrine surface authored by this ADR makes that
contract citable; the mechanical enforcement (ADR-0.0.32) makes it
testable.

## Decision

**Architectural precedent.** This ADR follows the proven ADR-0.0.18
(taxonomy doctrine) ↔ ADR-0.0.17 (taxonomy mechanical enforcement) split:
doctrine authored as a foundation-kind invariant lands first as a stable
referent; mechanical enforcement lands as a sibling ADR that cites the
doctrine. T0 (this ADR) is the doctrine half; ADR-0.0.32 is the mechanical
half. The split's load-bearing precedent is that ADR-0.0.18 has stayed
stable across multiple ADR-0.0.17 evolutions of the taxonomy enforcement
surface, validating the doctrine/mechanics decoupling at this repo's scale.

Every canonical surface — skills, rules, hooks, templates, chores, personas
— MUST be reproducibly delivered by `pip install py-gzkit && gz init` to a
fresh project, byte-equivalent (modulo path resolution and project-name
substitution) to the package's authored canonical content. A wheel that
ships without a canonical surface is a T0 breach, regardless of whether
downstream `gz init` reports success.

T0 sits underneath the existing trust-doctrine layers:

| Layer | Authority | Question it answers |
|-------|-----------|---------------------|
| **T0** (this ADR) | Distribution | Does the wheel reproducibly deliver every canonical surface to a fresh `gz init`? |
| **T1** | Canon | What is the authored, source-controlled truth? |
| **T2** | Ledger | What event sequence has been witnessed? |
| **T3** | Derived | What does a current view assert? |

T0 is upstream of T1: if a canonical surface only exists in this repo's
`.gzkit/` and never ships, then T1 (canon-as-truth) is silently project-
specific instead of project-portable. That is the failure shape GHI #318
surfaced.

**Mechanical-enforcement contract.** This ADR authors doctrine only. The
mechanical surface that satisfies T0 — wheel package-data extension,
canonical-content-shipping scaffolders for skills/rules, `gz init --update`,
and the build-then-install smoke test — is owned by ADR-0.0.32 (canonical
surface packaging). T0 prescribes the contract any future enforcement layer
MUST satisfy:

1. A T0 audit MUST detect missing package data without depending on
   downstream installation evidence.
2. A T0 audit MUST distinguish "canonical surface authored but not shipped"
   (the GHI #318 class) from "canonical surface authored and shipped"
   (correct state) and from "no canonical surface authored" (out of scope —
   T0 governs *delivery* of authored canon, not authorship volume).
3. A T0-passing build MUST produce a wheel that, when installed into a fresh
   venv and run through `gz init`, yields a project whose canonical surfaces
   are byte-equivalent (modulo project-name substitution) to a frozen
   baseline manifest.

**Doctrine surface authored by this ADR:**

- The T0 paragraph in `docs/governance/trust-doctrine.md` alongside the
  T1/T2/T3 table.
- Cross-link from this ADR's text to the trust-doctrine layer table.
- Scorecard entry in `docs/governance/advisory-rules-audit.md` classifying
  T0 as **Promotable** (mechanical enforcement landed by ADR-0.0.32).
- Pointer text naming the failure mode: "a wheel that ships without a
  canonical surface is a T0 breach, regardless of whether downstream
  `gz init` reports success."

**What this ADR does NOT author:** mechanical changes of any kind. No
scaffolders, no `CORE_RULES` registry, no `pyproject.toml` `include:`
extension, no `--update` flag, no smoke test implementation, no
`gz validate --distribution` scope. ADR-0.0.32 owns every mechanical
deliverable. Splitting doctrine from mechanics lets this ADR stay stable
across many future packaging-surface evolutions, mirroring the same
split between ADR-0.0.18 (taxonomy doctrine) and ADR-0.0.17 (taxonomy
mechanical enforcement).

## Comparator Uplift (2026-05-07)

Multi-runtime frameworks such as GSD and Compound Engineering make portability a
product strength. This ADR should frame distribution as an invariant: every
generated surface, installed skill, and vendor mirror must prove which canonical
input produced it and which validation command can rebuild or reject it. Ported
workflow files that lack that proof are distribution drift, not parity.

## Consequences

### Positive

- Closes the self-hosting blindness gap that allowed the GHI #318 class to
  accumulate for the entire pre-1.0 development cycle without surfacing.
- Gives every future canonical-surface promotion (new skill kind, new rule
  family, new hook surface) a single, citable invariant to satisfy: "is it
  T0-compliant?"
- Provides the upstream invariant ADR-0.0.32 cites as its mechanical
  contract, mirroring the ADR-0.0.18 (doctrine) → ADR-0.0.17 (mechanics)
  split that has held cleanly across the taxonomy work.
- Foundation-kind brief-level Gate 5 attestation (per § Lane & Kind
  Attestation Matrix) gates this ADR's closeout on a human witness even on
  the lite lane, ensuring the doctrine framing lands deliberately.
- Surfaces a place to file future "self-hosting blindness" patterns. T0
  generalizes beyond skills/rules to any canonical surface where the
  in-repo content and the wheel content can drift.

### Negative

- Every new canonical surface now has a packaging obligation. Authoring a
  new rule family or skill kind means budgeting the wheel-include extension
  + scaffolder integration alongside the content authoring.
- T0 is currently advisory until ADR-0.0.32 lands the mechanical enforcement
  scope. The doctrine surface alone does not prevent another GHI #318-class
  failure; it names the class so the mechanical fix has a stable referent.
- Adds a fourth layer to the trust-doctrine vocabulary, which downstream
  documentation and skills will need to absorb and cite correctly. Drift
  risk is non-trivial during the transition.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 0
- Logic/Engine: 0
- Interface: 1
- Observability: 1
- Lineage: 1
- Dimension Total: 3
- Baseline Range: 1-2
- Baseline Selected: 2
- Split Single-Narrative: 1
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 1
- Final Target OBPI Count: 3

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.0.31-01: Author T0 doctrine paragraph in `docs/governance/trust-doctrine.md` (extend layer table from T1/T2/T3 to T0/T1/T2/T3, paragraph with verbatim failure-mode quote, forward-link to ADR-0.0.32, cross-link from this ADR's Evidence section)
- [ ] OBPI-0.0.31-02: Add T0 scorecard entry in `docs/governance/advisory-rules-audit.md` classifying as **Promotable**, citing ADR-0.0.32 as the tracking promotion ADR; reconcile with the existing Promotable→Mechanical promotion-tracking convention (e.g. how previous Promotable entries record the landing GHI/ADR for their mechanical enforcement)
- [ ] OBPI-0.0.31-03: Author `docs/governance/distribution_invariant_catalog.md` — the T0 failure-mode catalog with worked examples (GHI #318 self-hosting blindness, the chores promotion gap that ADR-0.0.21 implicitly closed before T0 was named, and the canonical "is this a T0 breach?" decision tree future canonical-surface promotions check against)

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Design content sourced from GHI #318 amendment authored by ahuimanu on
2026-04-25T14:00:48Z, "ADR-0.0.26 — Distribution Invariant (T0 doctrine)"
section. The amendment proposed slug ADR-0.0.26; that slug was reused by
unrelated foundation work (evaluation-feedback-loop-doctrine) between
amendment authoring and ADR creation, so this ADR is booked at the next
available foundation slug, ADR-0.0.31. No design intent changed in the
slug shift; the substantive scope is the amendment text.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [x] Doctrine: `docs/governance/trust-doctrine.md` — T0 paragraph and layer table added (OBPI-0.0.31-01); see `## Trust Layers` and `### T0 — Distribution Invariant` sections in that file
- [ ] Scorecard: `docs/governance/advisory-rules-audit.md` (T0 entry classified Promotable) — OBPI-0.0.31-02
- [x] Cross-link: this ADR's Evidence section links to `docs/governance/trust-doctrine.md` trust-doctrine layer table (OBPI-0.0.31-01); T0 paragraph in trust-doctrine.md back-links to this ADR via "Doctrine source" reference
- [ ] Catalog: `docs/governance/distribution_invariant_catalog.md` (T0 failure-mode catalog) — OBPI-0.0.31-03
- [ ] Tests: `tests/` (no mechanical test surface in this ADR; mechanical enforcement deferred to ADR-0.0.32)
- [ ] Docs: `docs/`

## Alternatives Considered

**A. Single ADR covering both doctrine and mechanics.** The amendment's
original sketch (an "ADR-0.0.26 distribution-invariant" combining the T0
text and the canonical-surface-packaging mechanics) was rejected because the
two concerns have different change cadences (doctrine stable, mechanics
evolves with each new canonical surface) and different attestation evidence
shapes (doctrine cross-links + scorecard entry; mechanics smoke-test pass +
wheel-content manifest test pass). Splitting them mirrors the proven
ADR-0.0.18 (taxonomy doctrine) ↔ ADR-0.0.17 (taxonomy mechanical) pattern.

**B. Define T0 inside `trust-doctrine.md` without a backing ADR.** Rejected
because the trust-doctrine layers are foundation-kind invariants and every
prior layer (T1/T2/T3) traces to a foundation ADR. T0 deserves the same
provenance for symmetry and for citable authority when the mechanical ADR
(0.0.32) needs to point at the invariant it is satisfying.

**C. Defer T0 until the mechanical fix proves out.** Rejected per the
operator's amendment sequencing: "ADR-0.0.26 (T0 doctrine) lands first.
Authoring + closeout. Doctrine surface stable. ADR-0.0.27 (mechanical
delivery) opens with ADR-0.0.26 as the cited invariant." Authoring
mechanics against a forward-referenced invariant inverts the doctrine →
mechanism dependency direction and is the failure pattern this whole split
exists to avoid.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.31 | Completed | Jeffry | 2026-05-10 | Completed |
