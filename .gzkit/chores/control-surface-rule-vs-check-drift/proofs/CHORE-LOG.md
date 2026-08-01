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
