---
id: OBPI-0.0.99-01-allowlist-drift
parent: ADR-0.0.37-constitutional-invariant-composition
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/nonexistent_module.py
reqs:
  - REQ-0.0.99-01-01
verification:
  - uv run gz validate
citations: []
---
# Test Brief: Allowlist Drift
## Allowed Paths
- `src/gzkit/governance/nonexistent_module.py`
## Verification
```bash
uv run gz validate
```
## Requirements (FAIL-CLOSED)
REQUIREMENT: Test requirement one
## Acceptance Criteria
- [ ] REQ-0.0.99-01-01: test
