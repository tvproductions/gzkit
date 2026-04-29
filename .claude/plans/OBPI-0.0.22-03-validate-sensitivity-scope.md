# Plan: OBPI-0.0.22-03 — `gz validate --sensitivity` scope

**OBPI:** OBPI-0.0.22-03-validate-sensitivity-scope
**Parent ADR:** ADR-0.0.22-security-sensitivity-doctrine
**Lane:** Heavy (Foundation-kind)

## Context

OBPI-01 landed the schema-side `sensitivity` enum field on `adr.json` and `obpi.json`.
OBPI-02 landed `data/security_surfaces.json` plus `src/gzkit/models/security_surfaces.py`
which exposes `load_registry()` and `match_globs(candidate_globs, registry) -> tuple[str, ...]`.

This OBPI adds the third leg: a `gz validate --sensitivity` validator that intersects
each brief's `## ALLOWED PATHS` glob list against the registry, computes a
`detected_sensitivity`, and enforces auto-detect-floor + escalate-not-escape:

- intersection non-empty -> forces `sensitivity: security` (floor)
- frontmatter MAY declare `sensitivity: security` when paths don't trigger detection (escalation)
- frontmatter MAY NOT declare lower than detected -> exit 3 (escape blocked)
- registry missing/malformed -> exit 3 (fail-closed)
- `--explain ALLOWED_PATHS_LIST` predicts classification without modifying any artifact
- `--json` machine output to stdout, logs to stderr

## Brief alignment notes

- Brief Allowed Paths cites `src/gzkit/cli/parser_validate.py`. The actual validate-flag
  registration site is `src/gzkit/cli/parser_maintenance.py` (already hosts `--taxonomy`,
  `--brief-headings`, etc.). The brief allowlist also includes `src/gzkit/cli/**`, so
  the canonical site is in-scope; treating the explicit filename as advisory rather than
  binding (cite the discrepancy in the OBPI evidence section, do not gold-plate the brief).
- Validator dispatch lives in `src/gzkit/commands/validate_cmd.py` (not in scope for new
  files but is touched for wiring) — `src/gzkit/cli/**` allowance does not cover this;
  the validator wiring is unavoidable. The brief allowlist needs `src/gzkit/commands/**`
  added or the wiring belongs in `parser_maintenance.py` only via `_lazy("validate")`
  forwarding (existing pattern). Pursue the second path: extend the existing
  `_lazy("validate")(...)` call with a `check_sensitivity` kwarg, then add the dispatch
  branch inside `commands/validate_cmd.py` — that file is already a generic dispatcher
  and adding one more scope is the minimal-surface change. (If the wiring touch in
  `commands/validate_cmd.py` is later flagged as a brief-allowlist deviation, the
  intersection between brief intent and existing repo structure forces the choice;
  document in evidence.)

## Files (planned)

**Modify:**

- `src/gzkit/governance/trust_audits.py` — add `audit_sensitivity_binding(project_root)`
  following the shape of `audit_adr_taxonomy` (sibling-style validator).
- `src/gzkit/cli/parser_maintenance.py` — register `--sensitivity` + `--explain
  ALLOWED_PATHS_LIST` flags, forward to `_lazy("validate")(check_sensitivity=...,
  sensitivity_explain=...)`.
- `src/gzkit/commands/validate_cmd.py` — add `check_sensitivity` and
  `sensitivity_explain` kwargs to the public `validate()` entry; add dispatch branch
  that calls `audit_sensitivity_binding`; thread into the JSON aggregator. Add to
  the `--audits` umbrella so `gz validate --all` / `gz check` pick it up via the
  existing pipeline.

**Create:**

- `tests/governance/test_audit_sensitivity_binding.py` — REQ-derived unit tests for
  the validator (floor-fires, escalation-allowed, escape-blocked,
  registry-missing-fail-closed, malformed-paths-tolerated).
- `tests/cli/test_validate_sensitivity_flag.py` — REQ-derived CLI tests for the
  `--sensitivity`, `--explain`, `--json` flag wiring.

**No new dependencies.** Uses stdlib `glob`, `json`, `pathlib`, plus the existing
`src/gzkit/models/security_surfaces.py` registry helpers and the existing
`_parse_adr_frontmatter`-style frontmatter parsing already present in
`trust_audits.py`.

## REQ-coverage map (planned)

