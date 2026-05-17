---
id: OBPI-0.0.2-03-canonical-sync-grammar
parent: ADR-0.0.2-stdlib-cli-and-agent-sync
item: 3
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.0.2-03 — Canonical sync grammar and alias deprecation behavior

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.2-stdlib-cli-and-agent-sync/ADR-0.0.2-stdlib-cli-and-agent-sync.md`
- **Checklist Item:** #3 — "Establish canonical command grammar: `gz agent sync control-surfaces`. Provide compatibility aliases with explicit deprecation messaging."

**Status:** Completed — retroactive brief authored 2026-04-15 under GHI #160 Phase 3 Mode F; operator attestation recorded 2026-05-17.

## ALLOWED PATHS

- `src/gzkit/cli/parser_artifacts.py`
- `src/gzkit/commands/sync.py`
- `docs/user/manpages/agent-sync-control-surfaces.md`

## Objective

Make `gz agent sync control-surfaces` the canonical grammar for control-surface synchronization and provide deprecation-safe legacy aliases.

## Acceptance Criteria

- [x] REQ-0.0.2-03-01: Given the gzkit CLI parser, when inspected, then `gz agent sync control-surfaces` is registered as a canonical multi-depth verb.
- [x] REQ-0.0.2-03-02: Given the legacy alias `gz agent-control-sync`, when invoked, then it preserves behavior and emits deprecation guidance pointing operators to the canonical verb.
- [x] REQ-0.0.2-03-03: Given the legacy alias `gz sync`, when invoked, then it preserves behavior and emits deprecation guidance pointing operators to the canonical verb.

### Implementation Summary


- Canonical verb registered in `src/gzkit/cli/parser_artifacts.py`
- Compatibility aliases preserved during migration
- Date authored: 2026-04-15 (retroactive backfill)
- Defects noted: none

### Key Proof


```bash
$ uv run gz agent sync control-surfaces --help | head -1
usage: gz agent sync control-surfaces [-h]
```

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — retroactive ratification of canonical sync grammar. Re-verified 2026-05-17 against HEAD 35c5ace: gz agent sync control-surfaces --help resolves to argparse-bound multi-depth verb (usage: gz agent sync control-surfaces [-h] [--dry-run] [--quiet | --verbose]); legacy aliases gz agent-control-sync and gz sync remain operational with deprecation guidance pointing to the canonical verb. REQ-0.0.2-03-01 through REQ-0.0.2-03-03 all hold. Brief authored retroactively 2026-04-15 under GHI #160 phase 3 mode f; this attestation closes the ledger gap.
- Date: 2026-05-17
