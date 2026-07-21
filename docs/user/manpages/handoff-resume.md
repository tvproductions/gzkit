# gz handoff resume

Resume the newest handoff for an ADR with staleness (ADR-0.0.65).

---

## Overview

`gz handoff resume` is a read-only projection over `.gzkit/handoffs/`. It selects
the newest handoff for the given ADR, classifies its staleness (`Fresh`,
`Slightly-Stale`, `Stale`, `Very-Stale`), reports whether it requires human
verification, and extracts
the first next step from the handoff body. It never writes anything.

A handoff advises; it does not authorize. The reported next step is the advised
action for the operator to ratify — resuming is not a Gate-5 attestation.

---

## Usage

```
gz handoff resume [--adr ADR] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--adr ADR` | ADR id to resume the newest handoff for. Omit to resume the newest handoff overall — the only way to reach a handoff with no parent ADR (GHI #709). |
| `--json` | Emit the machine-readable `ResumeResult`. |

---

## Example

```bash
uv run gz handoff resume --adr ADR-0.0.65
```

Observed output:

```
resume — .gzkit/handoffs/20260715T003524Z-OBPI-0.0.65-04-orientation-single-location-scan-complete.md
  staleness: Fresh
  requires human verification: False
  next step: Continue the parent ADR-0.0.65 checklist, or open the next OBPI.
```

Machine-readable form:

```bash
uv run gz handoff resume --adr ADR-0.0.65 --json
```

```json
{
  "path": ".gzkit/handoffs/20260715T003524Z-OBPI-0.0.65-04-orientation-single-location-scan-complete.md",
  "staleness": "Fresh",
  "requires_human_verification": false,
  "first_next_step": "Continue the parent ADR-0.0.65 checklist, or open the next OBPI.",
  "chain": [
    ".gzkit/handoffs/20260715T003524Z-OBPI-0.0.65-04-orientation-single-location-scan-complete.md"
  ]
}
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Newest handoff resolved and reported. |
| 1 | User error — no handoff exists for the requested ADR. |
