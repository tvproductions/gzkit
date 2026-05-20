---
id: OBPI-0.0.99-02-discovery-drift
parent: ADR-0.0.37-constitutional-invariant-composition
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/brief_reconcile.py
reqs:
  - REQ-0.0.99-02-01
verification:
  - uv run gz validate
citations: []
---
# Test Brief: Discovery Drift
## Allowed Paths
- `src/gzkit/governance/brief_reconcile.py`
## Discovery Checklist
- [ ] `src/gzkit/governance/does_not_exist_at_all.py`
## Verification
```bash
uv run gz validate
```
## Requirements (FAIL-CLOSED)
REQUIREMENT: Test req one
## Acceptance Criteria
- [ ] REQ-0.0.99-02-01: test
