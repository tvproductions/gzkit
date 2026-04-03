---
name: gz-obpi-pipeline
description: Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. Use after exiting plan mode for an OBPI, when the user says "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-02
---

# gz-obpi-pipeline

Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

Planning happens in Claude Code's native plan mode. This pipeline picks up **after** the plan is approved and enforces the governance stages that get lost in freeform execution.

The canonical runtime launch surface is `uv run gz obpi pipeline`. The CLI
runtime, generated hook surfaces, and reminder messages share the same
runtime engine in `src/gzkit/pipeline_runtime.py`. This skill remains the
wrapper/operator ritual around that runtime rather than a second stage engine.

---

## The Iron Law

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

**There is no "stop and summarize" step.** There is no pause between stages unless Stage 4 is waiting for human attestation. Every stage flows into the next. If you are inside this pipeline and you have not reached the end of Stage 5, you are not done.

**Violating the spirit of this rule is violating the rule.**

### Rationalization Prevention

These thoughts mean STOP — you are about to break the pipeline:

| Thought | Reality |
|---------|---------|
| "Implementation is done, let me summarize" | Implementation is Stage 2. Stages 3, 4, 5 remain. You are not done. |
| "All tests pass, the work is complete" | Tests passing is Stage 3. Stages 4, 5 remain. You are not done. |
| "Let me present what was accomplished" | That is Stage 4. Stage 5 still remains. You are not done. |
| "I'll let the user handle the rest" | The user invoked the pipeline so they would NOT have to handle the rest. |
| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually. |
| "This is just a simple implementation" | Simple or complex, the pipeline owns the lifecycle. All 5 stages run. |
| "I can do the closing steps later" | No. The pipeline runs to completion NOW. Later means never. |
| "The user said 'implement the plan'" | The plan is for an OBPI. OBPI work = this pipeline. All stages. |
| "No plan receipt exists, I'll derive tasks from the brief" | No. Enter plan mode, get the plan approved, THEN resume. The brief is not a plan. |
| "The brief requirements are clear enough to skip planning" | Clarity is not the issue. The plan-audit handoff is a governance checkpoint. You do not get to skip it because you think you understand the work. |

### The Plan-Mode Gate

**No plan receipt → no implementation.** If Stage 1 finds no `.plan-audit-receipt.json` and the pipeline was invoked without `--from`, you MUST enter Claude Code's native plan mode before touching any source file. Read the OBPI brief, compose a plan, and wait for user approval. The plan-audit hook writes the receipt on exit. Only then does Stage 2 begin.

This is not optional. This is not something you can "derive informally." The plan-audit handoff exists because agents consistently skip planning when allowed to. You are not the exception.

### Hard Boundaries

After completing each stage, you MUST immediately begin the next stage. No summaries between stages. No "here's what I did" recaps. No waiting for permission to continue (except Stage 4 human gate in Normal mode).

**Stage 2 ends → Stage 3 begins immediately.**
**Stage 3 ends → Stage 4 begins immediately.**
**Stage 4 attestation received → Stage 5 begins immediately.**

If you find yourself composing a message that starts with "Here's a summary", "All working", "Implementation complete", or any variation — STOP. You are rationalizing. Proceed to the next stage.

---

## When to Use

- After exiting plan mode for an OBPI (plan approved, ready to execute)
- When the user says `execute OBPI-X.Y.Z-NN` or `complete OBPI-X.Y.Z-NN`
- When implementation is already done but governance stages (verify, ceremony, or
  sync) were skipped — use `--from=verify` or `--from=ceremony`

## When NOT to Use

- For planning — use Claude Code plan mode instead
- When no OBPI brief exists for the work

---

## Invocation

```text
/gz-obpi-pipeline OBPI-0.14.0-05
/gz-obpi-pipeline OBPI-0.14.0-05 --from=verify
/gz-obpi-pipeline OBPI-0.14.0-05 --from=ceremony
```

Short-form OBPI IDs are accepted: `0.14.0-05` expands to `OBPI-0.14.0-05`.

### `--from` Flag

| Flag | Stages Run | Use Case |
|------|------------|----------|
| *(none)* | 1 → 2 → 3 → 4 → 5 | Full post-plan execution |
| `--from=verify` | 1 → 3 → 4 → 5 | Already implemented, need governance |
| `--from=ceremony` | 1 → 4 → 5 | Already verified, need attestation + sync |

Stage 1 always runs — context is needed for ceremony and sync regardless of entry point.

---

## Pipeline Stages

The pipeline executes 5 stages sequentially. **Stage 4 behavior depends on execution mode** — all other stages are autonomous.

