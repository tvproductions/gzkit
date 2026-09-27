# gz migrate-semver

Record artifact ID rename migrations in the append-only ledger.

---

## Usage

```bash
gz migrate-semver [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--dry-run` | flag | Show rename events without writing |

---

## What It Does

1. Collects rename pairs from the legacy rename table (including SemVer pool IDs) and from on-disk drift: a bare ADR or OBPI id the ledger still carries whose file now has a slug stem.
2. Appends `artifact_renamed` events for pairs whose old ID appears in the ledger and is not already renamed.
3. Keeps ledger append-only (no rewrites).
4. Makes `gz state` and `gz status` resolve renamed IDs to canonical IDs.

---

## Example

```bash
# Preview migration
gz migrate-semver --dry-run

# Apply migration
gz migrate-semver
```

---

## Notes

- Safe to run repeatedly: existing rename events are skipped.
- This is the supported path for ID migrations (SemVer and pool ADR naming); do not edit `.gzkit/ledger.jsonl` manually.
