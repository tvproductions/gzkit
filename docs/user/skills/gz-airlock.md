# /gz-airlock

Cross the airlock membrane — the entry/exit gate every unit of work passes through (ADR-0.33.0). Use to inspect a target's seam-map before touching it (`gz airlock in`), account for what a transit disturbed (`gz airlock out`), or make a governed ad-hoc reconnaissance entry with light repair at most (`gz permitted-entry`). Diagnostic-only; never writes L1 canon.

---

## Purpose

`/gz-airlock` exposes the canonical gz-airlock workflow for operator invocation. Wield the airlock's operator-facing doors (ADR-0.33.0) to inspect a target's two-layer seam-map on the way in, account for drift on the way out, and cross the membrane for ad-hoc reconnaissance — so every entry into the project ecosystem leaves an accountable transit record.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-airlock/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-airlock
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-airlock/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-airlock/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-airlock/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-airlock/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [`gz airlock` manpage](../manpages/airlock.md) | Command reference |
| [`gz permitted-entry` manpage](../manpages/permitted-entry.md) | Command reference |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
