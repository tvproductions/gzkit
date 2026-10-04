# Record — context, phase and session review, 2026-10-04

This is a **dated record**, measured and read on 2026-10-04. It states measurements, one
reader's classification of the insight history, and a reading of the pipeline code. It rules on
nothing and removes nothing. The proposals at the end are proposals; the operator routes them.
Re-run the script rather than trusting a figure transcribed here.

## Why this was taken

The OBPI-0.35.0-08 pipeline run and the OBPI-0.35.0-10 single-session trial
([run-cost record](../obpi-run-cost-2026-10-03-evidence/README.md)) differed sharply in recorded
cost, and the [gate-by-gate value read](../gate-value-read-2026-10-03-evidence/README.md) could
count catches only where a control leaves a ledger record. On that evidence the automatic
controls were switched off on 2026-10-04. The operator reversed that the same day and asked for
a different review. Verbatim:

> I do not want to curtail ANYTHING (I change my mind). I want a thorough review that keeps
> EVERYTHING we've fought hard for over the last 6-7 months and rather focuses on context, phase,
> and focus/attention management for the model.

The question this record answers is where the cost and the errors of a long run come from, with
every control kept.

## Method

Four tracks, each run by a separate read-only agent and then checked by the session that
commissioned them.

1. **Context growth by stage.** [`context_analysis.py`](context_analysis.py) reads the two
   session transcripts, which live outside the repository on the machine that ran them, and
   writes [`results.json`](results.json) and the CSV files beside it. Its method follows the
   run-cost script: one usage record per API call, and context is input plus cache-read plus
   cache-creation tokens. Run it from the repository root:

   ```
   uv run python docs/governance/context-phase-review-2026-10-04-evidence/context_analysis.py
   ```

   Its totals for the baseline orchestrator match the run-cost record exactly.
2. **What loads into context.** Sizes are character counts from `wc -m`; token figures are
   estimates at four characters per token. Per-touch rule loads were computed by matching each
   rule's `paths:` globs against a touched path.
3. **Run state and phase boundaries.** A full read of the pipeline runtime, the launch command,
   the lock manager, the acceptance store and execution, precomplete and complete, with file and
   line references. Four of its claims were re-checked in the source before this record was
   written.
4. **The insight history.** All 798 `improvement` and `defect` rows of
   `.gzkit/insights/agent-insights.jsonl` were classified by one reader under
   [a written rubric](insight-classification-rubric.txt); the result is
   [`insight-classification.json`](insight-classification.json). The pipeline skill was read in
   full to list the cause it cites for each control.

"Estimated" below always means derived from a character count. "Projected" means arithmetic on
the measured curve.

## Findings

### 1. The cost is context re-read, concentrated late

The baseline orchestrator's context grew at every call and was never compacted. Its cache-read
tokens by stage:

| Stage | Calls | Context at entry | Context at exit | Share of cache-read |
|---|---:|---:|---:|---:|
| Before the pipeline (handoff resume, plan amendment) | 17 | 55,206 | 129,900 | 1.5% |
| Launch to first dispatch | 22 | 170,282 | 258,840 | 4.1% |
| Implementation | 38 | 262,574 | 362,462 | 9.9% |
| Review and fix cycles | 51 | 366,022 | 465,896 | 18.0% |
| Verification baseline | 11 | 466,936 | 480,772 | 4.4% |
| Evidence and cross-vendor review | 78 | 482,307 | 653,093 | 37.3% |
| Completion and sync | 43 | 658,104 | 743,855 | 24.9% |

The last two stages hold 62 percent of the reads in 121 calls. Stages were re-entered: reviewer
dispatch began at six different calls, the baseline at three, the cross-vendor review at three
and `gz obpi precomplete` at five. Three calls rewrote the whole context to cache; the largest
followed a wait of about two hours for the operator's attestation.

### 2. The controls print little; other things grow the context

`gz arb` output is about 4 percent of the command output that entered the baseline's context.
The largest growers were the model's own output (43 percent of measured growth), shell
inspection of the repository, skill bodies, and messages returned by subagents (about 34,000
tokens estimated). A fresh subagent started at about 16,000 to 17,000 tokens; the orchestrator
started at 55,206.

### 3. Fixed loads are large and loaded more than once

One full pipeline run loads about 458,000 characters of documents into the main session before
any code or command output. The largest are the pipeline skill, the parent ADR, the path-scoped
rules, the brief, and the handoff skill. Path-scoped rules load on a file read, not only on an
edit. The session-start orientation is run again at every compaction, and about 73 percent of it
is the campaign block. The root instruction files load again into every subagent. Root
`AGENTS.md` is over the budget in `data/instructions_files_budget.json`, and twelve skill bodies
are over the body ceiling in `src/gzkit/skill_contract.py`, all inside their grandfather
ceilings.

### 4. Nine pieces of run state live only in the conversation

Read from code. A different session can already resume a run at stage level: no launch path
checks session, agent or lock. What a fresh context would not find on disk:

1. the Stage 2 task list, per-task status and fix-cycle counters;
2. implementer results and how reviewer verification gaps were handled;
3. the cursor inside a stage (which task, which Stage 3 phase, which Stage 4 round, which
   Stage 5 step);
