# Feature Flag System

Feature flags in gzkit are **transition controls**: mechanisms for
routing between old and new behavior during migration, with the
explicit expectation that the old path and the toggle will be removed.

They are not A/B experiments, user tiers, or analytics features.

---

## Flag Categories

| Category | Purpose | Deadline | Default Rule |
|----------|---------|----------|--------------|
| `release` | Transient feature gates for new capabilities | `remove_by` (required) | Varies |
| `ops` | Operational kill switches for risky behavior | `review_by` (required) | Varies |
| `migration` | Internal representation transitions | `remove_by` (required) | Varies |
| `development` | Incomplete work gating | `remove_by` (required) | Must be `false` |

### Release Flags

Short-lived (days to weeks). OFF = old behavior, ON = new behavior.
Example: `release.drift_command` gates the `gz drift` command during
its stabilization window.

### Ops Flags

Variable lifetime. Kill switches that operators can flip to disable
risky behavior without reverting code. Must be reviewed periodically
(`review_by` date). Example: `ops.product_proof` controls whether
the product proof check blocks or warns during closeout.

### Migration Flags

Medium-lived (weeks to one release cycle). ON = new path, OFF = old
path. Once migration is verified, the old path and the flag are
removed. Example: `migration.config_gates_to_flags` tracks the
removal of the legacy `config.gates` configuration.

### Development Flags

Gate incomplete work. Must default to `false` so unfinished features
are never active in production. Must have a `remove_by` date so they
do not accumulate.

---

## Lifecycle Rules

Every flag has a deadline:

- **Release, migration, development:** `remove_by` date. The flag
  and all code paths it guards must be removed by this date.
- **Ops:** `review_by` date. The flag must be reviewed for continued
  necessity. Review may extend the date or trigger removal.

A CI time-bomb test (`tests/test_no_expired_flags.py`) fails if any
flag is past its deadline, enforcing cleanup discipline.

Use `gz flags --stale` to check for overdue flags at any time.

---

## Precedence Chain

Flag values resolve through five layers (highest wins):

| Priority | Layer | Source | Use Case |
|----------|-------|--------|----------|
| 1 (lowest) | Registry default | `data/flags.json` | Source-controlled fallback |
| 2 | Environment variable | `GZKIT_FLAG_<KEY>` | CI/container config |
| 3 | Project config | `.gzkit.json` `flags` section | Per-project override |
| 4 | Test override | In-memory | Test isolation |
| 5 (highest) | Runtime override | In-memory | Development debugging |

### Environment Variable Format

Replace dots with underscores, uppercase, prefix with `GZKIT_FLAG_`:

```text
ops.product_proof -> GZKIT_FLAG_OPS_PRODUCT_PROOF
release.drift_command -> GZKIT_FLAG_RELEASE_DRIFT_COMMAND
```

Valid values (case-insensitive): `true`, `1`, `yes`, `false`, `0`,
`no`.

### Project Config Override

Add a `flags` section to `.gzkit.json`:

```json
{
  "mode": "lite",
  "flags": {
    "ops.product_proof": false,
    "release.drift_command": true
  }
}
```

---

## ON/OFF Convention

- **ON (`true`):** New behavior is active.
- **OFF (`false`):** Old/safe behavior is active.

Flag names describe the capability, not the state. For example,
`ops.product_proof` controls whether product proof enforcement is
active --- set to `true` to enforce, `false` to make it advisory.

---

## Toggle Point Rules

### Allowed Locations

- Command entry functions (e.g. closeout checks `product_proof_enforced()`)
- Sync orchestrators routing between old/new pipelines
- Init/scaffold flows for new vendor surface rollout
- Rendering/output paths for alternative display modes
- Diagnostic surfaces showing which path is active

### Forbidden Locations

- **Lifecycle state transitions** --- ADR authority is absolute
- **Attestation semantics** --- either happened or did not
- **Ledger event schema** --- audit trail structure is fixed
- **Gate identity** --- Gate 1=ADR, Gate 2=TDD, etc.
- **Canon meaning** --- what ADR/OBPI *is* cannot be toggled

### Code Pattern

Commands consume flags through `FeatureDecisions`, never through
raw flag keys:

```python
from gzkit.flags.decisions import get_decisions

decisions = get_decisions()
if decisions.product_proof_enforced():
    # blocking path
else:
    # advisory path
```

This ensures flag keys are centralized in the registry and
`FeatureDecisions`, not scattered across command code.

---

## Migration: `config.gates` to `flags`

The legacy `config.gates` section in `.gzkit.json` has been replaced
by the `flags` section. If your project still has a `gates` key, gzkit
emits a deprecation warning at startup.

### Migration Steps

1. Replace the `gates` section with `flags`:

   **Before (deprecated):**
   ```json
   {
     "mode": "lite",
     "gates": {
       "product_proof": "advisory"
     }
   }
   ```

   **After:**
   ```json
   {
     "mode": "lite",
     "flags": {
       "ops.product_proof": false
     }
   }
   ```

2. Map old gate values to flag booleans:

   | Old `gates` value | New `flags` value |
   |-------------------|-------------------|
   | `"enforce"` | `true` |
   | `"advisory"` | `false` |
   | `"disabled"` | `false` |

3. Remove the `gates` key from `.gzkit.json`.

The `migration.config_gates_to_flags` flag tracks this transition.
Once all projects have migrated, the flag and its code paths will be
removed by its `remove_by` date.

---

## Registry

Flags are declared in `data/flags.json` and validated against
`data/schemas/flags.schema.json`. Each flag entry requires:

| Field | Required | Description |
|-------|----------|-------------|
| `key` | Yes | Dotted key (`{category}.{name}`) |
| `category` | Yes | One of: release, ops, migration, development |
| `default` | Yes | Boolean default value |
| `description` | Yes | Human-readable purpose sentence |
| `owner` | Yes | Responsible party |
| `introduced_on` | Yes | ISO 8601 date |
| `review_by` | Ops only | When to review |
| `remove_by` | Release/migration/dev | When to remove |
| `linked_adr` | No | ADR that introduced the flag |
| `linked_issue` | No | GitHub issue tracking the flag |

---

## CLI Commands

- [`gz flags`](../user/commands/flags.md) --- list all flags with
  resolved values
- [`gz flag explain <key>`](../user/commands/flag-explain.md) ---
  inspect one flag in detail
