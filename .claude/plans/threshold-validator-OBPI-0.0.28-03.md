# Plan: OBPI-0.0.28-03-threshold-validator

**OBPI:** OBPI-0.0.28-03-threshold-validator
**Parent ADR:** ADR-0.0.28 (foundation, heavy lane)
**Objective:** Implement `validate_complexity_thresholds` at `src/gzkit/governance/trust_audits/complexity_thresholds.py`, register the `gz validate --complexity-thresholds` CLI flag, integrate into `gz validate --all` and `gz check`, fail-close (exit 3) on policy breaches, honor the bootstrap-absolutes carve-out for portability checks, ship manpage + runbook updates in the same patch (gate5-runbook-code-covenant), and cover four canonical failure paths with behave scenarios.

## Allowed Files

- `src/gzkit/governance/trust_audits/complexity_thresholds.py` — new validator module
- `src/gzkit/governance/trust_audits/__init__.py` — re-export new validator
- `src/gzkit/cli/parser_maintenance.py` — `--complexity-thresholds` flag registration
- `src/gzkit/commands/validate_cmd.py` — dispatcher wiring + `--all` aggregation + policy-breach error type
- `tests/governance/test_complexity_thresholds_validator.py` — REQ-derived tests
- `features/complexity_thresholds.feature` — behave scenarios with REQ tags
- `docs/user/manpages/gz-validate.md` — manpage section
- `docs/user/runbook.md` — runbook entry under Complexity doctrine surfaces
- `docs/governance/advisory-rules-audit.md` — promote OBPI-01's scorecard entry citation
- Brief (evidence section + Discovery Checklist already authored)

## Steps (TDD)

### Step 1: Write failing tests — TDD RED

`tests/governance/test_complexity_thresholds_validator.py` covering REQ-01 through REQ-07:

- REQ-01: well-formed real rule body validates clean (exit 0, empty error list)
- REQ-02: rule body where any metric lacks a block band fails with named-error listing the metric
- REQ-03: band with `corpus_percentile=80` (off-enum) fails
- REQ-04: citation tuple that does not parse fails
- REQ-05: bootstrap-absolutes section present → portability checks skipped, "bootstrap-mode" warning emitted
- REQ-06: `gz validate --all` and `gz check` both fire the new validator
- REQ-07: manpage section and runbook entry exist (assertion on file content)

Tests use `tempfile`-backed fixtures for malformed rule bodies; one integration test against the real `.gzkit/rules/complexity-thresholds.md`.

### Step 2: Implement validator (TDD GREEN)

`src/gzkit/governance/trust_audits/complexity_thresholds.py`:

```python
"""ADR-0.0.28 complexity-threshold-doctrine validator (OBPI-0.0.28-03)."""

from __future__ import annotations
from pathlib import Path

from pydantic import ValidationError as PydanticValidationError

from gzkit.complexity.measurement import CANONICAL_METRICS
from gzkit.complexity.thresholds import load_threshold_table
from gzkit.core.validation_rules import ValidationError

_RULE_PATH = Path(".gzkit/rules/complexity-thresholds.md")
_BOOTSTRAP_SECTION_HEADING = "## Bootstrap absolutes"
_BOOTSTRAP_MODE_WARNING_TYPE = "complexity_thresholds_bootstrap_mode"


def validate_complexity_thresholds(project_root: Path) -> list[ValidationError]:
    """Validate the canonical complexity-thresholds rule body."""
    rule_path = project_root / _RULE_PATH
    if not rule_path.is_file():
        return [_missing_rule_error(rule_path)]

    errors: list[ValidationError] = []
    try:
        table = load_threshold_table(rule_path)
    except PydanticValidationError as exc:
        errors.append(_loader_failure_error(rule_path, exc))
        return errors  # cannot proceed with downstream checks if loader failed

    errors.extend(_check_metric_coverage(table))
    if _has_bootstrap_section(rule_path):
        errors.append(_emit_bootstrap_warning(rule_path))

    return errors


def _missing_rule_error(rule_path: Path) -> ValidationError: ...
def _loader_failure_error(rule_path, exc): ...
def _check_metric_coverage(table) -> list[ValidationError]: ...
def _has_bootstrap_section(rule_path: Path) -> bool: ...
def _emit_bootstrap_warning(rule_path: Path) -> ValidationError: ...
```

