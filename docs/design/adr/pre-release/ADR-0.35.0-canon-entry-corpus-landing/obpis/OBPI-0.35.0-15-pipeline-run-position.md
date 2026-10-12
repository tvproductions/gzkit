---
id: OBPI-0.35.0-15-pipeline-run-position
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 15
lane: Heavy
sensitivity: security
status: Active
allowlist:
  - src/gzkit/pipeline_markers.py
  - src/gzkit/pipeline_position.py
  - src/gzkit/pipeline_runtime.py
  - src/gzkit/commands/obpi_cmd.py
  - src/gzkit/commands/obpi_stages.py
  - src/gzkit/obpi_dispatch_channel.py
  - src/gzkit/commands/obpi_precomplete.py
  - src/gzkit/commands/obpi_complete.py
  - src/gzkit/commands/obpi_present_evidence.py
  - src/gzkit/commands/obpi_verify_packet.py
  - src/gzkit/commands/obpi_acceptance.py
  - src/gzkit/commands/task.py
  - src/gzkit/pipeline_stage_fence.py
  - src/gzkit/ledger_events.py
  - src/gzkit/events.py
  - src/gzkit/schemas/ledger.json
  - src/gzkit/ledger.py
  - src/gzkit/governance/trust_audits/events.py
  - src/gzkit/ontology/corpus.py
  - src/gzkit/commands/state.py
  - scripts/session_orientation.py
  - tests/test_pipeline_position.py
  - tests/commands/test_obpi_pipeline.py
  - tests/test_pipeline_runtime.py
  - tests/test_obpi_dispatch_channel.py
  - tests/scripts/test_session_orientation.py
  - tests/test_schemas.py
  - tests/adr/test_state_doctrine.py
  - features/pipeline_run_position.feature
  - features/steps/pipeline_run_position_steps.py
  - docs/user/manpages/obpi-pipeline.md
  - docs/user/manpages/state.md
  - docs/user/runbook.md
  - docs/governance/GovZero/obpi-runtime-contract.md
  - docs/governance/pipeline-marker-migration-path.md
  - docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md
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
  - uv run -m unittest tests.test_schemas tests.adr.test_state_doctrine
  - uv run -m behave features/pipeline_run_position.feature
  - uv run gz validate --documents --req-kind-discipline --cli-alignment
  - uv run gz cli audit
  - uv run mkdocs build --strict
tasks:
  - TASK-0.35.0-15-01-01
  - TASK-0.35.0-15-02-01
  - TASK-0.35.0-15-03-01
  - TASK-0.35.0-15-04-01
  - TASK-0.35.0-15-05-01
  - TASK-0.35.0-15-06-01
  - TASK-0.35.0-15-07-01
  - TASK-0.35.0-15-08-01
  - TASK-0.35.0-15-09-01
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

The contract change is the active pipeline marker payload, which `docs/governance/GovZero/obpi-runtime-contract.md` documents as a runtime contract read by hooks, the session orientation and operators. Since the ruling on Open Design Question 2 it is also the ledger schema, which gains a stage-transition event, and `uv run gz state --repair`, which gains the marker rebuild.

**Sensitivity: security.** These Allowed Paths are registered security surfaces in `data/security_surfaces.json`: `src/gzkit/pipeline_markers.py` (`subprocess_user_input`), `src/gzkit/commands/obpi_cmd.py` and `src/gzkit/commands/obpi_complete.py` (`auth_boundaries`), and `src/gzkit/ledger_events.py` and `src/gzkit/ledger.py` (`ledger_integrity`). `.gzkit/rules/security-sensitivity.md` § `gz validate --sensitivity` clause 1 requires the declaration, so the frontmatter carries it and Gate 5 runs the heightened walkthrough.

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

- `src/gzkit/pipeline_markers.py` — marker payload, refresh, resume command and stale-marker handling (registered security surface). Every marker file write stays here.
- `src/gzkit/pipeline_position.py` — **CREATE** (Open Design Question 6, ruled 2026-10-11): the run-position concept: the position model, the pure ledger replay, the recorder (ledger first, marker second) and the payload a rebuild writes. It depends on `src/gzkit/pipeline_markers.py` and is never imported by it.
- `src/gzkit/pipeline_runtime.py` — the re-export surface and the dispatch-state marker cache writer
- `src/gzkit/commands/obpi_cmd.py` — the launch producer and each re-entry by stage (registered security surface)
- `src/gzkit/commands/obpi_stages.py` — the verification, ceremony and sync runners
- `src/gzkit/obpi_dispatch_channel.py` — the dispatch producer's marker cache write
- `src/gzkit/commands/obpi_precomplete.py` — the precomplete producer
- `src/gzkit/commands/obpi_complete.py` — the complete producer (registered security surface)
- `src/gzkit/commands/obpi_present_evidence.py` — a Stage 4 round producer (Open Design Question 1, ruled)
- `src/gzkit/commands/obpi_verify_packet.py` — a Stage 4 round producer (Open Design Question 1, ruled)
- `src/gzkit/commands/obpi_acceptance.py` — the Stage 4 review-import producer (Open Design Question 1, ruled)
- `src/gzkit/commands/task.py` — the `gz task` verbs, which mark a Stage 2 task boundary (Open Design Question 1, ruled)
- `src/gzkit/pipeline_stage_fence.py` — READ-ONLY import of the covering tests for the fence control; never modified by this OBPI
- `src/gzkit/ledger_events.py` — the constructor for the stage-transition event (registered security surface)
- `src/gzkit/events.py` — the typed model of that event
- `src/gzkit/schemas/ledger.json` — its schema entry
- `src/gzkit/ledger.py` — the constructor's export and the artifact-graph handling of the event (registered security surface)
- `src/gzkit/governance/trust_audits/events.py` — the handler-coverage declaration that `gz validate --event-handlers` reads
- `src/gzkit/ontology/corpus.py` — the ontology's roster of ledger event types
- `src/gzkit/commands/state.py` — `state_repair`, which gains the marker rebuild and keeps its frontmatter reconciliation
- `scripts/session_orientation.py` — the orientation's pipeline section
- `tests/test_pipeline_position.py` — **CREATE**, following tests/test_pipeline_stage_fence.py
- `tests/commands/test_obpi_pipeline.py` — the launch, verify, ceremony and sync marker tests
- `tests/test_pipeline_runtime.py` — the stale-marker, orphan-purge and resume-command tests
- `tests/test_obpi_dispatch_channel.py` — the dispatch marker cache tests
- `tests/scripts/test_session_orientation.py` — the orientation pipeline-section tests
- `tests/test_schemas.py` — the event-model table every ledger event type is listed in
- `tests/adr/test_state_doctrine.py` — the existing `gz state --repair` tests
- `features/pipeline_run_position.feature` — **CREATE**, following features/subagent_pipeline.feature
- `features/steps/pipeline_run_position_steps.py` — **CREATE**, following features/steps/subagent_pipeline_steps.py
- `docs/user/manpages/obpi-pipeline.md` — the marker contract the operator reads
- `docs/user/manpages/state.md` — `--repair` now rebuilds pipeline markers
- `docs/user/runbook.md` — the pipeline passage that tells the operator how to inspect the marker
- `docs/governance/GovZero/obpi-runtime-contract.md` — § Active Pipeline Marker Fields
- `docs/governance/pipeline-marker-migration-path.md` — the Layer-2 source and rebuild path, reconciled with the ruling on Open Design Question 2
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md` — the dated amendment note on the `REQ-0.13.0-03-02` line only (Requirement 16); nothing else in this sealed brief changes
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-15-pipeline-run-position.md`