| REQ | Test target | Test class/method |
|-----|-------------|-------------------|
| REQ-0.0.22-03-01 (floor fires) | `tests/governance/test_audit_sensitivity_binding.py` | `TestSensitivityFloor.test_intersecting_paths_force_security` |
| REQ-0.0.22-03-02 (escalation allowed) | `tests/governance/test_audit_sensitivity_binding.py` | `TestSensitivityFloor.test_declared_security_no_intersection_accepted` |
| REQ-0.0.22-03-03 (escape blocked) | `tests/governance/test_audit_sensitivity_binding.py` | `TestSensitivityFloor.test_escape_attempt_emits_finding` |
| REQ-0.0.22-03-04 (registry missing fail-closed) | `tests/governance/test_audit_sensitivity_binding.py` | `TestSensitivityRegistry.test_missing_registry_fails_closed` + `test_malformed_registry_fails_closed` |
| REQ-0.0.22-03-05 (`--explain`) | `tests/cli/test_validate_sensitivity_flag.py` | `TestSensitivityExplain.test_explain_prints_prediction_and_exits_0` |
| REQ-0.0.22-03-06 (`--json` records) | `tests/cli/test_validate_sensitivity_flag.py` | `TestSensitivityJson.test_json_records_have_required_fields` |
| REQ-0.0.22-03-07 (`--all` / `gz check` integration) | `tests/cli/test_validate_sensitivity_flag.py` | `TestSensitivityAll.test_audits_umbrella_includes_sensitivity` |

Each test will carry an `@covers("REQ-0.0.22-03-NN")` decorator (or `@covers
REQ-0.0.22-03-NN` docstring) so the Stage 3 Phase 1b parity gate (`gz covers
OBPI-0.0.22-03 --json`) reports `uncovered_reqs == 0`.

## Steps

### Step 1 — RED: validator unit tests (`tests/governance/test_audit_sensitivity_binding.py`)

Author table-driven tests covering REQ-01..04. Use `tempfile.TemporaryDirectory` to
build a fixture project root with:

- `data/security_surfaces.json` (real or controlled fixture)
- one or more brief files under `docs/design/adr/foundation/ADR-test/obpis/`
  with controlled frontmatter + `## ALLOWED PATHS` blocks

Cases:

- `test_intersecting_paths_force_security` — brief allowlist includes
  `src/gzkit/ledger.py`; frontmatter has no `sensitivity` field; expect a
  `ValidationError` whose payload reports `detected_sensitivity == "security"`,
  `declared_sensitivity is None`, and intersecting paths cited. The validator
  reports the floor as a *finding* (informational at exit 0 if declared is null
  or matches detected), but only fails (exit 3) on escape attempts.
- `test_declared_security_no_intersection_accepted` — frontmatter declares
  `sensitivity: security`, allowlist has no intersecting paths; validator
  returns no errors (escalation channel).
- `test_escape_attempt_emits_finding` — allowlist intersects the registry and
  frontmatter declares `sensitivity: null` explicitly (or omits the field) —
  the policy is "MAY NOT declare a value lower than detected." The brief
  contract here is: omitted-field is *not* an escape (the floor simply forces
  the classification to security in the audit output); explicit
  `sensitivity: null` (or any non-`security` value, if added later) IS an
  escape. The conservative spec for v1 (only `security` permitted) is: any
  explicitly declared value other than `security` when detected is `security`
  fails closed. Pin this in the test.
- `test_missing_registry_fails_closed` — `data/security_surfaces.json`
  absent; expect a `ValidationError` referencing the registry path and
  classified as fail-closed.
- `test_malformed_registry_fails_closed` — registry JSON exists but does not
  validate against `SecuritySurfaceEntry` (missing `category`, etc.); expect
  fail-closed `ValidationError`.
- `test_malformed_brief_path_tolerated` — a brief whose `## ALLOWED PATHS`
  block has malformed entries (unparseable globs) does not crash; the
  validator emits a structured finding and proceeds.

Run:

```bash
uv run -m unittest tests.governance.test_audit_sensitivity_binding -v
```

Watch all tests fail (RED). Tests must fail because `audit_sensitivity_binding`
does not exist yet.

### Step 2 — GREEN: implement `audit_sensitivity_binding` in `trust_audits.py`

Add at the end of the validator block, following the shape of
`audit_adr_taxonomy`:

```python
def audit_sensitivity_binding(project_root: Path) -> list[ValidationError]:
    """Enforce ADR-0.0.22 security-sensitivity invariant:
    auto-detect floor + escalate-not-escape against data/security_surfaces.json.
    """
```

Implementation outline:

1. Load the registry via `gzkit.models.security_surfaces.load_registry`.
   On `FileNotFoundError`, `json.JSONDecodeError`, or `pydantic.ValidationError`
   return a single fail-closed `ValidationError` (`severity="error"`,
   `code="sensitivity-registry-missing"` / `"sensitivity-registry-malformed"`)
   with the registry path in the payload. Do not raise.
