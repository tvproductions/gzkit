# /gz-adr-sync

End-to-end ADR governance sync — discover `@covers` evidence, reconcile OBPI ledger state, and register ADR files.

---

## Purpose

`/gz-adr-sync` is the unified ADR governance sync skill. It runs across all three governance layers in trust order:

- **Layer 1** — discover `@covers` test annotations for ADRs
- **Layer 2** — reconcile OBPI evidence state against the ledger
- **Layer 3** — register ADR files and refresh the status view

It absorbs the formerly separate `/gz-adr-autolink` (Layer 1) and `/gz-adr-recon` (Layer 2) skills, which are now archived.

## When to Use

- After multi-session work when status drift is suspected
- After adding, moving, or importing pool ADRs
- Before requesting ADR closeout
- To investigate evidence gaps for a specific ADR

## Modes

### Full sync

```text
/gz-adr-sync
```

Runs all three layers globally. Use before closeout or after structural ADR changes.

### Scoped reconciliation

```text
/gz-adr-sync ADR-<X.Y.Z>
```

Runs Layer 1 and Layer 2 phases against a single ADR. Use for targeted investigation of one ADR's evidence and OBPI state.

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-adr-sync/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). Follow the agent-facing instructions in that file for the exact execution protocol, phases, and evidence requirements.

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-adr-sync/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-adr-sync/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-adr-sync/SKILL.md` | Codex mirror | Read |

## Archived predecessors

| Archived skill | Absorbed as |
|---|---|
| `/gz-adr-autolink` | Layer 1 phase (evidence gathering) |
| `/gz-adr-recon` | Layer 2 phase (ledger reconciliation) |
| `/gz-register-adrs` | Layer 3 phase (registration) |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [/gz-obpi-sync](gz-obpi-sync.md) | OBPI-level reconciliation (run before this skill) |
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
