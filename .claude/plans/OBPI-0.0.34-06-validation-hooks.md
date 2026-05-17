# Plan: OBPI-0.0.34-06-validation-hooks

**OBPI:** OBPI-0.0.34-06-validation-hooks
**ADR:** ADR-0.0.34-agent-control-surface-rendering-substrate
**Checklist Item #6:** "OBPI-0.0.34-06: Validation hooks — every render and every save fires the ADR-0.0.33 fidelity validators; output that fails validation does not land"

## Context

ADR-0.0.33 fidelity validators are landed and importable from
`gzkit.governance.trust_audits` (composite: `validate_surface_fidelity(project_root)`;
individual: `validate_bullet_retention`, `validate_surface_weight`,
`validate_pointer_integrity`, `validate_scenario_reachability`).

Prerequisites verified:
- OBPI-0.0.34-02: `from gzkit.content.render import render` → OK
- OBPI-0.0.34-04: `gz content edit --help` exits 0 → OK
- ADR-0.0.33 validators: `from gzkit.governance.trust_audits import validate_surface_fidelity` → OK

NOTE: Brief's prerequisite check (`from gzkit.validators.fidelity import VALIDATORS`) is
stale — the validators landed at `gzkit.governance.trust_audits`, not `gzkit.validators.fidelity`.
Plan uses the correct module path.

## Files

**New:**
- `src/gzkit/content/validation/__init__.py` — re-exports `validate_render`, `validate_save`
- `src/gzkit/content/validation/hooks.py` — hook implementations + `FidelityHookError`
- `tests/content/test_validation_hooks.py` — tests for all 5 REQs

**Modified:**
- `src/gzkit/content/render/pipeline.py` — add `project_root: Path | None = None`; call render hook before return
- `src/gzkit/commands/content/edit.py` — call save hook after render, before atomic write
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/obpis/OBPI-0.0.34-06-validation-hooks.md` — this brief

## Steps

### Step 1: TDD Red — write tests for hooks.py (none of these pass yet)

Create `tests/content/test_validation_hooks.py` with:
- `TestFidelityHookError` — verify error carries `validator_id` and `violation` fields
- `TestValidateRender`:
  - `test_clean_passes` — mock `validate_surface_fidelity` → `[]` → no raise
  - `test_violation_raises` — mock returns `[ValidationError(type="bullet_retention", ...)]` → raises `FidelityHookError` naming validator id
  - `test_no_warn_and_continue` — patch `logging.warning` → assert not called on failure
- `TestValidateSave` — same three cases as TestValidateRender
- `TestRenderPipelineWired`:
  - `test_render_calls_validate_render` — patch `hooks.validate_render`, call `render(model, vendor, project_root=fake_root)`, assert hook called once with rendered bytes
  - `test_render_fidelity_violation_raises` — patch `hooks.validate_render` to raise → `render()` propagates the error
- `TestEditSaveHookWired`:
  - `test_save_hook_blocks_write_on_violation` — patch `hooks.validate_save` to raise FidelityHookError → `content_edit_cmd` exits 1, no file written
  - `test_save_hook_called_before_write` — patch `hooks.validate_save` as spy → assert called before `staging_path.replace`

Run `uv run -m unittest tests.content.test_validation_hooks -v` — confirm all RED.

### Step 2: TDD Green — implement hooks.py and validation/__init__.py

Create `src/gzkit/content/validation/hooks.py`:

```python
"""Validation hooks — ADR-0.0.34 § Decision item #6 (OBPI-0.0.34-06).

Wires the ADR-0.0.33 fidelity validator suite at two hook points:
  - validate_render: fired by render() after producing bytes, before returning
  - validate_save: fired by gz content edit save-path, after render, before write

Fail-closed: any ValidationError from the suite raises FidelityHookError.
No warn-and-continue path exists.
"""
from __future__ import annotations

from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits import validate_surface_fidelity


class FidelityHookError(Exception):
    """Raised when validation hook detects a fidelity violation.

    Attributes:
        validator_id: The failing validator's type string.
        violation: Human-readable description of the failure.
        errors: Full list of ValidationError from the validator suite.
    """

    def __init__(
        self,
        *,
        validator_id: str,
        violation: str,
        errors: list[ValidationError],
    ) -> None:
        self.validator_id = validator_id
        self.violation = violation
        self.errors = errors
        super().__init__(
            f"Fidelity validation failed [{validator_id}]: {violation}"
        )


