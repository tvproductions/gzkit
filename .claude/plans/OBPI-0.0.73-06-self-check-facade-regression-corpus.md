# Plan: OBPI-0.0.73-06 Self-Check + Facade Regression Corpus

**OBPI:** OBPI-0.0.73-06-self-check-facade-regression-corpus
**Parent:** ADR-0.0.73-verification-layer-binding-audit
**Lane:** Lite

## Destination-in-mind (plan-audit disclosure)

Before exploration I expected: fix a fidelity-assertions formatting issue,
create self-check unit tests and facade corpus fixtures for theater-signature
regression detection.

## Rejected alternatives

1. Fix `src/gzkit/fidelity.py` to strip backtick wrapping — fixes the root
   class failure but `fidelity.py` is outside Allowed Paths. Chosen approach:
   fix the ADR's command cells directly (in scope). Filed as a future GHI
   after OBPI-06 lands (other ADRs will hit the same issue).
2. Use Python dict fixtures — JSON is more readable as documentation and
   doesn't require import mechanics.
3. Write REQ-03 test as a behave scenario — brief explicitly names the test
   file `test_qc_binding_self_check.py`, so it stays in `tests/governance/`.

## Discovered root causes

1. **Backtick wrapping**: All 6 commands in the Fidelity Assertions table are
   wrapped in markdown backticks (e.g. `` `uv run gz validate --qc-binding` ``).
   The parser calls `command.strip()` (whitespace only); backticks are preserved.
   `shlex.split("`uv run gz validate --qc-binding`")` tries to execute `` `uv ``
   as the binary → FileNotFoundError (OSError) → `observed = -1` for every
   assertion.
2. **Row 3 circular self-reference**: Row 3 asserts that running
   `gz adr fidelity ADR-0.0.73-verification-layer-binding-audit` exits 0.
   When the fidelity gate runs this command as a subprocess, the subprocess
   again runs all 6 assertions, including row 3, which again spawns a
   subprocess — infinite chain until resource exhaustion. This assertion can
   never pass as written; it must be changed to the `--check` (parse-only)
   form, which is non-circular.

## Steps

### Step 1: Fix ADR Fidelity Assertions table

**File:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`

Changes:
- Remove backtick wrapping from all 6 command cells
- Change row 3 command to `uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit --check`
  and update claim: "The fidelity gate exists and the Fidelity Assertions
  block on this ADR is parseable by the gate."
- Remove row 4 (now duplicate of updated row 3)

After: `gz adr fidelity ADR-0.0.73-verification-layer-binding-audit` runs
5 assertions, all exit 0.

### Step 2: Create facade corpus fixtures

**Files to create** (6 JSON, one per theater signature):
- `tests/governance/fixtures/facade_corpus/mtime_where_name_says_content.json`
- `tests/governance/fixtures/facade_corpus/empty_input_passes.json`
- `tests/governance/fixtures/facade_corpus/copy_vs_self.json`
- `tests/governance/fixtures/facade_corpus/fixture_only.json`
- `tests/governance/fixtures/facade_corpus/skip_if_pass.json`
- `tests/governance/fixtures/facade_corpus/prose_graded_by_nothing.json`

Each JSON file contains a QCStep-compatible dict with `theater_flags` set to
the relevant signature. Example:
```json
{
  "id": "hollow-mtime-check",
  "name": "Hollow Mtime Check",
  "kind": "audit",
  "subject": "docs/",
  "binding": "bound",
  "wired_into": ["gz check"],
  "theater_flags": ["mtime-where-name-says-content"],
  "enforcement_locus": "python_function"
}
```

### Step 3: Create test_facade_regression_corpus.py

**File:** `tests/governance/test_facade_regression_corpus.py`

- Class `TestFacadeRegressionCorpus` with 6 test methods (one per signature)
- Each test: load the JSON fixture → create QCStep → call
  `_check_theater_signatures(step)` → assert 1 error returned and error
  message contains the signature string
- `@covers("REQ-0.0.73-06-02")` on every test method
- Fixtures loaded from `Path(__file__).parent / "fixtures" / "facade_corpus"`

### Step 4: Create test_qc_binding_self_check.py

**File:** `tests/governance/test_qc_binding_self_check.py`

- Class `TestQCBindingSelfCheck` with 2 test methods:
  - `test_audit_qc_binding_no_theater_on_real_project`
    - `@covers("REQ-0.0.73-06-01")`
    - Calls `audit_qc_binding(Path("."))` with no `nc_registry` override
      (uses module-level registry — empty at OBPI-06 stage)
    - Asserts `len(errors) == 0`
  - `test_fidelity_gate_passes_for_adr_0073`
    - `@covers("REQ-0.0.73-06-03")`
    - Subprocess: `["uv", "run", "gz", "adr", "fidelity",
      "ADR-0.0.73-verification-layer-binding-audit"]`
    - `cwd = Path(__file__).parent.parent.parent` (project root)
    - Asserts `returncode == 0`
    - Note: integration-tier — actually runs 5 `uv run gz` subprocess
      commands; slow by unit-test standards but required to prove the
      assertion commands themselves exit 0

## Verification commands

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --qc-binding
uv run gz adr fidelity ADR-0.0.73-verification-layer-binding-audit
```

## Files

**Modified:**
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`

**Created:**
- `tests/governance/fixtures/facade_corpus/mtime_where_name_says_content.json`
- `tests/governance/fixtures/facade_corpus/empty_input_passes.json`
- `tests/governance/fixtures/facade_corpus/copy_vs_self.json`
- `tests/governance/fixtures/facade_corpus/fixture_only.json`
- `tests/governance/fixtures/facade_corpus/skip_if_pass.json`
- `tests/governance/fixtures/facade_corpus/prose_graded_by_nothing.json`
- `tests/governance/test_facade_regression_corpus.py`
- `tests/governance/test_qc_binding_self_check.py`

## Notes

- The fidelity parser in `src/gzkit/fidelity.py` doesn't strip markdown
  backtick wrapping from command cells. This is a latent issue for future ADRs
  that author Fidelity Assertions with backtick-wrapped commands (natural
  markdown). File as a GHI after OBPI-06 lands.
- Scope collision with OBPI-0.0.42-04 is advisory only (OBPI-0.0.42-04 is
  Completed).
