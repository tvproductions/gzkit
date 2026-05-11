---
id: ADR-pool.canonical-vs-runtime-separation
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.canonical-vs-runtime-separation: Canonical vs. Runtime Separation

## Status

Pool

## Intent

Separate canonical-instruction content from runtime-state (logs, receipts,
proofs, per-run artifacts) at the directory level. Today gzkit mixes
both classes within the same `<slug>/` directories:

- `.gzkit/chores/<slug>/CHORE.md` (canonical instruction) lives alongside
  `.gzkit/chores/<slug>/proofs/CHORE-LOG.md` (runtime state) and
  `.gzkit/chores/<slug>/proofs/<artifact>` (run-time evidence).
- The same pattern is likely to appear for any future canonical surface
  that grows runtime-state artifacts (skills with execution logs, rules
  with audit-receipt records, etc.).

The operator framing surfaced on 2026-05-11: *"keeping logs and receipts
with the instructions code (executables vs. outcomes/receipts) may be a
design flaw."* This pool ADR parks the resolution to that framing.

The proposed shape (to be ratified on promotion):

```
.gzkit/<surface>/<slug>/                # canonical authored content only
    CHORE.md, AGENTS.md, doctrine.md, ...

.gzkit/receipts/<surface>/<slug>/       # runtime state — logs, proofs, evidence
    CHORE-LOG.md
    proofs/<artifact>
    <run-id>/<artifact>
```

This satisfies the operator's framing on three axes simultaneously:

1. **Everything lives under `.gzkit/`** (operator-directive, 2026-05-11).
2. **Instructions are not co-located with outcomes** — canonical `<surface>/`
   directories carry only authored content; receipts/logs/proofs move out.
3. **Byte-parity invariants simplify** — once canonical and runtime are
   separated, the dual-surface byte-parity binding (ADR-0.0.32 § Decision)
   applies cleanly to canonical directories without per-class carve-out
   classifiers; runtime-state stays on whichever surface owns the run.

OBPI-0.0.32-13 (chores normalization) is the **temporary accommodation**
that preserves canonical-routing without prejudging this relocation. The
classifier authored there (`_classify_chore_file`) is shaped so the future
relocation is a mechanical move — drop the `runtime_state` class from the
classifier; relocate matching files to `.gzkit/receipts/<surface>/<slug>/`;
the byte-parity test simplifies to "every file under
`.gzkit/<surface>/<slug>/` and `src/gzkit/<surface>/<slug>/` is canonical
and binds."

## Decision

Park until ADR-0.0.32 closeout completes (so the canonical-routing
invariant is fully landed for skills + rules + personas + templates +
chores under the current layout). At that point, evaluate promotion:

- If the chores class-classifier from OBPI-0.0.32-13 has accumulated more
  than three carve-out classes, promotion is overdue.
- If a second canonical surface starts growing runtime-state artifacts
  (e.g., skills with per-run execution logs), promotion becomes urgent.
- If `gz agent sync control-surfaces` accumulates more than five
  carve-out branches in its sync logic, the relocation simplifies the
  sync mechanism enough to justify promotion regardless of other signals.

## Alternatives Considered

**A. Leave canonical and runtime-state mixed; expand the class-classifier
indefinitely.** Rejected on the operator framing ("may be a design flaw").
The classifier is a temporary accommodation, not a destination.

**B. Move runtime-state to a top-level directory OUTSIDE `.gzkit/` (e.g.,
`./runtime/`, `./state/`).** Rejected because the operator directive
("all aspects of gzkit must live in `.gzkit/` to keep things clean")
forbids it. Runtime state is a gzkit-owned aspect; it belongs under
`.gzkit/`, just not co-located with canonical content.

**C. Move runtime-state to a sibling directory at the canonical surface
level (e.g., `.gzkit/chores-runtime/<slug>/` next to `.gzkit/chores/<slug>/`).**
Rejected because the per-surface duplication doesn't scale — every new
canonical surface would need a `<surface>-runtime/` sibling, multiplying
top-level dirs under `.gzkit/`. The `.gzkit/receipts/<surface>/<slug>/`
shape collects runtime-state under one organizing principle.

**D. Use a manifest pointer at the canonical surface (e.g.,
`.gzkit/chores/<slug>/.runtime-state-at: .gzkit/receipts/chores/<slug>/`).**
Considered for handoff legibility; deferred — the directory shape
`.gzkit/receipts/<surface>/<slug>/` is already self-explanatory by
inspection, and a pointer file adds maintenance burden.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
