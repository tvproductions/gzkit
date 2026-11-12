# Waiver-Ratchet Drawdown

The waiver-ratchet gate refuses a debt list that grows; it cannot see one that never shrinks. This chore reports each
shrink-ratchet surface's live count against its baseline. At landing, 22 of 35 had never been drawn down.

## Commands

```bash
# The drawdown table
uv run python .gzkit/chores/waiver-ratchet-drawdown/check_drawdown.py --report

# Detector semantics, no repo state
uv run python .gzkit/chores/waiver-ratchet-drawdown/check_drawdown.py --self-test
```

## What it will not do

Tighten a baseline, remove an entry, or judge what coverage a waived entry provided (GHI #998).
