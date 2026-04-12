# /gz-prd

Create product requirement artifacts. Use when defining or revising project-level intent before ADR planning.

---

## Purpose

`/gz-prd` exposes the canonical gz-prd workflow for operator invocation. Operate the gz prd command surface as a reusable governance workflow.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-prd/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-prd
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-prd/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-prd/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-prd/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-prd/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
