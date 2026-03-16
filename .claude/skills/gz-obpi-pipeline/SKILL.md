---
name: gz-obpi-pipeline
description: End-to-end OBPI execution pipeline — plan, implement, verify, present evidence, and sync. Use when the user says "work on OBPI-X.Y.Z-NN", "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-16
---

# gz-obpi-pipeline

End-to-end OBPI execution pipeline: plan, implement, verify, present evidence, and sync.

This is the **single command** for all OBPI work. It owns the full lifecycle — from reading the brief through planning, implementation, verification, ceremony, and sync. There is no separate planning step; the pipeline handles it.

The canonical runtime launch surface is `uv run gz obpi pipeline`. The CLI
runtime, generated hook surfaces, and reminder messages share the same
runtime engine in `src/gzkit/pipeline_runtime.py`. This skill remains the
wrapper/operator ritual around that runtime rather than a second stage engine.

---

## The Iron Law

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 6 FINISHES.
```

**There is no "stop and summarize" step.** There is no pause between stages unless Stage 5 is waiting for human attestation. Every stage flows into the next. If you are inside this pipeline and you have not reached the end of Stage 6, you are not done.

**Violating the spirit of this rule is violating the rule.**

### Rationalization Prevention

These thoughts mean STOP — you are about to break the pipeline:

| Thought | Reality |
|---------|---------|
| "Implementation is done, let me summarize" | Implementation is Stage 3. Stages 4, 5, 6 remain. You are not done. |
| "All tests pass, the work is complete" | Tests passing is Stage 4. Stages 5, 6 remain. You are not done. |
| "Let me present what was accomplished" | That is Stage 5. Stage 6 still remains. You are not done. |
| "I'll let the user handle the rest" | The user invoked the pipeline so they would NOT have to handle the rest. |
| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually. |
| "This is just a simple implementation" | Simple or complex, the pipeline owns the lifecycle. All 6 stages run. |
| "I can do the closing steps later" | No. The pipeline runs to completion NOW. Later means never. |
| "The user said 'implement the plan'" | The plan is for an OBPI. OBPI work = this pipeline. All stages. |

### Hard Boundaries

After completing each stage, you MUST immediately begin the next stage. No summaries between stages. No "here's what I did" recaps. No waiting for permission to continue (except Stage 5 human gate in Normal mode).

**Stage 3 ends → Stage 4 begins immediately.**
**Stage 4 ends → Stage 5 begins immediately.**
**Stage 5 attestation received → Stage 6 begins immediately.**

If you find yourself composing a message that starts with "Here's a summary", "All working", "Implementation complete", or any variation — STOP. You are rationalizing. Proceed to the next stage.

---

## When to Use

- When the user says "work on OBPI-X.Y.Z-NN", "execute OBPI-X.Y.Z-NN", or "complete OBPI-X.Y.Z-NN"
- When implementation is done but governance stages were skipped — use `--from=verify` or `--from=ceremony`

## When NOT to Use

- When no OBPI brief exists for the work

---

## Invocation

```text
/gz-obpi-pipeline OBPI-0.11.0-05
/gz-obpi-pipeline OBPI-0.11.0-05 --from=verify
/gz-obpi-pipeline OBPI-0.11.0-05 --from=ceremony
```

Short-form OBPI IDs are accepted: `0.11.0-05` expands to `OBPI-0.11.0-05`.

### `--from` Flag

| Flag | Stages Run | Use Case |
|------|------------|----------|
| *(none)* | 1 → 2 → 3 → 4 → 5 → 6 | Full end-to-end execution |
| `--from=verify` | 1 → 4 → 5 → 6 | Already implemented, need governance |
| `--from=ceremony` | 1 → 5 → 6 | Already verified, need attestation + sync |

Stage 1 always runs — context is needed regardless of entry point.

---

## Pipeline Stages

The pipeline executes 6 stages sequentially.

```text
┌──────────────────────────────────────────────────────────────┐
│  Stage 1: LOAD CONTEXT       (autonomous)                    │
│  Stage 2: PLAN               (autonomous — enters plan mode) │
│  Stage 3: IMPLEMENT          (autonomous)                    │
│  ├─ DO NOT STOP HERE. Proceed to Stage 4.                    │
│  Stage 4: VERIFY             (autonomous)                    │
│  ├─ DO NOT STOP HERE. Proceed to Stage 5.                    │
│  Stage 5: PRESENT EVIDENCE   (mode-dependent — see below)   │
│  ├─ Normal: WAIT for human attestation, then Stage 6.        │
│  ├─ Exception: Self-close, then Stage 6.                     │
│  Stage 6: SYNC               (autonomous)                   │
│  └─ Pipeline complete. NOW you may report status.            │
└──────────────────────────────────────────────────────────────┘

