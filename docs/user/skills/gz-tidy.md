# /gz-tidy

Run maintenance checks and cleanup routines. Use for repository hygiene and governance maintenance operations.

---

## Purpose

`/gz-tidy` exposes the canonical gz-tidy workflow for operator invocation. Operate the gz tidy command surface as a reusable governance workflow. Includes Claude surface self-heal via `@claude-code-guide` when running in Claude Code.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-tidy/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-tidy
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-tidy/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-tidy/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-tidy/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-tidy/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
