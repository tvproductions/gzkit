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

1. Scans ledger history for known old artifact IDs (including legacy SemVer pool IDs).
2. Appends `artifact_renamed` events for matching IDs.
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
