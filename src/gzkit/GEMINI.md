# GEMINI.md (src/gzkit)

This directory contains the core implementation of the `gzkit` CLI.

## Architectural Guidelines

- **Commands:** All new CLI commands must be implemented in the `commands/` directory. Do not add new command logic directly to `cli.py`.
- **Ledger:** All state mutations must be handled by appending events to the ledger. Do not write side-effects directly to disk without a corresponding ledger event (unless specifically bypassing ledger for purely external operations like `mkdocs` or `git`).
- **Dependencies:** Imports between core modules (like `ledger.py`, `sync.py`, `quality.py`) should be minimized to avoid circular dependencies. Use `config.py` for shared data structures.