The rulings on the Open Design Questions may add paths. Each addition is named there and is made as a brief amendment. An addition that implementation shows is warranted is assessed at that point, with its consumers and coupled surfaces named, and is made only on the operator's ruling (Open Design Question 6). This replaces the earlier wording, "never during implementation".

## Denied Paths

- `src/gzkit/hooks/guards.py`, `src/gzkit/hooks/scripts/pipeline.py`, `src/gzkit/hooks/scripts/routing.py`, `.claude/hooks/**` — the fence and the hooks keep their rules. They read the stage the marker reports; no guard or hook generator changes.
- `src/gzkit/commands/adr_audit.py` — the marker authenticity check (`pipeline_launched` nonce, GHI #412) and the ADR-audit marker are unchanged.
- `src/gzkit/commands/roles.py`, `src/gzkit/commands/obpi_dispatch.py` — consumers and the dispatch CLI wrapper are read, never changed.
- `data/ledger_vocabulary_grandfather.json` — the new event type fires in this OBPI's own change before the tree is checked, and is never disclosed there as never-fired.
- A marker rebuild inside the pipeline launcher or a hook — the rebuild is `uv run gz state --repair` alone (Open Design Question 2, ruled).
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` and its generated mirrors — the skill's stage procedure is Decision item 13 (OBPI-0.35.0-17). This OBPI adds no step the skill must tell an agent to perform (Open Design Question 1, ruled).
- `src/gzkit/lock_manager.py`, `.gzkit/locks/**` — lock continuity is Decision item 15 (OBPI-0.35.0-19).
- The next command for a position inside a stage — Decision item 12 (OBPI-0.35.0-16). The outcome of a Stage 2 dispatch — Decision item 14 (OBPI-0.35.0-18).
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/**`, `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/**` — validated ADRs and their attested briefs are sealed records. The one exception is the requirement-line note named in Allowed Paths (operator ruling 2026-10-04).
- `.gzkit/ledger.jsonl`, `.claude/plans/**` — never hand-written. Fixtures live in temporary directories.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The recorded position is what the RUN has reached, never what the launch command named. After the run crosses a recorded boundary, a process that did not perform the run reads that boundary from the marker, and `updated_at` is the time of the crossing. A marker that reports the launch stage for a run that has left it is the defect this OBPI repairs (GHI #1172 § Observed).
2. REQUIREMENT: The stage is one of the four canonical stages named by `pipeline_stage_fence.CANONICAL_STAGES`. The positions inside a stage that are in scope are the four GHI #1172 names: the Stage 2 task, the Stage 3 phase, the Stage 4 round and the Stage 5 step. The boundaries that earn a record are the ones a command the run already invokes marks (operator ruling 2026-10-04, Open Design Question 1): a Stage 2 task at `gz obpi dispatch` and at the `gz task` events; Stage 3 at verification start, pass and fail and at `gz obpi precomplete`; a Stage 4 round at `gz obpi present-evidence`, `gz obpi verify-packet` and each `gz obpi acceptance` review import; a Stage 5 step at `gz obpi precomplete`, `gz obpi complete` and `gz obpi sync`. No position command is added and the skill gains no step. The plan MUST NOT add a boundary or drop one. **Amended 2026-10-11 on operator rulings (Open Design Questions 7, 8, 9 and 10), each made when implementation showed how the commands are invoked. The amended set governs where it differs from the sentence above.** (a) Only a command that begins a stage's work moves the stage (Question 9): the launch and each `--from` re-entry, the verify runner (to `verify`), the ceremony runner's entry and `gz obpi present-evidence` (to `ceremony`), `gz obpi complete` (to `sync`), and `gz task start` and `gz obpi dispatch` (to `implement`, the recorded re-entry). (b) A check or a bookkeeping event records its position inside the stage the run has already reached and never changes that stage: `gz obpi precomplete`, `gz obpi verify-packet`, an adversarial or human review import, the verification pass and fail, and `gz task complete`, `block` and `escalate`. The position's kind is the kind of the stage reached (task, phase, round or step) and its label names the command's own boundary. (c) A spec or quality review import records nothing (Question 7). (d) `gz obpi sync` is not a recorded boundary, because the completion receipt ends the run; `gz obpi complete` records its step as its transaction starts, before that receipt (Question 8). (e) The ceremony runner's entry is a recorded boundary (Question 10).
3. REQUIREMENT: A position inside a stage is never written as a new `current_stage` value. The post-Stage-2 fence refuses production writes and commits at any stage outside its authoring and committing sets, and the marker authenticity check refuses a marker whose stage is outside its canonical set, so a new stage value would trip both.
4. REQUIREMENT: Every position the marker carries is reproducible from canon and ledger. After both marker files are deleted, a rebuild from Layer 1 and Layer 2 alone yields the same stage and the same position inside it. A position with no Layer-1 or Layer-2 source MUST NOT be recorded. The Layer-2 source and the rebuilding verb are ruled under Open Design Question 2 and stated in Requirement 18.
5. REQUIREMENT (control): A launch with nothing after it reads exactly as it does today, for the full launch and for each `--from` entry: `entry`, `current_stage`, `blockers`, `required_human_action` and `resume_point` as the launch writes them. This brief leaves `next_command` as it finds it and pins no value for it: Decision item 12 (OBPI-0.35.0-16) re-derives it from the run's position (operator ruling 2026-10-04 on that brief's Open Design Question 2). The existing launch-state assertions in `tests/commands/test_obpi_pipeline.py` pass unchanged. If one cannot, STOP and surface it; an assertion bound to an attested `REQ-0.13.0-*` is never edited to fit. The one known exception, the marker state after a successful verification, is ruled under Open Design Question 4 and carried by Requirement 16.
6. REQUIREMENT (control): Stale-marker handling is unchanged: the `STALE_MARKER_HOURS` rule on `updated_at`, the treatment of an unreadable or timestamp-less marker as stale, `--clear-stale`, the launcher's purge of a marker whose OBPI is `attested_completed`, and the concurrency block on another OBPI's marker. `updated_at` moves only when the run crosses a boundary. A read never moves it, and a rebuild restores the time of the last recorded crossing, so neither can make an abandoned run look live.
7. REQUIREMENT: After every recorded boundary the per-OBPI marker and the legacy marker carry the same payload (`OBPI-0.13.0-02` Requirement 4). They diverge today after a dispatch, because `persist_dispatch_state` and `declare_single_driver` write only the per-OBPI file.
8. REQUIREMENT: Recording a position discards nothing the marker already carries: `nonce`, `started_at`, `entry`, `receipt_state`, `dispatch_state` and `single_driver_declaration` survive an advance unchanged.
9. REQUIREMENT: The marker's stage-output fields (`blockers`, `required_human_action`, `next_command`, `resume_point`) never contradict the recorded stage; at stage level they are what `pipeline_stage_output` returns for that stage today. The next command for a position INSIDE a stage belongs to Decision item 12 (OBPI-0.35.0-16) and is not defined here; that brief also re-derives the stage-level `next_command` from position, so no acceptance criterion of this brief pins a `next_command` value.
10. REQUIREMENT: The session orientation shows the stage reached and the position inside it for every in-flight run. `pipeline_resume_command`, the completion reminder, the post-Stage-2 fence and `gz roles` keep working against an advanced marker and act on the stage reached.
11. NEVER: remove, weaken or make conditional any pipeline control (campaign § Amendments 2026-10-04 (2): "none is removed by this entry"). Named so the review can check each: the pipeline-gate hook and the pre-commit fence, the `pipeline_launched` nonce check, the ledger-only Stage 2 dispatch credit (GHI #886), `gz obpi precomplete`, the operator-block gate, the reconcile-receipt gate and the concurrency block.
12. NEVER: let a position become gate evidence. No check added or touched by this OBPI fails closed on what a marker says about position; a missing or wrong position may warn. Dispatch credit keeps reading the ledger.
13. NEVER: add a repository-local file that stores position beside the two marker files (operator ruling 2026-10-04, Open Design Question 3).
14. ALWAYS: update the coupled docs in the same change, and correct what they misstate today. `docs/user/manpages/obpi-pipeline.md` says `--from=verify` "clears active markers on success" and `--from=ceremony` "clears active markers on exit"; the runtime keeps both markers until Stage 5. `docs/governance/GovZero/obpi-runtime-contract.md` omits `sync` from the `entry` and `current_stage` values.
15. ALWAYS: prove the exit condition on one real run as well as by test. Key Proof carries the orientation's `Active ADR pipeline state` section captured from a run that has advanced past its launch stage; this OBPI's own pipeline run qualifies. `uv run gz check` is green.
16. ALWAYS (operator ruling 2026-10-04, Open Design Question 4): amend `REQ-0.13.0-03-02` in place in the same change that lands the advance. Its line in the sealed `OBPI-0.13.0-03` brief keeps the attested text and gains a dated note that quotes the ruling and says the marker reports the stage the run has reached after a passed verification. The note names no command line, so it stays true when OBPI-0.35.0-16 re-derives `next_command`. The form is the note on `REQ-0.0.14-03-07` (`docs/governance/attested-req-subject-retirement.md` § Worked example 4). The covering test asserts the amended behaviour and its docstring records why.
17. ALWAYS (operator ruling 2026-10-04): the `@covers` binding for each of `REQ-0.13.0-02-01`, `REQ-0.13.0-02-02`, `REQ-0.13.0-03-02` and `REQ-0.13.0-03-03` sits on the test that asserts that requirement. Each is moved off the test it sits on today, which asserts something else: a marker-lookup test, a plan-audit receipt test, a verify-commands test with a ceremony-entry test, and a stale-marker test. The move and its reason are recorded in the test's docstring and the commit body. No binding is dropped.
18. REQUIREMENT (operator ruling 2026-10-04, Open Design Question 2): each recorded boundary appends one stage-transition event to the ledger before the marker is written, the order `record_dispatch` uses. A position is never inferred from another event's side effect. `uv run gz state --repair` rebuilds a missing or deleted marker from those events and keeps its frontmatter reconciliation; nothing else rebuilds one. The event type is added with every coupled surface a ledger event type has (the model, the schema entry, the constructor, the handler-coverage declaration, the ontology roster and the event-model test table), following `pipeline_marker_purged`. `docs/user/manpages/state.md` states the rebuild.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Open Design Questions (operator rules before plan)

GHI #1172 § Closure contract lists the first three as known uncertainties. The fourth follows from the code. Each needs a ruling recorded in this brief before a plan is written; the plan MUST NOT pick.

**1. Which boundaries inside a stage earn a record, and what marks them.** The runtime's verification stage has no phases and its ceremony stage has no rounds; the Stage 3 phases, the Stage 4 rounds and most Stage 5 steps exist only in the pipeline skill's procedure. The producers GHI #1172 names (launch, verification, dispatch, precomplete, complete) include none for a Stage 4 round.

- A. Record only the boundaries that a command the run already invokes marks: a Stage 2 task at `gz obpi dispatch` and the `gz task` events; Stage 3 at verification start, pass, fail and `gz obpi precomplete`; a Stage 4 round at `gz obpi present-evidence`, `gz obpi verify-packet` and each `gz obpi acceptance` review import; a Stage 5 step at `gz obpi precomplete`, `gz obpi complete` and `gz obpi sync`. The agent has nothing extra to remember. Stage 3 is coarser than the skill's phases 1, 1b, 1c and 2. Adds the acceptance and evidence command modules to the allowlist.
- B. A, plus an explicit position command the skill calls where no command marks a boundary. Finer, but the record then depends on the agent remembering to call it, which is the attention failure the review record names. Adds a CLI surface, the skill and its mirrors.
- C. Stage level only. Does not meet the GHI's boundary, which puts the four positions in scope.
- **Recommendation: A.**
- **RULED 2026-10-04: A.** Asked "which boundaries inside a stage earn a record?" with the three options above, the operator answered, verbatim: "A". Requirement 2 carries the set. The allowlist gains the three Stage 4 command modules the option names, and `src/gzkit/commands/task.py`: under the ruling on Open Design Question 2 a position is never inferred from another event, so the `gz task` verbs append the transition themselves.

**2. Whether a stage transition becomes a ledger event, and which verb rebuilds.** Rebuildability needs a Layer-2 source. `ADR-0.0.9` deferred "ledger events for stage transitions" to a Pipeline Lifecycle ADR that was never authored. `docs/governance/pipeline-marker-migration-path.md`, the deliverable of `OBPI-0.0.9-06`, names the event types, names `ADR-0.13.0` as the vehicle and names `uv run gz state --repair` as the rebuild; `gz state --repair` reconciles frontmatter only today.

- A. Derive position from events the ledger already holds (`pipeline_launched`, `task_started`, `stage2_dispatch_recorded`, `acceptance_recorded`, the completion receipt). No new event type. Position is then inferred from side effects, and a boundary with no existing event cannot be rebuilt.
- B. Each recorded boundary appends one transition event, ledger first and marker second, the order `record_dispatch` already uses. Position is declared, never inferred, and rebuild equality holds by construction. Adds `src/gzkit/ledger_events.py`, `src/gzkit/events.py`, `src/gzkit/schemas/ledger.json` and the coupled consumers of a new event type to the allowlist.
- C. A where an event exists, B only for the boundaries that have none.
- Rebuild verb: `gz state --repair` (named by `ADR-0.0.9` and the migration-path doc; adds `src/gzkit/commands/state.py` and its manpage), or the pipeline launcher rebuilding a missing marker on re-entry.
- **Recommendation: B, rebuilt by `gz state --repair`.** Inference is the larger surface for a wrong reading, and the dispatch channel already rules that credit is never inferred.
- **RULED 2026-10-04: B, rebuilt by `gz state --repair`.** Asked "does a stage transition become a ledger event?" with the three options above, the operator answered, verbatim: "B". Asked "which command rebuilds a deleted marker from the ledger?" with `gz state --repair` as option A, the launcher as B and both as C, the operator answered, verbatim: "A". Requirement 18 carries both.

**3. "MUST NOT add a second durable state file".** `OBPI-0.13.0-02` Requirement 6 and `OBPI-0.13.0-03` Requirement 7 both say it, each scoped "This OBPI MUST NOT". The review record's first proposal is a save point written at each boundary.

- A. The constraint carries over: position lives in the two existing marker files, and the ledger is the system of record, not a second state file.
- B. A separate position or save-point file. This retires the constraint, so it goes through `docs/governance/attested-req-subject-retirement.md`.
- **Recommendation: A.** A save point is a different deliverable and is not assigned by Decision item 11.
- **RULED 2026-10-04: A.** Asked whether the constraint against a second durable state file carries over, the operator answered, verbatim: "A". Position lives in the two existing marker files and the ledger is the system of record. Requirement 13 carries it.

**4. Whether the advance writes `current_stage` itself.** Two standing surfaces read that key.

- The post-Stage-2 fence refuses a commit carrying `src/**` when `current_stage` is `verify` or `ceremony`. A full launch stays at `implement` for the whole run today, so the fence binds only on a `--from` entry. Once the stage advances, the fence binds on every run, and an in-flight Stage 3 repair needs a recorded re-entry to `implement` through the runtime.
- `REQ-0.13.0-03-02` is attested: "Verify success writes marker payloads that expose the follow-up `--from=ceremony` command and `resume_point=ceremony` before cleanup." The runtime now chains from a passed verification straight into the ceremony, so after that pass the run has reached `ceremony`. `test_verify_rewrites_markers_with_verify_stage_state` asserts `current_stage=verify` at that moment.
- A. The advance writes `current_stage`. Every reader sees the stage reached; the fence does what its docstring says it is for; `REQ-0.13.0-03-02` is repaired at its surface under `docs/governance/attested-req-subject-retirement.md`, with the operator ruling what the marker reads after a passed verification.
- B. Position is written to a separate key and `current_stage` keeps the launch value. Nothing attested moves and the fence stays dormant on full launches, but every reader of `current_stage` still reads launch state, which is the contradiction GHI #1172 names.
- **Recommendation: A.**
- **RULED 2026-10-04: A.** Asked "when a run moves to the next stage, does the marker's `current_stage` change?", the operator answered, verbatim: "A". Two rulings followed the same day, each answered "A": `REQ-0.13.0-03-02` is amended in place (Requirement 16), and each misplaced `@covers` binding moves to the test that asserts its requirement (Requirement 17).

**5. Which stage `gz obpi precomplete` records.** Requirement 2 lists `gz obpi precomplete` as a boundary in both the Stage 3 set and the Stage 5 set, and one invocation records one transition.

- A. Stage 5 step only: precomplete records `stage=sync`, step `precomplete`. Matches the skill (Stage 5 Step 0); Stage 3 ends at verification pass or fail.
- B. Stage 3 phase only.
- C. Two transitions per invocation.
- **Recommendation: A.**
- **RULED 2026-10-11: A.** Asked which stage a precomplete records, with the three options above, the operator answered, verbatim: "Stage 5 step only (Recommended)". Requirement 2's Stage 3 mention of precomplete is read as a drafting overlap; the set of boundaries is otherwise unchanged.
- **SUPERSEDED 2026-10-11, the same day.** The question was put on a wrong premise: the agent had not read `_pipeline_verification_commands` (`src/gzkit/commands/obpi_stages.py`), which appends `gz obpi precomplete` as the verify runner's last command. Requirement 2 lists precomplete under Stage 3 and Stage 5 because it runs in both; under ruling A every Stage 3 run would have recorded `verify`, `sync`, `verify`, `ceremony`. Asked again with the fact stated ("Which stage should it record? This would supersede the Question 5 ruling I obtained on a wrong premise") and the options stage-relative, always Stage 5, always Stage 3, the operator answered, verbatim: "Stage-relative (Recommended)". Precomplete records the Stage 3 phase when the run is at `verify` and the Stage 5 step otherwise. **This re-ruling was itself superseded the same day by Question 9**, after two independent reviews showed that its "otherwise" arm let a check move the stage the fence reads.

**6. Where the run-position code lives (raised in Stage 2, 2026-10-11).** The first implementation put the position model, the replay and the marker advance in `src/gzkit/pipeline_markers.py`, which grew from 825 to 976 lines against the 600-line guidance in `.gzkit/rules/pythonic.md` and gained a second reason to change, the ledger event shape (quality review `arb-step-qualityreview-59190a1829eb48e2bd0ea32ef4fb3a9c`, finding QR1-AUX-03). The recorder was planned for `src/gzkit/obpi_dispatch_channel.py` and the rebuild for `src/gzkit/commands/state.py`, so the concept was spread across three modules. Allowed Paths then said an addition is "never" made "during implementation".

- Assessment at the point of growth. Consumers of the position code: `src/gzkit/pipeline_markers.py`, `src/gzkit/pipeline_runtime.py`, `src/gzkit/obpi_dispatch_channel.py`, three test modules and the BDD steps, all already allowlisted; a new module adds no consumer. `gz airlock in --dry-run` and `gz ontology reach` could not size the change: source modules are not ontology nodes (`ADR-0.33.0` § Calibration frontier), so the assessment was made by reading the importers. Keeping every marker file write in `src/gzkit/pipeline_markers.py` leaves the registered security surface unchanged, so `data/security_surfaces.json` needs no edit.
- A. Full concept: a new `src/gzkit/pipeline_position.py` owns the position model, the pure replay, the recorder and the rebuild payload; `src/gzkit/pipeline_markers.py` keeps marker file I/O; the dependency runs one way.
- B. The model and the replay only move; the recorder and the rebuild stay as planned.
- C. No new module; the extraction is a follow-up.
- **Recommendation: A.**
- **RULED 2026-10-11: A.** The operator first said of the freeze, verbatim: "that might be outmoded thinking" and "The impact of new additions is the best time to consider the implications of addition"; then, of the extraction: "it just seems that the point of insertion/growth is the time to consider the design." Asked "Do you ratify amending the OBPI-0.35.0-15 brief to add `src/gzkit/pipeline_position.py`, and if so, how much moves into it?" with the three options above, the operator answered, verbatim: "Full concept (Recommended)". Allowed Paths carries the path and the reworded closing sentence. No requirement and no acceptance criterion changes.

**7. Which review imports record a position (raised in Stage 2, 2026-10-11).** `gz obpi acceptance` imports the spec and quality reviews in Stage 2 and the adversarial review in Stage 4. Requirement 2 names "each `gz obpi acceptance` review import" as a Stage 4 round. Recording `ceremony` for every import would make a run still in Stage 2 read `ceremony` and arm the post-Stage-2 fence during implementation. The imported review carries its own stage.

- A. Adversarial and human-review imports record the Stage 4 round; spec and quality imports record nothing.
- B. All imports record, each in its own stage; this adds a Stage 2 boundary to the set ruled under Question 1.
- C. Every import records `ceremony`.
- **Recommendation: A.**
- **RULED 2026-10-11: A.** Asked "Which imports record a position?" with the three options above, the operator answered, verbatim: "Stage 4 imports only (Recommended)". Requirement 2 carries it.

**8. Where a run ends, and what records in Stage 5 (raised in Stage 2, 2026-10-11).** `gz obpi complete` emits the completion receipt. `gz obpi sync` runs after it, and in the pipeline skill's flow after the markers have been removed; its handler, `obpi_reconcile_cmd`, is in `src/gzkit/commands/status.py`, outside Allowed Paths. A run cannot both end at its receipt and record boundaries after it.

- A. The receipt ends the run. `gz obpi complete` records its step as its transaction starts, before the receipt. `gz obpi sync` leaves the boundary set. Stage 5 records precomplete and complete.
- B. A run ends at a recorded `sync` step; this adds `src/gzkit/commands/status.py` to Allowed Paths and needs the rebuild to skip completed OBPIs separately.
- C. Stage 5 records precomplete only.
- **Recommendation: A.**
- **RULED 2026-10-11: A.** Asked "Where does a run end, and what records in Stage 5?" with the three options above, the operator answered, verbatim: "Receipt ends the run (Recommended)". Requirement 2 carries it. A position recorded at `complete` says the run reached that step, not that completion succeeded; the outcome is the receipt.

**9. Which commands may move the stage the fence reads (raised by the Task 2 reviews, 2026-10-11).** As first built, every boundary command recorded its own stage. `gz task complete`, `block` and `escalate` therefore returned a run at `ceremony` to `implement`, reopening production writes on a bookkeeping event without the launcher's gates; and `gz obpi precomplete`, a check, moved a run at `ceremony` to `sync`, the one post-authoring stage where the pre-commit fence admits a production commit, and a run at `implement` to `sync`. The quality review (`arb-step-qualityreview-55341fa39e0645d1a6b3be30cca6d1f4`, QR2-AUX-fence-input-moved-by-non-entry-commands) and both spec reviews raised it for the operator's reading of Requirement 11. The fence code is untouched in every option.

- A. Work-starting commands only move the stage: the launch, the verify runner, the ceremony runner, `gz obpi present-evidence`, `gz obpi complete`, `gz task start` and `gz obpi dispatch`. Checks and bookkeeping record their position inside the stage the run has reached and never change it.
- B. As built: every boundary records its own stage.
- C. Only the `gz task` verbs are narrowed; precomplete keeps the stage-relative ruling.
- **Recommendation: A.**
- **RULED 2026-10-11: A.** Asked "Which commands may move the stage that the post-Stage-2 fence reads?" with the three options above, the operator answered, verbatim: "Work-starting only (Recommended)". Requirement 2 (a) and (b) carry it. It supersedes the Question 5 re-ruling. A run reaches `sync` at `gz obpi complete` or at a `--from=sync` launch, and never at a check.

**10. The ceremony runner's entry (raised by the Task 2 quality review, 2026-10-11).** The ceremony runner records its entry, which REQ-0.35.0-15-01 and Requirement 16 need after a passed verification, but Requirement 2's Stage 4 list named only `gz obpi present-evidence`, `gz obpi verify-packet` and the review import, and said the plan must add no boundary (QR2-AUX-ceremony-entry-outside-requirement-2-list).

- A. Requirement 2 names the ceremony runner's entry as a recorded boundary.
- B. The ceremony runner records nothing, and the marker stays at `verify` after a passed verification until `gz obpi present-evidence` runs, which contradicts the Question 4 ruling.
- **Recommendation: A.**
- **RULED 2026-10-11: A.** Asked "Ratify adding it to Requirement 2?", the operator answered, verbatim: "Ratify (Recommended)". Requirement 2 (e) carries it.

**11. Whether the blocker-summary cut is policy (raised in Task 2 fix cycle 1, 2026-10-11).** A failed verification's blockers go onto the transition event, and the quality review found the whole command output was written to the append-only ledger (QR2-AUX-unbounded-blockers-on-ledger). The repair cuts each blocker to a one-line summary of 240 characters. Its constant, named in the policy shape, tripped `gz validate --config-registry`, whose recovery is "Put the value in the config surface, or rename it out of the policy shape if it is an implementation detail" (GHI #1066). The roster's own description says the name pattern is deliberately broad and that "a reader judges individual rows". Nothing gates on the number, and the console still prints the full output. Dropping the output from the ledger is not available: an attested test pins the marker's blocker as command plus detail.

- A. Implementation detail: rename it out of the policy shape, with a comment saying what it is.
- B. Config surface: `data/pipeline_position.json` and its `data/config_registry.json` entry join Allowed Paths, and the recorder must tolerate a missing registry without failing its host.
- C. Reuse the ARB step receipt's retention default.
- **Recommendation: A.**
- **RULED 2026-10-11: A.** Asked "Is it policy that belongs in the config surface, or an implementation detail?" with the three options above, the operator answered, verbatim: "Implementation detail (Recommended)". The constant is renamed and commented; no path is added.

**12. When a run stops being in flight, and a third fix cycle (raised by the third Task 2 review round, 2026-10-11).** Task 2 used both fix cycles the pipeline allows. The third quality review (`arb-step-qualityreview-77c07f52211d411382fa73ef9e941844`) closed the three earlier findings and accepted both proofs, then refuted REQ-0.35.0-15-02 on `fc2-REQ02-a-retired-siblings-unreceipted-launch-is-still-a-run-in-flight`: the recorder ended a run only at `obpi_receipt_emitted`, so a launched OBPI later parked or withdrawn stayed in flight for good. The live ledger held two: `OBPI-0.0.37-17`, launched then withdrawn, and a second, launched twice then parked, whose ADR package is no longer on disk (its id is in the `obpi_blocked_on_operator` ledger row for this brief). The block was recorded with `gz obpi block` and put to the operator. Question 8 ruled where a completed run ends; it did not rule a retired one.

- A. One more fix cycle, scoped to this rule: a run ends at its completion receipt, or when its OBPI is parked or withdrawn, which is how the launcher's `active_prefix_matches` already resolves an id. If the next round refutes REQ-0.35.0-15-02 again, stop and escalate the design; no fourth cycle.
- B. As A, and a run also ends when its lock is released with an abandon category. This reads lock events, which Decision item 15 (OBPI-0.35.0-19) owns.
- C. Hold the block.
- **Recommendation: A.**
- **RULED 2026-10-11: A.** Asked "How do you rule?" with the three options above, the operator answered, verbatim: "Third cycle, retirement ends a run (Recommended)". The block was cleared with `gz obpi unblock` on that ruling. A launch abandoned with no ledger event still reads as in flight; that is recorded under Tracked Defects for OBPI-0.35.0-19.

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
- [ ] `src/gzkit/commands/obpi_present_evidence.py`, `src/gzkit/commands/obpi_verify_packet.py`, `src/gzkit/commands/obpi_acceptance.py` and `src/gzkit/commands/task.py` — what each writes to the ledger today, and where a stage-transition event is appended beside it
- [ ] `src/gzkit/obpi_dispatch_channel.py` and `src/gzkit/pipeline_runtime.py` — `record_dispatch`, `declare_single_driver` and `persist_dispatch_state` write the per-OBPI marker only
- [ ] `src/gzkit/pipeline_stage_fence.py`, `src/gzkit/hooks/guards.py` and `src/gzkit/commands/adr_audit.py` — the readers of `current_stage` that this OBPI must leave working: the fence, the pre-commit guard, the authenticity check (which reads `started_at` for freshness, not `updated_at`) and the ADR-audit marker written with `current_stage: audit` into the same directory
- [ ] `scripts/session_orientation.py` — `collect_adr_pipeline` and `_render_adr_pipeline`
- [ ] `src/gzkit/commands/state.py` — `state_repair` reconciles brief frontmatter from the ledger and rebuilds no marker today
- [ ] `src/gzkit/ledger_events.py` — `pipeline_marker_purged_event`, with its entries in `src/gzkit/events.py`, `src/gzkit/schemas/ledger.json`, `src/gzkit/ledger.py`, `src/gzkit/governance/trust_audits/events.py`, `src/gzkit/ontology/corpus.py` and `tests/test_schemas.py`: the precedent for adding a ledger event type
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
- [ ] `docs/user/manpages/obpi-pipeline.md`, `docs/user/runbook.md`, `docs/governance/GovZero/obpi-runtime-contract.md` and `docs/governance/pipeline-marker-migration-path.md` updated (Requirement 14); `docs/user/manpages/state.md` updated (Requirement 18)

### Gate 4: BDD (Heavy only)

- [ ] `features/pipeline_run_position.feature` carries one scenario per BEHAVIOR REQ it proves, each tagged with its `@REQ-0.35.0-15-NN` id
- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run -m unittest tests.test_pipeline_position tests.commands.test_obpi_pipeline tests.test_pipeline_runtime
uv run -m unittest tests.test_obpi_dispatch_channel tests.scripts.test_session_orientation tests.test_pipeline_stage_fence
uv run -m unittest tests.test_schemas tests.adr.test_state_doctrine
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
- [ ] REQ-0.35.0-15-03 [BEHAVIOR]: Given a run that has crossed any recorded boundary, when both marker files are deleted and `uv run gz state --repair` rebuilds the marker from canon and ledger alone, then the rebuilt marker reports the same stage and the same position inside it as before deletion, carries a nonce that a `pipeline_launched` event for the same OBPI recorded, and has the `updated_at` of the last recorded crossing, not the time of the rebuild
- [ ] REQ-0.35.0-15-04 [BEHAVIOR]: Given a launch with nothing after it, for the full launch and for each of `--from=verify`, `--from=ceremony` and `--from=sync` at the moment of entry, when the marker is read, then `entry`, `current_stage` and `resume_point` are the launch values they are today and no position beyond the launch is reported; `next_command` is not asserted here
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

- **2026-10-11, plan task cut.** The first plan grouped work by surface, so its Task 1 completed no REQ and could not be reviewed (`acceptance_context._review_subject` requires an executed proof for every scoped obligation). The plan was re-cut by the REQs each task completes and re-audited PASS. No contract clause changed.
- **2026-10-11, Open Design Question 5 (ruled).** `gz obpi precomplete` records a Stage 5 step only. Requirement 2's Stage 3 mention is read as a drafting overlap.
- **2026-10-11, Allowed Paths bullet split.** The three Stage 4 producers shared one bullet, which `gz plan audit` read as one path. Each now has its own line; no path was added or removed.
- **2026-10-11, REQ-0.35.0-15-04 covering test.** The first bound test compared the marker to values computed by the code under test. It was replaced by a CLI launch test pinning the literal launch values, bound in `tests/test_pipeline_position.py` so that `gz validate --brief-reconcile` reads no unrelated import as allowlist drift. Proof `proof-42abf58010164b05b7c9dbc31dd0c0e4`.
- **2026-10-11, Task 1 review (REQ-0.35.0-15-04, REQ-0.35.0-15-07).** Spec `arb-step-specreview-8fcedfb07f7f47dbbd1c57e4dd79e426` and quality `arb-step-qualityreview-59190a1829eb48e2bd0ea32ef4fb3a9c` both accepted proofs `proof-42abf58010164b05b7c9dbc31dd0c0e4` and `proof-b888112820d4492893f6615ac8b15476`. Their unmapped observations are carried into the next dispatch as corrections: the replay's defaults for a malformed row and its cyclomatic complexity (QR1-AUX-01), the dispatch-cache read/write asymmetry (QR1-AUX-02, `aux-dispatch-cache-legacy-fallback-asymmetry`), and the REQ-04 fixture and assertions (`aux-req04-fixture-brief-has-no-reqs`, `aux-test-placement-differs-from-task-text`). An earlier REQ-07 proof, `proof-556f4b0dd39e40b99ee50cd701c04ff2`, is invalid and retained: one orchestrator control raised `KeyError` instead of failing an assertion.
- **2026-10-11, Open Design Question 6 (ruled).** `src/gzkit/pipeline_position.py` is added to Allowed Paths and the "never during implementation" sentence is reworded, on the operator's ruling.
- **2026-10-11, Open Design Questions 5 (superseded and re-ruled), 7 and 8 (ruled).** Requirement 2 is amended in place: precomplete is stage-relative, only Stage 4 review imports record, and `gz obpi sync` leaves the boundary set because the receipt ends the run. The first Question 5 ruling rested on the agent's unread premise and is kept as history.
- **2026-10-11, Task 2 review (REQ-0.35.0-15-01, REQ-0.35.0-15-02).** Spec `arb-step-specreview-2c81301fde654042a22c4de6bb37f54a` accepted proofs `proof-e5b8e29492fc40d5ac95d9f858674838` and `proof-f9413fe9d8414ca59ce78e2870777223`. An earlier spec run, `arb-step-specreview-8da5d9d6c04f4710bba7d50b9f3aa387`, reached the same verdict but could not be imported: it reused a finding identifier an earlier review of other obligations had taken. Quality `arb-step-qualityreview-55341fa39e0645d1a6b3be30cca6d1f4` **refuted**: it accepted the REQ-01 proof and not the REQ-02 proof, on mapped finding `QR2-REQ02-noncanonical-id-records-nothing` (a boundary crossed with a short OBPI id is silently unrecorded). That finding is open until repaired, re-proved and independently closed.
- **2026-10-11, third Task 2 review round and the block.** Spec `arb-step-specreview-8c11989e03054bc2ba099b8318b90814` accepted proofs `proof-233bf07e8786418fa7b71f965550dd7c` and `proof-6f56d74b58d14c72aef330bb13c9799b` and closed `QR2-REQ02-noncanonical-id-records-nothing`, `fc1-REQ02-task-verbs-resolve-the-obpi-apart-from-the-launcher` and `fc1-REQ02-task-start-resolves-its-obpi-id-unlike-the-launcher`. Quality `arb-step-qualityreview-77c07f52211d411382fa73ef9e941844` closed the same three and accepted both proofs, then **refuted** on `fc2-REQ02-a-retired-siblings-unreceipted-launch-is-still-a-run-in-flight`. Both fix cycles being used, the run was blocked (`gz obpi block`) and unblocked on the operator's ruling (Question 12).
- **2026-10-11, Task 2 fix cycle 3 (authorized by Question 12).** A run ends at its receipt or when its OBPI is parked or withdrawn. The finding's second half: the `gz task` verbs name the run by the TASK's own short form, because a TASK started under a retired sibling's slug would otherwise name a run that no longer exists. `fc2-AUX-short-form-is-two-digits-in-the-recorder-and-any-digits-in-the-id-grammar`: the recorder's short form is the whole `OBPI-<semver>-<item>`, whatever the item's width.
- **2026-10-12, Task 2 fix-cycle-3 reviews; Task 2 clears its scoped Stage 2 gate.** Re-proved on the committed tree: REQ-0.35.0-15-01 `proof-c181ea9a8dc44aa69edeb2777a1f78b1` (4 substitutions) and REQ-0.35.0-15-02 `proof-0feee3b6bd7d4db797356a32c1330364` (34 covering tests, 11 substitutions; three new ones mutate the fix-cycle-3 rules: a parked OBPI left in flight, a withdrawn one left in flight, the short form cut at two digits). The new proof superseded the earlier closures, so four findings stood open. Spec `arb-step-specreview-c873521ea55846bc9aada76366772c00` and quality `arb-step-qualityreview-ba329112669840b9bbaa4bb790170006` both accepted both proofs and closed all four: `QR2-REQ02-noncanonical-id-records-nothing`, `fc1-REQ02-task-verbs-resolve-the-obpi-apart-from-the-launcher`, `fc1-REQ02-task-start-resolves-its-obpi-id-unlike-the-launcher` and `fc2-REQ02-a-retired-siblings-unreceipted-launch-is-still-a-run-in-flight`. Plan item 22 lives outside the proof's one source file; its control is a supplementary sweep on `src/gzkit/commands/task.py`, killed on an assertion. The rule that a launch after a retirement starts a new run has covering tests and no substitution of its own; both reviewers accepted it by reading. Unmapped observations: `fc3-AUX-a-receipt-that-is-not-a-completion-ends-the-run` with `fc3-aux-any-obpi-receipt-event-ends-a-run-whatever-its-receipt-kind` (Question 8 rules the completion receipt; carried into the Task 3 dispatch as a correction), `fc3-AUX-unpark-does-not-resume-the-run-the-park-ended` (the comment on the run-ending events claims a parity that holds for park and withdraw only; corrected in Task 3 with the unpark rule that task already owes a test), `fc3-aux-precomplete-dispatch-check-reads-the-typed-id-once-the-run-is-retired` (joins the precomplete correction queued for Task 3), and two recorded under Tracked Defects.
- **2026-10-11, Task 2 fix-cycle reviews.** Both reviewers accepted the REQ-0.35.0-15-01 proof `proof-b6b2cb57b71548d1ae4ac1f124eeaae4`. Both **refuted** REQ-0.35.0-15-02 (proof `proof-c160c2070ed648389670078fbf5df304`): spec `arb-step-specreview-611f71213a0c4d6eb62f97b6f86d5a6b` on `fc1-REQ02-task-start-resolves-its-obpi-id-unlike-the-launcher`, quality `arb-step-qualityreview-49de4512a4a34337b0d11aa152d08a6d` on `fc1-REQ02-task-verbs-resolve-the-obpi-apart-from-the-launcher`. Same root as `QR2-REQ02-noncanonical-id-records-nothing`: fix cycle 1 repaired id resolution in each caller, and `gz task start`, on a TASK's first start, still reached the recorder with the short id when the ledger graph held a second key under that prefix (the live ledger has one for this very OBPI). Three findings are open. Two earlier runs of the same reviews (`arb-step-qualityreview-472831148c8c4fa6bdabe3af15cb9cc1`, accepted with a closure; `arb-step-specreview-4a4f8f277b5f4c9da09fb68e0d59e426`, refuted) could not be imported, because each restated an earlier unmapped finding under its old identifier; they are not on the acceptance record.
- **2026-10-11, Task 2 fix cycle 2 (the last the pipeline allows this task).** The id rule moves into the recorder: a run is matched by its launch id or that id's short form among launches in flight, and recorded under the launch id; the caller-side resolution and its import of the command layer are removed. `gz obpi precomplete`'s Stage 2 dispatch check names the marker the same way (`fc1-AUX-precomplete-checks-still-run-under-the-typed-id`, a pre-existing defect that made the check pass for a short id). An in-place record carries the run's blockers forward (`fc1-aux-in-place-record-after-failed-verification-drops-blockers`).
- **2026-10-11, Task 2 fix cycle 1.** QR2-REQ02-noncanonical-id-records-nothing: every producer now resolves its OBPI id the way the launcher does, with a test crossing six id-taking producers by short id. Question 9: one table, `RULED_BOUNDARIES` in `src/gzkit/pipeline_position.py`, says which boundaries move the stage; a fence test shows no check or bookkeeping command changes the fence's verdict at any stage. QR2-AUX-unbounded-blockers-on-ledger: blockers on the ledger are one-line summaries (Question 11). QR2-AUX-position-record-failure-surfaces-as-host-failure and `t2-aux-position-append-failure-aborts-the-producer`: an I/O failure while recording warns and returns, and the host's outcome stands. `t2-aux-req01-verify-reading-is-the-reentry-launch`: REQ-0.35.0-15-01 is also proven on a run that stays `entry: full` to `ceremony` and `sync`. QR2-AUX-bdd-scenarios-drive-recorder-not-producers and `aux-bdd-scenarios-cross-through-the-recorder`: the REQ-01 and REQ-02 scenarios drive the real commands. QR2-AUX-size-and-residue: `refresh_pipeline_markers` had no consumer left and is removed; the sibling OBPI-0.35.0-16 brief still names it in its Allowed Paths note and Discovery Checklist and reconciles when that brief starts.
- **2026-10-11, Open Design Question 11 (ruled).** The blocker-summary cut is an implementation detail, renamed out of the policy shape.
- **2026-10-11, Open Design Questions 9 and 10 (ruled).** Only work-starting commands move the stage; checks and bookkeeping record in place. The ceremony runner's entry is named in Requirement 2. Question 9 supersedes the Question 5 re-ruling.
- **2026-10-11, extraction and Task 1 review corrections.** The position model and the pure replay moved to `src/gzkit/pipeline_position.py`; `src/gzkit/pipeline_markers.py` does not import it and went from 976 to 914 lines. QR1-AUX-01: the replay no longer reads a row lacking a required field as a crossing, and its cyclomatic complexity went from 16 to 9. QR1-AUX-02 and `aux-dispatch-cache-legacy-fallback-asymmetry`: the dispatch cache is read through the loader it is written through; one case was destructive (an empty-object per-OBPI marker let a single-driver declaration overwrite the legacy marker). `aux-req04-fixture-brief-has-no-reqs` and `aux-test-placement-differs-from-task-text`: the REQ-0.35.0-15-04 test asserts `blockers` and `required_human_action` per entry, and a second bound test launches a brief whose TASKs auto-start. Found in flight: `load_pipeline_json` let a non-UTF-8 marker raise, and now reads it, and JSON that is not an object, as unreadable. These edits supersede the Task 1 proofs and reviews; REQ-0.35.0-15-04 and REQ-0.35.0-15-07 are re-proved and re-reviewed on the finished tree.

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

No GitHub issue has been filed from this run; these are recorded through `gz insights remember` (`.gzkit/insights/agent-insights.jsonl`, 2026-10-11) and await the operator's routing. None discharges an obligation of this brief.

- **Sibling brief names a removed function.** `OBPI-0.35.0-16-next-command-for-position.md` names `refresh_pipeline_markers` in its Allowed Paths note and its Discovery Checklist. This brief removed it once nothing consumed it. That brief is not this run's to edit and reconciles when the operator initiates it.
- **Acceptance import refuses a restated finding.** `acceptance._record_findings` voids a whole review when an earlier finding identifier returns with any field changed, and the review frame does not tell reviewers that a prior identifier may appear only in a closure. Three reviews in this run could not be imported for it and were re-run whole.
- **`gz plan audit` passes a plan whose tasks complete no REQ.** Such a task cannot be reviewed, because a review context requires an executed proof for every scoped obligation.
- **`data/ledger_vocabulary_grandfather.json` carries two event types that now fire** (`ledger_event_corrected`, `unowned_ratchet_updated`). Pre-existing; a path this brief denies.
- **`ADR-0.33.0` calibration frontier, two measured instances.** Source modules are not ontology nodes, and a transit's own RED receipts read as un-accounted seams.
- **No ledger event ends an abandoned run.** A launch that is neither completed, parked nor withdrawn reads as in flight for good. Lock continuity is Decision item 15 (OBPI-0.35.0-19). Since fix cycle 3 the `gz task` verbs name the run by the TASK's short form only, so beside such a launch under the same semver and item every `gz task` verb records no position and warns (`fc3-AUX-task-verbs-name-the-run-by-short-form-only`, `fc3-aux-task-verbs-cannot-name-one-of-two-runs-in-flight`); no test crosses a task verb in that state.
- **A run's ending follows no rename.** The recorder ends a run only when the retirement row carries the id spelling the launch row carries. An OBPI renamed between creation and launch and then parked by pool demotion, or a slug corrected after a launch, leaves a launch in flight (`fc3-AUX-run-ending-matches-the-raw-row-id-and-follows-no-rename`). It needs an `artifact_renamed` row for an OBPI, which no pipeline command writes.
- **TASK identity under a reused semver.** A TASK id carries only semver and item, and the launch-time auto-start skips a TASK id already started under any OBPI slug, so a TASK's own ledger rows can name a retired sibling (`fc2-aux-task-verbs-hand-over-the-slug-the-tasks-own-ledger-row-names`). Predates this brief.
- **`src/gzkit/pipeline_markers.py` is over the module-size guidance** (917 lines), with three pre-existing functions at or above the threshold table's cyclomatic block entry.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
