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
- Requirement coverage from `@covers` test annotations (advisory)

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
- **Uncovered REQs**: Listed as advisory findings — they appear in output
  but do not affect the pass/fail status.
- **JSON output**: The `coverage` key contains `total_reqs`, `covered_reqs`,
  `uncovered_reqs`, `coverage_percent`, `by_obpi` array, and `uncovered` list.
  The `advisory_findings` key lists uncovered REQs separately from blocking findings.

Coverage is informational. Uncovered REQs are flagged for auditor awareness
but never block the audit gate.

---

## Example

```bash
uv run gz adr audit-check ADR-0.3.0

# JSON output with coverage data
uv run gz adr audit-check ADR-0.20.0 --json
```
