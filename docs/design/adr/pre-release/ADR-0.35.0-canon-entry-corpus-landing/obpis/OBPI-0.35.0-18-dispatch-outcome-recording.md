---
id: OBPI-0.35.0-18-dispatch-outcome-recording
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 18
lane: Heavy
sensitivity: security
status: Draft
allowlist:
  - src/gzkit/obpi_dispatch_channel.py
  - src/gzkit/pipeline_runtime.py
  - src/gzkit/pipeline_dispatch.py
  - src/gzkit/pipeline_verification.py
  - src/gzkit/commands/obpi_dispatch.py
  - src/gzkit/cli/parser_obpi.py
  - src/gzkit/commands/roles.py
  - src/gzkit/events.py
  - src/gzkit/ledger_events.py
  - src/gzkit/ledger.py
  - src/gzkit/schemas/ledger.json
  - src/gzkit/governance/trust_audits/events.py
  - src/gzkit/ontology/corpus.py
  - tests/test_obpi_dispatch_channel.py
  - tests/test_pipeline_integration.py
  - tests/test_pipeline_dispatch.py
  - tests/test_review_protocol.py
  - tests/test_verification_dispatch.py
  - tests/test_roles_cli.py
  - tests/commands/test_obpi_dispatch.py
  - tests/test_schemas.py
  - features/obpi_dispatch_outcome.feature
  - features/steps/obpi_dispatch_outcome_steps.py
  - features/subagent_pipeline.feature
  - features/steps/subagent_pipeline_steps.py
  - docs/user/manpages/obpi-dispatch.md
  - docs/user/manpages/roles.md
  - docs/user/concepts/subagent-pipeline.md
  - docs/user/runbook.md
  - docs/governance/governance_runbook.md
  - .gzkit/skills/gz-obpi-pipeline/SKILL.md
  - src/gzkit/skills/gz-obpi-pipeline/SKILL.md
  - .claude/skills/gz-obpi-pipeline/SKILL.md
  - .agents/skills/gz-obpi-pipeline/SKILL.md
  - src/gzkit/canonical_history.json
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-18-dispatch-outcome-recording.md
reqs:
  - REQ-0.35.0-18-01
  - REQ-0.35.0-18-02
  - REQ-0.35.0-18-03
  - REQ-0.35.0-18-04
  - REQ-0.35.0-18-05
  - REQ-0.35.0-18-06
  - REQ-0.35.0-18-07
  - REQ-0.35.0-18-08
  - REQ-0.35.0-18-09
  - REQ-0.35.0-18-10
verification:
  - uv run -m unittest tests.test_obpi_dispatch_channel tests.test_pipeline_integration tests.test_pipeline_dispatch tests.test_review_protocol tests.test_verification_dispatch tests.test_roles_cli tests.commands.test_obpi_dispatch
  - uv run -m behave features/obpi_dispatch_outcome.feature features/subagent_pipeline.feature
  - uv run gz validate --documents --req-kind-discipline --cli-alignment
  - uv run gz cli audit
  - uv run gz skill audit
  - uv run mkdocs build --strict
  - uv run gz check
---

# OBPI-0.35.0-18-dispatch-outcome-recording: Dispatch Outcome Recording

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #18 - "Stage 2 dispatch outcome recording -- the runtime records each dispatch's status, changed files, added tests, concerns, fix cycles and review findings from the subagent's structured result. Repair assignment against `ADR-0.18.0` (GHI #1175, amendment 2026-10-04)"
- **§ Decision item 14, verbatim:** "A STAGE 2 DISPATCH'S OUTCOME IS RECORDED BY THE RUNTIME (operator-ruled 2026-10-04, GHI #1175; repair assignment). The runtime records how each dispatch ended, from the subagent's structured result: its status, the files it changed, the tests it added, its concerns, and the fix cycles and review findings that followed. Obligation repaired: `REQ-0.18.0-02-04`, "Each subagent MUST return a structured result: `{status, files_changed, tests_added, concerns}`", and `OBPI-0.18.0-05`, "Pipeline runtime MUST track subagent dispatch state". Stage 2 dispatch credit stays Layer-2 evidence."

**This is a repair assignment.** It does not extend ADR-0.35.0's corpus intent (§ Intent, amendment 2026-10-04). It repairs obligations that `ADR-0.18.0-subagent-driven-pipeline-execution` stated and its shipped surface does not meet. That ADR is `Validated` and is not reopened; the obligations keep their identities:

