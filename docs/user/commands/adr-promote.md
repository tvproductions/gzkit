# gz adr promote

Promote a pool ADR into canonical ADR package structure and record ledger rename lineage.

---

## Usage

```bash
gz adr promote <POOL-ADR> --semver X.Y.Z [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--semver` | string | Target ADR semantic version (`X.Y.Z`) |
| `--slug` | string | Target ADR slug override (kebab-case) |
| `--title` | string | Target ADR title override |
| `--parent` | string | Target ADR parent override |
| `--lane` | `lite`/`heavy` | Target ADR lane override |
| `--status` | `draft`/`proposed` | Initial promoted ADR status (default: `proposed`) |
| `--dry-run` | flag | Show promotion plan without writing files/events |
| `--json` | flag | Emit structured output |

---

## Protocol (Enforced)

1. Source must be a pool ADR (`ADR-pool.*` or legacy `ADR-*.pool.*`).
2. Target ADR ID is derived as `ADR-{semver}-{slug}`.
3. Target ADR package path is selected by SemVer bucket:
   - `0.0.z` -> `foundation/`
   - `0.y.z` (`y>0`) -> `pre-release/`
   - `1.y.z+` -> `<major>.0/`
4. Pool file is retained and updated to archival context:
   - `status: Superseded`
   - `promoted_to: ADR-X.Y.Z-slug`
5. Promotion lineage is written to ledger as:
   - `artifact_renamed` with reason `pool_promotion`

---

## Examples

```bash
# Preview promotion
gz adr promote ADR-pool.gz-chores-system --semver 0.6.0 --dry-run

# Apply promotion
gz adr promote ADR-pool.gz-chores-system --semver 0.6.0
```
