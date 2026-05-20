---
id: OBPI-0.0.37-05-brief-reconcile-engine
parent: ADR-0.0.37-constitutional-invariant-composition
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/brief_reconcile.py
reqs:
  - REQ-0.0.37-05-01
verification:
  - uv run gz validate --brief-reconcile
citations: []
---
# OBPI-0.0.37-05: Test Brief (Passing)
## Allowed Paths
- `src/gzkit/governance/brief_reconcile.py`
## Verification
```bash
uv run gz validate --brief-reconcile
```
## Requirements (FAIL-CLOSED)
REQUIREMENT: Engine returns ReconcileResult
## Acceptance Criteria
- [ ] REQ-0.0.37-05-01: engine returns ReconcileResult
