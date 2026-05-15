# Plan: OBPI-0.0.33-02 Surface Weight Validator

**OBPI:** OBPI-0.0.33-02-surface-weight-validator
**ADR:** ADR-0.0.33-agent-control-surface-fidelity
**Lane:** Heavy
**Checklist Item:** #2 — Surface-weight validator (`gz validate --surface-weight`) — snapshot file, waiver schema, fail-closed direction-binding, provisional warning bands, recalibration commitment

## Context

ADR-0.0.33 Invariant 2 requires a surface-weight validator that:
- Computes per-turn corpus line count (AGENTS.md, CLAUDE.md, .claude/rules/**)
- Compares against a floor snapshot in data/surface_weight_floor.json
- Enforces direction-binding: growth past the floor is fail-closed
- Enforces band-based exit codes: green ≤ 1800 (pass), yellow 1801–2200 (fail unless waiver), red >2200 (fail always)
- Validates waiver schema and rejects expired waivers
- Detects floor drift: snapshot timestamp predates most recent recalibration ledger event by >24h

Current measured corpus line count: 1859 (yellow band). Initial snapshot floor will be set to 1859.

## Destination-in-mind disclosure (gz-plan-audit Step 6a)

Approach: follow the bullet_retention.py pattern exactly — single-responsibility module in trust_audits/, re-export from __init__.py, wire into parser_maintenance.py and validate_cmd.py, create data files, update manpage.

## Rejected alternatives

- Setting floor to ADR's historical 1768: rejected — bootstrapping with 1768 causes immediate validator failure on current codebase, defeating the bootstrap goal
- Embedding bands in the snapshot file: rejected — bands are pinned constants (ADR Decision), not recalibrated data; they belong in the module constant block
- Using a Pydantic model for the snapshot: rejected — simple JSON with dict read; Pydantic is warranted for the waiver schema but not the scalar snapshot

## Files

### New
- `src/gzkit/governance/trust_audits/surface_weight.py`
- `tests/governance/test_surface_weight.py`
- `data/surface_weight_floor.json`
- `data/surface_weight_waivers.json`

### Modified
- `src/gzkit/governance/trust_audits/__init__.py` (re-export validate_surface_weight)
- `src/gzkit/cli/parser_maintenance.py` (add --surface-weight flag + dispatch)
- `src/gzkit/commands/validate_cmd.py` (add check_surface_weight param + runner)
- `docs/user/manpages/validate.md` (add --surface-weight section)

## Steps

### Step 1: TDD — Write failing tests (Red phase)

Write `tests/governance/test_surface_weight.py` covering all 6 REQs:

- REQ-0.0.33-02-01: corpus at/below floor → exit 0, no warning
  - @covers REQ-0.0.33-02-01
  - Set up temp surface files totaling 100 lines, floor=200 → validate_surface_weight returns []
- REQ-0.0.33-02-02: yellow band (1801–2200) with no active waiver → exit 3 error
  - @covers REQ-0.0.33-02-02
  - Set up corpus at 1850 lines, floor=100, empty waivers → error with type="surface_weight"
- REQ-0.0.33-02-03: red band (>2200) → exit 3 regardless of waiver
  - @covers REQ-0.0.33-02-03
  - Set up corpus at 2300 lines, floor=100, active waiver → still returns error
- REQ-0.0.33-02-04: expired waiver rejected, delta treated as un-waived
  - @covers REQ-0.0.33-02-04
  - Set up yellow band corpus, waiver with past expiry date → error (waiver doesn't help)
- REQ-0.0.33-02-05: floor timestamp predates recalibration event by >24h → exit 3
  - @covers REQ-0.0.33-02-05
  - Set up floor snapshot timestamped 2 days ago, ledger has recalibration event yesterday → error type="surface_weight"
- REQ-0.0.33-02-06: validate_surface_weight importable from gzkit.governance.trust_audits
  - @covers REQ-0.0.33-02-06
  - from gzkit.governance.trust_audits import validate_surface_weight; assert callable

All tests use TempDirectory / tmp_path pattern with synthetic surface files and synthetic data files. No filesystem mutation of the real codebase.

### Step 2: Implement surface_weight.py (Green phase)

Create `src/gzkit/governance/trust_audits/surface_weight.py`:

```python
"""Surface-weight validator — ADR-0.0.33 Invariant 2.

Computes the per-turn surface corpus line count (AGENTS.md, CLAUDE.md,
.claude/rules/**), reads the direction-binding floor from
data/surface_weight_floor.json, and enforces:
  - current <= floor -> exit 0 (no warning)  [REQ-0.0.33-02-01]
  - yellow band (1801-2200) without active waiver -> exit 3  [REQ-0.0.33-02-02]
  - red band (>2200) -> exit 3 regardless of waivers  [REQ-0.0.33-02-03]
  - expired waivers rejected  [REQ-0.0.33-02-04]
  - floor drift (timestamp predates recalibration event by >24h) -> exit 3  [REQ-0.0.33-02-05]
"""
```

Constants block (pinned by ADR Decision):
```python
_GREEN_CEILING = 1800
_YELLOW_CEILING = 2200
_FLOOR_PATH = Path("data") / "surface_weight_floor.json"
_WAIVERS_PATH = Path("data") / "surface_weight_waivers.json"
_SURFACE_FILES = ("AGENTS.md", "CLAUDE.md")
_RULES_GLOB = ".claude/rules/**/*.md"
_DRIFT_THRESHOLD_HOURS = 24
_RECALIBRATION_EVENT_TYPE = "surface_weight_recalibrated"
```

Functions:
- `validate_surface_weight(project_root: Path) -> list[ValidationError]`
- `_count_surface_lines(project_root: Path) -> int`
- `_load_floor(project_root: Path) -> dict` (reads JSON, returns {lines, timestamp})
- `_load_waivers(project_root: Path) -> list[dict]` (reads JSON array)
- `_has_active_waiver(waivers: list[dict], delta: int) -> bool` (checks expiry + delta coverage)
- `_check_floor_drift(floor: dict, project_root: Path) -> bool` (reads ledger events)

Logic in validate_surface_weight:
1. Load floor (missing → return [] with warning, don't fail-closed on bootstrap)
2. Check floor drift → return error if drifted [REQ-05]
3. Count current lines
4. If current ≤ floor.lines → return [] [REQ-01]
5. Compute delta = current - floor.lines
6. Load waivers
7. If current > _YELLOW_CEILING → return error (red band) [REQ-03]
8. If current > _GREEN_CEILING → yellow band:
   - If active waiver covers delta → return [] (waiver dispensation, exit 0)
   - Else → return error [REQ-02]
9. Return [] (green band, current > floor but ≤ 1800)

Waiver schema (validated inline):
```json
{
  "waiver_id": "string",
  "expires": "YYYY-MM-DD",
  "delta_lines": integer,
  "attestor": "string",
  "reason": "string"
}
```

### Step 3: Re-export from __init__.py

Add to `src/gzkit/governance/trust_audits/__init__.py`:
```python
from gzkit.governance.trust_audits.surface_weight import validate_surface_weight
```
And add `"validate_surface_weight"` to `__all__`.

### Step 4: Wire CLI flag and dispatch

In `src/gzkit/cli/parser_maintenance.py`, add after `--bullet-retention`:
```python
p_validate.add_argument(
    "--surface-weight",
    dest="check_surface_weight",
    action="store_true",
    help="Surface-weight audit: direction-binding floor + warning bands (ADR-0.0.33-02).",
)
```
Add `check_surface_weight=a.check_surface_weight` to the lambda call.

In `src/gzkit/commands/validate_cmd.py`:
- Add `check_surface_weight: bool = False` parameter to `collect_validation_errors()`
- Add `"surface_weight": check_surface_weight` to explicit_scopes
- Add `"surface_weight": lambda: trust_audits.validate_surface_weight(project_root)` to `_explicit_scope_runners()`
- Mirror the same changes in the CLI entry-point function (validate_cmd) and its _other_scopes_active list

### Step 5: Create data files

Create `data/surface_weight_floor.json`:
```json
{
  "lines": 1859,
  "timestamp": "<ISO-8601 now>",
  "note": "Initial snapshot bootstrapped at OBPI-0.0.33-02 completion. Recalibrate via: gz adr emit-receipt with event surface_weight_recalibrated."
}
```

Create `data/surface_weight_waivers.json`:
```json
[]
```

### Step 6: Update manpage and run ARB quality checks

Update `docs/user/manpages/validate.md` to add `--surface-weight` to Usage line and add a description section for the flag (following --bullet-retention pattern).

Then run ARB quality checks:
```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_surface_weight -v
uv run gz arb step --name unittest -- uv run -m unittest -q
```

Verify:
```bash
uv run gz validate --surface-weight
test -f data/surface_weight_floor.json
test -f data/surface_weight_waivers.json
```

## Verification

```bash
uv run gz validate --surface-weight
uv run -m unittest tests.governance.test_surface_weight -v
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
```

## Notes

- The `docs/user/manpages/gz-validate.md` path in the brief maps to `docs/user/manpages/validate.md` in practice (same mapping as OBPI-0.0.33-01 receipt).
- Floor is initialized at 1859 (current measured count), not 1768 (ADR historical). This bootstraps the validator without an immediate failure. The ADR's 1768 was the count at authoring time (2026-04-26); growth since then is grandfathered into the initial snapshot.
- Waivers JSON file bootstraps empty; waivers are added via attested recalibration receipts only.
