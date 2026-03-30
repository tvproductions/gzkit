# gz flags

Display all registered feature flags with current values and sources.

## Usage

```bash
gz flags [OPTIONS]
```

## Options

| Flag | Description |
|------|-------------|
| `--stale` | Show only stale flags (past review_by or remove_by dates) |
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Lists every flag in the registry (`data/flags.json`) alongside its
resolved value and the precedence layer that determined it. The table
includes category, default, current value, source, owner, and days
until the next review or removal deadline.

The `--stale` filter restricts output to flags whose `review_by` or
`remove_by` date has passed. Overdue deadlines display with negative
day counts.

### Precedence Chain

Each flag resolves through five layers (highest wins):

1. **Registry default** (lowest) -- source-controlled fallback
2. **Environment variable** (`GZKIT_FLAG_<KEY>`, dots to underscores,
   uppercase)
3. **Project config** (`.gzkit.json` `flags` section)
4. **Test override** (in-memory, per-test)
5. **Runtime override** (in-memory, highest)

The `Source` column in the table shows which layer provided the value.

## Examples

List all flags:

```bash
gz flags
```

```text
                     Feature Flags
+-----------+-----------+---------+-------+----------+
| Key       | Category  | Default | Value | Source   |
+-----------+-----------+---------+-------+----------+
| ops.pro~  | ops       | True    | True  | registry |
| release~  | release   | False   | False | registry |
+-----------+-----------+---------+-------+----------+
```

Show only stale flags:

```bash
gz flags --stale
```

```text
No stale flags.
```

Machine-readable output:

```bash
gz flags --json
```

```json
[
  {
    "key": "ops.product_proof",
    "category": "ops",
    "default": true,
    "current_value": true,
    "source": "registry",
    "owner": "governance",
    "days_until_review": 91,
    "days_until_removal": null
  }
]
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error |
| 2 | System/IO error |
| 3 | Policy breach |
