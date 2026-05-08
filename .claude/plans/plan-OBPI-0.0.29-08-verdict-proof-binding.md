# Plan: OBPI-0.0.29-08-verdict-proof-binding

**OBPI:** OBPI-0.0.29-08-verdict-proof-binding
**Parent ADR:** ADR-0.0.29-complexity-advisor
**Lane:** Heavy
**Kind:** Foundation (parent ADR is foundation; brief-level Gate 5 attestation required)
**Brief:** docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-08-verdict-proof-binding.md

## Context

OBPI-0.0.29-01 landed the `AdvisorDiagnosis` Pydantic model with model-layer
enforcement: `proof: tuple[ProofRange, ...]` is `Field(min_length=1)` plus a
`_check_proof_nonempty` validator. OBPI-0.0.29-02 landed the engine with
engine-layer enforcement: `EngineError` raised before model instantiation when
proof is unavailable. Both layers are first-line defenses but live inside the
runtime path.

This OBPI (08) lands the **third defense layer** as a fail-closed validator
audit at gate-time. `validate_advisor_proof_binding` is the regression
backstop: even if a future refactor weakens the model `min_length=1` constraint
or relaxes the engine pre-instantiation check, this validator catches any
diagnosis that lands in fixtures or ledger events with empty proof. The CLI
flag `--advisor-proof-binding` integrates with `gz validate --all` and
`gz check`, so the audit fires in every pre-merge ARB pipeline.

Three scan scopes:

1. **Fixture scope** — walk `tests/fixtures/advisor/*.json` (vacuously empty
   today; future OBPIs add fixtures), parse each as a diagnosis, assert
   non-empty proof.
2. **Ledger scope** — read `.gzkit/ledger.jsonl`, find
   `intrinsic-complexity-attestation` events whose payload references a
   diagnosis (via the OBPI-07 event shape), cross-check that the cited
   diagnosis has non-empty proof.
3. **Schema scope** — load `src/gzkit/schemas/advisor_diagnosis.json` and
   assert the `proof` property requires `minItems: 1`.

Speculative-marker escape (REQ-6): fixtures explicitly named as negative-case
tests of the empty-proof rejection (the OBPI-01 model test that asserts
`ValidationError` on empty proof) are skipped via a sentinel marker — the
test of the defense is not itself a defect.

## Creates these files

These paths do not exist on disk yet; the plan creates them. Listed explicitly
so the `gz plan audit` non-existence check exempts them per GHI #403:

- `src/gzkit/governance/trust_audits/advisor_proof_binding.py`
- `tests/governance/test_advisor_proof_binding_validator.py`
- `features/advisor_proof_binding.feature`
- `docs/user/manpages/gz-validate.md`
- `features/steps/advisor_proof_binding_steps.py`
- `behave.ini`

## Allowed Files

- `src/gzkit/governance/trust_audits/advisor_proof_binding.py` (new module)
- `src/gzkit/governance/trust_audits/__init__.py` (register the new validator)
- `src/gzkit/cli/parser_maintenance.py` (register `--advisor-proof-binding` flag)
- `src/gzkit/commands/validate_cmd.py` (wire flag, integrate `--all`)
- `tests/governance/test_advisor_proof_binding_validator.py` (new)
- `features/advisor_proof_binding.feature` (new)
- `docs/user/commands/validate.md` (flag section)
- `docs/user/runbook.md` (entry under "Complexity doctrine surfaces")
- `docs/governance/advisory-rules-audit.md` (scorecard entry — Mechanical)
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-08-verdict-proof-binding.md` (evidence sections only)

## Steps

### Step 1: TDD Red — failing unit tests

Author `tests/governance/test_advisor_proof_binding_validator.py` with the
canonical scoped pattern (`unittest`, `TempDBMixin`-style isolation via
`tempfile.TemporaryDirectory`). Each test decorated `@covers("REQ-0.0.29-08-NN")`.

Test cases (all RED at this step — module under test does not exist yet):

- **REQ-01 / REQ-07a** — well-formed fixture diagnosis + valid ledger event +
  conforming JSON Schema → exit 0 / `[]`
- **REQ-02 / REQ-07b** — fixture diagnosis with empty `proof` → returns
  `ValidationError` whose message names the file path + line number
- **REQ-03 / REQ-07c** — `intrinsic-complexity-attestation` event citing a
  diagnosis with empty proof → returns `ValidationError` whose message names
  the event id
- **REQ-04 / REQ-07d** — JSON Schema `proof` property without `minItems: 1`
  (or `min_length`/equivalent constraint) → returns `ValidationError`
- **REQ-06 / REQ-07e** — fixture file with the speculative-marker sentinel
  (e.g. JSON top-level key `"_negative_case": true` or comment marker per
  `.claude/rules/governance-core.md` precedent) → skipped (vacuous pass)
- **REQ-03 / REQ-07f** — integration: `gz validate --all` includes
  `advisor_proof_binding` in scope set; `gz check` invokes the validator
- **REQ-05** — error messages cite file path + line number for fixture
  failures and event id for ledger failures

Tests use `tempfile.TemporaryDirectory` to construct fake project roots
with `tests/fixtures/advisor/` + `.gzkit/ledger.jsonl` + `src/gzkit/schemas/advisor_diagnosis.json`.
Write a fixture-creation helper to keep per-test setup small.

Confirm RED: `uv run -m unittest tests.governance.test_advisor_proof_binding_validator -v`
returns module-import or attribute errors (validator does not exist yet).

### Step 2: Green — implement validator module

Create `src/gzkit/governance/trust_audits/advisor_proof_binding.py`:

```python
"""Fail-closed audit: advisor diagnosis verdict <-> proof binding (OBPI-0.0.29-08).

Defense-in-depth backstop: model-layer enforcement (OBPI-01) and engine-layer
enforcement (OBPI-02) prevent empty-proof diagnoses at runtime; this validator
catches any that nevertheless reach fixtures, ledger events, or the JSON Schema.
"""
from __future__ import annotations

