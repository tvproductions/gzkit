# gz adr promote

Promote a pool ADR into an executable canonical ADR package and record promotion lineage.

---

## Usage

```bash
gz adr promote <POOL-ADR> --semver X.Y.Z --kind {foundation,feature} [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--semver` | string | Target ADR semantic version (`X.Y.Z`) |
| `--kind` | `foundation`/`feature` | Required. Target ADR taxonomy. `pool` is rejected (pool is the source kind, not a promotion target). |
| `--slug` | string | Target ADR slug override (kebab-case) |
| `--title` | string | Target ADR title override |
| `--parent` | string | Target ADR parent override |
| `--lane` | `lite`/`heavy` | Target ADR lane override |
| `--status` | `draft`/`proposed` | Initial promoted ADR status (default: `proposed`) |
| `--dry-run` | flag | Show promotion plan without writing files/events |
| `--json` | flag | Emit structured output |
| `--force` | flag | Override scaffold/eval quality gates. Does NOT bypass `--kind`/`--semver` binding. |

---

## Kind/Semver Binding (FAIL-CLOSED)

`--kind` and `--semver` are validated together before any file is moved or any ledger event written:

- `--kind foundation` requires `--semver` matching `^0\.0\.\d+$`. Mismatch -> exit 1.
- `--kind feature` requires `--semver` to NOT match `^0\.0\.\d+$`. Mismatch -> exit 1.
- `--kind pool` is rejected (pool is the source). Exit 1.
- Missing `--kind` is rejected with a recovery message naming both valid choices. Exit 1.

Validation runs before pool resolution, so a rejected promotion leaves the pool ADR, ledger, and target tree untouched.

---

## Protocol (Enforced)

1. Source must be a pool ADR (`ADR-pool.*` or legacy `ADR-*.pool.*`).
2. Target ADR ID is derived as `ADR-{semver}-{slug}`.
3. Target ADR package path is selected by **kind**:
   - `--kind foundation` -> `docs/design/adr/foundation/ADR-X.Y.Z-<slug>/`
   - `--kind feature`    -> `docs/design/adr/pre-release/ADR-X.Y.Z-<slug>/`
4. Pool ADR must already contain actionable `## Target Scope` bullets.
5. Promotion derives a concrete ADR checklist from that scope and creates matching OBPI briefs immediately.
6. Promoted ADR frontmatter carries `kind: <value>` (per ADR-0.0.17 schema).
7. Pool file is retained and updated to archival context:
   - `status: Superseded`
   - `promoted_to: ADR-X.Y.Z-slug`
8. Promotion lineage is written to ledger as:
   - `artifact_renamed` with `reason: pool_promotion`, `kind: <value>`, `semver: <value>`
9. One `obpi_created` ledger event is written per generated brief.

---

## Examples

```bash
# Preview promotion (foundation, infrastructure ADR)
gz adr promote ADR-pool.adr-taxonomy --semver 0.0.18 --kind foundation --dry-run

# Apply promotion (feature, release-carrying ADR)
gz adr promote ADR-pool.gz-chores-system --semver 0.6.0 --kind feature

# Override scaffold/eval gates (does NOT bypass kind/semver binding)
gz adr promote ADR-pool.sample --semver 0.6.0 --kind feature --force
```
