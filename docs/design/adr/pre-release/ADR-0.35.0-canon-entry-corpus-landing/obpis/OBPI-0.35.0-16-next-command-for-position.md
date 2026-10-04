---
id: OBPI-0.35.0-16-next-command-for-position
parent: ADR-0.35.0-canon-entry-corpus-landing
item: 16
lane: Heavy
sensitivity: security
status: Draft
allowlist:
  - src/gzkit/pipeline_markers.py
  - src/gzkit/pipeline_next_command.py
  - src/gzkit/pipeline_runtime.py
  - src/gzkit/commands/obpi_stages.py
  - src/gzkit/commands/status.py
  - scripts/session_orientation.py
  - tests/test_pipeline_next_command.py
  - tests/test_pipeline_runtime.py
  - tests/commands/test_obpi_pipeline.py
  - tests/commands/test_status.py
  - tests/scripts/test_session_orientation.py
  - features/obpi_pipeline_next_command.feature
  - features/steps/obpi_pipeline_next_command_steps.py
  - docs/user/manpages/obpi-pipeline.md
  - docs/user/manpages/obpi-status.md
  - docs/user/runbook.md
  - docs/governance/GovZero/obpi-runtime-contract.md
  - .gzkit/skills/gz-obpi-pipeline/SKILL.md
  - src/gzkit/skills/gz-obpi-pipeline/SKILL.md
  - .claude/skills/gz-obpi-pipeline/SKILL.md
  - .agents/skills/gz-obpi-pipeline/SKILL.md
  - docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md
  - docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-16-next-command-for-position.md
reqs:
  - REQ-0.35.0-16-01
  - REQ-0.35.0-16-02
  - REQ-0.35.0-16-03
  - REQ-0.35.0-16-04
  - REQ-0.35.0-16-05
  - REQ-0.35.0-16-06
  - REQ-0.35.0-16-07
verification:
  - uv run -m unittest tests.test_pipeline_next_command tests.test_pipeline_runtime tests.commands.test_obpi_pipeline tests.commands.test_status tests.scripts.test_session_orientation tests.test_hooks
  - uv run -m behave features/obpi_pipeline_next_command.feature
  - uv run gz validate --documents --req-kind-discipline --cli-alignment --behave-req-tags
  - uv run gz cli audit
  - uv run gz skill audit
  - uv run mkdocs build --strict
---

