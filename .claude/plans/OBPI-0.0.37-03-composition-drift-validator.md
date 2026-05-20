# Plan: OBPI-0.0.37-03-composition-drift-validator

**OBPI:** OBPI-0.0.37-03-composition-drift-validator
**Parent ADR:** ADR-0.0.37-constitutional-invariant-composition
**Lane:** Heavy

## Context

Wire OBPI-02's `render_agents_md` renderer into `gz validate` as
`--invariant-coherence`. Fail-closed on byte-drift between rendered registry
bytes and committed AGENTS.md. Emit `composition_rendered` and
`composition_drift_detected` ledger events on every run.

Prerequisites landed (attested_completed): OBPI-0.0.37-01 (registry + schema),
OBPI-0.0.37-02 (renderer).

## Coupled-Surface Coherence Note (AGENTS.md§1a)

`audit_event_schemas` scans `src/gzkit/ledger_events.py` + `src/gzkit/events.py`
and validates against `src/gzkit/schemas/ledger.json`. To satisfy this validator
the plan adds event factory functions to `src/gzkit/ledger_events.py` and schema
entries to `src/gzkit/schemas/ledger.json` in addition to the brief's listed paths.

## Files

### Create
- `src/gzkit/governance/trust_audits/invariant_coherence.py`
- `src/gzkit/governance/events.py`
- `tests/governance/test_invariant_coherence.py`
- `tests/fixtures/invariant_coherence/match.json`
- `tests/fixtures/invariant_coherence/drift.json`
- `.gzkit/schemas/ledger_events.json`

### Modify
- `src/gzkit/governance/trust_audits/__init__.py` — register `validate_invariant_coherence`
- `src/gzkit/commands/validate_cmd.py` — add `check_invariant_coherence` param + runner
- `src/gzkit/cli/parser_maintenance.py` — add `--invariant-coherence` argparse flag
- `src/gzkit/ledger_events.py` — add factory functions (coupled-surface coherence)
- `src/gzkit/schemas/ledger.json` — add event schema entries (coupled-surface coherence)
- `features/constitutional_invariants.feature` — drift-validator scenarios @REQ-0.0.37-03-*
- `docs/governance/advisory-rules-audit.md` — scorecard entry for --invariant-coherence
- `docs/user/manpages/gz-validate.md` — flag documentation (create if absent)

## Steps

### Step 1: Create invariant_coherence.py validator

Create `src/gzkit/governance/trust_audits/invariant_coherence.py`.

```python
"""Composition drift validator: byte-compares rendered registry against committed AGENTS.md.

Emits composition_rendered / composition_drift_detected ledger events (REQ-0.0.37-03-03).
Returns list[ValidationError] — empty on match, one error with unified diff on drift.
"""
from __future__ import annotations

import difflib
from pathlib import Path

from gzkit.core.validation_rules import ValidationError

_AGENTS_MD_PATH = "AGENTS.md"
_TEMPLATE_ROOT = Path(".gzkit") / "templates"


def validate_invariant_coherence(root: Path) -> list[ValidationError]:
    """Re-render registry bytes and byte-compare against committed AGENTS.md.

    Exit semantics (enforced by validate_cmd caller): 0 on match, 3 on drift
    (REQ-0.0.37-03-02). Events emitted via _emit_events (REQ-0.0.37-03-03).
    """
    from gzkit.governance.compose import render_agents_md
    from gzkit.governance.events import emit_composition_rendered, emit_composition_drift_detected
    from gzkit.governance.invariants import load_invariants

    invariants = load_invariants(root)
    template_root = root / ".gzkit" / "templates"
    rendered_bytes = render_agents_md(invariants, template_root)

    agents_path = root / _AGENTS_MD_PATH
    committed_bytes = agents_path.read_bytes() if agents_path.exists() else b""

    emit_composition_rendered(
        root=root,
        invariant_count=len(invariants),
        target=_AGENTS_MD_PATH,
        byte_count=len(rendered_bytes),
    )

    if rendered_bytes == committed_bytes:
        return []

    # Drift case
    rendered_lines = rendered_bytes.decode("utf-8", errors="replace").splitlines(keepends=True)
    committed_lines = committed_bytes.decode("utf-8", errors="replace").splitlines(keepends=True)
    diff_lines = list(difflib.unified_diff(
        committed_lines, rendered_lines,
        fromfile="AGENTS.md (committed)",
        tofile="AGENTS.md (rendered)",
    ))[:50]
    diff_text = "".join(diff_lines)

    emit_composition_drift_detected(
        root=root,
        target=_AGENTS_MD_PATH,
        diff_first_50_lines=diff_text,
    )

    return [
        ValidationError(
            type="invariant_coherence",
            artifact=_AGENTS_MD_PATH,
            message=(
                "AGENTS.md drifted from rendered registry output. "
                f"Run `gz governance render --target agents-md` to regenerate.\n\n"
                f"Diff (first 50 lines):\n{diff_text}"
            ),
        )
    ]
```

