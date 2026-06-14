---
id: OBPI-0.0.37-22-committed-rendition-store-deterministic-playback
parent: ADR-0.0.37-constitutional-invariant-composition
item: 22
lane: Heavy
status: Completed
# req_atomic: each REQ is a single indivisible labor unit — one behavior/support
# surface apiece (store, playback, freshness gate, coherence-diff, build-wiring,
# docs); none decomposes into parallel seq=02+ sub-tasks (ADR-0.0.64 exemption).
req_atomic:
  - REQ-0.0.37-22-01
  - REQ-0.0.37-22-02
  - REQ-0.0.37-22-03
  - REQ-0.0.37-22-04
  - REQ-0.0.37-22-05
  - REQ-0.0.37-22-06
---

# OBPI-0.0.37-22-committed-rendition-store-deterministic-playback: Committed-Rendition Store + Deterministic Playback + Freshness Gate

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #22 - "OBPI-0.0.37-22 — Committed-rendition store + deterministic playback + freshness gate (durable rendition artifact per surface×consumer; `sync_agents_md` plays it back deterministically; build fail-closes on corpus↔rendition drift; `--invariant-coherence` diffs playback vs committed surface; re-homes prior OBPI-14 sync/compose plumbing)"

**Status:** Completed

## Objective

Deliver the **rendition + playback** stages of the re-aligned CMS pipeline (`corpus → compress → rendition → playback`): a durable **committed-rendition store** (one artifact per surface×consumer), **deterministic playback** that renders the rendered surfaces from the committed rendition with NO LLM in the path, and a **freshness gate** that fails the build closed when the corpus has drifted from the committed rendition. This is the determinism seam the parent ADR names (§ Decision Re-Alignment point 4): the non-deterministic compression (OBPI-21) happens at authoring time; the render path here is pure playback.