# OBPI-0.35.0-16-next-command-for-position: Next Command For Position

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`
- **Checklist Item:** #16 - "Next command for the run's position -- at every boundary the runtime states the one next command for where the run is, or the blocker when there is none. Repair assignment against `ADR-0.13.0` (GHI #1173, amendment 2026-10-04)"
- **Decision Item:** § Decision item 12, verbatim - "THE RUNTIME STATES THE NEXT COMMAND FOR WHERE THE RUN IS (operator-ruled 2026-10-04, GHI #1173; repair assignment). At every boundary a run crosses, the runtime states the one next command for that position; a blocked position states its blocker and no next command. Obligation repaired: `ADR-0.13.0` § Decision, "Expose structured stage outputs for current stage, blockers, required human action, and next command or resume point". The rule against stopping between stages keeps its purpose and gains this as its mechanism. Depends on item 11."

Decision item 11 is checklist item 15, `OBPI-0.35.0-15-pipeline-run-position`. That brief supplies the run's position; this one reads it.

**Status:** Draft

## Objective

For every position a pipeline run can be at, the runtime states the one next command the `gz-obpi-pipeline` skill prescribes for that position, or the blocker and no command when the position is blocked. A process that holds only the repository can obtain it for an in-flight run, and the skill's rule against stopping between stages cites it as the mechanism that carries a run across a boundary.

This is a repair assignment (parent ADR § Intent, amendment 2026-10-04). The obligation repaired is `ADR-0.13.0` § Decision, "Expose structured stage outputs for current stage, blockers, required human action, and next command or resume point", as `OBPI-0.13.0-03-structured-stage-outputs` specified it. The shipped surface computes the next command from the `--from` argument of the launch, so the value states how the run was launched and not where the run is (GHI #1173). `ADR-0.13.0` is `Validated` and is not reopened. Its requirements keep their identities; the criteria below are this brief's local acceptance criteria.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

The contract that changes is what the pipeline states as the next command: the documented marker field `next_command`, and the text that the pipeline commands, the completion reminder and the session orientation print. By the ruling on Open Design Question 1 it is also the output of `gz obpi status`, human and `--json`, which gains the run's next command.

**Sensitivity: security, declared as the floor.** `src/gzkit/pipeline_markers.py` is a registered surface in `data/security_surfaces.json`, and the function this brief repairs lives in it. `.gzkit/rules/security-sensitivity.md` § `gz validate --sensitivity` requires the declaration for any overlap. The overlap is incidental: stating a next command spawns no subprocess and decides no attestation. The heightened Gate 5 walkthrough of that rule applies.

## Allowed Paths

- `src/gzkit/pipeline_markers.py` — `pipeline_stage_output`, `pipeline_marker_payload`, `refresh_pipeline_markers`, `pipeline_resume_command` and `pipeline_completion_reminder_message`: the functions that compute and present the next command today
- `src/gzkit/pipeline_next_command.py` — **CREATE**, beside `src/gzkit/pipeline_stage_fence.py`; a pure module (stdlib + Pydantic) for the position-to-command table, if the plan places the table outside `pipeline_markers.py`, which is already past the module size guidance of `.gzkit/rules/pythonic.md`
- `src/gzkit/pipeline_runtime.py` — the re-export block for `pipeline_markers` symbols; a new public symbol is re-exported here
- `src/gzkit/commands/obpi_stages.py` — the closing lines each stage runner prints (`_print_pipeline_implementation_next_steps`, the verify-failure blockers, the ceremony guidance)
- `src/gzkit/commands/status.py` — `obpi_status_cmd` and what it renders: the read-only query a fresh process asks (Open Design Question 1, ruled)
- `scripts/session_orientation.py` — `collect_adr_pipeline` and its rendering: the fresh session's reading of an in-flight run
- `tests/test_pipeline_next_command.py` — **CREATE**, following `tests/test_pipeline_stage_fence.py`; holds the table-driven test over positions
- `tests/test_pipeline_runtime.py` — the existing tests of `pipeline_resume_command` and the completion reminder
- `tests/commands/test_obpi_pipeline.py` — command-level tests through the launch. Its existing assertions of the values `REQ-0.13.0-03-01`, `-02` and `-04` attest change only under the ruling on Open Design Question 2
- `tests/commands/test_status.py` — the `gz obpi status` output, human and `--json`
- `tests/scripts/test_session_orientation.py` — the orientation's reading of markers
- `features/obpi_pipeline_next_command.feature` — **CREATE**, following `features/obpi_lock.feature`
- `features/steps/obpi_pipeline_next_command_steps.py` — **CREATE**, following `features/steps/obpi_lock_steps.py`
- `docs/user/manpages/obpi-pipeline.md` — § Runtime Behavior: the command contract bullets and the `next_command` and `resume_point` definitions
- `docs/user/manpages/obpi-status.md` — the next-command lines of the human output and the `--json` field
- `docs/user/runbook.md` — § Step 2: Execute the OBPI through the staged pipeline
- `docs/governance/GovZero/obpi-runtime-contract.md` — § Active Pipeline Marker Fields: the `blockers`, `next_command` and `resume_point` definitions
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` — § The Iron Law only, plus the `skill-version` and `last_reviewed` frontmatter that every skill edit moves
- `src/gzkit/skills/gz-obpi-pipeline/SKILL.md`, `.claude/skills/gz-obpi-pipeline/SKILL.md`, `.agents/skills/gz-obpi-pipeline/SKILL.md` — generated mirrors, written only by `uv run gz agent sync control-surfaces`, never hand-edited
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md` — the dated amendment notes on the `REQ-0.13.0-03-01` and `REQ-0.13.0-03-04` lines only (Requirement 16); nothing else in this sealed brief changes
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-16-next-command-for-position.md`

## Denied Paths

