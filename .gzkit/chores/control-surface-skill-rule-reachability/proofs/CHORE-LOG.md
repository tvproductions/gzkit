# CHORE-LOG: control-surface-skill-rule-reachability

## 2026-05-10T13:51:12-05:00
- Status: FAIL
- Chore: control-surface-skill-rule-reachability
- Title: Control Surface Audit — Skill/Rule Reachability Matrix (Pass B)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [FAIL] `test -f ops/chores/control-surface-skill-rule-reachability/proofs/skill-inventory.md` => rc=1 (0.01s) -- exit 1 != 0

```text
```
## 2026-05-10T14:27:03-05:00
- Status: PASS
- Chore: control-surface-skill-rule-reachability
- Title: Control Surface Audit — Skill/Rule Reachability Matrix (Pass B)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/skill-inventory.md` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/reachability-matrix.md` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/ghi-cross-reference.md` => rc=0 (0.01s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/summary.md` => rc=0 (0.01s) -- exit 0 == 0

```text
```
## 2026-06-29T21:49:00-05:00
- Status: PASS
- Chore: control-surface-skill-rule-reachability
- Title: Control Surface Audit — Skill/Rule Reachability Matrix (Pass B)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/skill-inventory.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/reachability-matrix.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/ghi-cross-reference.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/summary.md` => rc=0 (0.00s) -- exit 0 == 0

```text
```
## 2026-07-07T06:14:57-05:00
- Status: PASS
- Chore: control-surface-skill-rule-reachability
- Title: Control Surface Audit — Skill/Rule Reachability Matrix (Pass B)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/skill-inventory.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/reachability-matrix.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/ghi-cross-reference.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/summary.md` => rc=0 (0.00s) -- exit 0 == 0

```text
```
## 2026-07-31T19:07:58-05:00
- Status: PASS
- Chore: control-surface-skill-rule-reachability
- Title: Control Surface Audit — Skill/Rule Reachability Matrix (Pass B)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/skill-inventory.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/reachability-matrix.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/ghi-cross-reference.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-skill-rule-reachability/proofs/summary.md` => rc=0 (0.00s) -- exit 0 == 0

```text
```
## 2026-08-01T17:31:36-06:00
- Status: PASS
- Chore: control-surface-skill-rule-reachability
- Title: Control Surface Audit — Skill/Rule Reachability Matrix (Pass B)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py control-surface-skill-rule-reachability` => rc=0 (0.08s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py control-surface-skill-rule-reachability] stdout:
proof-freshness gate — control-surface-skill-rule-reachability
  audited surfaces:  .gzkit/rules, .gzkit/skills
  surface last moved: 2026-08-01
  ghi-cross-reference.md       2026-08-01  fresh
  reachability-matrix.md       2026-08-01  fresh
  skill-inventory.md           2026-08-01  fresh
  summary.md                   2026-08-01  fresh

PASS: every proof postdates the surfaces it audits.
```
## 2026-08-09T07:53:57-05:00
- Status: PASS
- Chore: control-surface-skill-rule-reachability
- Title: Control Surface Audit — Skill/Rule Reachability Matrix (Pass B)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py control-surface-skill-rule-reachability` => rc=0 (0.08s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py control-surface-skill-rule-reachability] stdout:
proof-freshness gate — control-surface-skill-rule-reachability
  audited surfaces:  .gzkit/rules, .gzkit/skills
  surface last moved: 2026-08-09
  ghi-cross-reference.md       2026-08-09  fresh
  reachability-matrix.md       2026-08-09  fresh
  skill-inventory.md           2026-08-09  fresh
  summary.md                   2026-08-09  fresh

PASS: every proof postdates the surfaces it audits.
```
