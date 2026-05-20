---
id: OBPI-0.0.99-03-verb-drift
parent: ADR-0.0.37-constitutional-invariant-composition
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/brief_reconcile.py
reqs:
  - REQ-0.0.99-03-01
verification:
  - uv run gz nonexistentverb --check
citations: []
---
# Test Brief: Verb Drift
## Allowed Paths
- `src/gzkit/governance/brief_reconcile.py`
## Verification
```bash
`gz nonexistentverb --check`
```
## Requirements (FAIL-CLOSED)
REQUIREMENT: test
## Acceptance Criteria
- [ ] REQ-0.0.99-03-01: test
