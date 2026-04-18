---
id: ADR-0.0.17-adr-taxonomy-mechanical
status: Draft
semver: 0.0.17
lane: heavy
parent: GHI-218
date: 2026-04-18
kind: foundation
---

# ADR-0.0.17: ADR Taxonomy — pool / foundation / feature (Mechanical)

## Persona

**Active persona:** `main-session` — craftsperson who treats governance vocabulary as a first-class artifact, refuses to encode a concept in semver ranges alone, and insists that every named kind be mechanically validatable so an adopter reading CLI help can learn the full contract without reading prose doctrine.

This ADR is a Foundation addition. Foundations are app/system invariants and identity-shaping facts, conditions, concepts, and semantics — and "what kind of ADR am I writing" is exactly that. The companion ADR-0.0.18 lands the operator doctrine; this ADR lands the mechanical enforcement so the doctrine has a schema to refer to.

## Intent

gzkit's ADR model has three conceptual kinds but only one is first-class. **Pool** is named and has CLI support (`ADR-pool.<slug>`, `gz adr promote`). **Foundation** is implicit — encoded by `0.0.x` semver convention and documented only in `AGENTS.md:194–217`. **Feature** is unnamed anywhere in the CLI, skills, schemas, or scaffolded governance docs. Adopters cannot unambiguously describe their ADRs, and `gz plan create` has no `--kind` parameter to express intent at authoring time. Reported by the RHEA adopter as GZKIT-BOOTSTRAP-009 (GHI #218); RHEA paused bootstrap at end of Session 3 rather than commit ADR-001 in a vocabulary vacuum.

**After this ADR**: `kind: {pool, foundation, feature}` is a required frontmatter field on every non-pool ADR (pool keeps its existing `ADR-pool.<slug>` id convention as its kind marker). `gz plan create --kind {pool,foundation,feature}` scaffolds the correct shape. `gz validate --documents` rejects a missing or invalid `kind`. `gz validate --taxonomy` (new scope) enforces kind/semver consistency: foundation ⇒ `0.0.x`, feature ⇒ non-`0.0.x`, pool ⇒ no semver. Existing ADRs are backfilled in a one-time pass shipped with OBPI-05. `AGENTS.md` is corrected to document kind and lane as orthogonal axes.

## Decision

Build the taxonomy as a typed frontmatter field + CLI + validator triple, not as a convention layered over semver ranges. This follows the ADR-0.0.6 / ADR-0.0.7 exemplar pattern (Foundation ADRs that added a `gz validate` check to mechanically enforce an architectural invariant declared elsewhere in canon).

**Key axis decisions (locked with operator, 2026-04-18):**

1. **`kind` and `lane` are orthogonal.** Kind describes *what the ADR is about*:
   - **Pool**: storage/waiting area for backlog items. No semver, no lane.
   - **Foundation**: app/system invariants and identity-shaping facts, conditions, concepts, and semantics. Always `0.0.x`. Adding a foundation never impacts release versioning.
   - **Feature**: active/committed (or queued) capability. Carries release-impacting semver (`0.y.z` and up).

   Lane describes *external-contract exposure*: heavy if the ADR changes an external contract, lite otherwise. Any kind can be any lane. A foundation ADR may be lite (pure doctrine) or heavy (doctrine that ships enforcement touching external contracts). A feature ADR may be lite (internal capability) or heavy (public CLI surface). Pool ADRs have no lane until promoted.

2. **`AGENTS.md:214` is wrong in its current shape.** It treats "Heavy/Foundation" as a single attestation bucket, conflating the two axes. The correction is part of this ADR (OBPI-06). Attestation rigor attaches to lane, not kind.

3. **Pool kind derives from id prefix, not frontmatter.** `ADR-pool.*` is already the live identifier convention. Rather than duplicate it in `kind: pool` frontmatter, the validator derives pool kind from the id. Non-pool ADRs carry `kind: foundation` or `kind: feature` in frontmatter.

