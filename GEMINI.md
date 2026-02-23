# GEMINI.md

This file provides context and instructions for Gemini CLI when working with `gzkit`.

## Project Overview

`gzkit` (GovZero Kit) is cognitive infrastructure for extended human-AI collaboration. It implements a **development covenant**—a protocol that preserves human intent across agent context boundaries through structured governance, explicit constraints, and verification loops.

The project itself is governed by `gzkit`.

## Technical Stack

- **Language**: Python 3.13+
- **Package Manager**: `uv`
- **Linting/Formatting**: `ruff`
- **Type Checking**: `ty` (custom wrapper, typically runs `pyright` or `mypy`)
- **Testing**: `unittest`
- **CLI Framework**: Built-in `argparse` with `rich` for terminal UI

## Core Concepts & Invariants

- **Five Gates**: Work flows through five gates:
  1. **ADR**: Record intent and tradeoffs (Gate 1).
  2. **TDD**: Automated tests pass (Gate 2).
  3. **Docs**: Documentation reflects reality (Gate 3).
  4. **BDD**: External contracts verified (Gate 4).
  5. **Human**: Human attestation of completion (Gate 5).
- **Lanes**:
  - `lite`: Gates 1 & 2 required.
  - `heavy`: All 5 gates required.
- **Artifacts**: PRDs, Constitutions, ADRs (Architectural Decision Records), and OBPIs (One Brief Per Item).
- **Ledger**: `.gzkit/ledger.jsonl` is the immutable record of all governance events.
- **Prime Directive**: You own the work completely. Do not defer or leave things incomplete. Fix broken things immediately, even if pre-existing.

## Key Commands

### Development
```bash
uv sync                              # Hydrate environment
uv run -m gzkit --help            # CLI entry point (alias 'gz' if installed)
uv run -m unittest discover tests    # Run unit tests
gz check                             # Run all quality checks (lint, format, test, typecheck)
gz lint                              # Run Ruff + PyMarkdown
gz format                            # Auto-format code
gz typecheck                         # Run static type checks
```

### Governance
```bash
gz status                            # Show ADR and gate status (tabular)
gz state                             # Query ledger state and artifact graph
gz plan "Feature Name"               # Create a new ADR
gz specify --parent ADR-ID ...      # Create a new OBPI brief
gz agent sync control-surfaces       # Synchronize agent context files (AGENTS.md, etc.)
gz attest                            # Record human attestation (Gate 5)
```

## Directory Structure

- `src/gzkit/`: Main source code.
  - `cli.py`: CLI entry point and command implementations.
  - `ledger.py`: Ledger management and event definitions.
  - `quality.py`: Logic for linting, testing, and type checking.
  - `sync.py`: Logic for synchronizing control surfaces and skills.
- `tests/`: Unit and integration tests.
- `docs/`: Project documentation, including the design/ governance surfaces.
- `.gzkit/`: Governance state (ledger, manifest, skills).
- `.agents/`, `.claude/`, `.github/`: Agent-specific skill mirrors and configurations.

## Development Workflow

1. **Check State**: Run `gz status` to see what's pending.
2. **Plan**: For any significant change, ensure an ADR exists (`gz plan`).
3. **Implement**: Write code and tests (`unittest`).
4. **Verify**: Run `gz check` to ensure all quality gates pass.
5. **Sync**: If you modified governance artifacts or skills, run `gz agent sync control-surfaces`.
6. **Attest**: Request human attestation for completed work items via `gz attest`.

## Authoritative Guidance

- **AGENTS.md**: The authoritative governance contract. **Always read this first.**
- **CLAUDE.md**: Provides specific operational guidance for AI agents.
- **OBPI Acceptance Protocol**: In `heavy` or `foundation` lanes, never mark a brief as `Completed` without explicit human attestation.
