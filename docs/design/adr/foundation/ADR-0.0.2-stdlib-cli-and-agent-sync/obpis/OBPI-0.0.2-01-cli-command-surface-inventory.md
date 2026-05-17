---
id: OBPI-0.0.2-01-cli-command-surface-inventory
parent: ADR-0.0.2-stdlib-cli-and-agent-sync
item: 1
lane: Lite
status: Completed
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# OBPI-0.0.2-01 — CLI command surface inventory and compatibility matrix

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.2-stdlib-cli-and-agent-sync/ADR-0.0.2-stdlib-cli-and-agent-sync.md`
- **Checklist Item:** #1 — "Define stdlib-only CLI invariant (`argparse` + stdlib support modules)."

**Status:** Completed — retroactive brief authored 2026-04-15 under GHI #160 Phase 3 Mode F; operator attestation recorded 2026-05-17.

## ALLOWED PATHS

- `src/gzkit/cli/main.py`
- `src/gzkit/cli/parser.py`
- `src/gzkit/cli/parser_artifacts.py`
- `docs/user/manpages/agent-sync-control-surfaces.md`

## Objective

Establish the stdlib-only CLI invariant for gzkit and document the compatibility matrix between legacy and canonical command surfaces.

## Acceptance Criteria

<!--
Backfilled 2026-04-15 under GHI #160 Phase 3 Mode F.
This OBPI did not exist in the obpis/ directory at the time of the audit;
the parent ADR's Feature Checklist row #1 was the only specification.
-->

- [x] REQ-0.0.2-01-01: Given the gzkit CLI runtime, when inspected, then argument parsing uses Python stdlib (`argparse`/`shlex`/`sys.argv`) exclusively for the runtime command path.
- [x] REQ-0.0.2-01-02: Given the gzkit runtime dependency closure, when audited, then no third-party CLI parser framework (Click, Typer, etc.) appears in the production import chain.
- [x] REQ-0.0.2-01-03: Given the legacy command surface, when surveyed, then every existing verb has a documented mapping to its canonical-grammar successor (or an explicit deprecation alias).

### Implementation Summary


- Files governing CLI parser: `src/gzkit/cli/parser.py`, `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/cli/main.py` — all use stdlib `argparse`
- Dependency closure verified via `pyproject.toml` runtime dependencies — no `click`, `typer`, or `cleo`
- Compatibility surface: legacy aliases `gz agent-control-sync` and `gz sync` resolve to the canonical `gz agent sync control-surfaces` verb
- Date authored: 2026-04-15 (retroactive under GHI #160 Phase 3 Mode F)
- Defects noted: none — the contract has held; the absence of this brief from the governance graph was the only defect, which this backfill resolves

### Key Proof


```bash
$ uv run python -c "import gzkit.cli.main as m; print(type(m._build_parser()).__name__)"
ArgumentParser

$ grep -rn "import click\|from click" src/gzkit/ | wc -l
0
```

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — retroactive ratification of long-shipped stdlib-only CLI invariant. Re-verified 2026-05-17 against HEAD 35c5ace: src/gzkit/cli/ has zero click imports (rg -c 'import click|from click' src/gzkit/ → 0); gz --help renders argparse-shaped output across 41 registered verbs; legacy aliases gz agent-control-sync and gz sync resolve to canonical gz agent sync control-surfaces. REQ-0.0.2-01-01 through REQ-0.0.2-01-03 all hold. Brief authored retroactively 2026-04-15 under GHI #160 phase 3 mode f; this attestation closes the ledger gap.
- Date: 2026-05-17
