# /gz-plan-audit

Pre-flight alignment audit — verify ADR intent, OBPI brief scope, and plan are aligned before implementation begins. Use when exiting plan mode, before starting implementation, or to catch scope drift between ADR intent and the active OBPI brief.

---

## Purpose

`/gz-plan-audit` exposes the canonical gz-plan-audit workflow for operator invocation. Pre-flight alignment audit that catches misalignment before implementation begins. The operator runs this after plan mode produces a plan, verifying three artifacts agree:

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-plan-audit/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-plan-audit
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-plan-audit/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-plan-audit/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-plan-audit/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-plan-audit/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
