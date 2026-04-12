---
name: gz-adr-closeout-ceremony
persona: main-session
description: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill.
category: adr-audit
compatibility: GovZero v6 framework; provides runbook walkthrough for human ADR attestation
metadata:
  skill-version: "7.2.1"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero-spec-references: "docs/governance/GovZero/charter.md, docs/governance/GovZero/audit-protocol.md"
  govzero-gates-covered: "Gate 5 (Human Attestation)"
  govzero_layer: "Layer 2 - Ledger Consumption"
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-08
---

# gz-adr-closeout-ceremony

Execute the ADR closeout ceremony by driving the CLI state machine.

**Authority:** `docs/governance/GovZero/audit-protocol.md`

---

## The Ceremony Contract

```
THE CEREMONY IS NOT COMPLETE UNTIL THE HUMAN ATTESTS AND THE REPO IS SYNCED.
```

Running walkthrough commands is not completion. Passing quality checks is not completion. Printing a summary is not completion. The ceremony exists to produce a **human attestation decision backed by structured evidence**, then persist that decision to the ledger and sync it.

**Violating the spirit of this contract is violating it.**

### Rationalization Prevention

These thoughts mean STOP — you are about to break the ceremony:

| Thought | Reality |
|---------|---------|
| "All checks passed, the ADR is done" | Checks passing is evidence. The human decides. You do not. |
| "Let me summarize the walkthrough results" | Present them in the evidence template. Do not interpret them. |
| "The human acknowledged each step, so they've attested" | Acknowledgment is not attestation. Wait for the explicit `--attest` decision. |
| "I'll skip the walkthrough since OBPIs already passed" | The walkthrough is the human's verification surface. You do not skip it for them. |
| "The CLI errored, I'll work around it" | CLI errors are signals. Diagnose the cause. Do not reimplement step logic. |
| "I can close the issues and sync later" | Later means never. The ceremony runs to completion NOW. |
| "The human said 'looks good'" | "Looks good" is not an attestation value. Ask for Completed, Completed-Partial, or Dropped. |

---

## Persona

**Active persona:** `main-session` — read `.gzkit/personas/main-session.md` and adopt its behavioral identity before executing this skill. Present evidence; do not interpret it. The human decides. You do not. When presenting walkthrough output, use the narrator's register: precision, operator-value framing, every word load-bearing.

## Trust Model

**Layer 2 — Ledger Consumption:** This skill orchestrates human attestation using ledger proof.

- **Reads:** Ledger entries, audit reports, ADR/OBPI files
- **Writes:** Attestation records, status updates via CLI commands
- **Does NOT re-verify:** Evidence (trusts Layer 1 proof)
- **Requires:** Human attestation before finalizing

---

## When to Use

- Human invokes "ADR closeout ceremony" (or equivalent: "begin closeout", "closeout ADR-X.Y.Z")
- Human is ready to witness and attest to ADR completion
- All OBPIs are believed to be complete

## When NOT to Use

- For individual OBPI completion — use `gz-obpi-pipeline` instead
- When OBPIs are still in progress — complete them first
- For audit-only checks without ceremony — use `gz adr audit-check`

---

## Architecture

The ceremony is driven by `src/gzkit/commands/closeout_ceremony.py`, which provides:

- **Step sequencing** — deterministic step ordering via `CeremonyStep` enum
- **Foundation skip** — `FOUNDATION_SKIP_STEPS` automatically skips RELEASE_NOTES and RELEASE steps for 0.0.x ADRs
- **State persistence** — ceremony state saved in `.gzkit/ceremonies/<ADR-ID>.json`
- **Walkthrough discovery** — commands extracted from OBPI briefs and command docs
- **Turn locks** — prevents step skipping

**The agent MUST drive the ceremony through CLI commands, not by reimplementing
step logic in prose.** The CLI handles all conditional logic (Foundation skips,
lane-specific steps, step ordering). The agent's role is to:

1. Run the CLI command for each step
2. Present the output using the evidence template
3. Wait for human acknowledgment
4. Advance via CLI

---

## Procedure

### Step 1: Initialize

When the human says "ADR closeout ceremony" (or equivalent), start the ceremony:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony
```

This initializes the ceremony state machine and outputs the Step 2 summary.
Present the output to the human. Do not interpret or claim outcomes.

**If resuming an interrupted ceremony:** The same command resumes from the last completed step. Check the current state first:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --ceremony-status
```

**Abort if:** ADR not found, no OBPIs exist, or ceremony state is corrupt (see Error Recovery).

