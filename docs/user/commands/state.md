# gz state

Query ledger artifact relationships and derived ADR semantics.

---

## Usage

```bash
gz state [--json] [--blocked] [--ready]
```

---

## Filters

- `--blocked`: show unattested artifacts.
- `--ready`: show ADRs that are genuinely ready for attestation.

`--ready` means:

- ADR is unattested, and
- prerequisite gates required by lane are satisfied.

It is not just "pending attestation".

---

## Derived ADR Fields

ADR entries include additive derived semantics (for example `lifecycle_status`, `closeout_phase`, `attestation_term`) based on ledger events.

---

## Example

```bash
uv run gz state --ready
uv run gz state --ready --json
```
