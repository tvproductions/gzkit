---
id: OBPI-0.0.2-04-runtime-test-click-removal
parent: ADR-0.0.2-stdlib-cli-and-agent-sync
item: 4
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.0.2-04 — Runtime/test dependency removal for Click

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.2-stdlib-cli-and-agent-sync/ADR-0.0.2-stdlib-cli-and-agent-sync.md`
- **Checklist Item:** #4 — "Remove Click from runtime dependencies and test harness."

**Status:** Completed — retroactive brief authored 2026-04-15 under GHI #160 Phase 3 Mode F; operator attestation recorded 2026-05-17.

## ALLOWED PATHS

- `src/gzkit/cli/main.py`
- `src/gzkit/cli/parser.py`
- `src/gzkit/cli/parser_artifacts.py`

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

- Attestor: `g0`
- Attestation: attest completed — retroactive ratification of Click removal from runtime and test harness. Re-verified 2026-05-17 against HEAD 35c5ace: rg -c '^import click|^from click' src/gzkit/ tests/ → 0; grep -c '"click"' pyproject.toml → 0; the dependency closure is Click-free across production code, test harness, and runtime dependency declarations. REQ-0.0.2-04-01 through REQ-0.0.2-04-03 all hold. Brief authored retroactively 2026-04-15 under GHI #160 phase 3 mode f; this attestation closes the ledger gap.
- Date: 2026-05-17
