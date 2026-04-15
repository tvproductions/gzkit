---
id: OBPI-0.0.2-04-runtime-test-click-removal
parent: ADR-0.0.2-stdlib-cli-and-agent-sync
item: 4
lane: Lite
status: Pending
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.0.2-04 — Runtime/test dependency removal for Click

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.2-stdlib-cli-and-agent-sync/ADR-0.0.2-stdlib-cli-and-agent-sync.md`
- **Checklist Item:** #4 — "Remove Click from runtime dependencies and test harness."

**Status:** Pending — retroactive brief authored 2026-04-15 under GHI #160 Phase 3 Mode F. Operator attestation required (Foundation ADR).

## Objective

Eliminate every Click reference from runtime sources, tests, and dependency declarations.

## Acceptance Criteria

- [x] REQ-0.0.2-04-01: Given `pyproject.toml` runtime dependencies, when inspected, then `click` is absent.
- [x] REQ-0.0.2-04-02: Given `src/gzkit/`, when scanned, then no module imports `click` (production code is Click-free).
- [x] REQ-0.0.2-04-03: Given `tests/`, when scanned, then no test file imports `click` or invokes Click-specific test utilities.

### Implementation Summary

- Click removed from runtime + test harness during the original ADR-0.0.2 era
- Date authored: 2026-04-15 (retroactive backfill)
- Defects noted: none

### Key Proof

```bash
$ grep -rn "^import click\|^from click" src/gzkit/ tests/ | wc -l
0

$ grep -c '"click"' pyproject.toml
0
```

## Human Attestation

- Attestor: pending — operator attestation required (Foundation ADR)
- Date: pending
