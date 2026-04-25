# OBPI-0.0.21-07-bdd-chores-distribution: BDD Chores Distribution

OBPI: `OBPI-0.0.21-07-bdd-chores-distribution`

## Context

ADR-0.0.21 makes chores a first-class gzkit surface with two-surface (canonical
package + project overlay) layout. OBPIs 01-06 landed the physical migration,
config schema, wheel packaging, project-first/package-fallback resolver,
`scaffold_core_chores` in `gz init`, and rule/doc updates. **No end-to-end
proof exists** that a freshly-installed gzkit delivers a working chores system
across the install → scaffold → list → repair lifecycle.

This OBPI authors `features/chores_distribution.feature` — Heavy-lane Gate 4
proof that the install-and-scaffold pipeline works as a single integrated
system, with `@REQ-0.0.21-07-NN` scenario tags so
`gz validate --behave-req-tags` mechanically maps coverage to this OBPI's
requirements.

## Brief-vs-Surface Reconciliation

The brief uses the phrase `gz init --repair` in REQ-04 and REQ-05. **No
explicit `--repair` flag exists** on `gz init` — the repair path is the
implicit branch taken when re-running `gz init` on an already-initialized
project (no `--force`). `_repair_missing_artifacts` ->
`_repair_chores` does the work, and `--yes` IS a real flag controlling
the merge-diff confirmation. The plan honors the *semantic* intent of REQ-04
and REQ-05 (skip_existing operator-edit preservation; merge diff requires
`--yes`) using the actual surface (`gz init` re-runs). This is the
"actual surface, not the brief's loose phrasing" path that
AGENTS.md § DO IT RIGHT #6g (verify the runtime surface) prescribes.

## Approach

### Scenario design (4 scenarios, mapped to REQs 02-05)

**Scenario A — Package fallback works without `gz init`** (REQ-02)

Tags: `@REQ-0.0.21-07-01 @REQ-0.0.21-07-02 @REQ-0.0.21-07-06 @REQ-0.0.21-07-07`
(carries the meta-REQs for the feature itself).

```gherkin
Given a fresh empty project directory
When I run "gz chores list" as a subprocess
Then the subprocess exits with code 0
And the subprocess output contains "quality-check"
And the subprocess output contains "skill-manifest-sync"
```

Rationale: empty cwd has no `.gzkit/chores/`, so resolver falls back to
package resource. Picks two stable canonical slugs from
`src/gzkit/chores/registry.json`.

**Scenario B — `gz init` populates project chores; `--explain` reports project source** (REQ-03)

Tag: `@REQ-0.0.21-07-03`

```gherkin
Given a fresh empty project directory
When I run "gz init" as a subprocess
And I run "gz chores list --explain" as a subprocess
Then the subprocess exits with code 0
And the file ".gzkit/chores/quality-check/CHORE.md" exists
And every chore row in the subprocess output reports "project" source
```

The "every chore row reports project source" assertion is implemented as a
step that parses the table output (exclude header rows) and asserts no row
contains "package" or "missing" in the Source column.

**Scenario C — Re-running `gz init` preserves operator edits** (REQ-04)

Tag: `@REQ-0.0.21-07-04`

```gherkin
Given a fresh empty project directory
And the workspace has been initialized via gz init
And the operator edits ".gzkit/chores/quality-check/CHORE.md" with marker "OPERATOR-EDIT-MARKER-XYZ"
When I run "gz init" as a subprocess
Then the subprocess exits with code 0
And the file ".gzkit/chores/quality-check/CHORE.md" contains "OPERATOR-EDIT-MARKER-XYZ"
```

Rationale: `_repair_chores` calls `scaffold_core_chores(skip_existing=True)`,
so the operator's CHORE.md edit MUST survive.

**Scenario D — Merge diff fires for canonical-only slug; `--yes` writes** (REQ-05)

Tag: `@REQ-0.0.21-07-05`

```gherkin
Given a fresh empty project directory
And the workspace has been initialized via gz init
And the slug "quality-check" has been removed from ".gzkit/chores/registry.json"
When I run "gz init --yes" as a subprocess
Then the subprocess exits with code 0
And the subprocess output contains "+ quality-check"
And ".gzkit/chores/registry.json" contains slug "quality-check"
```

Rationale: removing a slug from project-local registry simulates "canonical
has new slug not yet in project". The merge_chores_registry diff prints
`+ <slug>` for additions; `--yes` skips the interactive confirm and writes.

### Subprocess invocation strategy

