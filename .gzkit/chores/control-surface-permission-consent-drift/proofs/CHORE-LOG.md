# CHORE-LOG: control-surface-permission-consent-drift

## 2026-07-16T13:53:28-04:00
- Status: PASS
- Chore: control-surface-permission-consent-drift
- Title: Control Surface Audit — Rule Prose vs. Permission Standing Consent (Pass D)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/doctrine-map.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/permission-inventory.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/consent-drift.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/unwitnessable.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/summary.md` => rc=0 (0.00s) -- exit 0 == 0

```text
```
## 2026-07-31T19:07:58-05:00
- Status: PASS
- Chore: control-surface-permission-consent-drift
- Title: Control Surface Audit — Rule Prose vs. Permission Standing Consent (Pass D)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/doctrine-map.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/permission-inventory.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/consent-drift.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/unwitnessable.md` => rc=0 (0.00s) -- exit 0 == 0
  - [PASS] `test -f .gzkit/chores/control-surface-permission-consent-drift/proofs/summary.md` => rc=0 (0.00s) -- exit 0 == 0

```text
```
## 2026-08-01T17:31:36-06:00
- Status: PASS
- Chore: control-surface-permission-consent-drift
- Title: Control Surface Audit — Rule Prose vs. Permission Standing Consent (Pass D)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py control-surface-permission-consent-drift` => rc=0 (0.09s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py control-surface-permission-consent-drift] stdout:
proof-freshness gate — control-surface-permission-consent-drift
  audited surfaces:  .gzkit/rules, .claude/settings.json
  surface last moved: 2026-08-01
  consent-drift.md             2026-08-01  fresh
  doctrine-map.md              2026-08-01  fresh
  permission-inventory.md      2026-08-01  fresh
  summary.md                   2026-08-01  fresh
  unwitnessable.md             2026-08-01  fresh

PASS: every proof postdates the surfaces it audits.
```
## 2026-08-09T06:38:34-05:00
- Status: PASS
- Chore: control-surface-permission-consent-drift
- Title: Control Surface Audit — Rule Prose vs. Permission Standing Consent (Pass D)
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run python scripts/check_proof_freshness.py control-surface-permission-consent-drift` => rc=0 (0.09s) -- exit 0 == 0

```text
[uv run python scripts/check_proof_freshness.py control-surface-permission-consent-drift] stdout:
proof-freshness gate — control-surface-permission-consent-drift
  audited surfaces:  .gzkit/rules, .claude/settings.json
  surface last moved: 2026-08-09
  consent-drift.md             2026-08-09  fresh
  doctrine-map.md              2026-08-09  fresh
  permission-inventory.md      2026-08-09  fresh
  summary.md                   2026-08-09  fresh
  unwitnessable.md             2026-08-09  fresh

PASS: every proof postdates the surfaces it audits.
```
