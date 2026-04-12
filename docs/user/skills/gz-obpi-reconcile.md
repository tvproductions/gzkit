# /gz-obpi-reconcile

OBPI brief reconciliation — Audit briefs against evidence, fix stale metadata, sync ADR table, write ledger proof. Absorbs gz-obpi-audit and gz-obpi-sync.

---

## Purpose

`/gz-obpi-reconcile` exposes the canonical gz-obpi-reconcile workflow for operator invocation. **Single-command OBPI reconciliation** — audit briefs against actual evidence, fix stale metadata, sync the ADR table, and write ledger proof.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-obpi-reconcile/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-obpi-reconcile
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-obpi-reconcile/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-obpi-reconcile/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-obpi-reconcile/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-obpi-reconcile/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
