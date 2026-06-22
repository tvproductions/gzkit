# OBPI-0.0.74-12-mx-gates-as-sensors

## Context

OBPI: OBPI-0.0.74-12-mx-gates-as-sensors
Parent ADR: ADR-0.0.74-mx-mode-maintenance-hangar (Decision item 12)
Lane: Heavy

Prerequisite state:
- src/gzkit/mx/checkpoint.py ✅ (OBPI-02 landed)
- src/gzkit/mx/levels.py ✅ (OBPI-11 landed)
- GATE5_INVARIANTS frozenset lives in checkpoint.py (OBPI-03 seeds it; no separate invariants.py required by this brief)

## Objective

Create the single disposition handler (`disposition.py`) mapping each `GZ_<LEVEL>` to its
route per the parent ADR § Decision item 12 matrix. Update `checkpoint.py` to expose a
`resolve()` function that routes a guard's emitted level through the handler, applying
under-marker demotion and gate5_invariants floor pinning. Guards call `resolve()` — they
emit a level (sensor) and receive a Route; they no longer self-decide block/warn.

ADR matrix verbatim:
| GZ_<LEVEL> | → route |
|---|---|
| CRITICAL | AOG → MX hangar (+ GHI + insight) |
| ERROR | block / ground → GHI-fix |
| WARNING | refactor → Chores |
| NOTICE | drift → Chores drain |
| INFO | track |
| DEBUG | steering (not a defect) |

Under-marker: non-floor levels demote to ADVISORY (visible ledger debt);
gate5_invariants pin to CRITICAL (Route: AOG_MX_HANGAR).

## Files

Create:
- `src/gzkit/mx/disposition.py` — the one level→route matrix handler
- `tests/mx/test_disposition.py` — TDD coverage for matrix rows, under-marker demotion, gate5 pin

Modify:
- `src/gzkit/mx/checkpoint.py` — add `resolve(guard_name, emitted_level, project_root) -> Route`

## Steps

### Step 1: Write failing tests (TDD RED)

Author `tests/mx/test_disposition.py` derived strictly from brief Acceptance Criteria.

REQ-12-01 coverage:
- `TestGuardSensorInterface.test_resolve_exists_on_checkpoint` — checkpoint exposes `resolve()` taking (guard_name, level, root) — the sensor API shape. Fails because resolve() doesn't exist yet.

REQ-12-02 matrix row coverage (one subTest per row):
- `TestDispositionMatrix.test_each_matrix_row` — calls `disposition.route(level)` for all six levels; asserts each returns the expected Route enum value. Fails because disposition.py doesn't exist yet.

REQ-12-02 under-marker demotion coverage:
- `TestUnderMarkerDemotion.test_non_floor_demotes_to_advisory` — with an active marker, non-floor guard (e.g. name="gate3-docs", level=WARNING) resolves to Route.ADVISORY via checkpoint.resolve(). Fails because resolve() doesn't exist.
- `TestUnderMarkerDemotion.test_gate5_invariant_pins_critical_route` — with an active marker, gate5_invariant guard (e.g. "gate5-attestation", level=WARNING) resolves to Route.AOG_MX_HANGAR (CRITICAL route). Fails because resolve() doesn't exist.
- `TestUnderMarkerDemotion.test_critical_emitted_stays_aog_under_marker` — with an active marker, a non-floor guard emitting CRITICAL resolves to Route.AOG_MX_HANGAR (CRITICAL is the floor, no demotion). Fails because resolve() doesn't exist.

REQ-12-03: STRUCTURAL-FENCE — proof channel is ADR § Boundary Invariants #2 (no @covers test per brief req_atomic declaration).

Run `uv run -m unittest tests/mx/test_disposition.py -q` → expect failures.

### Step 2: Implement src/gzkit/mx/disposition.py (TDD GREEN Phase 1)

Create the pure level→route matrix handler:

```python
"""MX disposition handler — the single level→route matrix (ADR-0.0.74 item 12).

Pure matrix: no marker awareness, no guard-name state. The shared checkpoint
(checkpoint.resolve) applies under-marker demotion before calling route().
"""
from __future__ import annotations

from enum import Enum
from gzkit.mx import levels


class Route(str, Enum):
    AOG_MX_HANGAR = "aog-mx-hangar"      # CRITICAL
    BLOCK_GHI_FIX = "block-ghi-fix"      # ERROR
    REFACTOR_CHORES = "refactor-chores"  # WARNING
    DRIFT_DRAIN = "drift-drain"          # NOTICE
    TRACK = "track"                      # INFO
    STEERING = "steering"                # DEBUG
    ADVISORY = "advisory"               # under-marker demotion sentinel


_MATRIX: dict[int, Route] = {
    levels.CRITICAL: Route.AOG_MX_HANGAR,
    levels.ERROR: Route.BLOCK_GHI_FIX,
    levels.WARNING: Route.REFACTOR_CHORES,
    levels.NOTICE: Route.DRIFT_DRAIN,
    levels.INFO: Route.TRACK,
    levels.DEBUG: Route.STEERING,
}


def route(level: int) -> Route:
    """Map *level* to its ADR § Decision item 12 matrix route."""
    return _MATRIX.get(level, Route.TRACK)
```

### Step 3: Update src/gzkit/mx/checkpoint.py (TDD GREEN Phase 2)

Add imports and the `resolve()` function to checkpoint.py:

```python
from gzkit.mx import disposition
from gzkit.mx import levels as _levels

def resolve(
    guard_name: str,
    emitted_level: int,
    project_root: Path | None = None,
) -> "disposition.Route":
    """Route guard_name's emitted_level through the disposition handler.

    Under-marker demotion: non-floor guards become ADVISORY (visible ledger debt).
    gate5_invariants pin to CRITICAL regardless of emitted level or marker state.
    """
    if guard_name in GATE5_INVARIANTS:
        return disposition.route(_levels.CRITICAL)
    if marker.is_active(project_root) and emitted_level != _levels.CRITICAL:
        return disposition.Route.ADVISORY
    return disposition.route(emitted_level)
```

Keep `is_advisory()` unchanged (backward compat; existing callers and tests still use it).

### Step 4: Verify tests pass (TDD confirmation)

```bash
uv run -m unittest tests/mx/test_disposition.py -v
```

All tests must be GREEN.

### Step 5: Lint, format, type-check

```bash
uv run gz lint
uv run gz typecheck
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
test -f src/gzkit/mx/disposition.py
test -f tests/mx/test_disposition.py
```

## Notes

- Import direction: `checkpoint → disposition` (not the reverse) — checkpoint owns GATE5_INVARIANTS and marker state.
- `is_advisory()` is kept for backward compat; `resolve()` is the new sensor-interface surface.
- REQ-12-03 (structural-fence) proof channel: ADR § Boundary Invariants #2 entry (already present per OBPI-02/brief). No @covers test authored — req_atomic frontmatter in brief explicitly exempts this REQ.
- ADVISORY is a Route sentinel in disposition.py even though it's returned by checkpoint logic (not the matrix proper); it belongs in the Route enum as the canonical vocabulary for the demotion route.
