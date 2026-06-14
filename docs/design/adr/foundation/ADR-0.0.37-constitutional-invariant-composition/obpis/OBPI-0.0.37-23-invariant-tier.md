---
id: OBPI-0.0.37-23-invariant-tier
parent: ADR-0.0.37-constitutional-invariant-composition
item: 23
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit — one behavior/support
# surface apiece (policy accessor, verbatim-survival test, composer wiring, doc);
# none decomposes into parallel seq=02+ sub-tasks (ADR-0.0.64 exemption).
req_atomic:
  - REQ-0.0.37-23-01
  - REQ-0.0.37-23-02
  - REQ-0.0.37-23-03
  - REQ-0.0.37-23-04
---

# OBPI-0.0.37-23-invariant-tier: Invariant Tier (Verbatim, Never Condense)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #23 - "OBPI-0.0.37-23 — Invariant tier (verbatim, never condense) (`tier: invariant` entries emit verbatim at every setpoint; test asserts PRIME DIRECTIVE / DO IT RIGHT / NEVER PYTEST survive at the leanest setpoint; the 0-Kelvin floor made first-class)"

**Status:** Completed

## Objective

Make the **invariant tier the 0-Kelvin floor of the compression dial, first-class**. The corpus model (OBPI-18) already carries `tier: Literal["invariant", "compressible"]`, but presence enforcement is explicitly deferred — `Corpus.validate_against` notes *"Invariant-tier presence enforcement is OBPI-0.0.37-23."* This OBPI delivers that enforcement: a single shared `tier_policy` surface that the composer (OBPI-21) consumes so that `tier: invariant` entries are emitted **verbatim at every setpoint and never dropped, combined, or rewritten**, plus the canonical survival test asserting the named invariants (PRIME DIRECTIVE, DO IT RIGHT, NEVER PYTEST) survive verbatim at the **leanest** setpoint (`lite`).

The 0-Kelvin floor is the doctrinal analog of the immutable upstream system prompt the operator cannot edit (parent ADR § Decision Re-Alignment point 5): the dial thins only `compressible` content; invariant content is exact operator intent and is never condensed.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

This OBPI changes a runtime-contract behavior: which renditions are *valid* (an invariant-tier omission now fails closed). Foundation-kind brief-level Gate 5 attestation is mandatory (no self-close).

## Allowed Paths

