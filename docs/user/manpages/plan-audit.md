# gz plan audit

Structural prerequisite check for plan-OBPI alignment.

## Usage

```
gz plan audit OBPI-X.Y.Z-NN [--json]
```

## Description

Runs deterministic structural checks:
- ADR package directory exists
- OBPI brief file exists
- Plan file exists in `.claude/plans/`
- Plan file paths stay within brief allowed paths
- Brief allowed paths exist (or are declared as created by the brief or plan)
- Generated vendor mirrors are refused, with the canonical edit path reported

A leading `./` does not exempt a generated mirror from refusal. CREATE
declarations exempt missing paths only; they cannot authorize editing a mirror.

Scope comparison recognizes single backtick-delimited path tokens under any
root (including `.gzkit/`, `data/`, `scripts/`, and custom roots), root filenames
such as `AGENTS.md`, and legacy unquoted `src/`, `tests/`, and `docs/` paths.
Source coordinates (`:12`, `:12-15`, `:12:3`) are removed before comparison.
Literal entries allow their named subtree; glob entries use whole-path matching.
Leading `./` is equivalent, but absolute paths and paths escaping the project
are refused even when the allowlist names `.`. CREATE declarations do not expand
the allowlist. This is explicit-token checking, not semantic discovery of paths
hidden in arbitrary prose, commands, URLs, or filenames containing spaces.

Writes a receipt to `.claude/plans/.plan-audit-receipt-{OBPI-ID}.json`.

## Arguments

| Argument | Description |
|----------|-------------|
| `OBPI-X.Y.Z-NN` | OBPI identifier |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | PASS -- all prerequisites met |
| 1 | FAIL -- structural gaps found |
| 2 | System error |

## Examples

```bash
gz plan audit OBPI-0.1.0-01
gz plan audit OBPI-0.1.0-01 --json
```
