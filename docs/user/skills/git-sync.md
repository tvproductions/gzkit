# /git-sync

Run the guarded repository sync ritual with lint/test gates.

---

## Purpose

`/git-sync` exposes the canonical git-sync workflow for operator invocation. Run the guarded repository sync ritual with lint/test gates.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/git-sync/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/git-sync
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/git-sync/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/git-sync/SKILL.md` | Claude mirror | Read |
| `.agents/skills/git-sync/SKILL.md` | Codex mirror | Read |
| `.github/skills/git-sync/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
