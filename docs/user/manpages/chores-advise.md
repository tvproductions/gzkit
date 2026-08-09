# gz chores advise

Dry-run acceptance criteria for one chore and report actionable status.

## Usage

```bash
gz chores advise <slug>
```

## Description

Displays the acceptance criteria and actionable advice for a single chore without applying any changes. Use this to understand what a chore will do and gather evidence before running it.

The verdict reaches the exit status, so a scripted caller can branch on it without parsing the rendered output (GHI #781).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Every acceptance criterion passed |
| 1 | Chore not found or invalid input |
| 3 | At least one acceptance criterion failed (policy breach) |
