# /gz-state

Query artifact relationships and readiness state. Use when reporting lineage or artifact graph status.

---

## Purpose

`/gz-state` exposes the canonical gz-state workflow for operator invocation. It reads the ledger's artifact graph — relationships, attestation and readiness — and, with `--repair`, makes two repairs from the ledger: it sets OBPI brief frontmatter status, and it restores or rebuilds a missing pipeline marker file of the run in flight that was launched last. It reports the frontmatter fields it changed, each marker file it restored, each marker it rebuilt and each run it declined with the reason; `--repair --json` carries the last three in a `markers` object (`rebuilt`, `restored`, `declined`).

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-state/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-state
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-state/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-state/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-state/SKILL.md` | Codex mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
