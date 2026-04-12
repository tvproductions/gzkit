# /gz-obpi-lock

Claim or release OBPI-level work locks for multi-agent coordination. Use when claiming an OBPI before starting work, releasing a lock after completing or abandoning work, or checking which OBPIs are currently claimed by agents.

---

## Purpose

`/gz-obpi-lock` exposes the canonical gz-obpi-lock workflow for operator invocation. Claim or release OBPI-level work locks for multi-agent coordination.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-obpi-lock/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-obpi-lock
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-obpi-lock/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-obpi-lock/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-obpi-lock/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-obpi-lock/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
