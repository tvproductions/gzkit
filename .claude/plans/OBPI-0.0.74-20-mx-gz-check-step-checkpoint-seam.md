# OBPI-0.0.74-20: gz check Step Checkpoint Seam — Implementation Plan

## OBPI

`OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam`

## Parent ADR

`ADR-0.0.74-mx-mode-maintenance-hangar`

## Brief

`docs/design/adr/foundation/ADR-0.0.74-mx-mode-maintenance-hangar/obpis/OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam.md`

## Objective (from brief)

Route the ~37 `gz check` audit steps through the MX checkpoint at ONE seam in
`check()` so every MX-demotable guard resolves its disposition through
`checkpoint.resolve` instead of self-deciding `returncode=3`/`SystemExit(3)`.
Closes GHI #638. Extends ADR-0.0.74 BI#2 to the `gz check` surface.

## Files

- **Modify**: `src/gzkit/commands/quality.py` — guard metadata dict + seam helper + seam in `check()` loop
- **Create**: `tests/mx/test_check_step_checkpoint_seam.py` — live-NC unit tests for REQ-01 through REQ-04

## Destination-in-mind disclosure (gz-plan-audit Step 6a)

Before deep exploration I planned to extend `_build_check_steps()` from a
2-tuple to a 4-tuple `(name, guard_name, emitted_level, runner)`. After reading
the code I found three consuming test files that unpack steps as `(name, _)` —
changing tuple arity breaks them. Those files are outside the brief's Allowed
Paths. To stay within scope and preserve correctness, the plan uses a
**separate `_STEP_GUARD_META` dict** that maps step display names to
`(guard_name, emitted_level)` pairs. The tuple shape stays 2-tuple; no
consuming tests break.

## Rejected alternatives

- **4-tuple `_build_check_steps()`**: breaks `tests/governance/test_closeout_proof_view.py`,
  `test_surface_fidelity_composite.py`, and `test_complexity_doctrine_links.py`
  which unpack as `(name, _)` — outside Allowed Paths.
- **Per-runner `checkpoint.resolve()` calls**: rejected by REQ-02 and ADR §
  Alternatives (a)/(b) — "per-surface opt-in is the vibing surface."
- **Modifying individual `run_*_audit` wrappers**: runners correctly return
  `QualityResult(returncode=3)` for violations; the seam at `check()` is the
  right authority; no runner modification needed.

## Design

### Guard metadata dict