4. `gz covers` and verification-dispatch results;
5. the packet-replay verdict;
6. the cross-vendor round count and the comparison of each round's root with the last;
7. the operator's attestation words, until completion records them;
8. the closure narrative;
9. scratch paths for prompts, proof specifications and the reviewer's checkout.

The pipeline marker's stage is set at launch and not advanced within a run. The orientation's
pipeline section is hard-coded empty. The lock has no phase-boundary release: release needs a
completion or an abandon record, and a session handoff is never found because the finder reads
only `.gzkit/locks/exchange/`. A second session can continue under the first lock if it does not
claim again.

Proof and review currency is one digest over the source, test, feature, data, script, rule,
schema, workflow and configuration files plus the brief's contract. Any edit there stales every
proof and every review for the OBPI at once.

### 5. The history shows the controls were installed for cause

| Type | Context or attention | Fabrication or overclaim | Apparatus defect | Product defect | Process or scope | Other |
|---|---:|---:|---:|---:|---:|---:|
| improvement | 174 | 71 | 51 | 9 | 193 | 59 |
| defect | 11 | 19 | 150 | 55 | 3 | 3 |

Of 27 pipeline controls, 20 answer at least in part a failure of the model's attention or of its
honesty about its own work, by the cause the skill itself cites. Honesty dominates. The history
supports the claim that context size causes the attention failures only partly: twelve of the
attention rows name context size, compaction or session length. The direct evidence for the cost
of context is finding 1.

### 6. Hooks and validators leave no record of a refusal

No ledger event records that a hook refused or that a validator scope failed. The gate-by-gate
read could therefore count neither. A control that prevents a failure leaves nothing to count.

## Projection

Arithmetic, not measurement. With the same calls and the same growth inside each stage, and the
context reset at each stage boundary to the session's first-call load plus a 20,000-token save
point, the baseline orchestrator's cache-read tokens fall from 118,627,618 to 34,141,495, about
71 percent. With a subagent-sized starting load the fall is about 79 percent. The same arithmetic
on the trial gives about 40 percent, because half its reads sit inside one long implementation
stage. Boundary resets leave growth inside a stage untouched. The assumptions are listed in
`results.json`; that a 20,000-token save point suffices is untested.

## What stands in the way of each fresh-context method

| Method | Already supports it | In the way |
|---|---|---|
| A new session per phase | stage-level re-entry by `--from`; proofs, reviews and dispatch credit in the ledger; the handoff system | the skill's rule against stopping between stages; no lock release at a phase boundary; receipts counted since the lock claim; no re-entry point inside Stage 2 or Stage 4; the orientation shows no pipeline state |
| A thin orchestrator with phase agents | Stage 2 already has this shape; subagents share the lock identity; the acceptance importer takes only receipts | a subagent's claim is not evidence; dispatch recording accepts three roles only; results return as prose |
| Compaction at a stage boundary | same session, same lock, no relaunch; the Compact Instructions in `CLAUDE.md` | the summary is model prose, and every conversation-only item depends on it; the operator's verbatim words risk paraphrase |

## Proposals, for the operator to route

No control is removed by any of these.

**Phase and state**

1. The runtime writes a save point at each stage and sub-stage boundary, generated from the
   ledger and marker, covering the nine conversation-only items.
2. The marker advances within a run, and the orientation shows pipeline state.
3. All three fresh-context methods, each where it fits: a thin orchestrator with phase agents
   for long autonomous stretches; a new session at the human boundary; compaction as the
   fallback inside a stage.
4. The rule against stopping between stages keeps its purpose and changes its mechanism: a
   mechanical next command in the save point answers the premature-summary failure.
5. The lock gets a rule for continuing across a phase boundary.
6. Proof staleness is scoped to what a proof names.

**Load**

7. The pipeline skill is split by stage, so a phase loads only its own. Its incident history
   moves to a rationale record keyed by control, which becomes the register of causes.
8. The orientation's open-checkboxes line becomes a pointer.
9. Commands and agents return a file path and an exit code, not prose.

**Witness data**

10. Every hook and validator records its refusals to the ledger.
11. Each run records context size per stage, so cost is observed and not reconstructed from
    transcripts.

## Defects found in the existing machinery

Each is recorded once in `.gzkit/insights/agent-insights.jsonl`. None was repaired here.

- The `--no-subagents` flag of `gz obpi pipeline` is parsed and read nowhere else.
- The skill's abort path prescribes `gz obpi lock release --force`, which exits 3 without an
  abandon category or an exchange record.
- The orientation's pipeline section is always empty.
- The skill cites GHI #196 as the cause of the precomplete checklist; the issue is GHI #195.

## Limits

- The insight classification is one reader's judgment, not adjudicated by a second. A blind
  re-read of a 64-row sample matched on 56 rows; the attention class leans high.
- The insight file records what was missed, not how full the context was. It cannot show that
  context size caused a miss.
- Character-to-token estimates understate: recorded text explains about 60 percent of the
  non-output growth. Shares are more reliable than absolute token figures.
- The harness's own system prompt and tool schemas are not in the transcripts.
- One baseline run and one trial run were measured. The two OBPIs differ in scope.
- The reading of code in track 3 covered the files named in its report; the modules it did not
  read are not vouched for here.
