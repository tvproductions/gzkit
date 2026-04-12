# /gz-gates

Run lane-required gates or specific gate checks. Use when verifying governance gate compliance for an ADR.

---

## Purpose

`/gz-gates` exposes the canonical gz-gates workflow for operator invocation. Operate the gz gates command surface as a reusable governance workflow.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-gates/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-gates
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-gates/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-gates/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-gates/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-gates/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
