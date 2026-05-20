---
id: OBPI-0.0.3-03-test-malformed
parent: ADR-0.0.3-test-malformed
lane: Heavy
status: Draft
allowlist:
  - src/gzkit/some_file.py
reqs: []
verification:
  - uv run gz lint
citations: []
---
# Test Malformed Brief
This brief has an empty reqs list which is invalid.
