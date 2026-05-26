# OBPI-0.0.59-04: Decommission Tautological Tests Chore — Infrastructure

## Context

ADR-0.0.59 Decision item 4 ships the `decommission-tautological-tests` re-runnable
chore infrastructure. This OBPI creates the AST scanner, Pydantic models, drift gate
validator, event type, chore registration, initial state files, and docs. The first
sweep wave over the top-5 offenders is OBPI-05's responsibility.

Parent ADR: ADR-0.0.59-req-scope-discipline-and-test-shape-doctrine
OBPI: OBPI-0.0.59-04-decommission-tautological-tests-chore
Lane: Heavy

## Files

### New files
- `src/gzkit/models/tautological_tests.py` — Pydantic models
- `src/gzkit/tautological_tests.py` — AST scanner + drift gate validator
- `data/tautological_test_baseline.json` — initial empty baseline
- `data/tautological_test_waivers.json` — initial empty waivers
- `tests/governance/test_tautological_tests.py` — unit tests
- `.gzkit/chores/decommission-tautological-tests/CHORE.md`
- `.gzkit/chores/decommission-tautological-tests/acceptance.json`
- `.gzkit/chores/decommission-tautological-tests/README.md`
- `src/gzkit/chores/decommission-tautological-tests/CHORE.md` (byte-identical pkg copy)
- `src/gzkit/chores/decommission-tautological-tests/acceptance.json` (byte-identical)
- `src/gzkit/chores/decommission-tautological-tests/README.md` (byte-identical)

### Modified files
- `src/gzkit/events.py` — add ChoreDecommissionProcessedEvent + TypedLedgerEvent union
- `src/gzkit/ledger_events.py` — add chore_decommission_processed_event() factory
- `src/gzkit/chores/registry.json` — add decommission-tautological-tests entry
- `src/gzkit/commands/validate_cmd.py` — add --tautological-test-audit scope
- `src/gzkit/cli/parser_maintenance.py` — add --tautological-test-audit flag
- `src/gzkit/quality.py` — add run_tautological_test_audit runner
- `src/gzkit/commands/quality.py` — add step to _build_check_steps()
- `docs/user/manpages/validate.md` — add --tautological-test-audit section
- `data/behave_coverage_waivers.json` — add obpi-0.0.59-04-bdd-deferred-to-adr-closeout key

## Steps

### Step 1: Pydantic models (TDD — write tests first)

Write `tests/governance/test_tautological_tests.py` with:
- Tests for TautologicalTestOperation, Waiver, Baseline, ProposedDisposition model validity
- Tests for frozen enforcement and extra='forbid'
- Tests for AST scanner (scan a fixture test file with known tautological ops)
- Tests for disposition engine (each of the 4 proposal kinds)
- Tests for drift gate exit codes (exit 3 on excess, exit 0 on clean)
- Tests for self-exemption (waivers.json excluded from scan)
- Tests for event model and factory parseable by parse_typed_event()
- Tests for gz check step registration

Then implement `src/gzkit/models/tautological_tests.py`:
- TautologicalTestOperation(file_path, line_number, operation_kind, function_name, assertion_kind)
- Waiver(file_path, rationale_key, waived_count)
- Baseline(operations: list[TautologicalTestOperation], generated_at: datetime)
- ProposedDisposition(StrEnum: convert, replace_with_ledger, fold_to_validator, keep_as_fixture)

All models: BaseModel + ConfigDict(frozen=True, extra='forbid')

### Step 2: AST scanner + disposition engine

Implement `src/gzkit/tautological_tests.py`:
- `scan_test_tree(tests_path: Path) -> list[TautologicalTestOperation]`
  Uses ast.parse per file; walks FunctionDef nodes; detects co-occurrence of:
  - filesystem ops: ast.Call with func.id/attr in {open, read_text, read_bytes, exists,
    os.path.*} or ast.Attribute access on Path objects
  - assertion statements: ast.Assert or ast.Call with func.attr starting with 'assert'
  Returns one TautologicalTestOperation per co-occurrence
  HARDCODED exclusion: skip `data/tautological_test_waivers.json` path always

