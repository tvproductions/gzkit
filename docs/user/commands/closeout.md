# gz closeout

Initiate closeout mode for an ADR and record `closeout_initiated` in the ledger.

---

## Usage

```bash
gz closeout <ADR-ID> [--json] [--dry-run]
```

---

## Runtime Behavior

`gz closeout` is a presentation step. It emits paths and commands only.

Output includes:

- Gate 1 ADR path
- Linked OBPI evidence paths
- Verification command set for the ADR lane
- Canonical attestation choices
- Heavy-lane Gate 4 command when `features/` exists
- Heavy-lane explicit Gate 4 N/A reason when `features/` is absent

It does not interpret command outcomes.

---

## Canonical Attestation Choices

- `Completed`
- `Completed — Partial: [reason]`
- `Dropped — [reason]`

---

## Options

| Option | Description |
|--------|-------------|
| `--json` | Emit machine-readable closeout payload |
| `--dry-run` | Show payload without writing ledger event |

---

## Example

```bash
uv run gz closeout ADR-0.3.0
```
