# gz lint

Run the lint checks: Ruff, complexipy and gzkit's two path lints.

## Usage

```bash
gz lint [OPTIONS]
```

## Description

Runs four checks over the repository and fails when any of them fails:

- `uv run ruff check .`: the rules `[tool.ruff.lint]` selects, including the
  cyclomatic ceiling (`C901`, `[tool.ruff.lint.mccabe] max-complexity`).
- `uv run complexipy --failed --plain`: cognitive complexity over the paths and ceiling in
  `[tool.complexipy]`. A function already over the ceiling is held to its score
  in `complexipy-snapshot.json`; a new or worsened one fails.
- The ADR path-contract lint: no links to legacy ADR series folders.
- The parents-pattern lint: no `Path(__file__).parents[N]` in `src/gzkit/`.

`gz lint` reports and does not fix. Use `uv run ruff check . --fix` for Ruff's
safe fixes and `gz format` for formatting.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All four checks passed |
| non-zero | A check failed; the code is the first failing check's own exit status |
