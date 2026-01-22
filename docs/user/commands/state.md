# gz state

Query ledger state and artifact relationships.

---

## Usage

```bash
gz state [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--json` | flag | Output as JSON |
| `--blocked` | flag | Show only unattested artifacts |
| `--ready` | flag | Show only artifacts ready for attestation |

---

## What It Does

Shows the full artifact graph:

- All PRDs, briefs, and ADRs
- Parent-child relationships
- Attestation status

---

## Example

```bash
gz state
```

---

## Output

```
┌────────────────────────────────────────────────┐
│               Artifact State                    │
├──────────────────┬──────┬────────────┬─────────┤
│ ID               │ Type │ Parent     │ Attested│
├──────────────────┼──────┼────────────┼─────────┤
│ PRD-my-feature   │ prd  │ -          │ Yes     │
│ BRIEF-add-login  │ brief│ PRD-my-... │ No      │
│ ADR-0.1.0        │ adr  │ BRIEF-add..│ No      │
└──────────────────┴──────┴────────────┴─────────┘
```

---

## Filters

### Blocked only

```bash
gz state --blocked
```

Shows artifacts that haven't been attested.

### Ready only

```bash
gz state --ready
```

Shows ADRs that are ready for attestation (all prerequisite gates passed).

---

## JSON Output

```bash
gz state --json
```

```json
{
  "PRD-my-feature-1.0.0": {
    "type": "prd",
    "parent": null,
    "attested": true
  },
  "BRIEF-add-login": {
    "type": "brief",
    "parent": "PRD-my-feature-1.0.0",
    "attested": false
  },
  "ADR-0.1.0": {
    "type": "adr",
    "parent": "BRIEF-add-login",
    "attested": false,
    "lane": "lite"
  }
}
```

---

## Use Cases

1. **See what's pending**: `gz state --blocked`
2. **Find what to attest next**: `gz state --ready`
3. **Export for tooling**: `gz state --json`
4. **Understand artifact hierarchy**: `gz state`