- `src/gzkit/commands/obpi_cmd.py`, `src/gzkit/cli/parser_obpi.py` — no option or subcommand is added. The query is the existing `gz obpi status` (Open Design Question 1, ruled), and `gz obpi pipeline` gains nothing. `obpi_cmd.py` is also a registered security surface
- The recording of the run's position — the writes that advance the marker, and any ledger event for a stage transition. `OBPI-0.35.0-15-pipeline-run-position` owns them. This brief reads the position and never writes or defines it
- `src/gzkit/ledger_events.py`, `src/gzkit/schemas/ledger.json` — no ledger event is added. A stated next command is a Layer-3 statement
- `src/gzkit/obpi_lifecycle.py` and every gate, guard and completion check — none reads the stated next command (`ADR-0.0.9` Rule 5, quoted in `obpi_lifecycle.py`)
- `src/gzkit/hooks/scripts/pipeline.py`, `.claude/hooks/**` — the reminder hook calls the runtime function and is not edited
- Every section of `.gzkit/skills/gz-obpi-pipeline/SKILL.md` other than § The Iron Law — the stage procedure text is `OBPI-0.35.0-17-stage-procedure-served-by-runtime`'s subject
- `src/gzkit/pipeline_dispatch.py` — dispatch outcome recording is `OBPI-0.35.0-18-dispatch-outcome-recording`'s subject
- `src/gzkit/lock_manager.py` — lock continuity is `OBPI-0.35.0-19-lock-continuity-across-sessions`'s subject
- `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/**` — `Validated`, not reopened. The one exception is the requirement-line notes named in Allowed Paths (operator ruling 2026-10-04)
- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This brief repairs `ADR-0.13.0` § Decision, "Expose structured stage outputs for current stage, blockers, required human action, and next command or resume point", as specified by `OBPI-0.13.0-03` Requirements 3 to 6 and attested as `REQ-0.13.0-03-01` to `REQ-0.13.0-03-04`. It neither restates nor owns those requirements. Its own criteria are `REQ-0.35.0-16-01` to `REQ-0.35.0-16-07`.
2. REQUIREMENT: The stated next command is a function of the run's recorded position, never of the launch entry. The position is the one `OBPI-0.35.0-15` records. If that position cannot be read, there is nothing to derive from: STOP.
3. REQUIREMENT: The oracle for the command at each position is `.gzkit/skills/gz-obpi-pipeline/SKILL.md`: the first command the skill prescribes after the run reaches that position. A step the skill prescribes there is never skipped by stating a later stage's entry command in its place. The skill governs every row, including the three where the runtime has a composite command today (operator ruling 2026-10-04, Open Design Question 3); the `--from` entry points stay as compatibility entry points for partial re-runs and are not the stated next command inside a full run.
4. REQUIREMENT: The expected values of the table-driven test are transcribed from the skill, one row per position, each row citing the skill section it transcribes. They are never produced by calling the code under test (`AGENTS.md` § DO IT RIGHT item 6). The Change Log records the `skill-version` the table was transcribed from.
5. REQUIREMENT: Every position the run can record has exactly one outcome: one next command, or its blockers and no next command. A position the table does not know fails the test, and at runtime it states no command and names the unknown position. There is no default command.
6. REQUIREMENT: At a blocked position every consumer states each blocker and states no next command. Two blocks are in scope: a failed verification command, and an `obpi_blocked_on_operator` event standing in the ledger for the OBPI (the skill's second legitimate stop, GHI #887). The point to resume from after a blocker clears is never presented or returned as the next command.
7. REQUIREMENT: At the Stage 4 awaiting-attestation position the runtime states the required human action on every lane and kind (`ADR-0.0.36`). Every consumer that states a command at that position states the human action with it.
8. REQUIREMENT: A process holding only the repository can obtain the next command of an in-flight run. That read changes no marker field and appends no ledger event.
9. NEVER: The stated next command is never gate evidence. No gate, hook refusal or completion check reads it (`ADR-0.0.9` Rule 5; the marker is Layer 3).
10. NEVER: Remove or weaken a pipeline control (campaign § Amendments 2026-10-04 (2): "none is removed by this entry"). The `--from` entry points, the Stage 4 human-attestation pause, Step 4b, the Stage 4 round bound, `gz obpi precomplete` and the stale-marker handling all stand.
11. REQUIREMENT (operator ruling 2026-10-04, Open Design Question 1): each command that moves a run across a boundary ends its output with the next command, and the read-only `gz obpi status` states the run's next command, or its blockers, in its human and `--json` output. No CLI option, subcommand or second state file is added. The Heavy-lane obligations of the changed `gz obpi status` output (the manpage, a BDD scenario, `gz cli audit` clean) are part of this brief.
12. NEVER: Change a value an attested `REQ-0.13.0-*` literally asserts, or an assertion of its covering test, beyond what Open Design Question 2 rules. Ruled 2026-10-04 (A): the `next_command` value of `REQ-0.13.0-03-01` and the command clause of `REQ-0.13.0-03-04` change and are carried by Requirement 16. The human-action clause of `REQ-0.13.0-03-04`, all of `REQ-0.13.0-03-03`, and the other fields `REQ-0.13.0-03-01` names stand as attested. `ADR-0.13.0` is terminal, so `AGENTS.md` § OBPI Acceptance Protocol makes any further change an operator escalation, not an edit.
13. ALWAYS: Edit the skill in `.gzkit/skills/` and in § The Iron Law only. The edit keeps the completion statement, the no-summary rule, the Stage 4 pause after Step 4b and the round-bound stop. It does not grow the body past its ceiling in `src/gzkit/skill_body_grandfather.json` (`.gzkit/rules/skill-authoring.md` § Parsimony item 6). It moves `skill-version` and `last_reviewed`, and `uv run gz agent sync control-surfaces` writes the mirrors.
14. ALWAYS: Keep existing marker consumers working, including a marker written before `OBPI-0.35.0-15` that carries no recorded position. Such a marker reads as its launch position.
15. ALWAYS: Take the Key Proof from one real pipeline run, not from a fixture: the stated next command observed at two or more positions of that run, and a fresh process obtaining it (GHI #1173 exit condition). This OBPI's own run qualifies from the stage at which the repair is in the tree.
16. ALWAYS (operator ruling 2026-10-04, Open Design Question 2): amend `REQ-0.13.0-03-01` and `REQ-0.13.0-03-04` in place in the same change that makes `next_command` position-derived. Each line in the sealed `OBPI-0.13.0-03` brief keeps the attested text and gains a dated note that quotes the ruling, says `next_command` is the command the pipeline skill prescribes at the run's recorded position, and names which attested clauses still stand. The form is the note on `REQ-0.0.14-03-07` (`docs/governance/attested-req-subject-retirement.md` § Worked example 4). Each covering test asserts the amended behaviour and its docstring records why. `REQ-0.13.0-03-02` is amended by OBPI-0.35.0-15 and its note already holds under this ruling.
17. ALWAYS (operator ruling 2026-10-04): the `@covers` binding for `REQ-0.13.0-03-01` moves off the resume-command fallback test it sits on today and onto the test that asserts the requirement. The move and its reason are recorded in the test's docstring and the commit body. The binding for `REQ-0.13.0-03-04` already sits on the right test and stays.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Open Design Questions (operator rules before plan)

**1. How a consumer obtains the next command.** GHI #1173 leaves it open: "Whether a command prints the next step on completion, or a query returns it, is open."

- **A. Print on completion only.** Each command that moves a run across a boundary ends its output with the next command. A fresh process learns it from the session orientation. No new CLI surface. Cost: a fresh process has no `gz` read of its own. Reading the marker file by hand, as `docs/user/runbook.md` lines 209-210 does for dispatch state, stays the fallback.
- **B. A query only.** A read-only query returns the position and its next command or blockers. Cost: inside a run the agent must remember to ask, which is the dependence on attention the GHI names.
- **C. Both.** Recommended. The agent inside a run is told without asking, and a fresh process can ask.

If B or C, where the query lives:

- **(i)** The existing read-only `gz obpi status` gains the run's next command in its human and `--json` output. Adds `src/gzkit/commands/status.py` and `docs/user/manpages/obpi-status.md` to the allowlist. An output-schema change.
<!-- gz-validate-skip: command-shape -->
- **(ii)** A new option on `gz obpi pipeline`, such as the `--next-step` that `ADR-pool.skill-runtime-authority-inversion` § Alternatives A names. Adds `src/gzkit/cli/parser_obpi.py` and `src/gzkit/commands/obpi_cmd.py` to the allowlist, with a manpage flag row and a help example.
- **(iii)** The read surface `OBPI-0.35.0-15` lands for the position, if it lands one.

Recommendation: (iii) when it exists, otherwise (i). `gz obpi pipeline` with the option left off launches a run, writes the markers and appends `pipeline_launched` (`src/gzkit/commands/obpi_cmd.py` lines 893-903), so a mistyped query on that verb is a launch. `OBPI-0.13.0-03` denied itself "new CLI flags, JSON stdout modes, or alternate runtime subcommands"; that brief is sealed and does not bind this ruling.

- **RULED 2026-10-04: C, with the query at (i).** Asked "how does a consumer obtain the next command?" with printing at each boundary plus a query on `gz obpi status` as option A, the operator answered, verbatim: "A". The options were put as one choice: print plus a query on `gz obpi status`; print plus an option on `gz obpi pipeline`; print only; a query only. Location (iii) does not exist, because OBPI-0.35.0-15 as ruled lands no query verb. Requirement 11 carries it.

**2. The values three attested requirements literally assert.** `REQ-0.13.0-03-01`, `-02` and `-04` assert the launch-entry values (`--from=verify` at full launch, `--from=ceremony` after verify, the guarded-sync command at ceremony), and `tests/commands/test_obpi_pipeline.py` asserts them at lines 177-181, 345-349 and 446-450. Only the last of those tests carries a `@covers` binding (`REQ-0.13.0-03-04`, line 423); the `@covers("REQ-0.13.0-03-01")` binding sits on the resume-fallback test at `tests/test_pipeline_runtime.py` line 131. The skill prescribes other commands at those positions (rows 1, 5 and 10 below).

- **A. One statement.** `next_command` becomes position-derived. The operator rules how each of the three requirements and its covering test is carried, under `docs/governance/attested-req-subject-retirement.md`. Recommended: one field with one meaning, and Decision item 12 says "the one next command".
- **B. Two statements.** The marker's `next_command` and `resume_point` keep the attested stage re-entry values. The position's next command is stated separately, and it is the one every consumer presents. The three requirements stay literally true. Cost: a marker with two "next" values, one of them the value GHI #1173 reports.
- **C. Launch instants keep the attested values.** Only later positions are position-derived. Cost: `--from=verify` is still stated at the launch position, which is the instance GHI #1173 observed.
- **RULED 2026-10-04: A.** Asked "what does the marker's `next_command` mean?", the operator answered, verbatim: "A". Two rulings followed the same day, each answered "A": the requirements are amended in place (Requirement 16), and the misplaced `@covers` binding moves to the test that asserts its requirement (Requirement 17). OBPI-0.35.0-15 no longer pins a `next_command` value at launch, so this brief amends nothing that brief attests.

**3. Rows where the skill and the runtime disagree today.** The GHI names the skill as the oracle. At Stage 3 and at Stage 5 the runtime has one composite command where the skill prescribes a sequence, and the two differ in content (rows 4, 11 and 12 below).

- **A. The skill governs every row.** Recommended, as the closure contract states it. The `--from` entry points remain as the runbook describes them, "Compatibility entry points for partial re-runs", and are not the stated next command inside a full run.
- **B. The runtime's composite governs where one exists.** The skill is then corrected to prescribe it. That is a change to stage procedure text, which belongs with `OBPI-0.35.0-17`.
- **C. Ruled row by row.**
- **RULED 2026-10-04: A.** Asked which governs at the rows where the skill and the runtime disagree, the operator answered, verbatim: "A". The skill governs every row, and its text is not changed to match a composite. Requirement 3 carries it.

## What The Skill Prescribes Today

A dated record, read 2026-10-04 at `skill-version` 6.64.3. The skill and the code are the authorities; re-read both at plan time. Rows are skill boundaries, not the position set, which `OBPI-0.35.0-15` defines.

| # | Boundary the run has crossed | The skill prescribes next (`SKILL.md` lines) | The runtime states today |
|---|---|---|---|
| 1 | Launch wrote the markers | `uv run gz obpi acceptance <OBPI> init` (238-239), then the Stage 1 to 2 gate and the first Stage 2 task | `--from=verify`, in the marker (`pipeline_markers.py` 290-295) and printed (`obpi_stages.py` 232) |
| 2 | Stage 2, a task's implementer returned | `uv run gz obpi dispatch <OBPI> --role Implementer` (395), `gz obpi acceptance <OBPI> prove` (316-320), the two reviews (450-470) | unchanged since launch |
| 3 | Stage 2, last task advanced | unscoped `gz obpi acceptance <OBPI> status --stage stage2` (478-479), then Stage 3 (556) | unchanged since launch |
| 4 | Stage 3, Phases 1, 1b, 1c | `uv run gz arb ruff` and the rest of the baseline (566-576), `uv run gz covers <OBPI> --json` (609), `uv run gz arb red` per BEHAVIOR REQ (631) | `--from=verify`, one composite command (`obpi_stages.py` 129-180) |
| 5 | Stage 3 passed | `uv run gz obpi present-evidence <OBPI> --json` (906) | the marker says `--from=ceremony` (`pipeline_markers.py` 265-270) while the same process has already entered ceremony (`obpi_stages.py` 291-304) |
| 6 | Step 4a packet written | `uv run gz obpi verify-packet` (1020) | nothing |
| 7 | Step 4a-v verified | `uv run gz obpi adversary-workspace <OBPI>` (1135), the ARB-wrapped dispatch (1148-1150), `gz obpi acceptance <OBPI> review --receipt` (1255) | nothing |
| 8 | A Step 4b round imported | `uv run gz obpi acceptance <OBPI> status --stage stage4 --json` (762); on findings, one repair round and re-entry at 4a (838-841) | nothing |
| 9 | Round bound reached, or a round repeats the prior root | `uv run gz obpi block` and stop (864-878). The next move is the operator's `gz obpi unblock` (1604) | nothing. A launch is refused (`obpi_cmd.py` 767-778) |
| 10 | Stage 4 passed, awaiting attestation | wait for the operator (1324); on attestation, Stage 5 at once (1328-1332) | `required_human_action` and `--from=sync` (`pipeline_markers.py` 271-282). As stated that command cannot run: `--from=sync` requires `--evidence-json` (`obpi_cmd.py` 968-973) |
| 11 | Attestation received | `uv run gz obpi precomplete <OBPI>` (1345), the closure-narrative preview (1373), `uv run gz obpi complete` (1398) | `--from=sync` runs `gz obpi complete` first, with no preview (`obpi_stages.py` 493-508) |
| 12 | Completed | `uv run gz obpi lock list` (1456), the Step 4b brief section (1460), `uv run gz git-sync --apply` (1469), `uv run gz obpi sync <OBPI>` (1471), `uv run gz adr status <ADR> --json` (1472), `uv run gz git-sync --apply` (1474), `/gz-session-handoff` (1476) | `uv run gz git-sync --apply --lint --test` (`pipeline_markers.py` 81-83, 283-289), then `gz obpi sync`, `gz adr status` and a plain commit and push (`obpi_stages.py` 503-508, 579-586) |
| 13 | A verification command failed | fix once and re-verify, else abort surrender and handoff (600, 737) | the marker holds the blockers and `next_command: null` (`pipeline_markers.py` 258-264), but `pipeline_resume_command` returns `--from=verify` for that marker (652-667) and the reminder prints it under "Next canonical command" beside the blockers (726-766) |

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: § Decision item 12, "THE RUNTIME STATES THE NEXT COMMAND FOR WHERE THE RUN IS", quoted in full under § ADR Item above.
- [ ] Parent ADR § Intent — the 2026-10-04 amendment. It says why a corpus ADR carries a pipeline repair, and that no control is removed.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] `docs/governance/state-doctrine.md` - the marker is Layer 3
- [ ] `docs/governance/attested-req-subject-retirement.md` - governs Open Design Question 2

**Context:**

- [ ] GHI #1173 in full: the closure contract is the source of the criteria below
- [ ] GHI #1172 and `OBPI-0.35.0-15-pipeline-run-position`: the positions, and how a run records one
- [ ] `docs/design/adr/pre-release/ADR-0.13.0-obpi-pipeline-runtime-surface/obpis/OBPI-0.13.0-03-structured-stage-outputs.md`: the original requirement, its denied paths and its five attested REQs
- [ ] `docs/governance/context-phase-review-2026-10-04-evidence/README.md` proposal 4, and campaign § Amendments 2026-10-04 (2)
- [ ] `OBPI-0.35.0-17-stage-procedure-served-by-runtime`: it depends on this brief and owns the stage procedure text

**Prerequisites (check existence, STOP if missing):**

- [ ] `OBPI-0.35.0-15-pipeline-run-position` is completed in the ledger: `uv run gz obpi status OBPI-0.35.0-15-pipeline-run-position`. Without it there is no recorded position to read
- [ ] The operator's rulings on Open Design Questions 1, 2 and 3 are recorded in this brief
- [ ] Required path exists: `src/gzkit/pipeline_markers.py`
- [ ] Required path exists: `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] `src/gzkit/pipeline_markers.py` — `pipeline_stage_output` (line 248) takes `start_from` and nothing about progress; `pipeline_marker_payload` calls it at launch (336) and `refresh_pipeline_markers` on a failed verification (366), re-deriving `start_from` from the marker's `entry`
- [ ] `src/gzkit/pipeline_markers.py` — `pipeline_resume_command` (652-667) falls back from an empty `next_command` to `resume_point`, and `pipeline_completion_reminder_message` (713-768) falls back again to `--from=verify`
- [ ] `src/gzkit/commands/obpi_stages.py` — what each stage runner prints as it ends (227-233, 280-304, 327-358), and that a passed verification chains into ceremony in the same process
- [ ] `src/gzkit/commands/obpi_cmd.py` — `obpi_pipeline_cmd` (796-982): the launch writes the markers once (884-903) and `--from=sync` requires `--attestor` and `--evidence-json` (960-973)
- [ ] `src/gzkit/commands/status.py` — `obpi_status_cmd`, `_build_obpi_status_entry` and `_render_obpi_status_details`: what the verb returns today, and that it writes nothing
- [ ] `scripts/session_orientation.py` — `collect_adr_pipeline` reports `stage` and `resume_command` from the marker and carries no blockers (line 1019)
- [ ] `src/gzkit/hooks/scripts/pipeline.py` — the completion-reminder hook passes the marker to `pipeline_completion_reminder_message` (57-81)
- [ ] `tests/test_pipeline_runtime.py` lines 131-167 — two attested tests pin today's fallbacks: the resume command from `resume_point`, and a reminder that carries blockers and the `--from=verify` command together
- [ ] `tests/commands/test_obpi_pipeline.py`, `tests/scripts/test_session_orientation.py`, `tests/test_hooks.py` — fixture conventions for markers, the launch and the reminder hook
- [ ] `features/obpi_lock.feature` and `features/steps/obpi_lock_steps.py` — step conventions for a `gz obpi` command in an initialized workspace
- [ ] `docs/user/manpages/obpi-pipeline.md` lines 47-57 — the per-stage statements, to compare with what `obpi_stages.py` does

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted
- [ ] The repaired obligation of `ADR-0.13.0` cited by its existing identity

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] The table-driven test over positions lives in `tests/test_pipeline_next_command.py`
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] `docs/user/manpages/obpi-pipeline.md` § Runtime Behavior states where the next command is stated, how a fresh process obtains it and what a blocked position shows. Its per-stage statements match the runtime; the statements at lines 51-57 and 83-85, found stale at authoring, are corrected in the same patch
- [ ] `docs/user/manpages/obpi-status.md` shows the next-command output, human and `--json`
- [ ] `docs/user/runbook.md` § Step 2 describes the flow as the runtime now states it
- [ ] `docs/governance/GovZero/obpi-runtime-contract.md` § Active Pipeline Marker Fields matches the marker
- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] `features/obpi_pipeline_next_command.feature` carries one scenario per operator-visible BEHAVIOR REQ (`REQ-0.35.0-16-02` to `-05`), each tagged with its `@REQ-` id
- [ ] Acceptance scenarios pass: `uv run -m behave features/obpi_pipeline_next_command.feature`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded, with the security walkthrough of `.gzkit/rules/security-sensitivity.md`

## Verification

```bash
uv run -m unittest tests.test_pipeline_next_command tests.test_pipeline_runtime tests.commands.test_obpi_pipeline tests.commands.test_status tests.scripts.test_session_orientation tests.test_hooks
uv run -m behave features/obpi_pipeline_next_command.feature
uv run gz validate --documents --req-kind-discipline --cli-alignment --behave-req-tags
uv run gz cli audit
uv run gz skill audit
uv run mkdocs build --strict
```

## Demo

The feature drives the real commands in a throwaway workspace, so no marker or ledger row of this repository moves. It walks a run across boundaries and shows the stated next command change with the position, shows a fresh process obtaining it, shows a blocked position stating its blocker and no command, and shows the awaiting-attestation position stating the human action. It exits non-zero unless every scenario holds.

```bash
uv run -m behave features/obpi_pipeline_next_command.feature
```

The read surface is `gz obpi status` (Open Design Question 1, ruled). The feature invokes it in the throwaway workspace; its output against this repository's own in-flight run is captured in Key Proof (Requirement 15).

## Acceptance Criteria

<!-- REQ kinds per ADR-0.0.59; enforced by gz validate --req-kind-discipline. -->

- [ ] REQ-0.35.0-16-01 [BEHAVIOR]: Given every position a pipeline run can record, when the runtime derives the next command for that position, then it is the command `.gzkit/skills/gz-obpi-pipeline/SKILL.md` prescribes there, at every row (Open Design Question 3, ruled). One table-driven test holds a row per position, each row citing the skill section it transcribes, and a recordable position with no row fails the test
- [ ] REQ-0.35.0-16-02 [BEHAVIOR]: Given a run launched with any entry (full, `--from=verify`, `--from=ceremony`, `--from=sync`) whose recorded position has advanced past the launch, when the next command is stated, then it is the command for the recorded position and not the command for the launch entry. A run with no boundary crossed since launch states the launch position's command
- [ ] REQ-0.35.0-16-03 [BEHAVIOR]: Given an in-flight run whose position is recorded on disk, and a new process that holds only the repository (no conversation, no environment inherited from the run), when that process reads the run through the session orientation and through `gz obpi status` (human and `--json`), then it obtains the command REQ-0.35.0-16-01 specifies for that position, and the read changes no marker field and appends no ledger event
- [ ] REQ-0.35.0-16-04 [BEHAVIOR]: Given a blocked position (a failed verification command, or an `obpi_blocked_on_operator` event standing for the OBPI), when the marker stage output, the resume command, the completion reminder or the session orientation reports the run, then each states every blocker and none states a next command. When the blocker clears, the next command for the position is stated again
- [ ] REQ-0.35.0-16-05 [BEHAVIOR]: Given the Stage 4 awaiting-attestation position on any lane and kind, when the runtime states the position, then the required human action is stated, and every consumer that states a command there states the human action with it
- [ ] REQ-0.35.0-16-06 [SUPPORT]: `.gzkit/skills/gz-obpi-pipeline/SKILL.md` § The Iron Law names the runtime's stated next command as what carries a run across a boundary, and keeps the completion statement, the no-summary rule, the Stage 4 attestation pause after Step 4b and the round-bound stop. Witnessed by `artifact_edited` citing `.gzkit/skills/gz-obpi-pipeline/SKILL.md` + `gz validate --cli-alignment`.
- [ ] REQ-0.35.0-16-07 [SUPPORT]: `docs/user/manpages/obpi-pipeline.md` states where the next command is stated at each boundary, how a fresh process obtains it and what a blocked position shows, and its per-stage statements match the runtime. `docs/user/manpages/obpi-status.md` shows the next-command output, and `docs/user/runbook.md` § Step 2 and `docs/governance/GovZero/obpi-runtime-contract.md` § Active Pipeline Marker Fields agree with it. Witnessed by `artifact_edited` citing `docs/user/manpages/obpi-pipeline.md` + `gz validate --cli-alignment`.

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
