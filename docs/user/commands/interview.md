# gz interview

Run interactive governance interviews for structured input gathering.

## Usage

```bash
gz interview [OPTIONS]
```

## Description

Launches an interactive session to gather structured input for governance decisions. Captures responses in a durable format suitable for audit trails and ADR evidence.

## Options

| Option | Description |
|--------|-------------|
| `--from FILE` | Load answers from a JSON file instead of interactive prompts (non-interactive replay path for CI or scripted runs) |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Interview completed and recorded |
| 1 | Interview cancelled or validation failed |
