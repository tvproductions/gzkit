---
id: OBPI-0.0.99-05-citation-drift
parent: ADR-0.0.37-constitutional-invariant-composition
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/governance/brief_reconcile.py
reqs:
  - REQ-0.0.99-05-01
verification:
  - uv run gz validate
citations:
  - - docs/does-not-exist-anywhere.md
    - some-anchor
---
# Test Brief: Citation Drift
## Allowed Paths
- `src/gzkit/governance/brief_reconcile.py`
## Verification
```bash
uv run gz validate
```
## Requirements (FAIL-CLOSED)
REQUIREMENT: test
## Acceptance Criteria
- [ ] REQ-0.0.99-05-01: test
