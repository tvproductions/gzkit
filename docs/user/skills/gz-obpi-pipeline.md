# /gz-obpi-pipeline

Post-plan OBPI execution pipeline — implement, verify, present evidence, and sync after a plan is approved. Use after exiting plan mode for an OBPI, when the user says "execute OBPI-X.Y.Z-NN", or to enforce governance on already-implemented work via --from=verify or --from=ceremony.

---

## Purpose

`/gz-obpi-pipeline` exposes the canonical gz-obpi-pipeline workflow for operator invocation. Post-plan execution pipeline: implement the approved plan, verify, present evidence, and sync.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-obpi-pipeline/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

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
| `.github/skills/gz-obpi-pipeline/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
