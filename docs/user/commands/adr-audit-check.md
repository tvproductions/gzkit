# gz adr audit-check

Verify linked OBPIs for one ADR are completed and include implementation evidence.

---

## Usage

```bash
gz adr audit-check <ADR-ID> [--json] [--strict]
```

---

## Flags

- `--json` — emit the audit result as JSON (machine-readable; logs go to stderr).
- `--strict` — fail-close (exit 3) on any same-commit-window `@covers`
  backfill finding. Without this flag, backfill findings are surfaced as
  warnings (exit 0) regardless of lane or kind, pending GHI #385
  (the heuristic currently false-positives on every TDD-disciplined OBPI
  shipped via `gz git-sync` because the introducing commit and the closing
  receipt are the same ceremony commit). The temporal heuristic flags
  decorators introduced within `data/audit_thresholds.json` thresholds
  (default 3 commits / 7 days) of the REQ's closing receipt.

---

## What It Checks

- ADR-to-OBPI linkage from ledger and artifact metadata
- OBPI completion markers (`status: Completed` and/or `**Brief Status:** Completed`)
- Presence of non-placeholder implementation summary evidence
- Requirement coverage from `@covers` test annotations (advisory by default;
  severity is fail-open so Lite-lane docs-only OBPIs do not block the audit)
- **Same-commit-window `@covers` backfill heuristic** — flags decorators
  introduced within `max_covers_backfill_commits` commits OR
  `max_covers_backfill_days` days of the REQ's closing receipt
  (`data/audit_thresholds.json`). Catches the GHI #309 cosmetic-backfill
  anti-pattern that would otherwise silence the audit. Warns by default
  regardless of lane or kind; fails-close (exit 3) only under `--strict`
  pending GHI #385 (heuristic does not yet distinguish `Ceremony: gz-git-sync`
  ceremony commits from cosmetic backfill).

Implementation-summary evidence is parsed from inline markdown bullets in
`### Implementation Summary`, for example:

- `- Files created/modified: src/gzkit/cli.py, tests/test_cli.py`
- `- Tests added: tests/test_cli.py`
- `- Date completed: 2026-02-23`

Nested bullets or empty placeholder values can cause evidence to be treated as missing.

Returns explicit missing-proof findings and exits non-zero on failure.

---

## Coverage Section

The audit-check output includes a coverage section showing which REQs under
the target ADR are proven by `@covers` test annotations.

- **Per-OBPI rollup**: Each OBPI's REQ coverage count and percentage.
- **Uncovered REQs**: Surfaced with their severity. Advisory-severity entries
  print as a yellow `Advisory` section and do not block the audit; non-advisory
  severities (reserved for future per-REQ escalation) print as red `FAIL` and
  exit 1. OBPI completeness and evidence gaps — tracked under the separate
  `findings` key — remain fail-closed regardless of coverage severity.
- **JSON output**: The `coverage` key contains `total_reqs`, `covered_reqs`,
  `uncovered_reqs`, `coverage_percent`, `by_obpi` array, and `uncovered` list
  (each entry carries a `severity` field). The `coverage_findings` key
  enumerates every uncovered REQ; `coverage_blocking` and `coverage_advisory`
  split those entries by whether they block the audit.

When an ADR defines REQs, every REQ *should* be reachable from a `@covers`
annotation (or equivalent BDD `@REQ` tag / doc-proof channel — see GHI #165).
Advisory-severity gaps are legitimate for Lite-lane docs-only OBPIs whose
briefs declare "N/A for TDD" (GHI #268).

---

## Example

```bash
uv run gz adr audit-check ADR-0.3.0

# JSON output with coverage data
uv run gz adr audit-check ADR-0.20.0 --json
```