Normal mode:    Stage 5 = HUMAN GATE (wait for attestation)
Exception mode: Stage 5 = SELF-CLOSE (record evidence, proceed)
```

### Stage 1: Load Context

1. Locate the OBPI brief:
   - `docs/design/adr/**/obpis/OBPI-{id}-*.md`
   - `docs/design/adr/**/briefs/OBPI-{id}-*.md`
2. Extract: objective, requirements, allowed/denied paths, acceptance criteria, lane, verification commands
3. Identify parent ADR and lane inheritance
4. Determine execution mode: Read parent ADR for `## Execution Mode` section.
   - If "Exception (SVFR)" found → set mode=exception.
   - If absent or "Normal" → set mode=normal.
5. Check for existing handoffs: `docs/design/adr/**/handoffs/*.md` (resume if fresh)
6. Claim OBPI lock via `/gz-obpi-lock claim {OBPI-ID}`
7. Map brief's allowed paths to instruction files and surface constraint preamble.

**Abort if:** Brief not found, brief status already `Completed`.

**On any abort:** Release lock if claimed, run `/gz-session-handoff` to preserve context.

### Stage 2: Plan (skipped by `--from=verify` or `--from=ceremony`)

1. Check for existing plan-audit receipt at `.claude/plans/.plan-audit-receipt.json`
   - If receipt exists, matches this OBPI, and verdict is `PASS`: **skip planning** — load the approved plan and proceed to Stage 3.
   - If receipt exists and verdict is `FAIL`: delete stale receipt and re-plan.
2. Enter plan mode.
3. Write a plan that:
   - References the OBPI ID in the plan content
   - Breaks the brief's requirements into implementation steps
   - Respects the brief's allowed/denied paths
4. Run `/gz-plan-audit {OBPI-ID}` to produce `.plan-audit-receipt.json`
5. Exit plan mode.
   - `plan-audit-gate.py` hook verifies receipt exists — allows exit
   - `pipeline-router.py` hook confirms routing (informational)
6. Create pipeline marker: Write `.claude/plans/.pipeline-active-{OBPI-ID}.json` with
   `{"obpi_id": "<the-obpi-id>", "started_at": "<ISO-8601 timestamp>", "mode": "normal|exception"}`.
   This unblocks the `pipeline-gate.py` PreToolUse hook for `src/` and `tests/` writes.

**Abort if:** Plan audit verdict is `FAIL` after one revision attempt.

### Stage 3: Implement (skipped by `--from=verify` or `--from=ceremony`)

1. Create task list from plan steps
   - Normal mode: Last task MUST be "Present OBPI Acceptance Ceremony"
   - Exception mode: Last task MUST be "Record OBPI Evidence and Self-Close"
2. Follow the approved plan step by step
3. Write code with tests (unittest, coverage >= 40%)
4. One step at a time — show output after each
5. Run `uv run ruff check . --fix && uv run ruff format .` after code changes
6. Run `uv run -m unittest -q` after implementation

**Abort if:** Tests fail after 2 fix attempts. Create handoff, release lock, and stop.

**MANDATORY TRANSITION → Stage 4.** Do not summarize. Do not report. Proceed.

### Stage 4: Verify (skipped by `--from=ceremony`)

Run all verification commands from the brief's acceptance criteria:

```bash
# Always
uv run gz test
uv run gz lint
uv run gz typecheck

# If Heavy lane
uv run coverage run -m unittest discover -s tests -t .
uv run coverage report --fail-under=40
uv run behave features/{relevant}.feature  # if BDD specified

# Brief-specific verification commands
[commands from brief's Verification section]
```

Record all outputs as evidence.

**Abort if:** Any verification fails. Attempt fix, re-verify once. If still failing, create handoff, release lock, and stop.

**MANDATORY TRANSITION → Stage 5.** Do not summarize. Do not report. Proceed.

### Stage 5: Present Evidence

**Mode determines behavior at this stage.**

#### Normal Mode — HUMAN GATE

**Trigger:** "Present OBPI Acceptance Ceremony" task becomes next pending. Mark `in_progress`.

Present evidence using the **exact template below**. This is the human's attestation surface — they cannot provide attestation without seeing this output. Every field is mandatory. Do not omit, reorder, or freeform this.

**Required output template:**

```
## Stage 5: Present OBPI Acceptance Ceremony (Normal Mode — HUMAN GATE)

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
| Type check | `uv run gz typecheck` | <result> |
| Coverage | `uv run coverage report --fail-under=40` | <N>% |
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

**4. Awaiting attestation.** Do NOT proceed to Stage 6 until human responds.
```

**Every field above MUST be populated.** Do not skip the evidence table. Do not skip REQ verification. Do not skip files created/modified. The human needs all of this to make an attestation decision.

Wait for the human to respond "Accepted", "Completed", or equivalent. Do NOT proceed until attestation is received.

Do NOT mark ceremony task `completed` until attestation is received.

**Human rejects:** Record feedback, return to Stage 3 with corrections.

#### Exception Mode — SELF-CLOSE

**Trigger:** "Record OBPI Evidence and Self-Close" task becomes next pending. Mark `in_progress`.

Present evidence using the **same template as Normal mode** (all fields populated), then:

4. **Self-close** — Record `attestation_type: "self-close-exception"` in ledger. Proceed to Stage 6.

Evidence is full-fidelity. Human reviews at ADR closeout.

**MANDATORY TRANSITION → Stage 6.** Once attestation is received (Normal) or self-close is recorded (Exception), proceed to Stage 6 immediately. Do not summarize. Do not wait.

### Stage 6: Sync

After attestation (Normal) or self-close (Exception):

1. **Record attestation in ADR-level audit ledger** — Append a dedicated attestation entry to
   `{adr-package}/logs/obpi-audit.jsonl`:

   **Normal mode attestation entry format:**
   ```json
   {"type":"obpi-audit","timestamp":"<ISO-8601>","obpi_id":"<OBPI-ID>","adr_id":"<ADR-ID>","attestation_type":"human","evidence":{"human_attestation":true,"attestation_text":"<user's attestation text>","attestation_date":"<YYYY-MM-DD>"},"action_taken":"attestation_recorded","agent":"claude-code"}
   ```

   **Exception mode attestation entry format:**
   ```json
   {"type":"obpi-audit","timestamp":"<ISO-8601>","obpi_id":"<OBPI-ID>","adr_id":"<ADR-ID>","attestation_type":"self-close-exception","evidence":{"human_attestation":false},"action_taken":"attestation_recorded","agent":"claude-code"}
   ```

   **Critical vocabulary:** Use `"human"` exactly (not `"human-attested"`, not `"attested"`).