def _run_validators(project_root: Path) -> None:
    """Run the ADR-0.0.33 fidelity validator suite; raise FidelityHookError on failure."""
    errors = validate_surface_fidelity(project_root)
    if errors:
        first = errors[0]
        raise FidelityHookError(
            validator_id=first.type,
            violation=first.message,
            errors=errors,
        )


def validate_render(rendered: bytes, *, project_root: Path) -> None:
    """Validate rendered bytes against the ADR-0.0.33 fidelity suite.

    Called by render() after producing bytes, before returning.
    Raises FidelityHookError on any fidelity violation.
    """
    _run_validators(project_root)


def validate_save(rendered: bytes, *, project_root: Path) -> None:
    """Validate rendered bytes against the ADR-0.0.33 fidelity suite.

    Called by gz content edit save-path after render(), before write.
    Raises FidelityHookError on any fidelity violation.
    """
    _run_validators(project_root)
```

Create `src/gzkit/content/validation/__init__.py`:
```python
"""Validation hook entrypoint — re-exports ADR-0.0.33 hook wiring."""
from .hooks import FidelityHookError, validate_render, validate_save
__all__ = ["FidelityHookError", "validate_render", "validate_save"]
```

Run tests → expect most to go GREEN; pipeline wiring tests still RED.

### Step 3: Wire render hook into pipeline.py

Modify `render()` signature to accept `project_root: Path | None = None`.
After `rendered = template.render(**fields).encode("utf-8")`, before `return`:

```python
from gzkit.content import validation
if project_root is not None:
    validation.validate_render(rendered, project_root=project_root)
```

NOTE: `project_root=None` skips validation — used by callers (like tests) that
don't have a project root context. The edit command always passes project_root.

Run `uv run -m unittest tests.content.test_validation_hooks -v` → all GREEN.

### Step 4: Wire save hook into edit.py

After `rendered = render(model, vendor)` (line 107), before staging write:

```python
from gzkit.content import validation
_project_root = file_path.parent
while _project_root.parent != _project_root:
    if (_project_root / ".gzkit").exists():
        break
    _project_root = _project_root.parent
try:
    validation.validate_save(rendered, project_root=_project_root)
except validation.FidelityHookError as exc:
    print(
        f"Fidelity validation failed [{exc.validator_id}]: {exc.violation}\n"
        "File not written.",
        file=sys.stderr,
    )
    sys.exit(1)
```

Run `uv run -m unittest tests.content.test_validation_hooks -v` → all GREEN.

### Step 5: Full quality checks

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --documents
# Grep checks (REQ-04, REQ-05):
rg -n "logger\.warning.*fidelity|logger\.warn.*fidelity" src/gzkit/content/validation/ && exit 1 || true
rg -q "validation" src/gzkit/content/render/pipeline.py
rg -q "validation" src/gzkit/commands/content/edit.py
```

### Step 6: Present OBPI Acceptance Ceremony

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run python -m unittest tests.content.test_validation_hooks -v
rg -n "logger\.warning.*fidelity" src/gzkit/content/validation/ && exit 1 || true
rg -q "validation" src/gzkit/content/render/pipeline.py
rg -q "validation" src/gzkit/commands/content/edit.py
```

## Destination-in-mind

Wrap `validate_surface_fidelity(project_root)` in two named hook functions
(`validate_render`, `validate_save`) in a new `content/validation/hooks.py` module,
then wire both at their named call sites via import+call additions in `pipeline.py`
and `edit.py`. Fail-closed via `FidelityHookError`; no warn-and-continue.

## Rejected Alternatives

1. Calling `validate_surface_fidelity` inline with `Path.cwd()` — unreliable in CI/tests; passing `project_root` explicitly is the established pattern.
2. Creating new byte-level validators — rejected by REQ-04 (wiring-only scope).
3. Making project_root mandatory in `render()` — breaks backward compat with existing callers; optional param with None=skip is safer.
4. Raising pydantic `ValidationError` from hooks — confused with Pydantic's own error type; `FidelityHookError` is clearly typed.

## Notes

- The `project_root` for `validate_save` is discovered by walking up from `file_path` looking for `.gzkit/`, consistent with how other gzkit commands resolve the project root.
- `validate_render` is gated on `project_root is not None` so test callers and render callers that don't supply a project root don't accidentally trigger full-project validation.
- The `rendered` bytes parameter is passed to both hooks but not currently used (the ADR-0.0.33 validators take `project_root` and scan files on disk). The parameter is part of the API for future Era-2 byte-level validation.
