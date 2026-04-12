# /gz-adr-emit-receipt

Emit ADR receipt events with scoped evidence payloads. Use when recording completed or validated accounting events.

---

## Purpose

`/gz-adr-emit-receipt` exposes the canonical gz-adr-emit-receipt workflow for operator invocation. Operate the gz adr emit-receipt command surface as a reusable governance workflow.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-adr-emit-receipt/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-adr-emit-receipt
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-adr-emit-receipt/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-adr-emit-receipt/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-adr-emit-receipt/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-adr-emit-receipt/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
