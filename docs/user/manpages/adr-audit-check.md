# gz adr audit-check

Verify linked OBPIs are completed with evidence and that `@covers`
decorators were authored independently of their REQ's closing receipt.

## NAME

gz-adr-audit-check — fail-closed gate over linked OBPI completion,
implementation evidence, REQ traceability, and the same-commit-window
`@covers` backfill heuristic.

## SYNOPSIS

```text
gz adr audit-check ADR-ID [--json] [--strict]
```

## DESCRIPTION

`gz adr audit-check` walks the linked OBPIs for one ADR and asserts:

1. **OBPI linkage and completion.** Every OBPI claimed in the ADR's
   checklist resolves to an OBPI brief on disk and has the matching
   ledger receipts indicating completion.
2. **Implementation evidence.** Each completed OBPI carries a
   non-placeholder `### Implementation Summary` and `### Key Proof`
   section that survive the closing-receipt copy.
3. **REQ traceability.** Every REQ enumerated in the ADR's child OBPIs
   reaches a `@covers(REQ-X.Y.Z-NN-MM)` annotation in `tests/**`. Gaps
   surface as advisory (yellow) by default; non-advisory severity
   (reserved for future per-REQ escalation) surfaces as red `FAIL` and
   exits 1.
4. **Same-commit-window `@covers` backfill heuristic.** Operationalizes
   the `Skipped cheap verification` failure shape codified in
   `.gzkit/rules/agent-failure-modes.md`. For every `@covers` decorator
   under `tests/**` whose REQ matches the audited ADR, the heuristic
   compares the decorator's introducing commit (via `git log --reverse
   -L<line>,<line>:<file>`) against the closing-receipt commit for
   that REQ. When *either* gap is below the configured threshold, the
   decorator is flagged. When *both* gaps exceed thresholds (the
   legitimate-evolution case), the decorator passes.

The heuristic catches the GHI #309 anti-pattern — silencing the audit
by adding a cosmetic `@covers` tag in the same commit as the REQ's
closing receipt without re-deriving the assertion from REQ semantics.

## OPTIONS

- `ADR-ID` — ADR identifier (e.g. `ADR-0.1.0`); required positional.
- `--json` — emit the audit result as JSON to stdout. Logs go to
  stderr. The JSON includes `covers_backfill_findings` and
  `covers_backfill_unresolvable` keys carrying the heuristic's output
  in addition to the existing `findings`, `coverage`,
  `coverage_findings`, `coverage_blocking`, and `coverage_advisory`
  keys.
- `--strict` — fail-close on any covers-backfill finding regardless of
  the ADR's lane and kind. By default the heuristic exits with the
  severity matrix below; under `--strict`, every finding becomes
  blocking. Heavy-lane and foundation-kind ADRs already fail-close
  unconditionally — `--strict` does not relax their behavior.

## THRESHOLDS

The heuristic loads its threshold knobs from `data/audit_thresholds.json`:

```json
{
  "max_covers_backfill_commits": 3,
  "max_covers_backfill_days": 7
}
```

Both keys are required (`extra="forbid"`) and must be non-negative
integers. The schema lives at `src/gzkit/schemas/audit_thresholds.json`
and is enforced by a Pydantic model with `frozen=True`. A missing or
malformed file exits 1 with a diagnostic naming the file and the
validation failure — the heuristic NEVER silently falls back to
compiled-in defaults at runtime.

## SEVERITY MATRIX

The severity assigned to backfill findings depends on three orthogonal
axes from `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix:

| ADR lane | ADR kind | `--strict` | Severity   | Exit code |
|----------|----------|------------|------------|-----------|
| lite     | feature  | unset      | warning    | 0         |
| lite     | feature  | set        | blocking   | 3         |
| heavy    | any      | any        | blocking   | 3         |
| any      | foundation | any      | blocking   | 3         |