import json
from pathlib import Path

from gzkit.core.validation_rules import ValidationError


_NEGATIVE_CASE_KEY = "_negative_case"  # speculative-marker escape (REQ-6)


def validate_advisor_proof_binding(project_root: Path) -> list[ValidationError]:
    errors: list[ValidationError] = []
    errors.extend(_scan_fixtures(project_root))
    errors.extend(_scan_ledger(project_root))
    errors.extend(_scan_schema(project_root))
    return errors


def _scan_fixtures(project_root: Path) -> list[ValidationError]:
    fixtures_dir = project_root / "tests" / "fixtures" / "advisor"
    if not fixtures_dir.exists():
        return []
    errors: list[ValidationError] = []
    for path in sorted(fixtures_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # invalid JSON belongs to schema validator scope
        if isinstance(data, dict) and data.get(_NEGATIVE_CASE_KEY) is True:
            continue  # speculative-marker escape
        proof = data.get("proof") if isinstance(data, dict) else None
        if not proof:
            line = _locate_proof_line(path) or 1
            errors.append(
                ValidationError(
                    type="advisor_proof_binding",
                    artifact=str(path),
                    message=(
                        f"Advisor diagnosis fixture {path.as_posix()}:{line}: "
                        f"`proof` is empty. Verdict <-> proof binding requires non-empty "
                        f"proof: tuple[ProofRange, ...]."
                    ),
                )
            )
    return errors


def _scan_ledger(project_root: Path) -> list[ValidationError]:
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    # Build a lookup of fixture diagnoses by id (if cited).
    fixtures_by_id = _index_fixtures_by_id(project_root)
    errors: list[ValidationError] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("event") != "intrinsic-complexity-attestation":
            continue
        diagnosis_ref = ev.get("diagnosis_id") or ev.get("diagnosis_ref")
        if not diagnosis_ref:
            continue
        diag = fixtures_by_id.get(diagnosis_ref)
        if diag is None:
            continue  # unresolvable refs are an OBPI-07 concern, not this scope
        if not diag.get("proof"):
            errors.append(
                ValidationError(
                    type="advisor_proof_binding",
                    artifact=ev.get("id", "<unknown>"),
                    message=(
                        f"intrinsic-complexity-attestation event {ev.get('id')!r} "
                        f"cites diagnosis {diagnosis_ref!r} with empty `proof`."
                    ),
                )
            )
    return errors


def _scan_schema(project_root: Path) -> list[ValidationError]:
    schema_path = project_root / "src" / "gzkit" / "schemas" / "advisor_diagnosis.json"
    if not schema_path.exists():
        return []
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [
            ValidationError(
                type="advisor_proof_binding",
                artifact=str(schema_path),
                message=f"advisor_diagnosis.json is not valid JSON: {exc}.",
            )
        ]
    proof_node = (schema.get("properties") or {}).get("proof") or {}
    min_items = proof_node.get("minItems")
    if min_items is None or min_items < 1:
        return [
            ValidationError(
                type="advisor_proof_binding",
                artifact=str(schema_path),
                message=(
                    f"{schema_path.as_posix()}: properties.proof.minItems must be "
                    f">= 1; found {min_items!r}."
                ),
            )
        ]
    return []


def _index_fixtures_by_id(project_root: Path) -> dict[str, dict]:
    """..."""


def _locate_proof_line(path: Path) -> int | None:
    """Best-effort line lookup so the error message can cite a navigable position."""
```

Implementation notes:

- Module ≤300 lines per `.claude/rules/pythonic.md`.
- The `_locate_proof_line` helper does a simple text scan for `"proof"` —
  best-effort; on miss returns `None` and the message degrades to line 1.
- `_index_fixtures_by_id` lifts the `id` field from every fixture (if present)
  for ledger cross-check.
- Speculative-marker escape: top-level JSON key `"_negative_case": true`.
  Documented inline; tested by REQ-07e.

Confirm GREEN: `uv run -m unittest tests.governance.test_advisor_proof_binding_validator -v`
returns all tests passing.

### Step 3: Register validator in `trust_audits/__init__.py`

Add to `src/gzkit/governance/trust_audits/__init__.py`:

```python
from gzkit.governance.trust_audits.advisor_proof_binding import (
    validate_advisor_proof_binding,
)
# ... and append to the explicit __all__ tuple:
"validate_advisor_proof_binding",
```

Mirror the import + `__all__` placement next to `validate_intrinsic_attestation`
(the OBPI-07 sibling) so the registration pattern stays uniform.

### Step 4: Wire CLI flag in `parser_maintenance.py`

Locate the `gz validate` parser block (search for `--intrinsic-attestation`
to find the canonical flag-registration site) and add a sibling flag:

```python
parser.add_argument(
    "--advisor-proof-binding",
    action="store_true",
    help=(
        "Validate that every advisor diagnosis (fixture, ledger-cited, and "
        "JSON Schema) carries non-empty proof. Defense-in-depth backstop "
        "for OBPI-0.0.29-01/02 verdict<->proof enforcement."
    ),
)
```

### Step 5: Wire dispatcher in `validate_cmd.py`

Mechanical mirror of `--intrinsic-attestation` (lines 379, 428, 514, 960,
1144, 1284, 1348 per the grep at plan time). Add `check_advisor_proof_binding`
to the dispatcher signature, the kwarg map, the runner lookup, the
`ALL_SCOPES` tuple, and the upstream `gz check` call site.

Specifically:

- Add `check_advisor_proof_binding: bool = False` parameter
- Add `"advisor_proof_binding": check_advisor_proof_binding` to the scope-bool map
- Add `"advisor_proof_binding": lambda: trust_audits.validate_advisor_proof_binding(project_root)` to the runner map
- Add `"advisor_proof_binding"` to the `ALL_SCOPES` tuple so `--all` fires it
- Propagate the kwarg from the upstream entry point (the CLI binding around line 1144 / 1284)

### Step 6: BDD scenarios in `features/advisor_proof_binding.feature`

Two scenarios mapped to canonical failure paths (REQ-08 mandates these two):

```gherkin
Feature: Advisor proof binding validator
  As a governance maintainer
  I want gate-time enforcement of verdict<->proof binding
  So that no advisor diagnosis lands without grounded proof

  @REQ-0.0.29-08-02
  Scenario: Empty-proof fixture fails fail-closed
    Given an advisor diagnosis fixture at tests/fixtures/advisor/empty.json with empty proof
    When I run `gz validate --advisor-proof-binding`
    Then the exit code is 3
    And the output names tests/fixtures/advisor/empty.json

  @REQ-0.0.29-08-03
  Scenario: Ledger event citing empty-proof diagnosis fails fail-closed
    Given an intrinsic-complexity-attestation event citing a diagnosis with empty proof
    When I run `gz validate --advisor-proof-binding`
    Then the exit code is 3
    And the output names the cited event id
```

Step implementations under `features/steps/` either reuse existing sandbox
helpers (search for `tempdir` + `gz validate` step modules) or add a small
new module if no shared sandbox exists.

### Step 7: Document the flag in `docs/user/commands/validate.md`

Add a `### --advisor-proof-binding` subsection to the existing `validate`
command-doc, mirroring the `### --attestation-receipts` pattern. Include:

- One-paragraph description (defense-in-depth backstop for OBPI-29-01/02)
- Three scan scopes (fixtures / ledger / schema)
- Speculative-marker escape note
- One example block showing failure output
- Link to `ADR-0.0.29-complexity-advisor`

Also update the top-of-doc `gz validate ...` synopsis line to include the new
flag in the `[--advisor-proof-binding]` slot.

### Step 8: Runbook entry in `docs/user/runbook.md`

Under "Complexity doctrine surfaces" (search for the existing complexity
section), add one line entry:

```
- `gz validate --advisor-proof-binding` — fail-closed verdict <-> proof binding
  audit (OBPI-0.0.29-08; defense-in-depth backstop for OBPI-01/02 model+engine).
```

### Step 9: Scorecard entry in `docs/governance/advisory-rules-audit.md`

Add a row to the validator scorecard table (search for `intrinsic_attestation`
to find the canonical row format):

```
| advisor_proof_binding | Mechanical | OBPI-0.0.29-08 | gz validate --advisor-proof-binding |
```

The Mechanical classification is justified because the rule fires deterministic
checks on structural data (fixture JSON, ledger events, JSON Schema) — no
interpretive judgment required.

### Step 10: Verification + evidence

Run the full ARB-wrapped attestation suite per `AGENTS.md` § Attestation:

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_advisor_proof_binding_validator -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name behave -- uv run -m behave features/advisor_proof_binding.feature
uv run gz validate --advisor-proof-binding
uv run gz validate --all
uv run gz check
uv run gz covers OBPI-0.0.29-08 --json
```

Confirm `gz covers OBPI-0.0.29-08` reports `uncovered_reqs == 0`. Capture
ARB receipt IDs for the Stage 4 evidence table.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_advisor_proof_binding_validator -v
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz arb step --name behave -- uv run -m behave features/advisor_proof_binding.feature
uv run gz validate --advisor-proof-binding
uv run gz validate --all
uv run gz check
uv run gz covers OBPI-0.0.29-08 --json
```

## Notes

- Module ≤300 lines per `.claude/rules/pythonic.md`.
- All tests decorated with `@covers("REQ-0.0.29-08-NN")` per `.gzkit/rules/tests.md`.
- `tempfile.TemporaryDirectory` for sandbox isolation; never write to repo root.
- Operator PII rule: never include personal email in tests, fixtures, doc
  strings, or commit messages.
- Speculative-marker escape (`_negative_case: true`) inherits the precedent
  from `.claude/rules/governance-core.md` and is documented inline in the
  validator module + the `validate.md` flag section.
- `--advisor-proof-binding` integrates into both `gz validate --all` and
  `gz check`, satisfying REQ-3.
- Exit-code map (REQ-4): 0 success, 3 policy breach, 2 system error
  (per `.claude/rules/cli.md` convention used by sibling validators).
- ARB receipts emitted by Step 10 attest the Stage 4 evidence table per
  `AGENTS.md` § Attestation.

### Plan-Before-Exploration disclosure (gz-plan-audit Step 6a)

**Destination-in-mind:** Mirror the OBPI-0.0.29-07 (`intrinsic_attestation`)
validator structure module-for-module: a new `trust_audits/advisor_proof_binding.py`
module with three scan helpers (`_scan_fixtures`, `_scan_ledger`, `_scan_schema`),
register in `__init__.py`, wire flag and `--all`-aggregation parity in
`parser_maintenance.py` + `validate_cmd.py`, behave + command-doc + runbook +
scorecard documentation. The parallel between OBPI-07 (intrinsic attestation
event shape) and this OBPI (advisor diagnosis proof binding) was already
named in the brief context — both are validator audits over data shapes
that runtime-layer enforcement should already prevent.

**Rejected alternatives:**

1. **Extend an existing trust_audits module (e.g. `intrinsic_attestation.py`)
   instead of adding a new module** — Rejected because the two validators audit
   distinct surfaces (event shape vs proof presence) with distinct scan scopes
   (fixtures + schema in addition to ledger). Co-locating them would couple
   their lifecycles and obscure the defense-in-depth structure that motivates
   this OBPI.
2. **Single-source the proof-binding check inside the JSON Schema only**
   (relying on `minItems: 1`) — Rejected because the threat model includes
   future schema regression; the validator scan over fixtures + ledger is
   the regression backstop the brief explicitly motivates.
3. **Use Pydantic to re-validate fixtures on load instead of scanning JSON
   directly** — Rejected because the validator must itself be the regression
   backstop against a weakening of the model. Re-routing through the model
   couples the audit to the surface it is auditing.
4. **Skip the speculative-marker escape and require all fixtures to satisfy
   the rule** — Rejected because REQ-6 explicitly preserves the empty-proof
   negative-case test as a non-defect. Without the escape, the OBPI-01
   model test (which asserts `ValidationError` on empty proof) would itself
   trigger the validator.
