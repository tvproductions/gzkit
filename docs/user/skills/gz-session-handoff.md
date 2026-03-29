# /gz-session-handoff

Create and resume session handoff documents that preserve agent context across
engineering sessions.

---

## Purpose

When an agent pauses work on an ADR or OBPI, the context of what was done, what
decisions were made, and what comes next is lost when the session ends.
`/gz-session-handoff` solves this by creating structured handoff documents that
capture the full session state — so that a resuming agent (or the same agent in
a new session) can continue without re-deriving context from scratch.

## When to Use

Invoke `/gz-session-handoff` in these situations:

- **Pausing long-running work** — when an OBPI implementation spans multiple
  sessions, create a handoff before ending the session.
- **Pipeline abort** — when `/gz-obpi-pipeline` encounters a blocker and aborts,
  it automatically creates a handoff to preserve recovery context.
- **Agent rotation** — when handing work from one agent to another (e.g.,
  Claude Code to Codex), the handoff document bridges the context gap.
- **Resuming work** — at the start of a new session, resume from the most
  recent handoff to pick up where the previous session left off.

This skill operates at session boundaries in the
[daily workflow](../concepts/workflow.md). Handoffs are stored in the ADR
package alongside the work they describe.

## What to Expect

### CREATE Mode

Creates a handoff document at `{ADR-package}/handoffs/{timestamp}-{slug}.md`
with seven required sections:

1. **Current State Summary** — what was done and where the work stands.
2. **Important Context** — architectural constraints, non-obvious dependencies.
3. **Decisions Made** — decisions with rationale and rejected alternatives.
4. **Immediate Next Steps** — ordered list of 3-5 concrete next actions.
5. **Pending Work / Open Loops** — deferred items, blockers, discovered work.
6. **Verification Checklist** — commands and checks for the resuming agent.
7. **Evidence / Artifacts** — file paths produced during the session.

The document is validated: no placeholders (TBD, TODO), no secrets, all
referenced file paths must exist. Runtime is a few seconds.

### RESUME Mode

Discovers the most recent handoff for an ADR, classifies its staleness, and
presents the first next step for immediate action:

| Staleness | Age | Action |
|-----------|-----|--------|
| Fresh | < 24h | Resume directly |
| Slightly Stale | 24-72h | Resume with caution |
| Stale | 72h-7d | Human verification required |
| Very Stale | > 7d | Consider re-creating |

If the handoff has a `continues_from` link, the full chain of predecessor
handoffs is loaded to reconstruct session lineage.

## Invocation

```text
/gz-session-handoff create ADR-0.24.0 --slug template-validation
/gz-session-handoff resume ADR-0.24.0
/gz-session-handoff resume ADR-0.24.0 --file handoffs/20260329T120000Z-template-validation.md
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| `create` / `resume` | yes | Operation mode |
| `ADR-X.Y.Z` | yes | Parent ADR identifier |
| `--slug` | create only | Short descriptor for the handoff filename |
| `--obpi` | no | Scope handoff to a specific OBPI |
| `--file` | resume only | Resume a specific handoff instead of the newest |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/gz-session-handoff/SKILL.md` | Agent execution instructions | Read |
| `.claude/skills/gz-session-handoff/assets/handoff-template.md` | Template for handoff documents | Read |
| `.claude/skills/gz-session-handoff/assets/staleness-rules.md` | Staleness classification rules | Read |
| `{ADR-package}/handoffs/*.md` | Handoff documents for an ADR | Read/Write |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-obpi-pipeline`](gz-obpi-pipeline.md) | Creates handoffs automatically on pipeline abort |
| [`/gz-obpi-lock`](gz-obpi-lock.md) | Lock state is preserved in handoff context |
| [`/gz-adr-create`](gz-adr-create.md) | Creates the ADR package where handoffs are stored |
| [`/gz-closeout`](gz-closeout.md) | Closeout may reference handoff chain as evidence |
