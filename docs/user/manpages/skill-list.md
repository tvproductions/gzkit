# gz skill list

List skills discovered from the canonical skills directory.

## Usage

```bash
gz skill list [--all] [--json]
```

## Description

Displays skills from `.gzkit/skills/`. By default the listing matches the
filtering used when generating the `AGENTS.md` skill catalog: skills with
`lifecycle_state: retired` in their SKILL.md frontmatter are hidden so routing
docs and CLI discovery surface the same active set.

Pass `--all` to include retired/archived compatibility skills. When `--all` is
set the output adds a Lifecycle column labelled `active` or `retired`.

Use `--json` for machine-readable output. The JSON payload always carries
`include_retired` so downstream consumers can record which filter was applied.

## Options

| Option | Description |
|--------|-------------|
| `--all` | Include retired/archived skills (default: hidden). |
| `--json` | Emit JSON instead of a Rich table. |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Skills listed successfully |
| 1 | User/config error (project not initialized) |
