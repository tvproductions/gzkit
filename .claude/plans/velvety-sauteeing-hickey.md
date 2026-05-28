# OBPI-0.0.64-04: gz-validate-task-envelope-coherence

## Context

ADR-0.0.64 Decision item #4 closes the "presence != envelope" anti-pattern at the TASK tier.
OBPIs 01-03 delivered: `task_id` field on 8 worklog events, `@advances` decorator + registry,
`next_seq_for_req`, and `gz task start --req/--seq` CLI. OBPI-04 delivers the validator that
makes the four-channel discovery taxonomy fail-closed:

- Signature (a): worklog events emitted under an active TASK with no `task_id` (attribution-drift)
- Signature (b): OBPI with all-`seq=01` TASKs and no `req_atomic` exemption (subdivision-skipped)
- Signature (c): layer-drift — different TASK IDs for same (OBPI, REQ) unit across channels

Heavy lane: new CLI surface, new schema field, new pipeline integration.

## Destination-in-mind (per plan-audit Step 6a)

Conclusion already formed before writing this plan: the validator follows the `--commit-trailers`
inline pattern in `validate_cmd.py`; `gz task envelope diagnose` is a new top-level verb under
`gz task`, wired in `parser_artifacts.py`; `req_atomic` is an optional field on `BriefStructure`.

Rejected alternatives:
1. Separate trust_audits module — `--commit-trailers` lives inline; simpler to follow that
2. `gz task envelope diagnose` as a standalone `gz` top-level — belongs under `gz task`
3. `req_atomic` as a separate schema file — brief frontmatter is the authored escape valve surface

## Files

- `src/gzkit/governance/brief_structure.py` — add `req_atomic: list[str]` field
- `src/gzkit/commands/validate_cmd.py` — validator function + wiring
- `src/gzkit/cli/parser_maintenance.py` — `--task-envelope-coherence` CLI flag
- `src/gzkit/commands/task.py` — `gz task envelope diagnose` implementation
- `src/gzkit/cli/parser_artifacts.py` — `gz task envelope diagnose` subcommand registration
- `src/gzkit/commands/quality.py` — `gz check` pipeline membership
- `tests/governance/test_task_envelope_coherence.py` — new test file (three signatures + exemption)
- `tests/governance/test_brief_structure.py` — `req_atomic` field tests
- `docs/user/manpages/validate.md` — `--task-envelope-coherence` docs (Heavy Gate 3)
- `docs/user/manpages/task-start.md` — `gz task envelope diagnose` docs (Heavy Gate 3)

## Implementation Steps

### Step 1 — TDD Red: write failing tests first

Write `tests/governance/test_task_envelope_coherence.py` with tests derived from REQs:

```python
# Pattern: use tmp_path-style directory with synthetic ledger events
# Reference: tests/governance/test_brief_structure.py _VALID_FIELDS pattern
# Reference: tests/commands/test_validate_cmds.py _collect_errors() direct call pattern

class TestSignatureA(unittest.TestCase):
    @covers("REQ-0.0.64-04-01")
    def test_worklog_without_task_id_under_active_task_fails_heavy(self): ...

    @covers("REQ-0.0.64-04-01")
    def test_worklog_without_task_id_with_no_active_task_is_clean(self): ...

class TestSignatureB(unittest.TestCase):
    @covers("REQ-0.0.64-04-02")
    def test_obpi_all_seq01_no_req_atomic_fails(self): ...

    @covers("REQ-0.0.64-04-02")
    def test_obpi_all_seq01_req_atomic_covers_all_reqs_passes(self): ...

    @covers("REQ-0.0.64-04-02")
    def test_obpi_all_seq01_req_atomic_partial_fails_for_uncovered(self): ...

class TestSignatureC(unittest.TestCase):
    @covers("REQ-0.0.64-04-03")
    def test_layer_drift_across_frontmatter_and_ledger_fails(self): ...

    @covers("REQ-0.0.64-04-03")
    def test_same_task_id_all_channels_passes(self): ...

class TestCheckPipelineIntegration(unittest.TestCase):
    @covers("REQ-0.0.64-04-06")
    def test_validator_runs_in_gz_check_pipeline(self): ...  # smoke: runs without error
```

Add `req_atomic` tests to `tests/governance/test_brief_structure.py`:
```python
@covers("REQ-0.0.64-04-04")
def test_req_atomic_optional_defaults_empty(self): ...

@covers("REQ-0.0.64-04-04")
def test_req_atomic_accepts_valid_req_ids(self): ...

@covers("REQ-0.0.64-04-07")
def test_req_atomic_is_sole_bypass_for_signature_b(self): ...
```

Run `uv run -m unittest tests/governance/test_task_envelope_coherence.py -v` — expect failures.

### Step 2 — BriefStructure additive

Edit `src/gzkit/governance/brief_structure.py`:

First check: does `BriefStructure` already have a `tasks: list[str]` field? The task-discovery
rule says schema enforcement of `tasks:` is OBPI-04's scope. If absent, add it:
```python
tasks: list[str] = Field(
    default_factory=list,
    description="TASK IDs this artifact advances (ADR-0.0.64 / OBPI-02 channel). "
                "Schema enforcement added by OBPI-04.",
)
```

Then add `req_atomic` after `tasks` (or `citations` if `tasks` already exists):
```python
req_atomic: list[str] = Field(
    default_factory=list,
    description="REQ IDs exempt from subdivision-required check (ADR-0.0.64 / OBPI-04). "
                "Operator-authored escape valve; requires inline rationale in brief.",
)
```

No new field validator needed for either — `list[str]` with no format constraint at model level
matches the `citations` pattern. `parse_brief()` at line 86–114 filters by `model_fields.keys()` —
both new fields picked up automatically.

### Step 3 — Validator implementation

Edit `src/gzkit/commands/validate_cmd.py`.

Add helper at the top of the validator block (after line 545, following `_validate_req_kind_discipline`):

```python
def _validate_task_envelope_coherence(
    project_root: Path,
    *,
    lane_mode: str = "heavy",  # "heavy" → exit 3, "lite" → exit 2
) -> list[ValidationError]:
    """Three-signature task-envelope coherence validator (ADR-0.0.64 / OBPI-04)."""
    errors: list[ValidationError] = []

    # Signature (a): worklog events under active TASK with no task_id
    errors.extend(_sig_a_attribution_drift(project_root))

    # Signature (b): OBPI with all-seq=01 TASKs and no req_atomic exemption
    errors.extend(_sig_b_subdivision_skipped(project_root))

    # Signature (c): layer-drift across four channels
    errors.extend(_sig_c_layer_drift(project_root))

    return errors
```

Private helpers:

**`_sig_a_attribution_drift(project_root)`**:
- Read `project_root / ".gzkit" / "ledger.jsonl"` line by line
- Track active TASK windows: `task_started` → `task_completed` pairs
- For each event in a worklog event type (artifact_edited, gate_checked, etc.) that falls in an
  active TASK window, check `event.get("task_id")` is not None
- Return `ValidationError(type="task_envelope_coherence", artifact=event_ref, message=...)` per violation

**`_sig_b_subdivision_skipped(project_root)`**:
- Walk OBPI briefs via `brief_structure.parse_brief()` for each `.md` under `docs/design/adr/`
- For structured briefs (BriefStructure), collect `reqs` and `req_atomic`
- Query ledger for `task_started` events matching the OBPI ID
- For each REQ, collect TASK IDs; check if all are `seq=01`
- If all-seq=01 and REQ not in `req_atomic` → violation

**`_sig_c_layer_drift(project_root)`**:
- For each OBPI brief, read `tasks:` frontmatter field
- For each REQ in the brief, collect:
  - Channel 1: @advances registry — `get_task_registry()` from `gzkit.tasks`, filter by file paths in brief allowlist
  - Channel 2: frontmatter `tasks:` — BriefStructure.tasks if present (note: `tasks` is NOT a current field; the validator reads raw frontmatter for this channel)
  - Channel 3: commit trailers — `parse_task_trailers()` on recent commits touching allowlist files
  - Channel 4: ledger `task_id` — scan ledger events with this OBPI context
- If any two channels present TASK IDs and they disagree → violation
- Note: channels not present (empty/None) are skipped; drift only fires when two or more channels
  have conflicting non-empty TASK IDs

Wire into existing dispatch chain:
1. Add `check_task_envelope_coherence: bool = False` to `_collect_errors()` signature (line ~632)
2. Add `"task_envelope_coherence": check_task_envelope_coherence` to `explicit_scopes` dict (line ~713)
3. Add to `_explicit_scope_runners()`: `"task_envelope_coherence": lambda: _validate_task_envelope_coherence(project_root)`
4. Add `check_task_envelope_coherence: bool = False` to `validate()` signature (line ~1574)
5. Pass it through to `_collect_errors()` call
6. Add to `_other_scopes_active` check

**Lite vs Heavy behavior**: The `ValidationError.type` remains `"task_envelope_coherence"`; the
exit code is determined by the existing validator machinery (exit 3 for policy breach). For
Lite-lane behavior (warn-only), the validator returns errors but they're classified as warnings
via a `severity` field. Check how `--commit-trailers` handles severity — follow the same pattern.
If no severity mechanism exists, add a `severity: str = "error"` field to `ValidationError` or
use a separate `ViolationSeverity` enum that the exit-code mapper checks.

### Step 4 — CLI flag registration

Edit `src/gzkit/cli/parser_maintenance.py`:

