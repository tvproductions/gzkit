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
- `src/gzkit/obpi_lifecycle.py` — READ-ONLY import of `fold_renames` and `rename_events`, the ledger's one rule for where an artifact is now; never modified by this OBPI (Open Design Question 22, ruled 2026-10-12: "A")
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
- `docs/user/manpages/obpi-acceptance.md` — the exit code of a review import whose id the resolver cannot name (Open Design Question 20, ruled 2026-10-12)
- `docs/user/runbook.md` — the pipeline passage that tells the operator how to inspect the marker
- `src/gzkit/cli/parser_governance.py` — the `--repair` help text of `gz state` only (Open Design Question 14, ruled 2026-10-12); no flag, verb or exit code changes
- `docs/governance/state-doctrine.md` — the repair-sequence line that describes `gz state --repair` (Open Design Question 14, ruled 2026-10-12)
- `.gzkit/skills/gz-state/SKILL.md` — what `--repair` writes and reports (Open Design Question 14, ruled 2026-10-12)
- `src/gzkit/skills/gz-state/SKILL.md` — the wheel copy of the skill above, written by `uv run gz agent sync control-surfaces`
- `docs/user/skills/gz-state.md` — the docs copy of the skill above
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

**13. Whether an ADR audit ceremony is a pipeline run (raised in Task 3, 2026-10-12).** `gz adr audit-begin` writes a `pipeline_launched` row under the ADR's id with the entry `audit`. Nothing ends such a row: no receipt, park or withdrawal is written under an ADR id for it. The Task 3 implementer measured 29 of them on the live ledger, read-only, each of which the rule for a run in flight counted as a run, and which the rebuild would therefore have offered a marker. The implementer excluded them in the one rule the recorder and the rebuild share (`_starts_run` in `src/gzkit/pipeline_position.py`), beyond what the plan fixed.

- A. An `audit` launch is not a pipeline run: it starts no run for the recorder and is never rebuilt. A launch row that names no entry is read as `full`, as the replay already reads it.
- B. Every `pipeline_launched` row starts a run, as built before Task 3; the rebuild then needs its own exclusion, a second notion of in flight.
- **Recommendation: A.**
- **RULED 2026-10-12: A.** Told of the exclusion and asked "Do you ratify it, or should it come out?", the operator answered, verbatim: "ratify the audit exclusion". The audit marker and `src/gzkit/commands/adr_audit.py` are untouched (Denied Paths).

**14. Three surfaces that still describe `gz state --repair` as frontmatter-only (raised in Task 3, 2026-10-12).** Requirement 14 says the coupled docs change in the same change and that what they misstate is corrected. Requirement 18 makes `--repair` rebuild a missing marker. The implementer reported three surfaces outside its allowed files that still say `--repair` reconciles frontmatter only: the `--repair` help text in `src/gzkit/cli/parser_governance.py`, the repair-sequence line in `docs/governance/state-doctrine.md`, and the `gz-state` skill. None was in Allowed Paths or named in Denied Paths. (The orchestrator first told the operator the state doctrine document matched a Denied Path; that was a misreading of the entry for the sealed `ADR-0.0.9` directory, which stays denied and is not this document.)

- Assessment at the point of growth. The help text is one string on an existing flag; no flag, verb, exit code or output schema changes with it, and `uv run gz cli audit` reads it. The doctrine line is one comment on a command in a repair sequence. The skill is canonical under `.gzkit/skills/` and has four generated mirrors that `uv run gz agent sync control-surfaces` writes; its edit bumps `skill-version` and `last_reviewed` (`.gzkit/rules/skill-surface-sync.md`). No registered security surface is among them.
- A. Amend Allowed Paths to add the three surfaces and the skill's mirrors; Task 5 corrects them with the other docs.
- B. Leave them and track the drift for later routing.
- **Recommendation: A.**
- **RULED 2026-10-12: A.** Asked "Do you want the brief amended to cover them?", the operator answered, verbatim: "amend the brief for the three surfaces". Allowed Paths carries the paths. The skill's two vendor mirrors are not listed: `gz plan audit` refuses a generated vendor mirror as an allowed path, because the canonical file is the one edited and the sync writes the mirrors. No requirement and no acceptance criterion changes: Requirement 14 already binds the correction.

**15. Whether the rebuild declines a run idle past the stale bound (raised by the Task 3 quality review, 2026-10-12).** `gz state --repair` writes no marker for a run whose last recorded crossing is older than `STALE_MARKER_HOURS`: the marker would be stale the moment it landed, and the concurrency block ignores a marker's age, so a resurrected marker for an abandoned launch would block every other OBPI's launch. The plan fixed the decline and `docs/user/manpages/state.md` states it, but REQ-0.35.0-15-03 and Requirements 4 and 18 carry no age limit and no ruling recorded it (`t3-AUX-stale-bound-narrows-the-rebuild-and-the-brief-does-not-say-so`).

- A. The decline stands: a run idle past the bound is not rebuilt, the repair reports it as declined, and the run is resumed by launching it again. A live run idle that long cannot have its stage and position restored.
- B. Every run in flight is rebuilt whatever its age; Requirement 6's "a rebuild cannot make an abandoned run look live" is then met only by the rebuilt `updated_at`.
- **Recommendation: A.** Requirement 6 supports it, and both Task 3 reviewers read it so.
- **RULED 2026-10-12: A.** Asked "Do you ratify it?", the operator answered, verbatim: "ratify the stale-bound decline". Requirement 18's rebuild is read with this bound; no requirement text and no acceptance criterion changes.

**16. Whether a supersede ends a run (raised by the Task 3 spec review, 2026-10-12).** Question 12 ruled that retirement ends a run and named park and withdraw. `gz obpi supersede` appends `obpi_superseded`, which ended nothing, so an OBPI launched and then superseded stayed a run in flight: the recorder kept recording for it, and the repair would rebuild its marker, which the concurrency block then reports against every other OBPI's launch (`t3-aux-a-superseded-obpi-launch-stays-a-run-in-flight-and-is-rebuilt`).

- A. A supersede ends a run, as a park and a withdrawal do; a later launch of that id starts a new one.
- B. Only park and withdraw end a run, as built.
- **Recommendation: A.**
- **RULED 2026-10-12: A.** The operator answered, verbatim: "supersede ends a run". The rule sits with the other retiring events in `src/gzkit/pipeline_position.py`, the one rule the recorder and the rebuild share.

**17. Whether the repair restores a marker file from its twin (raised by the Task 3 reviews, 2026-10-12).** Both reviewers showed that the repair as first built could rewrite a marker that was on disk (the per-OBPI file gone, the legacy file present for the same run), restored nothing when only the legacy file was deleted, and could hand the legacy marker to an older unended run so that the live run read as blocked. The orchestrator carried a correction into Task 4 on its own reading of Requirements 7 and 18, without a ruling: when exactly one of a run's two marker files is on disk and reads as that run's marker, the repair restores the missing one as a copy of it; it rebuilds from the ledger only when neither file is on disk; and it declines an older run while a later one is in flight. The copy is one function in `src/gzkit/pipeline_markers.py`, a registered security surface, which creates the target exclusively and overwrites nothing.

- A. Keep the restore as built in Task 4.
- B. Revert it, leave the behaviour as Task 3 built it, and correct `docs/user/manpages/state.md` and the docstrings alone, as the reviewers also offered.
- **Recommendation: A.**
- **RULED 2026-10-12: A.** Told that the rule rested on the orchestrator's reading and asked "Do you want it kept, or reverted to the narrower fix?", the operator answered, verbatim: "keep the marker-twin restore". No requirement text and no acceptance criterion changes; Requirements 7 and 18 are read with it. What the implementer changed beyond the plan in building it stays for the reviews to judge.

