# Plan: OBPI-0.0.33-04-scenario-reachability-validator

**OBPI slug:** `OBPI-0.0.33-04-scenario-reachability-validator`
**Parent ADR:** `ADR-0.0.33-agent-control-surface-fidelity` (foundation, heavy lane)
**Brief:** `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/obpis/OBPI-0.0.33-04-scenario-reachability-validator.md`

## Objective

Implement `gz validate --scenario-reachability`: an advisory Era-1 validator
that exits 0 with a stderr advisory when the loading-scenarios registry is
absent, and in Era-2 (registry present) warns on orphan bullets and exits 3
only on schema violations.

## Context

OBPIs 01-03 of ADR-0.0.33 implemented bullet-retention, surface-weight, and
pointer-integrity validators using a consistent pattern:
- Module in `src/gzkit/governance/trust_audits/<scope>.py`
- `validate_<scope>(project_root: Path) -> list[ValidationError]` entry point
- Re-exported from `src/gzkit/governance/trust_audits/__init__.py`
- `--<flag>` registered in `src/gzkit/cli/parser_maintenance.py`
- Wired into `src/gzkit/commands/validate_cmd.py` at four locations

This OBPI follows the identical pattern for `--scenario-reachability`.

The registry (`data/agent-control-surface-scenarios.json`) is NOT created here
— that is owned by ADR-0.0.34. Era-1 state = registry absent = advisory-only.

## Files

**New:**
- `src/gzkit/governance/trust_audits/scenario_reachability.py` — validator module
- `tests/governance/test_scenario_reachability.py` — TDD asset (5 REQ test cases)
- `docs/user/manpages/gz-validate.md` — manpage entry for `--scenario-reachability`

**Modified:**
- `src/gzkit/governance/trust_audits/__init__.py` — re-export `validate_scenario_reachability`
- `src/gzkit/cli/parser_maintenance.py` — add `--scenario-reachability` flag + dispatch kwarg
- `src/gzkit/commands/validate_cmd.py` — wire at 4 locations (param, explicit_scopes, scope runner, policy_breach set + 2 pass-throughs)

## Steps

### Step 1: TDD — Red phase (tests/governance/test_scenario_reachability.py)

Write tests BEFORE the implementation. Derive from the 5 REQs in the brief:

- `TestREQ01_RegistryAbsent`: assert `validate_scenario_reachability(root)` returns `[]`
  and stderr advisory `"scenario-reachability: registry absent (ADR-0.0.34); skipping reachability check"`
  when `data/agent-control-surface-scenarios.json` does not exist.
  Use `@covers("REQ-0.0.33-04-01")` decorator.

- `TestREQ02_RegistryPresentNoOrphans`: use a temp registry fixture where all
  Mechanical/Promotable bullets are covered by at least one scenario corpus set.
  Assert returns `[]` and no orphan warnings.
  Use `@covers("REQ-0.0.33-04-02")` decorator.

- `TestREQ03_RegistryPresentWithOrphans`: fixture with an uncovered bullet.
  Assert returns `[]` (exits 0 — advisory) AND stderr contains
  `"scenario-reachability: orphan bullet"` line.
  Use `@covers("REQ-0.0.33-04-03")` decorator.

- `TestREQ04_RegistryMalformed`: fixture with a registry that fails JSON Schema.
  Assert returns `[ValidationError(type="scenario_reachability")]`.
  Use `@covers("REQ-0.0.33-04-04")` decorator.

- `TestREQ05_PackageExport`: assert
  `gzkit.governance.trust_audits.validate_scenario_reachability` is callable
  (import + attribute check).
  Use `@covers("REQ-0.0.33-04-05")` decorator.

Run `uv run -m unittest tests.governance.test_scenario_reachability -v` → expect
all RED (module not found). Paste output as TDD Red evidence.

### Step 2: Implement src/gzkit/governance/trust_audits/scenario_reachability.py

Follow the `bullet_retention.py` pattern exactly:

```python
"""Scenario-reachability validator — ADR-0.0.33 Invariant 4.

Era-1 behavior: when data/agent-control-surface-scenarios.json is absent,
exit 0 with advisory to stderr.

Era-2 behavior: when registry present, assert every Mechanical/Promotable
bullet (from advisory-rules-audit.md) is reachable from at least one
declared loading scenario. Orphan bullets emit warnings; registry schema
violations exit 3.
"""
```

