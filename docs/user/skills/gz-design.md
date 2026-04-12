# /gz-design

Collaborative design dialogue that produces GovZero ADR artifacts. Use when exploring a new feature, capability, or architectural change before implementation — replaces superpowers brainstorming for this project. Triggers on "design X", "let's design", "brainstorm X", "I want to build X", "gz-design".

---

## Purpose

`/gz-design` exposes the canonical gz-design workflow for operator invocation. Collaborative design dialogue that exits into GovZero artifacts — not superpowers specs, not flat plans.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-design/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-design
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-design/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-design/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-design/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-design/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
