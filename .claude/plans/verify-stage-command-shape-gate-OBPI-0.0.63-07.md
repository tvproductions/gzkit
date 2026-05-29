# Plan: OBPI-0.0.63-07 verify-stage-command-shape-gate

**OBPI:** `OBPI-0.0.63-07-verify-stage-command-shape-gate`
**Parent ADR:** `ADR-0.0.63-closeout-ceremony-runtime-engine-parity`
**Lane:** Heavy
**Brief:** `docs/design/adr/foundation/ADR-0.0.63-closeout-ceremony-runtime-engine-parity/obpis/OBPI-0.0.63-07-verify-stage-command-shape-gate.md`

## Context

Close GHI #550: brief `## Verification` compound commands fail under the
shell-less runtime. Two surfaces, both consuming the existing BI-1 classifier
`brief_commands.is_shell_less_executable` (OBPI-02):

1. `gz validate --brief-command-shape` — fail-closed authoring-time gate
2. OBPI-pipeline verify stage — classify-before-dispatch, actionable message

## Destination-in-mind (Step 6a disclosure)

Before writing this plan I identified the exact insertion points from codebase
reads:
- `briefs.py` for the new scope function (mirrors `audit_brief_headings`)
- `parser_maintenance.py` line 663 region for the flag (mirrors `--req-kind-discipline`)
- `validate_cmd.py` `_explicit_scope_runners` + main signature for dispatch
- `obpi_stages.py` `_pipeline_verification_commands` for classify-before-dispatch

## Rejected alternatives

1. Inline the validator logic in `validate_cmd.py` directly — rejected: all
   brief audit functions delegate to `trust_audits/briefs.py`; inline would
   violate the established pattern.
2. Modify `_dispatch_verification_commands` to handle non-shell-less — rejected:
   brief Non-Goal says classify-before-dispatch, not make dispatch shell-aware.
3. Walk briefs in `validate_cmd.py` directly — rejected: brief-walking already
   lives in `briefs.py`; adding a second brief-walker elsewhere creates a fork.

## Files

| File | Change |
|------|--------|
| `src/gzkit/governance/trust_audits/briefs.py` | NEW `audit_brief_command_shape(project_root)` function |
| `src/gzkit/cli/parser_maintenance.py` | Register `--brief-command-shape` flag (after `--req-kind-discipline` ~line 663) |
| `src/gzkit/commands/validate_cmd.py` | Add `check_brief_command_shape` param + explicit_scope + _explicit_scope_runners entry |
| `src/gzkit/commands/obpi_stages.py` | Classify non-shell-less commands in `_pipeline_verification_commands`; fail with clear message |
| `.gzkit/templates/obpi.md` | `## Verification` gains single-program authoring guidance |
| `tests/governance/test_brief_command_shape.py` | Validator tests (positive + fail-closed) |
| `tests/commands/test_obpi_stages.py` | Verify-stage classification test |

## Steps

### Step 0: TDD RED — Write failing tests first

**`tests/governance/test_brief_command_shape.py`:**
- `test_compound_command_fails_validation`: fixture brief with `test -f x && echo ok` in Verification → `audit_brief_command_shape` returns errors, exit 3
- `test_shell_less_commands_pass_validation`: brief with `uv run gz check` in Verification → returns no errors
- `test_quoted_pipe_not_flagged`: brief with `python -c "a | b"` → not flagged (data, not syntax)

**`tests/commands/test_obpi_stages.py`:**
- `test_compound_verification_command_rejected`: `_pipeline_verification_commands` called with OBPI content containing `test -f x && echo ok` → that command is absent from the returned list; result carries an error entry

### Step 1: Implement `audit_brief_command_shape` in `briefs.py`

```python
def audit_brief_command_shape(project_root: Path) -> list[ValidationError]:
    """Fail closed (exit 3) when a brief Verification block contains
    a non-shell-less command (GHI #550, OBPI-0.0.63-07).

    Walks all OBPI-*.md briefs, extracts ## Verification fenced commands
    via brief_commands.extract_fenced_commands, and flags any command
    that fails brief_commands.is_shell_less_executable.
    """
    from gzkit.brief_commands import (  # noqa: PLC0415
        extract_fenced_commands,
        is_shell_less_executable,
    )
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    errors: list[ValidationError] = []
    for brief in sorted(adr_root.rglob("OBPI-*.md")):
        text = brief.read_text(encoding="utf-8")
        section = extract_markdown_section(text, "Verification") or ""
        for cmd in extract_fenced_commands(section):
            if not is_shell_less_executable(cmd):
                errors.append(
                    ValidationError(
                        type="brief_command_shape",
                        artifact=str(brief.relative_to(project_root)),
                        message=(
                            f"Non-shell-less Verification command: {cmd!r}. "
                            "Rewrite as separate single-program lines "
                            "(no &&, ||, |, ;, $(...), or redirects)."
                        ),
                    )
                )
    return errors
```

Note: `extract_markdown_section` is already imported/available in `briefs.py`
(verify at implementation time — if not, add the import from `gzkit.core.markdown`
or wherever it lives in the codebase).

### Step 2: Register flag in `parser_maintenance.py`