Sensitivity is the third axis at the brief level (not at this
verb's surface) and is enforced separately by `gz validate
--sensitivity`.

## EXIT CODES

- `0` — Success. All linked OBPIs complete, evidence present, no
  blocking coverage gaps, no blocking backfill findings. Warnings
  may still print.
- `1` — User/config error. Linked OBPIs incomplete, blocking coverage
  gaps, or `data/audit_thresholds.json` missing or malformed.
- `2` — System error. Git history unavailable for one or more
  decorators (shallow clone, missing object, etc.) AND `--strict` is
  set. Default mode skips the unresolvable decorator and continues.
- `3` — Policy breach. Same-commit-window `@covers` backfill flagged
  as blocking per the severity matrix. Recovery: re-derive the
  assertion from REQ semantics per
  `.claude/rules/tests.md` § Invariant 6f, then commit the rewritten
  test in a new commit (away from the closing-receipt commit). Do not
  backfill cosmetic `@covers` decorators to silence the audit
  (GHI #272).

## EXAMPLES

### Default mode against a lite-feature ADR

```text
$ uv run gz adr audit-check ADR-0.1.0
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.1.0-01-foo

Coverage: 4/4 REQs covered (100%)
```

### Same-commit backfill on a lite-feature ADR (warning)

```text
$ uv run gz adr audit-check ADR-0.1.0
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.1.0-01-foo

Backfill 1 covers-backfill warning(s):
  tests/test_foo.py:42 REQ REQ-0.1.0-01-01 introduced @ aaaaaaa
  (0c / 0d before receipt evt-receipt-1); see
  .claude/rules/tests.md § Invariant 6f for remediation
```

Exit code: 0. Default behavior on lite-feature; surfaces the finding
as a warning but does not block.

### Same-commit backfill under `--strict` (blocking)

```text
$ uv run gz adr audit-check ADR-0.1.0 --strict
ADR audit-check: ADR-0.1.0
PASS All linked OBPIs are completed with evidence.
  - OBPI-0.1.0-01-foo

FAIL 1 covers-backfill finding(s):
  tests/test_foo.py:42 REQ REQ-0.1.0-01-01 introduced @ aaaaaaa
  (0c / 0d before receipt evt-receipt-1); see
  .claude/rules/tests.md § Invariant 6f for remediation
```

Exit code: 3. The same finding becomes blocking under `--strict`.

### JSON output

The `--json` form emits a single JSON object to stdout. To inspect it
on Windows-compatible terminals, write to a file first and then parse —
piping straight into `jq` runs `jq` against gzkit's UTF-8 output, which
crashes on cp1252. See `.gzkit/rules/cross-platform.md`
§ "Windows-safe helper patterns".

```bash
$ uv run gz adr audit-check ADR-0.1.0 --json > /tmp/audit.json
$ cat /tmp/audit.json
{
  "adr": "ADR-0.1.0",
  "passed": true,
  "checked_obpis": ["OBPI-0.1.0-01-foo"],
  "complete_obpis": ["OBPI-0.1.0-01-foo"],
  "findings": [],
  "coverage": { "total_reqs": 4, "covered_reqs": 4, ... },
  "coverage_findings": [],
  "coverage_blocking": [],
  "coverage_advisory": [],
  "covers_backfill_findings": [
    {
      "req_id": "REQ-0.1.0-01-01",
      "file": "tests/test_foo.py",
      "line": 42,
      "introducing_commit_sha": "aaaaaaa",
      "closing_receipt_id": "evt-receipt-1",
      "gap_commits": 0,
      "gap_days": 0,
      "severity": "warning"
    }
  ],
  "covers_backfill_unresolvable": []
}
```

## SEE ALSO

- `gz-adr-covers-check(1)` — sibling verb that audits `@covers`
  presence without the temporal heuristic.
- `gz-adr-audit-begin(1)` / `gz-adr-audit-end(1)` — co-presence
  marker management for the broader ADR audit ceremony.
- `.claude/rules/tests.md` § Invariant 6f — "Tests assert semantics,
  not strings" — the rule the remediation hint points at.
- `.gzkit/rules/agent-failure-modes.md` § Skipped cheap verification —
  the failure shape this heuristic operationalizes.
- ADR-0.0.23 — agent failure-mode taxonomy.
- GHI #309 — origin issue for the heuristic.
- GHI #272 — origin of the cosmetic-backfill anti-pattern.