**18. How REQ-0.35.0-15-06 is proved (raised in Stage 2, 2026-10-12).** REQ-0.35.0-15-06 is a BEHAVIOR requirement and needs an executed acceptance proof. Task 4 put the code that decides what counts as a recorded position, `_marker_position`, in `scripts/session_orientation.py`. `gz obpi acceptance prove` accepts a source file only under the configured source root: `_production_control_source` in `src/gzkit/acceptance_execution.py` refused the script with "Semantic mutations must target a project production source file". A supplementary sweep on the script killed two controls on an assertion, but a sweep is not an acceptance proof, and Stage 2 and Stage 4 readiness need a current proof for every obligation.

- A. Move the position-reading helper into `src`, into the module that owns the position concept, and have the script call it, as it already calls `gzkit.pipeline_markers` for the marker itself. The proof then mutates that source. The rendering line stays in the script, so the proof covers that a position reaches the output, not the wording of the line.
- B. Leave the code and treat the refusal as a gap in the acceptance tool, outside this brief's Allowed Paths, with its own GHI; this OBPI cannot complete until it lands.
- **Recommendation: A.**
- **RULED 2026-10-12: A.** The operator answered, verbatim: "option A; move the position helper into src". No path is added: `src/gzkit/pipeline_position.py` and `scripts/session_orientation.py` are both in Allowed Paths. That the acceptance tool cannot prove a BEHAVIOR requirement whose code is outside the source root stays recorded under Tracked Defects.

**19. Which OBPI an id names, for a command that takes one (raised by the final Stage 2 round, 2026-10-12).** The final round's spec review of REQ-0.35.0-15-02 (`arb-step-specreview-79c4ad05a17442f18b025bf037913f33`) closed the four earlier findings and refuted the requirement on a fifth, `fin-REQ02-a-slug-prefix-id-is-accepted-by-precomplete-and-records-nothing`: `gz obpi precomplete` and `gz obpi present-evidence` find the brief by a file glob on the id as typed, so they accept a prefix of the launch id longer than its short form, and then hand the recorder that id, which names no run. All five findings have one root: three rules say which OBPI an id names. The launcher resolves through the ledger graph (`resolve_obpi`), following renames and refusing an ambiguous id; `gz obpi precomplete` and `gz obpi present-evidence` resolve by a glob over brief file names and take the first sorted match; and the recorder matches the launch id or its short form. Two unmapped observations of the same round come from that root and bear on Requirement 11: since Task 3 item 9 the precomplete checks run under the id in the resolved brief's frontmatter, which is another OBPI's when a second brief's file name extends the typed id (`fin-AUX-precomplete-full-id-beside-a-hyphen-extended-sibling-brief-reads-the-siblings-controls`), and is the short form the ledger renamed for ten `ADR-0.1.0` briefs (`fin-aux-precomplete-checks-read-under-the-briefs-frontmatter-id-which-can-differ-from-the-ledger-id`), so a standing operator block or an unrecorded Stage 2 dispatch no longer fails the command for those inputs. The run was blocked with `gz obpi block`, as Question 12 rules.

- A. One resolver at command entry. Each command that takes an OBPI id and marks a boundary resolves the OBPI once, at entry, through the launcher's resolver, and uses the id that resolver returns for its checks, its report and its position record. An id that resolver cannot resolve to exactly one OBPI is refused. A fourth fix cycle on REQ-0.35.0-15-02, and every proof and review is redone after it.
- B. Bound the claim: REQ-0.35.0-15-02 covers the launch id and its short form, and a command that accepts any other spelling is a separate defect. The two Requirement 11 cases remain.
- C. Hold the block.
- **Recommendation: A.**
- **RULED 2026-10-12: A.** The operator answered, verbatim: "option A; one resolver at command entry". The block was cleared with `gz obpi unblock` on that ruling. The recorder's own rule (the launch id or its short form) stays for the `gz task` verbs, which hold only a TASK's short form. No path is added: the resolver is read from `src/gzkit/commands/common.py` and not changed.

