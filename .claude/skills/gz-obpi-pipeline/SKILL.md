---
name: gz-obpi-pipeline
description: Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved.
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-11
---

# gz-obpi-pipeline

Post-plan execution pipeline: implement the approved plan, verify, present
evidence, and sync.

Planning happens in native plan mode. This pipeline picks up after the plan is
approved and enforces the governance stages that get lost in freeform
execution.

---

## When to Use

- After exiting plan mode for an OBPI
- When the user says `execute OBPI-X.Y.Z-NN` or `complete OBPI-X.Y.Z-NN`
- When implementation is already done but verification, ceremony, or sync was
  skipped; use `--from=verify` or `--from=ceremony`

## When NOT to Use

- For planning; use plan mode instead
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
| *(none)* | 1 -> 2 -> 3 -> 4 -> 5 | Full post-plan execution |
| `--from=verify` | 1 -> 3 -> 4 -> 5 | Already implemented, need governance |
| `--from=ceremony` | 1 -> 4 -> 5 | Already verified, need attestation + sync |

Stage 1 always runs.

---

## Pipeline Stages

The pipeline executes five stages sequentially. Stage 4 behavior depends on the
parent ADR execution mode.

```text
1. Load Context
2. Implement
3. Verify
4. Present Evidence
5. Sync And Account
```

Normal mode uses a human gate at Stage 4. Exception mode self-closes with full
evidence and defers human review to ADR closeout.

### Stage 1: Load Context

1. Read `.claude/plans/.plan-audit-receipt.json` if it exists.
   - If the receipt matches the OBPI and verdict is `PASS`, load the approved
     plan file from `.claude/plans/`.
   - If verdict is `FAIL`, abort and correct plan alignment first.
   - If no receipt exists, warn and proceed; informal planning is compatible but
     should be treated as a gap.
2. Locate the OBPI brief under:
   - `docs/design/adr/**/obpis/OBPI-{id}-*.md`
   - `docs/design/adr/**/briefs/OBPI-{id}-*.md`
3. Extract objective, allowed and denied paths, requirements, acceptance
   criteria, lane, and verification commands.
4. Identify the parent ADR and inherit its lane and execution constraints.
5. Determine execution mode from the parent ADR:
   - `Exception (SVFR)` => `exception`
   - anything else => `normal`
6. Check for existing handoffs and resume context when present:
   - `docs/design/adr/**/handoffs/*.md`
7. Create a lightweight pipeline marker:
   - `.claude/plans/.pipeline-active-{OBPI-ID}.json`
8. Apply the brief allowlist as the working scope contract before any edits.

**gzkit compatibility rule:** A dedicated `gz-obpi-lock` surface is not present
yet. Until it exists, this pipeline must run one OBPI at a time for any shared
or spine-touch scope. If concurrent execution is required, stop with
`BLOCKERS`.

**Abort if:** brief not found, brief already `Completed`, or plan receipt verdict
is `FAIL`.

**On abort:** create a session handoff with `gz-session-handoff`.

### Stage 2: Implement

Skipped by `--from=verify` and `--from=ceremony`.

1. Create a task list from the approved plan.
   - Normal mode must end with `Present OBPI Acceptance Ceremony`.
   - Exception mode must end with `Record OBPI Evidence and Self-Close`.
2. Follow the plan step by step.
3. Keep edits inside the brief allowlist and transaction contract.
4. Run focused verification as work progresses.
5. Leave the tree in a state that can pass the brief verification commands.

### Stage 3: Verify

Skipped by `--from=ceremony`.

Run all verification commands from the brief, plus the baseline quality checks:

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
```

For Heavy lane work, also run:

```bash
uv run mkdocs build --strict
uv run -m behave features/
```

Record outputs as evidence.

**Abort if:** any required verification fails after one repair attempt.

### Stage 4: Present Evidence

#### Normal Mode — Human Gate

1. Present value narrative.
2. Present one key proof example.
3. Present verification evidence, file changes, and blockers cleared.
4. Wait for explicit human attestation.

Do not mark the brief `Completed` before attestation.

#### Exception Mode — Self-Close

1. Record the same value narrative, key proof, and verification evidence.
2. Record self-close evidence for later ADR closeout review.
3. Proceed to sync.

### Stage 5: Sync And Account

After attestation in Normal mode, or after evidence capture in Exception mode:

1. Run guarded repo sync before any final completion accounting:
   `uv run gz git-sync --apply --lint --test`
2. Abort Stage 5 if `git sync` fails or leaves unresolved divergence/blockers.
   Final completion receipts must not be captured from an unsynced state.
3. Emit the final completed receipt or equivalent OBPI completion accounting
   immediately after the successful sync so anchor evidence is captured from the
   synced repository state.
4. Update the OBPI brief with checked criteria, evidence, and attestation data.
5. Run `uv run gz obpi reconcile {OBPI-ID}` to confirm the synced receipt and
   brief agree.
6. Run `uv run gz adr status {PARENT-ADR} --json` so the parent ADR view
   reflects the reconciled OBPI state.
7. Remove `.claude/plans/.pipeline-active-{OBPI-ID}.json` if it was created.
8. Create a session handoff if more OBPIs remain or follow-up work is deferred.

---

## Error Recovery

| Failure Point | Action |
|---------------|--------|
| Brief not found | Stop and emit `BLOCKERS` |
| Plan audit receipt says `FAIL` | Stop and fix plan alignment |
| Tests or verification fail twice | Create handoff and stop |
| Human rejects attestation | Return to implementation with feedback |
| `git sync` fails or repo remains unsynced | Stop before completion accounting and repair blockers |
| Concurrent work required without a lock surface | Stop and emit `BLOCKERS` |

---

## Evidence Capture

| Stage | Evidence |
|-------|----------|
| 1 | brief, plan receipt, execution mode, scope contract |
| 2 | files changed, tests added, scope respected |
| 3 | command outputs and pass/fail status |
| 4 | value narrative, key proof, attestation text or self-close note |
| 5 | `git sync` result, completion receipt/accounting, brief update, reconcile/status proof, handoff if needed |

---

## Design Notes

- AirlineOps is the behavioral reference implementation for this pipeline.
- gzkit adapts the control surface to its native command vocabulary and current
  repository structure.
- Until `gz-obpi-lock` and plan-audit hooks are ported, pipeline stages that
  depend on them must fail closed instead of being silently skipped.
- The point of this skill is sequencing and governance memory: verify ->
  ceremony -> guarded git sync -> completion accounting is mandatory.
- In gzkit, `uv run gz git-sync --apply --lint --test` is the canonical Stage 5
  sync ritual. Do not substitute ad-hoc git commands.

---

## Related

- `AGENTS.md` section `OBPI Acceptance Protocol`
- `docs/user/concepts/workflow.md`
- `docs/user/runbook.md`
- `.gzkit/skills/gz-session-handoff/SKILL.md`
- `docs/governance/GovZero/obpi-transaction-contract.md`