```python
# In src/gzkit/commands/quality.py
from gzkit.mx import levels as _mx_levels

_STEP_GUARD_META: dict[str, tuple[str, int]] = {
    "Lint":                        ("lint",                      _mx_levels.ERROR),
    "Format":                      ("format",                    _mx_levels.ERROR),
    "Typecheck":                   ("typecheck",                 _mx_levels.ERROR),
    "Test":                        ("test",                      _mx_levels.ERROR),
    "Behave":                      ("behave",                    _mx_levels.ERROR),
    "Skill audit":                 ("skill-audit",               _mx_levels.ERROR),
    "Parity check":                ("parity-check",              _mx_levels.ERROR),
    "Readiness audit":             ("readiness-audit",           _mx_levels.ERROR),
    "CLI audit":                   ("cli-audit",                 _mx_levels.ERROR),
    "Unscoped rules":              ("unscoped-rules",            _mx_levels.ERROR),
    "ADR status freshness":        ("adr-status-fresh",          _mx_levels.ERROR),
    "Rendition freshness":         ("rendition-freshness",       _mx_levels.ERROR),
    "Rendition floor coherence":   ("rendition-floor-coherence", _mx_levels.ERROR),
    "Invariant coherence":         ("invariant-coherence",       _mx_levels.ERROR),
    "Session green gate":          ("session-green-gate",        _mx_levels.ERROR),
    "Closeout proof":              ("closeout-proof",            _mx_levels.ERROR),
    "Kind invariance":             ("kind-invariance",           _mx_levels.ERROR),
    "Interview transcripts":       ("interviews",                _mx_levels.ERROR),
    "Receipt shape":               ("receipt-shape",             _mx_levels.ERROR),
    "Orientation freshness":       ("orientation-freshness",     _mx_levels.ERROR),
    "Insights shape":              ("insights-shape",            _mx_levels.ERROR),
    "Instructions files budget":   ("instructions-files-budget", _mx_levels.ERROR),
    "AGENTS.md map conformance":   ("agents-md-map-conformance", _mx_levels.ERROR),
    "Complexity-doctrine links":   ("complexity-doctrine-links", _mx_levels.ERROR),
    "Complexity-thresholds":       ("complexity-thresholds",     _mx_levels.ERROR),
    "REQ kind discipline":         ("req-kind-discipline",       _mx_levels.ERROR),
    "tautological test audit":     ("tautological-test-audit",   _mx_levels.ERROR),
    "Task envelope coherence":     ("task-envelope-coherence",   _mx_levels.ERROR),
    "Lock-handoff coupling":       ("lock-handoff-coupling",     _mx_levels.ERROR),
    "QC binding":                  ("qc-binding",                _mx_levels.ERROR),
    "Fidelity presence":           ("fidelity-presence",         _mx_levels.ERROR),
    "Waiver ratchet":              ("waiver-ratchet",            _mx_levels.ERROR),
    "Handoff documents":           ("handoff-documents",         _mx_levels.ERROR),
    "Preflight":                   ("preflight",                 _mx_levels.ERROR),
    "Surface fidelity":            ("surface-fidelity",         _mx_levels.ERROR),
    "Line endings":                ("line-endings",              _mx_levels.ERROR),
    "Dispatch attestation":        ("dispatch-attestation",      _mx_levels.ERROR),
}
```

None of the current step guard_names map to `GATE5_INVARIANTS` members
(`gate5-attestation`, `secrets`, `operator-pii`, `ledger`, `grader-gaming`).
All current steps demote under the marker. Future steps that ARE floor members
inherit the floor pin automatically via `checkpoint.resolve`.

### Seam helper

```python
def _apply_mx_seam(
    result: QualityResult,
    guard_name: str,
    emitted_level: int,
    project_root: pathlib.Path,
) -> QualityResult:
    """Apply checkpoint resolution to a step result — the one seam for all steps.

    If the result carries returncode=3 (policy breach) and the resolved route is
    advisory (non-grounding), demote: return a success result so the aggregator
    does not block.  gate5_invariants members always resolve to a grounding route
    regardless of marker state (checkpoint pins them to CRITICAL).
    """
    if result.returncode != 3:
        return result
    from gzkit.mx import checkpoint, disposition  # noqa: PLC0415 — lazy for test isolation
    route = checkpoint.resolve(guard_name, emitted_level, project_root)
    if disposition.grounds(route):
        return result
    return QualityResult(
        success=True,
        command=result.command,
        stdout=result.stdout,
        stderr=result.stderr,
        returncode=0,
    )
```

### Seam in `check()` loop

```python
for name, runner in steps:
    progress.advance(name)
    result = runner(project_root)
    guard_name, emitted_level = _STEP_GUARD_META.get(
        name, (name.lower().replace(" ", "-"), _mx_levels.ERROR)
    )
    result = _apply_mx_seam(result, guard_name, emitted_level, project_root)
    results.append((name, result))
```

Fallback: if a step name isn't in `_STEP_GUARD_META` (future step not yet
registered), it gets a kebab-case guard_name derived from the display name and
ERROR level — the safe demotable default.

## Steps

### Step 1 (RED): Create `tests/mx/test_check_step_checkpoint_seam.py`

Mirror the helper pattern from `tests/mx/test_checkpoint.py`:

```python
def _mk_root(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".gzkit").mkdir(parents=True, exist_ok=True)
    return root

def _write_marker(root: Path) -> None:
    marker.write(Marker(session_id="test-session"), root)
```

Test classes:

