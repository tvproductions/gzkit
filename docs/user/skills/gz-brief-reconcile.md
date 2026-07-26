# /gz-brief-reconcile

Reconcile an OBPI brief against current project state and optionally write operator-attested amendments. Use when a brief's allowlist, discovery checklist, verification verbs, REQ count, or citation tuples may have drifted from reality.

---

## Purpose

`/gz-brief-reconcile` exposes the canonical gz-brief-reconcile workflow for operator invocation. It wraps the `gz obpi brief-drift` CLI verb over the OBPI-0.0.37-05 reconciliation engine to detect brief↔reality drift across five dimensions (invariant CIC-2) and, under `--apply --attestor`, write operator-attested amendments.

## When to Use

Invoke this skill when the task described above matches your current workflow stage. The governance runbook at `docs/governance/governance_runbook.md` lists the canonical workflows and points at this skill where appropriate.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-brief-reconcile/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, stages, and evidence requirements.

## Invocation

```text
/gz-brief-reconcile
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `<OBPI-ID>` | yes | OBPI identifier to reconcile |
| `--apply` | no | Write operator-attested amendments (requires `--attestor`) |
| `--attestor "<name>"` | with `--apply` | Attesting human's full name |
| `--dry-run` | no | Preview amendments without writing |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-brief-reconcile/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-brief-reconcile/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-brief-reconcile/SKILL.md` | Codex mirror | Read |
| `.github/skills/gz-brief-reconcile/SKILL.md` | Copilot mirror | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`gz obpi brief-drift`](../manpages/brief-reconcile.md) | Underlying CLI command |
| [`/gz-obpi-reconcile`](gz-obpi-reconcile.md) | Reconciles OBPI runtime state (distinct from brief-content) |
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
