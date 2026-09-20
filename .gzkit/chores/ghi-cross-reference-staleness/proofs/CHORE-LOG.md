# CHORE-LOG: ghi-cross-reference-staleness

## 2026-09-20T08:01:43-05:00
- Status: PASS
- Chore: ghi-cross-reference-staleness
- Title: GHI Cross-Reference Staleness — decayed sibling-state annotations
- Lane: lite
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py --self-test` => rc=0 (0.03s) -- exit 0 == 0
  - [PASS] `uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py` => rc=0 (6.49s) -- exit 0 == 0

```text
[uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py --self-test] stdout:
self-test: OK
[uv run python .gzkit/chores/ghi-cross-reference-staleness/check_cross_reference_staleness.py] stdout:
transcribed sibling-state annotations: 10
decayed (body asserts OPEN, sibling CLOSED): 5  -> rate 50%
  #799 asserts #533 is open; it is closed
  #894 asserts #883 is open; it is closed
  #894 asserts #877 is open; it is closed
  #930 asserts #929 is open; it is closed
  #969 asserts #889 is open; it is closed

All decay is disclosed.
```
