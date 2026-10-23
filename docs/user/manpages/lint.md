# gz lint

Run the lint checks: every Ruff rule against its baseline, and gzkit's two path lints.

## Usage

```bash
gz lint [OPTIONS] [PATHS...]
```

## Description

With no paths, runs three checks over the repository and fails when any of them fails:

- Ruff, judged against `data/ruff_baseline.json`. `[tool.ruff.lint]` selects `ALL` with
  preview, less the standing exceptions `pyproject.toml` records (RO-9 tranche 4). The
  findings the tree carried when the selection widened are held per file and rule, with a
  count, so the verdict is the baseline's: a finding no row holds, or one more than its row
  holds, fails; so does a row its findings no longer fill, and a row whose findings are gone.
  A tree with no baseline file fails every finding, which is plain `ruff check`.
- The ADR path-contract lint: no links to legacy ADR series folders.
- The parents-pattern lint: no `Path(__file__).parents[N]` in `src/gzkit/`.

Named paths lint those files with Ruff alone and judge only their rows; the pre-commit
`ruff-check` hook and the Claude hooks run it that way. Cognitive complexity is not a lint:
`gz validate --complexity-ceiling` scores it, as the "Complexity ceiling" step of `gz check`.

Run `gz lint`, not bare `ruff check`, for the gate's verdict: bare Ruff reports every held
finding too. `gz format` formats.

## Options

| Option | Description |
|--------|-------------|
| `PATHS` | Files or directories to lint with Ruff alone (default: the whole repository and the path lints) |
| `--fix` | Apply Ruff's safe fixes before judging what remains |
| `--ratchet` | Lower `data/ruff_baseline.json` to the tree's findings: a row is lowered or removed, never raised, and no row is added |

## Examples

```bash
gz lint
gz lint --fix src/gzkit/quality.py
gz lint --ratchet
```

A clean run:

```text
Running linters...
Ruff: no finding outside data/ruff_baseline.json (15044 held).
ADR path contract check passed.
No Path(__file__).parents[N] violations found.
Lint passed.
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All checks passed (`--ratchet`: the baseline was lowered) |
| 1 | A finding outside the baseline, or a row to lower or remove |
| 2 | Ruff could not run, or `data/ruff_baseline.json` is malformed |
