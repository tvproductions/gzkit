# Pipeline Reference Material

Error recovery, evidence capture, contracts, design notes, and related skill mapping.
Referenced by SKILL.md as needed. Not required for normal stage execution.

---

## Error Recovery

| Failure Point | Action |
|---------------|--------|
| Brief not found | Report error, release lock, stop |
| Receipt verdict FAIL | Report audit failure, release lock, stop |
| No receipt found (full run) | STOP — enter plan mode, get approval, then resume pipeline |
| No receipt found (`--from` set) | Proceed — user is resuming a partial pipeline |
| Tests fail during implementation | Attempt fix (2 tries), then handoff + release lock |
| Verification fails | Attempt fix (1 try), then handoff + release lock |
| Human rejects attestation | Record feedback, return to Stage 2 with corrections |
| `git sync` fails or repo remains unsynced | Stop before completion accounting and repair blockers |

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
| Stage 5 | Attestation ledger entry (Step 1), audit entry (Step 2), brief updated (Step 3), git-sync #1 (Step 7), completion receipt with clean anchor (Step 8), reconcile (Step 9), git-sync #2 (Step 11) |

---

## Plan-Audit-Receipt Contract

The plan-audit-receipt (`.claude/plans/.plan-audit-receipt.json`) is the handoff artifact linking plan mode to this pipeline:

```json
{
  "obpi_id": "OBPI-0.14.0-05",
  "timestamp": "2026-03-16T12:00:00Z",
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

- AirlineOps is the behavioral reference implementation for this pipeline.
- gzkit adapts the control surface to its native command vocabulary
  (`uv run gz lint`, `uv run gz test`, etc.) and repository structure.
- **Hooks do the hard enforcement.** This pipeline is orchestration narrative, not a security boundary. The real gates are:
  - `plan-audit-gate.py` — enforces plan ↔ OBPI alignment at plan-mode exit
  - `obpi-completion-validator.py` — enforces evidence requirements when marking briefs Completed
  - `pipeline-gate.py` — blocks src/tests writes until pipeline is active
- The pipeline's value is **sequencing and governance memory** — ensuring the ceremony and sync stages happen, which is exactly what gets lost in freeform execution.
- `src/gzkit/pipeline_runtime.py` is the canonical shared runtime used
  by the CLI and generated pipeline hooks.
- In gzkit, `uv run gz git-sync --apply --lint --test` is the canonical Stage 5
  sync ritual. Do not substitute ad-hoc git commands.

---

## Related

- OBPI Acceptance Protocol: `AGENTS.md` § OBPI Acceptance Protocol
- Plan audit: `.claude/skills/gz-plan-audit/SKILL.md`
- Session handoff: `.gzkit/skills/gz-session-handoff/SKILL.md`
- Governance workflow: `docs/user/concepts/workflow.md`
- Runbook: `docs/user/runbook.md`
- Transaction contract: `docs/governance/GovZero/obpi-transaction-contract.md`