2. **Emit completion receipt to main ledger** — This is the step that unblocks the
   `obpi-completion-validator.py` hook. The hook checks `.gzkit/ledger.jsonl` for an
   `obpi_receipt_emitted` event matching this OBPI. Without this, Step 5 will be BLOCKED.

   ```bash
   uv run gz obpi emit-receipt <OBPI-FULL-SLUG> \
     --event completed \
     --attestor "human:<Name>" \
     --evidence-json '{
       "value_narrative": "<from Stage 5>",
       "key_proof": "<from Stage 5>",
       "human_attestation": true,
       "attestation_text": "<user attestation text>",
       "attestation_date": "<YYYY-MM-DD>",
       "req_proof_inputs": [<structured REQ evidence>],
       "obpi_completion": "attested_completed",
       "attestation_requirement": "required",
       "parent_adr": "<ADR-FULL-SLUG>",
       "parent_lane": "<lite|heavy>"
     }'
   ```

   **For Heavy/Foundation lane:** `--attestor` MUST use `human:<Name>` format.
   **For Lite lane:** `--attestor` can be `agent:claude-code`.

   **DO NOT skip this step.** If you proceed to Step 5 without emitting the receipt,
   the hook will block the brief update and you will waste a tool call.

3. Run guarded repo sync: `uv run gz git-sync --apply`
   - Lint and test gates are handled by pre-commit hooks; no need to pass `--lint --test`.
   - Abort if sync fails or leaves unresolved divergence/blockers.
4. Run `/gz-obpi-audit {OBPI-ID}` to record full evidence ledger entry
5. Update brief: check all criteria boxes, add evidence section, set status to `Completed`
   - (Hook `obpi-completion-validator.py` enforces evidence requirements — receipt from Step 2 must exist)
6. Run `/gz-obpi-sync {ADR-ID}` to propagate status to ADR table
7. Release OBPI lock via `/gz-obpi-lock release {OBPI-ID}`
8. Remove `.claude/plans/.pipeline-active-{OBPI-ID}.json` if it was created.
9. Remove `.claude/plans/.pipeline-active.json` only when it still points at
   the same OBPI as the per-OBPI marker.
10. Run final `uv run gz git-sync --apply` to push brief and ADR table updates.
11. Create handoff if more OBPIs remain for the ADR

---

## Error Recovery

| Failure Point | Action |
|---------------|--------|
| Brief not found | Report error, release lock, stop |
| Plan audit verdict FAIL | Revise plan once, then handoff + release lock |
| Tests fail during implementation | Attempt fix (2 tries), then handoff + release lock |
| Verification fails | Attempt fix (1 try), then handoff + release lock |
| Human rejects attestation | Record feedback, return to Stage 3 with corrections |

**Lock bracket:** Lock is claimed at Stage 1 and released at Stage 6 AND on any abort/handoff. No orphaned locks.

**Handoff creation:** On any abort, run `/gz-session-handoff` to preserve context for the next session.

---

## Evidence Capture

Each stage records evidence to the OBPI audit ledger:

| Stage | Evidence Written |
|-------|-----------------|
| Stage 1 | Brief parsed, execution mode determined, lock claimed |
| Stage 2 | Plan created, plan-audit receipt produced |
| Stage 3 | Files changed, tests added |
| Stage 4 | Verification outputs (pass/fail) |
| Stage 5 | Attestation text + timestamp |
| Stage 6 | ADR audit ledger entry (Step 1), completion receipt in `.gzkit/ledger.jsonl` (Step 2), full audit entry (Step 4), brief updated (Step 5), lock released |

---

## Plan-Audit-Receipt Contract

The plan-audit-receipt (`.claude/plans/.plan-audit-receipt.json`) is an internal handoff artifact between Stage 2 and Stage 3:

```json
{
  "obpi_id": "OBPI-0.11.0-05",
  "timestamp": "2026-02-14T12:00:00Z",
  "verdict": "PASS",
  "plan_file": "my-plan-name.md",
  "gaps_found": 0
}
```

- Written by `/gz-plan-audit` during Stage 2
- Read by Stage 2 to determine if planning can be skipped (receipt already exists)
- **verdict = PASS**: plan is aligned with OBPI brief — proceed to implementation
- **verdict = FAIL**: plan has alignment gaps — revise plan

---

## Parallel Execution (Exception Mode)

Multiple independent OBPIs within the same ADR can run this pipeline concurrently in separate agent sessions when Exception mode is granted. Requirements:

1. ADR has `## Execution Mode: Exception (SVFR)` section (granted at ADR Defense)
2. OBPIs have non-overlapping allowed paths
3. Each session claims its OBPI via `/gz-obpi-lock`
4. Sync operations (Stage 6) are atomic per-brief