### Step 2: Advance Through Steps

After the human acknowledges each step, advance:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --next
```

The CLI outputs the content for the next step. Present it and wait for acknowledgment.

**Repeat this cycle for each step.** The CLI handles:

- Which step comes next
- Skipping Foundation-excluded steps (RELEASE_NOTES, RELEASE for 0.0.x)
- What content to present at each step

### Step 3: Docs Alignment Check

When the CLI presents the docs alignment checklist (CLI Step 3), the human confirms
documentation parity. Advance via `--next` after acknowledgment.

**If the human identifies doc gaps:** Do not advance. Fix the documentation, run `uv run mkdocs build --strict` to verify, then re-present the checklist. Only advance after the human confirms parity.

### Step 4: Walkthrough Execution

When the CLI presents walkthrough commands (CLI Steps 4-5), run them one at a time:

- Run ONE command, show output, STOP and WAIT for acknowledgment
- Only proceed to next command after acknowledgment
- After all walkthrough commands are done, advance via `--next`

**If a walkthrough command fails:** See Error Recovery. Do not skip it. Do not advance past it. Fix it or escalate.

### Step 5: Attestation

When the CLI presents the attestation prompt (CLI Step 6), present the **Evidence Summary** (see template below), then wait for the human's decision:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --attest "Completed"
```

Valid attestations:
- `"Completed"` — ADR work is finished; all claims verified
- `"Completed - Partial: [reason]"` — Subset accepted, remainder deferred
- `"Dropped - [reason]"` — ADR rejected; does not advance

**Human requests corrections:** This is a rejection. Record the feedback, identify which ceremony steps need re-execution, and return to the appropriate step. Do NOT record a partial attestation when the human wants fixes. See Rejection Loop-Back below.

### Step 6: Closeout Pipeline

When the CLI presents CLI Step 7, run the closeout pipeline:

```bash
uv run gz closeout ADR-X.Y.Z
```

This handles quality gates, attestation recording, version bump, and closeout form.
After it completes, advance the ceremony:

```bash
uv run gz closeout ADR-X.Y.Z --ceremony --next
```

### Step 7: GitHub Issues

When the CLI presents CLI Step 8, close related issues:

```bash
gh issue list --search "ADR-X.Y.Z" --state open
gh issue close <number> --comment "Resolved by ADR-X.Y.Z closeout."
```

Then advance via `--next`.

### Step 8: Release Steps (CLI-Driven)

The CLI automatically handles Foundation vs non-Foundation:

- **Foundation (0.0.x):** Steps 9-10 are skipped automatically by `FOUNDATION_SKIP_STEPS`
- **Non-Foundation:** The CLI presents RELEASE_NOTES and GitHub Release steps

For non-Foundation releases:

```bash
# Step 9: Update RELEASE_NOTES.md (agent edits the file)
# Step 10: Sync and create GitHub release
uv run gz git-sync --apply --lint --test
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
```

After each step, advance via `--next`.

### Step 9: Completion (Two-Sync Pattern)

When the CLI outputs the ceremony completion summary (CLI Step 11), present it to the human, then run the **two-sync pattern** to commit the closeout cleanly. This mirrors `gz-obpi-pipeline`'s Stage 5 — every governance artifact must land in two reviewable commits.

```bash
# Sync 1 — closeout artifacts: ceremony state, attestation receipt, ADR audit
# updates, GHI close comments, release notes (if applicable).
uv run gz git-sync --apply --lint --test

# Sync 2 — reconcile output and ADR status refresh after the first sync lands.
uv run gz adr reconcile ADR-X.Y.Z
uv run gz git-sync --apply --lint --test
```

**Why two syncs:**

1. The first sync makes the human attestation, receipt, and walkthrough evidence durable before any derived state is rebuilt.
2. The second sync captures the reconciled ADR status (Layer 3 derived state) so `gz status` and downstream consumers see the closure.

If sync 1 fails, the ceremony is paused — fix the failing gate, re-run sync 1. **Never** skip sync 2: skipping it leaves the ledger and the derived ADR table out of sync, which is the same failure family as #129 (canon green, derived view stale).

The ceremony is done.

#### Fallback / Degraded Mode

If `gz git-sync` is unavailable (network failure, gh outage, dirty submodule):

1. Stop the ceremony at the failed sync. Do not advance.
2. Capture the exact error output and the ceremony state file path (`.gzkit/ceremonies/<ADR-ID>.json`).
3. Hand off to the human with a one-line summary plus the resume command:
   `uv run gz closeout ADR-X.Y.Z --ceremony` (re-attaches to the persisted state).
