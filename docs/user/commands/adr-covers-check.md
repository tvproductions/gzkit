# gz adr covers-check

Verify `@covers(...)` traceability between an ADR package and tests.

---

## Usage

```bash
gz adr covers-check <ADR-ID> [--json]
```

---

## Runtime Behavior

- Resolves ADR ID through ledger rename chains.
- Collects linked OBPI IDs for the ADR from ledger/file state.
- Scans `tests/**/*.py` for annotations matching:
  - `@covers("ADR-...")`
  - `@covers("OBPI-...")`
- `@covers("REQ-<semver>-<obpi_item>-<criterion_index>")`
- Parses each linked OBPI `## Acceptance Criteria` checkbox and extracts required `REQ-*` IDs.
- Fails if an acceptance criterion checkbox has no `REQ-*` ID.
- Fails if the ADR ID, linked OBPI ID, or extracted REQ ID is missing from `@covers` targets.
- Reports unmatched `@covers` targets that are not linked to the ADR.

This command is a "tests for spec" primitive:
- spec target = ADR/OBPI/REQ identifier
- test proof = `@covers("<target>")`

---

## Examples

```bash
uv run gz adr covers-check ADR-0.3.0
uv run gz adr covers-check ADR-0.3.0 --json
```
