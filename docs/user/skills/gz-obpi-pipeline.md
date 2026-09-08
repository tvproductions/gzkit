# /gz-obpi-pipeline

Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. Use after exiting plan mode for an OBPI, when the user says "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.

---

## Purpose

`/gz-obpi-pipeline` exposes the canonical gz-obpi-pipeline workflow for operator invocation. Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

Reviewers receive the execution records supporting each requirement, including
observed failure evidence where claimed. Stage 4 presents one current proof table
and supplies that packet to independent review. Review checks whether the evidence
supports the requirement; a reproducing transcript or coverage inventory alone
does not establish that relationship.

The runtime now retains these obligations and judgments through
[`gz obpi acceptance`](../manpages/obpi-acceptance.md). Initialize once, execute
requirement proof, and import each independent review from its actual ARB
execution output. Stage 2 requires current spec and quality approval; Stage 4
adds adversarial approval. Intermediate tasks may inspect their Stage-2 REQ
scope, while stage advancement requires the complete canonical population.
The existing ledger-declared single-driver mode retains its Stage-2 reviewer
exception; executed proof, findings, and Step-4b approval remain required.
Step 4a can generate the independent review's input once Stage-2 proof is ready.
Pending Step-4b closure keeps that packet non-attestable, even when packet
generation exits zero. The ceremony waits for both proof and review readiness.
See [acceptance obligations](../../governance/acceptance-obligations.md) for the
finding and closure lifecycle, conservative freshness boundary, and judgment limits.

Findings return through implementation and verification with their full repair
obligation preserved. Follow-up review verifies the correction and affected
requirements. Auxiliary diagnostics do not automatically become acceptance
requirements, and findings remain relevant when they expose missing required
proof regardless of where they were discovered. Authorized corrections continue
within the initiated OBPI; human completion attestation remains required.
Historical standing-verdict prose remains history. Current readiness derives
from proof identities, explicit independent approvals, and verified closure.

## Invocation

```text
/gz-obpi-pipeline
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-obpi-pipeline/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-obpi-pipeline/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-obpi-pipeline/SKILL.md` | Codex mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
