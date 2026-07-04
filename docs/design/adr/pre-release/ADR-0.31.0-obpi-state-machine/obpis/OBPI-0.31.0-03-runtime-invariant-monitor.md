---
id: OBPI-0.31.0-03-runtime-invariant-monitor
parent: ADR-0.31.0-obpi-state-machine
item: 3
lane: Heavy
status: Completed
req_atomic:
  - REQ-0.31.0-03-01  # One pure classifier module + its unit-test file — one indivisible authoring unit (no I/O, single class).
  - REQ-0.31.0-03-02  # One integration edit at the single write chokepoint + one contrast test — indivisible (refusal and receipt surfacing land together or not at all).
  - REQ-0.31.0-03-03  # Single landing-falsifier regression test reproducing the GHI #348 shape — one indivisible test-authoring unit.
  - REQ-0.31.0-03-04  # Structural fence (no labor unit — a constraint audited via parent-ADR Boundary Invariants, not subdividable work).
  - REQ-0.31.0-03-05  # Single manpage edit documenting the refusal path — one indivisible SUPPORT authoring unit.
  - REQ-0.31.0-03-06  # Single Implementation Summary quotation written at completion ceremony — one indivisible SUPPORT authoring unit.
---

# OBPI-0.31.0-03-runtime-invariant-monitor: Runtime Invariant Monitor

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md`
- **Checklist Item:** #3 - "OBPI-0.31.0-03: **runtime-invariant-monitor** — Runtime invariant monitor on the artifact-graph read/write boundary that refuses silent `status:` frontmatter drift (GHI #348 class) in production — the pre-registered landing falsifier"

**Status:** Completed

## Objective

Build the runtime invariant monitor that classifies every requested `status:`
frontmatter edit against OBPI-01's `CANONICAL_TRANSITIONS` before allowing
the write at the one production chokepoint that performs it
(`rewrite_governed_keys_in_place`), refusing an edit that does not correspond
to a declared transition. This is the pre-registered landing falsifier: it
must, in production, refuse the exact GHI #348 shape (a hand-marked
`Withdrawn` silently demoted to `pending` by the reconciler).

## Lane

**Heavy** - This OBPI changes a runtime-contract surface: `gz frontmatter
reconcile` gains a new refusal/exit-code path when a requested rewrite has no
declared transition backing it.

## Allowed Paths

- `src/gzkit/governance/obpi_transition_monitor.py` — **CREATE**: the
  monitor. Classifies a requested `status` edit (`from_state`, `to_state`)
  against OBPI-01's `CANONICAL_TRANSITIONS` (`gzkit.core.obpi_state_machine`);
  returns an allow/refuse decision. Pure classification logic — no I/O.
- `src/gzkit/governance/frontmatter_coherence.py` — **MODIFY**: hook the
  monitor into `rewrite_governed_keys_in_place` (line ~151) — the confirmed
  single write chokepoint for governed keys including `status` (`_GOVERNED_KEYS`
  at line ~29) — and/or its caller `reconcile_frontmatter` (line ~248). A
  refused edit must skip the write and surface in the `ReconciliationReceipt`
  rather than silently landing.
- `src/gzkit/core/obpi_state_machine.py` — **READ-ONLY IMPORT SURFACE**:
  consume `OBPIState`, `Transition`, `CANONICAL_TRANSITIONS` from OBPI-01. Do
  NOT edit — Boundary Invariant #1.
- `tests/governance/test_obpi_transition_monitor.py` — **CREATE**: monitor
  classification unit tests.
- `tests/governance/test_frontmatter_coherence.py` — **MODIFY**: add the
  landing-falsifier regression test — reproduce the GHI #348 shape (an
  undeclared `status` rewrite reaching `rewrite_governed_keys_in_place`) and
  assert it is refused, not silently applied.
- `docs/user/manpages/frontmatter-reconcile.md` — **MODIFY**: document the
  new refusal path and its exit-code/output contract.
- `src/gzkit/commands/frontmatter_reconcile.py` — **MODIFY** (coupled-surface
  amendment, 2026-07-04 Step 4b adversary finding, DO IT RIGHT 1a): the CLI
  renderer consumes `ReconciliationReceipt` and MUST render
  `refused_rewrites` — a run carrying refusals must never print "no drift
  detected". Operator ratification of this amendment occurs at Gate 5.
- `src/gzkit/commands/obpi_precomplete.py` — **MODIFY** (same coupled-surface
  amendment): `_check_reconcile_idempotent` consumes the receipt and MUST
  surface refused rewrites in its check message (pass-with-note; a hard fail
  would deadlock the refused OBPI's own completion).
- `src/gzkit/commands/validate_frontmatter.py` — **READ-ONLY IMPORT SURFACE**:
  imported by the REQ tests; declared here for allowlist/import-scan
  coherence, no edits.
- `tests/commands/test_frontmatter_reconcile.py` — **MODIFY**: renderer
  output-form fixture tests for the refusal section.
- `tests/commands/test_obpi_precomplete.py` — **MODIFY**: refused-rewrites
  surfacing test for `_check_reconcile_idempotent`.
- `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md` — parent ADR (Boundary Invariants already present; no edit expected).
- `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/**` — parent ADR package scope (this brief; evidence).

## Denied Paths

- `src/gzkit/governance/invariants.py` — **NOT the monitor's home.** Read
  during authoring (2026-07-03): this module is `ConstitutionalInvariant`
  (ADR-0.0.37 content-rendering claims registry) — an unrelated concept that
  only shares a filename word with "invariant." OBPI-01/02 denied this path
  by name-association, not architecture; this brief corrects that — the
  runtime monitor is a new module (see Allowed Paths), not an extension of
  this file.
- `src/gzkit/governance/trust_audits/**` — this is the batch/CI-audit
  pattern (`gz validate --scope`, run periodically, read-only). The ADR
  Decision item 4 describes a **live** monitor on the write path itself
  ("every read or write... passes through one monitor") — a fundamentally
  different integration shape. A future `gz validate` wrapper consuming this
  monitor's classifier is plausible but out of scope here.
- `src/gzkit/core/obpi_state_machine.py` — no edits (Boundary Invariant #1)
- `src/gzkit/commands/obpi_cmd.py`, `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/cli/parser_handler_manifest.py` — no new `gz obpi` CLI verbs in this OBPI (that is OBPI-02's surface)
- `src/gzkit/core/lifecycle.py`, `src/gzkit/lifecycle.py` — legacy choreography; deferred-in-keel
- Paths not listed in Allowed Paths
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Build `src/gzkit/governance/obpi_transition_monitor.py` — a pure classifier that, given a current `status` and a requested `status`, returns whether the transition is a member of OBPI-01's `CANONICAL_TRANSITIONS`.
2. REQUIREMENT: Hook the monitor into `rewrite_governed_keys_in_place` (or its caller `reconcile_frontmatter`) in `src/gzkit/governance/frontmatter_coherence.py` so an undeclared `status` rewrite is refused before the write happens — not merely logged after the fact.
3. REQUIREMENT: The landing falsifier MUST be proven live: a regression test reproducing the GHI #348 shape (hand-marked `Withdrawn`, ledger has no matching completion/abandonment event, reconciler would otherwise rewrite to `pending`) MUST demonstrate the monitor refuses the write.
4. NEVER: Modify `src/gzkit/core/obpi_state_machine.py` (consume the OBPI-01 model, do not alter it — Boundary Invariant #1) or extend `src/gzkit/governance/invariants.py` with this monitor's logic (that module is an unrelated ADR-0.0.37 concept — see Denied Paths).
5. ALWAYS: Reconcile this brief against the parent ADR § Decision item 4 and § Target Scope before implementation; quote both verbatim into Implementation Summary.
6. ALWAYS: Preserve `reconcile_frontmatter`'s existing behavior for every rewrite that IS backed by a declared transition — this OBPI adds a refusal path, it does not change accepted-case behavior.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision item 4 quoted** verbatim into Implementation Summary (to be completed during implementation): "A single invariant monitor. Every read or write to the artifact graph passes through one monitor that asserts: (a) the operation names a transition declared in (2); (b) preconditions are satisfied; (c) the witness requirement is met. A frontmatter hand-edit that is not backed by a declared transition is either rejected (no matching transition allowed) or auto-emits the transition (so receipts and state never disagree). Today the reconciler silently picks a winner; the monitor would refuse to let them disagree in the first place."
- [x] Parent ADR § Intent — the canonical observed symptom (GHI #348): `OBPI-0.31.0-02-complexity-check.md` hand-marked `Withdrawn`, no ledger event existed for it, `gz frontmatter reconcile` applied ledger-wins (ADR-0.0.9 Rule 1) and silently rewrote the brief to `status: pending` — operator intent erased.
- [x] Parent ADR § Target Scope — "runtime-invariant-monitor" bullet: "The load-bearing monitor on the artifact-graph read/write boundary: it classifies each state-affecting operation against a declared transition, rejects undeclared ones, and refuses a silent `status:` frontmatter drift (the GHI #348 class) in production config. This refusal is the constellation's pre-registered landing falsifier... and gates Phase 2 / HULL."
- [x] Parent ADR § Boundary Invariants #1 (model/monitor/CLI separation — this OBPI is the monitor consumer) and #3 (landing falsifier gates breadth — no deferred-in-keel work begins until this monitor refuses a silent drift live).

**Existing Code (read; do NOT modify unless named in Allowed Paths):**

- [x] `src/gzkit/governance/frontmatter_coherence.py` — `rewrite_governed_keys_in_place` (line ~243 post-implementation), the confirmed single write chokepoint for governed keys (`_GOVERNED_KEYS = {"id", "parent", "lane", "status"}` at line ~31); this is where GHI #348's silent rewrite actually landed. Also `reconcile_frontmatter` (line ~396 post-implementation), the orchestrator that computes ledger-wins diffs and calls the write function.
- [x] `src/gzkit/governance/invariants.py` — read in full; confirmed unrelated (`ConstitutionalInvariant`, ADR-0.0.37 content-rendering registry) — grounds the Denied Paths correction above.
- [x] `src/gzkit/core/obpi_state_machine.py` — OBPI-01's delivered `OBPIState`, `Transition`, `CANONICAL_TRANSITIONS` (the model this OBPI consumes).
- [x] `tests/governance/test_frontmatter_coherence.py` — existing test shape for the write-boundary function, to extend with the falsifier regression test.
- [x] `docs/user/manpages/frontmatter-reconcile.md` — current documented contract for `gz frontmatter reconcile`.

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/core/obpi_state_machine.py` exists (OBPI-01 completed, attested 2026-07-03)
- [x] `src/gzkit/governance/frontmatter_coherence.py` exists with `rewrite_governed_keys_in_place` and `reconcile_frontmatter`
- [x] Parent ADR present and registered in `gz state`

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
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.governance.test_obpi_transition_monitor -v
uv run -m unittest tests.governance.test_frontmatter_coherence -v
uv run mkdocs build --strict

# Specific verification for this OBPI
test -f src/gzkit/governance/obpi_transition_monitor.py
```

## Demo

```bash
# The landing falsifier: gz frontmatter reconcile now refuses an undeclared
# status drift instead of silently applying it (dry-run shows the refusal).
uv run gz frontmatter reconcile --dry-run
```

## Acceptance Criteria

- [ ] REQ-0.31.0-03-01 [BEHAVIOR]: `obpi_transition_monitor` classifies a `(from_status, to_status)` pair as allowed only when it matches a `Transition` in OBPI-01's `CANONICAL_TRANSITIONS`; an unmatched pair is classified as refused. Proven by a `@covers(REQ-0.31.0-03-01)` test in `tests/governance/test_obpi_transition_monitor.py`.
- [ ] REQ-0.31.0-03-02 [BEHAVIOR]: `rewrite_governed_keys_in_place` (or its `reconcile_frontmatter` caller) consults the monitor before writing a `status` edit; a refused edit does not reach `path.write_text` and is surfaced in the `ReconciliationReceipt`. Proven by a `@covers(REQ-0.31.0-03-02)` test in `tests/governance/test_frontmatter_coherence.py`.
- [ ] REQ-0.31.0-03-03 [BEHAVIOR]: the landing falsifier — a regression test reproducing the exact GHI #348 shape (hand-marked `Withdrawn`, no matching ledger event, reconciler would otherwise ledger-wins rewrite to `pending`) — demonstrates the monitor refuses the write in this exact scenario. Proven by a `@covers(REQ-0.31.0-03-03)` test.
- [ ] REQ-0.31.0-03-04 [STRUCTURAL-FENCE]: OBPI-03 does not modify `src/gzkit/core/obpi_state_machine.py` and does not extend `src/gzkit/governance/invariants.py` — anchored in the parent ADR `## Boundary Invariants` #1.
- [ ] REQ-0.31.0-03-05 [SUPPORT]: `docs/user/manpages/frontmatter-reconcile.md` is updated to document the refusal path — `gz validate --documents` passing AND an `artifact_edited` ledger event citing this path.
- [ ] REQ-0.31.0-03-06 [SUPPORT]: this brief's `### Implementation Summary` quotes the parent ADR § Decision item 4 verbatim (Requirements item 5) — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing this brief file.

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


The landing falsifier reproduces the exact GHI #348 shape live and passes: `uv run -m unittest tests.governance.test_frontmatter_coherence.ReconciliationLogicTests.test_landing_falsifier_ghi_348_undeclared_status_transition_refused -v` asserts pre/post SHA-256 byte equality (refused edit never reaches path.write_text), refusal surfaced in receipt.refused_rewrites, and absence from files_rewritten. Observed live on this brief itself: `uv run gz frontmatter reconcile --dry-run` renders "refused rewrites: 1 / REFUSED docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/obpis/OBPI-0.31.0-03-runtime-invariant-monitor.md / Invalid OBPI status transition: Draft → Active (not in CANONICAL_TRANSITIONS)" instead of the pre-fix false "no drift detected". Receipts: arb-step-unittest-63e9e1c02669438d984f1befb173a54b (6765/6765), arb-ruff-a56b409511f1409786ee4d65498f6114, arb-step-typecheck-c65f9934eb134711a4c4e6626473cc59, arb-step-mkdocs-0862cee475ce4b0f8d55f0c169f9bbd6.

### Implementation Summary


- Parent ADR § Decision item 4 (verbatim): "A single invariant monitor. Every read or write to the artifact graph passes through one monitor that asserts: (a) the operation names a transition declared in (2); (b) preconditions are satisfied; (c) the witness requirement is met. A frontmatter hand-edit that is not backed by a declared transition is either rejected (no matching transition allowed) or auto-emits the transition (so receipts and state never disagree). Today the reconciler silently picks a winner; the monitor would refuse to let them disagree in the first place."
- Parent ADR § Target Scope (verbatim): "The load-bearing monitor on the artifact-graph read/write boundary: it classifies each state-affecting operation against a declared transition, rejects undeclared ones, and refuses a silent `status:` frontmatter drift (the GHI #348 class) in production config. This refusal is the constellation's pre-registered landing falsifier... and gates Phase 2 / HULL."
- Files created/modified: created src/gzkit/governance/obpi_transition_monitor.py (pure classifier) and tests/governance/test_obpi_transition_monitor.py; modified src/gzkit/governance/frontmatter_coherence.py (monitor consultation at the write chokepoint; refused_rewrites on the receipt), src/gzkit/commands/frontmatter_reconcile.py (REFUSED lines rendered; no false "no drift detected"), src/gzkit/commands/obpi_precomplete.py (reconcile_idempotent pass-with-note naming refusals), tests/commands/test_frontmatter_reconcile.py, tests/commands/test_obpi_precomplete.py, tests/governance/test_frontmatter_coherence.py, docs/user/manpages/frontmatter-reconcile.md, data/schemas/frontmatter_coherence_receipt.schema.json.
- Tests added: 9 TransitionMonitor classifier tests including the full 8x8 biconditional (@covers REQ-0.31.0-03-01); write-boundary refused-vs-declared contrast test (@covers REQ-0.31.0-03-02); GHI #348 landing falsifier (@covers REQ-0.31.0-03-03); 3 refusal-visibility tests (renderer output-form pair + precomplete surfacing). Full suite 6765/6765.
- Date completed: 2026-07-04
- Attestation status: operator-verbatim conversational Gate 5 ("keep all four, attest completed"), attestor g0
- Defects noted: STATUS_VOCAB_MAPPING cannot express PLANNED/VERIFIED/SYNCED, so multi-step ledger-wins catch-up is permanently refused (visibly); tracked in ## Tracked Defects as a correction under ADR-0.31.0's deferred transition-emitter migration.

## Tracked Defects

- **Vocabulary/state-machine impedance mismatch (correction under
  ADR-0.31.0, surfaced by Step 4b adversarial validation 2026-07-04):**
  `STATUS_VOCAB_MAPPING` has no frontmatter term for `PLANNED`, `VERIFIED`,
  or `SYNCED`, so ordinary multi-step ledger-wins catch-up (`Draft → Active`,
  `Active → Completed`) can never match a single declared adjacent transition
  and is permanently refused by the monitor. Refusals are now operator-visible
  (CLI `REFUSED` lines; precomplete pass-with-note — this OBPI's coupled-surface
  amendment), so the disagreement is surfaced, not silent; but resolving the
  mismatch itself belongs to the parent ADR's deferred-in-keel
  transition-emitter migration ("Migrate `gz obpi complete` / `gz obpi
  reconcile` / `gz frontmatter reconcile` from batch-reconciler shape to
  transition-emitter shape"). Routed per operator doctrine as a correction
  under ADR-0.31.0, never an enhancement. Also logged in
  `.gzkit/insights/agent-insights.jsonl`.

## Human Attestation

- Attestor: `g0`
- Attestation: keep all four, attest completed — Gate 5 for OBPI-0.31.0-03-runtime-invariant-monitor (Heavy lane): operator ratified all four session decisions (--from=verify recovery entry over commit d864140b; brief drift repairs including the coupled-surface allowlist amendment; refusal-visibility fix with pass-with-note precomplete; vocabulary mismatch routed as a correction under ADR-0.31.0). Evidence: full suite 6765/6765 pass (receipt arb-step-unittest-63e9e1c02669438d984f1befb173a54b), lint clean (receipt arb-ruff-a56b409511f1409786ee4d65498f6114), typecheck clean (receipt arb-step-typecheck-c65f9934eb134711a4c4e6626473cc59), mkdocs strict pass (receipt arb-step-mkdocs-0862cee475ce4b0f8d55f0c169f9bbd6); landing falsifier refuses the GHI #348 shape live; Step 4b independent adversary verdict NOT-REFUTED after the refusal-visibility fix.
- Date: 2026-07-04

---

**Date Completed:** 2026-07-04

**Evidence Hash:** -
