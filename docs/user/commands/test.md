# gz test

Run the project unit test suite using unittest.

## Usage

```bash
gz test [OPTIONS]
```

## Description

Executes all unit tests in the tests/ directory. Provides verbose output of test results, failures, and coverage summary. Required for all pre-commit checks.

## Options

| Option | Description |
|--------|-------------|
| `--bdd` | Also run behave scenarios (Heavy-lane / closeout-ceremony tier) in addition to the unit suite |
| `--obpi OBPI` | Scope the run to tests whose `@covers(REQ-...)` decorators map to one OBPI's requirements |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All tests passed |
| 1 | One or more tests failed |
