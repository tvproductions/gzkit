# gz complexity advise

Trigger-time complexity advisor diagnosis for files and directories.

## NAME

gz complexity advise — analyze a file or directory for complexity-band
crossings and emit a doctrinal diagnosis (archetype, authority, proof
range, recommended move) for each crossing.

## SYNOPSIS

```text
gz complexity advise <path> [--json] [--quiet] [--verbose] [--dry-run]
                            [--auto-chain] [--rule-path PATH]
```

## DESCRIPTION

`gz complexity advise` is the operator-facing trigger-time response
surface introduced by ADR-0.0.29 (the third foundation in the four-ADR
complexity-doctrine cluster). The verb loads the canonical threshold
table at `.gzkit/rules/complexity-thresholds.md` (ADR-0.0.28), measures
per-function `radon_cc` for every Python file under `<path>` via
radon's Python API (`radon.complexity.cc_visit`), and runs the
OBPI-0.0.29-02 :class:`DiagnosisEngine` against each band crossing.

For every crossing, the engine emits an `AdvisorDiagnosis` carrying:

- the canonical refactor archetype (one of ten enumerated values per
  ADR-0.0.29 § Decision rationale #2),
- the cited doctrinal authority (Fowler / Martin / Page-Jones /
  Constantine — the four-authority canon ADR-0.0.27 binds),
- a non-empty proof tuple linking to the responsible AST nodes /
  line ranges (verdict ↔ proof binding per ADR-0.0.29 § Decision
  rationale #5),
- the recommended-move excerpt sourced from the active
  distilled-characteristics document (never fabricated).

Default output is structured human-readable prose; `--json` mode
emits the canonical Pydantic serialization as a JSON array. The
`--auto-chain` flag is reserved for OBPI-0.0.29-05 (the xenon
auto-fire hook) and is currently a no-op marker.

## OPTIONS

- `<path>` — File or directory to analyze. Directories are walked
  recursively for `*.py` files; non-Python files are skipped.
- `--json` — Emit the diagnosis list as a JSON array (one
  `AdvisorDiagnosis` object per crossing). Validates against
  `src/gzkit/schemas/advisor_diagnosis.json`.
- `--quiet` — Errors only; no progress output.
- `--verbose` — Debug output (per-file analysis trace).
- `--dry-run` — Reserved; analysis is read-only and dry-run is a no-op.
- `--auto-chain` — Reserved for OBPI-0.0.29-05.
- `--rule-path PATH` — Override the threshold rule path. Default is
  `.gzkit/rules/complexity-thresholds.md`. Test injection only;
  production runs use the default.
- `--help`, `-h` — Show usage and exit 0.

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Success — no crossings, or all crossings stayed at advise/warn band |
| 1 | User / config error (bad path, malformed flags) |
| 2 | System / IO error (missing threshold table, AST parse failure, engine cannot resolve cited distilled-characteristics) |
| 3 | Policy breach — one or more `block`-band crossings |

## EXAMPLES

```bash
gz complexity advise src/gzkit/commands/validate.py
gz complexity advise src/gzkit/ --json
gz complexity advise tests/ --quiet
```

## SEE ALSO

- `docs/user/runbook.md` § "Governance Doctrine Surfaces" — operator
  workflow for previewing advisor diagnoses before commit.
- `docs/user/manpages/gz-complexity-advise.md` — manpage form of this
  documentation.
- ADR-0.0.29 — the trigger-time response surface invariant.
- ADR-0.0.28 — the threshold table this verb consumes.
- [`gz complexity distill`](complexity-distill.md) — produces the
  distilled-characteristics document this verb cites for
  doctrinal-frame attribution.