Find the block where `--req-kind-discipline` is added (around line 650-674). After it, add:
```python
p_validate.add_argument(
    "--task-envelope-coherence",
    dest="check_task_envelope_coherence",
    action="store_true",
    default=False,
    help=(
        "Fail-close (exit 3 Heavy / exit 2 Lite) on three TASK attribution "
        "defects: worklog event with no task_id under active TASK, OBPI with "
        "all-seq=01 TASKs and no req_atomic exemption, and layer-drift across "
        "four discovery channels. ADR-0.0.64 / OBPI-04."
    ),
)
```

In the `set_defaults` lambda (lines 704–777), add:
```python
check_task_envelope_coherence=a.check_task_envelope_coherence,
```

### Step 5 — `gz task envelope diagnose <OBPI-ID>`

Edit `src/gzkit/commands/task.py`, add:
```python
def task_envelope_diagnose_cmd(obpi_id: str, *, as_json: bool = False) -> None:
    """Render per-channel TASK declarations for an OBPI side-by-side."""
    # Collect four channels for each REQ in the named OBPI
    # Channel 1: @advances registry (gzkit.tasks.get_task_registry())
    # Channel 2: frontmatter tasks: (read brief YAML)
    # Channel 3: commit trailers (parse_task_trailers on recent commits)
    # Channel 4: ledger task_id events

    # Render as table: REQ × Channel → TASK ID (or "—" if absent)
    # Flag drift rows with indicator
    # --json: emit dict with same structure
```

Edit `src/gzkit/cli/parser_artifacts.py`:
Find the `task_commands` subparser block (line ~1429-1544). Add after existing subcommands:
```python
p_task_envelope = task_commands.add_parser(
    "envelope",
    help="TASK envelope utilities",
)
envelope_cmds = p_task_envelope.add_subparsers(dest="envelope_command", required=True)
p_diagnose = envelope_cmds.add_parser(
    "diagnose",
    help="Show per-channel TASK declarations side-by-side for an OBPI",
)
p_diagnose.add_argument("obpi_id", help="OBPI identifier (e.g. OBPI-0.0.64-04)")
p_diagnose.add_argument("--json", dest="as_json", action="store_true")
p_diagnose.set_defaults(
    func=lambda a: _lazy("task_envelope_diagnose_cmd")(a.obpi_id, as_json=a.as_json)
)
```

Add `"task_envelope_diagnose_cmd": "gzkit.commands.task"` to the `_lazy` registry.

### Step 6 — `gz check` pipeline membership

Edit `src/gzkit/commands/quality.py`.

In `build_check_steps()` (line ~283), add an import and a step entry:
- Read the existing `run_*_audit` wrappers to understand the `CheckStepRunner` type and how they
  call validate_cmd functions. Follow the same wrapper shape.
- Add: `("Task envelope coherence", run_task_envelope_coherence_audit)` at the same position
  as `--commit-trailers` and `--cli-alignment` checks.
- Define `run_task_envelope_coherence_audit` as the wrapper function in the same file.

### Step 7 — Turn tests green

Run `uv run -m unittest tests/governance/test_task_envelope_coherence.py -v`.
Fix until all pass. Then run full suite: `uv run gz arb step --name unittest -- uv run -m unittest -q`.

### Step 8 — Docs (Heavy Gate 3)

Update `docs/user/manpages/validate.md`: add `--task-envelope-coherence` section with description,
exit codes, and example invocation.

Update `docs/user/manpages/task-start.md` OR create `docs/user/manpages/task-envelope-diagnose.md`
(prefer: update existing if the manpage covers `gz task` broadly; create new if per-verb pattern).

Run `uv run mkdocs build --strict` to verify.

## Verification

```bash
# Quality gates
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q

# Specific OBPI tests
uv run -m unittest tests/governance/test_task_envelope_coherence.py -v
uv run -m unittest tests/governance/test_brief_structure.py -v

# Behavioral smoke
uv run gz validate --task-envelope-coherence  # should exit 0 or 2/3 depending on state
uv run gz task envelope diagnose OBPI-0.0.64-04

# Heavy Gate 3
uv run mkdocs build --strict
```

## Covers parity

REQ-0.0.64-04-01 → `TestSignatureA.test_worklog_without_task_id_under_active_task_fails_heavy`
REQ-0.0.64-04-02 → `TestSignatureB.test_obpi_all_seq01_no_req_atomic_fails`
REQ-0.0.64-04-03 → `TestSignatureC.test_layer_drift_across_frontmatter_and_ledger_fails`
REQ-0.0.64-04-04 → `TestBriefStructure.test_req_atomic_optional_defaults_empty`
REQ-0.0.64-04-05 → `TestDiagnoseCmd.test_per_channel_side_by_side_rendered`
REQ-0.0.64-04-06 → `TestCheckPipelineIntegration.test_validator_runs_in_gz_check_pipeline`
REQ-0.0.64-04-07 → `TestSignatureB.test_req_atomic_is_sole_bypass`