**Six OBPIs decompose the decision:**

**OBPI-01 — Schema + model.** Add `kind` to `src/gzkit/schemas/adr.json` as an enum `{foundation, feature}` (pool is id-derived). Extend `AdrFrontmatter` Pydantic model with the new field. Update `SCHEMA_TO_MODEL` alignment test to cover the new enum. Cross-validation tests lock schema ↔ model parity. **Parallel-root: no predecessor.**

**OBPI-02 — `--kind` on `gz plan create`.** Add `--kind {pool, foundation, feature}` flag with no default (operator must choose; a default would re-encode the silent convention this ADR exists to eliminate). Scaffolder emits the correct `kind:` frontmatter. Scaffolder validates kind/semver consistency at authoring time (refuses to write a feature ADR at `0.0.x` or a foundation ADR at non-`0.0.x`) with a recovery message naming the correct combination. **Depends on OBPI-01.**

**OBPI-03 — `--kind` on `gz adr promote`.** Pool promotion expresses intent at promotion time: `gz adr promote ADR-pool.<slug> --kind {foundation, feature} --semver X.Y.Z`. Promotion writes the correct `kind:` into the promoted ADR's frontmatter and validates kind/semver consistency. Error paths preserve the pool file unmodified. **Depends on OBPI-01.**

**OBPI-04 — `gz validate --taxonomy` scope.** New validate scope enforces:
- Every non-pool ADR has a `kind:` field.
- `kind: foundation` ⇒ semver matches `^0\.0\.\d+$`.
- `kind: feature` ⇒ semver does NOT match `^0\.0\.\d+$`.
- Pool ADRs (id prefix `ADR-pool.`) have no `kind` and no `semver`.

Registered as both a default-scope check (runs under `gz validate` with no flags) and a discrete `--taxonomy` flag for targeted invocation. **Depends on OBPI-01.**

