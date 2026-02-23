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

Implementation-summary evidence is parsed from inline markdown bullets in
`### Implementation Summary`, for example:

- `- Files created/modified: src/gzkit/cli.py, tests/test_cli.py`
- `- Tests added: tests/test_cli.py`
- `- Date completed: 2026-02-23`

Nested bullets or empty placeholder values can cause evidence to be treated as missing.

Returns explicit missing-proof findings and exits non-zero on failure.

---

## Example

```bash
uv run gz adr audit-check ADR-0.3.0
```
