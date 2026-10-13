## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

OBPI-0.35.0-15-pipeline-run-position. Parent ADR-0.35.0-canon-entry-corpus-landing, checklist item 15. Lane Heavy, sensitivity security. Repair assignment against ADR-0.13.0 (GHI #1172). Observed 2026-10-13 UTC on HEAD `87aa2613e`; code and tests are identical to `ba7e20341`.

**1. Value Narrative**

Before this OBPI a pipeline marker recorded the stage the launch named. A run launched in full read `implement` for its whole life, so a new session's orientation could not say where the run was.

Now each ruled boundary appends one `pipeline_stage_transition` event to the ledger and then advances both marker files. The marker carries the stage reached and a `position` (kind, label, boundary), `gz state --repair` rebuilds a deleted marker from the ledger, and the session orientation shows the stage reached and the position inside it.

This is claimed for boundaries the recorder records for the run its own rule names. Which ids name which run after a rename, beside a second OBPI under the same semver and item, or after a retirement is not asserted (limits 1 and 3 below).

**2. Key Proof**

A. This OBPI's own run, launched in full (entry `full`, launch stage `implement`), read by a new process after the run crossed `gz obpi present-evidence`. Requirement 15 of the brief asks for this capture. The requirement it shows is REQ-0.35.0-15-06, executed proof `proof-ea77aca538b24c87a6c1b7bf9e16ee3f`.

```console
$ uv run python scripts/session_orientation.py
...
## Active ADR pipeline state
- OBPI-0.35.0-15-pipeline-run-position (ADR-0.35.0-canon-entry-corpus-landing) — stage: ceremony
  - Position inside the stage: round `present-evidence`, marked by `gz obpi present-evidence`
...
```

This is a capture of a run that is still moving. The position line names the last boundary recorded, so it reproduces only until the run crosses another one. `gz obpi verify-packet` records its own position after its replay, and an adversarial review import records another.

B. The orientation section and the rebuild of a deleted marker, by test (REQ-0.35.0-15-06 and REQ-0.35.0-15-03, executed proof `proof-6705a688eb384821a8e280ab0ac0d7e9` for the latter). 10 tests, OK. The `Ran 10 tests` line carries a duration and is elided.

```console
$ uv run -m unittest tests.test_pipeline_position.TestPipelineSectionShowsWhereARunIs tests.adr.test_state_doctrine.TestRepairRebuildsADeletedMarker -v
test_a_launch_with_nothing_after_it_shows_its_stage_and_claims_no_position (tests.test_pipeline_position.TestPipelineSectionShowsWhereARunIs.test_a_launch_with_nothing_after_it_shows_its_stage_and_claims_no_position)
No boundary crossed is no position: the section invents none (Requirement 4). ... ok
test_a_position_the_marker_does_not_hold_whole_is_reported_as_none (tests.test_pipeline_position.TestPipelineSectionShowsWhereARunIs.test_a_position_the_marker_does_not_hold_whole_is_reported_as_none)
A marker is a cache anyone can write: a part of a position is no position. ... ok
test_an_advanced_run_reports_the_stage_reached_and_its_position (tests.test_pipeline_position.TestPipelineSectionShowsWhereARunIs.test_an_advanced_run_reports_the_stage_reached_and_its_position) ... ok
test_the_section_shows_the_stage_reached_and_its_position (tests.test_pipeline_position.TestPipelineSectionShowsWhereARunIs.test_the_section_shows_the_stage_reached_and_its_position)
The launch stage never stands in for the stage reached or the position. ... ok
test_a_deleted_marker_is_rebuilt_to_the_stage_and_position_it_held (tests.adr.test_state_doctrine.TestRepairRebuildsADeletedMarker.test_a_deleted_marker_is_rebuilt_to_the_stage_and_position_it_held)
Same stage, same position, a launch's nonce, the last crossing's time. ... ok
test_a_launch_with_nothing_after_it_rebuilds_to_its_launch_values (tests.adr.test_state_doctrine.TestRepairRebuildsADeletedMarker.test_a_launch_with_nothing_after_it_rebuilds_to_its_launch_values) ... ok
test_a_relaunched_run_is_rebuilt_from_its_latest_launch (tests.adr.test_state_doctrine.TestRepairRebuildsADeletedMarker.test_a_relaunched_run_is_rebuilt_from_its_latest_launch)
The run is the latest launch: its nonce, its entry, the crossings after it. ... ok
test_the_dispatch_caches_are_not_rebuilt_and_credit_still_reads_the_ledger (tests.adr.test_state_doctrine.TestRepairRebuildsADeletedMarker.test_the_dispatch_caches_are_not_rebuilt_and_credit_still_reads_the_ledger)
``dispatch_state`` and the single-driver declaration are caches (GHI #886). ... ok
test_the_rebuilt_time_is_the_last_crossing_and_not_the_rebuild (tests.adr.test_state_doctrine.TestRepairRebuildsADeletedMarker.test_the_rebuilt_time_is_the_last_crossing_and_not_the_rebuild) ... ok
test_the_receipt_state_is_read_back_from_the_receipt_file (tests.adr.test_state_doctrine.TestRepairRebuildsADeletedMarker.test_the_receipt_state_is_read_back_from_the_receipt_file) ... ok
...
OK
```

C. The acceptance feature, which is the brief's Demo. The duration line is left out.

```console
$ uv run -m behave features/pipeline_run_position.feature
...
1 feature passed, 0 failed, 0 skipped
40 scenarios passed, 0 failed, 0 skipped
270 steps passed, 0 failed, 0 skipped
```

D. Requirement coverage. The two uncovered requirements are the two SUPPORT requirements, which carry no `@covers` test by their proof channel.

```console
$ uv run gz covers OBPI-0.35.0-15-pipeline-run-position --json
...
  "summary": {
    "identifier": "OBPI-0.35.0-15-pipeline-run-position",
    "total_reqs": 9,
    "covered_reqs": 7,
    "uncovered_reqs": 2,
    "coverage_percent": 77.8,
    "behavior_uncovered_reqs": 0,
    "grandfathered_reqs": 0
  }
```

**3. Evidence**

**Quality checks:**

All run in this session on the reviewed tree. Full invocations are in the block under the table.

| Check | Command | Result |
|-------|---------|--------|
| Tests (full suite) | `arb:unittest` | 11772 tests, OK, 4 skipped, exit 0 — `arb-step-unittest-4c66fba2a5634fdda9ed4d5fb80186d0` |
| Lint | `arb:ruff` | exit 0 — `arb-ruff-e58e877fec34403e9cdcadcc6ac1be2d` |
| Typecheck | `arb:typecheck` | exit 0 — `arb-step-typecheck-8de481c0b00641fdb8dc499484fb24f2` |
| Docs | `arb:mkdocs` | exit 0 — `arb-step-mkdocs-99e9aa2578ef404d98efb8dafb26b8d7` |
| Behave | `arb:behave` | 40 scenarios passed, 0 failed, exit 0 — `arb-step-behave-725360f5030146b6af03e5f4b6ff19fd` |
| OBPI tests 1 | `arb:obpi-a` | 195 tests OK — `arb-step-unittestobpia-392d73754c524d1cbfd04d90f37139b8` |
| OBPI tests 2 | `arb:obpi-b` | 163 tests OK — `arb-step-unittestobpib-21e0d2b8506b4ba4816ea94eb4b4ab4a` |
| OBPI tests 3 | `arb:obpi-c` | 85 tests OK — `arb-step-unittestobpic-6c9e467cc1444ab8a2abe6d211486176` |
| Validators | `validate` | exit 0, 3 scopes; no receipt |
| CLI audit | `cli-audit` | exit 0; no receipt |
| REQ coverage | `covers` | 9 REQs; 7 covered; 2 uncovered (both SUPPORT); 0 BEHAVIOR uncovered |
| RED witness | `arb:red`, seven times | each exit 0 and INCONCLUSIVE (limit 5) |
| Evidence packet input | `present-evidence` | after 4b round 2: exit 0; attestable true; no blocker; both Demo commands exit 0 |
| Stage 2 acceptance | `acceptance:stage2` | exit 0; ready true; no blocker; no open finding |
| Pre-push gate | `gz check` | Passed on `ba7e20341` and on `87aa2613e`; no receipt |

```bash
# arb:unittest — full unit suite
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer

# arb:ruff — lint
uv run gz arb ruff

# arb:typecheck — static type check
uv run gz arb typecheck

# arb:mkdocs — docs build
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict

# arb:behave — the acceptance feature
uv run gz arb step --name behave -- uv run -m behave features/pipeline_run_position.feature

# arb:obpi-a — OBPI-scoped tests 1
uv run gz arb step --name unittestobpia -- uv run -m unittest tests.test_pipeline_position tests.commands.test_obpi_pipeline tests.test_pipeline_runtime

# arb:obpi-b — OBPI-scoped tests 2
uv run gz arb step --name unittestobpib -- uv run -m unittest tests.test_obpi_dispatch_channel tests.scripts.test_session_orientation tests.test_pipeline_stage_fence

# arb:obpi-c — OBPI-scoped tests 3
uv run gz arb step --name unittestobpic -- uv run -m unittest tests.test_schemas tests.adr.test_state_doctrine

# validate — three validator scopes
uv run gz validate --documents --req-kind-discipline --cli-alignment

# cli-audit
uv run gz cli audit

# covers — REQ coverage (also Key Proof D)
uv run gz covers OBPI-0.35.0-15-pipeline-run-position --json

# arb:red — once per BEHAVIOR requirement, REQ-0.35.0-15-01 to -07
uv run gz arb red --req <REQ> --obpi OBPI-0.35.0-15-pipeline-run-position

# present-evidence — Step 4a review input
uv run gz obpi present-evidence OBPI-0.35.0-15-pipeline-run-position --json

# acceptance:stage2
uv run gz obpi acceptance OBPI-0.35.0-15-pipeline-run-position status --stage stage2

# gz check — run by the pre-push hook
uv run gz check
```

No security-scan receipt exists or can be produced. The brief is `sensitivity: security` because its Allowed Paths overlap registered security surfaces (`src/gzkit/pipeline_markers.py`, `src/gzkit/commands/obpi_cmd.py`, `src/gzkit/commands/obpi_complete.py`, `src/gzkit/ledger_events.py`, `src/gzkit/ledger.py`). The canonical security-scan slot in `CANONICAL_STEP_COMMANDS` (`src/gzkit/canonical_steps.py`) is empty, so `gz obpi complete` exits 3 for this brief unless the operator approves `--accept-security-floor` with a reason (GHI #462). OBPI-0.35.0-06 completed that way. That approval is the operator's and has not been asked for or given.

**Files created:**

From the 32 commits of this run whose subject ends "(OBPI-0.35.0-15)", first `4091cfa1b` on 2026-10-11, last `87aa2613e`. 44 paths: 5 created, 39 modified.

- `src/gzkit/pipeline_position.py` (position model, ledger replay, recorder, rebuild payload)
- `tests/test_pipeline_position.py` (unit tests)
- `features/pipeline_run_position.feature` (acceptance feature; the brief's Demo)
- `features/steps/pipeline_run_position_steps.py` (its steps)
- `.claude/plans/pipeline-run-position-OBPI-0.35.0-15.md` (the plan)

**Files modified:**

Source:

- `src/gzkit/pipeline_markers.py` (the two marker files)
- `src/gzkit/pipeline_runtime.py`
- `src/gzkit/obpi_dispatch_channel.py`
- `src/gzkit/commands/state.py` (`gz state --repair`)
- `src/gzkit/commands/task.py` (the `gz task` verbs mark a Stage 2 task boundary)
- `src/gzkit/commands/obpi_present_evidence.py` (a Stage 4 round producer)
- `src/gzkit/commands/obpi_verify_packet.py` (a Stage 4 round producer)
- `src/gzkit/commands/obpi_acceptance.py` (the Stage 4 review-import producer)
- `src/gzkit/commands/obpi_precomplete.py`
- `src/gzkit/commands/obpi_complete.py`
- `src/gzkit/commands/obpi_stages.py`
- `src/gzkit/cli/parser_governance.py` (the `--repair` help text of `gz state` only)
- `src/gzkit/schemas/ledger.json` (ledger schema; gains the stage-transition event)
- `src/gzkit/ledger_events.py`
- `src/gzkit/ledger.py`
- `src/gzkit/events.py`
- `src/gzkit/governance/trust_audits/events.py`
- `src/gzkit/ontology/corpus.py`
- `src/gzkit/canonical_history.json`
- `scripts/session_orientation.py` (the `Active ADR pipeline state` section)

Tests:

- `tests/adr/test_state_doctrine.py`
- `tests/commands/test_obpi_pipeline.py`
- `tests/test_obpi_dispatch_channel.py`
- `tests/test_pipeline_runtime.py`
- `tests/test_schemas.py`

Documents and skills:

- `docs/user/manpages/obpi-pipeline.md` (REQ-0.35.0-15-08)
- `docs/user/runbook.md` (REQ-0.35.0-15-08)
- `docs/governance/GovZero/obpi-runtime-contract.md` (REQ-0.35.0-15-09)
- `docs/governance/pipeline-marker-migration-path.md` (REQ-0.35.0-15-09)
- `docs/user/manpages/state.md` (states the rebuild)
- `docs/user/manpages/obpi-acceptance.md` (exit code of a review import whose id the resolver cannot name)
- `docs/governance/state-doctrine.md` (the repair-sequence line for `gz state --repair`)
- `.gzkit/skills/gz-state/SKILL.md` (what `--repair` writes and reports), with its mirrors `.agents/skills/gz-state/SKILL.md`, `.claude/skills/gz-state/SKILL.md` and `src/gzkit/skills/gz-state/SKILL.md`
- `docs/user/skills/gz-state.md` (docs copy of the gz-state skill)
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md` (dated note on `REQ-0.13.0-03-02`, Requirement 16)
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-15-pipeline-run-position.md` (this brief: rulings and Change Log)

**REQ coverage:**

Current executed proofs, acceptance digest `b659edd6bce1...`. "Pass" means: the proof is recorded with its baseline green and every substitution killed on an assertion, `gz covers` reports proof status pass, and both Stage 2 reviews of the group accepted it. Rows 01 to 07 have an accepted adversarial review from Step 4b round 1, and rows 08 and 09 from round 2 (limit 8).

| REQ | Kind | Mechanism | Proof location | Proof | Result |
|-----|------|-----------|----------------|-------|--------|
| REQ-0.35.0-15-01 | BEHAVIOR | stage advances at a boundary | `req-01` | 2 tests; 4 substitutions killed | Pass as read (limit 3) |
| REQ-0.35.0-15-02 | BEHAVIOR | recorder, by the id handed in | `req-02` | 61 tests; 23 substitutions killed | Pass as restated (limits 1, 2) |
| REQ-0.35.0-15-03 | BEHAVIOR | `gz state --repair` rebuild | `req-03` | 7 tests; 4 substitutions killed | Pass |
| REQ-0.35.0-15-04 | BEHAVIOR | bare launch reads as before | `req-04` | 2 tests; 3 substitutions killed | Pass |
| REQ-0.35.0-15-05 | BEHAVIOR | stale-marker handling unchanged | `req-05` | 13 tests; 4 substitutions killed | Pass (limit 6) |
| REQ-0.35.0-15-06 | BEHAVIOR | orientation section | `req-06` | 5 tests; 3 substitutions killed | Pass (limit 6) |
| REQ-0.35.0-15-07 | BEHAVIOR | readers of an advanced marker | `req-07` | 10 tests; 5 substitutions killed | Pass |
| REQ-0.35.0-15-08 | SUPPORT | pipeline manpage and runbook | `req-08` | document on disk + validator | Resolver pass; accepted in 4b round 2 as ruled (limits 7, 8) |
| REQ-0.35.0-15-09 | SUPPORT | runtime contract document | `req-09` | document on disk + validator | Resolver pass; accepted in 4b round 2 as ruled (limits 7, 8) |

```text
# req-01 — proof-e0ae47384e9246cfb62377ccda26a526
tests/test_pipeline_position.py
  TestTheMarkerReportsTheStageTheRunHasReached (2)
substitutions: 4 in src/gzkit/pipeline_position.py

# req-02 — proof-66266957ef7e4a8b88d55ceea1bae1df
tests/test_pipeline_position.py
  TestRecordPositionWritesTheLedgerThenTheMarker (3)
  TestTheRecorderFindsTheRunItself (11)
  TestEachBoundaryNamesThePositionInsideItsStage (12)
  TestABoundaryIsRecordedUnderTheIdTheLaunchCarries (12)
  TestARenameNeitherEndsARunNorHidesIt (8)
  TestAnIdNamesTheRunInFlightOrNone (5)
  TestNoCheckOrBookkeepingCommandMovesTheFence (4)
tests/test_obpi_dispatch_channel.py
  TestPrecompleteNamesTheObpiOnceAtEntry (5)
  TestADispatchRecordsTheTaskAndCreditStaysOnTheLedger (1)
substitutions: 23 in src/gzkit/pipeline_position.py

# req-03 — proof-6705a688eb384821a8e280ab0ac0d7e9
tests/adr/test_state_doctrine.py
  TestRepairRebuildsADeletedMarker (4)
  TestRepairRestoresAMarkersTwin (2)
  TestRepairRebuildsOnlyARunInFlightWhoseMarkerIsGone (1)
substitutions: 4 in src/gzkit/pipeline_position.py

# req-04 — proof-8b8594aed33244a1b28a3dfb3cd18b26
tests/test_pipeline_position.py
  TestALaunchWithNothingAfterItReportsNoPosition (2)
substitutions: 3 in src/gzkit/pipeline_markers.py

# req-05 — proof-385ae77651514dbdbc24fe5ddef361ca
tests/test_pipeline_position.py
  TestStaleMarkerHandlingIsUnchanged (4)
  TestNeitherAReadNorARebuildMovesUpdatedAt (3)
tests/adr/test_state_doctrine.py
  TestRepairDeclinesARunStaleOnArrival (3)
  TestRepairRestoresAMarkersTwin (2)
  TestRepairRebuildsOnlyARunInFlightWhoseMarkerIsGone (1)
substitutions: 4 in src/gzkit/pipeline_position.py

# req-06 — proof-ea77aca538b24c87a6c1b7bf9e16ee3f
tests/test_pipeline_position.py
  TestPipelineSectionShowsWhereARunIs (4)
  TestAMarkerRecordsAWholePositionOrNone (1)
substitutions: 3 in src/gzkit/pipeline_position.py (marker_position)

# req-07 — proof-8f6d0af219e847cba0a8f985c6b4ddcc
tests/test_pipeline_position.py
  TestAnAdvancedMarkerKeepsEveryReaderWorking (7)
tests/test_obpi_dispatch_channel.py
  TestBothMarkerFilesAgreeAfterADispatch (3)
substitutions: 5 in src/gzkit/pipeline_markers.py

# req-08 — proof-1e65995d18a64f9e8ee208e78bc68819
declared witness: artifact_edited citing docs/user/manpages/obpi-pipeline.md
no such ledger row exists; the resolver passed on the document existing
uv run gz validate --cli-alignment

# req-09 — proof-9c82af8240504d0aad726002327b0a96
declared witness: artifact_edited citing docs/governance/GovZero/obpi-runtime-contract.md
no such ledger row exists; the resolver passed on the document existing
uv run gz validate --documents
```

The classes and per-class counts are the unit tests `gz covers` binds to each requirement (the full output of Key Proof D). Their sum per requirement equals the proof's test count. The proof's own selector list is in the proof record.

Stage 2 reviews of this round. All six accepted every proof of their group. 26 findings were closed (13 on REQ-0.35.0-15-02, 1 on -05, 11 on -08, 1 on -09) and none is mapped open. The reviewers are Claude (opus), read-only: they execute nothing.

```text
group A (REQ-01, -02, -04, -07)
  arb-step-specreview-4f35e1ba0af64f0d8e5d1864a44f5378
  arb-step-qualityreview-d0f92a31a7654af688224fff4c4e0ecc
group B (REQ-03, -05)
  arb-step-specreview-0e6e7c5fe4f2481a82efb9548c51560c
  arb-step-qualityreview-f2521d837300417e8770c7ec7e34b7c5
group C (REQ-06, -08, -09)
  arb-step-specreview-3e40eb0363224b63962c3eadeb73ef1d
  arb-step-qualityreview-24b4055993364b2e874bee7258a239cc
```

History, separate from the table above: this was the sixth Stage 2 round of this session's lineage and the first with no mapped finding. The earlier rounds are indexed in the brief's Change Log by receipt.

**Limits and what is not established**

1. REQ-0.35.0-15-02 was refuted nine times in Stage 2 across two days. It was then restated by operator ruling (brief Open Design Question 26, operator verbatim: "A. Recorder's own rule (Recommended)"). It now asserts only what the recorder does with the id a command hands it: one run named, the boundary is recorded for that run; none named, nothing is recorded; several named, nothing is recorded and a warning is logged. Which ids name which run after a rename, beside a second OBPI under the same semver and item, or after a retirement is not asserted. That is a narrower claim than the brief began with. Its known gaps are tracked: GHI #1194 (the ledger's rename fold is not idempotent), GHI #1195 (no rename writer checks for a run in flight), GHI #1199 (the launcher admits a withdrawn or superseded OBPI).
2. Both group A reviews said four of the thirteen REQ-0.35.0-15-02 finding closures rest on the restatement alone. The behaviour those four findings describe is unchanged in the code.
3. Operator ruling 2026-10-13, verbatim "Ratify the reading (Recommended)": REQ-0.35.0-15-01, Requirement 1 and the Objective are read as speaking of boundaries the recorder records (Requirement 2 (f)). Read alone, the last clause of REQ-0.35.0-15-01 ("the marker never reports `implement` for a run that has left Stage 2") does not hold on the tracked naming-gap inputs. The requirement text was not changed.
4. Operator ruling 2026-10-13, verbatim "No section (Recommended)": the brief carries no Threat Model section. It asserts no tamper resistance (Requirement 12: a position is never gate evidence).
5. The RED falsifiability witness (`gz arb red`) was run for all seven BEHAVIOR requirements in this session. Every one returned INCONCLUSIVE, failure class error against a RECONSTRUCTED base tree. That is not a RED and not a finding about the tests. The witness that stands is each requirement's executed acceptance proof, whose substitutions were killed on an assertion.
6. The acceptance proof command mutates one source file per requirement. Controls for the command modules (`obpi_precomplete.py`, `obpi_present_evidence.py`, `obpi_acceptance.py`) and four stale-marker controls in `pipeline_markers.py` are in supplementary sweeps taken on earlier trees (at `dadbe852c` and `124aa85f4`). They were not re-run on this tree. The control for REQ-0.35.0-15-06 on the orientation script itself was not re-run.
7. REQ-0.35.0-15-08 and -09 are SUPPORT requirements. Each names as its witness an `artifact_edited` ledger row citing its document, plus a validator scope. No such row exists for either document, and none can: the edit-recording hooks record that event only for ADR, OBPI and PRD documents, `AGENTS.md` and `CLAUDE.md`. The recorded proof is the resolver `resolve_support_proof` returning pass on the document existing on disk and its validator passing (GHI #647 arm). An earlier version of this packet, and the evidence handed to the Stage 2 reviewers, called that "an edit record plus a validator". That was wrong, and the two group C reviews accepted these proofs under it. That the documents say what the requirements demand rests on those two reviews by reading and on the Codex adversary's reading (limit 8). The class is filed as GHI #1202.
8. Step 4b, round 1 (Codex, tier 1, receipt `arb-step-codexadversary-1724336063044e33bb799eef0d714298`, about 15 minutes, in a disposable writable copy): verdict NOT-CORROBORATED. It accepted the seven BEHAVIOR proofs after replaying two substitutions of each (14 replays: baseline green, the named test failing on its own assertion, source restored, green again) and after its own end-to-end script of launch, record, read from another process, delete and repair. It corroborated the document content of REQ-0.35.0-15-08 and -09 and refused their proofs on `fin-4b1-REQ08-missing-cited-edit-event` and `fin-4b1-REQ09-missing-cited-edit-event`: the declared `artifact_edited` witness does not exist (limit 7). The run was blocked and the operator ruled, verbatim "A. Rule on the reading (Recommended)": the witness is satisfied as the resolver defines it, the document on disk plus its validator; no brief text changes. What Codex said it did not confirm: the full unit suite, lint, typecheck, docs build and `gz check` (it read their receipts, which record a dirty tree); every recorded substitution (it replayed two per requirement); an unmocked end-to-end completion; real git hooks. Step 4b, round 2, a focused follow-up on the two findings only (Codex, tier 1, receipt `arb-step-codexadversary-f306181059844d2fbfd942ed4d088a50`, about 9 minutes): CORROBORATED-WITH-CAVEATS. It closed both findings and approved both proofs "under the operator's recorded reading: document on disk plus its validator", and said the closure "rests on that reading, not on an edit event appearing". Its weakest point, verbatim: "The unchanged clauses still literally name absent edit events. These closures depend on the explicit, unit-specific operator interpretation, alongside independently checked document content and validators. The general resolver defect remains open." It could not confirm this packet's replay verdict, because the ledger row for a replay records no verdict. `gz obpi acceptance ... status --stage stage4` now reads ready, with no blocker and no open finding.
9. Reviewer observations that are unmapped and not repaired are listed in the brief's Change Log entry "the round after fix cycle 9". Among them: the module docstring and the `_launches_in_flight` docstring in `src/gzkit/pipeline_position.py` say the recorder reads that function, and it does not; the Failure Modes section of `docs/user/manpages/obpi-pipeline.md` lists two blockers the launcher does not run and omits two it does.
10. `gz obpi precomplete`, run after Step 4b round 2, passes eleven of twelve checks and fails one: task-envelope coherence, Signature (b). Every requirement has only its first TASK (`seq=01`) and the brief declares no `req_atomic` exemption. The labour of REQ-0.35.0-15-02 and REQ-0.35.0-15-08 was plainly more than one unit (nine fix cycles) and was never subdivided when it happened. Completion is refused until that is remedied; the remedy is put to the operator with this packet.
11. The lock on this OBPI is held by the previous session's identity (`claude-code-326a9a3f`, claimed 2026-10-12T23:00Z, 24-hour TTL). This session could not claim it and worked under it.

**4. Awaiting attestation.** Step 4b ran twice (limit 8) and the Stage 4 acceptance status reads ready. Two completion preconditions need the operator's word: the security-floor override (under the quality table) and the task subdivision (limit 10). Do NOT proceed to Stage 5 until the human responds.