**OBPI-05 — Backfill + round-trip test.** One-time backfill pass that reads every existing ADR under `docs/design/adr/foundation/` and `docs/design/adr/pre-release/`, inspects the semver, and writes `kind: foundation` (for `0.0.x`) or `kind: feature` (for the rest) into the frontmatter. Round-trip test asserts `gz plan create … --kind X` produces a file that `gz validate --documents --taxonomy` accepts with zero errors (the exact pattern from GHI #186 / #216). **Depends on OBPI-01, OBPI-02, OBPI-04.**

**OBPI-06 — AGENTS.md correction + release notes.** Correct `AGENTS.md:194–217` to document `kind` and `lane` as orthogonal; remove the "Heavy/Foundation" bucketing; document the four-combo matrix. Cross-link to ADR-0.0.18 (doctrine) for the operator-facing decision guidance. Update `docs/user/commands/plan.md` and any other surfaces referencing foundation implicitly. **Depends on all prior OBPIs.**

**Scope boundary — what this ADR explicitly does NOT do:**
- Does NOT author operator doctrine (PRD→ADR derivation guidance, pool curation, epic grouping). Those are ADR-0.0.18.
- Does NOT add `kind: pool` to pool ADR frontmatter. The id-prefix convention is already the marker; duplicating it in frontmatter invites drift.
- Does NOT introduce `epic:` frontmatter or epic-grouped CLI surfaces. Epic grouping lives in ADR-0.0.18 because the naming convention and curation policy are doctrine-driven.
- Does NOT renumber or restructure existing ADRs. Backfill is frontmatter-only.
- Does NOT remove `semver`/`lane` fields from pool ADR frontmatter if present — pool ADRs may carry hint fields for future promotion, but the taxonomy validator only enforces the presence/absence rules above.

**Forcing-function stress tests applied during design:**

- **Pre-mortem:** 18 months out, failure modes include operators fighting the no-default `--kind` flag ("let me just put `--kind feature` because it's the common case"), foundation ADRs proliferating (0.0.17, 0.0.18, 0.0.19 in one week) because the lower bar tempts under-documented decisions, the taxonomy validator becoming a friction tax with no enforcement teeth, and `kind` drifting from the actual ADR content (a doctrine ADR tagged `kind: feature` because the operator wanted a release bump). Mitigations: no default kind (force explicit choice); kind/semver mechanical binding; `--kind foundation` requires semver match; ADR-0.0.18 ships the operator guidance to reduce accidental foundations.
- **WWHTBT:** Schema enum stable (holds — {foundation, feature} with pool id-derived is the operator-agreed taxonomy); Pydantic + JSON schema alignment mechanical (holds — `test_schemas.py` locks it); CLI flag naming consistent with `--lane` (holds); backfill semantics decidable from semver alone (holds for every existing ADR — `0.0.x` ⇒ foundation, else feature); adopters reach for `--kind` after reading `--help` (shaky — depends on ADR-0.0.18 publishing the doctrine).
- **Constraint archaeology:** Pool id convention `ADR-pool.<slug>` is load-bearing and recent (`.gzkit/rules/constraints.md § Architectural Boundaries`, rule 1-2). Foundation convention `0.0.x` is live in `AGENTS.md:196, 214, 217` but informal. No prior mechanical enforcement of either. GHI #208 (pool-adr-isolation audit) is the closest precedent — it enforces pool ADR isolation from runtime-track events but does not enforce the `kind` concept.
- **Assumption surfacing:** Every ADR fits cleanly into one of three kinds (FALSE edge cases: ADRs that are *about* the taxonomy itself — this one — are mildly recursive; ADRs that document cross-cutting policy without a single invariant — rare, handled as feature with appropriate semver). Semver alone determines foundation (TRUE under current convention). `kind` is user-visible and edit-safe (TRUE — it's frontmatter, not derived).
- **2am operator:** Error messages name the recovery command. Missing `kind` → "add `kind: foundation` if this ADR codifies an app/system invariant; `kind: feature` if it scopes a capability. See `docs/user/concepts/adr-taxonomy.md`." Kind/semver mismatch → "foundation ADRs carry `0.0.x` semver (next available: `0.0.19`); feature ADRs carry `0.y.z` and up." No prose dispatch — every error cites a concrete next step.
- **Reversibility:** Fully reversible. Schema can shed the field (no downstream consumer locks it in hard), CLI flag can be removed, validator scope can be disabled. The backfill is one-way in cultural terms (the decision that ADR-0.0.9 is `kind: foundation` is now mechanical, not folk knowledge) but the field itself is hand-editable.
- **Scope minimization:** Floor is OBPI-01 (schema) + OBPI-02 (CLI) + OBPI-04 (validator) + OBPI-05 (backfill). OBPI-03 (promote) and OBPI-06 (AGENTS.md) are high-value but can ship in a follow-on patch if time pressure demands. Under extreme pressure, OBPI-01 + OBPI-05 alone satisfies the RHEA round-trip requirement — adopters can hand-edit `kind:` until the CLI lands.

**Downstream decisions forced by this ADR:**
1. ADR-0.0.18 lands the operator doctrine (runbook, PRD→ADR derivation, pool curation, epic grouping). ADR-0.0.18's decisions are informed by this ADR's mechanical vocabulary.
2. `gz-adr-create` and `gz-plan` skills will need updating to prompt for `--kind` in their interviews (follow-on, tracked in ADR-0.0.18).
3. The `--taxonomy` audit joins the advisory-rules-audit scorecard (`docs/governance/advisory-rules-audit.md`) as a promoted mechanical rule.
4. Pool ADRs that never got a foundation/feature designation remain in the pool — no promotion is forced by this ADR. Pool curation policy lives in ADR-0.0.18.

## Consequences

### Positive

1. Adopter vocabulary is complete — RHEA (and every future adopter) can reason about "what kind of ADR am I writing" by reading CLI help.
2. Foundation vs feature is mechanically enforced — no more `AGENTS.md` readers inferring conventions from semver ranges.
3. Round-trip contract is locked — every scaffolded ADR passes its own validator on first creation, same shape as the PRD fix (GHI #186) and constitution fix (GHI #216).
4. `AGENTS.md` correction removes a live doctrine ambiguity — kind and lane become orthogonal in operator-facing prose, not just in this ADR.
5. Backfill is mechanical — one-time pass writes `kind:` into every existing ADR from the semver signal, no operator per-file review needed.
6. Scorecard moves another rule from advisory to mechanical — `--taxonomy` joins `--version-release`, `--utf8-prefix`, `--test-tiers`, etc.

### Negative

1. New frontmatter field expands schema surface — every ADR scaffolder invocation now has to emit `kind:`; every schema consumer must handle the new field. Mitigation: Pydantic model extension + cross-validation test locks drift at test time.
2. No-default `--kind` flag increases authoring friction — operator must choose explicitly. Mitigation: doctrine ADR-0.0.18 ships the decision guidance so the choice is informed, not arbitrary; CLI error message names both options with concrete criteria.
3. Backfill is a sticky one-way classification — once every existing ADR is tagged `kind: foundation` or `kind: feature` from semver, reclassifying requires operator judgment. Mitigation: semver convention is already load-bearing; backfill formalizes existing classification, doesn't invent it.
4. Taxonomy validator is new failure mode at gate time — a gate run that passed yesterday may fail today if a hand-edited frontmatter violates kind/semver consistency. Mitigation: error message names the recovery command; backfill clears all existing violations before the gate lands.
5. Risk of taxonomy bikeshed during review — operators may propose renaming "feature" mid-implementation. Mitigation: operator locked the vocabulary 2026-04-18 (see GHI #218); any renaming is a new ADR.
6. Pool ADR kind remains id-derived, not frontmatter-derived — adopters reading a pool ADR frontmatter won't see `kind: pool`. Mitigation: ADR-0.0.18 doctrine documents this; the id prefix is already the canonical marker.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->

- Data/State: 1
- Logic/Engine: 1
- Interface: 2
- Observability: 1
- Lineage: 1
- Dimension Total: 6
- Baseline Range: 4-5
- Baseline Selected: 6
- Split Single-Narrative: 0
- Split Surface-Boundary: 1
- Split State-Anchor: 0
- Split Testability-Ceiling: 0
- Final Target OBPI Count: 6

Rationale: baseline of 5 plus a surface-boundary split (schema surface + CLI surface + validator surface + doctrine-correction surface are four distinct surfaces, with the AGENTS.md correction warranting its own OBPI boundary to preserve the doctrine-vs-code separation this ADR cares about).

## Checklist

- [ ] OBPI-0.0.17-01 — Schema + Pydantic model + cross-validation test
- [ ] OBPI-0.0.17-02 — `gz plan create --kind` CLI flag + scaffolder
- [ ] OBPI-0.0.17-03 — `gz adr promote --kind` CLI flag + promotion validation
- [ ] OBPI-0.0.17-04 — `gz validate --taxonomy` scope + default-scope registration
- [ ] OBPI-0.0.17-05 — Backfill existing ADRs + round-trip test
- [ ] OBPI-0.0.17-06 — AGENTS.md correction + docs/user alignment

## Evidence

Evidence accumulates in `audit/proofs/` as OBPIs complete. Expected artifacts:

- Schema cross-validation test output (`tests/test_schemas.py`)
- `gz plan create --kind foundation --semver 0.0.19 --lane lite` transcript + scaffolded file
- `gz validate --taxonomy` clean run across backfilled tree
- Round-trip test output (scaffolder → validator zero errors)
- Backfill receipt (per-file diff of added `kind:` field)

## Attestation Block

- Scope: ADR-0.0.17 mechanical taxonomy
- Lane: heavy
- Date attested: pending
- Attestor: pending
- Notes: pending
