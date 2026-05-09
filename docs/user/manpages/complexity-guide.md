# gz complexity guide

Authoring-time complexity hint surface for files and directories.

## NAME

gz complexity guide — surface authoring-time complexity hints for functions
approaching the warn threshold (advise-band crossings only).

## SYNOPSIS

```text
gz complexity guide <path> [--json] [--quiet] [--verbose] [--help]
```

## DESCRIPTION

`gz complexity guide` is the operator-facing authoring-time preview surface
introduced by ADR-0.0.30 (OBPI-0.0.30-01). The verb loads the canonical
threshold table at `.gzkit/rules/complexity-thresholds.json` (ADR-0.0.28),
measures per-function `radon_cc` for every Python file under `<path>` via
the OBPI-0.0.30-03 authoring engine, and emits an `AuthoringHint` for each
`advise`-band crossing.

The authoring surface is **design-time only** — it never blocks. It is
intended for use while editing a file to preview which functions are
approaching the warn threshold *before* committing. Functions that have
already crossed into the `warn` or `block` band are the `gz complexity advise`
surface's responsibility; this verb filters those crossings out.

For each `advise`-band crossing the verb emits:

- the canonical refactor archetype (one of ten enumerated values per
  ADR-0.0.29 § Decision rationale #2),
- position within the `advise` band (`approaching` or `approaching_warn`),
- the one-line doctrinal-frame headline sourced from the active
  distilled-characteristics document,
- the recommended-move excerpt.

Default output is human-readable prose (one block per hint). `--json` emits
the canonical `AuthoringHint` Pydantic serialization as a JSON array
validating against `src/gzkit/schemas/authoring_hint.json`.

## OPTIONS

- `<path>` — File or directory to analyze. Directories are walked
  recursively for `*.py` files; non-Python files are skipped.
- `--json` — Emit the hint list as a JSON array (one `AuthoringHint`
  object per advise-band crossing).
- `--quiet` — Suppress output; rely on exit code only.
- `--verbose` — Emit debug output to stderr.
- `--help`, `-h` — Show usage and exit 0.

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Success — no advise-band crossings, or hints emitted |
| 1 | User / config error (bad path, malformed flags) |
| 2 | System / IO error (missing threshold table, AST parse error) |

**Exit 3 is NOT used by this verb.** The authoring-time surface never blocks;
that is `gz complexity advise`'s role (exit 3 = block-band crossing).

## EXAMPLES

```bash
# Preview hints on a single file before committing
gz complexity guide src/gzkit/commands/validate.py

# Walk a directory
gz complexity guide src/gzkit/complexity/

# Machine-readable AuthoringHint JSON array
gz complexity guide src/gzkit/commands/ --json

# Clean file — no output beyond "No advise-band hints found."
gz complexity guide tests/test_simple.py
```

## SEE ALSO

- `docs/user/runbook.md` § "Governance Doctrine Surfaces" — operator
  workflow for previewing authoring-time complexity hints before commit.
- [`gz complexity advise`](complexity-advise.md) — trigger-time gate
  (runs at commit time; exit 3 on block-band crossing).
- [`gz complexity distill`](complexity-distill.md) — produces the
  distilled-characteristics document this verb cites for
  doctrinal-frame attribution.
- ADR-0.0.30 — the authoring-guidance surface this verb implements.
- ADR-0.0.28 — the threshold table this verb consumes.
