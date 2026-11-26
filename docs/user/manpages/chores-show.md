# gz chores show

Display the CHORE.md content for one chore.

## Usage

```bash
gz chores show <slug>
```

## Description

Outputs the full CHORE.md specification for a single chore: its scope, workflow and governance annotations. Acceptance criteria live in `acceptance.json`; `gz chores plan` prints them.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Chore content displayed successfully |
| 1 | Chore not found or invalid input |
