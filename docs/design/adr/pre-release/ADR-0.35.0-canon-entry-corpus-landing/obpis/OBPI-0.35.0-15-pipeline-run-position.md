---
id: OBPI-0.35.0-15-pipeline-run-position
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 15
lane: Heavy
sensitivity: security
status: Draft
allowlist:
  - src/gzkit/pipeline_markers.py
  - src/gzkit/pipeline_runtime.py
  - src/gzkit/commands/obpi_cmd.py
  - src/gzkit/commands/obpi_stages.py
  - src/gzkit/obpi_dispatch_channel.py
  - src/gzkit/commands/obpi_precomplete.py
  - src/gzkit/commands/obpi_complete.py
  - src/gzkit/pipeline_stage_fence.py
  - scripts/session_orientation.py
  - tests/test_pipeline_position.py
  - tests/commands/test_obpi_pipeline.py
  - tests/test_pipeline_runtime.py
  - tests/test_obpi_dispatch_channel.py
  - tests/scripts/test_session_orientation.py
  - features/pipeline_run_position.feature
  - features/steps/pipeline_run_position_steps.py
  - docs/user/manpages/obpi-pipeline.md
  - docs/user/runbook.md
  - docs/governance/GovZero/obpi-runtime-contract.md
  - docs/governance/pipeline-marker-migration-path.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-15-pipeline-run-position.md
reqs:
  - REQ-0.35.0-15-01
  - REQ-0.35.0-15-02
  - REQ-0.35.0-15-03
  - REQ-0.35.0-15-04
  - REQ-0.35.0-15-05
  - REQ-0.35.0-15-06
  - REQ-0.35.0-15-07
  - REQ-0.35.0-15-08
  - REQ-0.35.0-15-09
verification:
  - uv run -m unittest tests.test_pipeline_position tests.commands.test_obpi_pipeline tests.test_pipeline_runtime
  - uv run -m unittest tests.test_obpi_dispatch_channel tests.scripts.test_session_orientation tests.test_pipeline_stage_fence
  - uv run -m behave features/pipeline_run_position.feature
  - uv run gz validate --documents --req-kind-discipline --cli-alignment
  - uv run gz cli audit
  - uv run mkdocs build --strict
---

# OBPI-0.35.0-15-pipeline-run-position: Pipeline Run Position

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #15 - "Pipeline run position on disk -- the stage a run has reached and its position inside that stage are recorded as the run crosses each boundary, readable by a process that did not perform the run; the marker stays rebuildable Layer 3. Repair assignment against `ADR-0.13.0` (GHI #1172, amendment 2026-10-04)"
- **Decision item 11, verbatim:**

> 11. A PIPELINE RUN'S POSITION IS READABLE FROM DISK (operator-ruled 2026-10-04, GHI #1172; repair assignment, amendment in § Intent). The stage a run has reached, and its position inside that stage, are recorded as the run crosses each boundary, so a process that did not perform the run can read them. Obligation repaired: `ADR-0.13.0` § Intent, "one canonical command contract for launch, stage progression, resume, abort, and sync", and § Decision, "Persist pipeline stage state in a repository-local, machine-readable form". The marker stays Layer 3 under `ADR-0.0.9`: rebuildable from canon and ledger, and never gate evidence.

**Status:** Draft

## Objective

After a pipeline run crosses a stage boundary or a boundary inside a stage, a process that did not perform the run reads from disk the stage the run has reached and its position inside that stage. Deleting the marker and rebuilding it from canon and ledger yields the same position. A launch with nothing after it still reads as the launch stage, and stale-marker handling is unchanged.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The contract change is the active pipeline marker payload, which `docs/governance/GovZero/obpi-runtime-contract.md` documents as a runtime contract read by hooks, the session orientation and operators.

**Sensitivity: security.** Three Allowed Paths are registered security surfaces in `data/security_surfaces.json`: `src/gzkit/pipeline_markers.py` (`subprocess_user_input`), `src/gzkit/commands/obpi_cmd.py` and `src/gzkit/commands/obpi_complete.py` (`auth_boundaries`). `.gzkit/rules/security-sensitivity.md` § `gz validate --sensitivity` clause 1 requires the declaration, so the frontmatter carries it and Gate 5 runs the heightened walkthrough.

