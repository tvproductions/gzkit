# Implementation Plan: OBPI-0.0.35-04-kind-invariance-validator

**OBPI:** OBPI-0.0.35-04-kind-invariance-validator  
**Parent ADR:** ADR-0.0.35-foundation-feature-invariance-test  
**Lane:** Heavy  
**Date:** 2026-05-17

## Context

The `## Why foundation tier?` section convention was established by OBPI-03
(now Completed). The foundation-ADR template scaffolds the section pre-populated
for new ADRs. This OBPI ships the mechanical enforcement: `gz validate
--kind-invariance` checks every existing foundation ADR carries the section with
substantive non-placeholder content.

The validator lives in `src/gzkit/governance/trust_audits/kind_invariance.py`
(new module in the existing package). It is registered as `--kind-invariance` in
`src/gzkit/cli/parser_maintenance.py`, dispatched in
`src/gzkit/commands/validate_cmd.py`, and wired into `gz check` via a
`run_kind_invariance_audit()` wrapper in `src/gzkit/quality.py` added to
`_build_check_steps()` in `src/gzkit/commands/quality.py`.

## Files

**New:**
- `src/gzkit/governance/trust_audits/kind_invariance.py` — validator scope
- `tests/governance/test_kind_invariance.py` — REQ-derived unit tests
- `features/kind_invariance.feature` — behave scenario

**Modified:**
- `src/gzkit/governance/trust_audits/__init__.py` — re-export `audit_kind_invariance`
- `src/gzkit/cli/parser_maintenance.py` — `--kind-invariance` flag registration
- `src/gzkit/commands/validate_cmd.py` — dispatch to `audit_kind_invariance`
- `src/gzkit/quality.py` — `run_kind_invariance_audit()` wrapper
- `src/gzkit/commands/quality.py` — add to `_build_check_steps()`
- `tests/commands/test_validate.py` — flag wiring tests
- `docs/user/manpages/gz-validate.md` — flags table + example invocation
- `docs/user/runbook.md` — kind-invariance verification cross-reference

## Steps

### Task 1: TDD Red-Green — Enumeration (foundation ADR selection)

1. Create `tests/governance/test_kind_invariance.py` with:
   - Test fixture helper that writes minimal ADR frontmatter + body to a temp dir
   - `test_selects_only_foundation_adrs()` decorated `@covers("REQ-0.0.35-04-02")`
     and `@covers("REQ-0.0.35-04-05")`: fixture has one foundation ADR (passes)
     and one feature ADR (not enumerated). Assert only foundation ADR is checked.
   - Run `uv run -m unittest tests.governance.test_kind_invariance -v` → RED

2. Create `src/gzkit/governance/trust_audits/kind_invariance.py` with:
   - `audit_kind_invariance(project_root: Path) -> list[ValidationError]`
   - Glob `docs/design/adr/foundation/ADR-*/ADR-*.md` (relative to project_root)
   - Parse frontmatter to filter `kind: foundation` ADRs only
   - Return `[]` for now (empty implementation for enumeration test)
   - Run → GREEN for enumeration test

3. Add `from gzkit.governance.trust_audits.kind_invariance import audit_kind_invariance`
   and `__all__` entry to `src/gzkit/governance/trust_audits/__init__.py`

### Task 2: TDD Red-Green — Section presence check

1. Add to `test_kind_invariance.py`:
   - `test_foundation_adr_missing_section_fails()` decorated
     `@covers("REQ-0.0.35-04-03")`: fixture writes foundation ADR body WITHOUT
     `## Why foundation tier?` heading. Assert `len(errors) > 0` and
     `errors[0].type == "kind_invariance"`. Run → RED

2. Implement section-presence check in `kind_invariance.py`:
   - After globbing, parse the ADR file body (strip frontmatter)
   - Check for EXACTLY `## Why foundation tier?` as a line
     (byte-identical: sentence case, single space, trailing `?`)
   - Return `ValidationError(type="kind_invariance", artifact=..., message=...)`
     if missing. Run → GREEN

3. Add passing case test:
   - `test_foundation_adr_with_section_passes()` decorated
     `@covers("REQ-0.0.35-04-02")`: fixture writes foundation ADR WITH the
     exact heading and substantive body. Assert `errors == []`. Run → GREEN

### Task 3: TDD Red-Green — Substantive content check

1. Add to `test_kind_invariance.py`:
   - `test_placeholder_body_fails()` decorated `@covers("REQ-0.0.35-04-04")`:
     fixture writes foundation ADR with `## Why foundation tier?` heading but
     body is only `TBD`. Assert `len(errors) > 0`. Run → RED
   - `test_author_prompt_body_fails()` decorated `@covers("REQ-0.0.35-04-04")`:
     fixture writes heading with body containing `_[To be filled]_` author prompt.
     Assert `len(errors) > 0`. Run → RED

2. Extend `kind_invariance.py`:
   - Import `STRICT_PLACEHOLDERS` from `gzkit.hooks.obpi` (or replicate its
     placeholder detection logic via a private `_is_placeholder_body(text)` fn
     that matches the same set: empty, "TBD"/"TODO"/"To be filled" variants,
     "paste here" patterns — determined by reading `gzkit.hooks.obpi` source
     before implementing)
   - After confirming heading present, extract body text between heading and
     next `##` heading
   - Apply placeholder check; return error if body is placeholder-only
   - Run → GREEN

3. Add `test_substantive_body_passes()` decorated `@covers("REQ-0.0.35-04-02")`:
   fixture with operator-filled body. Assert `errors == []`. Run → GREEN

