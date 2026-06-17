# Plan: OBPI-0.0.73-02-qc-binding-validate-scope

**OBPI:** OBPI-0.0.73-02-qc-binding-validate-scope
**ADR:** ADR-0.0.73-verification-layer-binding-audit
**ADR Checklist Item #2:** `gz validate --qc-binding` scope — behavioral negative-control
(each step ships a fixture it must fail on; the scope runs it) + theater-signature detection
(the six ADR-0.0.37 facade signatures); wired into `gz check`; fail-closed exit 3;
manpage + `gz cli audit` green; unit tests.

## Context

OBPI-01 delivered `src/gzkit/qc_binding.py`: the `QCStep` Pydantic frozen model and
`build_qc_registry()` which derives the registry from `_build_check_steps()`. The
`theater_flags` field (empty list in OBPI-01) is intended for OBPI-02 to populate
via detection; `_STEP_CLASSIFICATION` holds per-step metadata.

This OBPI delivers the audit scope that CONSUMES the registry.

## Files

**CREATE:**
- `src/gzkit/governance/trust_audits/qc_binding.py` — behavioral audit: theater-signature
  detection + NC execution
- `tests/governance/test_qc_binding_scope.py` — unit tests for all 8 REQs

**MODIFY:**
- `src/gzkit/governance/trust_audits/__init__.py` — add `audit_qc_binding` re-export
- `src/gzkit/commands/validate_cmd.py` — add `check_qc_binding: bool = False` param,
  handle in `_other_scopes_active`, dispatch in `_dispatch_early_return_scopes`
- `src/gzkit/cli/parser_maintenance.py` — add `--qc-binding` argument + dispatch kwarg
- `src/gzkit/quality.py` — add `run_qc_binding_audit()` runner
- `src/gzkit/commands/quality.py` — add `("QC binding", run_qc_binding_audit)` to
  `_build_check_steps()`
- `src/gzkit/qc_binding.py` — add `"QC binding"` entry to `_STEP_CLASSIFICATION`
- `docs/user/manpages/validate.md` — add `--qc-binding` section
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-02-qc-binding-validate-scope.md` — evidence

## Steps

### Step 1: Author `src/gzkit/governance/trust_audits/qc_binding.py`

**Design:**

- `THEATER_SIGNATURES: tuple[str, ...]` — the six signature IDs from ADR-0.0.37 facade:
  `"mtime-where-name-says-content"`, `"empty-input-passes"`, `"copy-vs-self"`,
  `"fixture-only"`, `"skip-if-PASS"`, `"prose-graded-by-nothing"`
- `_NEGATIVE_CONTROLS: dict[str, Callable[[], int]]` — module-level registry;
  step_id → callable returning exit code (0=hollow/theater, non-zero=genuine/bound)
- `register_negative_control(step_id, nc)` — register NC for a step (OBPI-06 fills these in)
- `_check_theater_signatures(step: QCStep) -> list[ValidationError]` — iterates
  `step.theater_flags`; each flag in `THEATER_SIGNATURES` → one error
- `_check_negative_control(step, nc_registry=None) -> list[ValidationError]` — looks up NC
  in registry; NC returning 0 → hollow → ValidationError; NC absent → skip
- `audit_qc_binding(project_root, *, nc_registry=None) -> list[ValidationError]` — calls
  `build_qc_registry()`, iterates all steps (theater check), then bound steps (NC check)

**Key invariants:**
- `nc_registry` parameter allows test injection without module-level mutation
- `project_root` kept for registry-protocol parity (unused in OBPI-02; OBPI-06 may use it)
- `build_qc_registry()` `KeyError` → ValidationError on "registry" artifact, not crash

### Step 2: Register in `src/gzkit/governance/trust_audits/__init__.py`

Add:
```python
from gzkit.governance.trust_audits.qc_binding import audit_qc_binding
```

### Step 3: Add `--qc-binding` to `src/gzkit/cli/parser_maintenance.py`

After the `--lock-handoff-coupling` argument block, add:
```python
p_validate.add_argument(
    "--qc-binding",
    dest="check_qc_binding",
    action="store_true",
    default=False,
    help="Behavioral QC-step binding audit (ADR-0.0.73). Exit 0: clean; 3: theater found.",
)
```

In the dispatch call to `validate(...)`, add:
```python
check_qc_binding=a.check_qc_binding,
```

### Step 4: Update `src/gzkit/commands/validate_cmd.py`

- Add `check_qc_binding: bool = False` to `validate()` signature
- Add `check_qc_binding` to `_other_scopes_active` list
- Add dedicated runner `_run_qc_binding_scope(project_root, *, as_json)` (early-return pattern)
- Dispatch in `_dispatch_early_return_scopes()`: when `check_qc_binding and not other_scopes_active`

Runner skeleton:
```python
def _run_qc_binding_scope(project_root: Path, *, as_json: bool) -> None:
    from gzkit.governance.trust_audits.qc_binding import audit_qc_binding
    errors = audit_qc_binding(project_root)
    if as_json:
        print(json.dumps([e.model_dump(exclude_none=True) for e in errors], indent=2))
        raise SystemExit(3 if errors else 0)
    if not errors:
        console.print("[bold]Validated:[/bold] qc-binding\n")
        console.print("[green]✓ No QC theater detected.[/green]")
        raise SystemExit(0)
    console.print("[bold]Validated:[/bold] qc-binding\n")
    console.print(f"[red]❌ {len(errors)} theater finding(s):[/red]\n")
    for e in errors:
        console.print(f"   [red]→[/red] {e.artifact}: {e.message}")
    raise SystemExit(3)