- `REQ-0.18.0-02-04`: "Each subagent MUST return a structured result: `{status, files_changed, tests_added, concerns}`." The result is returned and then read only by the orchestrating model.
- `REQ-0.18.0-05-01`: "Pipeline runtime MUST track subagent dispatch state: `{task_id, role, agent_file, model, isolation, background, dispatched_at, completed_at, status, result}`." `completed_at`, `status` and `result` are modelled and no production path writes them.
- `REQ-0.18.0-05-03`: "Result aggregation MUST compute: total tasks, completed, blocked, fix cycles, review findings by severity, model usage per role." The aggregation is implemented and no production path runs it.
- `REQ-0.18.0-05-06`: "`gz roles --pipeline {OBPI-ID}` MUST show which roles were dispatched, their model overrides, isolation mode, and results for a completed or active pipeline run." It shows no results, and nothing for a completed run.

This brief's own REQs (`REQ-0.35.0-18-NN`) are local acceptance criteria for the repair. It stands alone: it depends on no other item of ADR-0.35.0, and items 15-17 do not depend on it.

**Status:** Draft

## Objective

When a Stage 2 subagent (Implementer, SpecReviewer, QualityReviewer) or a Stage 3 verification subagent returns, the runtime parses the returned text and records how the dispatch ended, so that a process which did not run the dispatch reads its status, changed files, added tests, concerns, review findings and fix-cycle count from disk. A missing or invalid result block is recorded as that and never reads as success.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The contract changes are an outcome-recording form of `gz obpi dispatch` (Question 2, ruled), new fields in the `gz roles --pipeline` JSON output, and a new ledger event type (Question 1, ruled).

**Sensitivity: security.** The Allowed Paths overlap registered security surfaces in `data/security_surfaces.json`: `src/gzkit/pipeline_dispatch.py` (category `deserialization_user_input`) under every answer to the open questions, and `src/gzkit/ledger_events.py` with `src/gzkit/ledger.py` (category `ledger_integrity`) under the ruling on Question 1. `.gzkit/rules/security-sensitivity.md` makes the declaration mandatory on overlap, so it is not a design choice. The work is what the registry describes: text returned by a subagent is parsed and written to a durable record. `gz obpi complete` therefore runs the extended Gate 5 walkthrough with the security-scan receipt.

## Allowed Paths

**Runtime: the recorder, the records, the reader**

- `src/gzkit/obpi_dispatch_channel.py` — the dispatch recorder; a recorded dispatch gains its outcome here. The credit logic in this module is read and not changed.
- `src/gzkit/pipeline_runtime.py` — the dispatch record model and its completion, persistence, aggregation and summary functions
- `src/gzkit/pipeline_dispatch.py` — the result parsers and the task-status and fix-cycle logic. Registered security surface.
- `src/gzkit/pipeline_verification.py` — Stage 3 verification result parsing and its dispatch records
- `src/gzkit/commands/obpi_dispatch.py` — the dispatch command handler, home of outcome recording (Question 2, ruled)
- `src/gzkit/cli/parser_obpi.py` — the dispatch parser: arguments, help text and exit codes
- `src/gzkit/commands/roles.py` — the reader: outcome, fix cycles and aggregation in the pipeline view

**Ledger event files: in scope by the ruling on Question 1 (ledger-backed)**

- `src/gzkit/events.py` — the typed event model
- `src/gzkit/ledger_events.py` — the event constructor. Registered security surface.
- `src/gzkit/ledger.py` — the constructor re-export. Registered security surface.
- `src/gzkit/schemas/ledger.json` — the event schema
- `src/gzkit/governance/trust_audits/events.py` — the event-handler roster
- `src/gzkit/ontology/corpus.py` — the ontology event roster
- `tests/test_schemas.py` — the schema roster test

**Tests**

- `tests/test_obpi_dispatch_channel.py` — recorder behaviour and the credit control
- `tests/test_pipeline_integration.py` — record completion, persistence, aggregation, summary
- `tests/test_pipeline_dispatch.py` — result parsing and task-status handling
- `tests/test_review_protocol.py` — review result derivation and the fix-cycle bound
- `tests/test_verification_dispatch.py` — Stage 3 verification results and records
- `tests/test_roles_cli.py` — the reader
- `tests/commands/test_obpi_dispatch.py` — **CREATE**, the dispatch command contract. Convention checked against the sibling test_obpi_pipeline.py in the same directory.
- `features/obpi_dispatch_outcome.feature` — **CREATE**. Convention checked against the sibling obpi_lock.feature, which drives the real CLI.
- `features/steps/obpi_dispatch_outcome_steps.py` — **CREATE**. Convention checked against the sibling obpi_lock_steps.py.
- `features/subagent_pipeline.feature` — existing scenarios that pin the aggregation and fix-cycle behaviour this brief corrects
- `features/steps/subagent_pipeline_steps.py` — their steps

