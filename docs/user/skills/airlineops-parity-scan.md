# /airlineops-parity-scan

Run a repeatable governance parity scan between ../airlineops (canon) and gzkit (extraction).

---

## Purpose

`/airlineops-parity-scan` exposes the canonical airlineops-parity-scan workflow for operator invocation. Run a repeatable governance parity scan between `../airlineops` (canon) and gzkit (extraction).

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/airlineops-parity-scan/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/airlineops-parity-scan
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/airlineops-parity-scan/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/airlineops-parity-scan/SKILL.md` | Claude mirror | Read |
| `.agents/skills/airlineops-parity-scan/SKILL.md` | Codex mirror | Read |
| `.github/skills/airlineops-parity-scan/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
