# gz status

Display gate status for current work.

---

## Usage

```bash
gz status [OPTIONS]
```

---

## Options

| Option | Type | Description |
|--------|------|-------------|
| `--json` | flag | Output as JSON |

---

## What It Does

Shows the current state of all ADRs and their gate progress:

- Which gates have passed
- Which gates are pending
- Overall lane (lite or heavy)

---

## Example

```bash
gz status
```

---

## Output

```
Lane: lite

ADR-0.1.0 (Pending)
  Gate 1 (ADR):   PASS
  Gate 2 (TDD):   PENDING

ADR-0.2.0 (Completed)
  Gate 1 (ADR):   PASS
  Gate 2 (TDD):   PASS
```

For heavy lane:

```
Lane: heavy

ADR-1.0.0 (Pending)
  Gate 1 (ADR):   PASS
  Gate 2 (TDD):   PASS
  Gate 3 (Docs):  PENDING
  Gate 4 (BDD):   PENDING
  Gate 5 (Human): PENDING
```

---

## JSON Output

```bash
gz status --json
```

```json
{
  "mode": "lite",
  "adrs": {
    "ADR-0.1.0": {
      "type": "adr",
      "parent": "BRIEF-add-login",
      "attested": false
    }
  },
  "pending_attestations": ["ADR-0.1.0"]
}
```

---

## Gates

| Gate | Name | What It Checks | Lane |
|------|------|----------------|------|
| 1 | ADR | ADR document exists | All |
| 2 | TDD | Tests exist and pass | All |
| 3 | Docs | Documentation updated | Heavy |
| 4 | BDD | Acceptance tests pass | Heavy |
| 5 | Human | Explicit attestation recorded | Heavy |
