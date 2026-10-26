# Competitor Radar Currency

Keep the competitor radar (`artifacts/reports/competitor-radar/`) current by running
the `gz-competitor-radar` skill on a staleness clock. The chore refreshes every
registry competitor from current sources, discovers new candidates, writes the
month's scan, and opens the grill discussion for each suggested move.

Scan + route only. It never mutates governance artifacts. Moves route after the
operator rules them.

## Quick Start

```bash
uv run gz chores advise competitor-radar-currency
```

## Lane

**lite**