4. Do **not** manually commit closeout artifacts or hand-edit the ledger as a workaround. The ceremony resumes cleanly once sync is restored.

---

## Evidence Summary Template

Present this template at Step 5, before requesting attestation. Every field is mandatory. The human cannot make an informed attestation decision without structured evidence.

```
## ADR Closeout Evidence: ADR-X.Y.Z

**1. ADR Intent**

<What was this ADR's purpose? 1-2 sentences from the ADR document.>

**2. OBPI Completion Status**

| OBPI | Status | Attestor | Date |
|------|--------|----------|------|
| OBPI-X.Y.Z-01 | Completed | <name> | <date> |
| OBPI-X.Y.Z-02 | Completed | <name> | <date> |

**3. Walkthrough Results**

| Command | Result | Notes |
|---------|--------|-------|
| `uv run gz lint` | Pass | <summary> |
| `uv run gz test` | Pass | <N> tests |
| `uv run gz typecheck` | Pass | <summary> |
| `uv run gz validate --documents` | Pass | <summary> |
| `uv run mkdocs build --strict` | Pass | <summary> |
| <brief-specific commands> | <result> | <summary> |

**4. Documentation Alignment**

- [ ] Runbook updated
- [ ] Command docs current
- [ ] ADR document reflects final state

**5. Open Issues**

| Issue | Status | Disposition |
|-------|--------|-------------|
| #<N> | Open/Closed | Resolved by closeout / Deferred to ADR-X.Y.Z |

**6. Awaiting attestation.** Provide: "Completed", "Completed - Partial: [reason]", or "Dropped - [reason]".
```

---

## Error Recovery

| Failure Point | Action | Retry Limit |
|---------------|--------|-------------|
| `--ceremony` init fails (ADR not found) | Verify ADR path exists, check `gz adr status`, report to human | 0 — fix config |
| `--next` fails (step logic error) | Check `--ceremony-status` for current step. Report CLI error to human. Do not reimplement step logic. | 1 — retry after status check |
| Walkthrough command fails (non-zero exit) | Show the error output to the human. Diagnose: is it a code bug, config issue, or environment problem? Fix if possible, re-run the command. | 2 — fix and retry, then escalate to human |
| Walkthrough command produces unexpected output | Present output as-is to the human. Do not interpret. Let the human decide if it's acceptable. | 0 — human decides |
| `gz closeout ADR-X.Y.Z` pipeline fails | Show error. Check if quality gates failed (`gz lint`, `gz test`). Fix failing gates, re-run. | 2 — fix gates, then escalate |
| `gh issue close` fails | Verify issue exists and is open (`gh issue view <N>`). Retry with correct number. | 1 |
| `gz git-sync` fails | Do not proceed past the sync step. Diagnose: lint failures, test failures, merge conflicts. Fix and re-sync. | 2 — fix and retry, then escalate |
| Ceremony state corrupt | `--ceremony-status` shows inconsistent state. Re-initialize: `gz closeout ADR-X.Y.Z --ceremony` (resumes from last completed step). | 1 — re-init |
| Human is unresponsive at attestation | Do nothing. Wait. Do not infer attestation from silence. | 0 — wait indefinitely |

**On any unrecoverable failure:** Report the failure clearly to the human with the exact error output. Do not attempt to work around the CLI. The ceremony is paused — state is persisted in `.gzkit/ceremonies/` and can be resumed in a new session.

---

## Rejection Loop-Back

When the human requests corrections instead of attesting:

1. **Record the feedback** — note exactly what the human wants fixed
2. **Identify the scope** — is it a code fix (return to OBPI pipeline), a doc fix (fixable in ceremony), or an evidence gap (re-run walkthrough)?
3. **Execute the fix:**
   - **Code fix needed:** The ceremony cannot fix code. Advise the human to re-open the relevant OBPI via `gz-obpi-pipeline --from=verify`. Pause the ceremony.
   - **Doc fix needed:** Fix the documentation, run `uv run mkdocs build --strict`, re-present the docs alignment step.
   - **Evidence gap:** Re-run the relevant walkthrough commands, update the evidence template, re-present to the human.
4. **Re-present attestation** — after fixes, present the updated Evidence Summary Template and wait for the human's decision again.
5. **Bound the loop** — if the human rejects a third time, escalate: "Three correction cycles completed. Should we continue fixing, defer this ADR, or drop it?"

