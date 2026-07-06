---
id: OBPI-0.31.0-02-withdraw-supersede-transitions
parent: ADR-0.31.0-obpi-state-machine
item: 2
lane: Heavy
sensitivity: security
status: Completed
# req_atomic (ADR-0.0.64 / OBPI-04 task-envelope exemption): every REQ below
# was implemented as one indivisible RGR cycle — REQ-01 (elevate withdraw:
# one helper + command + event), REQ-02 (supersede: one cohesive command +
# event + graph-metadata unit), REQ-03 (witness enforcement inside those two
# commands, no separable labor), REQ-04 (STRUCTURAL-FENCE, audit-only, no
# labor), REQ-05/06 (SUPPORT doc/narrative units) — none decomposed into
# sub-steps warranting a seq=02+ TASK subdivision.
req_atomic:
  - REQ-0.31.0-02-01
  - REQ-0.31.0-02-02
  - REQ-0.31.0-02-03
  - REQ-0.31.0-02-04
  - REQ-0.31.0-02-05
  - REQ-0.31.0-02-06
---

# OBPI-0.31.0-02-withdraw-supersede-transitions: Withdraw Supersede Transitions

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md`
<!-- gz-validate-skip: command-shape -->
- **Checklist Item:** #2 - "OBPI-0.31.0-02: **withdraw-supersede-transitions** — Elevate withdraw to a monitor-backed first-class transition and build `gz obpi supersede`; both emit canonical transition events; closes GHI #348 root"

**Status:** Completed

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
- `src/gzkit/ledger.py` — **MODIFY (surgical, discovered at plan time)**: add
  `_apply_obpi_superseded_metadata` (mirrors `_apply_obpi_withdrawn_metadata`
  at line ~693, setting `graph[id]["superseded"] = True` +
  `superseded_by`), and register its dispatch call alongside the existing
  `_apply_obpi_withdrawn_metadata` / `_apply_obpi_completion_repudiated_metadata`
  calls (line ~733-734) — without this, `obpi_superseded` events are silently
  invisible to the artifact graph and no consumer (including this OBPI's own
  terminal-state check) can see that an OBPI was superseded.
- `src/gzkit/core/obpi_state_machine.py` — **READ-ONLY IMPORT SURFACE**:
  consume `OBPIState`, `Transition`, `CANONICAL_TRANSITIONS`,
  `WitnessRequirement` from OBPI-01. Do NOT edit — Boundary Invariant #1
  (model/monitor/CLI separation).
- `src/gzkit/commands/common.py` — **READ / SHARED-UTILITY NEIGHBOR**: the
  withdraw/supersede commands and their tests import `GzCliError`,
  `ensure_initialized`, `get_project_root` etc. from this same-directory
  utility module; declared so the reconcile allowlist matches the real
  import surface (no edit expected).
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

**Coupled surfaces (discovered at Stage-3 full-suite verify; scope expansion per Prime Directive #4 / coupled-surface coherence 1a).** Adding a new `obpi_superseded` ledger event and a new `gz obpi supersede` CLI verb mechanically couples four consumer surfaces the initial allowlist under-declared. Each is well-precedented (OBPI-0.0.71 for the event-model triple; OBPI-0.0.67-02 for skill-alignment):

- `src/gzkit/events.py` — **MODIFY**: add the `ObpiSupersededEvent` typed model (mirrors `ObpiCompletionRepudiatedEvent`) and add `attestor` to `ObpiWithdrawnEvent` — `test_schemas.py::TestLedgerSchemaAlignment` cross-checks that every committed ledger-schema event has a typed model and that every schema property exists on the model.
- `tests/test_schemas.py` — **MODIFY**: register `"obpi_superseded": ObpiSupersededEvent` in the `_EVENT_MODELS` alignment registry.
- `.gzkit/skills/gz-obpi-reconcile/SKILL.md` — **MODIFY**: wield `gz obpi supersede` (mirrors how the skill already wields `gz obpi withdraw` for phantom remediation) — `tool-skill-runbook-alignment` Invariant 1 requires every CLI verb to have a wielding skill. Requires `skill-version` + `last_reviewed` bump and `gz agent sync control-surfaces`.
- `config/doc-coverage.json` — **MODIFY**: declare `obpi supersede` (mirrors the `obpi withdraw` entry) — `test_doc_coverage` fails closed on any AST-discovered command missing from the manifest.

## Denied Paths

- `src/gzkit/core/obpi_state_machine.py` — **NO EDITS** (model layer belongs to OBPI-01; Boundary Invariant #1)
- `src/gzkit/governance/invariants.py`, `src/gzkit/governance/trust_audits/**` — no runtime monitor in this OBPI (that is OBPI-03)
- `src/gzkit/core/lifecycle.py`, `src/gzkit/lifecycle.py` — legacy choreography; deferred-in-keel, not touched here
- `tests/test_obpi_repudiate_cli.py` — read as precedent only, not modified (ADR-0.0.71 scope, untouched by this OBPI)
- Paths not listed in Allowed Paths
- New dependencies, CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Elevate `obpi_withdraw_cmd` (`src/gzkit/commands/obpi_cmd.py`) to construct and validate a `Transition` against OBPI-01's `CANONICAL_TRANSITIONS` (`gzkit.core.obpi_state_machine`) before emitting `obpi_withdrawn_event`; an OBPI whose current state is not a valid predecessor for the `withdrawn` transition MUST be rejected (non-zero exit, no ledger write).
2. REQUIREMENT: Add a new "supersede" verb under `gz obpi` — invocation shape `OBPI-X --by OBPI-Y --rationale <text>` (`obpi_supersede_cmd`, modeled on `obpi_repudiate_cmd`) — that validates the `superseded` transition and emits `obpi_superseded_event` citing both the superseded and superseding OBPI IDs. The event MUST be registered in the artifact-graph builder (`src/gzkit/ledger.py`, mirroring `_apply_obpi_withdrawn_metadata`) so a superseded OBPI is visible to the graph the same way a withdrawn one is — an unregistered event type is silently invisible to every downstream consumer, including this OBPI's own terminal-state check (Requirement 1).
3. REQUIREMENT: The witness requirement declared on the `withdrawn` and `superseded` transitions in OBPI-01's `CANONICAL_TRANSITIONS` MUST be enforced at the CLI boundary — transport-agnostic (`human_attested` via `--attestor-present`/`--attestation-text`, or `self_close`), never a TTY/PTY/interactive-terminal value (canon-owner directive; parent ADR Boundary Invariant #2).
4. NEVER: Modify `src/gzkit/core/obpi_state_machine.py`, add a runtime invariant monitor, or edit `src/gzkit/governance/invariants.py` / `src/gzkit/governance/trust_audits/**` — the model layer is OBPI-01's (Boundary Invariant #1) and the runtime monitor is OBPI-03's (Boundary Invariant #3: landing falsifier gates breadth); this OBPI consumes the former and does not build the latter.
5. ALWAYS: Reconcile this brief against the parent ADR § Decision item 5 before implementation; quote it verbatim into Implementation Summary.
6. ALWAYS: Register new CLI surface in both `src/gzkit/cli/parser_artifacts.py` and `src/gzkit/cli/parser_handler_manifest.py` (the confirmed dual-registration pattern for existing `obpi_withdraw_cmd`), plus a manpage under `docs/user/manpages/`.

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

- [x] `src/gzkit/commands/obpi_cmd.py` (lines ~62-97) — `obpi_withdraw_cmd` (current bare event-recorder to elevate)
- [x] `src/gzkit/commands/obpi_cmd.py` (lines ~98-193) — `_reset_brief_status_after_repudiation` + `obpi_repudiate_cmd` (the proven precedent pattern for `obpi_supersede_cmd`)
- [x] `src/gzkit/ledger_events.py` (lines ~47-84) — `obpi_created_event`, `obpi_withdrawn_event`, `obpi_completion_repudiated_event` (event-constructor shape to mirror for `obpi_superseded_event`)
- [x] `src/gzkit/core/obpi_state_machine.py` — OBPI-01's delivered `OBPIState`, `Transition`, `CANONICAL_TRANSITIONS`, `WitnessRequirement` (the model this OBPI consumes)
- [x] `src/gzkit/cli/parser_artifacts.py` (lines ~1243-1261) — existing `withdraw` subparser registration (pattern to mirror for `supersede`)
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

Before: `gz obpi withdraw` was a bare event-recorder with no connection to any
state model, and gzkit had no way to record that one OBPI *supersedes* another
— the GHI #348 gap where a hand-edited `Withdrawn` status was silently demoted
because no transition existed to prove it. After: both `withdraw` and the new
`gz obpi supersede` verb are witnessed, model-validated transitions that consult
OBPI-01's `CANONICAL_TRANSITIONS` before emitting, refuse illegal transitions
out of terminal states, and mark the artifact graph so downstream consumers can
see the supersession lineage. This is the KEEL's CLI/ledger slice consuming the
state-machine model OBPI-01 laid.

### Key Proof


```bash
uv run gz obpi supersede OBPI-0.0.71-01-completion-repudiation-event \
  --by OBPI-0.0.71-02-gz-obpi-repudiate-cli \
  --rationale "demo: superseded lineage" --attestor "g0" --dry-run
```
→ emits a well-formed `obpi_superseded` event carrying both ids + the witness:
```json
{ "event": "obpi_superseded", "id": "OBPI-0.0.71-01-completion-repudiation-event",
  "superseded_by": "OBPI-0.0.71-02-gz-obpi-repudiate-cli",
  "rationale": "demo: superseded lineage", "attestor": "g0" }
```
The refusal path is model-driven: superseding an already-terminal OBPI is
rejected because `_supersede_transition_available` finds no matching transition
in `CANONICAL_TRANSITIONS` (verified by the `TestSupersedeTransitionConsultsModel`
unit test asserting `DRAFTED→True`, `SUPERSEDED→False`). Full suite 6752/6752
(receipt `arb-step-unittest-201bcd2be1ff4c959ed4199d0be46659`); `gz cli audit`
115/115.

### Implementation Summary


**Parent ADR § Decision item 5 (verbatim):** "Withdraw / supersede are
first-class transitions. `gz obpi withdraw OBPI-X.Y.Z-NN --rationale ...` and
`gz obpi supersede OBPI-X.Y.Z-NN --by OBPI-Y.Y.Y-MM` emit canonical transitions
with their own receipts, witness requirements, and lifecycle semantics. The
Withdrawn-demotion failure (GHI #348) is closed because (a) a hand-edit
`Withdrawn` is rejected by the monitor pointing at the canonical transition CLI;
(b) once the transition fires, the ledger has the event and the reconciler has
nothing to 'fix.'"

- Files created/modified: `src/gzkit/commands/obpi_cmd.py` (elevated
  `obpi_withdraw_cmd` + new `obpi_supersede_cmd`; model-consulting helpers
  `_withdraw_transition_available` / `_supersede_transition_available` /
  `_current_terminal_state`); `src/gzkit/ledger_events.py` +
  `src/gzkit/events.py` + `src/gzkit/schemas/ledger.json` (new `obpi_superseded`
  event across factory / typed-model / JSON-schema representations; `attestor`
  added to `obpi_withdrawn` in all three); `src/gzkit/ledger.py`
  (`_apply_obpi_superseded_metadata` + dispatch registration for graph
  visibility); `src/gzkit/cli/parser_artifacts.py` +
  `parser_handler_manifest.py` (withdraw `--attestor`, new `supersede`
  subparser); manpages (`obpi-supersede.md` created, `obpi-withdraw.md`
  updated), `index.md`, `docs/user/runbook.md`,
  `docs/governance/governance_runbook.md`, `config/doc-coverage.json`,
  `.gzkit/skills/gz-obpi-reconcile/SKILL.md` (wields the new verb;
  synced to mirrors)
- Tests added: `tests/commands/test_obpi_supersede_cmd.py` (9 tests incl.
  model-consultation, graph-metadata, witness, both-ids-exist);
  elevation + witness + terminal-rejection tests in
  `tests/commands/test_obpi_withdraw_cmd.py`; `_EVENT_MODELS` registration in
  `tests/test_schemas.py`
- Date completed: 2026-07-03
- Attestation status: operator-attested (Gate 5, Stage 4)
- Defects noted: an in-flight fix to `src/gzkit/governance/brief_reconcile.py`
  (glob-pattern false-positive in the allowlist checker, sibling of GHI #626 —
  TDD'd with `test_allowlist_glob_path_not_existence_checked`); GHI #666 filed
  for the plan-audit-receipt id-normalization mismatch surfaced during Stage 2

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — OBPI-0.31.0-02-withdraw-supersede-transitions: 6752/6752 tests pass (receipt arb-step-unittest-5eaf0c6044b54d788ea920c25ef393a5), lint clean (arb-ruff-10872309e75e4e6a85f2e4477a21507e), typecheck clean (arb-step-typecheck-bb67e3e27001418f819c0b20dd933f53), mkdocs --strict clean (arb-step-mkdocs-b5b4059df55b4fe9902b210b524004ef), gz cli audit 115/115, REQ→@covers behavior_uncovered_reqs=0, brief reconcile has_drift=false. Stage 4b independent adversarial validation (fresh Opus context, refute-framed) returned REFUTED on REQ-06 (Implementation Summary was an empty template) and a test-discrimination caveat; both fixed and re-verified before this attestation — the Implementation Summary now carries the verbatim parent-ADR Decision item 5 quote, and the model-consultation test now patches CANONICAL_TRANSITIONS with a synthetic inverted model to genuinely discriminate a model-read from a hardcode (proven RED against a stubbed hardcode). Boundary fence intact: obpi_state_machine.py / governance/invariants.py / trust_audits untouched. Stage 5 precomplete 8/8 green.
- Date: 2026-07-03

---

**Date Completed:** 2026-07-03

**Evidence Hash:** -