In Normal mode, OBPIs run sequentially with per-OBPI human attestation.

---

## Relationship to Existing Skills

| Skill | Role in Pipeline |
|-------|-----------------|
| `/gz-obpi-lock` | Stage 1 claim, Stage 6 release, abort release |
| `/gz-plan-audit` | Stage 2 — plan ↔ OBPI alignment check, produces receipt |
| `/gz-obpi-audit` | Stage 6 ledger recording |
| `/gz-obpi-sync` | Stage 6 ADR table sync |
| `/gz-session-handoff` | Error recovery — preserves context on abort |

---

## Hook Enforcement

**Hooks enforce the pipeline mechanically — the skill provides sequencing and governance memory.**

| Hook | Event | Enforcement |
|------|-------|-------------|
| `plan-audit-gate.py` | PreToolUse `ExitPlanMode` | Blocks plan exit until receipt exists |
| `pipeline-router.py` | PostToolUse `ExitPlanMode` | Confirms pipeline routing (informational) |
| `pipeline-gate.py` | PreToolUse `Write\|Edit` | Blocks `src/` and `tests/` writes until pipeline marker exists |
| `pipeline-completion-reminder.py` | PreToolUse `Bash` | Warns before `git commit/push` if pipeline incomplete |
| `obpi-completion-validator.py` | PreToolUse `Write\|Edit` | Blocks brief `Completed` status without ledger evidence |

---

## Design Notes

The pipeline's value is **end-to-end orchestration** — a single invocation takes an OBPI from brief to completion without requiring the operator to remember intermediate steps or invoke separate commands.

Hooks do the hard enforcement. The pipeline is orchestration narrative, not a security boundary.

In gzkit, `uv run gz git-sync --apply` is the canonical Stage 6
sync ritual. Lint and test gates run via pre-commit hooks.
Do not substitute ad-hoc git commands.

---

## Completion Contract

The pipeline is complete when — and ONLY when — all of these are true:

1. Attestation recorded in ADR-level audit ledger (Stage 6, Step 1)
2. `uv run gz git-sync --apply` succeeded (Stage 6, Step 2)
3. `/gz-obpi-audit` ran (Stage 6, Step 3)
4. Brief updated to `Completed` (Stage 6, Step 4)
5. `/gz-obpi-sync` ran (Stage 6, Step 5)
6. Lock released (Stage 6, Step 6)
7. Pipeline markers cleaned up (Stage 6, Steps 7-8)

If any of these have not happened, the pipeline is not complete. Do not claim otherwise.

**What "done" looks like:** The final output of a successful pipeline run is a short status line confirming Stage 6 completed — not a summary of the implementation, not a recap of what was built, not a celebration. Just: "Pipeline complete. OBPI-X.Y.Z-NN synced and locked released."

### Anti-Pattern: The Premature Summary

The single most common pipeline failure is: the agent finishes writing code, prints a summary of files created and tests passing, and stops. This abandons the OBPI in a half-finished governance state — implemented but unverified, unattested, unsynced. The operator must then manually re-invoke the pipeline with `--from=verify` to finish the job.

**This is the failure mode this skill exists to prevent.** If you find yourself writing a summary after Stage 3 or Stage 4, you are committing this exact anti-pattern. Stop writing the summary. Start the next stage.

### Anti-Pattern: Hook Bypass

If `pipeline-gate.py` blocks a write, that means the pipeline is not active. The correct response is to invoke the pipeline — NOT to manually create `.claude/plans/.pipeline-active-*.json` files. Manually creating marker files to bypass hooks defeats the entire enforcement mechanism.

---

## Related

- OBPI Acceptance Protocol: `AGENTS.md` § OBPI Acceptance Protocol
- Plan audit: `.claude/skills/gz-plan-audit/SKILL.md`
- Session handoff: `docs/governance/GovZero/session-handoff-obligations.md`
- Audit protocol: `docs/governance/GovZero/audit-protocol.md`