**20. Whether a review import refuses an id the resolver cannot name (raised by the orchestrator's read of fix cycle 4, 2026-10-12).** Fix cycle 4 (commit `da2f3fc48`) brought `gz obpi precomplete` and `gz obpi present-evidence` under the launcher's resolver at entry. For the review import of `gz obpi acceptance` it changed the position record only: the recorder is handed the resolver's id, and the id as typed when the resolver names no single OBPI, and nothing is refused. The acceptance records are keyed by the id as typed and their brief is found by the file glob, so a prefix of the launch id that stops inside a word, used for the whole acceptance sequence, still imports a review and records no boundary, with no warning. That is the shape of `fin-REQ02-a-slug-prefix-id-is-accepted-by-precomplete-and-records-nothing` on the one producer its reviewer said it had not traced. Established by reading `src/gzkit/commands/obpi_acceptance.py` and `src/gzkit/acceptance_store.py`; a probe through the test fixture was inconclusive because the fixture replaces the store. The ruling on Question 19 reads "Each command that takes an OBPI id and marks a boundary resolves the OBPI once, at entry".

- A. The `review` and `human-review` actions of `gz obpi acceptance` resolve the id at entry through the launcher's resolver and exit 1 with the resolver's message for an id it cannot give to exactly one OBPI; nothing is imported and nothing is recorded. The position is recorded under the resolver's id. The acceptance store's keying is unchanged, and `init`, `prove` and `status` mark no boundary and are unchanged. This changes that command's exit behaviour for those ids, so `docs/user/manpages/obpi-acceptance.md` joins Allowed Paths.
- B. Leave fix cycle 4 as committed, record the gap under Tracked Defects, and go to the proofs and reviews.
- **Recommendation: A.**
- **RULED 2026-10-12: A.** The operator answered, verbatim: "1. A". `docs/user/manpages/obpi-acceptance.md` is added to Allowed Paths. Carried as plan item 7 of "Fix cycle after the final round". Whether the acceptance store itself should be keyed by the resolver's id is not ruled and not changed: `src/gzkit/acceptance_store.py` is outside Allowed Paths.

**21. An OBPI renamed while its run is in flight (raised by the round after fix cycle 4, 2026-10-12).** Both group A reviews closed the five earlier REQ-0.35.0-15-02 findings, accepted its proof, and refuted it on one new counterexample each with the same input (`fin-fc4-REQ02-an-obpi-renamed-after-its-launch-crosses-every-id-taking-boundary-unrecorded`, `fin-fc4A-REQ02-an-obpi-renamed-after-its-launch-records-no-boundary-under-any-spelling`): a run is launched under id A and the ledger then renames the OBPI to B (`artifact_renamed`). The entry resolver reads the ledger graph, whose keys follow renames, and returns B for A, for B and for the short form. The recorder reads raw rows and names a run by the id its launch row carries, or that id's short form, so B names no run: the boundary is crossed with no record and no warning. For the short form this is new in fix cycle 4, which stopped handing the recorder the id as typed. Observed by the orchestrator at the component level, not through a whole command: with a launch under A followed by a rename to B, `Ledger.get_artifact_graph` holds B alone, and `in_flight_launch_id` returns no run for B and the launch id for the short form as typed. Measured on the live ledger the same day: 31 `artifact_renamed` rows name an OBPI, and none follows a launch of that OBPI, so the input has not occurred here. Four commands write the event: `src/gzkit/governance/obpi_slug_rename.py`, `src/gzkit/commands/register.py`, `src/gzkit/commands/adr_promote.py` and `src/gzkit/commands/adr_demote.py`, all outside Allowed Paths; the slug rename refuses a disposed id and does not look for a run in flight. The root is the one Question 19 names, met from the other side: the resolver's identity follows the ledger's renames and the recorder's does not. Tracked Defects already carries its sibling ("A run's ending follows no rename"), and one unmapped observation of the round is the same input on a control (`fin-fc4-aux-stage2-dispatch-check-reads-no-marker-once-the-ledger-renames-a-launched-obpi`: the marker file keeps the launch id, so precomplete's Stage 2 dispatch check finds no marker under the new id). The run was blocked with `gz obpi block`, as the ruling on Question 12 and the fix-cycle handoff require.

- A. The recorder follows the ledger's renames. In `src/gzkit/pipeline_position.py` a launch names its run by the id its row carries taken through the `artifact_renamed` rows the recorder already reads, so the id the resolver returns names the run, and a retirement or receipt written under either id ends it. Records stay filed under the launch row's own id, so the replay, the rebuild and the two marker files keep one key. `gz obpi precomplete` reads the marker for its Stage 2 dispatch check under the launch id of the run the resolver's id names. A fifth fix cycle on REQ-0.35.0-15-02; every proof and review is redone after it.
- B. A rename is refused while a run is in flight. The four writers of `artifact_renamed` refuse an OBPI whose run is in flight, so the input cannot arise. Four modules join Allowed Paths, and the semantics of pool promotion and demotion change.
- C. Bound the claim. REQ-0.35.0-15-02 covers a run under the id it was launched with; a rename during a run is a separate defect, tracked. The short-form regression of fix cycle 4 remains unless the entry commands hand the recorder the id as typed again, which reopens the finding fix cycle 4 closed.
- D. Hold the block.
- **Recommendation: A.** It removes the second identity rule instead of the one input, it closes the tracked sibling defect in the same change, and it stays inside Allowed Paths.
- **RULED 2026-10-12: A.** The operator answered, verbatim: "A; fifth fix cycle authorized, REQ-08 rides along". The block was cleared with `gz obpi unblock` on that ruling. Carried as plan section "Fix cycle 5", items 8 and 9; the REQ-0.35.0-15-08 correction is in the same dispatch, as Task 5's second fix cycle. No path is added.

**22. One rule for where an artifact is now (raised by the round after fix cycle 5, 2026-10-12).** Both group A reviews closed all seven earlier REQ-0.35.0-15-02 findings, accepted its proof, and refuted it on one new input each, the same in both (`fin-fc5A-REQ02-a-rename-back-to-an-earlier-id-leaves-the-resolvers-id-naming-no-run`, `fin-fc5A-REQ02-a-rename-reverted-after-the-launch-leaves-the-run-named-by-no-id-the-resolver-returns`): an OBPI is renamed A to B, launched under B, and renamed back to A while the run is in flight. The ledger answers "where is this artifact now" with one function, `fold_renames` in `src/gzkit/obpi_lifecycle.py`, which folds renames in ledger order and gives A for both ids; the resolver reads it through `Ledger.canonicalize_id`. Fix cycle 5 gave the recorder (`_renames`, `_current_name` in `src/gzkit/pipeline_position.py`) and the operator-block check (`_ledger_renames`, `_current_name`, `_under_current_name` in `src/gzkit/commands/obpi_precomplete.py`) their own reading: a flat last-write-wins map walked until it would revisit an id. That reading agrees with the fold on one rename and on a chain and differs on a round trip, so the launch under B takes the current name A while the id the resolver returns, A, takes B, and no run is named. Group B's quality review refuted REQ-0.35.0-15-05 on the same input (`fin-fc5-qB-REQ05-a-rename-round-trip-leaves-a-completed-obpis-launch-in-flight-and-the-repair-acts-on-it`): a completed OBPI's launch stays in flight and the repair acts on it. The cause is the plan the orchestrator wrote for fix cycle 5: item 8 had the recorder read the rename rows itself and forbade it any import, where the ledger's fold was importable. `src/gzkit/obpi_lifecycle.py` imports only the standard library, and `src/gzkit/commands/obpi_precomplete.py` already imports `operator_block_state` from it. The implementer disclosed the cycle behaviour in its report ("only one of the two ids then names the run") and the orchestrator carried it to the reviewers as a disclosure and did not treat it as a defect. Not executed: both findings are established by reading. The run was blocked with `gz obpi block`.

- A. One rule. The recorder and the operator-block check take an id's current name from `fold_renames`, read from `src/gzkit/obpi_lifecycle.py` and not changed; both private readings are deleted. The operator-block check reads its rows the way the recorder does, so a rename a correction has voided renames nothing there either. Tests take a run launched under an intermediate name through a rename back, and take a renamed run through `gz state --repair`, which no test does today. The two document findings ride along. A sixth fix cycle on REQ-0.35.0-15-02; every proof and review is redone after it.
- B. Bound the claim. REQ-0.35.0-15-02 and REQ-0.35.0-15-05 cover a run whose OBPI is not renamed while it is in flight; the rename-following of fix cycle 5 is taken out again or kept as best effort, and the four writers of `artifact_renamed` refuse an OBPI whose run is in flight (four modules join Allowed Paths).
- C. Hold the block and end the session here. The lock lapses at about 18:06Z on 2026-10-12; Stages 3 to 5 are not started.
- **Recommendation: A, with a stop rule.** A removes the copies that caused this finding and the one before it, and it is a deletion more than an addition. If the round after it refutes REQ-0.35.0-15-02 again, the recommendation becomes B, because a seventh patch would be evidence that the claim, not the code, is what needs ruling.
- **RULED 2026-10-12: A.** The operator answered, verbatim: "A". The block was cleared with `gz obpi unblock` on that ruling. The lock had been reaped at 22:47Z before the ruling, so no lock is held when it is recorded. The recommendation's stop rule stays the orchestrator's commitment: if the round after the sixth fix cycle refutes REQ-0.35.0-15-02 again, the run is blocked and option B is brought to the operator.

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
- **2026-10-12, fix cycle 6, the manpages' statement of the rename rule (REQ-0.35.0-15-08); before the round.** Found by the orchestrator reading the documents the cycle had not edited, after the code was committed as `d68b7073c` and before any review: the rename paragraph of `docs/user/manpages/obpi-pipeline.md` and its copy in `docs/user/manpages/obpi-acceptance.md` spoke only of a run launched before a rename and of an ending "under the new id". Both now state the rule the code has: a run is named by every id whose current name is the current name of its launch id, a rename later reversed ends no run, and an ending under any id with that current name ends it. Raised by the implementer while writing it, and corrected in the same pass: three sentences of the id-rule paragraph of `docs/user/manpages/obpi-pipeline.md` said a boundary is recorded "under that id", where the record is filed under the launch id of the run that id names (`_record_crossing` in `src/gzkit/pipeline_position.py`); and its sentence on `gz obpi verify-packet` said a name the rule gives no id is recorded only when it is itself a launch id or its short form, which was narrower than the recorder's rule. Documents only; no file the acceptance digest reads changed. Strict docs build `arb-step-mkdocs-066cfe86c1cb4342b5ec0f62fc75b882`.
- **2026-10-12, fix cycle 6 implemented (plan items 10 and 11); not yet proved or reviewed.** One rule for where an artifact is now (`fin-fc5A-REQ02-a-rename-back-to-an-earlier-id-leaves-the-resolvers-id-naming-no-run`, `fin-fc5A-REQ02-a-rename-reverted-after-the-launch-leaves-the-run-named-by-no-id-the-resolver-returns`, `fin-fc5-qB-REQ05-a-rename-round-trip-leaves-a-completed-obpis-launch-in-flight-and-the-repair-acts-on-it`): in `src/gzkit/pipeline_position.py` the in-flight rule and the matching rule take an id's current name from `fold_renames` (`src/gzkit/obpi_lifecycle.py`, imported and not changed); `_renames` only extracts the pairs and `_current_name` is deleted. In `src/gzkit/commands/obpi_precomplete.py` the operator-block check takes current names from the same fold and `_ledger_renames`, `_current_name` and `_under_current_name` are deleted. No private walk of the rename rows remains in either module. The resolver, the recorder and the operator-block check now fold the same stream: the resolver and the recorder read `Ledger.read_all()`, and the check reads `read_corrected_rows` at its default `live` stream, where before it parsed the file itself and netted nothing. Two consequences of that netting on a control Requirement 11 names, both the reading the launcher's own operator-block gate already had: a block row a correction voided no longer refuses READY, and an unblock row a correction voided no longer clears a standing block. Both directions are pinned by a test and were shown to fail against an un-netted read. Found by the orchestrator tracing the implementer's first report, and repaired in the same cycle before any proof: the check extracted its pairs through `rename_events`, which stringifies, so a rename row whose `new_id` is not a string (the strict reader accepts one) renamed its id to the literal `None` in the check while the resolver and the recorder renamed nothing, and two such rows gave two OBPIs one name; the check now takes pairs by the resolver's own predicate (`Ledger._build_rename_map`), with a test watched red first. That `rename_events` stringifies a non-string `new_id` is a property of `src/gzkit/obpi_lifecycle.py`, which this OBPI reads and does not change; it is recorded as an insight for routing. Documents: the runbook says the marker's `dispatch_state` holds only the dispatches recorded since the marker was last written afresh (`fin-fc5-c-REQ08-runbook-says-the-marker-holds-one-dispatch-entry-for-each-recorded-dispatch`); the migration-path document states the current-name rule for when a run ends (`fin-r6qc-REQ09-migration-path-ends-a-run-only-under-the-same-id-after-the-rename-rule-landed`); the runbook's repair passage and the migration path's rebuild passage name the one other marker writer, `gz adr audit-begin`. No existing test was edited. Ten tests were added: six bound to REQ-0.35.0-15-02 or REQ-0.35.0-15-05 were watched red on an assertion before the code, one case was added to a table after the fold landed, and three controls bind no requirement. Verified on the whole tree before the commit: `arb-ruff-f7f48ef43cd94448a79e766fe91b4051`, `arb-step-typecheck-e0ee32cc8a9d48b297af8ce13faab3a1`, `arb-step-unittest-518dcd994d4545b5a01d95bb56a61120` (11771 tests, 4 skipped, exit 0), `arb-step-mkdocs-8d7c25b6ae9d4c7eb1b4c6e63eb912de`, `arb-step-behave-5c45a4ce83dc45b19939a61ded60f2a5` (40 scenarios). No `gz arb red` receipt was produced for this cycle; the executed acceptance proof is the witness.
- **2026-10-12, Open Design Question 22 (ruled); the block is cleared.** One rule for where an artifact is now: fix cycle 6 for REQ-0.35.0-15-02, authorized by the operator, verbatim: "A". `src/gzkit/obpi_lifecycle.py` joins Allowed Paths as a READ-ONLY import, as the option ruled names it. The lock claimed on 2026-10-11 was reaped at 22:47Z before the ruling; the operator initiated the pipeline again and a new lock was claimed. Carried as plan section "Fix cycle 6", items 10 to 12; item 12 is the orchestrator's stop rule.
- **2026-10-12, the round after fix cycle 5, and the second block.** All nine obligations were re-proved on one tree (HEAD `79e2a175c`), each control dry-run first (41 substitutions, all killed on an assertion): `proof-87d17bc89f234236b1f0d4e1ec9d6398` (REQ-0.35.0-15-01), `proof-fef869dbf8ef4af8bb942e7c300c2be5` (-02, 55 covering tests, 19 substitutions, five of them on the rename rule), `proof-646641d2d5d84bd0a55e63586c9802a3` (-03), `proof-5d01f7acbf674cb09e20a6c8cfacc055` (-04), `proof-2b04644de7bd433fbec5dc1b6dfe92fd` (-05), `proof-105808a0f4ce4e4fa4a6600ef15ad138` (-06), `proof-30dcbb8c4a68417994ee6f6b60972fef` (-07), `proof-90ca318d8365453a9b9fac5ebd771b8e` (-08) and `proof-94aecff7bf264f9ab4ee942f6e33ff2f` (-09). The supplementary sweep over the command modules was re-run whole with two new controls (ten substitutions, all killed on an assertion). Group A: spec `arb-step-specreview-20b2039da3954e4b8e84cd3a53e33d56` and quality `arb-step-qualityreview-229ac285260643a0982a1c1856fb4167` each accepted all four proofs and closed the seven REQ-0.35.0-15-02 findings, the two rename findings of the round before among them, and each **refuted** REQ-0.35.0-15-02 on one new mapped finding: `fin-fc5A-REQ02-a-rename-back-to-an-earlier-id-leaves-the-resolvers-id-naming-no-run` and `fin-fc5A-REQ02-a-rename-reverted-after-the-launch-leaves-the-run-named-by-no-id-the-resolver-returns`. Group B: quality `arb-step-qualityreview-1abae3e5df9b4ad4a5368602298b118b` accepted the REQ-0.35.0-15-03 proof and **refuted** REQ-0.35.0-15-05 on `fin-fc5-qB-REQ05-a-rename-round-trip-leaves-a-completed-obpis-launch-in-flight-and-the-repair-acts-on-it`; spec `arb-step-specreview-9749c202940c4dc3b9fa05dd3e65f1f8` accepted both proofs but **could not be imported**: it mapped its finding of the same input to REQ-0.35.0-15-02, an obligation outside its review scope, so REQ-0.35.0-15-03 and -05 hold no spec review on this tree. Group C: spec `arb-step-specreview-d2528786c41c4a348bb2ea56cfa1ff39` accepted the REQ-0.35.0-15-06 and -09 proofs and **refuted** REQ-0.35.0-15-08 on `fin-fc5-c-REQ08-runbook-says-the-marker-holds-one-dispatch-entry-for-each-recorded-dispatch` (a sentence fix cycle 5 wrote: every launch writes the marker afresh with no dispatch state, so the cache holds the dispatches since the last launch only); quality `arb-step-qualityreview-7991690e2f6f4972a8f1dec1fb66e32a` accepted the REQ-0.35.0-15-06 and -08 proofs, closed all six REQ-0.35.0-15-08 findings, and **refuted** REQ-0.35.0-15-09 on `fin-r6qc-REQ09-migration-path-ends-a-run-only-under-the-same-id-after-the-rename-rule-landed` (the migration-path document still says a run ends under the same id, which fix cycle 5 made false for a renamed OBPI). Five mapped findings are open: two on REQ-0.35.0-15-02 and one each on REQ-0.35.0-15-05, -08 and -09. The run was blocked with `gz obpi block` and the design put to the operator as Question 22. Unmapped observations of the round are in the receipts and not yet routed: three statements of the rename rule beside the ledger's fold, and the operator-block copy reading the ledger un-netted; every rename test launching before the first rename; a bare id the ledger renamed naming its target ahead of the two-runs rule; no test taking a renamed run through the repair; the runbook's State Repair passage and one migration-path line still without the `gz adr audit-begin` exception; the runbook's short-id placeholder beside three things that take the id literally; the runbook transcribing the review fix-cycle bound as a number.
- **2026-10-12, fix cycle 5 implemented (plan items 8 and 9); not yet proved or reviewed.** The recorder follows the ledger's renames (`fin-fc4-REQ02-an-obpi-renamed-after-its-launch-crosses-every-id-taking-boundary-unrecorded`, `fin-fc4A-REQ02-an-obpi-renamed-after-its-launch-records-no-boundary-under-any-spelling`): in `src/gzkit/pipeline_position.py` the in-flight rule and the matching rule compare ids by their current name, read from the `artifact_renamed` rows the recorder already reads, and a record stays filed under the launch row's own id; the module gains no import. `gz obpi precomplete` reads the marker and the dispatch channel for its Stage 2 dispatch check under the launch id of the run the entry id names, through a new read-side adapter `run_launch_id` in `src/gzkit/pipeline_runtime.py` (`fin-fc4-aux-stage2-dispatch-check-reads-no-marker-once-the-ledger-renames-a-launched-obpi`). Found by the orchestrator reading the implementer's first report against its own disclosed gap, and repaired in the same cycle before any proof: the operator-block check ran under the resolver's id alone since fix cycle 4, so a block recorded under the launch id no longer failed precomplete once the OBPI was renamed (Requirement 11); it now reads block and unblock rows under each row id's current name. The other id-taking checks find nothing under a new id and fail, which is stricter and is left. No existing test was edited. Ten tests were added; seven bound to REQ-0.35.0-15-02 were watched failing on their assertions before the code, and three are Requirement 11 or rule controls bound to no requirement, of which two passed on their first run. Disclosed by the implementer: the rename map is read over the whole ledger and not in ledger order, so a rename applies to rows written before it; a cycle of renames ends, and only one of its two ids then names the run; no test covers an unblock recorded under the old id after the rename. REQ-0.35.0-15-08 (`fin-fc-c-REQ08-runbook-says-review-findings-are-recorded-in-the-markers-dispatch-state`, `fin-c2-REQ08-runbook-says-review-findings-status-and-result-are-in-the-marker-dispatch-state`): the runbook's pipeline passage says what a `dispatch_state` entry holds, that no command writes a result, a completion time or a review finding into the marker, and that review findings are read from the acceptance record. Three unmapped observations of the round are corrected in the named documents: the id-rule paragraph gains the prefix shorter than the short form, the verify-packet fall-through and the rename rule; the migration-path document's no-nonce decline gains its neither-file condition; and the three statements that nothing else writes a marker name `gz adr audit-begin`. Whole unit suite under ARB `arb-step-unittest-816fe6102b73463eb9da5efed423f6be` (11761 tests, 4 skipped, all Windows-only), the feature `arb-step-behave-298da7666ed1453ca6b0260d9cb08600`, the strict docs build `arb-step-mkdocs-7f8705eb78b844f6b81be6f6822ee0a0`, lint `arb-ruff-22abfaf502b14a94937b33254cd590a8` and typecheck `arb-step-typecheck-991983d9ea414eb494ae47a252894315`, exit status 0 each.
- **2026-10-12, Open Design Question 21 (ruled); the block is cleared.** The recorder follows the ledger's renames: fix cycle 5 for REQ-0.35.0-15-02, authorized by the operator, with Task 5's second fix cycle for the two REQ-0.35.0-15-08 findings in the same dispatch (plan, "Fix cycle 5").
- **2026-10-12, the round after fix cycle 4, and the block.** All nine obligations were re-proved on one tree (HEAD `f9c9b9c05`), each control dry-run first: `proof-7a885321405b44d083667b7472295102` (REQ-0.35.0-15-01), `proof-d2bf34cf5c1b472d938bbb62921e7e01` (-02, 49 covering tests, 14 substitutions), `proof-ea240c068e974902854261aa5b172278` (-03), `proof-05d589652a9640dc9832be9969e8b3d6` (-04), `proof-5c1c9f557d824683b4b6b5843fc78900` (-05), `proof-e0d6664b932543d6b265fb4162c7e90c` (-06), `proof-25e2a6142f1f47749eaebf3cc43bc33a` (-07), `proof-65bdd07be8284003832ca9f02cfc59e4` (-08) and `proof-7e31c222b1784f439435dc31b4d816aa` (-09). A supplementary sweep over the entry rule, outside the REQ-0.35.0-15-02 proof's one source file, killed eight substitutions on an assertion (the resolver handing back the id as typed; a refused id falling back to the glob; precomplete, present-evidence and both review imports keeping the id as typed; a review import falling back when refused; the twin restore creating before it reads). One round in three groups, all six reviews imported. Group B (REQ-0.35.0-15-03, -05): spec `arb-step-specreview-bee9f30149e54c3cab79415858db59be` and quality `arb-step-qualityreview-32f3e074ed66448fa1375ef13cc793f1` accepted both proofs; no mapped finding. Group A (REQ-0.35.0-15-01, -02, -04, -07): spec `arb-step-specreview-e0bb8bf73b15452c9bf75b8e0e9d25f1` and quality `arb-step-qualityreview-354b5803941d4c5c9f2da48a15bd2b15` each accepted all four proofs and closed the five REQ-0.35.0-15-02 findings (`QR2-REQ02-noncanonical-id-records-nothing`, `fc1-REQ02-task-verbs-resolve-the-obpi-apart-from-the-launcher`, `fc1-REQ02-task-start-resolves-its-obpi-id-unlike-the-launcher`, `fc2-REQ02-a-retired-siblings-unreceipted-launch-is-still-a-run-in-flight`, `fin-REQ02-a-slug-prefix-id-is-accepted-by-precomplete-and-records-nothing`), and each **refuted** REQ-0.35.0-15-02 on one new mapped finding with the same input: `fin-fc4-REQ02-an-obpi-renamed-after-its-launch-crosses-every-id-taking-boundary-unrecorded` and `fin-fc4A-REQ02-an-obpi-renamed-after-its-launch-records-no-boundary-under-any-spelling`. Group C (REQ-0.35.0-15-06, -08, -09): spec `arb-step-specreview-35307cfc0d5c4090b36fad85faa16f94` and quality `arb-step-qualityreview-72b6b26fbea846bda85beeefd07f9c9d` accepted the REQ-0.35.0-15-06 and REQ-0.35.0-15-09 proofs and **refuted** REQ-0.35.0-15-08 on one new mapped finding each, again the same statement: `fin-fc-c-REQ08-runbook-says-review-findings-are-recorded-in-the-markers-dispatch-state` and `fin-c2-REQ08-runbook-says-review-findings-status-and-result-are-in-the-marker-dispatch-state` (the runbook's pipeline passage says dispatch records show a status and a result and that review findings are recorded in the marker's dispatch state; no production code writes them). Both judged the four earlier REQ-0.35.0-15-08 findings repaired and withheld their closures only because a closure must cite an approved proof. Eight mapped findings are open: two on REQ-0.35.0-15-02 and six on REQ-0.35.0-15-08. REQ-0.35.0-15-02 being refuted after its fourth fix cycle, the run was blocked with `gz obpi block` and the design put to the operator as Question 21. Unmapped observations of the round are in the six receipts and are not yet routed: the lock and plan-audit checks of precomplete still match an id as a file-name prefix; a review import names its OBPI by the resolver for the record and by the glob for the store; the entry refusal is rendered three ways and the shared entry rule lives in a command module; the docstring of `record_run_position` still says no command resolves an id; the twin restore copies a second read it does not check and a failed write still leaves a partial target; the id-rule paragraph omits a prefix shorter than the short form and the verify-packet fall-through; the migration-path document's no-nonce decline lacks its neither-file condition; `gz adr audit-begin` writes a marker file the documents do not account for; the pipeline manpage's Failure Modes lists two launch blockers the launcher does not run; the `--clear-stale` help string transcribes the stale bound; the verify-packet id lookup sits outside the recorder's I/O containment.
- **2026-10-12, plan item 7 implemented (Question 20); not yet proved or reviewed.** The `review` and `human-review` actions of `gz obpi acceptance` name the OBPI at entry through `resolve_obpi_at_entry` and exit 1 with the resolver's message for an id it cannot give to one OBPI, before anything is read or imported; the boundary is recorded under the resolver's id with no fallback, and the acceptance records stay keyed by the id as typed. Outcomes that changed for those two actions: a prefix that stops inside a word and a short form two live OBPIs share were imported and are refused; an unknown id exits 1 where the store's own error exited 3; the resolver runs before the argument checks, so a refused id exits 1 even when `--receipt` or `--ruling` is also missing. `gz obpi verify-packet` takes a path and keeps the rule of item 1: a packet whose name names no single OBPI records nothing. Two tests bound to REQ-0.35.0-15-02: the refusal test was watched failing on its assertion in all eight subtests (`0 != 1`); the second is a control that passed before the change and pins the store's keying. No acceptance test outside Allowed Paths needed a change. Whole unit suite under ARB `arb-step-unittest-ba3dbb2513204420a24630f7a397cb8d` (11751 tests, 4 skipped, all Windows-only), the feature `arb-step-behave-e89249dc7722413e95fb898e4e46d457`, the strict docs build `arb-step-mkdocs-d10358c6040f4016916a6e60b33c57f7`, lint `arb-ruff-9fe16f55b55d4286bc54689f1a506ee0` and typecheck `arb-step-typecheck-29e1c47905c6422f9a2de5b534a50cfd`, exit status 0 each.
- **2026-10-12, Open Design Question 20 (ruled).** A review import refuses an id the resolver cannot name: `docs/user/manpages/obpi-acceptance.md` joins Allowed Paths, and the change is plan item 7 of "Fix cycle after the final round". The gap was found by the orchestrator reading fix cycle 4's diff against the ruling on Question 19, before any proof was recorded.
- **2026-10-12, fix cycle after the final round implemented (plan items 1 to 6); not yet proved or reviewed.** Commit `da2f3fc48`. `gz obpi precomplete` and `gz obpi present-evidence` name the OBPI once at entry through `resolve_obpi_file` and use that id for the checks, the report, the packet and the position record (`fin-REQ02-a-slug-prefix-id-is-accepted-by-precomplete-and-records-nothing`, `fin-AUX-precomplete-full-id-beside-a-hyphen-extended-sibling-brief-reads-the-siblings-controls`, `fin-aux-precomplete-checks-read-under-the-briefs-frontmatter-id-which-can-differ-from-the-ledger-id`). Outcomes that changed, each exit 1 with the resolver's message where the glob once accepted the id: a prefix that stops inside a word, a short form two live OBPIs share, and a short id for a brief the ledger does not know; `present-evidence` writes its packet under the resolved id. One existing test bound to REQ-0.35.0-15-02 was amended, `test_a_short_id_records_under_the_live_run_when_a_retired_brief_sorts_first`: it asserted that the checks ran under a retired sibling's id while the record went to the live run, the split the ruling removes. The twin restore reads its source before it creates its target (`fin-specB-twin-restore-creates-its-target-before-reading-its-source`). The four REQ-0.35.0-15-08 document findings and the state manpage's example (`fin-specB-state-manpage-json-example-shows-a-report-the-repair-cannot-produce`, `fin-c-aux-state-manpage-json-example-cannot-be-produced-by-the-code`) are corrected, the example from output captured in a temporary project; the `gz-state` skill is 0.3.1 with its mirrors regenerated. Whole unit suite under ARB `arb-step-unittest-802f73538e694bc4b90ed64850675dfd` (11749 tests, 7 skipped: four Windows-only, three for a missing offline `pre-commit`, recorded through `gz insights remember`), the feature `arb-step-behave-ca716532d97b4e889274f3fb91392f3f` (40 scenarios), the strict docs build `arb-step-mkdocs-b729565c1fd74d70af5dd1ae36a16936`, lint `arb-ruff-3f2727252b004f528e9331bd82fd57ac` and typecheck `arb-step-typecheck-cec84cbd80534182bb47da402e15ca9a`, exit status 0 each. The implementer stopped once at its turn limit without a report and was resumed with the measured state of the tree. It disclosed that the per-test red was witnessed by putting the HEAD version of `src/gzkit/commands/obpi_precomplete.py` back and running both test classes (19 assertion failures), not test by test before the code. Not changed, awaiting the operator: `docs/user/manpages/obpi-present-evidence.md`, outside Allowed Paths, still describes exit 1 and the packet file name as they were.
- **2026-10-12, Open Design Question 19 (ruled); the block is cleared.** One resolver at command entry: fix cycle 4 for REQ-0.35.0-15-02, authorized by the operator, with Task 5's first fix cycle for the four REQ-0.35.0-15-08 findings and three unmapped corrections in the same dispatch (plan, "Fix cycle after the final round").
- **2026-10-12, final Stage 2 round and the block.** All nine obligations were re-proved on one tree (HEAD `124aa85f4`): `proof-8e046c54f0bf4f3bba6c4d4d815b71c7` (REQ-0.35.0-15-01), `proof-3e41d2995ac24a41b3cc27cdd47670b5` (-02, 42 covering tests, 14 substitutions), `proof-ab13c4010cc14807afc28d742f31aadc` (-03), `proof-ca28b5f313b74ddb94199f70ad175629` (-04), `proof-e329a9e4688346ada940efa5ff121b4c` (-05), `proof-b1b15ae5f8c34ba695247a970d8c6831` (-06), `proof-ba935ea082344d8682f355f14b8b46cd` (-07), `proof-910e11f6976d42e6878f73d63439c491` (-08) and `proof-2998816a70a44942a7e862c95a47ff02` (-09). One round reviewed them in three groups, in place of separate Task 4 and Task 5 rounds on the same tree. Group A (REQ-0.35.0-15-01, -02, -04, -07): quality `arb-step-qualityreview-b9a24fbc50534f49acec3e9a5002fc13` accepted all four proofs and closed the four REQ-0.35.0-15-02 findings the new proof had reopened; spec `arb-step-specreview-79c4ad05a17442f18b025bf037913f33` accepted all four proofs and closed the same four, then **refuted** REQ-0.35.0-15-02 on a new mapped finding, `fin-REQ02-a-slug-prefix-id-is-accepted-by-precomplete-and-records-nothing`: `gz obpi precomplete` and `gz obpi present-evidence` accept a prefix of the launch id longer than its short form, resolve the brief by a glob, and hand the recorder the id as typed, which names no run. Group B (REQ-0.35.0-15-03, -05): spec `arb-step-specreview-a95ee40c4be84cd399a14144b84187f8` and quality `arb-step-qualityreview-9fe8608a6e79432db318bf9cf0ebaa37` accepted both proofs with no mapped finding. Group C (REQ-0.35.0-15-06, -08, -09): spec `arb-step-specreview-fe9109ec0adf41f9a6c5a61d7ba2bac7` and quality `arb-step-qualityreview-acd029000dd749bf8dcff1dcc8acd365` accepted the REQ-0.35.0-15-06 and REQ-0.35.0-15-09 proofs and **refuted** REQ-0.35.0-15-08 on four mapped findings about `docs/user/manpages/obpi-pipeline.md` and `docs/user/runbook.md`: `fin-c-REQ08-manpage-says-the-launcher-leaves-a-missing-marker-missing`, `fin-c-REQ08-stale-decline-stated-without-its-neither-file-condition`, `fin-c-REQ08-runbook-says-timing-metrics-are-in-the-marker` and `fin-c-REQ08-runbook-sends-the-operator-to-the-marker-for-timing-metrics-nothing-writes`. REQ-0.35.0-15-02 being refuted again, the run was blocked with `gz obpi block` and the design put to the operator, as Question 12 rules. Two unmapped observations bear on Requirement 11 and come from Task 3 item 9, which made `gz obpi precomplete` run its checks under the id the resolved brief carries: `fin-AUX-precomplete-full-id-beside-a-hyphen-extended-sibling-brief-reads-the-siblings-controls`, and `fin-aux-precomplete-checks-read-under-the-briefs-frontmatter-id-which-can-differ-from-the-ledger-id` (ten `ADR-0.1.0` briefs carry a short frontmatter id the ledger renamed, so the full ledger id now reads the operator block and the dispatch check under the short one). The other unmapped observations of the round are in the six receipts.
- **2026-10-12, Task 4 item 7: the position-reading helper is in `src` (Question 18).** `marker_position` in `src/gzkit/pipeline_position.py` decides what counts as a recorded position, and the orientation script calls it; `src/gzkit/pipeline_markers.py` is untouched. One direct test over fourteen cases, watched failing on its assertion against a stub; no existing test was edited. Two differences from a pure move, for the reviews: it accepts any mapping where the script checked for a dict, and the script imports it inside the same guard as the marker reader, so a failed import of the position module would report no runs. Full unit suite under ARB `arb-step-unittest-a96fca7c946d4423a113c72c22f11f56`, exit status 0.
- **2026-10-12, Task 5 implemented (REQ-0.35.0-15-08, REQ-0.35.0-15-09 and the three surfaces of Question 14); not yet proved or reviewed.** Full unit suite under ARB `arb-step-unittest-a1fd59d588444c84b76bac107e81ab09` and the strict docs build `arb-step-mkdocs-e32f257bffb142f98fb494683376928b`, exit status 0 each; `uv run gz cli audit` reports every command covered. The pipeline manpage, the runbook, the runtime contract and the migration-path document state the position, the boundary set, the in-flight rule and the repair as built; the migration-path document is rewritten from plan to record. The `--repair` help string, the state doctrine's repair-sequence line and the `gz-state` skill (0.3.0, mirrors regenerated by the sync) say what `--repair` does; `docs/user/skills/gz-state.md` is hand-maintained, was first taken for a generated copy by the orchestrator, and is corrected too. The implementer found and corrected eight statements beyond those the task named, among them that ceremony attestation applied only to heavy lane or foundation kind, and that a rebuild-on-launch and seven event types existed. It measured that a rebuilt `started_at` differs from the launcher's in format and precision, and the docs say so. What it found outside its allowed files is under Tracked Defects.
- **2026-10-12, Open Design Question 18 (ruled).** The position-reading helper moves from the orientation script into `src/gzkit/pipeline_position.py` so that REQ-0.35.0-15-06 can be proved; carried as plan Task 4 item 7. Supplementary sweep over the Task 4 rules before the move (seven controls: six killed on an assertion, one on the script errored through the control's own fault).
- **2026-10-12, Open Design Question 17 (ruled).** The marker-twin restore is kept as Task 4 built it.
- **2026-10-12, Task 4 implemented (REQ-0.35.0-15-06 and the corrections from the Task 3 reviews); not yet proved or reviewed.** Full unit suite under ARB `arb-step-unittest-88af7379e02a4b05a3cfc84b53e0d0e1`, exit status 0. The orientation's pipeline section reports the stage reached and the position inside it. `gz obpi precomplete` records its position under the id as typed and keeps the brief's id for its checks. A supersede ends a run (Question 16). `gz state --repair` restores a missing marker file as a copy of its twin on disk through a new function in `src/gzkit/pipeline_markers.py` that creates the file exclusively and overwrites nothing, rebuilds from the ledger only when neither file is on disk, and declines an older run while a later one is in flight; `--json` reports restores in a third list. This restore rule is the orchestrator's reading of Requirements 7 and 18 and is not ruled; the reviewers also offered correcting the manpage alone. Disclosed by the implementer: six of fourteen new tests were not red-first and were watched failing only with the production hunk withheld or mutated; the tests bound to REQ-0.35.0-15-06 are in `tests/test_pipeline_position.py`, after the orchestrator's dispatch first named a module whose reach is outside Allowed Paths.
- **2026-10-12, Open Design Questions 15 and 16 (ruled).** The rebuild's decline of a run idle past the stale bound is ratified. A supersede ends a run, with park and withdraw; carried into the Task 4 dispatch as plan item 6.
- **2026-10-12, Task 3 review (REQ-0.35.0-15-03, REQ-0.35.0-15-05); Task 3 clears its scoped Stage 2 gate.** Proofs `proof-4f14940aa06741d29736fef4bdba9c6a` (4 substitutions) and `proof-94a090e903814ee7b0b758c19a750f11` (10 covering tests, 3 substitutions), with a supplementary sweep of seven more over the state command, the in-flight rule, the precomplete id and two stale-detection branches, each killed on an assertion. Spec `arb-step-specreview-7db82877df1944eead241e3746cc9f01` and quality `arb-step-qualityreview-05f4e86c32fd4b95928c23455021f12d` both accepted both proofs; no mapped finding. Unmapped observations and where each goes. Carried into the Task 4 dispatch as corrections (plan, Task 4 items 2 to 5): `t3-AUX-precomplete-short-id-follows-the-first-sorted-brief-for-the-position-record`; `t3-AUX-a-skipped-latest-run-lets-an-older-run-take-the-legacy-marker` with `t3-AUX-a-legacy-marker-on-disk-is-overwritten-when-the-per-obpi-file-is-gone`, `t3-aux-repair-rewrites-a-legacy-marker-on-disk-when-the-per-obpi-file-is-gone` and `t3-aux-a-deleted-legacy-marker-is-rebuilt-by-nothing-while-the-per-obpi-file-stands`; `t3-AUX-declines-and-unchanged-controls-without-a-negative-control` (the no-nonce decline has no test); `t3-aux-two-rebuilt-keys-have-no-layer-1-or-layer-2-source` with `t3-AUX-rebuilt-keys-with-no-ledger-source-and-a-launch-time-that-moves` (the manpage overstates "from the ledger alone"). Put to the operator for a ruling: `t3-AUX-stale-bound-narrows-the-rebuild-and-the-brief-does-not-say-so` and `t3-aux-a-superseded-obpi-launch-stays-a-run-in-flight-and-is-rebuilt`. Under Tracked Defects: the two stale rules (`t3-AUX-the-stale-rule-has-two-copies-that-already-differ-on-one-input`, `t3-aux-the-two-stale-rules-already-differ-on-a-zoneless-time`) and `t3-AUX-position-module-size-and-disk-reads`. `t3-aux-req05-control-half-has-a-green-baseline-only-in-its-recorded-proof` is answered at the final round by controls for the age comparison, the orphan purge and the concurrency block.
- **2026-10-12, Task 3 corrections found while preparing its proofs.** A dry run of the REQ-0.35.0-15-05 controls left one survivor: nothing failed when the rebuild read an unreadable last-crossing time as not stale. The implementer added `test_a_run_whose_last_crossing_time_cannot_be_placed_is_declined` (a time that is no time, and a naive one) and watched it fail on its assertion with the branch reversed. The orchestrator's first text for Question 13 named a command that is not registered; the full unit suite failed five CLI-alignment tests on it (`arb-step-unittest-a1a81a7f1cb942bcbf4ec3a092398965`), and the brief, the plan, one code comment and two test docstrings now name `gz adr audit-begin`. Two proofs recorded before that correction, `proof-6ae5e41efd97437aa2f9b87af58da36a` and `proof-59d1d07a134e49c3be67bdb43f17f267`, are superseded and retained. Full unit suite on the corrected tree: `arb-step-unittest-8601ee5cef9745488e109843bee1eeb1`, exit status 0.
- **2026-10-12, Open Design Questions 13 and 14 (ruled).** An ADR audit launch is not a pipeline run, ratified as the Task 3 implementer built it. Allowed Paths gains the `--repair` help text in `src/gzkit/cli/parser_governance.py`, `docs/governance/state-doctrine.md`, and the `gz-state` skill with its wheel and docs copies; Task 5 corrects them.
- **2026-10-12, Task 3 implemented (REQ-0.35.0-15-03, REQ-0.35.0-15-05); not yet proved or reviewed.** Commit `00e2bcfe4`. Full unit suite under ARB `arb-step-unittest-585f10efa3194aa586edd03ca200b109`, exit status 0. The implementer's first report left two failures in the full suite, both sent back to it and fixed: an unescaped console print in `src/gzkit/commands/state.py`, and allowlist drift from binding the REQ-0.35.0-15-05 tests in `tests/test_pipeline_runtime.py`, whose other tests reach modules outside Allowed Paths; they are bound in `tests/test_pipeline_position.py` instead, as in Task 1. Disclosed by the implementer: the 16 repair tests were written as a batch against a stub, and the stale-handling tests, the `updated_at` tests and the new scenarios after the code, so a per-behaviour red was not observed for them. Its choices the plan did not fix are put to the reviews.
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

- **GHI #1193, filed 2026-10-11 on the operator's instruction ("track it as a defect").** `gz obpi acceptance prove` records the mutated source file's host-absolute path in each proof row's `evidence.sweep.source`. Found while committing this run's proof rows; the writer is `src/gzkit/mutation_witness.py`, outside this brief's Allowed Paths.
- **Sibling brief names a removed function.** `OBPI-0.35.0-16-next-command-for-position.md` names `refresh_pipeline_markers` in its Allowed Paths note and its Discovery Checklist. This brief removed it once nothing consumed it. That brief is not this run's to edit and reconciles when the operator initiates it.
- **Acceptance import refuses a restated finding.** `acceptance._record_findings` voids a whole review when an earlier finding identifier returns with any field changed, and the review frame does not tell reviewers that a prior identifier may appear only in a closure. Three reviews in this run could not be imported for it and were re-run whole.
- **`gz plan audit` passes a plan whose tasks complete no REQ.** Such a task cannot be reviewed, because a review context requires an executed proof for every scoped obligation.
- **`data/ledger_vocabulary_grandfather.json` carries two event types that now fire** (`ledger_event_corrected`, `unowned_ratchet_updated`). Pre-existing; a path this brief denies.
- **`ADR-0.33.0` calibration frontier, two measured instances.** Source modules are not ontology nodes, and a transit's own RED receipts read as un-accounted seams.
- **No ledger event ends an abandoned run.** A launch that is neither completed, parked nor withdrawn reads as in flight for good. Lock continuity is Decision item 15 (OBPI-0.35.0-19). Since fix cycle 3 the `gz task` verbs name the run by the TASK's short form only, so beside such a launch under the same semver and item every `gz task` verb records no position and warns (`fc3-AUX-task-verbs-name-the-run-by-short-form-only`, `fc3-aux-task-verbs-cannot-name-one-of-two-runs-in-flight`); no test crosses a task verb in that state.
- **The stale rule has two copies.** `find_stale_pipeline_markers` in `src/gzkit/pipeline_markers.py` and `_stale_on_arrival` in `src/gzkit/pipeline_position.py` each carry the age arithmetic, held together only by tests at the bound. They differ on a zoneless `updated_at`: the rebuild declines, and stale detection raises `TypeError`, a crash that predates this brief and that Requirement 6 forbids this brief to change.
- **`src/gzkit/pipeline_position.py` is over the module-size guidance** (680 lines by the reviewer's reading) and now has four reasons to change: the model, the replay, the recorder and the rebuild.
- **The acceptance proof cannot reach code outside the source root.** `gz obpi acceptance prove` refuses a source file that is not under `src`, so a BEHAVIOR requirement whose code lives under `scripts/` has no proof channel. Worked around here by moving the logic (Open Design Question 18); the tool is unchanged.
- **Found by the Task 5 implementer outside Allowed Paths, not changed.** `_UTF8_PIPE_WAIVERS` in `src/gzkit/governance/trust_audits/cross_platform.py` still lists a line of `docs/governance/pipeline-marker-migration-path.md` that the rewrite removed. The `--clear-stale` help in `src/gzkit/cli/parser_obpi.py` transcribes the stale bound as a number of hours. `docs/governance/state-doctrine.md` says, in a rule quoted from the sealed `ADR-0.0.9`, that running `gz state` reconstructs every derived view; plain `gz state` rebuilds no marker. `docs/user/skills/gz-state.md` names a `.github/skills/` mirror directory that does not exist.
- **A run's ending follows no rename.** The recorder ends a run only when the retirement row carries the id spelling the launch row carries. An OBPI renamed between creation and launch and then parked by pool demotion, or a slug corrected after a launch, leaves a launch in flight (`fc3-AUX-run-ending-matches-the-raw-row-id-and-follows-no-rename`). It needs an `artifact_renamed` row for an OBPI, which no pipeline command writes. **Repaired 2026-10-12 in fix cycle 5 (Question 21):** the in-flight rule compares ids by their current name, so a receipt or a retirement written under either id ends the run. It stays listed until the round after fix cycle 5 has reviewed it.
- **TASK identity under a reused semver.** A TASK id carries only semver and item, and the launch-time auto-start skips a TASK id already started under any OBPI slug, so a TASK's own ledger rows can name a retired sibling (`fc2-aux-task-verbs-hand-over-the-slug-the-tasks-own-ledger-row-names`). Predates this brief.
- **`src/gzkit/pipeline_markers.py` is over the module-size guidance** (917 lines), with three pre-existing functions at or above the threshold table's cyclomatic block entry.

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
