# /gz-adr-status

Show the ADR table for summary requests, or show focused lifecycle and OBPI detail for one ADR.

---

## Purpose

`/gz-adr-status` exposes the canonical gz-adr-status workflow for operator invocation. Show ADR status using the current `gz` command surface.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-adr-status/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-adr-status
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-adr-status/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-adr-status/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-adr-status/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-adr-status/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
