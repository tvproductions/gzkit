# Plan: OBPI-0.0.74-03-mx-gate5-invariants

**OBPI:** `OBPI-0.0.74-03-mx-gate5-invariants`
**Parent ADR:** `ADR-0.0.74-mx-mode-maintenance-hangar`
**Lane:** Heavy
**Checklist Item #3:** gate5_invariants — the never-relax floor as a code constant (faked Gate-5 attestation, secrets, operator-PII, ledger integrity, grader-gaming); structural proof the checkpoint cannot downgrade a member below CRITICAL; unit tests

## Context

`checkpoint.py` (OBPI-02) currently defines `GATE5_INVARIANTS` locally with 4 members —
missing `grader-gaming`. The brief requires:
1. A dedicated `src/gzkit/mx/invariants.py` as the canonical home for the full 5-member constant.
2. `checkpoint.py` imports from `invariants.py` instead of defining locally.
3. Unit tests in `tests/mx/test_gate5_invariants.py` covering REQ-01 and REQ-02.

`req_atomic:` is declared in the brief — all three REQs ship as one indivisible unit.

## Files

**Create:**
- `src/gzkit/mx/invariants.py` — `GATE5_INVARIANTS` code constant (5 members)
- `tests/mx/test_gate5_invariants.py` — unit tests for REQ-01 and REQ-02

**Modify:**
- `src/gzkit/mx/checkpoint.py` — remove local `GATE5_INVARIANTS`, import from `invariants.py`

## Steps

### Step 1: Write failing tests (TDD RED)

Author `tests/mx/test_gate5_invariants.py` before implementation:

```python
class TestGate5InvariantsConstant(unittest.TestCase):
    """REQ-0.0.74-03-01: GATE5_INVARIANTS names exactly the five never-relax guards."""

    @covers("REQ-0.0.74-03-01")
    def test_exactly_five_members(self):
        from gzkit.mx.invariants import GATE5_INVARIANTS
        self.assertEqual(len(GATE5_INVARIANTS), 5)

    @covers("REQ-0.0.74-03-01")
    def test_all_five_guards_present(self):
        from gzkit.mx.invariants import GATE5_INVARIANTS
        expected = {"gate5-attestation", "secrets", "operator-pii", "ledger", "grader-gaming"}
        self.assertEqual(GATE5_INVARIANTS, expected)

    @covers("REQ-0.0.74-03-01")
    def test_is_frozenset_code_constant(self):
        from gzkit.mx.invariants import GATE5_INVARIANTS
        self.assertIsInstance(GATE5_INVARIANTS, frozenset)

    @covers("REQ-0.0.74-03-01")
    def test_grader_gaming_is_member(self):
        from gzkit.mx.invariants import GATE5_INVARIANTS
        self.assertIn("grader-gaming", GATE5_INVARIANTS)


class TestCheckpointCannotDowngradeInvariant(unittest.TestCase):
    """REQ-0.0.74-03-02: the checkpoint cannot downgrade a gate5_invariant below CRITICAL."""

    @covers("REQ-0.0.74-03-02")
    def test_invariant_resolves_critical_outside_hangar(self):
        from gzkit.mx import checkpoint, disposition, levels
        from gzkit.mx.invariants import GATE5_INVARIANTS
        for member in GATE5_INVARIANTS:
            with TemporaryDirectory() as tmp:
                root = _mk_root(tmp)
                result = checkpoint.resolve(member, levels.WARNING, root)
                self.assertEqual(result, disposition.Route.FAIL_CLOSED, ...)

    @covers("REQ-0.0.74-03-02")
    def test_invariant_resolves_critical_inside_hangar(self):
        # With active marker, gate5_invariants still pin to CRITICAL
        ...
```

Run: tests fail (module `gzkit.mx.invariants` does not exist) — RED confirmed.

### Step 2: Create `src/gzkit/mx/invariants.py` (TDD GREEN)

```python
"""Gate-5 invariants — the never-relax floor for MX mode.

ADR-0.0.74 Decision item #3: the integrity-class guards as a code constant
(not config). The shared checkpoint reads this constant and structurally
cannot resolve a member below CRITICAL.
"""
from __future__ import annotations

GATE5_INVARIANTS: frozenset[str] = frozenset(
    {
        "gate5-attestation",   # faked Gate-5 attestation
        "secrets",             # secrets leakage guard
        "operator-pii",        # operator-PII protection
        "ledger",              # ledger integrity (validate_cmd scope)
        "grader-gaming",       # grader-gaming (OBPI-13 makes this live)
    }
)
```

Run tests: GREEN.

### Step 3: Update `src/gzkit/mx/checkpoint.py`

- Remove the local `GATE5_INVARIANTS` definition (lines 17-27).
- Add import: `from gzkit.mx.invariants import GATE5_INVARIANTS`
- Keep all logic unchanged — `resolve()` and `is_advisory()` already reference `GATE5_INVARIANTS`.

Run tests: all pass. Existing `test_checkpoint.py` tests continue to pass because they
access `checkpoint.GATE5_INVARIANTS`, which now resolves via the import.

### Step 4: Quality checks

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest -q
uv run gz arb typecheck
```

## Verification

```bash
# Module exists and exports the constant
test -f src/gzkit/mx/invariants.py
test -f tests/mx/test_gate5_invariants.py

# Constant has 5 members including grader-gaming
uv run python -c "from gzkit.mx.invariants import GATE5_INVARIANTS; assert len(GATE5_INVARIANTS) == 5; assert 'grader-gaming' in GATE5_INVARIANTS; print(sorted(GATE5_INVARIANTS))"

# Tests pass
uv run -m unittest tests.mx.test_gate5_invariants -v
```

## Notes

- `req_atomic:` declared in brief — all 3 REQs ship as one unit; no labor subdivision.
- REQ-0.0.74-03-03 is `[structural-fence]` — proof channel is parent ADR § Boundary Invariants #3, not a `@covers` test.
- `grader-gaming`'s floor membership is named here (OBPI-03); its live detector is OBPI-13.
- `checkpoint.py` tests continue to pass unchanged because they access `checkpoint.GATE5_INVARIANTS` which resolves via import.
