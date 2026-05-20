---
id: OBPI-0.0.99-04-req-count-drift
parent: ADR-0.0.37-constitutional-invariant-composition
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/brief_reconcile.py
reqs:
  - REQ-0.0.99-04-01
  - REQ-0.0.99-04-02
verification:
  - uv run gz validate
citations: []
---
# Test Brief: REQ Count Drift
## Allowed Paths
- `src/gzkit/governance/brief_reconcile.py`
## Verification
```bash
uv run gz validate
```
## Requirements (FAIL-CLOSED)
REQUIREMENT: test req one
REQUIREMENT: test req two
## Acceptance Criteria
- [ ] REQ-0.0.99-04-01: only one acceptance criterion
