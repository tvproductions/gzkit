---
name: gz-obpi-pipeline
description: Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. Use after exiting plan mode for an OBPI, when the user says "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-03-16
---

# gz-obpi-pipeline

Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

Planning happens in native plan mode. This pipeline picks up **after** the plan is approved and enforces the governance stages that get lost in freeform execution.

The canonical runtime launch surface is now `uv run gz obpi pipeline`. The CLI
runtime, generated hook surfaces, and reminder messages now share the same
runtime engine in `src/gzkit/pipeline_runtime.py`. This skill remains the
wrapper/operator ritual around that runtime rather than a second stage engine.

---

## When to Use

- After exiting plan mode for an OBPI (plan approved, ready to execute)
- When the user says "execute OBPI-X.Y.Z-NN" or "complete OBPI-X.Y.Z-NN"
- When implementation is done but governance stages (verify, ceremony, sync) were skipped — use `--from=verify` or `--from=ceremony`

## When NOT to Use

- For planning — use plan mode instead
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
│  Stage 3: VERIFY             (autonomous)                    │
│  Stage 4: PRESENT EVIDENCE   (mode-dependent — see below)   │
│  Stage 5: SYNC               (autonomous)                   │
└──────────────────────────────────────────────────────────────┘

Normal mode:    Stage 4 = HUMAN GATE (wait for attestation)
Exception mode: Stage 4 = SELF-CLOSE (record evidence, proceed)
```

### Stage 1: Load Context

1. Read `.claude/plans/.plan-audit-receipt.json` to find the approved plan
   - If receipt exists and OBPI matches: load the plan file from `.claude/plans/`, extract implementation steps
   - If receipt verdict is `FAIL`: **abort** — plan did not pass audit
   - If no receipt found: **warn** but proceed (user may have planned informally or implemented without formal plan)
2. Locate the OBPI brief:
   - `docs/design/adr/**/obpis/OBPI-{id}-*.md`
   - `docs/design/adr/**/briefs/OBPI-{id}-*.md`
3. Extract: objective, requirements, allowed/denied paths, acceptance criteria, lane, verification commands
4. Identify parent ADR and lane inheritance
5. Determine execution mode: Read parent ADR for `## Execution Mode` section.
   - If "Exception (SVFR)" found → set mode=exception.
   - If absent or "Normal" → set mode=normal.
6. Check for existing handoffs: `docs/design/adr/**/handoffs/*.md` (resume if fresh)
7. Claim OBPI lock via `/gz-obpi-lock claim {OBPI-ID}`
8. Create pipeline marker: Write `.claude/plans/.pipeline-active-{OBPI-ID}.json` with
   `{"obpi_id": "<the-obpi-id>", "started_at": "<ISO-8601 timestamp>", "mode": "normal|exception"}`.
   This unblocks the pipeline-gate PreToolUse hook for src/ and tests/ writes.
8. Map brief's allowed paths to instruction files and surface constraint preamble.

**Abort if:** Brief not found, brief status already `Completed`, receipt verdict is `FAIL`.

**On any abort:** Release lock if claimed, run `/gz-session-handoff` to preserve context.

### Stage 2: Implement (skipped by `--from=verify` or `--from=ceremony`)

1. Create task list from plan steps
   - Normal mode: Last task MUST be "Present OBPI Acceptance Ceremony"
   - Exception mode: Last task MUST be "Record OBPI Evidence and Self-Close"
2. Follow the approved plan step by step
3. Write code with tests (unittest, coverage >= 40%)
4. One step at a time — show output after each
5. Run `uv run ruff check . --fix && uv run ruff format .` after code changes
6. Run `uv run -m unittest -q` after implementation

**Abort if:** Tests fail after 2 fix attempts. Create handoff, release lock, and stop.

### Stage 3: Verify (skipped by `--from=ceremony`)

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

### Stage 4: Present Evidence

**Mode determines behavior at this stage.**

#### Normal Mode — HUMAN GATE

**Trigger:** "Present OBPI Acceptance Ceremony" task becomes next pending. Mark `in_progress`.

1. **Value narrative** — What problem existed before? What capability exists now? (2-3 sentences)
2. **Key proof** — One concrete usage example the reviewer can mentally execute
3. **Evidence** — Verification outputs, test results, files changed
4. **Wait for attestation** — Do NOT proceed until human responds "Accepted"/"Completed"

Do NOT mark ceremony task `completed` until attestation is received.

**Human rejects:** Record feedback, return to Stage 2 with corrections.

#### Exception Mode — SELF-CLOSE

**Trigger:** "Record OBPI Evidence and Self-Close" task becomes next pending. Mark `in_progress`.

1. **Value narrative** — Same content as Normal mode. Recorded to ledger.
2. **Key proof** — Same content as Normal mode. Recorded to ledger.
3. **Evidence** — Same content as Normal mode. Recorded to ledger.
4. **Self-close** — Record `attestation_type: "self-close-exception"` in ledger. Proceed to Stage 5.

