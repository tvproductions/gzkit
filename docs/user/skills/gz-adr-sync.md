# /gz-adr-sync

Reconcile ADR files with ledger registration and status views.

---

## Purpose

`/gz-adr-sync` exposes the canonical gz-adr-sync workflow for operator invocation. Sync ADR governance state using current `gz` capabilities.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-adr-sync/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-adr-sync
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-adr-sync/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-adr-sync/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-adr-sync/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-adr-sync/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