Key implementation points:
- `_REGISTRY_PATH = Path("data") / "agent-control-surface-scenarios.json"`
- `_SCORECARD_PATH = Path("docs") / "governance" / "advisory-rules-audit.md"`
- Era-1 guard: `if not (project_root / _REGISTRY_PATH).exists(): print advisory to stderr; return []`
- Era-2: load registry JSON, validate against inline JSON Schema (basic list-of-objects shape), then check reachability
- Registry schema: `{"type": "array", "items": {"type": "object", "required": ["name", "corpus"], "properties": {"name": {"type": "string"}, "corpus": {"type": "array", "items": {"type": "string"}}}}}`
- Schema validation failure → `ValidationError(type="scenario_reachability", ...)`
- Reachability: for each bullet, assert at least one scenario's `corpus` list contains the bullet's surface file; if not, print `scenario-reachability: orphan bullet: <bullet_text>` to stderr
- Orphan bullets → warning only (return []), per REQ-0.0.33-04-03
- Output prefix: `scenario-reachability:` on all stderr lines, per REQ-0.0.33-04-05
- Re-use `_parse_scorecard` and `_is_enforced` from `bullet_retention.py` or inline equivalent

Run `uv run -m unittest tests.governance.test_scenario_reachability -v` → expect GREEN.

### Step 3: Re-export in __init__.py

Add to `src/gzkit/governance/trust_audits/__init__.py`:
- Import: `from gzkit.governance.trust_audits.scenario_reachability import validate_scenario_reachability`
- Add `"validate_scenario_reachability"` to `__all__`

Follow exact location pattern of `validate_pointer_integrity` import (lines 85-87, 147).

### Step 4: Register CLI flag in parser_maintenance.py

After the `--pointer-anchors` block (line 585-590), add:
```python
p_validate.add_argument(
    "--scenario-reachability",
    dest="check_scenario_reachability",
    action="store_true",
    help="Scenario-reachability audit: orphan bullets vs loading scenarios (ADR-0.0.33-04).",
)
```

Add to `set_defaults` lambda (after `check_pointer_anchors=a.check_pointer_anchors` at line 673):
```python
check_scenario_reachability=a.check_scenario_reachability,
```

### Step 5: Wire into validate_cmd.py at 4 locations

**Location 1** — `_collect_validation_errors` function signature (after line 422):
```python
check_scenario_reachability: bool = False,
```

**Location 2** — `explicit_scopes` dict (after line 480):
```python
"scenario_reachability": check_scenario_reachability,
```

**Location 3** — `_explicit_scope_runners` lambda (after line 571):
```python
"scenario_reachability": lambda: trust_audits.validate_scenario_reachability(project_root),
```

**Location 4** — `_POLICY_BREACH_ERROR_TYPES` set: do NOT add `scenario_reachability` here — REQ-0.0.33-04-03 states orphan bullets are advisory (exit 0), not policy breach (exit 3). Only schema violations return a `ValidationError`, and those already cause exit 3 via the standard error path.

**Location 5** — `validate()` function signature (after line 1297):
```python
check_scenario_reachability: bool = False,
```

**Location 6** — Pass-through to `_collect_validation_errors` (after line 1367):
```python
check_scenario_reachability,
```

**Location 7** — Second pass-through dict (after line 1511):
```python
"scenario_reachability": check_scenario_reachability,
```

### Step 6: Update manpage docs/user/manpages/gz-validate.md

Add entry for `--scenario-reachability` following the `--pointer-anchors` section pattern:
- Flag name and description
- Exit codes: 0 (clean or advisory-only), 3 (registry schema violation)
- Example invocation

### Step 7: Run quality checks and ceremony

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --scenario-reachability   # must exit 0 with advisory
uv run gz covers OBPI-0.0.33-04-scenario-reachability-validator --json
```

## Verification

```bash
uv run gz validate --scenario-reachability            # Era-1: exit 0 + stderr advisory
uv run -m unittest tests.governance.test_scenario_reachability -v
test -f src/gzkit/governance/trust_audits/scenario_reachability.py
test ! -f data/agent-control-surface-scenarios.json   # registry MUST remain absent
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
```

## Notes

- Composite wiring (`--surface-fidelity`) is owned by OBPI-05; this OBPI does NOT wire into the composite.
- Registry creation (`data/agent-control-surface-scenarios.json`) is owned by ADR-0.0.34; do NOT create it here.
- The `scenario_reachability` error type is NOT added to `_POLICY_BREACH_ERROR_TYPES` because orphan bullets are advisory (exit 0); only schema violations produce `ValidationError`, and exit-3 promotion is deferred to the follow-up `--strict` GHI per ADR-0.0.33 Decision.
- Sibling-ADR scope collisions on `parser_maintenance.py`, `trust_audits/__init__.py`, and `gz-validate.md` are advisory-only per CLI structural check; sequential execution is the correct pattern.