- `src/gzkit/content/tier_policy.py` **CREATE** — the first-class invariant-tier policy: `invariant_entries(corpus)` (all `tier: invariant` rows) and `assert_invariant_verbatim(corpus, rendered_text)` (fail-closed when any invariant entry's text is absent/altered in the rendered/candidate text); stdlib + Pydantic, NO LLM. This is the single enforcement surface the composer (OBPI-21) consumes — see § Tracked Defects for the cross-OBPI wiring seam
- `tests/content/test_tier_policy.py` **CREATE** — BEHAVIOR tests for the policy accessor + the canonical named-invariant survival test + a composer-equivalent enforcement test (`@covers`)
- `src/gzkit/content/composer.py` — EDIT (operator-approved coupled-surface amendment 2026-06-14, § Tracked Defects path (b)): re-point the OBPI-21 composer off its inline invariant-floor check onto `tier_policy.assert_invariant_verbatim` / `tier_policy.invariant_entries` so REQ-03's centralized-enforcement / no-duplicated-inline-check contract holds
- `docs/governance/agent-control-surface-rendering-substrate.md` — EDIT: document the invariant-tier 0-Kelvin floor as a first-class guarantee (narrow subsection; the broader mechanism refresh is OBPI-27)
- `data/behave_coverage_waivers.json` — EDIT: OBPI-level behave-coverage waiver for the SUPPORT doc REQ (no Gherkin-observable behavior)
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-23-invariant-tier.md` — active brief and evidence record
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only, for intent and the 1:1 checklist sync)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/content/models/corpus.py` — the `tier` field already exists (OBPI-18); this OBPI enforces presence, it does NOT change the model
- `src/gzkit/content/vendors.py`, `src/gzkit/content/rendition_store.py`, the playback path — setpoint accessor (OBPI-20) and rendition/playback (OBPI-22) are consumed/coordinated, not modified here
- `src/gzkit/commands/content/compose.py` — the composer *command* surface is OBPI-21; this OBPI touches only the engine's enforcement seam
- Any LLM/network call — the policy is deterministic
- New runtime dependencies; CI files; lockfiles

## Creates These Files

Net-new paths this OBPI creates (exempt from the brief-path existence gate per GHI #419):

- `src/gzkit/content/tier_policy.py`
- `tests/content/test_tier_policy.py`

All other Allowed Paths reference existing files modified in place.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT [BEHAVIOR]: `tier_policy.invariant_entries(corpus)` MUST return exactly the corpus entries whose `tier == "invariant"`, and `tier_policy.assert_invariant_verbatim(corpus, rendered_text)` MUST raise (fail closed) when any invariant entry's `text` is absent from or altered in `rendered_text`, and return cleanly when all are present verbatim.
1. REQUIREMENT [BEHAVIOR]: Given a corpus carrying the canonical invariants (PRIME DIRECTIVE, DO IT RIGHT, NEVER PYTEST) as `tier: invariant` entries, when a rendition is produced at the **leanest** setpoint (`lite`), then all three texts survive verbatim — the 0-Kelvin floor holds at the most aggressive compression.
1. REQUIREMENT [BEHAVIOR]: `tier_policy` MUST be the single, composer-consumable enforcement surface — a test MUST demonstrate that a candidate rendition dropping/combining/rewriting an invariant-tier entry is rejected by the policy exactly as the composer's compression path would call it (centralized enforcement, no duplicated inline check).
1. REQUIREMENT [SUPPORT]: `docs/governance/agent-control-surface-rendering-substrate.md` MUST document the invariant-tier 0-Kelvin floor as a first-class guarantee — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the doc.
1. NEVER: weaken, special-case, or bypass the invariant-tier floor; introduce an LLM/network call into the policy; or modify the corpus model.
1. ALWAYS: reconcile the brief with the parent ADR (`uv run gz validate --brief-reconcile`) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The contract: "Invariant tier (verbatim, never condense) (`tier: invariant` entries emit verbatim at every setpoint; test asserts PRIME DIRECTIVE / DO IT RIGHT / NEVER PYTEST survive at the leanest setpoint; the 0-Kelvin floor made first-class)" (Checklist item #23; § Decision Re-Alignment 2026-06-03, point 5 "Invariant tier (0-Kelvin floor)").
- [ ] Parent ADR § Decision Re-Alignment point 5 — the verbatim-at-every-setpoint contract and the immutable-upstream-system-prompt analogy.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § PRIME DIRECTIVE, § DO IT RIGHT, § STDLIB-FIRST (forbid-pytest) — the verbatim invariant texts the survival test anchors against
- [ ] `.gzkit/rules/tests.md` — the `forbid-pytest` ("NEVER PYTEST") invariant source
- [ ] `.gzkit/rules/models.md` + `.gzkit/rules/tests.md` § "Tests assert semantics, not strings" — derive the survival assertion from the REQ, not from a render

**Context:**

- [ ] OBPI-0.0.37-18 (corpus model) — `CorpusEntry.tier` already exists; `Corpus.validate_against` defers invariant presence enforcement to this OBPI
- [ ] OBPI-0.0.37-21 (composer) — the consumer of `tier_policy`; this OBPI deepens 21's inline floor into the shared policy
- [ ] OBPI-0.0.37-25 (bullet-retention tier-scoped) — the validator that asserts verbatim presence on the invariant tier; coordinates with this policy
- [ ] OBPI-0.0.37-22 (playback) — playback also honors the invariant floor; coordinated, not modified here

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/content/models/corpus.py` exists with `CorpusEntry.tier` = `Literal["invariant", "compressible"]` (OBPI-18, attested-complete)
- [ ] `src/gzkit/content/corpus_store.py` exists with `load_corpus` (OBPI-19, attested-complete)
- [ ] `src/gzkit/content/vendors.py` exists with `SETPOINT_TOKENS` including `lite` (the leanest setpoint) (OBPI-20, attested-complete)
- [ ] `src/gzkit/content/composer.py` exists (OBPI-21) — its invariant-floor check is the seam this OBPI centralizes

**Existing Code (understand current state):**

- [ ] `src/gzkit/content/models/corpus.py` — the `tier`/`text` fields + `validate_against`'s deferral note
- [ ] `tests/content/test_corpus_store.py` + `tests/content/test_corpus_model.py` — the unittest + `tempfile` + `@covers` convention for content tests
- [ ] `src/gzkit/content/composer.py` (OBPI-21, if landed) — the consumer of `tier_policy`; review its invariant-floor seam for the wiring direction (see § Tracked Defects)
- [ ] `AGENTS.md` PRIME DIRECTIVE (lines ~31-46) + DO IT RIGHT (lines ~48-65) — the verbatim invariant texts the survival test references

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` documents the invariant-tier floor

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass / waived: REQ-01/02/03 are unit-proven engine behavior; REQ-04 is SUPPORT (doc). Behave coverage waived per the OBPI-level waiver (no Gherkin-observable CLI surface — this OBPI ships no new verb).

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (mandatory; foundation/heavy; no self-close)

## Verification

```bash
uv run gz validate --brief-reconcile
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI
test -f src/gzkit/content/tier_policy.py
uv run -m unittest tests.content.test_tier_policy -v
```

## Demo

```bash
# The named invariants survive verbatim at the leanest setpoint (0-Kelvin floor)
uv run -m unittest tests.content.test_tier_policy.TestInvariantSurvivesLeanestSetpoint -v

# The policy fails closed when an invariant entry would be dropped/rewritten
uv run python -c "from gzkit.content import tier_policy; help(tier_policy.assert_invariant_verbatim)"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-23-01 [BEHAVIOR]: Given a corpus with mixed-tier entries, when `tier_policy.invariant_entries` and `assert_invariant_verbatim` run, then the accessor returns exactly the `tier: invariant` rows and the assertion raises on any absent/altered invariant text and passes when all are verbatim. Proof: `@covers`-decorated test in `tests/content/test_tier_policy.py`.
- [ ] REQ-0.0.37-23-02 [BEHAVIOR]: Given a corpus carrying PRIME DIRECTIVE / DO IT RIGHT / NEVER PYTEST as `tier: invariant` entries, when a rendition is produced at the leanest setpoint (`lite`), then all three texts survive verbatim. Proof: `@covers`-decorated survival test.
- [ ] REQ-0.0.37-23-03 [BEHAVIOR]: Given a candidate rendition that drops/combines/rewrites an invariant-tier entry, when the shared `tier_policy` enforcement (the surface the composer consumes) is applied, then the candidate is rejected — proving centralized enforcement, not a duplicated inline check. Proof: `@covers`-decorated composer-equivalent enforcement test in `tests/content/test_tier_policy.py`.
- [ ] REQ-0.0.37-23-04 [SUPPORT]: Given the substrate doctrine doc, when the OBPI is complete, then `docs/governance/agent-control-surface-rendering-substrate.md` documents the invariant-tier 0-Kelvin floor as first-class — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the doc.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Behave waived for this OBPI — see Gate 4 above and data/behave_coverage_waivers.json
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


- `uv run -m unittest tests.content.test_tier_policy.TestInvariantSurvivesLeanestSetpoint -v` -> 5/5 pass; PRIME DIRECTIVE / DO IT RIGHT / NEVER PYTEST survive verbatim at the leanest setpoint (lite). The 0-Kelvin floor holds at the most aggressive compression and fails closed when an invariant would be dropped.
- Composer routing proven: TestComposerRoutesThroughPolicy.test_compose_invokes_shared_tier_policy patches gzkit.content.composer.assert_invariant_verbatim and asserts compose() invokes it (mock-verified centralized enforcement, no duplicated inline check).
- Full suite: 6149 pass, 1 skipped (receipt arb-step-unittest-a37f8b15eb97439299bd6f94703b08ec); ruff clean (arb-ruff-c581b13e929f45b3bd8c813f74433173); typecheck clean (arb-step-typecheck-834d31669bd74ce1bbe2557aa474b066); mkdocs --strict built (arb-step-mkdocs-2ca375107d814848b9b778490cb2b9c8); validate --documents passed (REQ-04 SUPPORT proof).

### Implementation Summary


- Files created: src/gzkit/content/tier_policy.py (single composer-consumable invariant-tier enforcement surface — invariant_entries + assert_invariant_verbatim; stdlib + Pydantic, no LLM); tests/content/test_tier_policy.py (18 @covers tests across 5 classes)
- Files modified: src/gzkit/content/composer.py (re-pointed onto tier_policy, duplicated inline check removed — operator-approved path b); docs/governance/agent-control-surface-rendering-substrate.md (0-Kelvin floor subsection); data/behave_coverage_waivers.json (OBPI-level waiver); brief (allowlist amendment + Tracked Defects resolution)
- Tests added: TestInvariantEntries, TestAssertInvariantVerbatim, TestInvariantSurvivesLeanestSetpoint, TestCentralizedEnforcement, TestComposerRoutesThroughPolicy
- Date completed: 2026-06-14
- Attestation status: operator-attested "attest completed" (Heavy/foundation Gate 5)
- Defects noted: 21<->23 wiring seam resolved via path (b) (operator-approved coupled-surface edit); corpus_store fixture-import false-positive eliminated by direct JSONL seeding

## Tracked Defects

**21 ↔ 23 enforcement-wiring seam (ADR sequencing tension, surfaced not silently owned).** The parent ADR sequences OBPI-21 (composer) before OBPI-23, yet says 21's invariant floor is *"deepened by OBPI-23."* `tier_policy` is the canonical floor; the composer (`src/gzkit/content/composer.py`, OBPI-21's create) must consume it. This brief deliberately does **not** list `composer.py` as an edit path — it does not exist at authoring time, and silently editing a sibling OBPI's create is the boundary-collision pattern Behavior Rule Always #9 forbids. Resolution to ratify at Stage 1 brief-reconcile: either (a) implement OBPI-23's `tier_policy` first so OBPI-21's composer imports it from the start, or (b) if OBPI-21 lands first with an inline check, the brief-reconcile pass when OBPI-23 lands re-points the composer to `tier_policy` as a coupled-surface edit. Either way the wiring is operator-sequenced, not assumed here.

**RESOLVED (2026-06-14, operator-approved path (b)).** OBPI-21 had landed first with an inline invariant-floor check at `src/gzkit/content/composer.py:53-62`, leaving two parallel enforcement implementations — a spec-review FAIL on REQ-03 ("no duplicated inline check"). Per the path-(b) resolution above, the operator approved adding `composer.py` to this brief's allowlist as a coupled-surface edit; the composer now imports and calls `tier_policy.assert_invariant_verbatim` / `tier_policy.invariant_entries`, and `tests/content/test_tier_policy.py::TestComposerRoutesThroughPolicy` proves the compression path routes through the shared policy (REQ-03 centralized enforcement). DO IT RIGHT 1a coupled-surface coherence satisfied in-commit. **23 ↔ 27 doc coupling:** this OBPI adds a narrow invariant-tier subsection to the substrate doc; OBPI-27 does the broader mechanism refresh of the same file. Both are sequenced edits to different subsections. Confirm both seams at Stage 1 brief-reconcile.

_No further defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.0.37-23: tier_policy is the single invariant-tier enforcement surface; the OBPI-21 composer re-pointed onto it (path b, operator-approved) removing the duplicated inline check; 18 @covers tests prove REQ-01/02/03 (incl. PRIME DIRECTIVE / DO IT RIGHT / NEVER PYTEST verbatim survival at the leanest setpoint) + REQ-04 SUPPORT doc; full suite 6149 pass (arb-step-unittest-a37f8b15eb97439299bd6f94703b08ec), ruff clean (arb-ruff-c581b13e929f45b3bd8c813f74433173), typecheck clean (arb-step-typecheck-834d31669bd74ce1bbe2557aa474b066), mkdocs strict (arb-step-mkdocs-2ca375107d814848b9b778490cb2b9c8), validate --documents passed, brief reconcile clean.
- Date: 2026-06-14

---

**Date Completed:** 2026-06-14

**Evidence Hash:** -
