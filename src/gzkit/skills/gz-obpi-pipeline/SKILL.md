---
name: gz-obpi-pipeline
persona: pipeline-orchestrator
description: Use after a plan is approved, or when the operator says "execute OBPI-X.Y.Z-NN", to implement, verify and sync an OBPI.
category: obpi-pipeline
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-10-24
metadata:
  skill-version: "6.69.3"
model: sonnet
---

# gz-obpi-pipeline

Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

The canonical runtime launch surface is `uv run gz obpi pipeline`.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § I-001

Read
`docs/governance/acceptance-obligations.md` and
`docs/user/manpages/obpi-acceptance.md` before producing or importing these records.
This replaces authored standing-verdict lines as the acceptance authority;
historical verdicts remain unchanged. It does not authorize starting an OBPI:
the operator initiates this pipeline, and GHI corrective work retains its direct route.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § I-002

**Each stage's procedure is served by the runtime at stage entry.** `uv run gz obpi pipeline <OBPI-ID>` prints `Stage N procedure: <path> (sha256 <digest>)` for Stage 1 and again for every stage it enters; read that file before acting in the stage. The five files live in `references/` beside this skill, `stage-1-load-context.md` through `stage-5-sync-and-account.md`, rendered from the attested control inventory (`data/obpi_pipeline_control_inventory.json`), verbatim except where a row declares its rewording and reason; this body keeps the controls that apply at invocation or at every stage. A stage file that is missing, empty or altered refuses the launch before any marker is written (OBPI-0.35.0-17, Requirement 7; cut over in OBPI-0.35.0-20).

## Persona

**Active driver:** `pipeline-orchestrator` — read `.gzkit/personas/pipeline-orchestrator.md` and adopt its behavioral identity before executing this skill.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § I-005

## Persona Dispatch

The pipeline dispatches four subagent personas across its stages. Stage-2 implementer/spec-reviewer/quality-reviewer dispatch is documented procedurally below (§ Stage 2); the Stage-4 narrator dispatch is declared here:

Persona doctrine reference: ADR-0.0.11-persona-driven-agent-identity-frames (Validated). Runtime mapping: `src/gzkit/pipeline_dispatch.py` (`ROLE_PERSONA_MAP`).

---

## The Iron Law

```
THE PIPELINE IS NOT COMPLETE UNTIL STAGE 5 FINISHES.
```

Every stage flows into the next. No "stop and summarize" between stages. If you have not reached the end of Stage 5, you are not done — and violating the spirit of this rule is violating the rule.

### Rationalization Prevention

These thoughts mean STOP — you are about to break the pipeline:

| Thought | Reality |
|---------|---------|
| "The hook blocked me, I'll work around it" | Hook blocks are signals. Diagnose the cause. NEVER create marker files manually to bypass. |

---

## Work selection (operator rulings, verbatim canon)