**Docs and skill**

- `docs/user/manpages/obpi-dispatch.md` — the outcome-recording surface, its exit codes and what a recorded outcome is not
- `docs/user/manpages/roles.md` — the pipeline view's outcome, fix-cycle and aggregation fields
- `docs/user/concepts/subagent-pipeline.md` — the Dispatch State section
- `docs/user/runbook.md` — the Stage 2 dispatch, review and Stage 3 verification passages
- `docs/governance/governance_runbook.md` — the one line naming the dispatch command, if its contract changes
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — the canonical skill: Stage 2 Subagent Dispatch Mode and Stage 3 Phase 2
- `src/gzkit/skills/gz-obpi-pipeline/SKILL.md`, `.claude/skills/gz-obpi-pipeline/SKILL.md`, `.agents/skills/gz-obpi-pipeline/SKILL.md` — generated mirrors, written only by `uv run gz agent sync control-surfaces`, never hand-edited
- `src/gzkit/canonical_history.json` — generated, written by the same sync
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-18-dispatch-outcome-recording.md`

## Denied Paths

- `src/gzkit/roles.py` — the result contracts `HandoffResult` and `ReviewResult` are imported and not changed. `REQ-0.18.0-02-04`'s four fields stay as they are.
- `src/gzkit/acceptance.py`, `src/gzkit/acceptance_store.py`, `src/gzkit/commands/obpi_acceptance.py` — the acceptance store already records each imported review on the ledger. It is read here and never changed; its readiness and finding-closure rules are untouched.
- `src/gzkit/commands/obpi_precomplete.py` — the Stage 5 dispatch verdict is a control this brief must leave exactly as it is.
- `src/gzkit/pipeline_markers.py`, `src/gzkit/commands/obpi_cmd.py` — marker stage, resume point, next command and the launch path belong to items 15-17. Both are registered security surfaces.
- `.gzkit/agents/**` — agent definitions, tool grants and the Implementer's result format are not changed.
- `data/ledger_vocabulary_grandfather.json`, `data/security_surfaces.json` — no grandfather entry and no registry edit.
- `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/**` — the Validated ADR and its attested briefs are cited, never edited.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` — the parent ADR is read, not edited.
- Results returned by a subagent as a file path and an exit code. That is new design and GHI #1175 does not ask for it.
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The runtime does the parse. The outcome of a dispatch is recorded from the text the subagent returned, parsed by `parse_handoff_result` (Implementer) or `parse_verification_results` (Stage 3). A reviewer's outcome is derived from the review the acceptance store holds for the same receipt, which the acceptance review import recorded from the reviewer's text; the dispatch record points at that review and holds no second copy of its findings (operator ruling 2026-10-04, Question 4). The orchestrating model MUST NOT supply a parsed status, a field value or a count in place of that text.
2. REQUIREMENT: A recorded Implementer outcome carries the four `HandoffResult` fields (`status`, `files_changed`, `tests_added`, `concerns`) and a completion time. A recorded reviewer outcome carries a completion time and, by reference to the acceptance store's review for the same receipt, the verdict, the findings with their severities and the verification gaps; a reviewer dispatch with no such review is recorded as missing or invalid (Requirement 4). Every recorded dispatch of the three mandated roles names its role's agent file.
3. REQUIREMENT: Every recorded outcome is readable from disk by a process that shares no memory with the one that recorded it. The reader of record is `gz roles --pipeline` with `--json`, for an active run and for a completed one (`REQ-0.18.0-05-06`).
4. REQUIREMENT: Returned text with no result block, unparseable JSON, an unknown status, or a field outside the contract is recorded as an outcome that names the block missing or invalid. One such state is enough; the two need not be told apart. That outcome is never `done`, `done_with_concerns` or `PASS`, is never counted as completed, and no reader renders it as success. A dispatch with no outcome recorded reads as unrecorded, never as success.
5. REQUIREMENT: A fix cycle is one re-dispatch of the Implementer for a task after a review that blocks advancement. The count per task is recorded when the cycle happens. A later session reads the same count, and the reader states whether the count has reached `MAX_REVIEW_FIX_CYCLES`. Dispatches of different roles for one task are not fix cycles. Implementer retries for `NEEDS_CONTEXT` and `BLOCKED` are not fix cycles; recorded outcomes make them countable, and this brief adds no enforcement for them.
6. REQUIREMENT: The six quantities of `REQ-0.18.0-05-03` are computed by a production path from recorded outcomes and returned by the same reader. Total tasks counts tasks, not dispatch records.
7. REQUIREMENT: For each Stage 3 verification dispatch, the outcome of every requirement it was asked to verify is recorded from its returned text. An expected requirement with no parsed result is recorded as having none, never as `PASS`. The same reader returns these beside the Stage 2 records, and neither kind of record makes the other unreadable. This brief's Stage 3 scope ends there: baseline checks, covers parity, the RED witness and timing metrics are not in it.
8. NEVER: Let an outcome record change dispatch credit. Credit comes only from `stage2_dispatch_recorded` ledger events (GHI #886). The Stage 5 dispatch verdict is the same with and without outcome records, whatever they say and wherever they are stored. `Verifier` is not added to the mandated Stage 2 roster.
9. NEVER: Add a gate, verdict or attestation that reads a recorded outcome. Under `ADR-0.0.9` Rule 5 a marker-held value can never be gate evidence, and whether a subagent's own claim is evidence is Question 3. Every reader labels the outcome as what the subagent reported.
10. NEVER: Ask a declared single-driver run for an outcome. A run carrying a `stage2_single_driver_declared` event behaves exactly as it does today: same exit codes, same rendering, same Stage 5 verdict.
11. NEVER: Remove a pipeline control (campaign plan § Amendments 2026-10-04 (2)). After the skill edit, Stage 2 still states the handling of all four result statuses, both retry limits, the review gate, the two-stage review, receipted reviewer execution, the acceptance review import, the separation of verification gaps from findings, the fix-cycle bound, the dispatch-recording step and the Stage 2 acceptance readiness check. The edit changes who parses and who counts. It does not change what is checked.
12. ALWAYS: Edit the skill in `.gzkit/skills/`, bump `metadata.skill-version` and `last_reviewed`, and run `uv run gz agent sync control-surfaces`. The skill body may not grow past its ceiling in `src/gzkit/skill_body_grandfather.json`: compress first (`.gzkit/rules/skill-authoring.md` § Parsimony 6).
13. ALWAYS: Correct, in the same change, every doc passage that describes recording which does not happen today (§ Measured Ground Truth names them).
14. ALWAYS: Before acceptance, show one real dispatched Stage 2 run whose outcomes the delivered surface recorded and a fresh process read back. A fixture run does not discharge this. `uv run gz check` is green on the final tree.
15. REQUIREMENT (operator ruling 2026-10-04, Question 1): each recorded outcome appends one ledger event, and that event is the record. The marker's `dispatch_state` and the completion summary are caches written after it and rebuilt from those events, in the order `record_dispatch` uses. The event type is added with every coupled surface a ledger event type has, and the plan sequences the first real recording before the tree is checked, because a declared event type that has never fired trips the ledger-vocabulary inertness check.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt. The five Open Design Questions below are prerequisites: no plan is written until the operator has ruled each.

## Open Design Questions (operator rules before plan)

Each question names what changes in this brief if the ruling differs from the recommendation. The requirements above hold under every option unless a question says otherwise.

**1. Where the outcome lives.**
- A. A ledger event only.
- B. The marker's `dispatch_state` and a completion summary only, as `REQ-0.18.0-05-02` worded it.
- C. A ledger event is the record; the marker and the summary are caches rebuilt from it.

B is the smallest change and needs no ledger files. It is permissible only because no gate reads the outcome. It loses the outcome when the marker is cleared by `gz obpi pipeline --clear-stale`, which is the loss GHI #886 measured for credit, and it leaves the marker holding state that cannot be rebuilt from the ledger, against § Decision item 11's "rebuildable from canon and ledger". A and C survive both. C keeps `gz roles` working without a ledger scan.
**Recommendation: C**, in the order `record_dispatch` already uses (ledger first, cache second). Under B, remove the seven ledger-event paths. Under A or C, note that a declared event type which has not yet fired trips the ledger-vocabulary inertness check: the plan must sequence the first real recording before the tree is checked. `data/ledger_vocabulary_grandfather.json` is denied.
**RULED 2026-10-04: C.** Asked where a dispatch's outcome lives, with the ledger event as the record and the marker and summary as caches put as option A, the operator answered, verbatim: "A". Option B, marker only, was not put: § Decision item 11 keeps the marker rebuildable from canon and ledger, and the ruling on `OBPI-0.35.0-15` Open Design Question 2 already makes the ledger the record. Requirement 15 carries the ruling.

**2. What CLI surface records an outcome.**
- A. Extend `gz obpi dispatch`: the existing verb gains the outcome-recording form. A new flag is a Heavy contract change with a manpage row.
- B. A new subcommand under `gz obpi`, with the seven obligations of `.gzkit/rules/cli.md` § New Subcommand.

Either way the returned text reaches the command as a file or standard input that the orchestrator passes unedited, and the exit code for a missing or invalid block is settled in the plan.
**Recommendation: A.** The module docstring of `src/gzkit/commands/obpi_dispatch.py` calls this verb "the call"; a second verb would split one record across two commands. Under B, add `config/doc-coverage.json`, a new manpage, `docs/user/manpages/index.md` and a wielding-skill line to Allowed Paths.
**RULED 2026-10-04: A.** Asked which command records an outcome, the operator answered, verbatim: "A". `gz obpi dispatch` gains the outcome-recording form; no subcommand is added. The flag and the exit code for a missing or invalid block are settled in the plan. Allowed Paths already cover the ruling.

**3. Whether a subagent's own claim counts as evidence.**
- A. Record it as a claim, labelled as reported, read by no gate. This is canon today: `.gzkit/rules/model-selection.md` operative claim 5, "A subagent's claim is not evidence."
- B. As A, and the runtime also compares `files_changed` with the files actually changed and marks each claim corroborated or not.
- C. Treat the recorded outcome as evidence. This contradicts claim 5.

**Recommendation: A.** B is new design that GHI #1175 does not ask for. Requirement 9 holds under A and B; C would need it rewritten and a ruling against claim 5.
**SETTLED BY CANON 2026-10-04: A.** Not put to the operator as a choice. `.gzkit/rules/model-selection.md` operative claim 5 already rules it: "A subagent's claim is not evidence." Option C contradicts that rule, and option B is new design outside a repair assignment. The operator was told and may rule otherwise; Requirement 9 stands as written.

**4. Where a reviewer's outcome comes from.**
- A. Derive it from the review the acceptance store already holds for the same receipt (the `acceptance_recorded` ledger row written by the acceptance review import). One record of the findings; the dispatch outcome points at it.
- B. Parse the reviewer's text a second time into the dispatch record. Two records of one review, held together by REQ-0.35.0-18-03's agreement clause.

**Recommendation: A** (`.gzkit/rules/hexagonal-architecture.md` operative rule 8: prefer subsumption to a parallel model). Both options leave the acceptance store unedited.
**RULED 2026-10-04: A.** Asked where a reviewer's outcome comes from, the operator answered, verbatim: "A". The dispatch outcome points at the review the acceptance store already holds for the same receipt. Requirements 1 and 2 carry it.

**5. Whether the resume rendering is a consumer.**
GHI #1175's boundary names "the consumers `gz roles` and the resume rendering". Measured: nothing in `src/gzkit/pipeline_markers.py` reads `dispatch_state`; its only readers are `gz roles` and the recorder.
- A. Leave resume and reminder output unchanged here. Run position and next command are items 15-16.
- B. Add the outcome to that output in this brief.

**Recommendation: A.** Under B, move `src/gzkit/pipeline_markers.py` from Denied Paths to Allowed Paths.

## Measured Ground Truth (2026-10-04)

A dated record. Re-derive before relying on it.

- **GHI #1175's central claim holds.** `create_dispatch_state`, `handle_task_result`, `advance_dispatch`, `handle_review_cycle`, `parse_handoff_result`, `parse_review_result`, `complete_subagent_dispatch_record`, `aggregate_dispatch_results` and `persist_dispatch_summary` have no call site under `src/gzkit`, `scripts`, `.claude/hooks` or `.gzkit/hooks` beyond their definitions and the re-exports in `src/gzkit/pipeline_runtime.py`. The Stage 3 functions `parse_verification_results`, `aggregate_verification_results` and `create_verification_dispatch_records` are the same. The callers are tests and `features/steps/subagent_pipeline_steps.py`, a wider test surface than the one file the issue names. `update_subagent_dispatch`, named in the issue's second grep, does not exist.
- **Review findings are already on the ledger.** `record_review` (`src/gzkit/acceptance_store.py`) writes an `acceptance_recorded` row for each newly imported review. The issue's "review findings exist only in the conversation" is true of the dispatch record and the aggregation, not of the findings themselves. Question 4 follows from this.
- **The fix-cycle counter has no persistence at all.** `DispatchRecord.review_fix_count` lives in `DispatchState` (`src/gzkit/pipeline_dispatch.py`), and no function serializes a `DispatchState`. Requirement 5 needs a store, not only a call.
- **The aggregation miscounts the records production writes.** `record_dispatch` writes one record per role. For one clean task with three role dispatches, `aggregate_dispatch_results` returned `total_tasks` 3, `completed` 0 and `fix_cycles` 2, because it counts repeated task ids as re-dispatches.
- **The SpecReviewer record has no agent file.** `AGENT_FILE_MAP` is keyed `Reviewer`; the mandated roster says `SpecReviewer`. `create_subagent_dispatch_record` returned an empty `agent_file` for that role.
- **A Stage 3 verification record does not load as a dispatch record.** `SubagentDispatchRecord` raised a `ValidationError` on the dict `create_verification_dispatch_records` returns.
- **Missing and malformed are one value.** `parse_handoff_result` returned `None` for no block, for unparseable JSON and for a block with an extra field.
- **The reader has nothing to read for a completed run.** `uv run gz roles --pipeline OBPI-0.35.0-14-meaning-preserving-landing --json` exited 1 with "No dispatch data found". The ledger holds 140 `stage2_dispatch_recorded` rows; the plans directory holds no dispatch summary.
- **Skill and docs describe recording that does not happen.** The skill's Stage 2 step h-v says the marker cache is refreshed "with model, timestamps, and result", and steps 5-6 and Stage 3 step 6 say state and a summary are persisted. `docs/user/concepts/subagent-pipeline.md` § Dispatch State says a summary is written on completion. `docs/user/runbook.md` says dispatch records show "timestamps, status, result" and that review findings are recorded in the dispatch state; its example also records the three roles of one task under task indices 1, 2 and 3.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: § Decision item 14, "A STAGE 2 DISPATCH'S OUTCOME IS RECORDED BY THE RUNTIME". It is quoted in full under ADR Item above.
- [ ] Parent ADR § Intent — the amendment "AMENDED 2026-10-04": what a repair assignment is, and why this ADR carries it.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] GHI #1175 in full (`gh issue view 1175`): its closure contract is the source of these requirements
- [ ] The repaired obligations: `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/obpis/OBPI-0.18.0-02-implementer-subagent-dispatch.md` and `docs/design/adr/pre-release/ADR-0.18.0-subagent-driven-pipeline-execution/obpis/OBPI-0.18.0-05-pipeline-runtime-integration.md`
- [ ] The module docstring of `src/gzkit/obpi_dispatch_channel.py`: why credit is Layer-2 evidence and never a marker key (GHI #845, #886)
- [ ] `docs/design/adr/foundation/ADR-0.0.9-state-doctrine-source-of-truth/ADR-0.0.9-state-doctrine-source-of-truth.md` Rule 5: Layer 3 artifacts cannot block gates
- [ ] `docs/governance/context-phase-review-2026-10-04-evidence/README.md` finding 4 items 1 and 2
- [ ] `docs/governance/build-to-1.0-campaign-2026-09-20.md` § Amendments 2026-10-04 (2): no control is removed
- [ ] `.gzkit/rules/security-sensitivity.md` and `data/security_surfaces.json`: the walkthrough this brief's sensitivity adds
- [ ] `docs/user/manpages/obpi-acceptance.md`: the review import that already records findings

**Prerequisites (check existence, STOP if missing):**

- [ ] The operator's rulings on Open Design Questions 1-5 are recorded in this brief's Change Log
- [ ] Required path exists: `src/gzkit/obpi_dispatch_channel.py`
- [ ] Required path exists: `src/gzkit/commands/obpi_dispatch.py`
- [ ] Required path exists: `src/gzkit/pipeline_runtime.py`
- [ ] Required path exists or is intentionally created in this OBPI: `tests/commands/test_obpi_dispatch.py`
- [ ] Required path exists or is intentionally created in this OBPI: `features/obpi_dispatch_outcome.feature`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `src/gzkit/pipeline_dispatch.py` — the three parsers' failure values, `handle_task_result`, `handle_review_cycle`, and the two in-memory models `DispatchRecord` and `DispatchState`
- [ ] `src/gzkit/pipeline_runtime.py` — `SubagentDispatchRecord`, `complete_subagent_dispatch_record`, `persist_dispatch_state`, `load_dispatch_state`, `aggregate_dispatch_results`, `persist_dispatch_summary`, `AGENT_FILE_MAP`
- [ ] `src/gzkit/obpi_dispatch_channel.py` — `record_dispatch` write order, `dispatch_channel`, `MANDATED_STAGE2_ROLES`
- [ ] `src/gzkit/pipeline_verification.py` — `parse_verification_results`, `create_verification_dispatch_records`
- [ ] `src/gzkit/commands/obpi_dispatch.py` and `src/gzkit/cli/parser_obpi.py` — the three invocation forms and exit codes
- [ ] `src/gzkit/commands/roles.py` — active marker first, summary second, exit 1 when neither
- [ ] `src/gzkit/roles.py` — `HandoffResult`, `ReviewResult`, both `frozen=True` and `extra="forbid"`
- [ ] `src/gzkit/acceptance_store.py` — `record_review` and `load_history`
- [ ] `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — Stage 2 Subagent Dispatch Mode steps e to h and 5 to 6, and Stage 3 Phase 2 steps 6 to 7
- [ ] `tests/test_obpi_dispatch_channel.py`, `tests/test_pipeline_integration.py` and `features/subagent_pipeline.feature` — fixture conventions, and the tests that pin today's fix-cycle counting

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
- [ ] `docs/user/manpages/obpi-dispatch.md` documents the outcome-recording surface, its exit codes, and that a recorded outcome grants no credit
- [ ] `docs/user/manpages/roles.md` documents the pipeline view's outcome, fix-cycle and aggregation fields
- [ ] `docs/user/concepts/subagent-pipeline.md` and `docs/user/runbook.md` state what is recorded, by what, and where it is read
- [ ] `uv run gz cli audit` exits 0

### Gate 4: BDD (Heavy only)

- [ ] `features/obpi_dispatch_outcome.feature` runs the real command in one process and the reader in another, with scenarios tagged for REQ-0.35.0-18-01, -02, -04 and -07
- [ ] Acceptance scenarios pass: `uv run -m behave features/obpi_dispatch_outcome.feature features/subagent_pipeline.feature`

### Gate 5: Human

- [ ] Human attestation recorded, after the security-sensitivity walkthrough

## Verification

```bash
uv run -m unittest tests.test_obpi_dispatch_channel tests.test_pipeline_integration tests.test_pipeline_dispatch tests.test_review_protocol tests.test_verification_dispatch tests.test_roles_cli tests.commands.test_obpi_dispatch
uv run -m behave features/obpi_dispatch_outcome.feature features/subagent_pipeline.feature
uv run gz validate --documents --req-kind-discipline --cli-alignment
uv run gz cli audit
uv run gz skill audit
uv run mkdocs build --strict
uv run gz check
```

## Demo

The yielded product is a real run's outcome read back by a process that did not record it (Requirement 14). The commands name this OBPI because its own Stage 2 can be that run once the surface exists; the plan may name another real run instead. Both commands are read-only, and each exits 1 when there is nothing to show. Pipeline markers are tracked files, so the disposable Demo copy carries them. The outcome is recorded by a form of `gz obpi dispatch` (Question 2, ruled); its invocation joins this section when the plan has settled the flag.

```bash
uv run gz obpi dispatch OBPI-0.35.0-18-dispatch-outcome-recording
uv run gz roles --pipeline OBPI-0.35.0-18-dispatch-outcome-recording --json
```

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-18-01 [BEHAVIOR]: Given an active pipeline with a recorded Implementer dispatch for a task, when the runtime is given that subagent's returned text containing a valid result block, then the dispatch's record on disk carries a completion time and the block's `status`, `files_changed`, `tests_added` and `concerns` as the runtime parsed them, and a process that did not record it reads those values through `gz roles --pipeline` with `--json`
- [ ] REQ-0.35.0-18-02 [BEHAVIOR]: Given returned text with no result block, unparseable JSON, an unknown status or a field outside the contract, when the runtime records it, then the dispatch's outcome names the block missing or invalid, is not `done`, `done_with_concerns` or `PASS`, and is not counted as completed; and a dispatch with no outcome recorded reads as unrecorded, never as success
- [ ] REQ-0.35.0-18-03 [BEHAVIOR]: Given recorded SpecReviewer and QualityReviewer dispatches for a task, when each reviewer's outcome is recorded, then each record carries the verdict, the findings with severities, the verification gaps and its role's agent file; a reviewer output that yields no valid result is recorded as invalid, never as `PASS`; and the recorded outcome never disagrees on verdict or findings with the review the acceptance store holds for the same receipt
- [ ] REQ-0.35.0-18-04 [BEHAVIOR]: Given a task whose review blocked advancement and whose Implementer was re-dispatched N times, when a process holding none of the earlier process's state reads the run, then it reports N fix cycles for that task and whether N has reached `MAX_REVIEW_FIX_CYCLES`; and a task with one dispatch per mandated role and no blocking review reports zero
- [ ] REQ-0.35.0-18-05 [BEHAVIOR]: Given a run with recorded outcomes, when a fresh process asks for the run's aggregation, then it returns total tasks, completed, blocked, fix cycles, review findings by severity and model usage per role computed from those outcomes, with total tasks counting tasks; and the same query answers for a completed run whose active marker has been removed
- [ ] REQ-0.35.0-18-06 [BEHAVIOR]: Given a Stage 3 verification dispatch asked to verify a set of requirements, when the runtime records its returned text, then each expected requirement carries its parsed outcome, an expected requirement with no parsed result is recorded as having none and never as `PASS`, and the reader returns these records beside the Stage 2 records without failing on either kind
- [ ] REQ-0.35.0-18-07 [BEHAVIOR]: Given any outcome records, including a failing one, one for a role with no dispatch event and one hand-written into the marker, when the dispatch channel and the Stage 5 dispatch verdict are computed, then each role is credited only from its `stage2_dispatch_recorded` ledger events and the verdict equals the verdict for the same ledger with no outcome records
- [ ] REQ-0.35.0-18-08 [BEHAVIOR]: Given a run with a `stage2_single_driver_declared` event, when the dispatch command renders the channel and the Stage 5 dispatch verdict is computed, then the exit codes, the rendering and the verdict are the same as before this OBPI and no outcome is demanded
- [ ] REQ-0.35.0-18-09 [SUPPORT]: The pipeline skill's Stage 2 Subagent Dispatch Mode and Stage 3 Phase 2 instruct the orchestrator to hand each subagent's returned text to the runtime, in place of parsing results and counting fix cycles in the conversation, and still state every control Requirement 11 lists. Witnessed by `artifact_edited` citing `.gzkit/skills/gz-obpi-pipeline/SKILL.md` + `gz validate --cli-alignment`.
- [ ] REQ-0.35.0-18-10 [SUPPORT]: The dispatch manpage documents the outcome-recording surface, its exit codes, the missing-or-invalid outcome, and that a recorded outcome is the subagent's report and grants no credit; the roles manpage, the concept doc and the runbook describe the same behaviour. Witnessed by `artifact_edited` citing `docs/user/manpages/obpi-dispatch.md` + `gz validate --cli-alignment`.

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

- 2026-10-04 — Open Design Question 1 ruled before the plan. Operator, verbatim: "A", to the option that is C in this brief's lettering. A ledger event is the record of a dispatch's outcome; the marker and the completion summary are caches rebuilt from it. The ledger-event paths stay in Allowed Paths, and Requirement 15 is added.
- 2026-10-04 — Open Design Question 2 ruled before the plan. Operator, verbatim: "A". `gz obpi dispatch` gains the outcome-recording form and no subcommand is added. Allowed Paths are unchanged.
- 2026-10-04 — Open Design Question 3 settled by canon, not by a new ruling: `.gzkit/rules/model-selection.md` operative claim 5. A recorded outcome is the subagent's report, labelled as reported and read by no gate.
- 2026-10-04 — Open Design Question 4 ruled before the plan. Operator, verbatim: "A". A reviewer's dispatch outcome is derived from the acceptance store's review for the same receipt; Requirements 1 and 2 are amended to say so. Allowed Paths are unchanged. Question 5 is open.

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