```text
┌──────────────────────────────────────────────────────────────┐
│  Stage 1: LOAD CONTEXT       (autonomous)                    │
│  Stage 2: IMPLEMENT          (autonomous)                    │
│  ├─ DO NOT STOP HERE. Proceed to Stage 3.                    │
│  Stage 3: VERIFY             (autonomous)                    │
│  ├─ DO NOT STOP HERE. Proceed to Stage 4.                    │
│  Stage 4: PRESENT EVIDENCE   (mode-dependent — see below)   │
│  ├─ Normal: WAIT for human attestation, then Stage 5.        │
│  ├─ Exception: Self-close, then Stage 5.                     │
│  Stage 5: SYNC AND ACCOUNT   (autonomous)                   │
│  └─ Pipeline complete. NOW you may report status.            │
└──────────────────────────────────────────────────────────────┘

Normal mode:    Stage 4 = HUMAN GATE (wait for attestation)
Exception mode: Stage 4 = SELF-CLOSE (record evidence, proceed)
```

### Stage 1: Load Context

1. Read `.claude/plans/.plan-audit-receipt.json` to find the approved plan
   - If receipt exists and OBPI matches: load the plan file from `.claude/plans/`, extract implementation steps
   - If receipt verdict is `FAIL`: **abort** — plan did not pass audit
   - If no receipt found AND `--from` flag is NOT set: **STOP — enter plan mode.** Read the OBPI brief, compose a plan in Claude Code's native plan mode, and wait for user approval. Only resume the pipeline after the plan-audit-receipt is written. Do NOT "derive tasks informally" or "proceed without a plan." The plan-audit handoff is a governance checkpoint, not an optimization.
   - If no receipt found AND `--from=verify` or `--from=ceremony`: proceed (the user is explicitly resuming a partially-completed pipeline where implementation already happened)
2. Locate the OBPI brief under:
   - `docs/design/adr/**/obpis/OBPI-{id}-*.md`
   - `docs/design/adr/**/briefs/OBPI-{id}-*.md`
3. Extract: objective, requirements, allowed/denied paths, acceptance criteria, lane, verification commands
4. Identify the parent ADR and inherit its lane and execution constraints.
5. Determine execution mode from the parent ADR:
   - `Exception (SVFR)` → set mode=exception
   - anything else → set mode=normal
6. Check for existing handoffs and resume context when present:
   - `docs/design/adr/**/handoffs/*.md`
7. Claim OBPI lock via `/gz-obpi-lock claim {OBPI-ID}`
8. Create pipeline markers:
   - `.claude/plans/.pipeline-active-{OBPI-ID}.json`
   - `.claude/plans/.pipeline-active.json` as a legacy compatibility marker
     for the same OBPI
   - Marker payload should include `obpi_id`, `parent_adr`, `lane`, `entry`,
     `execution_mode`, `current_stage`, `started_at`, `updated_at`,
     `receipt_state`, `blockers`, `required_human_action`, `next_command`, and
     `resume_point`
   - This unblocks the pipeline-gate PreToolUse hook for src/ and tests/ writes.
9. Apply the brief allowlist as the working scope contract before any edits.

**Abort if:** brief not found, brief already `Completed`, or plan receipt verdict is `FAIL`.

**On any abort:** Release lock if claimed, run `/gz-session-handoff` to preserve context.

### Stage 2: Implement (skipped by `--from=verify` or `--from=ceremony`)

**Check the `--no-subagents` flag first.** If set, skip to the Inline Fallback below.

#### Subagent Dispatch Mode (default)

Read `DISPATCH.md` for the full protocol. Summary:

1. Extract plan tasks from the approved plan file
2. Create task list (last task = ceremony or self-close depending on mode)
3. Read brief requirements (`## Requirements (FAIL-CLOSED)`) as scoped context
4. For each task sequentially: classify complexity → select model tier → dispatch implementer → two-stage review (spec + quality)
5. Handle results: DONE → review → advance; BLOCKED → halt and escalate
6. Persist dispatch state after each task

**Abort if:** Any task returns `BLOCKED` after retry or after exhausting review fix cycles. Create handoff, release lock, and stop.

#### Inline Fallback (`--no-subagents`)

When `--no-subagents` is set, Stage 2 runs entirely in the main session (no Agent tool dispatch):

1. Create task list from plan steps (same as above)
2. Follow the approved plan step by step
3. Keep edits inside the brief allowlist and transaction contract
4. Write code with tests (unittest, TempDBMixin for DB, coverage >= 40%)
5. Run `uv run ruff check . --fix && uv run ruff format .` after code changes
6. Run `uv run -m unittest -q` after implementation

**Abort if:** Tests fail after 2 fix attempts. Create handoff, release lock, and stop.

