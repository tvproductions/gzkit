---
id: ADR-pool.identifier-ladder-migration
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
---

# ADR-pool.identifier-ladder-migration: Identifier ladder migration: ECP, EO and WP at 1.0, aliases before

## Status

Pool

## Intent

**Origin.** Row 5 of R&D run `renewing-vows` (`docs/rnd/renewing-vows.md`), signed off
*fund* on 2026-10-10; the row's program is `docs/rnd/renewing-vows/identifier-migration-program.md`
and this ADR is its route B, selected by the operator the same day (verbatim: 'B, create,
then git sync'). A pool ADR is a change proposal: it books nothing and initiates nothing;
promotion is the operator's (IRON LAW), timed to 1.0.

The artifact ladder's names were ruled on 2026-10-05 ('A'): a pool ADR is a change proposal
(`ECP-<slug>`); the feature ADR, the stopgap "(m)ADR", is an engineering order
(`EO-<semver>-<slug>`); an OBPI is a work package (`WP-<semver>-<NN>-<slug>`); a TASK is a
task card and keeps `TASK-`; `ADR-<n>` is reserved for architecture decisions, with the
closed `0.0.x` series kept as gzkit's certification basis and not renamed; a release is a
block and carries no identifier. `REQ` and `TASK` keep their numeric grammar beneath the new
prefixes, so `@covers(REQ-…)` and the Task trailers are untouched. Identifiers migrate at
1.0, full operational capability (rulings of 2026-10-07 and 2026-10-10); aliases bridge
until then.

The ladder met canon it was ruled without: `docs/governance/GovZero/adr-lifecycle.md` holds
a scheme of its own (`0.1.15-obpi.03`), `docs/governance/GovZero/releases/README.md` makes the
ADR a minor release's intent carrier, and `docs/governance/ieee/OPEN-QUESTIONS.md` Q-18
(2026-10-04) recorded "Names are chosen later". Phase 0 reconciles them, and the operator may
re-rule the names at promotion.

Measured 2026-10-10: 91 ADR packages under `pre-release/` and `foundation/`, 219 pool
entries, 1350 ledger rows carrying an `adr_id`, 105 Python files under `src/gzkit` matching
an `ADR-` or `OBPI-` prefix, and two schemas pinning the grammar (`adr.json`, `obpi.json`).
The mechanism exists: `gz migrate-semver` appends `artifact_renamed` events from
`SEMVER_ID_RENAMES` and never rewrites the ledger; the pool migration of `ADR-0.2.0-pool.*`
to `ADR-pool.*` is its precedent.

## Decision

Proposed, not decided. When promoted, the feature ADR would carry three phases, each a
work package the operator initiates:

0. **Record and freeze.** The target grammar in this ADR; no artifact takes a new prefix
   before 1.0; `adr-lifecycle.md`'s scheme and `releases/README.md`'s carrier sentence
   reconciled with the ladder (with GHI #1188's class); the names put to the operator once
   more against Q-18.
1. **Aliases, before 1.0.** One id-resolution function every reader shares (validators,
   `gz adr status`, `gz obpi *`, the hooks, the handoff resolver), mapping either form to
   the canonical id by prefix table and by `artifact_renamed` events; both schemas admit
   both forms during the bridge; a validator proves every reader resolves through it (the
   `_crossing_channels` precedent: one implementation, consumers that share it). The 105
   matching files and the two schemas are the population.
2. **The rename, at 1.0.** `git mv` of feature ADR, OBPI and pool files; one
   `gz migrate-semver` run from the extended table, its dry-run list shown and approved by
   the operator before it writes (a bulk rename cannot be removed from the ledger, only
   countered, GHI #584); docs, skills, nav and the delivered surfaces in the same change;
   `0.0.x` packages untouched; the operator's attestation as the Gate 5 of the package.
3. **Retirement, after 1.0.** The old form accepted silently for one block, then with a
   warning, then refused; the resolver keeps resolving it forever through the ledger.

Dependencies: GHI #1186 (the `@covers` tags citing OBPI ids) lands before or with phase 1, or
the resolver admits that form; the bridge ships in the wheel, because adopters' scaffolds
and 42 delivered skills cite ids (GHI #1138).

## Alternatives Considered

- **A feature ADR at the 1.0 boundary.** Not selected (operator, 2026-10-10: 'B'): the alias
  layer would wait until that ADR is authored, which is late for a bridge.
- **A chore-class one-shot refactoring.** Rejected on canon: the change alters a runtime
  contract (the id grammar, two schemas, every reader), which is OBPI work the operator
  initiates, not a chore.
- **Rename without aliases.** Rejected: 1350 ledger rows and every delivered surface cite
  the old form; a reader that greps for a literal prefix instead of resolving is the class
  phase 1's validator exists to catch.
- **Keep the (m)ADR name.** Superseded by the ruling of 2026-10-05 and the Q-18 direction:
  the stopgap's successor is a feature bundle, named here.

## Notes

Pool ADRs are backlog items — they carry no `semver:` or `kind:` frontmatter.
Promotion into the active tree (foundation or feature) is performed via
`gz adr promote`, which rewrites the frontmatter with the chosen taxonomy.
