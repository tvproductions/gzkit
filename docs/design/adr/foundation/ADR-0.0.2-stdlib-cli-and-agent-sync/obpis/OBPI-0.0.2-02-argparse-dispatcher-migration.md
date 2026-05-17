---
id: OBPI-0.0.2-02-argparse-dispatcher-migration
parent: ADR-0.0.2-stdlib-cli-and-agent-sync
item: 2
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.0.2-02 — argparse dispatcher and command binding migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.2-stdlib-cli-and-agent-sync/ADR-0.0.2-stdlib-cli-and-agent-sync.md`
- **Checklist Item:** #2 — "Migrate command parsing/dispatch off Click while preserving command behavior."

**Status:** Completed — retroactive brief authored 2026-04-15 under GHI #160 Phase 3 Mode F; operator attestation recorded 2026-05-17.

## ALLOWED PATHS

- `src/gzkit/cli/main.py`
- `src/gzkit/cli/parser.py`
- `src/gzkit/cli/parser_artifacts.py`

## Objective

Implement an argparse-based command dispatcher that preserves all existing gz verb behavior while removing every dependency on Click decorators.

## Acceptance Criteria

- [x] REQ-0.0.2-02-01: Given the gzkit CLI entrypoint, when invoked, then control flows through `src/gzkit/cli/main.py:_build_parser()` using `argparse.ArgumentParser`.
- [x] REQ-0.0.2-02-02: Given every legacy gz verb, when called via the new dispatcher, then it produces the same observable behavior as before the migration.
- [x] REQ-0.0.2-02-03: Given the dispatcher implementation, when inspected, then it carries no `@click.command`, `@click.option`, or `@click.argument` decorators in the runtime import chain.

### Implementation Summary


- Files: `src/gzkit/cli/main.py`, `src/gzkit/cli/parser.py`, `src/gzkit/cli/parser_artifacts.py`
- Date authored: 2026-04-15 (retroactive backfill)
- Defects noted: none

### Key Proof


```bash
$ uv run gz --help | head -3
usage: gz [-h] {init,prd,...} ...

$ grep -rn "click\." src/gzkit/cli/ | wc -l
0
```

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — retroactive ratification of argparse dispatcher migration. Re-verified 2026-05-17 against HEAD 35c5ace: gz --help shows usage: gz [-h] [--version] [--quiet | --verbose] [--debug] {init,…} signature confirming argparse.ArgumentParser flow through src/gzkit/cli/main.py; rg -c 'click\.' src/gzkit/cli/ → 0 (no Click decorators in runtime import chain); legacy verb behavior preserved across the 41-verb surface. REQ-0.0.2-02-01 through REQ-0.0.2-02-03 all hold. Brief authored retroactively 2026-04-15 under GHI #160 phase 3 mode f; this attestation closes the ledger gap.
- Date: 2026-05-17