**MANDATORY TRANSITION → Stage 3.** Do not summarize. Do not report. Proceed.

### Stage 3: Verify (skipped by `--from=ceremony`)

Stage 3 runs two phases: **baseline quality checks** and **REQ-level verification dispatch**.

#### Phase 1: Baseline Quality Checks

Run the standard quality checks sequentially (these are always inline, never dispatched):

```bash
# Always
uv run gz lint
uv run gz typecheck
uv run gz test

# If Heavy lane
uv run gz validate --documents
uv run mkdocs build --strict
uv run -m behave features/
```

If any baseline check fails, attempt fix and re-verify once. If still failing, create handoff, release lock, and stop.

#### Phase 2: REQ-Level Verification Dispatch

Read `VERIFICATION.md` for the full protocol. Summary:

1. Extract verification scopes from brief requirements
2. Partition into independent groups by path overlap (non-overlapping → parallel, overlapping → same group)
3. Dispatch verification subagents per group (worktree-isolated, concurrent)
4. Aggregate results: all pass → Stage 4; any fail → fix once, then handoff

**Inline fallback:** When `--no-subagents` is set or strategy is `sequential`, run verification commands sequentially inline.

**Abort if:** Any verification fails after one fix attempt. Create handoff, release lock, and stop.

**MANDATORY TRANSITION → Stage 4.** Do not summarize. Do not report. Proceed.

### Stage 4: Present Evidence

**Mode determines behavior at this stage.**

#### Normal Mode — HUMAN GATE

**Trigger:** "Present OBPI Acceptance Ceremony" task becomes next pending. Mark `in_progress`.

Present evidence using the **exact template below**. This is the human's attestation surface — they cannot provide attestation without seeing this output. Every field is mandatory. Do not omit, reorder, or freeform this.

**Required output template:**

```
## Stage 4: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

**1. Value Narrative**

<What problem existed before this OBPI? What capability exists now? 2-3 sentences.>

**2. Key Proof**

<One concrete command + output the reviewer can run or mentally execute.
Include the exact command and its output or expected output.>

**3. Evidence**

| Check | Command | Result |
|-------|---------|--------|
| Tests | `uv run gz test` | <N> pass |
| Lint | `uv run gz lint` | <result> |
| Typecheck | `uv run gz typecheck` | <result> |
| OBPI tests | `uv run -m unittest tests.<test_module> -v` | <N/N> pass |
| <brief-specific> | <command> | <result> |

**Files created:**
- <path> (<description>)

**Files modified:**
- <path> (<description>)

**REQ verification:**
- REQ-X.Y.Z-NN-01: <function/mechanism> — <what it detected/proved>
- REQ-X.Y.Z-NN-02: ...
- ...

**4. Awaiting attestation.** Do NOT proceed to Stage 5 until human responds.
```

**Every field above MUST be populated.** Do not skip the evidence table. Do not skip REQ verification. Do not skip files created/modified. The human needs all of this to make an attestation decision.

Wait for the human to respond "Accepted", "Completed", or equivalent. Do NOT proceed until attestation is received.

Do NOT mark ceremony task `completed` until attestation is received.

**Human rejects:** Record feedback, return to Stage 2 with corrections.

#### Exception Mode — SELF-CLOSE

**Trigger:** "Record OBPI Evidence and Self-Close" task becomes next pending. Mark `in_progress`.

Present evidence using the **same template as Normal mode** (all fields populated), then:

4. **Self-close** — Record `attestation_type: "self-close-exception"` in ledger. Proceed to Stage 5.

Evidence is full-fidelity. Human reviews at ADR closeout.

**MANDATORY TRANSITION → Stage 5.** Once attestation is received (Normal) or self-close is recorded (Exception), proceed to Stage 5 immediately. Do not summarize. Do not wait.

### Stage 5: Sync And Account

After attestation (Normal) or self-close (Exception):

**Two-sync pattern:** Stage 5 uses two git-sync cycles. The first commits all
governance edits (attestation, brief, audit) so the tree is clean. The completion
receipt is then emitted against that clean commit — capturing a deterministic
per-OBPI anchor hash. The second sync commits the receipt and reconcile output.

