# gz interview

Run interactive governance interviews for structured input gathering.

## Usage

```bash
gz interview [OPTIONS] {prd,adr,obpi}
```

## Description

Launches an interactive session to gather structured input for governance decisions. Captures responses in a durable format suitable for audit trails and ADR evidence.

`gz interview obpi` authors the brief through the same builder as `gz specify`: the parent ADR's checklist item named by the `item` answer must exist and be live, as `gz specify` requires; the `allowed_paths`, `denied_paths` and `acceptance_criteria` answers replace the sections `gz specify` would infer, each acceptance criterion numbered as a REQ of that item; and a section left unanswered gets the inferred one.

## Options

| Option | Description |
|--------|-------------|
| `--from FILE` | Load answers from a JSON file instead of interactive prompts (non-interactive replay path for CI or scripted runs) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Interview completed and recorded |
| 1 | Interview cancelled or validation failed |