- The active docs/governance/*-campaign-*.md plan governs work selection; handoffs and triage advise. Select its topmost unchecked item whose gate is met, subject to ascending feature-ADR order and operator-only OBPI initiation. Campaign amendments require operator ratification; ADR, OBPI, and GHI repair remain the work mechanisms.
- Work feature ADRs in ascending semver order: the lowest version with unlanded OBPIs is in flight. Do not work, author, or recommend a higher feature ADR ahead of it. The campaign selects work but cannot override that order. If campaign sequencing conflicts, semver governs; surface the conflict to the operator rather than silently resolving it. “One feature at a time” does not authorize swapping the order. An ADR in flight may be revised to take more OBPIs. The revision updates the document (an Intent amendment, a Decision item, a checklist item and the scorecard baseline) and the briefs table in the same change. A Validated ADR is not revised: scope missed from one enters the in-flight ADR as a repair assignment that cites the obligation it repairs. An item off the ADR's theme is labelled as such in the Intent amendment.

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § I-041

> Carried verbatim from root `AGENTS.md` § Operator Doctrine on 2026-09-17 (GHI #921); the corpus `.gzkit/corpus/AGENTS.md.jsonl` keeps the ruling's history.

## When to Use

- After exiting plan mode for an OBPI (plan approved, ready to execute)
- When the user says `execute OBPI-X.Y.Z-NN` or `complete OBPI-X.Y.Z-NN`
- When implementation is already done but governance stages (verify, ceremony, or
  sync) were skipped — use `--from=verify` or `--from=ceremony`

## When NOT to Use

- For planning — use Claude Code plan mode instead
- When no OBPI brief exists for the work
- For independently routed defect repairs: use AGENTS.md § Defect-fix routing and its GHI direct-repair authority. Do not start an OBPI merely to repair a defect. Corrections already owned by the active, operator-initiated OBPI stay in that pipeline regardless of patch size.

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
│  Stage 4: PRESENT EVIDENCE   (human gate — universal)        │
│  ├─ WAIT for human attestation, then Stage 5.                │
│  Stage 5: SYNC AND ACCOUNT   (autonomous)                   │
│  └─ Pipeline complete. NOW you may report status.            │
└──────────────────────────────────────────────────────────────┘

Stage 4 = HUMAN GATE (wait for attestation) — universal per ADR-0.0.36
```

---

## Error Recovery

**Lock bracket:** Lock is claimed at Stage 1 and surrendered by `gz obpi complete` at Stage 5, or by an abort surrender.

### Abort surrender

On an abort the lock is surrendered with a recorded category (GHI #1167):

```bash
uv run gz obpi lock release {OBPI-SLUG} --abandon <category>:<reason>
```

A release without `--abandon` exits 3 and leaves the lock in place
(`.gzkit/rules/token-block-discipline.md` § Sub-Invariant 5). `--force` waives
the ownership check only. A session handoff is not an exchange record and
discharges nothing. The categories are a closed enum, listed in
`docs/user/manpages/obpi-lock-release.md`; if none describes the abort, do not
pick one that misdescribes it. Leave the lock held, name it in the handoff and
report it to the operator

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-024

**Handoff creation:** On any abort, after the surrender, run `/gz-session-handoff` to preserve context for the next session.

---

## Blocked on the Operator (GHI #887)

**When the next legitimate action is a human's, say so in the ledger and stop.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-026

```bash
uv run gz obpi block {OBPI-SLUG} \
  --reason "<what cannot proceed without a human>" \
  --next-action "<the concrete decision the operator owes>"
```

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-027

The operator
clears it with their own words:

```bash
uv run gz obpi unblock {OBPI-SLUG} --ruling "<decision>" --operator "<who>"
```

**No attestor is required to record a block.**

> Rationale: docs/governance/obpi-pipeline-control-rationale.md § T-030

---

## Evidence Capture

> See references/evidence-capture.md for the full stage-by-stage evidence table.

---

## Plan-Audit-Receipt Contract

> See references/plan-audit-receipt-contract.md for the receipt JSON schema and contract details.

---

## Parallel Execution

Use one writer per governed checkout. Read-only investigation may run independently.
Only the operator initiates OBPI work; separate sessions do not grant initiation.
Capture the contract and input components before review and verify applicability
before consuming it. Sequence shared acceptance/schema writes outside review windows.
If another run changes the subject, identify affected evidence before continuing.
Never stash, pop, reset, revert, or sync another active run's work to clean the tree.

All OBPIs require per-OBPI human attestation (universal per ADR-0.0.36).

---

## Relationship to Existing Skills

| CLI Command / Skill | Role in Pipeline |
|---------------------|-----------------|
| `gz obpi lock claim/release` | Stage 1 claim, Stage 5 release, abort release (`--force`) |
| `/gz-plan-audit` | Pre-pipeline — runs in plan mode, produces receipt |
| `gz obpi complete` | Stage 5 atomic completion (attestation + brief + receipt) |
| `gz obpi sync` | Stage 5 confirmation — receipt and brief agree |
| `/gz-session-handoff` | Error recovery — preserves context on abort |

---

## Completion Contract

### Anti-Pattern: Hook Bypass

If a pipeline hook blocks a write, that means the pipeline is not active or evidence is missing. The correct response is to diagnose the cause — NOT to manually create marker files or ledger entries to bypass the hook. Manually creating files to bypass hooks defeats the entire enforcement mechanism.

---

## Design Notes

> See references/design-notes.md for architectural context, hook enforcement details, and AirlineOps lineage.

---

## Related

- OBPI Acceptance Protocol: `AGENTS.md` § OBPI Acceptance Protocol
- Plan audit: `.claude/skills/gz-plan-audit/SKILL.md`
- Session handoff: `.gzkit/skills/gz-session-handoff/SKILL.md`
- Governance workflow: `docs/user/concepts/workflow.md`
- Runbook: `docs/user/runbook.md`
- Transaction contract: `docs/governance/GovZero/obpi-transaction-contract.md`

## Related ADRs

- **ADR-0.0.19** — Pre-execution reasoning walkthrough. The Stage 1→2
  Justification Gate routes a plan with an ambiguous scope boundary, an
  unresolved integration point or an unread surface into the `gz-justify`
  walkthrough before implementation begins.