1. **Record attestation in ledger** — Append a dedicated attestation entry to the **ADR-level** audit ledger
   (`{adr-package}/logs/obpi-audit.jsonl`) BEFORE updating the brief. The `obpi-completion-validator.py` hook
   checks the ledger for `attestation_type: "human"` (Normal mode) or
   `attestation_type: "self-close-exception"` (Exception mode) and will BLOCK the brief
   status change if this entry is missing.

   **Normal mode attestation entry format:**
   ```json
   {"type":"obpi-audit","timestamp":"<ISO-8601>","obpi_id":"<OBPI-ID>","adr_id":"<ADR-ID>","attestation_type":"human","evidence":{"human_attestation":true,"attestation_text":"<user's attestation text>","attestation_date":"<YYYY-MM-DD>"},"action_taken":"attestation_recorded","agent":"claude-code"}
   ```

   **Exception mode attestation entry format:**
   ```json
   {"type":"obpi-audit","timestamp":"<ISO-8601>","obpi_id":"<OBPI-ID>","adr_id":"<ADR-ID>","attestation_type":"self-close-exception","evidence":{"human_attestation":false},"action_taken":"attestation_recorded","agent":"claude-code"}
   ```

   **Critical vocabulary:** Use `"human"` exactly (not `"human-attested"`, not `"attested"`).
   The hook checks `attestation_type == "human"` or `evidence.human_attestation == true`.

2. Run `/gz-obpi-audit {OBPI-ID}` to record full evidence ledger entry
3. Update brief using a **single Write operation** (full file rewrite):
   - Read the current brief content
   - Compose the complete final content: check all criteria boxes `[x]`,
     add `### Implementation Summary` (bullet format: `- Key: value`),
     add `### Key Proof` (command output in code blocks),
     update Human Attestation section, update `**Brief Status:**` to `Completed`,
     update `**Date Completed:**`, AND change frontmatter `status: Completed`
   - Write the entire file at once
   - **Why atomic:** The `obpi-completion-validator.py` hook fires on
     any edit introducing `Status: Completed` and checks the would-be file
     content for evidence sections. Incremental Edit calls that change status
     before evidence exists will always be blocked. A single Write with
     everything included passes on the first attempt.
4. Release OBPI lock via `/gz-obpi-lock release {OBPI-ID}`
5. Remove `.claude/plans/.pipeline-active-{OBPI-ID}.json` if it was created.
6. Remove `.claude/plans/.pipeline-active.json` only when it still points at
   the same OBPI as the per-OBPI marker.
7. **Git-sync #1** — `uv run gz git-sync --apply --lint --test`
   Commits all governance edits from steps 1-6. Tree is now clean with a
   deterministic commit hash anchoring this OBPI's work.
8. **Emit completion receipt** — `uv run gz obpi emit-receipt {OBPI-ID} --event completed --attestor {attestor} --evidence-json '{...}'`
   Captures the clean commit anchor from step 7. The receipt's `git_sync_state.dirty`
   will be `false` and `anchor.commit` will point to the exact commit containing
   this OBPI's final state.
9. Run `uv run gz obpi reconcile {OBPI-ID}` to confirm receipt and brief agree.
10. Run `uv run gz adr status {PARENT-ADR} --json` so the parent ADR view
    reflects the reconciled OBPI state.
11. **Git-sync #2** — `uv run gz git-sync --apply --lint --test`
    Commits the receipt (step 8) and reconcile output (step 9).
12. Create a session handoff if more OBPIs remain or follow-up work is deferred.

---

## Completion Contract

The pipeline is complete when — and ONLY when — all of these are true:

1. Attestation recorded in ADR-level audit ledger (Stage 5, Step 1)
2. `/gz-obpi-audit` ran (Stage 5, Step 2)
3. Brief updated to `Completed` (Stage 5, Step 3)
4. Lock released, markers cleaned (Stage 5, Steps 4-6)
5. Git-sync #1 committed governance edits (Stage 5, Step 7)
6. Completion receipt emitted with clean anchor (Stage 5, Step 8)
7. Reconcile passed (Stage 5, Step 9)
8. Git-sync #2 committed receipt and reconcile (Stage 5, Step 11)

If any of these have not happened, the pipeline is not complete. Do not claim otherwise.

**What "done" looks like:** The final output of a successful pipeline run is a short status line confirming Stage 5 completed — not a summary of the implementation, not a recap of what was built. Just: "Pipeline complete. OBPI-X.Y.Z-NN synced and lock released."

### Anti-Pattern: The Premature Summary

The single most common pipeline failure is: the agent finishes writing code, prints a summary of files created and tests passing, and stops. This abandons the OBPI in a half-finished governance state — implemented but unverified, unattested, unsynced. The operator must then manually re-invoke the pipeline with `--from=verify` to finish the job.

**This is the failure mode this skill exists to prevent.** If you find yourself writing a summary after Stage 2 or Stage 3, you are committing this exact anti-pattern. Stop writing the summary. Start the next stage.

### Anti-Pattern: Hook Bypass

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.

---

## Reference Material

Error recovery, evidence capture, plan-audit-receipt contract, parallel execution,
design notes, and related skill mapping are in `REFERENCE.md`.