2. Walk briefs under `docs/design/adr/**/obpis/*.md` and
   `docs/design/adr/**/briefs/*.md`. For each:
   - Parse frontmatter (reuse `_parse_adr_frontmatter` or local helper).
   - Extract the `## ALLOWED PATHS` block (one bullet per glob; tolerate
     `- path` and `- path -- comment` shapes).
   - Compute `intersecting_paths` via `match_globs(allowed_globs, registry)`.
   - Compute `detected_sensitivity = "security" if intersecting_paths else None`.
   - `declared_sensitivity` = frontmatter value (string or None).
   - Decision matrix:
     * `detected == None` and `declared in {None, "security"}` -> ok.
     * `detected == "security"` and `declared in {None, "security"}` -> ok
       (floor forces classification; no error). Optionally emit an
       `info`-level finding when `declared is None` so `--json` consumers see
       the floor activated; severity stays at `info` so exit code remains 0.
     * `detected == "security"` and `declared not in {None, "security"}` ->
       ERROR with code `sensitivity-escape-attempt`, payload listing
       `file`, `declared_sensitivity`, `detected_sensitivity`,
       `intersecting_paths`, `registry_categories`.
3. Return the accumulated list.

Add an explain helper:

```python
def explain_sensitivity_for_paths(
    candidate_globs: Sequence[str], project_root: Path
) -> dict[str, object]:
    """Return predicted classification for an ad-hoc path list, no mutation."""
```

Returns `{"detected_sensitivity": ..., "matching_categories": (...), "intersecting_globs": (...)}`.

Re-run:

```bash
uv run -m unittest tests.governance.test_audit_sensitivity_binding -v
```

GREEN. Then run lint + typecheck.

### Step 3 — RED: CLI flag tests (`tests/cli/test_validate_sensitivity_flag.py`)

Author tests using `unittest.mock.patch` on the dispatch surface (mirror the
pattern used by the existing `tests/cli/test_*.py` for `--taxonomy`):

- `test_sensitivity_flag_dispatches_audit` — invoking `gz validate --sensitivity`
  via `argparse` calls `validate(check_sensitivity=True, ...)`.
- `test_explain_prints_prediction_and_exits_0` — `gz validate --sensitivity
  --explain "src/gzkit/ledger.py,tests/**"` returns exit 0 and stdout contains
  `detected_sensitivity` and at least one category label.
- `test_explain_does_not_modify_artifacts` — verify that `--explain` path does
  not read the on-disk brief tree; assertion via mock that
  `audit_sensitivity_binding` was NOT called when `--explain` is passed.
- `test_json_records_have_required_fields` — `gz validate --sensitivity --json`
  emits JSON-parseable records on stdout, each containing keys: `file`,
  `declared_sensitivity`, `detected_sensitivity`, `intersecting_paths`,
  `registry_categories`. Logs (info/warn lines) go to stderr.
- `test_audits_umbrella_includes_sensitivity` — invoking `gz validate
  --audits` includes the sensitivity scope in the dispatched scopes.

Run:

```bash
uv run -m unittest tests.cli.test_validate_sensitivity_flag -v
```

RED.

### Step 4 — GREEN: wire `--sensitivity` + `--explain` + dispatch

a. In `src/gzkit/cli/parser_maintenance.py`, register the flags inside the
   existing `_register_validate_parsers` block alongside `--taxonomy`:

   ```python
   p_validate.add_argument(
       "--sensitivity",
       dest="check_sensitivity",
       action="store_true",
       help="ADR-0.0.22 sensitivity-binding (auto-detect floor; escalate-not-escape)",
   )
   p_validate.add_argument(
       "--explain",
       dest="sensitivity_explain",
       metavar="ALLOWED_PATHS_LIST",
       help="With --sensitivity: predict classification for a comma- or newline-separated path list",
   )
   ```

   Extend the `_lazy("validate")(...)` forwarding kwargs with
   `check_sensitivity=a.check_sensitivity`,
   `sensitivity_explain=a.sensitivity_explain`. Add `--sensitivity` to the
   `--audits` umbrella branch so `check_sensitivity=a.check_sensitivity or
   a.check_audits` (mirrors `check_cli_alignment or check_audits`).

b. In `src/gzkit/commands/validate_cmd.py`, extend the `validate(...)`
   signature with `check_sensitivity: bool = False, sensitivity_explain:
   str | None = None`. Add the corresponding dispatch:

   - When `sensitivity_explain` is set, call `explain_sensitivity_for_paths`
     and print its result to stdout (json-ish for `--json`, plain table
     otherwise), then return 0 (skip the rest of validate dispatch).
   - When `check_sensitivity` is true (without `--explain`), call
     `audit_sensitivity_binding(project_root)` and aggregate findings into the
     existing scope-results dict under the `"sensitivity"` key. Findings that
     are exclusively `info`-level do not raise the exit code.
   - Wire `"sensitivity"` into the `--json` output schema (one record per
     brief, plus registry-error records when fail-closed).