1. **`TestDemoteUnderMarker`** (covers REQ-01 + REQ-02)
   - `test_non_floor_step_demotes_to_advisory_under_marker` (@covers REQ-0.0.74-20-01)
     - Write marker; call `_apply_mx_seam(failing_result, "test-guard", ERROR, root)`
     - Assert `success=True, returncode=0`
   - `test_non_floor_step_stays_fatal_without_marker` (@covers REQ-0.0.74-20-02)
     - No marker; same call
     - Assert `success=False, returncode=3`

2. **`TestFloorPin`** (covers REQ-03)
   - `test_gate5_invariant_stays_fatal_under_marker` (@covers REQ-0.0.74-20-03)
     - Write marker; for each `invariant in GATE5_INVARIANTS`:
       - Call `_apply_mx_seam(failing_result, invariant, ERROR, root)`
       - Assert `success=False, returncode=3`

3. **`TestExcludedPaths`** (covers REQ-04)
   - `test_sensitivity_handler_not_in_step_list` (@covers REQ-0.0.74-20-04)
     - Import `_build_check_steps`; extract guard_names via `_STEP_GUARD_META`
     - Assert no guard_name matches "sensitivity" or related excluded names
   - `test_excluded_guard_names_not_in_step_guard_meta`
     - Assert `_STEP_GUARD_META` contains no key whose guard_name is in
       `{"sensitivity", "gate5-attestation-lane-kind"}` (excluded policy paths)

Run: `uv run -m unittest tests.mx.test_check_step_checkpoint_seam`
**Expect RED** (AttributeError: `_apply_mx_seam` not defined)

### Step 2 (GREEN): Implement in `src/gzkit/commands/quality.py`

1. Add lazy import at top of module: `from gzkit.mx import levels as _mx_levels`
2. After `CheckStepRunner` type alias, add `_STEP_GUARD_META` dict (see Design above)
3. After `_STEP_GUARD_META`, add `_apply_mx_seam()` module-level function (see Design above)
4. In `check()` loop body (after `result = runner(project_root)`, before `results.append`):
   ```python
   guard_name, emitted_level = _STEP_GUARD_META.get(
       name, (name.lower().replace(" ", "-"), _mx_levels.ERROR)
   )
   result = _apply_mx_seam(result, guard_name, emitted_level, project_root)
   ```

No changes to `_build_check_steps()` tuple shape, `_gz_check_cmd_steps()`,
`gz_check_cmd.steps`, `quality.py` runners, or `validate_cmd.py` solo handlers.

Run: `uv run -m unittest tests.mx.test_check_step_checkpoint_seam`
**Expect GREEN**

### Step 3: Verify quality gates

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
uv run mkdocs build --strict
uv run gz covers OBPI-0.0.74-20-mx-gz-check-step-checkpoint-seam --json
```

## REQ coverage map

| REQ | Kind | Proof channel | Test |
|-----|------|---------------|------|
| REQ-0.0.74-20-01 | BEHAVIOR | `@covers` | `TestDemoteUnderMarker.test_non_floor_step_demotes_to_advisory_under_marker` |
| REQ-0.0.74-20-02 | BEHAVIOR | `@covers` | `TestDemoteUnderMarker.test_non_floor_step_stays_fatal_without_marker` |
| REQ-0.0.74-20-03 | BEHAVIOR | `@covers` | `TestFloorPin.test_gate5_invariant_stays_fatal_under_marker` |
| REQ-0.0.74-20-04 | BEHAVIOR | `@covers` | `TestExcludedPaths.test_sensitivity_handler_not_in_step_list` |
| REQ-0.0.74-20-05 | STRUCTURAL-FENCE | Parent ADR BI#2 | (no test — fence proof via BI#2 citing OBPI-20) |

## Confidence assessment

**98%** — the design is clear, all dependencies are verified (checkpoint, disposition,
marker, GATE5_INVARIANTS modules exist and work), and the tuple-backward-compatibility
issue is resolved by the dict approach. Minor uncertainty: `_mx_levels` lazy import
vs top-level import interaction with ruff; will verify after implementation.
