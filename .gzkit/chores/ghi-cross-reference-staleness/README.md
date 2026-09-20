# GHI Cross-Reference Staleness

An open issue body writing `#889 (open)` transcribes GitHub's issue state into prose that
never reconciles. The annotation is true when authored and false the moment the sibling
closes. At landing, **5 of 10** such annotations in the open queue were already false.

## Commands

```bash
# Report the population and the decay rate
uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py --report

# Enforcement — exit 1 when decay is not disclosed
uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py

# Detector semantics, no network
uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py --self-test
```

## What it will not do

| | |
|---|---|
| Rewrite a body | The annotation was **true when authored**; editing it falsifies a dated record. `gh issue edit` is also outside the allowed-command list. |
| Detect implicit decay | Prose that reasons as if a sibling were open without annotating it needs a reader, not this gate. |
| Judge a falsified premise | Advisory by operator ruling and by this chore's own text — no mechanical witness is claimed. |

The remedy it recommends is **subtractive**: stop writing the second copy, because GitHub
renders issue state live. Same shape as GHI #768's ruling for transcribed ADR counts.

## Baseline

`data/ghi_cross_reference_baseline.json`, registered shrink-only in
`data/waiver_ratchet_registry.json`. The five disclosed entries are dated records, not
repair debt.
