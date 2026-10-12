# Plan — OBPI-0.35.0-15-pipeline-run-position

**OBPI:** OBPI-0.35.0-15-pipeline-run-position
Brief: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-15-pipeline-run-position.md`
Parent: ADR-0.35.0-canon-entry-corpus-landing, Decision item 11, checklist item 15 (repair assignment against ADR-0.13.0, GHI #1172). Lane: Heavy. Sensitivity: security.

## Context

A pipeline marker records the stage the LAUNCH named. `pipeline_marker_payload` sets `current_stage` from `--from`; `write_pipeline_markers` replaces the whole payload at launch; the verify runner writes the marker only on failure; the dispatch writers touch the per-OBPI file alone. A full launch therefore reads `implement` for the whole run, and the legacy and per-OBPI markers diverge after a dispatch. Four Open Design Questions are ruled (A, B+`gz state --repair`, A, A). More were ruled in this session on 2026-10-11 and are recorded in the brief: Question 9 (only a work-starting command moves the stage; a check or a bookkeeping event records in place, which supersedes both Question 5 rulings), Question 10 (the ceremony runner's entry is a named boundary), Question 6 (the run-position concept gets its own module), Question 7 (only Stage 4 review imports record) and Question 8 (the completion receipt ends the run; `gz obpi sync` is not a recorded boundary).

The design the rulings fix:

- **Ledger first, marker second** (Requirement 18, the order `record_dispatch` uses). Each boundary appends one `pipeline_stage_transition` event, then advances both marker files.
- **`current_stage` carries the stage reached** (ruling 4). **The position inside the stage lives in a separate `position` key** `{kind, label, boundary}`, never as a new `current_stage` value (Requirement 3).
- **`gz state --repair` rebuilds a missing marker** from the latest `pipeline_launched` event plus the transitions after it (Requirement 18). Nothing else rebuilds one.
- **No second state file** (ruling 3). The skill and its mirrors gain no step (ruling 1).
- **One module owns the concept** (ruling 6). `src/gzkit/pipeline_position.py` holds the position model, the pure replay, the recorder and the rebuild payload, and takes the ledger as a parameter. `src/gzkit/pipeline_markers.py` keeps every marker file write and never imports the position module; the advance takes the position as plain data. The dependency runs one way, and the registered security surface is unchanged.

Position is `(kind, label)` naming the last boundary crossed: `task`, `phase`, `round` or `step`, with the command's own name as the label. This brief carries no round counter, so a round ordinal is not recorded.

## Destination in mind and rejected alternatives (gz-plan-audit Step 6a)

I formed the transition-event design from the brief's rulings before reading the code, then checked it against the producers. Alternatives considered and rejected:

1. **Infer position from existing events** (Question 2 A). Ruled out by the operator; a boundary with no event cannot be rebuilt.
2. **Put the recorder in the markers module.** It is 825 lines and documents that it does not import the ledger.
3. **Spread the concept across existing modules** (model and replay in the markers module, recorder in the dispatch channel, rebuild in the state command). This was the first plan, because Allowed Paths forbade a new file during implementation. The Task 1 quality review showed the cost (the markers module at 976 lines with a second reason to change), and the operator ruled the new module under Question 6.
4. **Gate in-flight recording on marker presence.** Rejected: a deleted marker would then drop a crossing, and rebuild equality would fail. In-flight is read from the ledger: the latest `pipeline_launched` not followed by `obpi_receipt_emitted`, `obpi_parked` or `obpi_withdrawn` for that id (fix cycle 3, item 21).

## Files

Source: CREATE `src/gzkit/pipeline_position.py`; `src/gzkit/pipeline_markers.py`, `src/gzkit/pipeline_runtime.py`, `src/gzkit/obpi_dispatch_channel.py`, `src/gzkit/commands/obpi_stages.py`, `src/gzkit/commands/obpi_precomplete.py`, `src/gzkit/commands/obpi_complete.py`, `src/gzkit/commands/obpi_present_evidence.py`, `src/gzkit/commands/obpi_verify_packet.py`, `src/gzkit/commands/obpi_acceptance.py`, `src/gzkit/commands/task.py`, `src/gzkit/commands/state.py`, `src/gzkit/commands/obpi_cmd.py`, `scripts/session_orientation.py`.

Event type: `src/gzkit/ledger_events.py`, `src/gzkit/events.py`, `src/gzkit/schemas/ledger.json`, `src/gzkit/ledger.py`, `src/gzkit/governance/trust_audits/events.py`, `src/gzkit/ontology/corpus.py`.

Tests: CREATE `tests/test_pipeline_position.py`; `tests/commands/test_obpi_pipeline.py`, `tests/test_pipeline_runtime.py`, `tests/test_obpi_dispatch_channel.py`, `tests/scripts/test_session_orientation.py`, `tests/test_schemas.py`, `tests/adr/test_state_doctrine.py`. CREATE `features/pipeline_run_position.feature`, `features/steps/pipeline_run_position_steps.py`.

Docs: `docs/user/manpages/obpi-pipeline.md`, `docs/user/manpages/state.md`, `docs/user/runbook.md`, `docs/governance/GovZero/obpi-runtime-contract.md`, `docs/governance/pipeline-marker-migration-path.md`, the `REQ-0.13.0-03-02` line of `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md`, and the OBPI-0.35.0-15 brief (Change Log, Evidence).

`src/gzkit/pipeline_stage_fence.py` is imported read-only for the fence control. Nothing else changes: no hook, guard, ADR-audit, roles, dispatch-wrapper, skill or lock file.

## Steps

**Task cut revised 2026-10-11, during Stage 2.** The first cut grouped work by surface, so its Task 1 (the event type alone) completed no REQ. The acceptance runtime composes a review only over obligations that each hold a current executed proof, and the pipeline skill proves "the current task's BEHAVIOR obligations" before review, so a task that completes no REQ can never be reviewed. The tasks below are cut by the REQs they complete. The design, the files and the boundaries are unchanged. The event-type work already landed is part 1 of Task 1.

One implementer per task, sequential, Red-Green-Refactor with an assertion-level RED (stub the symbol first so the RED fails on an assertion, not an import). Each task writes the `@covers` tests for the REQs it completes, adds their scenarios to `features/pipeline_run_position.feature` (tagged `@REQ-0.35.0-15-NN`, steps in `features/steps/pipeline_run_position_steps.py`, following the existing subagent pipeline feature), and ends with `uv run gz arb ruff` and the task's tests. After each task the orchestrator runs `gz obpi acceptance prove` for the task's REQs, then the spec and quality review scoped to them. A `Task:` trailer is on every production-code and test commit; subdivide REQ labour with `gz task start --seq next`.

### Task 1 — The event type, the marker advance and its readers (completes REQ-0.35.0-15-04 and REQ-0.35.0-15-07; Requirements 3, 5, 7, 8, 9, 18)

Part 1, landed: the `pipeline_stage_transition` event type with every coupled surface.

1. `pipeline_stage_transition_event(obpi_id, parent_adr, stage, position_kind, position_label, boundary, blockers=None)` in `src/gzkit/ledger_events.py`, following `pipeline_marker_purged_event`; `PipelineStageTransitionEvent` in `src/gzkit/events.py` (`stage` and `position_kind` closed literals, `extra="forbid"`) in the discriminated union; the schema entry in `src/gzkit/schemas/ledger.json`; the export from `src/gzkit/ledger.py`; the handler-coverage declaration in `src/gzkit/governance/trust_audits/events.py`; the roster entry in `src/gzkit/ontology/corpus.py`; the table entry and contract tests in `tests/test_schemas.py`.

Part 2:

2. `advance_pipeline_markers(plans_dir, obpi_id, *, stage, position, updated_at, blockers, requires_human_attestation)` in `src/gzkit/pipeline_markers.py`. It loads the per-OBPI marker (legacy as fallback), sets `current_stage`, `position` (`{kind, label, boundary}`) and `updated_at` (the event's `ts`), replaces `blockers`, `required_human_action`, `next_command` and `resume_point` from `pipeline_stage_output` for that stage, and writes the SAME payload to both files. It preserves every other key (`nonce`, `started_at`, `entry`, `receipt_state`, `dispatch_state`, `single_driver_declaration`). It skips a file whose `obpi_id` differs, and does nothing when no marker exists. A position is never written as a `current_stage` value.
3. `refresh_pipeline_markers` derives its stage output from `current_stage`, not `entry` (the bug the brief names).
4. `persist_dispatch_state` and `declare_single_driver` write both files through one shared writer, so the payloads cannot diverge after a dispatch. The re-exports in `src/gzkit/pipeline_runtime.py` follow.
5. `replay_pipeline_position(events, obpi_id)`, the pure replay: the latest `pipeline_launched` for the OBPI, then the `pipeline_stage_transition` events after it in ledger order. It returns the stage, position, blockers and last-crossing time, and the launch stage with no position when nothing follows the launch.
6. REQ-04 tests (`tests/commands/test_obpi_pipeline.py`, `tests/test_pipeline_position.py`): for the full launch and each `--from` entry, `entry`, `current_stage` and `resume_point` are the launch values and no position is reported. `next_command` is not asserted. The existing launch-state assertions pass unchanged; if one cannot, STOP and surface it.
7. REQ-07 tests (`tests/test_pipeline_position.py`, `tests/test_pipeline_runtime.py`, `tests/test_obpi_dispatch_channel.py`): against a marker advanced past `implement`, the fence decides on the stage reached (the fence module is imported read-only), `pipeline_resume_command` and the completion reminder agree with the recorded stage, `load_dispatch_state` still reads it, the six preserved keys are unchanged, and the two files are byte-equal after an advance and after a dispatch.

Part 3, the ruled extraction and the Task 1 review corrections (the reviews of parts 1 and 2 accepted REQ-04 and REQ-07; their unmapped observations are repaired here):

8. Create `src/gzkit/pipeline_position.py` and move `PipelinePosition`, `PipelineReplay`, `PipelineLedgerRow` and `replay_pipeline_position` into it. `advance_pipeline_markers`, `load_obpi_pipeline_marker`, `rewrite_pipeline_markers` and `refresh_pipeline_markers` stay in `src/gzkit/pipeline_markers.py`, which must not import the new module: the advance takes `position` as a plain mapping. `src/gzkit/pipeline_runtime.py` re-exports the moved names so existing imports hold. The module docstring of `src/gzkit/pipeline_markers.py` stops claiming the module is under 600 lines.
9. The replay invents nothing: a transition row lacking a required field is not a crossing, and a test proves it. Its cyclomatic complexity comes under the block entry of the threshold table (it measured 16).
10. The dispatch cache reads and writes symmetrically: `load_dispatch_state` and the dispatch channel's marker reader use the shared loader that `persist_dispatch_state` writes through, with tests for the legacy fallback and for a corrupt per-OBPI marker.
11. The REQ-04 test also asserts `blockers` and `required_human_action` on the marker for each entry, and a full launch of a brief that HAS acceptance-criteria REQs (so TASKs are auto-started) still reports no position.

### Task 2 — `record_position` and every producer (completes REQ-0.35.0-15-01 and REQ-0.35.0-15-02; Requirements 1, 2, 12, 16, 17, 18)

1. `record_position(ledger, plans_dir, obpi_id, *, stage, kind, label, boundary, blockers=None)` in `src/gzkit/pipeline_position.py`, taking the ledger as a parameter. It does nothing unless the ledger shows a run in flight (the latest `pipeline_launched` not followed by `obpi_receipt_emitted`, `obpi_parked` or `obpi_withdrawn` for that id; items 16 and 21 below say how the run is found); then it appends the event and calls `advance_pipeline_markers`. A marker I/O failure warns and never raises, because a position is never gate evidence (Requirement 12).
2. **Stage 2.** `record_dispatch` records `(implement, task, "task <n>")`. The `gz task` verbs `start`, `complete`, `block`, `escalate` and `start --req` in `src/gzkit/commands/task.py` record `(implement, task, <TASK id>)` after their own event. The launch-time `auto_start_obpi_tasks` and the completion-time `auto_complete_obpi_tasks` do not record. A `gz task` event during Stage 3 or Stage 4 therefore re-enters `implement` through the runtime, which is the recorded re-entry ruling 4 requires.
3. **Stage 3.** The verify runner in `src/gzkit/commands/obpi_stages.py` records `(verify, phase, "verification")` at start, `"verification-passed"` on pass and `"verification-failed"` with the blockers on failure, in place of the bare `refresh_pipeline_markers` call.
4. **Stage 4.** The ceremony runner records `(ceremony, round, "ceremony")` on entry after the Stage-2 acceptance check; the verify runner chains straight into it, so the marker reads `ceremony` after a passed verification. `src/gzkit/commands/obpi_present_evidence.py` records `"present-evidence"` after the packet is written; `src/gzkit/commands/obpi_verify_packet.py` records `"verify-packet"`; in `src/gzkit/commands/obpi_acceptance.py` a successful import records `"acceptance-review"` only when the imported review is adversarial or a human review; a spec or quality import records nothing (Question 7).
5. **Precomplete; Stage 5 complete.** `src/gzkit/commands/obpi_precomplete.py` records in place (Question 9, item 10 below): its position inside the stage the run has reached, never a change of stage. `src/gzkit/commands/obpi_complete.py` records `(sync, step, "complete")` as its transaction starts, before the receipt, because the receipt ends the run (Question 8). `gz obpi sync` and the sync runner record nothing.
6. REQ-01 and REQ-02 tests (`tests/commands/test_obpi_pipeline.py`, `tests/test_pipeline_position.py`, `tests/test_obpi_dispatch_channel.py`): after a full launch crosses into `verify`, `ceremony` or `sync`, both marker files read that stage with `updated_at` later than `started_at`; each producer appends exactly one event before the marker write and the marker names the task, phase, round or step; no event when no run is in flight; dispatch credit still reads the ledger.
7. Requirement 16: `test_verify_rewrites_markers_with_verify_stage_state` asserts the marker reads the ceremony stage after a passed verification, and its docstring records the ruling. Add the dated amendment note to the `REQ-0.13.0-03-02` line of the sealed OBPI-0.13.0-03 brief, in the form of the note on `REQ-0.0.14-03-07` (the attested-REQ subject-retirement doctrine, Worked example 4), naming no command line.
8. Requirement 17: move the `@covers` for `REQ-0.13.0-02-01`, `-02-02`, `REQ-0.13.0-03-02` and `-03-03` onto the tests that assert them, with the reason in each docstring. No binding is dropped.

Fix cycle 1, after the Task 2 reviews (quality refuted REQ-02 on mapped finding QR2-REQ02-noncanonical-id-records-nothing; Questions 9 and 10 ruled):

9. **Canonical id.** Every producer records under the id the launch carries: the project-root adapters resolve a short OBPI id the way the launcher does before they match a launch. A test crosses each id-taking producer with the short form.
10. **Stage movement (Question 9).** One table, in `src/gzkit/pipeline_position.py`, says which boundaries move the stage. Work-starting boundaries move it: the verify runner start, the ceremony runner's entry, `gz obpi present-evidence`, `gz obpi complete`, `gz task start` and `gz obpi dispatch`. Every other boundary records in place: the stage is the one the ledger replay says the run has reached, the kind is that stage's kind, and the label is the command's own. `gz task complete`, `block` and `escalate`, `gz obpi precomplete`, `gz obpi verify-packet`, the review import and the verification pass and fail are in-place.
11. **Bounded blockers.** A transition event carries a bounded summary of each blocker, never a command's whole output.
12. **The record never fails its host.** An I/O failure while recording a position warns and returns; the host command's own outcome stands. A malformed argument still raises.
13. **REQ-01 on an unbroken run.** The covering test also takes a run launched in full to `ceremony` through `gz obpi present-evidence` and to `sync` through `gz obpi complete` with no re-entry, asserting `entry` is still `full` and the nonce is unchanged. The tests proving that a non-boundary records nothing are bound to REQ-0.35.0-15-02.
14. **BDD drives the commands.** The REQ-01 and REQ-02 scenarios cross their boundaries through the real commands, not the recorder.
15. **Residue.** One helper for the verify runner's three record calls; one project-ledger helper, not two; the recorder takes the position as one value so its parameter count comes down; `refresh_pipeline_markers` is removed if nothing consumes it. Say what was compressed.

Fix cycle 2, after the fix-cycle reviews (spec refuted REQ-02 on a second id counterexample; quality accepted and closed the first, with structural observations). This is the last fix cycle the pipeline allows Task 2:

16. **The recorder matches the run itself.** The first repair put id resolution in each caller, through three different paths, and `gz task start` on a TASK's first start still reached the recorder with the short id when the ledger graph held a second key under that prefix. `record_position` now finds the run by reading the ledger rows it already reads: the in-flight launch whose id equals the id given, or whose short `OBPI-<semver>-<item>` form equals it, and it records under that launch's id. Two in-flight launches sharing a short form record nothing and warn. No caller resolves an id for the recorder any more: the adapter's resolution through the command layer is removed, with its function-level import and its scan of every brief.
17. **Every producer is crossed by short id.** The short-id test also covers `gz obpi complete` and each `gz task` verb, including a first `gz task start` with a second key under the same prefix on the ledger graph, and the recorder's own matching rule is tested directly: exact id, short form, two launches sharing a short form, and a different OBPI.

18. **Precomplete names the run for its controls too.** Pre-existing defect found by the fix-cycle quality review (`fc1-AUX-precomplete-checks-still-run-under-the-typed-id`): `gz obpi precomplete` decides whether a pipeline ran by testing for the marker file under the id as typed, so a short id reports "no active pipeline marker" and passes the Stage 2 dispatch check while a run is in flight. The check uses the in-flight launch's id, from the same matching rule as item 16. No control is weakened: the check becomes stricter for a short id and is unchanged for a full one.
19. **The REQ-02 proof carries the id control.** With the matching rule inside `src/gzkit/pipeline_position.py`, the acceptance proof for REQ-0.35.0-15-02 mutates it directly instead of leaving that control to a supplementary sweep.

20. **A check never erases a failed verification.** Found by the fix-cycle spec review (`fc1-aux-in-place-record-after-failed-verification-drops-blockers`): an in-place record wrote no blockers, the replay keeps the last crossing's blockers only, and the marker of a run whose verification had failed then read no blockers and a resume point of `ceremony`. An in-place record carries the run's blockers forward; only a verification result sets them, and a work-starting boundary clears them. The ruled table says which boundaries settle blockers.

Fix cycle 3, authorized by the operator past the two-cycle bound (brief Question 12) after the third review round left one mapped finding open:

21. **Retirement ends a run.** A run is in flight from its latest `pipeline_launched` until an `obpi_receipt_emitted`, an `obpi_parked` or an `obpi_withdrawn` for that id follows it; a later launch starts a new run. This is the rule the launcher's id resolution already applies to parked and withdrawn siblings.
22. **A task verb names the run by the TASK's short form.** `gz task start`, `complete`, `block` and `escalate` hand the recorder the `OBPI-<semver>-<item>` their TASK id carries, never the slug a `task_started` row happens to name, so a TASK first started under a retired sibling records in the live run. The verb's own task event keeps the id it has today.
23. **One short form, whatever the item's width.** The recorder's short form is the whole `OBPI-<semver>-<item>`, matched against the next `-` or the end of the id, so item 10 never names item 100.

### Task 3 — `gz state --repair` rebuilds the marker (completes REQ-0.35.0-15-03 and REQ-0.35.0-15-05; Requirements 4, 6, 18)

1. `state_repair` in `src/gzkit/commands/state.py` keeps its frontmatter reconciliation and adds the rebuild; the payload it writes is built by a function in `src/gzkit/pipeline_position.py`. For each OBPI with a `pipeline_launched` event and no later `obpi_receipt_emitted`, whose per-OBPI marker is missing, it writes both markers from the replay. The launch event supplies `obpi_id`, `parent_adr`, `lane`, `entry`, `nonce` and `started_at`. `receipt_state` is read back from the plan-audit receipt file, or "missing" when there is none.
2. A rebuild never moves a live marker and never writes a position that has no ledger source. The rebuilt `updated_at` is the last recorded crossing, so a rebuild cannot make an abandoned run look live. A run whose last recorded crossing is older than `STALE_MARKER_HOURS` is not rebuilt at all: its marker would be stale on arrival, and the live ledger holds launches that were never completed (measured 2026-10-11: `OBPI-0.47.0-02` and `OBPI-0.0.37-17`), whose resurrected markers would trip the concurrency block. `--repair` reports each run it declines to rebuild and why.
3. Not rebuilt, and stated in `docs/user/manpages/state.md`: the `dispatch_state` and `single_driver_declaration` caches. Dispatch credit reads the ledger, so no gate depends on them.
4. REQ-03 tests (`tests/adr/test_state_doctrine.py`): delete both markers mid-run, run `--repair`, and assert the same `current_stage` and `position`, a `nonce` a `pipeline_launched` event recorded, and the `updated_at` of the last crossing; a launch with nothing after it rebuilds to the launch values.
5. REQ-05 tests (`tests/test_pipeline_runtime.py`, `tests/test_pipeline_position.py`): a marker older than `STALE_MARKER_HOURS`, an unreadable one, one with no `updated_at` and one whose OBPI is `attested_completed` each behave as before under stale detection, `--clear-stale` and the orphan purge; reading a position or rebuilding a marker does not move `updated_at`; the concurrency block is unchanged.

Corrections carried into this task from the Task 2 review rounds (unmapped observations and one pre-existing defect in a named control; each is recorded in the brief's Change Log). They touch `src/gzkit/pipeline_position.py`, so REQ-0.35.0-15-01 and REQ-0.35.0-15-02 are re-proved with the rest on the finished tree:

6. **One notion of in flight.** The rebuild takes the runs it considers from the recorder's own rule in `src/gzkit/pipeline_position.py`, never a second copy: a run is in flight from its latest `pipeline_launched` until a run-ending event for that id (item 21 of Task 2). Item 1 above says "no later `obpi_receipt_emitted`"; the recorder's rule governs, so a parked or withdrawn OBPI's marker is not rebuilt.
7. **Only a completion receipt ends a run** (brief Question 8; `fc3-AUX-a-receipt-that-is-not-a-completion-ends-the-run`, `fc3-aux-any-obpi-receipt-event-ends-a-run-whatever-its-receipt-kind`). The run-ending rule reads the receipt's `receipt_event`: `completed` ends the run, `validated` ends nothing. Tests: a `validated` receipt for a run in flight leaves it in flight for the recorder, for `in_flight_launch_id` and for the rebuild; a `completed` receipt ends it as before.
8. **Unpark starts no run** (brief Question 12: "a later launch starts a new run"; `fc3-AUX-unpark-does-not-resume-the-run-the-park-ended`). An OBPI launched, parked and unparked has no run in flight until it is launched again: the recorder records nothing, and the rebuild writes no marker. A test pins both. The comment on the run-ending events stops claiming parity with the launcher's id resolution, which reads `obpi_unparked` and holds for park and withdraw only.
9. **Precomplete names the OBPI once, at entry** (Requirement 11; `fc1-AUX-precomplete-checks-still-run-under-the-typed-id`, `fc2-aux-precomplete-operator-block-check-still-reads-the-id-as-typed`, `fc3-aux-precomplete-dispatch-check-reads-the-typed-id-once-the-run-is-retired`). `gz obpi precomplete` already resolves a brief from the id as typed. Every check, and the position record, then uses the canonical id that brief carries, so a short id reads the same operator block, the same marker and the same dispatch records as the full id, whether or not a run is in flight. No control is weakened: each check is unchanged for a full id and no weaker for a short one. Tests: with an operator block standing, a short id is refused as the full id is; with the run retired or the OBPI parked, unparked and not relaunched, the Stage 2 dispatch check for a short id reads the marker the full id reads.
10. **REQ-05, the two new unreadable shapes.** The marker loader now reads JSON that is not an object, and bytes that are not UTF-8, as unreadable. The REQ-05 tests cover both shapes under stale detection, `--clear-stale` and the orphan purge, beside the unreadable marker the suite already had.
11. **The command's own page.** `docs/user/manpages/state.md` states the rebuild, what it does not restore (item 3) and that it reports each run it declines to rebuild, in the same change as the code. Task 5 checks it against the other docs.

### Task 4 — Orientation (completes REQ-0.35.0-15-06; Requirement 10)

`collect_adr_pipeline` in `scripts/session_orientation.py` also reports `position`; `_render_adr_pipeline` shows the stage reached and the position inside it. Tests in `tests/scripts/test_session_orientation.py`: an in-flight run advanced past its launch stage renders the stage reached and its position, not the launch stage.

### Task 5 — Docs, in the same change (completes REQ-0.35.0-15-08 and REQ-0.35.0-15-09; Requirements 14, 18)

`docs/user/manpages/obpi-pipeline.md` states the marker contract, including `position`, and corrects two misstatements: `--from=verify` "clears active markers on success" and `--from=ceremony` "clears active markers on exit"; the runtime keeps both markers until Stage 5. It also says a `gz task` event re-enters `implement`, and how a deleted marker is rebuilt. `docs/user/runbook.md` agrees with it. `docs/user/manpages/state.md` states the rebuild and what it omits. `docs/governance/GovZero/obpi-runtime-contract.md` § Active Pipeline Marker Fields adds `position` and the `sync` value of `entry` and `current_stage`. `docs/governance/pipeline-marker-migration-path.md` describes the Layer-2 source and the rebuild as ruled, not as future intent.

### After the tasks — verify and prove (Requirement 15)

Re-run `gz obpi acceptance prove` for every obligation on the finished tree, then the final spec and quality review, then the brief's verification commands. Capture the orientation's `Active ADR pipeline state` section from this OBPI's own run once it has advanced past its launch stage. Then Stage 4 with the independent Step 4b adversary (Codex first).

## Verification

- `uv run -m unittest tests.test_pipeline_position tests.commands.test_obpi_pipeline tests.test_pipeline_runtime`
- `uv run -m unittest tests.test_obpi_dispatch_channel tests.scripts.test_session_orientation tests.test_pipeline_stage_fence`
- `uv run -m unittest tests.test_schemas tests.adr.test_state_doctrine`
- `uv run -m behave features/pipeline_run_position.feature`
- `uv run gz validate --documents --req-kind-discipline --cli-alignment`
- `uv run gz cli audit`
- `uv run mkdocs build --strict`
- `uv run gz check`

## Notes

- **Fence consequence.** The post-Stage-2 fence now binds every run once the stage advances. A Stage 3 or Stage 4 repair that edits production code needs a `gz task start` first to re-enter `implement`. Task 9 documents this, because the fence's refusal message already prescribes the recorded re-entry.
- **Size.** `src/gzkit/pipeline_markers.py` was 825 lines at the start and reached 976 after Task 1 parts 1 and 2. The extraction under Question 6 moves the model and the replay out; the recorder and the rebuild payload land in the new module.
- **A round is recorded by the boundary command's name, not by an ordinal.** The first Question 5 ruling read Requirement 2's Stage 3 mention of `precomplete` as a drafting overlap; that premise was wrong and the ruling is superseded.
