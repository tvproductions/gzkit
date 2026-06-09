# Plan: OBPI-0.0.68-02-session-green-gate-validator

**OBPI:** OBPI-0.0.68-02-session-green-gate-validator
**Parent ADR:** ADR-0.0.68-green-between-sessions-gate
**Lane:** Heavy

## Context

ADR-0.0.68 Decision item #2 (verbatim):
> "Implement `gz validate --session-green-gate` as a fail-closed floor — parse
> `.pre-commit-config.yaml`, exit 3 if no `stages: [pre-push]` hook running `gz check`
> is declared, wire the scope into the `gz check` default scope, add the manpage/docs
> and a fail-close regression test (Heavy)"

Decision item #3 (self-referential wiring):
> "That validator is itself part of the `gz check` default scope, so deleting the
> pre-push declaration makes the NEXT `gz check` go red and surface it — the floor
> enforces its own wiring."

Precedent: `--adr-status-fresh` (run_adr_status_fresh_audit in quality.py → audit_adr_status_fresh in trust_audits/taxonomy.py → registered in validate_cmd.py explicit_scopes + opt_in_scopes → flag in parser_maintenance.py → step in _build_check_steps()).

OBPI-0.0.68-01 is `attested_completed` — the pre-push hook declaration is present in `.pre-commit-config.yaml`. This is the green-path fixture.

## Destination-In-Mind (Plan-Before-Exploration Disclosure)

Before writing this plan I concluded: add a new `src/gzkit/governance/trust_audits/session_green_gate.py` module containing `audit_session_green_gate(project_root)` that parses `.pre-commit-config.yaml` via `yaml.safe_load()` and returns a `ValidationError` list. Wire it exactly like `audit_adr_status_fresh`: into `trust_audits/__init__.py`, `validate_cmd.py` `_collect_errors()` + `_explicit_scope_runners()` + `_resolve_scopes()` + `validate()`, `parser_maintenance.py` `--session-green-gate` flag, and `commands/quality.py` `_build_check_steps()`.

## Rejected Alternatives

1. **Embed logic in taxonomy.py** — rejected: that module handles ADR taxonomy; mixing the pre-commit parse concern there violates single-concern discipline.
2. **Inline YAML parse in validate_cmd.py** — rejected: audit logic belongs in the trust_audits layer (consistent with every other scope).
3. **Reuse `_pre_push_gz_hooks()` from tests/test_pre_push_hook.py** — rejected: test helpers cannot be imported from production code.

## Files

- `src/gzkit/governance/trust_audits/session_green_gate.py` (**NEW**)
- `src/gzkit/governance/trust_audits/__init__.py` (add re-export)
- `src/gzkit/quality.py` (add `run_session_green_gate_audit`)
- `src/gzkit/commands/validate_cmd.py` (wire `check_session_green_gate` throughout)
- `src/gzkit/cli/parser_maintenance.py` (register `--session-green-gate` flag)
- `src/gzkit/commands/quality.py` (add step to `_build_check_steps()`)
- `docs/user/manpages/validate.md` (document new scope)
- `tests/test_session_green_gate_validator.py` (**NEW**, fail-close regression tests)

## Steps

### Step 1: TDD RED — Write failing tests

Create `tests/test_session_green_gate_validator.py` covering:

- `TestAuditSessionGreenGateRedPath` (REQ-0.0.68-02-01): write a temp `.pre-commit-config.yaml` without a `stages: [pre-push]` hook running `gz check` → `audit_session_green_gate(tmp_root)` returns a non-empty list with `type="session_green_gate"`.
- `TestAuditSessionGreenGateGreenPath` (REQ-0.0.68-02-01): write a temp `.pre-commit-config.yaml` with the hook → `audit_session_green_gate(tmp_root)` returns `[]`.
- `TestAuditSessionGreenGateUnparseable` (REQ-0.0.68-02-01): write a temp invalid YAML → returns non-empty list (fail-closed for unparseable config).
- `TestAuditSessionGreenGateMissingFile` (REQ-0.0.68-02-01): no `.pre-commit-config.yaml` → returns non-empty list (fail-closed for missing file).
- `TestSessionGreenGateInCheckScope` (REQ-0.0.68-02-02): import `_build_check_steps` from `gzkit.commands.quality` → assert a step tuple with key `"Session green gate"` exists in the list.

Run tests → observe RED (ImportError on `audit_session_green_gate`).

### Step 2: GREEN — Implement audit logic

Create `src/gzkit/governance/trust_audits/session_green_gate.py`:

```python
from __future__ import annotations
from pathlib import Path
import yaml
from gzkit.core.validation_rules import ValidationError

_RECOVERY = (
    "Recovery: declare a 'pre-push' stage hook running 'gz check' in "
    ".pre-commit-config.yaml (see ADR-0.0.68 / OBPI-0.0.68-01)."
)

def audit_session_green_gate(project_root: Path) -> list[ValidationError]:
    """Fail closed when .pre-commit-config.yaml declares no pre-push gz check hook."""
    config_path = project_root / ".pre-commit-config.yaml"
    if not config_path.exists():
        return [ValidationError(
            type="session_green_gate",
            artifact=".pre-commit-config.yaml",
            message=f"Missing .pre-commit-config.yaml — no pre-push gz check hook declared. {_RECOVERY}",
        )]
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except Exception:
        return [ValidationError(
            type="session_green_gate",
            artifact=".pre-commit-config.yaml",
            message=f"Unparseable .pre-commit-config.yaml — treated as violation (fail-closed). {_RECOVERY}",
        )]
    if not isinstance(config, dict):
        return [ValidationError(
            type="session_green_gate",
            artifact=".pre-commit-config.yaml",
            message=f"Invalid .pre-commit-config.yaml structure. {_RECOVERY}",
        )]
    all_hooks = [h for repo in config.get("repos", []) for h in repo.get("hooks", [])]
    pre_push_gz_hooks = [
        h for h in all_hooks
        if "pre-push" in (h.get("stages") or []) and "gz check" in h.get("entry", "")
    ]
    if not pre_push_gz_hooks:
        return [ValidationError(
            type="session_green_gate",
            artifact=".pre-commit-config.yaml",
            message=f"No stages: [pre-push] hook running 'gz check' declared. {_RECOVERY}",
        )]
    return []
```

### Step 3: GREEN — Wire trust_audits/__init__.py

Add to `src/gzkit/governance/trust_audits/__init__.py`:
```python
from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate
```
And add `"audit_session_green_gate"` to `__all__`.

### Step 4: GREEN — Add run_session_green_gate_audit to quality.py

Add after `run_adr_status_fresh_audit`:
```python
def run_session_green_gate_audit(project_root: Path) -> QualityResult:
    """Run the session-green-gate declaration audit (ADR-0.0.68 / OBPI-0.0.68-02).

    Fails closed (exit 3) when .pre-commit-config.yaml declares no
    stages: [pre-push] hook running gz check.
    Recovery: add the hook (see OBPI-0.0.68-01) and run gz init --install-hooks.
    """
    return run_command("uv run gz validate --session-green-gate", cwd=project_root)
```

### Step 5: GREEN — Register --session-green-gate flag in parser_maintenance.py

After the `--adr-status-fresh` block (~line 501):
```python
    p_validate.add_argument(
        "--session-green-gate",
        dest="check_session_green_gate",
        action="store_true",
        help="pre-push gz check hook must be declared in .pre-commit-config.yaml (ADR-0.0.68 / OBPI-0.0.68-02)",
    )
```

Add `check_session_green_gate=a.check_session_green_gate` to the `validate(...)` call (~line 772 neighborhood).

### Step 6: GREEN — Wire into validate_cmd.py (5 insertion points)

1. `_collect_errors()` params — add `check_session_green_gate: bool = False`
2. `explicit_scopes` dict in `_collect_errors()` — add `"session_green_gate": check_session_green_gate`
3. `_explicit_scope_runners()` dispatch map — add `"session_green_gate": lambda: trust_audits.audit_session_green_gate(project_root)`
4. `_resolve_scopes()` `opt_in_scopes` list — add `"session_green_gate"`
5. `validate()` params + `_collect_errors()` call + `checks` dict — add `check_session_green_gate: bool = False` and pass through

### Step 7: GREEN — Add to _build_check_steps() in commands/quality.py

Import `run_session_green_gate_audit` and add:
```python
        ("Session green gate", run_session_green_gate_audit),
```
After the `("ADR status freshness", ...)` line.

### Step 8: GREEN — Update docs/user/manpages/validate.md

Add `--session-green-gate` scope documentation with its exit-3 contract following the pattern of existing scope entries.

### Step 9: Verify

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests/test_session_green_gate_validator.py -v
uv run gz validate --session-green-gate
uv run gz check
uv run gz cli audit
uv run mkdocs build --strict
```

## Verification

- `uv run gz validate --session-green-gate` exits 0 (project has the hook declared)
- `uv run gz check` exits 0 (session-green-gate is in the check scope)
- `uv run gz cli audit` exits 0 (manpage documents the new flag)
- `uv run mkdocs build --strict` exits 0

## Notes

- Fail-closed pattern: missing config and unparseable config both produce `ValidationError` (not passes)
- `gz check` delegation not frozen validator list — the brief's REQ-03 ensures this
- The `opt_in_scopes` placement in `_resolve_scopes()` is correct: the scope does not activate in the default `run_all` pass (it only activates when `--session-green-gate` is specified explicitly, or when called by `run_session_green_gate_audit` via `gz check`)
