# gz handoff list

List session handoffs newest-first (ADR-0.0.65).

---

## Overview

`gz handoff list` is a read-only projection over the canonical handoff store
`.gzkit/handoffs/`. It returns the frontmatter-filtered handoffs (only files
carrying an `adr_id`) sorted newest-first by timestamp. Pass `--adr` to scope
the listing to a single ADR. It never writes, moves, or deletes anything.

---

## Usage

```
gz handoff list [--adr ADR] [--json]
```

### Options

| Option | Description |
|--------|-------------|
| `--adr ADR` | Scope the listing to one ADR id (e.g. `ADR-0.0.65`). |
| `--json` | Emit the machine-readable `HandoffInfo` list. |

---

## Example

```bash
uv run gz handoff list --adr ADR-0.0.65
```

Observed output:

```
2026-07-15T00:35:24Z  ADR-0.0.65  OBPI-0.0.65-04-orientation-single-location-scan  .gzkit/handoffs/20260715T003524Z-OBPI-0.0.65-04-orientation-single-location-scan-complete.md
```

Machine-readable form:

```bash
uv run gz handoff list --adr ADR-0.0.65 --json
```

```json
[
  {
    "path": ".gzkit/handoffs/20260715T003524Z-OBPI-0.0.65-04-orientation-single-location-scan-complete.md",
    "adr_id": "ADR-0.0.65",
    "obpi_id": "OBPI-0.0.65-04-orientation-single-location-scan",
    "timestamp": "2026-07-15T00:35:24Z"
  }
]
```

---

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Listing produced (may be empty). |