## Repair Assignment

This brief is a repair assignment (parent ADR § Intent, amendment 2026-10-04). It owns none of the obligations below. They keep their identities, their attestations and their tests; `ADR-0.13.0` and `ADR-0.0.9` are `Validated` and are not reopened. The REQs in § Acceptance Criteria are this brief's local acceptance criteria.

Obligations repaired, cited as they stand:

- `ADR-0.13.0` § Intent: "one canonical command contract for launch, stage progression, resume, abort, and sync".
- `ADR-0.13.0` § Decision: "Persist pipeline stage state in a repository-local, machine-readable form".
- `OBPI-0.13.0-02` Requirement 3: "Full launch MUST persist `entry=full` and `current_stage=implement`; `--from=verify` MUST persist `entry=verify` and `current_stage=verify`; `--from=ceremony` MUST persist `entry=ceremony` and `current_stage=ceremony`." This specified persistence at launch only, which is what GHI #1172 names as the origin of the defect. Its acceptance criteria are `REQ-0.13.0-02-01` and `REQ-0.13.0-02-02`.
- `OBPI-0.13.0-02` Requirement 4: "The per-OBPI and legacy marker files MUST carry the same JSON payload while the pipeline is active."
- `OBPI-0.13.0-03` Requirement 2: "Marker payloads MUST expose `blockers`, `required_human_action`, `next_command`, and `resume_point` in addition to the stage-state fields from `OBPI-0.13.0-02`." Its acceptance criteria are `REQ-0.13.0-03-01` through `REQ-0.13.0-03-04`.
- `ADR-0.0.9` § Decision: "Layer 3 artifacts (pipeline markers, caches, derived indexes) are always rebuildable. Delete them all, run `gz state`, and everything reconstructs from L1 + L2." Nothing rebuilds a pipeline marker today.

Constraint inherited, not repaired: `ADR-0.0.9` § Decision, "Layer 3 artifacts cannot block gates. Only L1 (canon) and L2 (events) can be gate evidence."

## Allowed Paths

