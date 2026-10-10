# The identifier migration — a program, for the operator to route

> **What this is.** Row 5 of R&D run `renewing-vows` (`../renewing-vows.md`): "one-shot
> refactoring — propose a program; the operator selects its route." Drafted 2026-10-10 on
> the operator's go ('go on row 5'). It proposes and starts nothing. Figures are measured
> on the date given; re-run the command before relying on one.

## What is migrated, as ruled

Ruled 2026-10-05 ('A', the artifact ladder) and carried 2026-10-07 and 2026-10-10 (timed
to 1.0, full operational capability):

| Today | Ultimate name | Identifier | Standing |
|---|---|---|---|
| pool ADR | change proposal | `ECP-<slug>` | ruled; "change proposal" in no landed source |
| feature ADR, the "(m)ADR" | engineering order | `EO-<semver>-<slug>` | ruled; "engineering order" a maintenance term only (AC 120-16G § 7-1c) |
| OBPI | work package | `WP-<semver>-<NN>-<slug>` | ruled; "work package" verified (AC 120-16G § 6-1) |
| TASK | task card | `TASK-…` kept | ruled; "task card" verified (AC 120-16G § 3-3d) |
| ADR | architecture decision record | `ADR-<n>` | ruled: reserved for architecture decisions; the closed `0.0.x` series kept as the certification basis and not renamed |
| release | block | no identifier | ruled; "block" in no landed source |

Not renamed: `REQ-<semver>-<NN>-<MM>` and `TASK-<semver>-<NN>-<MM>-<PP>` keep their numeric
grammar beneath the new prefixes, so `@covers(REQ-…)` and the Task trailers are untouched.
`GHI #N` is the issue tracker's.

**What the ladder met after it was ruled** (record, 2026-10-08): `docs/governance/GovZero/adr-lifecycle.md`
holds an identifier scheme of its own (`0.1.15-obpi.03`, `0.1.15-ghi.67`); `releases/README.md`
makes the ADR a minor release's intent carrier; and `ieee/OPEN-QUESTIONS.md` Q-18
(2026-10-04) recorded "Names are chosen later" one day before the names were ruled. The
program's phase 0 reconciles these; the operator may re-rule the names with the go on this
row (record, frontier item 11).

## Measured surface (2026-10-10)

| What | Measure | Command |
|---|---|---|
| ADR packages under `pre-release/` and `foundation/` | 91 | `ls docs/design/adr/pre-release docs/design/adr/foundation \| wc -l` |
| Pool entries | 219 | `ls docs/design/adr/pool \| wc -l` |
| Ledger rows carrying an `adr_id` | 1350 | `grep -c '"adr_id"' .gzkit/ledger.jsonl` |
| Python files under `src/gzkit` matching an `ADR-` or `OBPI-` prefix | 105 | `grep -rl 'ADR-\\\|OBPI-\\\|"ADR-\|"OBPI-' src/gzkit --include='*.py' \| wc -l` |
| Schemas pinning the id grammar | `adr.json` (`ADR-pool.<slug>` or `ADR-<semver>-<slug>`), `obpi.json` (`OBPI-<semver>-<NN>[-<slug>]`) | `grep -n '"pattern"' src/gzkit/schemas/adr.json src/gzkit/schemas/obpi.json` |

## The mechanism gzkit already has

- `gz migrate-semver` appends `artifact_renamed` events (reason
  `semver_minor_sequence_migration`) from a fixed table, `SEMVER_ID_RENAMES` in
  `src/gzkit/commands/register.py`, and from on-disk drift. The ledger is never rewritten;
  an old id resolves to its canonical id through the event. Re-running is safe. A bulk
  rename written in error cannot be removed, only countered (GHI #584), so the skill shows
  the dry-run list and takes the operator's approval first.
- `gz adr promote` records its own rename for a pool promotion; slug-to-slug corrections go
  through `python -m gzkit.governance.obpi_slug_rename`.
- The precedent: the pool migration `ADR-0.2.0-pool.*` → `ADR-pool.*` ran through the same
  table.

So the alias layer the ruling asks for ("aliases bridge") is the ledger's rename event plus
a resolver that accepts both forms. What does not exist: a resolver for the new prefixes, and
schema patterns that admit them.

## The program

**Phase 0, now (this row's go).** Record the target grammar in one place, the pool ADR this
program proposes; freeze: no artifact takes a new prefix before 1.0; reconcile
`adr-lifecycle.md`'s scheme and `releases/README.md`'s carrier sentence with the ladder, as
corrections under GHI #1188's class or as items of the pool ADR; put the names to the
operator once more against Q-18.

**Phase 1, before 1.0: aliases.** One id-resolution function, used by every reader
(validators, `gz adr status`, `gz obpi *`, the hooks, the handoff resolver), that maps an id
in either form to its canonical form by prefix table and by `artifact_renamed` events. The
two schemas admit both forms during the bridge. A validator proves every reader goes through
the resolver (the `_crossing_channels` precedent: one implementation, consumers that share
it). Measured surface: the 105 Python files and the two schemas; each reader that matches a
prefix by hand is a finding for this phase.

**Phase 2, at 1.0: the rename.** Directory and file renames for feature ADRs, OBPIs and pool
entries (`git mv`, history preserved); one `gz migrate-semver` run from an extended
`SEMVER_ID_RENAMES` table, dry-run shown to the operator, approved, then written; the
docs, skills, nav and delivered surfaces updated in the same change; `0.0.x` foundation
packages untouched. The operator attests the run as the Gate 5 of the package that carries
it.

**Phase 3, after 1.0.** The old form is accepted silently for one block, then with a
warning, then refused; the resolver keeps resolving it forever through the ledger.

## Routes, for the operator to select

- **A. A feature ADR at the 1.0 boundary**, inside the first-release work
  (`ADR-pool.first-release-ceremony`'s neighbourhood): the migration is a runtime-contract
  change (heavy) and ships with the block it names. Cost: the alias layer (phase 1) would
  wait until that ADR is authored, which is late for a bridge.
- **B. A pool ADR now, promoted at 1.0** (recommended): `ADR-pool.identifier-ladder-migration`
  carries the grammar, the freeze and the three phases; phase 1 can be drawn as its first
  OBPI when the operator initiates it; promotion at 1.0 carries phase 2. Consistent with
  rows 1 and 5 as drafted ("a change proposal is a pool ADR") and with `gz adr promote`
  recording its own rename.
- **C. A chore-class one-shot refactoring.** Rejected on canon: the change alters a runtime
  contract (the id grammar, two schemas, every reader), which is OBPI work the operator
  initiates, not a chore.

## Risks and unknowns

- GHI #1186: 525 `@covers` tags cite OBPI ids today; whichever route that issue takes
  must land before or with phase 1, or the resolver must admit the OBPI-id form there too.
- Adopters: `gz init` scaffolds and 42 delivered skills cite ids (GHI #1138); the bridge
  must ship in the wheel, not only in this repository.
- The IEEE series' comparison of release containers (Q-18) is reference material; "block"
  and "change proposal" have no landed source and are gzkit's own words.
- The 1350 ledger references are never rewritten; a reader that greps the ledger for a
  literal prefix instead of resolving is the class this program's phase 1 validator exists
  to catch.
