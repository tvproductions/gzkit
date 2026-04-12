# /gz-adr-promote

Promote a pool ADR into canonical ADR package structure. Use when moving a backlog item (ADR-pool.*) into an active, versioned ADR.

---

## Purpose

`/gz-adr-promote` exposes the canonical gz-adr-promote workflow for operator invocation. Operate the gz adr promote command surface to transition pool (backlog) ADRs into versioned, executable ADR packages with preserved ledger lineage.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-adr-promote/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-adr-promote
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-adr-promote/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-adr-promote/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-adr-promote/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-adr-promote/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
