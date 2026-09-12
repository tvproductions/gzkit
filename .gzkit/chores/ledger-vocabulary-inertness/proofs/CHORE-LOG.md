# CHORE-LOG: ledger-vocabulary-inertness

## 2026-09-12T12:18:57-05:00
- Status: FAIL
- Chore: ledger-vocabulary-inertness
- Title: Ledger Vocabulary Inertness — never-fired types and paired-event ratios
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [FAIL] `uv run python scripts/check_proof_freshness.py ledger-vocabulary-inertness` => rc=3 (0.07s) -- exit 3 != 0

```text
[uv run python scripts/check_proof_freshness.py ledger-vocabulary-inertness] stdout:
proof-freshness gate — ledger-vocabulary-inertness
  audited surfaces:  src/gzkit/schemas/ledger.json, src/gzkit/ledger_events.py, src/gzkit/events.py
  surface last moved: 2026-09-09
  vocabulary-inertness.md      2026-08-15  STALE
[uv run python scripts/check_proof_freshness.py ledger-vocabulary-inertness] stderr:
POLICY BREACH:
  .gzkit/chores/ledger-vocabulary-inertness/proofs/vocabulary-inertness.md was last committed 2026-08-15, before its audited surface last moved (2026-09-09).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the ledger-vocabulary-inertness audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
```
