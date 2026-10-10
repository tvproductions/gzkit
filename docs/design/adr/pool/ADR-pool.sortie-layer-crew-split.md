---
id: ADR-pool.sortie-layer-crew-split
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.sortie-layer-crew-split: Sortie layer: the crew split with the tasking order and the sortie matrix

## Status

Pool

## Intent

**Origin.** Proposed under row 1 of R&D run `renewing-vows` (`docs/rnd/renewing-vows.md`), signed off *fund* on 2026-10-10 and given its go on row 1 the same day (operator, verbatim: 'pool; beside it, provisional, new, now — create, then git sync'). A pool ADR is a change proposal: it books nothing and initiates nothing; promotion is the operator's (IRON LAW).

One work package is flown as a set of sorties by distinct positions rather than by one
session doing every step inline. The requirement's kind fixes the standard set
(`.gzkit/rules/weaponeering.md`, landed 2026-10-10, advisory until this layer gives it a
runtime check): a BEHAVIOR requirement flies constraints, red and green; SUPPORT one
documentary sortie; STRUCTURAL-FENCE none. The constraints sortie is a Design act that lands
the contracts before any failing test (operator ruling 2026-10-05), so that red fails on an
assertion and not on a missing symbol; measured 2026-10-05, 207 of 282 red receipts on the
ledger failed on `error`.

The tasking order is the ledger record of what was commanded (operator ruling 2026-10-05,
'4. A'), and is item 1 of `ADR-pool.command-doctrine-internalization`, the captain's brief;
this ADR consumes that event and does not redefine it. The sortie matrix is a Layer-3 view:
rows from the brief's requirements, cells from the ledger's tasking, dispatch and outcome
events. Positions are obligations with a role to fulfil them; crew fill them and command
nothing (statement of command, `docs/governance/GovZero/command-doctrine.md`, ratified
2026-10-10).

**Depends on** `ADR-0.35.0` briefs 15 to 18 (the run's position, next command, stage
procedure and dispatch outcome), without which no sortie has a recorded outcome to assess.
**Assembles** the pool nominations already present: `ADR-pool.sandboxed-delegation`,
`ADR-pool.tool-permission-classifier`, `ADR-pool.execution-memory-graph`,
`ADR-pool.tdd-receipt-stream`, `ADR-pool.review-receipt-taxonomy`, `ADR-pool.harness-lab`,
`ADR-pool.rulings-as-first-class-events`, `ADR-pool.change-isolation-workspace`. **Sits
beside** `ADR-pool.workflow-specification` (operator ruling 2026-10-10: 'beside it'): that
specification describes stages, evidence and events machine-readably, and this layer is its
first consumer, not its replacement.

## Decision

Proposed, not decided. When promoted, the feature ADR would carry, in this order:

1. The weaponeering check in the runtime: the sortie set for each requirement derived from
   its kind; a skipped standard sortie refused unless the order cites the ledger product
   that stands in for it; green and assessment never waived. Reclassifies
   `.gzkit/rules/weaponeering.md` from advisory to mechanical.
2. The constraints sortie as a dispatched position with its own receipt, whose product
   (interfaces, invariants, stubs) travels in the tasking order.
3. The sortie matrix as a `gz` view over ledger events, with no state of its own.
4. The assessment position (BDA) owning five outputs: hit, works, effect on the surrounding
   system (the scope report, GHI #1181), munitions effectiveness (ruled 2026-10-10 as this
   position's), and reattack.

Model and effort are allocated by echelon and role on the agent definitions
(`.gzkit/rules/model-selection.md` 0.7.0, advisory table), one definition per role × effort
band.

## Alternatives Considered

- **Keep the inline session.** One session plans, constrains, writes red and green and
  presents. Rejected by the operator's direction of 2026-10-05: 'a series of much smaller,
  and much more focused agents, being orchestrated, often by skill-driven workflow, is a
  better goal.'
- **Fold this into `ADR-pool.workflow-specification`.** Rejected 2026-10-10 ('beside it'):
  the specification is a description; this is the runtime it would describe.
- **Make the tasking order this ADR's.** Rejected: it is item 1 of the command doctrine's
  worklist, carried by the campaign (§ Amendments 2026-10-10); this ADR consumes it.
- **Planner discretion over the sortie set.** Refused by the operator 2026-10-05: the kind
  fixes the set; subtraction cites evidence; addition is free.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
