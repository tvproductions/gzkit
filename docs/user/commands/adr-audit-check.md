# gz adr audit-check

Verify linked OBPIs for one ADR are completed and include implementation evidence.

---

## Usage

```bash
gz adr audit-check <ADR-ID> [--json]
```

---

## What It Checks

- ADR-to-OBPI linkage from ledger and artifact metadata
- OBPI completion markers (`status: Completed` and/or `**Brief Status:** Completed`)
- Presence of non-placeholder implementation summary evidence
- Requirement coverage from `@covers` test annotations (advisory by default;
  severity is fail-open so Lite-lane docs-only OBPIs do not block the audit)

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
