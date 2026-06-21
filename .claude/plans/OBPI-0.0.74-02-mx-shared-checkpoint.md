# Plan: OBPI-0.0.74-02-mx-shared-checkpoint

**OBPI:** OBPI-0.0.74-02-mx-shared-checkpoint
**ADR:** ADR-0.0.74-mx-mode-maintenance-hangar (Heavy / Foundation)
**Checklist item #2 (verbatim):** "The shared checkpoint — single place code reads the marker and drops guards to advisory except gate5_invariants; funnel inventory + fence test that every fail-closed funnel consults it; unit tests"

## Context

OBPI-01 (the marker file) has landed: `src/gzkit/mx/marker.py` and `src/gzkit/mx/__init__.py` exist. The marker API exposes `marker.is_active(project_root)` (cheap presence check) and `marker.read(project_root)` (full payload). No checkpoint module exists yet; no funnel in `validate_cmd.py` consults MX state.

## Files

**Created:**
- `src/gzkit/mx/checkpoint.py` — the shared checkpoint
- `tests/mx/test_checkpoint.py` — unit tests covering REQ-01, REQ-02

**Modified:**
- `src/gzkit/commands/validate_cmd.py` — wire one fail-closed funnel through the checkpoint (proves the wiring contract; REQ-03 structural-fence proof)

**Evidence recording only:**
- `docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-02-mx-shared-checkpoint.md`

## Steps

### Step 1: TDD Red — Write tests first (before implementation)

Create `tests/mx/test_checkpoint.py` with:

- `TestInHangar.test_ordinary_guard_is_advisory` — with an active marker, `is_advisory("gate3-docs")` returns True [REQ-01]
- `TestInHangar.test_gate5_invariant_stays_fail_closed` — with an active marker, `is_advisory("gate5-attestation")` returns False (stays fail-closed) [REQ-01]
- `TestOutsideHangar.test_no_marker_ordinary_guard_not_advisory` — without marker, `is_advisory("gate3-docs")` returns False (strict no-op) [REQ-02]
- `TestOutsideHangar.test_no_marker_gate5_invariant_not_advisory` — without marker, `is_advisory("gate5-attestation")` returns False [REQ-02]

Tests use `unittest.mock.patch("gzkit.mx.marker.is_active")` to control marker state without filesystem side-effects. Decorators: `@covers("REQ-0.0.74-02-01")` and `@covers("REQ-0.0.74-02-02")`.

### Step 2: TDD Green — Implement checkpoint.py

Create `src/gzkit/mx/checkpoint.py`:

```python
"""MX shared checkpoint — the single place code reads the marker and resolves guard severity.

ADR-0.0.74 Decision item #2.
"""
from __future__ import annotations
from gzkit.mx import marker

GATE5_INVARIANTS: frozenset[str] = frozenset({
    "gate5-attestation",
    "operator-pii",
    "secrets",
    "ledger-integrity",
})

def is_advisory(guard_name: str, project_root=None) -> bool:
    """True when guard_name should be advisory (not fail-closed) in context.

    - gate5_invariants: always False regardless of MX state.
    - Outside the hangar (no marker): always False — strict no-op.
    - Inside the hangar (marker present): True for all non-gate5_invariant guards.
    """
    if guard_name in GATE5_INVARIANTS:
        return False
    return marker.is_active(project_root)
```

### Step 3: Wire one funnel in validate_cmd.py

Find the dispatch path where a scoped validator's errors produce `raise SystemExit(3)`. Add a checkpoint consultation: when errors are non-empty and the scope name is NOT a gate5_invariant, if `checkpoint.is_advisory(scope_name)` returns True, demote the exit to advisory (exit 0 with a warning) rather than fail-closed (exit 3).

The concrete target is the `_collect_errors`/`validate()` dispatch that reads scope entries and raises SystemExit. A minimal, surgical wire: import `checkpoint` at the top of `validate_cmd.py`, and in the loop that processes validation results for a scope, insert `if checkpoint.is_advisory(scope.stem): continue` before the append-to-errors step.

### Step 4: Quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

## Verification

```bash
test -f src/gzkit/mx/checkpoint.py
test -f tests/mx/test_checkpoint.py
uv run gz arb step --name unittest -- uv run -m unittest tests.mx.test_checkpoint -v
```

## Notes

- `req_atomic:` is declared in the brief — all three REQs ship as one `checkpoint.py` write plus one `test_checkpoint.py` write; no task subdivision needed.
- REQ-03 [structural-fence] is proved structurally: the validate_cmd.py wiring IS the fence proof that at least one funnel consults the checkpoint. The parent ADR § Boundary Invariants is the proof channel.
- Gate5_invariant names ("gate5-attestation", "operator-pii", "secrets", "ledger-integrity") match the ADR's stated never-relax list. OBPI-03 will formally define these as a code constant; this OBPI seeds the set.
- No new dependencies added; checkpoint imports only `gzkit.mx.marker` (already in the mx package).
