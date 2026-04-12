# /gz-validate

Validate governance artifacts against schema rules. Use when checking manifest, ledger, document, or surface validity.

---

## Purpose

`/gz-validate` exposes the canonical gz-validate workflow for operator invocation. Operate the gz validate command surface as a reusable governance workflow.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-validate/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-validate
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-validate/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-validate/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-validate/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-validate/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