Each helper ≤50 lines. The bootstrap-mode "warning" is emitted as a `ValidationError` with a non-policy-breach error type so it surfaces in operator output but doesn't fail the build.

### Step 3: Register CLI flag

`src/gzkit/cli/parser_maintenance.py`:

```python
ms.add_argument(
    "--complexity-thresholds",
    dest="check_complexity_thresholds",
    action="store_true",
    help="Validate the complexity-thresholds rule body against ADR-0.0.28 invariants.",
)
```

Plus dispatch wiring at line ~575: `check_complexity_thresholds=a.check_complexity_thresholds`.

### Step 4: Wire dispatcher

`src/gzkit/commands/validate_cmd.py`:
- Add `check_complexity_thresholds: bool = False` parameter (lines ~365 and ~1119)
- Add to `checks` dict at ~413
- Add to `_validation_dispatchers` at ~485-499
- Add `"complexity_thresholds"` to the `run_all_scopes` list at ~935
- Add `"complexity_thresholds"` to `_POLICY_BREACH_ERROR_TYPES` at ~966 (the canonical breach type the validator emits when block band missing / off-enum percentile / unparseable citation)
- Add to the second checks dict at ~1320

### Step 5: Author behave scenarios

`features/complexity_thresholds.feature`:

```gherkin
Feature: gz validate --complexity-thresholds enforces ADR-0.0.28 invariants

  @REQ-0.0.28-03-02
  Scenario: rule body where any metric lacks a block band fails closed
    Given a complexity-thresholds rule body where radon_cc is missing the block band
    When I run "gz validate --complexity-thresholds"
    Then the exit code is 3
    And the error names "radon_cc"

  @REQ-0.0.28-03-03
  Scenario: band with off-enum percentile fails closed
    ...

  @REQ-0.0.28-03-04
  Scenario: citation tuple that does not parse fails closed
    ...

  @REQ-0.0.28-03-05
  Scenario: bootstrap-mode rule body emits the bootstrap-mode warning
    ...
```

The fixture rule body is generated in a behave step from a tempfile; the validator runs against the synthetic body via `--rule-path` parameterization (or the existing project root + `_RULE_PATH` is staged).

### Step 6: Manpage + runbook

`docs/user/manpages/gz-validate.md`:

Add a `--complexity-thresholds` section under the existing flag catalogue. Purpose, exit codes, at least one example invocation.

`docs/user/runbook.md`:

Add an entry under "Complexity doctrine surfaces" (next to the existing `complexity-doctrine-links` row) — prescribed verb for "verify the threshold table is well-formed".

### Step 7: Promote scorecard entry

`docs/governance/advisory-rules-audit.md`:

Update rule 51's "Why" column from "Enforced by `gz validate --complexity-thresholds` (OBPI-0.0.28-03 — forthcoming...)" to land the present-tense form once the validator exists. Update the Summary table's narrative line to note OBPI-03 promotion.

### Step 8: Validate

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_complexity_thresholds_validator -v
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name behave -- uv run -m behave features/complexity_thresholds.feature
uv run gz validate --complexity-thresholds
uv run gz validate --all
uv run gz check
uv run gz covers OBPI-0.0.28-03-threshold-validator --json
uv run gz plan audit OBPI-0.0.28-03-threshold-validator
```

## Notes

- **No BDD waiver** — heavy + has-CLI-surface OBPI; behave scenarios are required.
- **Function-size discipline:** decompose into 5 named helpers (loader invocation + per-metric coverage + band shape + citation + bootstrap-mode handling).
- **Stale-path defects** in original brief (`trust_audits.py`, `parser_artifacts.py`, `validate.py`) corrected in Allowed Paths under DO IT RIGHT 1a; class-level fix tracked under GHI #406.
- **Bootstrap-mode warning** is non-policy-breach: ledger records the carve-out is active, operator sees it in output, but `gz check` does not exit 3 because the OBPI-01 rule body explicitly declares the carve-out.
