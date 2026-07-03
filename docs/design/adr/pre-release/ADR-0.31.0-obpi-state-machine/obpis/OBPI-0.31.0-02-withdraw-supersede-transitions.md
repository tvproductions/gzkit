---
id: OBPI-0.31.0-02-withdraw-supersede-transitions
parent: ADR-0.31.0-obpi-state-machine
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.31.0-02-withdraw-supersede-transitions: Withdraw Supersede Transitions

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #2 - "OBPI-0.31.0-02: **withdraw-supersede-transitions** — Elevate withdraw to a monitor-backed first-class transition and build `gz obpi supersede`; both emit canonical transition events; closes GHI #348 root"

**Status:** Draft

## Objective

Elevate `gz obpi withdraw` from a bare event-recorder to a witnessed transition
validated against OBPI-01's `CANONICAL_TRANSITIONS`, and build the missing
new "supersede" verb under `gz obpi` (invocation shape: OBPI-X --by OBPI-Y,
introduced by this OBPI) — both emitting canonical transition events
(`obpi_withdrawn` / `obpi_superseded`), consuming the OBPI-01 model layer
without modifying it. Closes the GHI #348 root cause: withdrawal becomes a
validated transition, not a hand-edit the reconciler silently demotes.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface
(new "supersede" CLI verb under `gz obpi`, elevated `gz obpi withdraw`
contract, new `obpi_superseded` ledger event schema entry).

## Allowed Paths

- `src/gzkit/commands/obpi_cmd.py` — **MODIFY**: elevate `obpi_withdraw_cmd`
  (currently line ~62) to construct and validate a `Transition` from OBPI-01's
  `CANONICAL_TRANSITIONS` before emitting `obpi_withdrawn_event`; **ADD**
  `obpi_supersede_cmd`, modeled on the existing `obpi_repudiate_cmd` (line
  ~125) — ADR-0.0.71 names this as the "proven transition" precedent this
  OBPI inherits.
- `src/gzkit/ledger_events.py` — **MODIFY**: elevate `obpi_withdrawn_event`
  (line ~56) with a witness field if the transition validation requires one;
  **ADD** `obpi_superseded_event(obpi_id, parent, superseded_by, rationale)`
  mirroring the shape of `obpi_completion_repudiated_event` (line ~66).
- `src/gzkit/cli/parser_artifacts.py` — **MODIFY**: existing `withdraw`
  subparser (lines ~1243-1261) gains witness flags if required; **ADD** new
  `supersede` subparser registration.
- `src/gzkit/cli/parser_handler_manifest.py` — **MODIFY**: register the
  lazy-import handler entry for `obpi_supersede_cmd` (mirrors the existing
  `obpi_withdraw_cmd` entry in this file).
- `src/gzkit/schemas/ledger.json` — **MODIFY**: register the `obpi_superseded`
  event schema entry; extend `obpi_withdrawn`'s `extra` schema if witness
  fields are added.
- `src/gzkit/core/obpi_state_machine.py` — **READ-ONLY IMPORT SURFACE**:
  consume `OBPIState`, `Transition`, `CANONICAL_TRANSITIONS`,
  `WitnessRequirement` from OBPI-01. Do NOT edit — Boundary Invariant #1
  (model/monitor/CLI separation).
- `tests/commands/test_obpi_withdraw_cmd.py` — **MODIFY**: add elevation and
  transition-validation tests.
- `tests/commands/test_obpi_supersede_cmd.py` — **CREATE**: new verb tests,
  following the `tests/commands/` convention (not the older flat
  `tests/test_obpi_repudiate_cli.py` layout).
- `docs/user/manpages/obpi-withdraw.md` — **MODIFY**: document the elevated
  witness/transition contract.
- `docs/user/manpages/obpi-supersede.md` — **CREATE**: new verb manpage (CLI
  contract doctrine § New Subcommand requires this for Heavy lane).
