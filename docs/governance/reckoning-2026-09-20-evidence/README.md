# Campaign reckoning — re-run instructions

```bash
uv run python docs/governance/reckoning-2026-09-20-evidence/reckon.py
```

Read-only. Runs `git log`, reads `.gzkit/ledger.jsonl`, and walks `src/`, `tests/`
and `docs/design/adr/`. Writes nothing, makes no network call, touches no ledger.

**Carries no literals from its authoring date.** Every figure is derived at run
time, so a later run reports the later tree. The 2026-09-20 campaign edition cites
this script rather than transcribing its output, per the operator's
*"Pointer, not value"* ruling of 2026-09-20.

## Reading the window

The 90-day window is measured **from the run date**, which is how the 2026-07-18
and 2026-08-16 passes measured theirs. A later run therefore covers a later
period: the figures are comparable **in method**, not in period. Two runs months
apart are two windows, not a before/after of one.

## Counting methods, stated because they decide comparability

- **ADRs** — `docs/design/adr/**/ADR-*.md`. **OBPI briefs** — `**/obpis/OBPI-*.md`.
  The 08-16 edition recorded 659 briefs where this glob reports 545. That is a
  method difference, not 114 deleted briefs; neither prior edition recorded the
  glob it used, which is why this one does.
- **Commit mix** — the leading word of the subject line, so `fix(scope):` and a
  bare `fix:` both count as `fix`. `gz git-sync` is counted by subject substring
  and overlaps the `chore` bucket rather than adding to it.
- **Airlock** — cumulative over the whole ledger, never windowed, matching how the
  07-18 and 08-16 passes quoted it.
- **Oversized modules** — physical lines over 600 under `src/`, excluding
  `__pycache__`. The 08-16 edition did not state its method.

## What it deliberately does not compute

Advisory-scorecard tallies. `gz validate --advisory-scorecard` already checks the
Summary roll-up against the scored rows and fails closed when they disagree. A
draft of this script computed its own and produced 70/34/71/1 against the
validated 71/33/72/0 — a second counter disagreeing with the instrument is a fresh
instance of the defect this campaign is chasing, so it was removed rather than
reconciled. Read the scorecard's own Summary, or run the validator.