### Step 2: Create governance/events.py

Create `src/gzkit/governance/events.py` — thin helpers that write ledger events
for governance-layer operations. Use `gzkit.ledger.Ledger` directly.

Provide:
- `emit_composition_rendered(root, invariant_count, target, byte_count) -> None`
- `emit_composition_drift_detected(root, target, diff_first_50_lines) -> None`

Both look up the ledger path from config and append via `Ledger.append_event`.

### Step 3: Add event factory functions to ledger_events.py (coupled-surface)

Add `composition_rendered_event(...)` and `composition_drift_detected_event(...)`
factory functions to `src/gzkit/ledger_events.py` following the existing pattern
(return `LedgerEvent` with typed fields, `event=` literal string).

### Step 4: Extend src/gzkit/schemas/ledger.json (coupled-surface)

Add two entries under the `events` key:
- `composition_rendered`: fields `invariant_count` (int), `target` (str), `byte_count` (int), `render_ts` (str)
- `composition_drift_detected`: fields `target` (str), `diff_first_50_lines` (str), `render_ts` (str)

### Step 5: Create .gzkit/schemas/ledger_events.json (REQ-5)

Create `.gzkit/schemas/ledger_events.json` with the two event type definitions
per REQ-5 schema (id, name, schema, required-fields format).

### Step 6: Register in trust_audits/__init__.py

Add import and `__all__` entry for `validate_invariant_coherence` in
`src/gzkit/governance/trust_audits/__init__.py`.

### Step 7: Wire --invariant-coherence in validate_cmd.py

Add `check_invariant_coherence: bool = False` parameter to `_run_checks_impl`.
Add `"invariant_coherence": check_invariant_coherence` to `default_scopes` dict
(REQ-6: gz check includes it by default).
Add runner lambda: `lambda: trust_audits.validate_invariant_coherence(project_root)`.

### Step 8: Wire --invariant-coherence in parser_maintenance.py

Add `--invariant-coherence` flag (dest=`check_invariant_coherence`) to the
validate subcommand in `src/gzkit/cli/parser_maintenance.py`, matching the
`--advisor-proof-binding` pattern.
Pass through to `validate_cmd` call at the dispatch site.

### Step 9: Write tests

Create `tests/governance/test_invariant_coherence.py` with:
- `TestMatchNoDrift`: loaded registry bytes match committed AGENTS.md → no errors
- `TestMismatchDrift`: drift → one ValidationError with diff in message
- `TestRegistryLoadError`: invariants dir absent → no errors (graceful empty)
- `TestEventEmissionMatch`: composition_rendered emitted, drift event NOT emitted
- `TestEventEmissionDrift`: both events emitted; composition_drift_detected has diff payload

Each test:
- Uses `tests/fixtures/invariant_coherence/` fixtures
- Decorates with `@covers("REQ-0.0.37-03-0N")` per covers contract

### Step 10: Create fixtures

Create `tests/fixtures/invariant_coherence/`:
- `match.json` — invariant registry + AGENTS.md bytes that match rendered output
- `drift.json` — invariant registry + AGENTS.md bytes that differ

### Step 11: BDD scenarios

Add to `features/constitutional_invariants.feature`:

```gherkin
@REQ-0.0.37-03-01
Scenario: Drift validator exits 0 on matching AGENTS.md
  Given the registry renders to bytes matching the committed AGENTS.md
  When I run `gz validate --invariant-coherence`
  Then the exit code is 0

@REQ-0.0.37-03-02
Scenario: Drift validator exits 3 and shows diff on drift
  Given the committed AGENTS.md differs from the rendered registry output
  When I run `gz validate --invariant-coherence`
  Then the exit code is 3
  And the output contains a unified diff

@REQ-0.0.37-03-03
Scenario: Drift validator emits composition_rendered on every run
  Given any AGENTS.md state
  When I run `gz validate --invariant-coherence`
  Then a composition_rendered ledger event is emitted
```

### Step 12: Update advisory-rules-audit.md

Add a scorecard row for `--invariant-coherence`:
- Classification: Mechanical
- Description: Fail-closed drift check for AGENTS.md vs. rendered registry
- Status: Enforced (gz validate --invariant-coherence, gz check default)

### Step 13: Create/update docs/user/manpages/gz-validate.md

If the file exists, add `--invariant-coherence` flag documentation.
If not, create a stub that documents the flag.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_invariant_coherence -v
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --invariant-coherence
uv run gz check --list-scopes 2>&1 | grep invariant-coherence
```