After the `--req-kind-discipline` block (~line 669):

```python
p_validate.add_argument(
    "--brief-command-shape",
    dest="check_brief_command_shape",
    action="store_true",
    default=False,
    help="Fail closed (exit 3) when a brief Verification block contains non-shell-less commands (OBPI-0.0.63-07).",
)
```

### Step 3: Wire in `validate_cmd.py`

3a. Add `check_brief_command_shape: bool = False` to the `run_validation` (or equivalent) function signature after `check_task_envelope_coherence`.

3b. Add to `explicit_scopes` dict:
```python
"brief_command_shape": check_brief_command_shape,
```

3c. Add to `_explicit_scope_runners` dict:
```python
"brief_command_shape": lambda: trust_audits.audit_brief_command_shape(project_root),
```

3d. Thread the parameter through all intermediate call sites (there are several — check `grep -n "check_req_kind_discipline\|check_task_envelope_coherence"` to find all).

### Step 4: Classify-before-dispatch in `obpi_stages.py`

In `_pipeline_verification_commands`, after the loop that appends non-baseline commands, add classification before returning:

```python
from gzkit.brief_commands import is_shell_less_executable  # (top or local import)

classified: list[str] = []
for cmd in deduped:
    if cmd in BASELINE_VERIFICATION:
        classified.append(cmd)  # baselines always pass through
        continue
    if not is_shell_less_executable(cmd):
        console.print(
            f"[red]BLOCKED[/red] Non-shell-less Verification command: {cmd!r}. "
            "Rewrite as separate single-program lines "
            "(no &&, ||, |, ;, $(...), or redirects)."
        )
        raise SystemExit(1)
    classified.append(cmd)
return classified
```

Alternative: return a sentinel / raise before dispatching, consistent with
`_run_pipeline_verify_stage`'s existing `failures` → `SystemExit(1)` pattern.
Pick the pattern that keeps `_pipeline_verification_commands` a pure-value
function — flag the bad command and let the verify stage raise, vs raise
inline. Decision: since `_pipeline_verification_commands` currently returns a
list and doesn't raise, prefer returning the list with non-shell-less commands
excluded PLUS a `console.print` warning, and let `_run_pipeline_verify_stage`
detect the empty/modified list via a separate returned flag — OR simply raise
inline in `_pipeline_verification_commands` (simpler, no caller changes). The
brief says "clear remediation message and NEVER dispatches it" — raise inline.

### Step 5: Update `.gzkit/templates/obpi.md` Verification section

Add a paragraph under `## Verification`:
```
> **Authoring contract:** Every command in this section must be a single-program,
> shell-less invocation — no `&&`, `||`, `|`, `;`, `$(...)`, or redirects.
> The OBPI-pipeline verify stage executes commands via `shlex.split` + `shell=False`
> (GHI #415); compound commands will be rejected at authoring time by
> `gz validate --brief-command-shape` and blocked at the verify stage.
> Write multi-step verification as separate `uv run …` lines.
```

Then run `uv run gz agent sync control-surfaces`.

### Step 6: Docs gate (Heavy lane)

```bash
uv run gz cli audit  # verify --brief-command-shape appears in manpage/index
uv run mkdocs build --strict
```

If `gz cli audit` fails on missing manpage entry: update the appropriate
manpage (check `docs/user/manpages/` for the validate manpage).

### Step 7: Run full quality gate

```bash
uv run gz check
uv run gz validate --brief-command-shape
uv run -m unittest tests.governance.test_brief_command_shape -v
uv run -m unittest tests.commands.test_obpi_stages -v
```

### Step 8: Pre-commit src/tests + git-sync

Pre-commit src/tests with `Task:` trailer before Stage 5 git-sync:
```bash
git add src/gzkit/governance/trust_audits/briefs.py \
        src/gzkit/cli/parser_maintenance.py \
        src/gzkit/commands/validate_cmd.py \
        src/gzkit/commands/obpi_stages.py \
        tests/governance/test_brief_command_shape.py \
        tests/commands/test_obpi_stages.py
git commit -m "feat(validate): brief-command-shape scope — reject non-shell-less Verification cmds (GHI #550)

Task: TASK-0.0.63-07-01-01-01"
```

Then `gz git-sync --apply` for the remaining surfaces.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --brief-command-shape
uv run -m unittest tests.governance.test_brief_command_shape -v
```

## Notes

- `extract_markdown_section` import: confirm location at implementation time
  (`grep -rn "def extract_markdown_section" src/`).
- `BASELINE_VERIFICATION` const: check current baseline set in `obpi_stages.py`
  to ensure classify-before-dispatch skips them correctly.
- The template update (`obpi.md`) fires `artifact_edited` event via git-sync;
  that is the SUPPORT proof channel for REQ-03.
- REQ-04 [STRUCTURAL-FENCE]: audited at ADR-0.0.63 closeout against BI-1.
- Heavy lane → Gate 5 human attestation required; use `--attestor-present`
  with `--accept-uncovered REQ-0.0.63-07-04 --accept-uncovered-reason "STRUCTURAL-FENCE: audited at ADR closeout"`.
