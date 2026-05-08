# gz-complexity-advise

Trigger-time complexity advisor diagnosis for files and directories.

## NAME

gz-complexity-advise — analyze a file or directory for complexity-band
crossings and emit a doctrinal diagnosis (archetype, authority, proof
range, recommended move) for each crossing.

## SYNOPSIS

```text
gz complexity advise <path> [--json] [--quiet] [--verbose] [--dry-run]
                            [--auto-chain] [--rule-path PATH]
```

## DESCRIPTION

`gz complexity advise` is the operator-facing trigger-time response surface
introduced by ADR-0.0.29 (the third foundation in the four-ADR
complexity-doctrine cluster). The verb loads the canonical threshold
table at `.gzkit/rules/complexity-thresholds.md` (ADR-0.0.28), measures
per-function `radon_cc` for every Python file under `<path>`, and runs
the OBPI-0.0.29-02 diagnosis engine against each band crossing.

For every crossing, the engine emits an `AdvisorDiagnosis` carrying
the canonical refactor archetype, the cited doctrinal authority
(Fowler / Martin / Page-Jones / Constantine), a non-empty proof tuple
linking to the responsible AST nodes / line ranges, and the
recommended move excerpted from the active distilled-characteristics
document. The verdict ↔ proof binding (per ADR-0.0.29 § Decision
rationale #5) is structural — the engine fails closed if proof
cannot be produced.

The default output is structured human-readable prose (verbose `AdHocPresenter`);
`--json` mode emits the canonical Pydantic serialization (REQ-0.0.29-03-04).
The `--auto-chain` flag (introduced in OBPI-0.0.29-05 for the xenon auto-fire hook)
activates the concise `AutoChainPresenter` output mode (landed in OBPI-0.0.29-06).

## OPTIONS

- `<path>` — File or directory to analyze. Directories are walked
  recursively for `*.py` files; non-Python files are skipped.
- `--json` — Emit the diagnosis list as a JSON array (one
  `AdvisorDiagnosis` object per crossing). Validates against
  `src/gzkit/schemas/advisor_diagnosis.json`.
- `--quiet` — Errors only; no progress output.
- `--verbose` — Debug output (per-file analysis trace).
- `--dry-run` — Reserved; analysis is read-only and dry-run is a no-op.
- `--auto-chain` — Signals ad-hoc pathway is invoked by the xenon-as-gate
  auto-chain hook (OBPI-0.0.29-05). Activates the concise `AutoChainPresenter`:
  one-line summary per diagnosis plus "run `gz complexity advise <path>` for
  full detail" hint. Without this flag (ad-hoc), the verbose `AdHocPresenter`
  is used (full doctrinal frame, source snippets, attestation reference).
- `--rule-path PATH` — Override the threshold rule path. Default is
  `.gzkit/rules/complexity-thresholds.md`. Test injection only;
  production runs should use the default.
- `--help`, `-h` — Show usage and exit 0.

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Success — no crossings, or all crossings stayed at advise/warn band |
| 1 | User / config error (bad path, malformed flags) |
| 2 | System / IO error (missing threshold table, AST parse failure, engine cannot resolve cited distilled-characteristics) |
| 3 | Policy breach — one or more `block`-band crossings |

The exit-code map follows the four-code standard documented in
`.claude/rules/cli.md` § "Exit Codes (Standard 4-Code Map)".

## EXAMPLES

Analyze a single file with default prose output:

```bash
gz complexity advise src/gzkit/commands/validate.py
```

Analyze a directory and emit machine-readable JSON:

```bash
gz complexity advise src/gzkit/ --json
```

Analyze tests directory in quiet mode (errors only):

```bash
gz complexity advise tests/ --quiet
```

Use a non-canonical threshold rule (test injection):

```bash
gz complexity advise subject.py --rule-path /tmp/synthetic-rules.md
```

### Ad-hoc preview pathway (verbose output)

Analyze a file in ad-hoc mode (default, without `--auto-chain`):

```bash
gz complexity advise src/foo.py
```

This emits the verbose `AdHocPresenter` output: each crossing includes the
metric name, band (`warn` or `block`), numeric value, refactor archetype,
full doctrinal frame (authority and citation), source-line snippets from the
proof range, recommended move, and intrinsic attestation reference. If no
crossings are detected, output is: "no crossings detected, checked N functions
across M metrics".

Example output snippet:
```
CROSSING: radon_cc (function foo) — band: warn (threshold: 10)
  Value: 12
  Archetype: ExtractMethod
  Authority: Fowler, Refactoring (1999)
  Proof: src/foo.py:45-62 (radon_cc=12, 2 decision points)

  Source snippet:
  45 def foo(x, y):
  46     if x > 0:
  47         ...
  62         return result

  Recommended move: Extract the conditional logic (lines 46–60) into a
  separate function. See `.gzkit/rules/complexity-thresholds.md` for
  band definitions.

  Attestation: Gate 5 witness required if moving to foundation scope
  (ADR-0.0.29 § Attestation).
```

### Auto-chain context (concise output)

Analyze a file with `--auto-chain` (invoked by the xenon hook):

```bash
gz complexity advise src/foo.py --auto-chain
```

This emits the concise `AutoChainPresenter` output: a one-line summary per
diagnosis (metric, band, archetype, file:line, recommended move) followed by
a footer hint. If no crossings are detected, output is silent (no output).

Example output snippet:
```
src/foo.py:45 | radon_cc warn | ExtractMethod | Extract conditional logic (lines 46–60)
Run `gz complexity advise src/foo.py` for full detail.
```

## SEE ALSO

- `docs/user/runbook.md` § "Complexity doctrine surfaces" — operator
  workflow for previewing advisor diagnoses before commit.
- ADR-0.0.29 § Decision — the trigger-time response surface invariant.
- ADR-0.0.28 — the threshold table this verb consumes.
- `.gzkit/rules/complexity-thresholds.md` — canonical band definitions.
- `gz-complexity-distill(1)` — produces the distilled-characteristics
  document the engine cites for doctrinal-frame attribution.

## NOTES

- The advisor consumes the `ThresholdTable` model directly (no JSON
  re-parse) per ADR-0.0.29 § Decision rationale #1.
- `radon_cc` is the metric covered in OBPI-0.0.29-03; additional
  metrics (`radon_mi`, `lizard_*`, `cohesion_*`) are surfaced by
  subsequent OBPIs in the cluster.
- Foundation-kind brief-level Gate 5 stacks per ADR-0.0.18 — every
  diagnosis change requires Gate 5 walkthrough at the OBPI level.
