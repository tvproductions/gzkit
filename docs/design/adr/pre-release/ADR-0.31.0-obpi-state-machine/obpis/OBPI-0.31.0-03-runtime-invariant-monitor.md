---
id: OBPI-0.31.0-03-runtime-invariant-monitor
parent: ADR-0.31.0-obpi-state-machine
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.31.0-03-runtime-invariant-monitor: Runtime Invariant Monitor

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md`
- **Checklist Item:** #3 - "OBPI-0.31.0-03: **runtime-invariant-monitor** — Runtime invariant monitor on the artifact-graph read/write boundary that refuses silent `status:` frontmatter drift (GHI #348 class) in production — the pre-registered landing falsifier"

**Status:** Draft

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
4. NEVER: Modify `src/gzkit/core/obpi_state_machine.py` — consume the OBPI-01 model, do not alter it (Boundary Invariant #1).
5. NEVER: Extend `src/gzkit/governance/invariants.py` with this monitor's logic — that module is an unrelated ADR-0.0.37 concept (see Denied Paths).
6. ALWAYS: Reconcile this brief against the parent ADR § Decision item 4 and § Target Scope before implementation; quote both verbatim into Implementation Summary.
7. ALWAYS: Preserve `reconcile_frontmatter`'s existing behavior for every rewrite that IS backed by a declared transition — this OBPI adds a refusal path, it does not change accepted-case behavior.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [x] **Parent ADR § Decision item 4 quoted** verbatim into Implementation Summary (to be completed during implementation): "A single invariant monitor. Every read or write to the artifact graph passes through one monitor that asserts: (a) the operation names a transition declared in (2); (b) preconditions are satisfied; (c) the witness requirement is met. A frontmatter hand-edit that is not backed by a declared transition is either rejected (no matching transition allowed) or auto-emits the transition (so receipts and state never disagree). Today the reconciler silently picks a winner; the monitor would refuse to let them disagree in the first place."
- [x] Parent ADR § Intent — the canonical observed symptom (GHI #348): `OBPI-0.31.0-02-complexity-check.md` hand-marked `Withdrawn`, no ledger event existed for it, `gz frontmatter reconcile` applied ledger-wins (ADR-0.0.9 Rule 1) and silently rewrote the brief to `status: pending` — operator intent erased.
- [x] Parent ADR § Target Scope — "runtime-invariant-monitor" bullet: "The load-bearing monitor on the artifact-graph read/write boundary: it classifies each state-affecting operation against a declared transition, rejects undeclared ones, and refuses a silent `status:` frontmatter drift (the GHI #348 class) in production config. This refusal is the constellation's pre-registered landing falsifier... and gates Phase 2 / HULL."
- [x] Parent ADR § Boundary Invariants #1 (model/monitor/CLI separation — this OBPI is the monitor consumer) and #3 (landing falsifier gates breadth — no deferred-in-keel work begins until this monitor refuses a silent drift live).

**Existing Code (read; do NOT modify unless named in Allowed Paths):**

- [x] `src/gzkit/governance/frontmatter_coherence.py:151-188` — `rewrite_governed_keys_in_place`, the confirmed single write chokepoint for governed keys (`_GOVERNED_KEYS = {"id", "parent", "lane", "status"}` at line ~29); this is where GHI #348's silent rewrite actually landed.
- [x] `src/gzkit/governance/frontmatter_coherence.py:248` — `reconcile_frontmatter`, the orchestrator that computes ledger-wins diffs and calls the write function.
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
- [ ] REQ-0.31.0-03-06 [SUPPORT]: this brief's `### Implementation Summary` quotes the parent ADR § Decision item 4 verbatim (Requirements item 6) — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing this brief file.

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

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
