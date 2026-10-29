# RO-9 tranche 7: the checkpoint's Red witness (2026-10-29)

A dated record. It witnesses the production hunks of the tranche 7 checkpoint
`b5d6335cf` against the tests written after it, on the operator's ruling of
2026-10-29 (verbatim: "a").

## Why a sweep and not `gz arb red --commit`

`gz arb red --commit b5d6335cf` grades a commit's hunks against the test
modules that same commit touched. The checkpoint was committed before its tests
on the operator's word ("commit now"), so its own tests were two lightly
adjusted modules, and the verdict was `undriven`: 22 hunks survived (receipt
`arb-red-commit-b5d6335cfb83-33b9efa3129b40bb801ad40cf89edbb3`). The tests
landed in `82bb9eddc` and in the commit that carries this record. No re-run of
the per-commit witness can see them, so this sweep reverts each surviving hunk
in turn and runs the current tests against it.

## Binding

| Fact | Value |
|---|---|
| Tree | `9276d47c2` for every source swept; `tests/commands/test_init.py` as committed with this record (sha256 `d259ff19…`) |
| Command | `uv run python docs/governance/ro9-tranche7-red-sweep-2026-10-29-evidence/sweep_b5d6335cf.py <out.json>`, from the repository root |
| Test command per mutant | `python -m unittest -v tests.commands.test_init` (71 tests in each baseline) |
| Engine | `gzkit.mutation_witness.run_mutation_sweep`: one subprocess per mutant, its own `PYTHONPYCACHEPREFIX`, a killed verdict only on a clean assertion failure of the nominated test |
| Environment | Python 3.14.10, uv 0.13.6, macOS arm64 |
| Raw result | `sweep_b5d6335cf.json`, with `output_tail`, `baseline_output_tail` and `pycache_prefix` removed because they carry machine-local paths, and `source` made repository-relative. Every `source_sha256` equals its `restored_source_sha256`: each file was restored byte for byte |

## Result

All three sweeps are conclusive (`is_conclusive` true): 13 killed, 2 survived,
none invalid or inconclusive.

| Hunk (line in `b5d6335cf`) | Mutant | Outcome | Killing test |
|---|---|---|---|
| `init_cmd.py:407-414` | no-floor branch returns a floor instead of refusing | killed | `test_missing_python_floor_refuses_to_pin_one` |
| `init_cmd.py:426-442` | missing uv returns instead of refusing | killed | `test_missing_uv_names_the_install_step` |
| `init_cmd.py:442-450` | failing uv command returns instead of refusing | killed | `test_failing_uv_command_names_the_command_and_stops` |
| `init_cmd.py:483-489` | non-`src` move skipped | killed | `test_non_src_source_root_moves_the_package_and_tells_uv_build` |
| `init_cmd.py:487-488` | empty `src/` left behind | killed | same |
| `init_cmd.py:492-495` | governance README not written | killed | `test_readme_points_at_the_agent_contract` |
| `init_cmd.py:500` | CI workflow not written | killed | `test_ci_workflow_runs_uv_with_the_lock_checked` |
| `init_cmd.py:827-830` | dry-run seeds instead of planning | killed | `test_repair_dry_run_plans_the_seed_without_writing_it` |
| `init_cmd.py:1156-1162` | repair does not seed | killed | `test_repair_seeds_a_missing_baseline` |
| `init_cmd.py:1345` | repair drops `--project-type` | killed | `test_repair_builds_the_requested_project_type` |
| `parser_governance.py:175` | `--project-type` not passed to `init` | killed | `test_each_project_type_builds_its_uv_shape` |
| `astral_discipline.py:642-643` | existing baseline overwritten | killed | `test_existing_baseline_is_left_untouched` |
| `astral_discipline.py:652` | row count not returned | killed | `test_returns_the_number_of_rows_it_wrote` |
| `parser_governance.py:123` | `--help` example removed | survived | none: help text, graded by `gz cli audit` rather than a unit test |
| `astral_discipline.py:64` | `__all__` entry removed | survived | none: an export list, which no behavior reads |

## What this does not establish

- The import hunks the per-commit witness listed (`init_cmd.py:3-4` and `:28`)
  were not swept. An import has no behavior of its own; the hunks that use it
  are graded above.
- The hunks the per-commit witness graded `inconclusive` or `invalid` and that
  are not listed above were not re-swept. They are the bodies of functions the
  rows above exercise, not separate guards.
- Two of the tests that kill a mutant were strengthened during the sweep. They
  first read the missing file before asserting it existed, so the mutant ended in
  `FileNotFoundError`, which the engine rightly graded `inconclusive`. The record
  above is the re-run after that change.
- Each mutant is the agent's own rendering of what the hunk's absence would
  do. A different rendering could grade differently.
