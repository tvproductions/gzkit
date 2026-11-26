# gz chores advise

Dry-run acceptance criteria for one chore and report actionable status.

## Usage

```bash
gz chores advise <slug>
```

## Description

Runs every acceptance criterion of a single chore, as `gz chores run` does, and reports `PASS` or `FAIL` for each without writing the chore's log. Use it to see what a run would find before running it; `gz chores plan` lists the criteria without running them.

The verdict reaches the exit status, so a scripted caller can branch on it without parsing the rendered output (GHI #781).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Every acceptance criterion passed |
| 1 | Chore not found or invalid input |
| 3 | At least one acceptance criterion failed (policy breach) |
