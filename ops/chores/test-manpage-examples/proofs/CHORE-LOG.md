# CHORE-LOG: test-manpage-examples

## 2026-03-21T14:39:26-05:00
- Status: PASS
- Chore: test-manpage-examples
- Title: Test Manpage Examples (Executable Verification)
- Lane: heavy
- Version: 1.0.0
- Criteria Results:
  - [PASS] `uv run gz cli audit` => rc=0 (0.29s) — exit 0 == 0
  - [PASS] `uv run -m unittest -q` => rc=0 (21.65s) — exit 0 == 0

```text
[uv run gz cli audit] stdout:
CLI audit passed.
[uv run -m unittest -q] stdout:
No dispatch data found for OBPI-NONEXISTENT
[uv run -m unittest -q] stderr:
----------------------------------------------------------------------
Ran 961 tests in 21.273s

OK
```
