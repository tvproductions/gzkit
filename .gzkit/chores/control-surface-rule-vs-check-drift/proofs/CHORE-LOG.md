# CHORE-LOG: control-surface-rule-vs-check-drift

## 2026-05-10T14:20:16-05:00
- Status: FAIL
- Chore: control-surface-rule-vs-check-drift
- Title: Control Surface Audit — Rule Prose vs Promoted Check Parity (Pass C)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [FAIL] `test -f ops/chores/control-surface-rule-vs-check-drift/proofs/promoted-inventory.md` => rc=1 (0.01s) -- exit 1 != 0

```text
```
## 2026-05-10T14:28:07-05:00
- Status: PASS
- Chore: control-surface-rule-vs-check-drift
- Title: Control Surface Audit — Rule Prose vs Promoted Check Parity (Pass C)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/promoted-inventory.md` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/prose-assertions.md` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/check-behaviors.md` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/parity-diff.md` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/summary.md` => rc=0 (0.01s) -- exit 0 == 0

```text
```
## 2026-06-29T21:49:00-05:00
- Status: PASS
- Chore: control-surface-rule-vs-check-drift
- Title: Control Surface Audit — Rule Prose vs Promoted Check Parity (Pass C)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/promoted-inventory.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/prose-assertions.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/check-behaviors.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/parity-diff.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/summary.md` => rc=0 (0.00s) -- exit 0 == 0

```text
```
## 2026-07-07T06:14:57-05:00
- Status: PASS
- Chore: control-surface-rule-vs-check-drift
- Title: Control Surface Audit — Rule Prose vs Promoted Check Parity (Pass C)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/promoted-inventory.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/prose-assertions.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/check-behaviors.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/parity-diff.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/summary.md` => rc=0 (0.00s) -- exit 0 == 0

```text
```
## 2026-07-31T19:07:58-05:00
- Status: PASS
- Chore: control-surface-rule-vs-check-drift
- Title: Control Surface Audit — Rule Prose vs Promoted Check Parity (Pass C)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/promoted-inventory.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/prose-assertions.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/check-behaviors.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/parity-diff.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-rule-vs-check-drift/proofs/summary.md` => rc=0 (0.00s) -- exit 0 == 0

```text
```
## 2026-08-01T17:31:36-06:00
- Status: PASS
- Chore: control-surface-rule-vs-check-drift
- Title: Control Surface Audit — Rule Prose vs Promoted Check Parity (Pass C)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py control-surface-rule-vs-check-drift` => rc=0 (0.09s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py control-surface-rule-vs-check-drift] stdout:
proof-freshness gate — control-surface-rule-vs-check-drift
  audited surfaces:  .gzkit/rules, src/gzkit/governance/trust_audits
  surface last moved: 2026-08-01
  check-behaviors.md           2026-08-01  fresh
  parity-diff.md               2026-08-01  fresh
  promoted-inventory.md        2026-08-01  fresh
  prose-assertions.md          2026-08-01  fresh
  summary.md                   2026-08-01  fresh

PASS: every proof postdates the surfaces it audits.
```
## 2026-08-09T07:21:52-05:00
- Status: PASS
- Chore: control-surface-rule-vs-check-drift
- Title: Control Surface Audit — Rule Prose vs Promoted Check Parity (Pass C)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py control-surface-rule-vs-check-drift` => rc=0 (0.09s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py control-surface-rule-vs-check-drift] stdout:
proof-freshness gate — control-surface-rule-vs-check-drift
  audited surfaces:  .gzkit/rules, src/gzkit/governance/trust_audits
  surface last moved: 2026-08-09
  check-behaviors.md           2026-08-09  fresh
  parity-diff.md               2026-08-09  fresh
  promoted-inventory.md        2026-08-09  fresh
  prose-assertions.md          2026-08-09  fresh
  summary.md                   2026-08-09  fresh

PASS: every proof postdates the surfaces it audits.
```
## 2026-09-19T06:15:19-05:00
- Status: FAIL
- Chore: control-surface-rule-vs-check-drift
- Title: Control Surface Audit — Rule Prose vs Promoted Check Parity (Pass C)
- Lane: lite
- Version: 1.1.0
- Criteria Results:
  - [FAIL] `uv run python scripts/check_proof_freshness.py control-surface-rule-vs-check-drift` => rc=3 (0.18s) -- exit 3 != 0

```text
[uv run python scripts/check_proof_freshness.py control-surface-rule-vs-check-drift] stdout:
proof-freshness gate — control-surface-rule-vs-check-drift
  audited surfaces:  .gzkit/rules, src/gzkit/governance/trust_audits
  surface last moved: 2026-09-19
  check-behaviors.md           2026-08-09  STALE
  parity-diff.md               2026-08-09  STALE
  promoted-inventory.md        2026-08-09  STALE
  prose-assertions.md          2026-08-09  STALE
  summary.md                   2026-08-09  STALE
[uv run python scripts/check_proof_freshness.py control-surface-rule-vs-check-drift] stderr:
POLICY BREACH:
  .gzkit/chores/control-surface-rule-vs-check-drift/proofs/check-behaviors.md was last committed 2026-08-09, before its audited surface last moved (2026-09-19).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the control-surface-rule-vs-check-drift audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
  .gzkit/chores/control-surface-rule-vs-check-drift/proofs/parity-diff.md was last committed 2026-08-09, before its audited surface last moved (2026-09-19).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the control-surface-rule-vs-check-drift audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
  .gzkit/chores/control-surface-rule-vs-check-drift/proofs/promoted-inventory.md was last committed 2026-08-09, before its audited surface last moved (2026-09-19).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the control-surface-rule-vs-check-drift audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
  .gzkit/chores/control-surface-rule-vs-check-drift/proofs/prose-assertions.md was last committed 2026-08-09, before its audited surface last moved (2026-09-19).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the control-surface-rule-vs-check-drift audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
  .gzkit/chores/control-surface-rule-vs-check-drift/proofs/summary.md was last committed 2026-08-09, before its audited surface last moved (2026-09-19).
    Why: this chore's acceptance previously gated on `test -f`, which passes forever once a report exists and cannot see that the evidence now describes a surface that has changed.
    Fix: re-run the control-surface-rule-vs-check-drift audit and commit refreshed proofs. Touching the file without redoing the analysis restores the green-by-construction gate this replaced.
```