Evidence is full-fidelity. Human reviews at ADR closeout.

### Stage 5: Sync

After attestation (Normal) or self-close (Exception):

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

2. Run guarded repo sync: `uv run gz git-sync --apply --lint --test`
   - Abort if sync fails or leaves unresolved divergence/blockers.
3. Run `/gz-obpi-audit {OBPI-ID}` to record full evidence ledger entry
4. Update brief: check all criteria boxes, add evidence section, set status to `Completed`
   - (Hook `obpi-completion-validator.py` enforces evidence requirements)
5. Run `/gz-obpi-sync {ADR-ID}` to propagate status to ADR table
6. Release OBPI lock via `/gz-obpi-lock release {OBPI-ID}`
7. Remove `.claude/plans/.pipeline-active-{OBPI-ID}.json` if it was created.
8. Remove `.claude/plans/.pipeline-active.json` only when it still points at
   the same OBPI as the per-OBPI marker.
9. Create handoff if more OBPIs remain for the ADR

---

## Error Recovery

| Failure Point | Action |
|---------------|--------|
| Brief not found | Report error, release lock, stop |
| Receipt verdict FAIL | Report audit failure, release lock, stop |
| No receipt found | Warn and proceed (informal planning is allowed) |
| Tests fail during implementation | Attempt fix (2 tries), then handoff + release lock |
| Verification fails | Attempt fix (1 try), then handoff + release lock |
| Human rejects attestation | Record feedback, return to Stage 2 with corrections |

**Lock bracket:** Lock is claimed at Stage 1 and released at Stage 5 AND on any abort/handoff. No orphaned locks.

**Handoff creation:** On any abort, run `/gz-session-handoff` to preserve context for the next session.

---

## Evidence Capture

Each stage records evidence to the OBPI audit ledger:

| Stage | Evidence Written |
|-------|-----------------|
| Stage 1 | Brief parsed, plan file loaded, lock claimed |
| Stage 2 | Files changed, tests added |
| Stage 3 | Verification outputs (pass/fail) |
| Stage 4 | Attestation text + timestamp |
| Stage 5 | Attestation ledger entry (Step 1), full evidence ledger entry (Step 3), lock released |

---

## Plan-Audit-Receipt Contract

The plan-audit-receipt (`.claude/plans/.plan-audit-receipt.json`) is the handoff artifact linking plan mode to this pipeline:

```json
{
  "obpi_id": "OBPI-0.11.0-05",
  "timestamp": "2026-02-14T12:00:00Z",
  "verdict": "PASS",
  "plan_file": "my-plan-name.md",
  "gaps_found": 0
}
```

- Written by the `plan-audit-gate.py` hook when exiting plan mode
- Read by Stage 1 to locate the approved plan
- **verdict = PASS**: plan is aligned with OBPI brief — proceed
- **verdict = FAIL**: plan has alignment gaps — abort and resolve

---

## Parallel Execution (Exception Mode)

Multiple independent OBPIs within the same ADR can run this pipeline concurrently in separate agent sessions when Exception mode is granted. Requirements:

1. ADR has `## Execution Mode: Exception (SVFR)` section (granted at ADR Defense)
2. OBPIs have non-overlapping allowed paths
3. Each session claims its OBPI via `/gz-obpi-lock`
4. Sync operations (Stage 5) are atomic per-brief

In Normal mode, OBPIs run sequentially with per-OBPI human attestation.

---

## Relationship to Existing Skills

| Skill | Role in Pipeline |
|-------|-----------------|
| `/gz-obpi-lock` | Stage 1 claim, Stage 5 release, abort release |
| `/gz-plan-audit` | Pre-pipeline — runs in plan mode, produces receipt |
| `/gz-obpi-audit` | Stage 5 ledger recording |
| `/gz-obpi-sync` | Stage 5 ADR table sync |
| `/gz-session-handoff` | Error recovery — preserves context on abort |

---

## Design Notes

**Hooks do the hard enforcement.** This pipeline is orchestration narrative, not a security boundary. The real gates are:

- `plan-audit-gate.py` — enforces plan ↔ OBPI alignment at plan-mode exit
- `obpi-completion-validator.py` — enforces evidence requirements when marking briefs Completed

The pipeline's value is **sequencing and governance memory** — ensuring the ceremony and sync stages happen, which is exactly what gets lost in freeform execution.

In gzkit, `uv run gz git-sync --apply --lint --test` is the canonical Stage 5
sync ritual. Do not substitute ad-hoc git commands.

---

## Related

- OBPI Acceptance Protocol: `AGENTS.md` § OBPI Acceptance Protocol
- Plan audit: `.claude/skills/gz-plan-audit/SKILL.md`
- Session handoff: `docs/governance/GovZero/session-handoff-obligations.md`
- Audit protocol: `docs/governance/GovZero/audit-protocol.md`