---

## Ceremony State

State is persisted at `.gzkit/ceremonies/<ADR-ID>.json` by the CLI. Structure:

| Field | Purpose |
|-------|---------|
| `adr_id` | ADR being closed out |
| `current_step` | CeremonyStep enum value |
| `completed_steps` | List of steps already finished |
| `started_at` | Ceremony initialization timestamp |
| `updated_at` | Last step advancement timestamp |
| `attestation` | Human's attestation text (null until Step 5) |
| `walkthrough_results` | Command → exit code + output summary |

**Resumption:** `gz closeout ADR-X.Y.Z --ceremony` checks for existing state and resumes from the last completed step. The agent does not need to re-run completed steps.

**Concurrent ceremonies:** Each ADR has its own state file. Multiple ADR ceremonies can run in separate sessions without interference.

---

## CLI Reference

> See references/cli-reference.md for the full command table.

---

## MUST Rules

1. **MUST** drive the ceremony through CLI commands (`--ceremony`, `--next`, `--attest`) — never reimplement step logic in prose
2. **MUST** present CLI output to the human without interpreting or claiming outcomes
3. **MUST** use the Evidence Summary Template before requesting attestation
4. **MUST** use only runbook/manpage-documented gzkit commands for the walkthrough
5. **MUST** run walkthrough commands one at a time, wait for acknowledgment
6. **MUST** wait for explicit human attestation before closing — acknowledgment is not attestation
7. **MUST** run `uv run gz closeout ADR-X.Y.Z` for the closeout pipeline — never manually record attestation
8. **MUST** review and close related GitHub Issues after attestation
9. **MUST** run `uv run gz git-sync --apply --lint --test` before `gh release create` (non-Foundation) and after ceremony completion
10. **MUST** follow the Rejection Loop-Back procedure when the human requests corrections

---

## MUST NOT Rules

1. **MUST NOT** manually reimplement ceremony step logic — the CLI state machine is authoritative
2. **MUST NOT** manually skip or add steps — the CLI handles Foundation skips and step ordering
3. **MUST NOT** claim outcomes or interpret evidence — present, do not conclude
4. **MUST NOT** use ad-hoc Python scripts, raw SQL, or heredoc code
5. **MUST NOT** flood multiple walkthrough commands without waiting for acknowledgment
6. **MUST NOT** infer attestation from silence, "looks good", or implicit approval
7. **MUST NOT** auto-close an ADR based on passing checks
8. **MUST NOT** advance past a failed walkthrough command without fixing or escalating
9. **MUST NOT** work around CLI errors by reimplementing step logic in prose
10. **MUST NOT** record "Completed - Partial" when the human wants fixes — that is a rejection, not a partial completion

---

## Anti-Patterns

### The Premature Close

The agent runs walkthrough commands, they all pass, and the agent says "ADR-X.Y.Z is complete." No — the agent does not decide completion. The human attests. Passing checks are evidence, not a verdict.

### The Silent Attestation

The human says "ok" or "looks good" after reviewing walkthrough output. The agent records `--attest "Completed"`. No — vague acknowledgment is not attestation. Ask explicitly: "What attestation would you like to record? Completed, Completed-Partial, or Dropped?"

### The Skipped Walkthrough

OBPIs all passed their pipelines, so the agent skips the walkthrough to "save time." No — the walkthrough is the human's ADR-level verification surface. Individual OBPI attestations do not substitute for ADR-level review.

### The Workaround

A CLI command errors and the agent reimplements the step in prose or with ad-hoc code. No — CLI errors are diagnostic signals. Fix the root cause or escalate. The ceremony state is persisted and can resume after fixes.

### The Dangling Ceremony

The agent completes attestation but does not sync the repo. The attestation exists in local state but is not committed. This is the closeout equivalent of the pipeline's "Premature Summary" — the governance action happened but was never persisted.

---

## ADR Folder Structure (Canonical)

> See references/folder-structure.md for the expected directory layout.

---

## References

- Ceremony code: `src/gzkit/commands/closeout_ceremony.py`
- Step renderers: `src/gzkit/commands/ceremony_steps.py`
- Audit protocol: `docs/governance/GovZero/audit-protocol.md`
- Gate definitions: `docs/governance/GovZero/charter.md`
- Release tag rule: `docs/governance/GovZero/adr-lifecycle.md`
- Runbook: `docs/user/operator_runbook.md`
- Pipeline skill (behavioral reference): `.gzkit/skills/gz-obpi-pipeline/SKILL.md`
