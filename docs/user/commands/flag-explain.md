# gz flag explain

Display flag metadata, resolved value with source, staleness, and
linked ADR.

## Usage

```bash
gz flag explain <key> [OPTIONS]
```

## Arguments

| Argument | Description |
|----------|-------------|
| `key` | Dotted flag key (e.g. `ops.product_proof`) |

## Options

| Flag | Description |
|------|-------------|
| `--json` | Output as JSON |
| `--quiet`, `-q` | Suppress non-error output |
| `--verbose`, `-v` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Description

Shows the full metadata for a single flag: category, description,
owner, default value, current resolved value, the precedence layer
that provided it, review/removal deadlines with days remaining, and
any linked ADR or GitHub issue.

If the flag is past its `review_by` or `remove_by` date, the output
marks it as **STALE** and the days count is negative.

If the key does not exist in the registry, exits with code 1.

## Examples

Explain a flag:

```bash
gz flag explain ops.product_proof
```

```text
ops.product_proof
  Category:      ops
  Description:   When enabled, the product proof check blocks
                 closeout for OBPIs without operator-facing
                 documentation. When disabled, the check warns
                 but does not block.
  Owner:         governance
  Default:       True
  Current value: True
  Source:        registry
  Review by:     2026-06-29 (91d)
  Linked ADR:    ADR-0.23.0
  Linked issue:  GHI-49
```

Machine-readable output:

```bash
gz flag explain ops.product_proof --json
```

```json
{
  "key": "ops.product_proof",
  "category": "ops",
  "default": true,
  "current_value": true,
  "source": "registry",
  "description": "When enabled, the product proof check ...",
  "owner": "governance",
  "review_by": "2026-06-29",
  "remove_by": null,
  "days_until_review": 91,
  "days_until_removal": null,
  "is_stale": false,
  "linked_adr": "ADR-0.23.0",
  "linked_issue": "GHI-49"
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Unknown flag key or user/config error |
| 2 | System/IO error (e.g. missing registry file) |
| 3 | Policy breach |