```

### Step 5: Add `run_qc_binding_audit()` to `src/gzkit/quality.py`

After `run_lock_handoff_coupling_audit`:
```python
def run_qc_binding_audit(project_root: Path) -> QualityResult:
    """Run the QC-binding behavioral audit (ADR-0.0.73 / OBPI-0.0.73-02).

    Fails closed (exit 3) when any bound QC step exhibits theater.
    Recovery: gz validate --qc-binding to see per-step details.
    """
    return run_command("uv run gz validate --qc-binding", cwd=project_root)
```

### Step 6: Add step to `src/gzkit/commands/quality.py`

In `_build_check_steps()`, add the import and step:
```python
from gzkit.quality import run_qc_binding_audit
...
("QC binding", run_qc_binding_audit),
```

Position: after `("Lock-handoff coupling", run_lock_handoff_coupling_audit)`.

### Step 7: Add classification to `src/gzkit/qc_binding.py`

In `_STEP_CLASSIFICATION`, add:
```python
"QC binding": ("audit", "src/", "bound", "python_function"),
```

Note: this step IS bound (fails on theater findings) and runs as a python_function.

### Step 8: Create `tests/governance/test_qc_binding_scope.py`

REQ coverage plan:
- REQ-0.0.73-02-01: `test_hollow_step_flagged_as_theater` — creates QCStep with
  NC returning 0; verifies `_check_negative_control` returns 1 error
- REQ-0.0.73-02-02: `test_genuine_step_passes_no_false_positive` — creates QCStep
  with NC returning 1; verifies no errors
- REQ-0.0.73-02-03: `test_six_theater_signatures_each_detected` — for each of the
  6 signature IDs, creates QCStep with `theater_flags=[sig_id]`; verifies error
- REQ-0.0.73-02-04: `test_exit_3_on_theater_exit_0_on_clean` — patches
  `audit_qc_binding` to return errors vs empty; runs `gz validate --qc-binding`
  via `subprocess.run` on a temp dir, checks exit codes
- REQ-0.0.73-02-05: `test_wired_into_gz_check` — imports `_build_check_steps`,
  verifies "QC binding" is in the step names
- REQ-0.0.73-02-06: `test_qc_binding_fail_closed_exit_3` — structural fence:
  verifies "QC binding" is in `_STEP_CLASSIFICATION` with `binding=="bound"`;
  verifies `--qc-binding` is in validate_cmd signature
- REQ-0.0.73-02-07: `test_behavioral_detection_via_negative_control` — verifies
  a step without NC is not flagged (behavioral: must HAVE NC and PASS it to be theater)
- REQ-0.0.73-02-08: `test_cli_alignment_includes_qc_binding` — runs
  `gz validate --cli-alignment` and checks exit 0; alternatively, inspects
  the manpage for `--qc-binding` text

### Step 9: Add `--qc-binding` to `docs/user/manpages/validate.md`

Add entry in the validate manpage following the `--lock-handoff-coupling` section:

```markdown
### `--qc-binding`

Behavioral QC-step binding audit (ADR-0.0.73 / OBPI-0.0.73-02). Flags any bound
QC step that passes its own negative-control fixture (a hollow step) or exhibits
one of the six ADR-0.0.37 theater signatures.

Detection is behavioral, not declarative: each `bound` step must fail its registered
negative control; a step that passes is theater regardless of its docstring.

**Exit codes:** 0 — clean, no theater detected. 3 — theater found (fail-closed).

**Usage:**

```bash
uv run gz validate --qc-binding
uv run gz validate --qc-binding --json
```
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
test -f src/gzkit/governance/trust_audits/qc_binding.py
test -f tests/governance/test_qc_binding_scope.py
uv run gz validate --qc-binding
```

## Notes

- `nc_registry` injection in `audit_qc_binding` is the test-isolation mechanism;
  no module-level registry mutation in tests
- Brief allowlist was amended before this plan was written to include 3 missed
  coupled surfaces: `parser_maintenance.py`, `commands/quality.py`, `qc_binding.py`
- OBPI-06 (self-check + facade regression corpus) registers concrete NCs for all
  existing steps; OBPI-02 ships the infrastructure only
