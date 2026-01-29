# gz attest

Record human attestation for an ADR.

---

## Usage

```bash
gz attest <ADR> --status <STATUS> [OPTIONS]
```

---

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `ADR` | Yes | ADR identifier (e.g., `ADR-0.1.0`) |

---

## Options

| Option | Type | Required | Description |
|--------|------|----------|-------------|
| `--status` | `completed` \| `partial` \| `dropped` | Yes | Attestation status |
| `--reason` | string | If partial/dropped | Reason for status |
| `--force` | flag | No | Skip prerequisite gate checks |
| `--dry-run` | flag | No | Show actions without writing |

---

## Attestation Status

| Status | Meaning |
|--------|---------|
| `completed` | Work finished; all claims verified |
| `partial` | Subset accepted; remainder deferred |
| `dropped` | Work rejected; rationale provided |

---

## What It Does

1. Verifies the ADR exists
2. Checks prerequisite gates (unless `--force`)
3. Records attestation in the ledger with:
   - ADR ID
   - Status
   - Attester (from git config)
   - Timestamp
   - Reason (if provided)

---

## Example

```bash
# Complete attestation
gz attest ADR-0.1.0 --status completed

# Partial attestation
gz attest ADR-0.1.0 --status partial --reason "Auth flow done, password reset deferred"

# Drop an ADR
gz attest ADR-0.1.0 --status dropped --reason "Requirements changed, approach obsolete"

# Force attestation (skip gate checks)
gz attest ADR-0.1.0 --status completed --force

# Dry run
gz attest ADR-0.1.0 --status completed --dry-run
```

---

## Output

```
Checking prerequisite gates...

Attestation recorded:
  ADR: ADR-0.1.0
  Status: completed
  By: Your Name
  Date: 2024-01-15
```

---

## Important

- This is **Gate 5**: the human verification gate
- It cannot be automated or skipped (without `--force`)
- The attester is recorded from `git config user.name`
- Partial and dropped statuses require `--reason`

---

## Why Manual?

Attestation is intentionally manual because:

1. It proves a human reviewed the work
2. It creates an audit trail
3. It prevents rubber-stamping

If you find yourself wanting to automate this, you're missing the point.
