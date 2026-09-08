# Ledger Vocabulary Inertness

Asks of the **ledger** what Pass D asks of validators: does a declared thing
actually happen? An event type declared in `src/gzkit/schemas/ledger.json` that
never appears in `.gzkit/ledger.jsonl` requires either disclosure or freshly
verified execution of its registered real producer in a disposable project.

## Commands

```bash
# Both dimensions
uv run python src/gzkit/chores/ledger-vocabulary-inertness/check_ledger_inertness.py --report

# Enforcement — exit 3 without live use, disclosure, or verified isolated execution
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

Isolated execution is run afresh and checks the typed persisted subject and
contract. Its structured observation is separate from live ledger counts.
Old reports cannot satisfy the gate, and the project ledger remains untouched.

## Baseline

`data/ledger_vocabulary_grandfather.json`, registered shrink-only in
`data/waiver_ratchet_registry.json`.
