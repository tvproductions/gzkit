---
id: ADR-pool.operator-first-spec-workspace
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.operator-first-spec-workspace: Operator-First Spec Workspace

## Status

Pool

## Intent

Create a low-friction front door for change work that feels as approachable as
Spec Kit/Kiro/betterspec while preserving gzkit's heavier trust model.

The gap is not ceremony volume; it is entry ergonomics. Operators should be able
to start a change with a compact workspace that gathers problem statement,
requirements, plan, tasks, unchanged behavior, risks, and promotion route before
the full ADR/OBPI machinery expands. That workspace must be mechanically
witnessed and promotable, not a side-channel note.

**Target promotion kind:** feature candidate.

**Comparator signals:** GitHub Spec Kit's spec/plan/tasks loop, Kiro's
requirements/design/tasks UX, betterspec/specledger's persistent spec folders.

## Decision

When promoted, add a repo-owned change workspace surface with a command shape
similar to:

```bash
gz change start <slug>
gz change inspect <slug>
gz change promote <slug> --to pool|adr|obpi|ghi
gz change validate <slug>
```

The workspace should be compact enough for first contact but structured enough
to become governance evidence:

- `spec.md`: problem, goals, non-goals, user/operator value
- `requirements.md`: REQ rows, unchanged behavior, acceptance hints
- `plan.md`: candidate implementation path and scope boundaries
- `tasks.md`: task list with dependencies and wave hints
- `witness.json`: source command, author, timestamps, linked GHI/ADR/OBPI,
  comparator intake source if applicable, and validation status
- `receipts/`: optional ARB or command receipts generated while refining the
  workspace

Promotion should fail closed unless the destination is explicit. A workspace can
be discarded, filed as GHI, kept as pool backlog, promoted to active ADR, or
decomposed into OBPI work, but it must not become an untracked alternate source
of truth.

## Alternatives Considered

- **Use existing ADR scaffolding only.** Rejected. Direct ADR scaffolding is
  correct once scope is known, but comparator tools are stronger at the first
  10 minutes of shaping a change. gzkit needs that front door.
- **Adopt Spec Kit folder semantics verbatim.** Rejected. gzkit requires
  ledger/receipt/validator linkage; a generic spec folder is not enough.
- **Keep this inside `ADR-pool.change-isolation-workspace`.** Rejected as the
  whole home. Change isolation covers workspace boundaries. This ADR is about
  operator-first spec intake and promotion routing.
- **Make workspaces self-completing.** Rejected. Workspaces can stage evidence;
  completion remains owned by ADR/OBPI/GHI/commit routes.

## Promotion Triggers

- Operators repeatedly start with loose prose before an ADR/OBPI can be named.
- Comparator intake produces a lesson that needs staging before promotion.
- GHI triage identifies items that are too large for direct fix but too early
  for active ADR promotion.

## Related Destinations

- `ADR-pool.change-isolation-workspace`
- `ADR-pool.spec-delta-markers`
- `ADR-pool.pre-planning-interview`
- `ADR-pool.workflow-specification`
- `ADR-0.45.0-prefill-driven-authoring-scaffolding`

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