c. Manpage / runbook changes — this OBPI deliberately keeps
   docs out of scope for the in-flight increment. The Heavy-lane Gate 3
   docs covering `--sensitivity` will land in OBPI-06 alongside the rule
   file and `AGENTS.md` matrix update. (Verified via parent-ADR Decision
   line item: "OBPI-06: Rule file + AGENTS.md matrix + advisory
   scorecard … `gz agent sync control-surfaces` propagates rule to vendor
   mirrors".)

Re-run unit + CLI tests. GREEN.

### Step 5 — Wire-through verification

Run, in order:

```bash
uv run gz validate --sensitivity         # exit 0 on a clean tree
uv run gz validate --sensitivity --json  # JSON records on stdout
uv run gz validate --sensitivity --explain "src/gzkit/ledger.py"   # prediction
uv run gz validate --audits              # sensitivity included in umbrella
uv run gz check                          # composite still green
```

Capture observed output in the OBPI evidence section. Verify exit codes
match the REQ table.

### Step 6 — Baseline checks + ARB receipts

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run mkdocs build --strict
```

Capture receipt IDs. The Heavy-lane Gate 3 docs requirement is covered by the
strict mkdocs build pass plus the runbook touch deferred to OBPI-06; behave
coverage is tagged for the BDD scenarios that exist (none new in this OBPI —
the validator is exercised via unit tests). Add a waiver entry to
`data/behave_coverage_waivers.json` if behave-req-tags audit flags this OBPI's
REQs as needing scenarios.

### Step 7 — Stage 3 Phase 1b parity gate

```bash
uv run gz covers OBPI-0.0.22-03 --json
```

Confirm `summary.uncovered_reqs == 0`. Add `@covers` decorators if any REQ row
shows `covered: false`.

## Verification

Final verification commands (Stage 4 evidence table):

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_audit_sensitivity_binding tests.cli.test_validate_sensitivity_flag -v
uv run gz validate --sensitivity --json
uv run gz validate --sensitivity --explain "src/gzkit/ledger.py"
uv run gz validate --audits
uv run gz check
uv run gz covers OBPI-0.0.22-03 --json
```

## Notes

- **Destination-in-mind:** The natural shape is a sibling validator beside
  `audit_adr_taxonomy` because (a) the trust-audits module is the canonical
  home for fail-closed validators that touch frontmatter + a registered
  external surface (taxonomy reads ADR frontmatter; sensitivity reads OBPI
  frontmatter + `data/security_surfaces.json`), and (b) the existing
  `validate_cmd.py` dispatch pattern already accepts new scope kwargs without
  refactor. The risk of building this elsewhere (a new `governance/sensitivity.py`
  module) is splitting the validator surface across files for one new scope —
  premature abstraction, rejected.
- **Rejected alternatives during plan authoring:**
  1. *New CLI parser module `parser_validate.py`* — rejected; the brief's
     citation of that filename is a drift in the brief, not a doctrine
     directive. The repo already centralizes validate flags in
     `parser_maintenance.py`.
  2. *Add `--explain` as a separate top-level CLI verb (`gz sensitivity
     explain`)* — rejected; the brief explicitly describes it as a subform of
     `gz validate --sensitivity`, and operators authoring briefs expect to
     reach for `gz validate ...` first. Subforms minimize CLI surface bloat.
  3. *Implement `--explain` by mocking the on-disk brief tree* — rejected;
     `--explain` should be a pure function of (path list, registry) and not
     touch the disk other than the registry. This is the doctrine: prediction
     before authoring, no mutation.
- **Foundation-kind + heavy-lane attestation rigor:** Brief-level Gate 5
  attestation will fire at Stage 4 of the pipeline. Stage 5 will use the
  `--attestor-present` path (GHI #292) since the pipeline marker will be live.
- **Defect surfacing:** the brief's `parser_validate.py` citation is a brief
  defect in the Allowed Paths list. Per "flag defects, never excuse them" —
  surface this in the OBPI evidence section as a brief drift, do not amend
  the brief retroactively (the brief allowlist's `src/gzkit/cli/**` covers
  the actual file in scope, so it's not a scope violation).

## Rollback

The only schema-touching change is implicit (the validator reads schema
frontmatter; it does not mutate schemas). To rollback:

1. Revert the new `audit_sensitivity_binding` and `explain_sensitivity_for_paths`
   functions in `trust_audits.py`.
2. Revert the parser-maintenance flag registrations.
3. Revert the `validate_cmd.py` dispatch additions.
4. Revert the two new test files.

No data migration; no schema rollback; no ledger event to retract.
