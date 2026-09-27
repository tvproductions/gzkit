# gz adr promote

Promote a pool ADR into an executable canonical ADR package and record promotion lineage.

---

## Usage

```bash
gz adr promote <POOL-ADR> --semver X.Y.Z --kind feature [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--semver` | string | Required. Target ADR semantic version (`X.Y.Z`) |
| `--kind` | `feature` | Required. Target ADR taxonomy. `pool` is rejected (pool is the source kind, not a promotion target). **`foundation` is closed to new authoring by [ADR-0.34.0](../../design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md) and is rejected here — see [Closed kind: `foundation`](#closed-kind-foundation).** |
| `--slug` | string | Target ADR slug override (kebab-case) |
| `--title` | string | Target ADR title override |
| `--parent` | string | Target ADR parent override |
| `--lane` | `lite`/`heavy` | Target ADR lane override (defaults to the pool's `lane:`, then the project `mode`) |
| `--status` | `draft`/`proposed` | Initial promoted ADR status (default: `proposed`) |
| `--dry-run` | flag | Show promotion plan without writing files/events |
| `--json` | flag | Emit structured output |
| `--force` | flag | Skip the post-write structure, path, scaffold and evaluation checks. Takes effect only on the first application. Does NOT bypass `--kind`/`--semver` binding. |

---

## Closed kind: `foundation`

[ADR-0.34.0 (Foundation Sunset)](../../design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md)
closed the `foundation` kind to new authoring. `gz adr promote --kind foundation`
is rejected at the command handler, before any promotion I/O:

```
ERROR: --kind foundation was requested, but the foundation kind is closed to new
authoring by ADR-0.34.0 (Foundation Sunset). It remains a valid schema value only
for the existing grandfathered kind: foundation ADRs already on disk.
Re-run with --kind feature (release-carrying work) or --kind pool (backlog).
```

The kind is **sealed, not deleted**: `foundation` stays in the `--kind` argparse
choices and in the `kind` schema enum so the grandfathered on-disk foundation
ADRs keep validating. Promote new work with `--kind feature`.

---

## Kind/Semver Binding (FAIL-CLOSED)

`--kind` and `--semver` are validated together before any file is moved or any ledger event written:

- `--kind foundation` is rejected outright where the kind is closed, as in gzkit (see above). Exit 1. In a project that never closed it (no `data/foundation_grandfather.json`), `--kind foundation` requires a `0.0.x` `--semver`.
- `--kind feature` requires `--semver` to NOT match `^0\.0\.\d+$`. Mismatch -> exit 1.
- `--kind pool` is rejected (pool is the source). Exit 1.
- Missing `--kind` is rejected with a recovery message naming the valid choices. Exit 1.

Validation runs before pool resolution, so a rejected promotion leaves the pool ADR, ledger, and target tree untouched.

---

## Protocol (Enforced)

1. Source must be a pool ADR (`ADR-pool.*` or legacy `ADR-*.pool.*`).
2. Target ADR ID is derived as `ADR-{semver}-{slug}`.
3. Target ADR package path is selected by **kind**:
   - `--kind feature` -> `docs/design/adr/pre-release/ADR-X.Y.Z-<slug>/`
   - `--kind foundation`, where open -> `docs/design/adr/foundation/ADR-0.0.Z-<slug>/`
4. Pool ADR must contain a non-empty `## Target Scope` section, preserved verbatim in the promoted ADR.
5. Promotion derives the ADR checklist from a `## Proposed OBPI Decomposition` table (`Slug` and `Description` columns) when present, else from the top-level `## Target Scope` bullets; legacy narrative-only bullets warn (GHI #241). It creates one OBPI brief per checklist item immediately.
6. Promoted ADR frontmatter carries `kind: <value>` (per ADR-0.0.17 schema).
7. Pool file is retained and updated to archival context:
   - `status: Superseded`
   - `promoted_to: ADR-X.Y.Z-slug`
   - a `> Promoted to ... on <date>` note under the H1
8. Promotion lineage is written to ledger as:
   - `artifact_renamed` with `reason: pool_promotion`, `kind: <value>`, `semver: <value>`
9. One `obpi_created` ledger event is written per generated brief, and one `obpi_unparked` per OBPI a prior `gz adr demote` parked at this pool id (GHI #584).
10. No `adr_created` is written. The promoted ADR inherits the pool id's `adr_created` through the rename; if the pool ADR was never booked (`gz plan create --kind pool` books nothing), run `gz register-adrs <TARGET-ADR>` to book it.

Post-promotion brief checks report missing allowed paths and generated vendor
mirrors, including paths beginning with `./`, with canonical edit advice for
mirrors. Brief CREATE declarations exempt missing paths only. These checks
run after promotion writes; the existing `--force` quality override still applies.

If those checks fail, the promotion **has already been applied**: the target
ADR and briefs, the Superseded pool source, and promotion ledger events remain.
Structural/path/scaffold failures exit `1`; a non-GO evaluation exits `3`.
Author the created package and run `gz obpi validate --adr <TARGET-ADR> --authored`
and `gz adr evaluate <TARGET-ADR>` against that target. These commands recheck
the existing artifacts; they do not repeat promotion. Do not retry promotion
with `--force`: the recorded source rename refuses another promotion. `--force`
only overrides the checks when supplied on the initial application.

---

## Examples

```bash
# Preview promotion (feature, release-carrying ADR)
gz adr promote ADR-pool.adr-amendment-tracking --semver 0.7.0 --kind feature --dry-run

# Apply promotion (feature, release-carrying ADR)
gz adr promote ADR-pool.gz-chores-system --semver 0.6.0 --kind feature

# Override scaffold/eval gates (does NOT bypass kind/semver binding)
gz adr promote ADR-pool.sample --semver 0.6.0 --kind feature --force
```
