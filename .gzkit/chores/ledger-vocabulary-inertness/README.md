# Ledger Vocabulary Inertness

Asks of the **ledger** what Pass D asks of validators: does a declared thing
actually happen? An event type declared in `src/gzkit/schemas/ledger.json` that
never appears in `.gzkit/ledger.jsonl` is vocabulary with no producer.

## Commands

```bash
# Both dimensions
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py --report

# Enforcement — exit 3 on an undisclosed never-fired type
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py

# Re-baseline after draining (refuses to grow)
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py --report --write
```

## Two dimensions, unequal in force

| Dimension | Force | Why |
|---|---|---|
| Never-fired types | **enforced** — shrink-only disclosure | a declared type with no producer records nothing while reading as a modelled fact |
| Paired-event ratios | **reported only** | what a lopsided pair means depends on its producer; the chore names the question, the operator rules |

The reporting restraint is deliberate. See `CHORE.md` § Policy and Guardrails for
the 2026-08-15 case where a correct ratio was given an invented explanation.

## Baseline

`data/ledger_vocabulary_grandfather.json`, registered shrink-only in
`data/waiver_ratchet_registry.json`.