### Task 4: TDD Red-Green — CLI integration (flag wiring)

1. Add to `tests/commands/test_validate.py`:
   - `test_kind_invariance_flag_registered()` decorated
     `@covers("REQ-0.0.35-04-01")`: run `gz validate --help` via subprocess,
     assert `--kind-invariance` in output, exit 0. Run → RED

2. Register flag in `src/gzkit/cli/parser_maintenance.py`:
   - Add to the `gz validate` subparser (after existing `--taxonomy`-adjacent flags):
     ```python
     p_validate.add_argument(
         "--kind-invariance",
         dest="check_kind_invariance",
         action="store_true",
         help="Validate every foundation ADR carries a substantive Why-foundation-tier section",
     )
     ```
   - Run → GREEN

3. Wire dispatch in `src/gzkit/commands/validate_cmd.py`:
   - Add `check_kind_invariance: bool = False` parameter to `_collect_errors()`
   - Add `"kind_invariance": check_kind_invariance` to explicit scopes dict
   - Add `"kind_invariance": lambda: trust_audits.audit_kind_invariance(project_root)` to
     `_explicit_scope_runners()` dict
   - Pass `check_kind_invariance=getattr(args, "check_kind_invariance", False)` at call site

4. Add dispatch integration test to `tests/commands/test_validate.py`:
   - `test_kind_invariance_scope_dispatched()` decorated
     `@covers("REQ-0.0.35-04-06")`: mock audit returns error; assert validate
     surfaces it when `--kind-invariance` flag is passed. Run → GREEN

5. Run full test suite: `uv run -m unittest -q` — all pass

### Task 5: Wire into gz check pipeline

1. Add to `src/gzkit/quality.py`:
   ```python
   def run_kind_invariance_audit(project_root: Path) -> QualityResult:
       from gzkit.governance import trust_audits
       errors = trust_audits.audit_kind_invariance(project_root)
       if errors:
           return QualityResult(status="fail", message=errors[0].message)
       return QualityResult(status="pass", message="Kind invariance: all foundation ADRs carry Why-foundation-tier section")
   ```
   (Adapt to QualityResult constructor pattern by reading existing wrappers)

2. Add to `src/gzkit/commands/quality.py` `_build_check_steps()` imports and list:
   ```python
   from gzkit.quality import run_kind_invariance_audit
   # in the return list:
   ("Kind invariance", run_kind_invariance_audit),
   ```

3. Add integration test for `REQ-0.0.35-04-06`:
   `test_kind_invariance_in_check_pipeline()` decorated `@covers("REQ-0.0.35-04-06")`:
   assert `"Kind invariance"` label appears in `_build_check_steps()` output.

### Task 6: Author behave scenario

Create `features/kind_invariance.feature` with scenarios tagged `@REQ-0.0.35-04-NN`:

```gherkin
Feature: gz validate --kind-invariance enforcement

  @REQ-0.0.35-04-01
  Scenario: flag is registered in gz validate
    When I run "gz validate --help"
    Then it exits with code 0
    And the output contains "--kind-invariance"

  @REQ-0.0.35-04-02
  Scenario: foundation ADR with substantive section passes
    When I run "gz validate --kind-invariance"
    Then it exits with code 0

  @REQ-0.0.35-04-03
  Scenario: foundation ADR missing section fails
    Given a foundation ADR fixture without the Why-foundation-tier section
    When I run "gz validate --kind-invariance"
    Then it exits with code 3
```

Note: Step definitions already available for `When I run ...` / `Then it exits ...` /
`And the output contains ...` patterns. The foundation-ADR fixture step may need
a new step definition if not already registered; check `features/steps/` first.

### Task 7: Update documentation

1. `docs/user/manpages/gz-validate.md`:
   - Add `--kind-invariance` row to the flags table (alphabetical position)
   - Add example invocation in the Examples section:
     `uv run gz validate --kind-invariance`

2. `docs/user/runbook.md`:
   - Add cross-reference at the quality-checks section:
     "Run `uv run gz validate --kind-invariance` to verify every foundation ADR carries a substantive `## Why foundation tier?` section."

3. Verify `uv run mkdocs build --strict` exits 0.

### Task 8: Present OBPI Acceptance Ceremony

- Run all ARB-wrapped attestation commands (Heavy-lane require all five receipts)
- Present evidence per Stage 4 template
- Await human attestation

## Verification

```bash
# Flag registered
uv run gz validate --help | grep "kind-invariance"

# Validator passes on current foundation-ADR population
uv run gz validate --kind-invariance

# Tests pass with REQ coverage
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz covers OBPI-0.0.35-04-kind-invariance-validator

# gz check includes the scope
uv run gz check

# Behave scenario passes
uv run -m behave features/kind_invariance.feature

# Heavy-lane ARB receipts
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb coverage run -m unittest discover -s tests -t .
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

## Notes

- `trust_audits` is a package (`src/gzkit/governance/trust_audits/`);
  new scope goes in `kind_invariance.py` with re-export in `__init__.py`
- `gz check` wiring: `quality.py` for the `run_*` wrapper;
  `commands/quality.py` for `_build_check_steps()` insertion
- The `_is_placeholder` check: read `gzkit.hooks.obpi` to find the actual
  import path before implementing — the brief says reuse, not reimport
- ADR-0.0.35 itself must pass the validator (REQ-16); it currently has no
  `## Why foundation tier?` section — OBPI-03 backfill rule says it gains
  the section during implementation of this OBPI
- Exit codes: 0 (all pass), 3 (policy breach), per .claude/rules/cli.md