- `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — **MODIFY
  IF NEEDED**: sync the operator-facing withdraw/supersede moment if the
  runbook currently documents the pre-elevation `withdraw` contract.
- `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md` — parent ADR (Boundary Invariants already present; no edit expected).
- `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/**` — parent ADR package scope (this brief; evidence).

## Denied Paths

- `src/gzkit/core/obpi_state_machine.py` — **NO EDITS** (model layer belongs to OBPI-01; Boundary Invariant #1)
- `src/gzkit/governance/invariants.py`, `src/gzkit/governance/trust_audits/**` — no runtime monitor in this OBPI (that is OBPI-03)
- `src/gzkit/core/lifecycle.py`, `src/gzkit/lifecycle.py` — legacy choreography; deferred-in-keel, not touched here
- `tests/test_obpi_repudiate_cli.py` — read as precedent only, not modified (ADR-0.0.71 scope, untouched by this OBPI)
- Paths not listed in Allowed Paths
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Elevate `obpi_withdraw_cmd` (`src/gzkit/commands/obpi_cmd.py`) to construct and validate a `Transition` against OBPI-01's `CANONICAL_TRANSITIONS` (`gzkit.core.obpi_state_machine`) before emitting `obpi_withdrawn_event`; an OBPI whose current state is not a valid predecessor for the `withdrawn` transition MUST be rejected (non-zero exit, no ledger write).
2. REQUIREMENT: Add a new "supersede" verb under `gz obpi` — invocation shape `OBPI-X --by OBPI-Y --rationale <text>` (`obpi_supersede_cmd`, modeled on `obpi_repudiate_cmd`) — that validates the `superseded` transition and emits `obpi_superseded_event` citing both the superseded and superseding OBPI IDs.
3. REQUIREMENT: The witness requirement declared on the `withdrawn` and `superseded` transitions in OBPI-01's `CANONICAL_TRANSITIONS` MUST be enforced at the CLI boundary — transport-agnostic (`human_attested` via `--attestor-present`/`--attestation-text`, or `self_close`), never a TTY/PTY/interactive-terminal value (canon-owner directive; parent ADR Boundary Invariant #2).
4. NEVER: Modify `src/gzkit/core/obpi_state_machine.py` — this OBPI consumes the OBPI-01 model layer, it does not extend or alter it (Boundary Invariant #1).
5. NEVER: Add a runtime invariant monitor or edit `src/gzkit/governance/invariants.py` / `src/gzkit/governance/trust_audits/**` — that is OBPI-03's scope (Boundary Invariant #3: landing falsifier gates breadth).
6. ALWAYS: Reconcile this brief against the parent ADR § Decision item 5 before implementation; quote it verbatim into Implementation Summary.
7. ALWAYS: Register new CLI surface in both `src/gzkit/cli/parser_artifacts.py` and `src/gzkit/cli/parser_handler_manifest.py` (the confirmed dual-registration pattern for existing `obpi_withdraw_cmd`), plus a manpage under `docs/user/manpages/`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

<!-- gz-validate-skip: command-shape -->
- [x] **Parent ADR § Decision item 5 quoted** verbatim into Implementation Summary (to be completed during implementation): "Withdraw / supersede are first-class transitions. `gz obpi withdraw OBPI-X.Y.Z-NN --rationale ...` and `gz obpi supersede OBPI-X.Y.Z-NN --by OBPI-Y.Y.Y-MM` emit canonical transitions with their own receipts, witness requirements, and lifecycle semantics."
- [x] Parent ADR § Intent — the canonical observed symptom (GHI #348 silent `Withdrawn` → `pending` demotion) this OBPI closes the root cause of.
- [x] Parent ADR § Target Scope — "withdraw-supersede-transitions" bullet: elevate the existing `gz obpi withdraw` event-recorder into a first-class monitor-*validated* (not monitor-*enforced* — that's OBPI-03) transition; build the missing new "supersede" verb.
- [x] Parent ADR § Boundary Invariants #1 (model/monitor/CLI separation) and #2 (transport-agnostic witness) — both directly constrain this OBPI's Requirements 3-5 above.

**Sibling ADR (read — direct precedent, GHI-adjacent):**

- [x] `docs/design/adr/foundation/ADR-0.0.71-completion-repudiation/ADR-0.0.71-completion-repudiation.md` — explicitly scoped OUT withdraw's elevation ("Does NOT touch `withdraw`'s semantics") and named `ADR-pool.obpi-state-machine` (now this ADR) as the inheritor: *"`ADR-pool.obpi-state-machine` inherits a proven transition when it schedules, rather than designing repudiation from scratch."* `obpi_repudiate_cmd` is therefore the concrete pattern to follow, not a novel design.
- [x] `.gzkit/rules/governance-core.md` § Withdraw vs Repudiate — operator-facing doctrine distinguishing the two verbs; already documents `withdraw` as "permanent one-way retirement" — this OBPI does not change that semantic, only adds transition validation + witness.

**Existing Code (read; do NOT modify unless named in Allowed Paths):**

- [x] `src/gzkit/commands/obpi_cmd.py:62-97` — `obpi_withdraw_cmd` (current bare event-recorder to elevate)
- [x] `src/gzkit/commands/obpi_cmd.py:98-193` — `_reset_brief_status_after_repudiation` + `obpi_repudiate_cmd` (the proven precedent pattern for `obpi_supersede_cmd`)
- [x] `src/gzkit/ledger_events.py:47-84` — `obpi_created_event`, `obpi_withdrawn_event`, `obpi_completion_repudiated_event` (event-constructor shape to mirror for `obpi_superseded_event`)
- [x] `src/gzkit/core/obpi_state_machine.py` — OBPI-01's delivered `OBPIState`, `Transition`, `CANONICAL_TRANSITIONS`, `WitnessRequirement` (the model this OBPI consumes)
- [x] `src/gzkit/cli/parser_artifacts.py:1243-1261` — existing `withdraw` subparser registration (pattern to mirror for `supersede`)
- [x] `docs/user/manpages/obpi-repudiate.md`, `docs/user/manpages/obpi-withdraw.md` — doc precedent and current withdraw contract to update
- [x] `tests/commands/test_obpi_withdraw_cmd.py`, `tests/test_obpi_repudiate_cli.py` — test precedent for CLI-verb coverage shape

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/core/obpi_state_machine.py` exists (OBPI-01 completed, attested 2026-07-03)
- [x] `src/gzkit/commands/obpi_cmd.py` exists with `obpi_withdraw_cmd` and `obpi_repudiate_cmd`
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
uv run -m unittest tests.commands.test_obpi_withdraw_cmd -v
uv run -m unittest tests.commands.test_obpi_supersede_cmd -v
uv run mkdocs build --strict

# Specific verification for this OBPI
test -f docs/user/manpages/obpi-supersede.md
```

## Demo

```bash
# Elevated withdraw: validated transition, witnessed
uv run gz obpi withdraw OBPI-0.31.0-99-example --reason "phantom entry" --dry-run
```

<!-- gz-validate-skip: command-shape -->
```bash
# New supersede verb (introduced by this OBPI — not yet registered at
# authoring time; GHI #432 speculative-skip marker applies)
uv run gz obpi supersede OBPI-0.31.0-98-example --by OBPI-0.31.0-97-example --rationale "refactor consolidated scope" --dry-run
```

## Acceptance Criteria

- [ ] REQ-0.31.0-02-01 [BEHAVIOR]: `obpi_withdraw_cmd` validates the `withdrawn` transition against OBPI-01's `CANONICAL_TRANSITIONS` before emitting `obpi_withdrawn_event`; an OBPI not in a valid predecessor state is rejected with a non-zero exit and no ledger write. Proven by a `@covers(REQ-0.31.0-02-01)` test in `tests/commands/test_obpi_withdraw_cmd.py`.
- [ ] REQ-0.31.0-02-02 [BEHAVIOR]: the new "supersede" verb under `gz obpi` (invocation shape: OBPI-X --by OBPI-Y --rationale text) exists, validates the `superseded` transition, and emits `obpi_superseded_event` citing both IDs. Proven by a `@covers(REQ-0.31.0-02-02)` test in `tests/commands/test_obpi_supersede_cmd.py`.
- [ ] REQ-0.31.0-02-03 [BEHAVIOR]: the witness requirement for both transitions is transport-agnostic — no TTY/PTY/interactive-terminal value is accepted; only `--attestor-present`/`--attestation-text` (`human_attested`) or `self_close` per Exception-mode rules. Proven by a `@covers(REQ-0.31.0-02-03)` test.
- [ ] REQ-0.31.0-02-04 [STRUCTURAL-FENCE]: OBPI-02 does not modify `src/gzkit/core/obpi_state_machine.py` and does not add a runtime invariant monitor — anchored in the parent ADR `## Boundary Invariants` #1 and #3.
- [ ] REQ-0.31.0-02-05 [SUPPORT]: `docs/user/manpages/obpi-supersede.md` is created and `docs/user/manpages/obpi-withdraw.md` is updated to reflect the elevated contract — `gz validate --documents` passing AND an `artifact_edited` ledger event citing both paths.
- [ ] REQ-0.31.0-02-06 [SUPPORT]: this brief's `### Implementation Summary` quotes the parent ADR § Decision item 5 verbatim (Requirements item 6) — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing this brief file.

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