Per brief REQ-3, scenarios MUST exercise the **real wheel** — not a mocked
in-process `main()`. The brief explicitly permits `pip install -e .` (which
is what `uv sync` does in this repo's `.venv`) with cwd manipulated so
resolver and scaffolder see clean state.

Implementation: invoke via `[sys.executable, "-m", "gzkit", *args]` with
`cwd=context._tmpdir`. This:

- Uses the editable install already in `.venv` (the "real wheel" semantic)
- Resolves `gzkit.chores` package resources from the real installed location
  via `importlib.resources` (the resolver path under test)
- Avoids `uv run` complications (no need to point `uv` at the gzkit project
  root from within a tempdir cwd)
- Cross-platform safe (uses `sys.executable`, `pathlib.Path`, UTF-8 explicit)

### New step module: `features/steps/chores_distribution_steps.py`

New steps:

| Step | Purpose |
|------|---------|
| `Given a fresh empty project directory` | Asserts cwd is the per-scenario tempdir from `environment.py:before_scenario`; no-op confirmation step |
| `Given the workspace has been initialized via gz init` | Runs `gz init` subprocess in cwd; asserts exit 0 |
| `Given the operator edits "{path}" with marker "{marker}"` | Appends marker line to file |
| `Given the slug "{slug}" has been removed from "{registry_path}"` | Loads JSON, removes entry from `chores` list, writes back |
| `When I run "{command}" as a subprocess` | `shlex.split(command)`, replace leading `gz` with `[sys.executable, "-m", "gzkit"]`, capture exit + stdout/stderr |
| `Then the subprocess exits with code {code:d}` | Asserts on `context.subprocess_exit_code` |
| `Then the subprocess output contains "{text}"` | Asserts on `context.subprocess_output` |
| `Then every chore row in the subprocess output reports "{source}" source` | Parses table rows; asserts every data row's last column contains the expected source label |
| `Then "{path}" contains slug "{slug}"` | Loads JSON registry; asserts slug present in chores list |

Existing steps (`features/steps/gz_steps.py`) reused: `Then the file "{path}"
exists`, `Then the file "{path}" contains "{text}"`. These are file-system
checks unrelated to in-process `main()` invocation, so they work fine with
subprocess scenarios.

### Behave coverage waiver — none

Every REQ in Acceptance Criteria (01-07) gets a scenario tag. No waiver
needed; `data/behave_coverage_waivers.json` is untouched.

## Files to create / modify

**Create:**

- `features/chores_distribution.feature` — 4 scenarios with `@REQ-0.0.21-07-NN`
  scenario-level tags
- `features/steps/chores_distribution_steps.py` — new step module (estimate
  ~150 lines)

**Do not modify:**

- `features/environment.py` — existing `before_scenario` tempdir + cd handling
  is sufficient; no new fixture hook needed
- `src/gzkit/**` — denied by brief allowlist
- `tests/**` — denied by brief allowlist

## Verification

After authoring, run in order:

```bash
# Lint + typecheck on new step module
uv run gz lint
uv run gz typecheck

# Feature file exists with expected REQ tag count
test -f features/chores_distribution.feature
grep -c "@REQ-0.0.21-07-" features/chores_distribution.feature   # expect >= 7

# Scenarios pass end-to-end
uv run behave features/chores_distribution.feature

# REQ coverage validator passes
uv run gz validate --behave-req-tags

# Heavy-lane gates
uv run mkdocs build --strict
```

## Reuse references

- `features/environment.py:11-21` — per-scenario tempdir + cd, already
  isolates state per `.gzkit/rules/tests.md`
- `features/steps/gz_steps.py:230-238` — `Then the file "..." exists/contains`
  step reuse
- `features/arb.feature:1-16` — `@REQ-X.Y.Z-NN-MM` scenario-level tag
  pattern (canonical example)
- `src/gzkit/chores/__init__.py:127-217` — `merge_chores_registry()` diff
  format (`+ <slug>` markers Scenario D asserts on)
- `src/gzkit/commands/chores.py:294-301` — `_explain_source()` labels
  ("project" / "package..." / "missing") that Scenario B's "every row
  reports project source" assertion validates

## Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Subprocess startup adds ~2s per scenario × 4 = ~8s runtime | Within heavy-tier behave ceiling per `.gzkit/rules/tests.md` § Smoke/BVT |
| `gz init` subprocess may emit ANSI codes that break `+ quality-check` substring assertions | Parse subprocess output with `--no-color`-equivalent path or strip ANSI before assertion; use plain stable substring search |
| Scenario D depends on the project-local registry being writable JSON | The scaffold step writes the registry; test owns the file after Scenario B runs the init step |
| `quality-check` slug rename in future could break stable-substring assertions | Acceptable — this is the canonical contract surface; if the slug renames, this BDD must update with it (same coupling as the rest of the chores test surface) |

## Iron Law reminder

This is Stage 2 → 3 → 4 → 5 of a Heavy-lane + foundation-kind OBPI. After
implementation, the pipeline runs Stage 3 (verify), Stage 4 (HUMAN GATE —
present evidence and wait for attestation), Stage 5 (sync + reconcile + ADR
status refresh + git-sync ×2). No premature summary after Stage 2.