- `propose_disposition(op: TautologicalTestOperation) -> ProposedDisposition`
  Heuristic: if op references ledger/receipt paths → replace_with_ledger;
  if op references schema/config paths → fold_to_validator;
  if op is in setUp/setUpClass → keep_as_fixture;
  default → convert

- `load_baseline(data_dir: Path) -> Baseline`
- `load_waivers(data_dir: Path) -> dict[str, list[str]]` (file_path → rationale_keys)
- `count_waived(waivers: dict, file_path: str) -> int`
- `audit_drift(project_root: Path) -> list[ValidationError]`
  Compares scan count to baseline + waivers; returns errors on excess

### Step 3: Event type + factory

Edit `src/gzkit/events.py`:
- Add ChoreDecommissionProcessedEvent with Literal["chore_decommission_processed"]
  Fields: file_path: str, disposition: str, obpi_id: str
- Add to TypedLedgerEvent union

Edit `src/gzkit/ledger_events.py`:
- Add chore_decommission_processed_event(file_path, disposition, obpi_id) -> LedgerEvent

### Step 4: Drift gate CLI integration

Edit `src/gzkit/commands/validate_cmd.py`:
- Add `check_tautological_test_audit: bool = False` parameter to validate()
- Add `_validate_tautological_test_audit(project_root)` function
- Register scope in opt_in_scopes dict and scope execution block
- Follow --req-kind-discipline pattern from OBPI-02

Edit `src/gzkit/cli/parser_maintenance.py`:
- Add `--tautological-test-audit` flag to validate subparser
- Follow --req-kind-discipline flag as model

Edit `src/gzkit/quality.py`:
- Add `run_tautological_test_audit(project_root) -> CheckResult` function

Edit `src/gzkit/commands/quality.py`:
- Add ("tautological test audit", run_tautological_test_audit) to _build_check_steps()

### Step 5: Initial state files

Create `data/tautological_test_baseline.json`:
- Empty baseline matching Baseline schema: {"operations": [], "generated_at": "<iso8601>"}

Create `data/tautological_test_waivers.json`:
- Empty waivers dict matching behave_coverage_waivers.json pattern:
  {"default_rationale": {}}

### Step 6: Chore directory + registry

Create `.gzkit/chores/decommission-tautological-tests/`:
- CHORE.md: operator workflow, 4 steps (scan, review, process-file, validate)
- acceptance.json: exit-code criteria for gz validate --tautological-test-audit and tests
- README.md: brief chore description

Create `src/gzkit/chores/decommission-tautological-tests/` as byte-identical copies.

Edit `src/gzkit/chores/registry.json`:
- Add entry: slug=decommission-tautological-tests, lane=heavy, title=..., version=1.0.0

### Step 7: Docs + BDD waiver

Edit `docs/user/manpages/validate.md`:
- Add `--tautological-test-audit` section following existing scope documentation pattern
- Include scope semantics, exit-code contract, drift-gate formula, waiver-file path

Edit `data/behave_coverage_waivers.json`:
- Add key "obpi-0.0.59-04-bdd-deferred-to-adr-closeout" with rationale text

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz validate --tautological-test-audit
uv run gz validate --chores-layout
uv run mkdocs build --strict
```

## Notes

- Self-exemption for waivers.json is hardcoded (not configurable) per 2am-operator analysis
- BDD deferred to ADR-0.0.59 closeout per sibling pattern (OBPI-02, OBPI-03)
- Scope-collision warnings from plan-audit (55 sibling-ADR overlaps) are all advisory;
  these shared infrastructure files (validate_cmd.py, events.py, etc.) receive additive
  changes only — no existing behavior is modified
- First sweep wave (modifying test files) is OBPI-05's scope; this OBPI creates no changes
  to existing tests