Concretely: (a) a committed-rendition store at `.gzkit/renditions/<surface>/<consumer>.md`; (b) `sync_agents_md` (re-homing OBPI-14's sync/compose plumbing) plays the committed rendition back to `AGENTS.md` and vendor mirrors deterministically; (c) a fail-closed freshness gate (`gz validate --rendition-freshness`, also in the `gz check` build) that detects corpus↔rendition drift and emits a `composition_drift_detected` ledger event with a recompose recovery hint; (d) `gz validate --invariant-coherence` is re-pointed to diff deterministic playback of the committed rendition against the committed rendered surface.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

A new `gz validate --rendition-freshness` scope, a re-pointed `--invariant-coherence` semantics, a new committed-rendition store contract, and a change to the `sync_agents_md` render path are all runtime-contract changes → Heavy. Gate 5 human attestation is mandatory (foundation/heavy; no self-close).

## Allowed Paths

- `src/gzkit/content/rendition_store.py` **CREATE** — committed-rendition persistence: `rendition_path(root, surface, consumer)` → `.gzkit/renditions/<surface>/<consumer>.md`; `load_rendition` / `save_rendition` / `rendition_exists`; deterministic, stdlib-only
- `src/gzkit/sync_surfaces.py` — EDIT: repoint `sync_agents_md` (lines ~352-381) to play back the committed rendition deterministically; retire the `render_template("agents")` monolith fallback path in favour of rendition playback (re-homes OBPI-14 plumbing)
- `src/gzkit/governance/compose.py` — EDIT: `render_agents_md` (lines ~51-72) becomes deterministic playback of the committed rendition (no template-substitution compose at the rendered location)
- `src/gzkit/governance/trust_audits/invariant_coherence.py` — EDIT: diff deterministic playback of the committed rendition against the committed rendered surface (replaces the registry-re-render byte-compare)
- `src/gzkit/governance/trust_audits/rendition_freshness.py` **CREATE** — the corpus↔rendition drift gate (mutation-timestamp comparison; fail-closed; recompose recovery hint)
- `src/gzkit/governance/trust_audits/__init__.py` — EDIT: export `validate_rendition_freshness` (re-export convention)
- `src/gzkit/cli/parser_maintenance.py` — EDIT: register the `--rendition-freshness` argparse flag (cf. `--invariant-coherence`, `--setpoint-coherence`)
- `src/gzkit/commands/validate_cmd.py` — EDIT: wire the `rendition_freshness` runner into the dispatch table + default-scope registry (cf. `_invariant_coherence_runner`)
- `src/gzkit/commands/quality.py` — EDIT: add the rendition-freshness gate to the `gz check` build steps (`_build_check_steps`)
- `src/gzkit/quality.py` — EDIT: add the `run_rendition_freshness_audit` runtime delegate that `_build_check_steps` imports from `gzkit.quality` (coupled producer surface; convention per `run_adr_status_fresh_audit` — every `run_*_audit` runner lives here. Allowlist amendment 2026-06-14, evaluator-attested: sibling briefs OBPI-0.0.68-02/0.0.69-03 declared this same path for the identical pattern)
- `src/gzkit/governance/events.py` — EDIT: add a typed read-path model for the rendition-drift/playback event if a new one is needed (reuse `CompositionDriftDetectedEvent` where the shape fits)
- `src/gzkit/ledger_events.py` — EDIT: add/extend the factory for the rendition-drift event (reuse `composition_drift_detected_event` where the shape fits)
- `src/gzkit/schemas/ledger.json` — EDIT: register any new event type with its required-fields schema (the REAL registry `gz validate --ledger` reads)
- `data/behave_coverage_waivers.json` — EDIT: OBPI-level behave-coverage waiver for any SUPPORT REQ with no Gherkin-observable behavior
- `tests/content/test_rendition_store.py` **CREATE** — store-level BEHAVIOR tests (`@covers`)
- `tests/governance/test_rendition_freshness.py` **CREATE** — freshness-gate BEHAVIOR tests (`@covers`)
- `tests/governance/test_invariant_coherence.py` — EDIT: update the coherence test to the playback-vs-committed-surface diff semantics
- `tests/commands/test_sync_cmds.py` — EDIT: update sync tests to the rendition-playback semantics
- `features/rendition_playback.feature` **CREATE** — Heavy-lane BDD scenarios tagged `@REQ-0.0.37-22-*`
- `features/steps/rendition_playback_steps.py` **CREATE** — step definitions
- `docs/user/manpages/validate.md` — EDIT: document the `--rendition-freshness` scope and the re-pointed `--invariant-coherence` semantics
- `docs/user/runbook.md` — EDIT: operator runbook entry for the recompose-on-drift flow
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-22-committed-rendition-store-deterministic-playback.md` — active brief and evidence record
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only, for intent and the 1:1 checklist sync)

## Denied Paths

- Paths not listed in Allowed Paths
- Any LLM / network call in the playback path — playback is deterministic (the load-bearing invariant of this OBPI)
- `src/gzkit/content/composer.py`, `src/gzkit/commands/content/compose.py` — the authoring-time compress stage is OBPI-21 scope
- `src/gzkit/content/models/corpus.py`, `src/gzkit/content/vendors.py` — corpus model + setpoint accessor are consumed read-only
- `AGENTS.md`, `CLAUDE.md`, mirrors — these are *written by playback*, never hand-edited (the substrate doctrine's binding claim)
- `.gzkit/ledger.jsonl` — never hand-edited
- New runtime dependencies; CI files; lockfiles

## Creates These Files

Net-new paths this OBPI creates (exempt from the brief-path existence gate per GHI #419):

- `src/gzkit/content/rendition_store.py`
- `src/gzkit/governance/trust_audits/rendition_freshness.py`
- `tests/content/test_rendition_store.py`
- `tests/governance/test_rendition_freshness.py`
- `features/rendition_playback.feature`
- `features/steps/rendition_playback_steps.py`
- `.gzkit/renditions/<surface>/<consumer>.md` (committed rendition artifact; the OBPI-26 interim is its seed — see § Open Implementation Decision)

All other Allowed Paths reference existing files modified in place.

## Open Implementation Decision (operator confirmation at Gate 5)

Two boundary choices are surfaced rather than resolved unilaterally (Behavior Rule Always #9):

- **(A) Committed-rendition store location.** Recommended: `.gzkit/renditions/<surface>/<consumer>.md` — project-level, parallels `.gzkit/corpus/<surface>.jsonl`, and makes the OBPI-26 interim (`docs/design/.../renditions/agentcontract-codex-root-interim.md`) the migration seed for `.gzkit/renditions/AGENTS.md/codex.md`. Alternative: keep renditions in the ADR package dir (ADR-scoped, weaker for production playback). **Recommend (A).**
- **(B) Freshness gate placement.** Recommended: a new dedicated `--rendition-freshness` scope added to the `gz check` build, with `--invariant-coherence` reserved for the playback-vs-committed-surface diff. Alternative: fold freshness into `--invariant-coherence`. **Recommend the dedicated scope** (single-responsibility validator modules, cf. OBPI-20).

Confirm or redirect at Gate 5 before the store layout and scope registration land.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT [BEHAVIOR]: A durable committed-rendition artifact MUST exist per `(surface × consumer)` at `.gzkit/renditions/<surface>/<consumer>.md`, and the rendition store module MUST load it deterministically (same file → same bytes) with a fail-closed error when the artifact is absent.
1. REQUIREMENT [BEHAVIOR]: `sync_agents_md` MUST render `AGENTS.md` (and the vendor mirrors) by deterministic playback of the committed rendition — NO LLM, NO network; an identical committed rendition MUST yield byte-identical rendered surfaces across runs.
1. REQUIREMENT [BEHAVIOR]: A fail-closed freshness gate MUST exit 3 when the corpus for a surface has mutated since its committed rendition (corpus↔rendition drift), with a recovery hint naming the recompose verb; it MUST exit 0 when corpus and committed rendition agree.
1. REQUIREMENT [BEHAVIOR]: `gz validate --invariant-coherence` MUST diff deterministic playback of the committed rendition against the committed rendered surface and exit 3 on drift (re-pointed from the registry-re-render byte-compare).
1. REQUIREMENT [SUPPORT]: The rendition-freshness gate MUST run in the default `gz check` build, and a drift MUST emit a `composition_drift_detected` ledger event — proven by `uv run gz validate --rendition-freshness` plus the `composition_drift_detected` event.
1. REQUIREMENT [SUPPORT]: `docs/user/manpages/validate.md` and `docs/user/runbook.md` MUST document the committed-rendition store, deterministic playback, and the freshness gate, and the references MUST resolve — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the doc surfaces.
1. NEVER: introduce an LLM/network call into the playback path, hand-edit a rendered surface, or hand-edit the ledger.
1. ALWAYS: reconcile the brief with the parent ADR (`uv run gz validate --brief-reconcile`) before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The contract: "Committed-rendition store + deterministic playback + freshness gate (durable rendition artifact per surface×consumer; `sync_agents_md` plays it back deterministically; build fail-closes on corpus↔rendition drift; `--invariant-coherence` diffs playback vs committed surface; re-homes prior OBPI-14 sync/compose plumbing)" (Checklist item #22; § Decision Re-Alignment 2026-06-03, point 4 "Deterministic playback").
- [ ] Parent ADR § Decision Re-Alignment "The binding pipeline" + "Recompose contract (build + on-demand + chore)" — the build-time freshness gate shape.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `docs/governance/state-doctrine.md` — Layer-3 derived views; AGENTS.md becomes a rendered (derived) surface
- [ ] `.claude/rules/governance-core.md` § "ADR status index regeneration" — the freshness-gate precedent shape (drift fail-closed, single-command recovery)
- [ ] `.gzkit/rules/cli.md` — exit-code map; new-scope (Heavy) requirements

**Context:**

- [ ] OBPI-0.0.37-21 (composer) — emits the *candidate* rendition this OBPI promotes/commits and plays back; the candidate↔committed boundary
- [ ] OBPI-0.0.37-19/20 — the corpus store + setpoint surfaces the freshness gate compares against
- [ ] OBPI-0.0.37-26 — the interim committed rendition that seeds the store
- [ ] OBPI-0.0.37-14 (withdrawn; attested-complete) — the sync/playback plumbing re-homed here

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/sync_surfaces.py` exists with `sync_agents_md` (the current render orchestrator)
- [ ] `src/gzkit/governance/compose.py` exists with `render_agents_md`
- [ ] `src/gzkit/governance/trust_audits/invariant_coherence.py` exists with `validate_invariant_coherence`
- [ ] `src/gzkit/commands/validate_cmd.py` + `src/gzkit/cli/parser_maintenance.py` expose the scope registration pattern (cf. `--setpoint-coherence`, OBPI-20)
- [ ] `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/agentcontract-codex-root-interim.md` exists (OBPI-26 seed)

**Existing Code (understand current state):**

- [ ] `src/gzkit/sync_surfaces.py` `sync_agents_md` (~352-381) — current render path + the `render_template("agents")` fallback to retire
- [ ] `src/gzkit/governance/compose.py` `render_agents_md` (~51-72) — the format_map→parse→render pipeline
- [ ] `src/gzkit/governance/trust_audits/invariant_coherence.py` — the current re-render byte-compare + `emit_composition_rendered`/`emit_composition_drift_detected` calls
- [ ] `src/gzkit/governance/trust_audits/reconcile.py` / `taxonomy.py` (`audit_adr_status_fresh`) — the freshness-gate precedents (mutation-timestamp comparison)
- [ ] `src/gzkit/commands/quality.py` `_build_check_steps` — where the freshness gate is added to `gz check`
- [ ] `src/gzkit/content/corpus_store.py` — `corpus_path`/`load_corpus` the freshness gate reads to detect drift

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
- [ ] `docs/user/manpages/validate.md` + `docs/user/runbook.md` updated; `gz validate --cli-alignment` resolves `--rendition-freshness`

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave --tags=@REQ-0.0.37-22-01,@REQ-0.0.37-22-02,@REQ-0.0.37-22-03,@REQ-0.0.37-22-04 features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (mandatory; foundation/heavy; no self-close)
- [ ] § Open Implementation Decision confirmed or redirected by operator

## Verification

```bash
uv run gz validate --brief-reconcile
uv run gz validate --rendition-freshness
uv run gz validate --invariant-coherence
uv run gz validate --documents
uv run gz validate --ledger
uv run gz validate --cli-alignment
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/rendition_playback.feature

# Specific verification for this OBPI
test -f src/gzkit/content/rendition_store.py
test -f src/gzkit/governance/trust_audits/rendition_freshness.py
uv run -m unittest tests.content.test_rendition_store -v
uv run -m unittest tests.governance.test_rendition_freshness -v
```

## Demo

```bash
# Playback renders AGENTS.md deterministically from the committed rendition (no LLM)
uv run gz agent sync control-surfaces
git diff --stat AGENTS.md

# Mutating the corpus without recomposing fails the build closed
uv run gz validate --rendition-freshness
# -> exit 3: "corpus drifted; run content compose <surface> and attest"

# Coherence diffs playback vs the committed surface
uv run gz validate --invariant-coherence
```

## Acceptance Criteria

- [ ] REQ-0.0.37-22-01 [BEHAVIOR]: Given a committed rendition at `.gzkit/renditions/<surface>/<consumer>.md`, when the rendition store loads it, then it returns byte-identical content across runs and fails closed when the artifact is absent. Proof: `@covers`-decorated test in `tests/content/test_rendition_store.py`.
- [ ] REQ-0.0.37-22-02 [BEHAVIOR]: Given a committed rendition, when `sync_agents_md` plays it back, then `AGENTS.md` (and mirrors) are produced by deterministic playback with no LLM/network call, and identical renditions yield byte-identical surfaces. Proof: `@covers`-decorated test in `tests/commands/test_sync_cmds.py`.
- [ ] REQ-0.0.37-22-03 [BEHAVIOR]: Given a corpus mutated after its committed rendition, when the freshness gate runs, then it exits 3 with a recompose recovery hint; given corpus and rendition agree, it exits 0. Proof: `@covers`-decorated test in `tests/governance/test_rendition_freshness.py`.
- [ ] REQ-0.0.37-22-04 [BEHAVIOR]: Given a committed rendition whose playback differs from the committed rendered surface, when `gz validate --invariant-coherence` runs, then it exits 3 on the playback-vs-surface diff. Proof: `@covers`-decorated test in `tests/governance/test_invariant_coherence.py`.
- [ ] REQ-0.0.37-22-05 [SUPPORT]: Given the build, when `gz check` runs and the corpus has drifted, then the rendition-freshness gate fires and a `composition_drift_detected` ledger event is emitted — proven by `uv run gz validate --rendition-freshness` plus the `composition_drift_detected` event.
- [ ] REQ-0.0.37-22-06 [SUPPORT]: Given the operator docs, when the OBPI is complete, then `docs/user/manpages/validate.md` and `docs/user/runbook.md` document the store, playback, and freshness gate and the references resolve — proven by `uv run gz validate --documents` plus the `artifact_edited` event for the docs.

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
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


Freshness gate fails closed on corpus drift; playback is deterministic:

$ uv run gz validate --rendition-freshness   # corpus newer than committed rendition
-> exit 3: "Corpus for 'AGENTS.md' has mutated after its committed rendition ('claude'). Run `gz content compose AGENTS.md` and attest to recompose."

$ uv run gz agent sync control-surfaces && git diff --stat AGENTS.md
-> (no diff — AGENTS.md byte-identical to committed rendition; deterministic playback, no LLM)

Receipts: arb-step-unittest-d459a288befe408fa5fa87dcd74d6e10 (6131/6131 pass), arb-ruff-a9d1d983fdd94f119b9c052b82b0ca49, arb-step-typecheck-040f8f8835f742778313409e9681e137, arb-step-mkdocs-35dc676c7f114aa3a39a302d093614d5. 8/8 BDD scenarios pass (@REQ-0.0.37-22-01..04); behavior_uncovered_reqs=0.

### Implementation Summary


- Committed-rendition store: src/gzkit/content/rendition_store.py provides rendition_path/load_rendition/save_rendition/rendition_exists over .gzkit/renditions/<surface>/<consumer>.md; deterministic, stdlib-only, fail-closed (FileNotFoundError) on absent artifact.
- Deterministic playback: sync_agents_md (sync_surfaces.py) and render_agents_md (compose.py) re-pointed to load committed rendition bytes verbatim — no LLM, no network. Template-model pipeline retained only as fresh-init bootstrap fallback.
- Freshness gate: src/gzkit/governance/trust_audits/rendition_freshness.py compares corpus mtime vs committed-rendition mtime; exits 3 + emits composition_drift_detected on drift; wired into gz check (_build_check_steps) and gz validate --rendition-freshness.
- --invariant-coherence re-pointed from registry-re-render to rendition-playback-vs-committed-surface diff.
- Renditions seeded: .gzkit/renditions/AGENTS.md/claude.md (from current AGENTS.md), .gzkit/renditions/AGENTS.md/codex.md (from OBPI-26 interim).
- Files created: rendition_store.py, rendition_freshness.py, test_rendition_store.py, test_rendition_freshness.py, rendition_playback.feature, rendition_playback_steps.py.
- Tests added: 20 unit tests (REQ-01, REQ-03) + 8 BDD scenarios (REQ-01..04) + updated test_invariant_coherence/test_sync_cmds/test_compose for playback semantics.
- Date completed: 2026-06-14
- Attestation status: operator-attested ("attest completed", g0)
- Defects noted: none

## Tracked Defects

**OBPI-26 interim rendition is the migration seed.** The committed-rendition store this OBPI lands should adopt `docs/design/.../renditions/agentcontract-codex-root-interim.md` as the seed for `.gzkit/renditions/AGENTS.md/codex.md` (per the parent ADR: "composer regenerates the rendition once 21/22 land"). The physical migration of that interim artifact + the retirement of the monolith template framing is OBPI-27's disposition scope; this OBPI establishes the store contract and playback path. Confirm the seam at Stage 1 brief-reconcile.

_No further defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator g0 attests OBPI-0.0.37-22 (committed-rendition store + deterministic playback + freshness gate) complete after Stage 4 evidence review: rendition_store.py + rendition_freshness.py landed, sync_agents_md/render_agents_md/invariant_coherence re-pointed to deterministic rendition playback, --rendition-freshness scope wired into gz check. Receipts: arb-step-unittest-d459a288befe408fa5fa87dcd74d6e10 (6131/6131 pass), arb-ruff-a9d1d983fdd94f119b9c052b82b0ca49, arb-step-typecheck-040f8f8835f742778313409e9681e137, arb-step-mkdocs-35dc676c7f114aa3a39a302d093614d5. 8/8 BDD scenarios pass (@REQ-0.0.37-22-01..04); behavior_uncovered_reqs=0. Open Implementation Decision (A) .gzkit/renditions/<surface>/<consumer>.md and (B) dedicated --rendition-freshness scope both confirmed.
- Date: 2026-06-14

---

**Date Completed:** 2026-06-14

**Evidence Hash:** -