- `src/gzkit/pipeline_markers.py` — marker payload, refresh, resume command and stale-marker handling (registered security surface)
- `src/gzkit/pipeline_runtime.py` — the re-export surface and the dispatch-state marker cache writer
- `src/gzkit/commands/obpi_cmd.py` — the launch producer and each re-entry by stage (registered security surface)
- `src/gzkit/commands/obpi_stages.py` — the verification, ceremony and sync runners
- `src/gzkit/obpi_dispatch_channel.py` — the dispatch producer's marker cache write
- `src/gzkit/commands/obpi_precomplete.py` — the precomplete producer
- `src/gzkit/commands/obpi_complete.py` — the complete producer (registered security surface)
- `src/gzkit/pipeline_stage_fence.py` — READ-ONLY import of the covering tests for the fence control; never modified by this OBPI
- `scripts/session_orientation.py` — the orientation's pipeline section
- `tests/test_pipeline_position.py` — **CREATE**, following tests/test_pipeline_stage_fence.py
- `tests/commands/test_obpi_pipeline.py` — the launch, verify, ceremony and sync marker tests
- `tests/test_pipeline_runtime.py` — the stale-marker, orphan-purge and resume-command tests
- `tests/test_obpi_dispatch_channel.py` — the dispatch marker cache tests
- `tests/scripts/test_session_orientation.py` — the orientation pipeline-section tests
- `features/pipeline_run_position.feature` — **CREATE**, following features/subagent_pipeline.feature
- `features/steps/pipeline_run_position_steps.py` — **CREATE**, following features/steps/subagent_pipeline_steps.py
- `docs/user/manpages/obpi-pipeline.md` — the marker contract the operator reads
- `docs/user/runbook.md` — the pipeline passage that tells the operator how to inspect the marker
- `docs/governance/GovZero/obpi-runtime-contract.md` — § Active Pipeline Marker Fields
- `docs/governance/pipeline-marker-migration-path.md` — the Layer-2 source and rebuild path, reconciled with the ruling on Open Design Question 2
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-15-pipeline-run-position.md`

The rulings on the Open Design Questions may add paths. Each addition is named there and is made as a brief amendment before the plan, never during implementation.

## Denied Paths

- `src/gzkit/hooks/guards.py`, `src/gzkit/hooks/scripts/pipeline.py`, `src/gzkit/hooks/scripts/routing.py`, `.claude/hooks/**` — the fence and the hooks keep their rules. They read the stage the marker reports; no guard or hook generator changes.
- `src/gzkit/commands/adr_audit.py` — the marker authenticity check (`pipeline_launched` nonce, GHI #412) and the ADR-audit marker are unchanged.
- `src/gzkit/commands/roles.py`, `src/gzkit/commands/obpi_dispatch.py` — consumers and the dispatch CLI wrapper are read, never changed.
- `src/gzkit/ledger_events.py`, `src/gzkit/events.py`, `src/gzkit/schemas/ledger.json`, `src/gzkit/ledger.py` — no ledger event type is added until Open Design Question 2 is ruled. `ledger_events.py` and `ledger.py` are registered `ledger_integrity` surfaces.
- `src/gzkit/commands/state.py`, `docs/user/manpages/state.md` — which verb rebuilds a marker is part of Open Design Question 2.
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` and its generated mirrors — the skill's stage procedure is Decision item 13 (OBPI-0.35.0-17). This OBPI adds no step the skill must tell an agent to perform, unless the ruling on Open Design Question 1 says otherwise.
- `src/gzkit/lock_manager.py`, `.gzkit/locks/**` — lock continuity is Decision item 15 (OBPI-0.35.0-19).
- The next command for a position inside a stage — Decision item 12 (OBPI-0.35.0-16). The outcome of a Stage 2 dispatch — Decision item 14 (OBPI-0.35.0-18).
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/**`, `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/**` — validated ADRs and their attested briefs are sealed records.
- `.gzkit/ledger.jsonl`, `.claude/plans/**` — never hand-written. Fixtures live in temporary directories.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The recorded position is what the RUN has reached, never what the launch command named. After the run crosses a recorded boundary, a process that did not perform the run reads that boundary from the marker, and `updated_at` is the time of the crossing. A marker that reports the launch stage for a run that has left it is the defect this OBPI repairs (GHI #1172 § Observed).
2. REQUIREMENT: The stage is one of the four canonical stages named by `pipeline_stage_fence.CANONICAL_STAGES`. The positions inside a stage that are in scope are the four GHI #1172 names: the Stage 2 task, the Stage 3 phase, the Stage 4 round and the Stage 5 step. Which boundaries inside each stage earn a record is Open Design Question 1; the plan MUST NOT choose them.
3. REQUIREMENT: A position inside a stage is never written as a new `current_stage` value. The post-Stage-2 fence refuses production writes and commits at any stage outside its authoring and committing sets, and the marker authenticity check refuses a marker whose stage is outside its canonical set, so a new stage value would trip both.
4. REQUIREMENT: Every position the marker carries is reproducible from canon and ledger. After both marker files are deleted, a rebuild from Layer 1 and Layer 2 alone yields the same stage and the same position inside it. A position with no Layer-1 or Layer-2 source MUST NOT be recorded. The Layer-2 source and the rebuilding verb are Open Design Question 2.
5. REQUIREMENT (control): A launch with nothing after it reads exactly as it does today, for the full launch and for each `--from` entry: `entry`, `current_stage` and the stage-output fields as `pipeline_stage_output` returns them. The existing launch-state assertions in `tests/commands/test_obpi_pipeline.py` pass unchanged. If one cannot, STOP and surface it; an assertion bound to an attested `REQ-0.13.0-*` is never edited to fit. The one known exception, the marker state after a successful verification, is Open Design Question 4.
6. REQUIREMENT (control): Stale-marker handling is unchanged: the `STALE_MARKER_HOURS` rule on `updated_at`, the treatment of an unreadable or timestamp-less marker as stale, `--clear-stale`, the launcher's purge of a marker whose OBPI is `attested_completed`, and the concurrency block on another OBPI's marker. `updated_at` moves only when the run crosses a boundary. A read never moves it, and a rebuild restores the time of the last recorded crossing, so neither can make an abandoned run look live.
7. REQUIREMENT: After every recorded boundary the per-OBPI marker and the legacy marker carry the same payload (`OBPI-0.13.0-02` Requirement 4). They diverge today after a dispatch, because `persist_dispatch_state` and `declare_single_driver` write only the per-OBPI file.
8. REQUIREMENT: Recording a position discards nothing the marker already carries: `nonce`, `started_at`, `entry`, `receipt_state`, `dispatch_state` and `single_driver_declaration` survive an advance unchanged.
9. REQUIREMENT: The marker's stage-output fields (`blockers`, `required_human_action`, `next_command`, `resume_point`) never contradict the recorded stage; at stage level they are what `pipeline_stage_output` returns for that stage today. The next command for a position INSIDE a stage belongs to Decision item 12 (OBPI-0.35.0-16) and is not defined here.
10. REQUIREMENT: The session orientation shows the stage reached and the position inside it for every in-flight run. `pipeline_resume_command`, the completion reminder, the post-Stage-2 fence and `gz roles` keep working against an advanced marker and act on the stage reached.
11. NEVER: remove, weaken or make conditional any pipeline control (campaign § Amendments 2026-10-04 (2): "none is removed by this entry"). Named so the review can check each: the pipeline-gate hook and the pre-commit fence, the `pipeline_launched` nonce check, the ledger-only Stage 2 dispatch credit (GHI #886), `gz obpi precomplete`, the operator-block gate, the reconcile-receipt gate and the concurrency block.
12. NEVER: let a position become gate evidence. No check added or touched by this OBPI fails closed on what a marker says about position; a missing or wrong position may warn. Dispatch credit keeps reading the ledger.
13. NEVER: add a repository-local file that stores position beside the two marker files, unless the operator rules it under Open Design Question 3.
14. ALWAYS: update the coupled docs in the same change, and correct what they misstate today. `docs/user/manpages/obpi-pipeline.md` says `--from=verify` "clears active markers on success" and `--from=ceremony` "clears active markers on exit"; the runtime keeps both markers until Stage 5. `docs/governance/GovZero/obpi-runtime-contract.md` omits `sync` from the `entry` and `current_stage` values.
15. ALWAYS: prove the exit condition on one real run as well as by test. Key Proof carries the orientation's `Active ADR pipeline state` section captured from a run that has advanced past its launch stage; this OBPI's own pipeline run qualifies. `uv run gz check` is green.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Open Design Questions (operator rules before plan)

GHI #1172 § Closure contract lists the first three as known uncertainties. The fourth follows from the code. Each needs a ruling recorded in this brief before a plan is written; the plan MUST NOT pick.

**1. Which boundaries inside a stage earn a record, and what marks them.** The runtime's verification stage has no phases and its ceremony stage has no rounds; the Stage 3 phases, the Stage 4 rounds and most Stage 5 steps exist only in the pipeline skill's procedure. The producers GHI #1172 names (launch, verification, dispatch, precomplete, complete) include none for a Stage 4 round.

- A. Record only the boundaries that a command the run already invokes marks: a Stage 2 task at `gz obpi dispatch` and the `gz task` events; Stage 3 at verification start, pass, fail and `gz obpi precomplete`; a Stage 4 round at `gz obpi present-evidence`, `gz obpi verify-packet` and each `gz obpi acceptance` review import; a Stage 5 step at `gz obpi precomplete`, `gz obpi complete` and `gz obpi sync`. The agent has nothing extra to remember. Stage 3 is coarser than the skill's phases 1, 1b, 1c and 2. Adds the acceptance and evidence command modules to the allowlist.
- B. A, plus an explicit position command the skill calls where no command marks a boundary. Finer, but the record then depends on the agent remembering to call it, which is the attention failure the review record names. Adds a CLI surface, the skill and its mirrors.
- C. Stage level only. Does not meet the GHI's boundary, which puts the four positions in scope.
- **Recommendation: A.**

**2. Whether a stage transition becomes a ledger event, and which verb rebuilds.** Rebuildability needs a Layer-2 source. `ADR-0.0.9` deferred "ledger events for stage transitions" to a Pipeline Lifecycle ADR that was never authored. `docs/governance/pipeline-marker-migration-path.md`, the deliverable of `OBPI-0.0.9-06`, names the event types, names `ADR-0.13.0` as the vehicle and names `uv run gz state --repair` as the rebuild; `gz state --repair` reconciles frontmatter only today.

- A. Derive position from events the ledger already holds (`pipeline_launched`, `task_started`, `stage2_dispatch_recorded`, `acceptance_recorded`, the completion receipt). No new event type. Position is then inferred from side effects, and a boundary with no existing event cannot be rebuilt.
- B. Each recorded boundary appends one transition event, ledger first and marker second, the order `record_dispatch` already uses. Position is declared, never inferred, and rebuild equality holds by construction. Adds `src/gzkit/ledger_events.py`, `src/gzkit/events.py`, `src/gzkit/schemas/ledger.json` and the coupled consumers of a new event type to the allowlist.
- C. A where an event exists, B only for the boundaries that have none.
- Rebuild verb: `gz state --repair` (named by `ADR-0.0.9` and the migration-path doc; adds `src/gzkit/commands/state.py` and its manpage), or the pipeline launcher rebuilding a missing marker on re-entry.
- **Recommendation: B, rebuilt by `gz state --repair`.** Inference is the larger surface for a wrong reading, and the dispatch channel already rules that credit is never inferred.

**3. "MUST NOT add a second durable state file".** `OBPI-0.13.0-02` Requirement 6 and `OBPI-0.13.0-03` Requirement 7 both say it, each scoped "This OBPI MUST NOT". The review record's first proposal is a save point written at each boundary.

- A. The constraint carries over: position lives in the two existing marker files, and the ledger is the system of record, not a second state file.
- B. A separate position or save-point file. This retires the constraint, so it goes through `docs/governance/attested-req-subject-retirement.md`.
- **Recommendation: A.** A save point is a different deliverable and is not assigned by Decision item 11.

**4. Whether the advance writes `current_stage` itself.** Two standing surfaces read that key.

- The post-Stage-2 fence refuses a commit carrying `src/**` when `current_stage` is `verify` or `ceremony`. A full launch stays at `implement` for the whole run today, so the fence binds only on a `--from` entry. Once the stage advances, the fence binds on every run, and an in-flight Stage 3 repair needs a recorded re-entry to `implement` through the runtime.
- `REQ-0.13.0-03-02` is attested: "Verify success writes marker payloads that expose the follow-up `--from=ceremony` command and `resume_point=ceremony` before cleanup." The runtime now chains from a passed verification straight into the ceremony, so after that pass the run has reached `ceremony`. `test_verify_rewrites_markers_with_verify_stage_state` asserts `current_stage=verify` at that moment.
- A. The advance writes `current_stage`. Every reader sees the stage reached; the fence does what its docstring says it is for; `REQ-0.13.0-03-02` is repaired at its surface under `docs/governance/attested-req-subject-retirement.md`, with the operator ruling what the marker reads after a passed verification.
- B. Position is written to a separate key and `current_stage` keeps the launch value. Nothing attested moves and the fence stays dormant on full launches, but every reader of `current_stage` still reads launch state, which is the contradiction GHI #1172 names.
- **Recommendation: A.**

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: § Decision item 11, "A PIPELINE RUN'S POSITION IS READABLE FROM DISK".
- [ ] Parent ADR § Intent — the 2026-10-04 amendment. It says what a repair assignment is and that no pipeline control is removed.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `docs/governance/state-doctrine.md` — the three layers and the five authority rules

**Context:**

- [ ] GHI #1172 in full: observed marker, canonical contradiction and closure contract
- [ ] `docs/governance/context-phase-review-2026-10-04-evidence/README.md` finding 4 — the run state that lives only in the conversation
- [ ] `docs/governance/build-to-1.0-campaign-2026-09-20.md` § Amendments 2026-10-04 (2)
- [ ] `ADR-0.13.0` § Intent and § Decision; `OBPI-0.13.0-02` and `OBPI-0.13.0-03` Requirements and Acceptance Criteria
- [ ] `ADR-0.0.9` § Decision and § Non-Goals; `docs/governance/pipeline-marker-migration-path.md`
- [ ] Sibling briefs OBPI-0.35.0-16 (depends on this one), -17, -18 and -19, for the seams named in Denied Paths

**Prerequisites (check existence, STOP if missing):**

- [ ] Open Design Questions 1 to 4 each carry an operator ruling recorded in this brief
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/pipeline_markers.py`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/commands/obpi_stages.py`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/test_pipeline_position.py`
- [ ] Required path exists or is intentionally created in this OBPI: `features/pipeline_run_position.feature`

**Existing Code (understand current state):**

- [ ] `src/gzkit/pipeline_markers.py` — `pipeline_marker_payload` sets the stage from the `--from` flag; `write_pipeline_markers` replaces the whole payload on every launch and re-entry; `refresh_pipeline_markers` derives the stage output from `entry`, not from the stage, so it would drop the blockers of a run whose `entry` is `full`; `find_stale_pipeline_markers` reads `updated_at`
- [ ] `src/gzkit/commands/obpi_cmd.py` — `obpi_pipeline_cmd`: the marker write, the `pipeline_launched` event carrying the nonce, and the dispatch to each stage runner
- [ ] `src/gzkit/commands/obpi_stages.py` — the verify runner writes the marker only on failure and chains into the ceremony without a write; the sync runner removes the markers at the end
- [ ] `src/gzkit/obpi_dispatch_channel.py` and `src/gzkit/pipeline_runtime.py` — `record_dispatch`, `declare_single_driver` and `persist_dispatch_state` write the per-OBPI marker only
- [ ] `src/gzkit/pipeline_stage_fence.py`, `src/gzkit/hooks/guards.py` and `src/gzkit/commands/adr_audit.py` — the readers of `current_stage` that this OBPI must leave working: the fence, the pre-commit guard, the authenticity check (which reads `started_at` for freshness, not `updated_at`) and the ADR-audit marker written with `current_stage: audit` into the same directory
- [ ] `scripts/session_orientation.py` — `collect_adr_pipeline` and `_render_adr_pipeline`
- [ ] `tests/commands/test_obpi_pipeline.py`, `tests/test_pipeline_runtime.py`, `tests/test_pipeline_stage_fence.py`, `tests/scripts/test_session_orientation.py` — fixture conventions. Several `@covers` decorators for `REQ-0.13.0-02-*` and `REQ-0.13.0-03-*` in `tests/test_pipeline_runtime.py` sit on tests of other behaviour (`REQ-0.13.0-02-02` on a plan-audit receipt test, `REQ-0.13.0-03-03` on a stale-marker test), so the launch control needs its own assertions here.
- [ ] `features/subagent_pipeline.feature` and `features/steps/subagent_pipeline_steps.py` — step conventions

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
- [ ] `docs/user/manpages/obpi-pipeline.md`, `docs/user/runbook.md`, `docs/governance/GovZero/obpi-runtime-contract.md` and `docs/governance/pipeline-marker-migration-path.md` updated (Requirement 14)

### Gate 4: BDD (Heavy only)

- [ ] `features/pipeline_run_position.feature` carries one scenario per BEHAVIOR REQ it proves, each tagged with its `@REQ-0.35.0-15-NN` id
- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run -m unittest tests.test_pipeline_position tests.commands.test_obpi_pipeline tests.test_pipeline_runtime
uv run -m unittest tests.test_obpi_dispatch_channel tests.scripts.test_session_orientation tests.test_pipeline_stage_fence
uv run -m behave features/pipeline_run_position.feature
uv run gz validate --documents --req-kind-discipline --cli-alignment
uv run gz cli audit
uv run mkdocs build --strict
```

## Demo

The acceptance feature is the demonstration. In a throwaway project it launches a run, takes it across each recorded boundary, reads the position after each one from a process that did not perform the run, then deletes both marker files, rebuilds, and compares. It exits non-zero unless every read matches. The unit module repeats the controls: a bare launch, a stale marker, and the fence against an advanced marker.

```bash
uv run -m behave features/pipeline_run_position.feature
uv run -m unittest tests.test_pipeline_position
```

The real-run half of the exit condition is not a Demo command, because `gz obpi present-evidence` runs Demo commands in a disposable copy with no live run in it. It is captured into Key Proof (Requirement 15).

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-15-01 [BEHAVIOR]: Given a run launched in full, when the run crosses into `verify`, `ceremony` or `sync`, then a process that did not perform the run reads that stage from the per-OBPI marker and from the legacy marker, with an `updated_at` later than `started_at`; the marker never reports `implement` for a run that has left Stage 2
- [ ] REQ-0.35.0-15-02 [BEHAVIOR]: Given a run inside Stage 2, 3, 4 or 5, when it crosses a boundary in the set ruled under Open Design Question 1, then a process that did not perform the run reads which Stage 2 task, Stage 3 phase, Stage 4 round or Stage 5 step the run has reached
- [ ] REQ-0.35.0-15-03 [BEHAVIOR]: Given a run that has crossed any recorded boundary, when both marker files are deleted and the marker is rebuilt from canon and ledger alone, then the rebuilt marker reports the same stage and the same position inside it as before deletion, carries a nonce that a `pipeline_launched` event for the same OBPI recorded, and has the `updated_at` of the last recorded crossing, not the time of the rebuild
- [ ] REQ-0.35.0-15-04 [BEHAVIOR]: Given a launch with nothing after it, for the full launch and for each of `--from=verify`, `--from=ceremony` and `--from=sync` at the moment of entry, when the marker is read, then `entry`, `current_stage`, `next_command` and `resume_point` are the launch values they are today and no position beyond the launch is reported
- [ ] REQ-0.35.0-15-05 [BEHAVIOR]: Given a marker whose `updated_at` is older than `STALE_MARKER_HOURS`, one that is unreadable, one with no `updated_at`, and one whose OBPI is `attested_completed`, when stale detection, `--clear-stale` and the launcher's orphan purge run, then each behaves as it did before this OBPI; and when a position is read or a marker is rebuilt, `updated_at` does not move
- [ ] REQ-0.35.0-15-06 [BEHAVIOR]: Given an in-flight run that has advanced past its launch stage, when a new process collects the session orientation, then the `Active ADR pipeline state` section names the stage reached and the position inside it, not the launch stage
- [ ] REQ-0.35.0-15-07 [BEHAVIOR]: Given a marker advanced past `implement`, when the post-Stage-2 fence, `pipeline_resume_command`, the completion reminder and `load_dispatch_state` read it, then the fence decides on the stage reached as `pipeline_stage_fence` defines, the resume command and the reminder agree with the recorded stage, `nonce`, `started_at`, `entry`, `receipt_state`, `dispatch_state` and `single_driver_declaration` are unchanged by the advance, and the per-OBPI and legacy marker files hold the same payload
- [ ] REQ-0.35.0-15-08 [SUPPORT]: `docs/user/manpages/obpi-pipeline.md` states that the marker's stage and position advance as the run crosses each recorded boundary, names the position fields, states how a deleted marker is rebuilt, and no longer says that `--from=verify` or `--from=ceremony` clears the markers; `docs/user/runbook.md` agrees with it. Witnessed by `artifact_edited` citing `docs/user/manpages/obpi-pipeline.md` + `gz validate --cli-alignment`.
- [ ] REQ-0.35.0-15-09 [SUPPORT]: `docs/governance/GovZero/obpi-runtime-contract.md` § Active Pipeline Marker Fields lists the position fields and every stage value the runtime writes, including `sync`; `docs/governance/pipeline-marker-migration-path.md` describes the Layer-2 source and the rebuild path as ruled under Open Design Question 2, not as future intent. Witnessed by `artifact_edited` citing `docs/governance/GovZero/obpi-runtime-contract.md` + `gz validate --documents`.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Change Log

<!-- Keep substantive implementation, test, documentation, and evidence
     corrections within this OBPI. Reuse existing finding identities and cite
     the affected REQ or contract clause, change, and proof/closure references.
     Group related repairs; do not log every edit or duplicate transcripts.
     This is an index to evidence, not a second acceptance ledger. Record approved
     amendments in their normative sections and reference the ruling here.
     Create a GHI only when independent work or disposition is needed, or the
     operator explicitly requests an issue; link it back to the owning work.
     Keep this subsection under Evidence so history is not treated as contract. -->

_No substantive adjustments recorded yet._

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

<!-- Link independently routed GitHub defects, one bullet per issue so status
     surfaces preserve traceability. Within-OBPI corrections belong in the
     Change Log above; they do not need a GHI. An issue link does not discharge
     an unmet acceptance obligation. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
