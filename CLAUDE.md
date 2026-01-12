# CLAUDE.md

This file provides guidance to Claude Code when working with the gzkit codebase.

## Project Overview

gzkit is a Development Covenant for Human-AI Collaboration—cognitive infrastructure that preserves human intent across agent context boundaries, gives agents constraints to reason against, creates verification loops both parties trust, and reserves final judgment for humans.

### What gzkit IS

- A Python CLI for managing development covenants
- Executable documentation: Markdown artifacts validated by code
- A bridge between specification (agent-native) and governance (human-native)

### What gzkit is NOT

- An AI/ML framework
- A replacement for human judgment
- Automation for automation's sake

## Tech Stack (Strict)

- **uv** — Package/environment management
- **ruff** — Linting and formatting
- **ty** — Type checking (strict: error-on-warning)
- **unittest** — Testing (NOT pytest)

**NEVER** use pip, poetry, mypy, black, isort, pyright, pytest, or any other tools.

**Python version**: 3.13.x only.

## Build Commands

```bash
uv sync                              # Hydrate environment
uv sync --extra docs                 # Include docs dependencies
uv run -m gzkit --help               # CLI entry point
uvx ruff check src tests             # Lint
uvx ruff format --check .            # Format check
uvx ty check src                     # Type check
uv run -m unittest discover tests    # Run tests
```

## Documentation

```bash
uv run mkdocs serve                  # Local dev server at localhost:8000
uv run mkdocs build                  # Build static site to site/
```

Site hosted at https://gzkit.org (MkDocs Material theme).

## Architecture

```
src/gzkit/
├── __init__.py
├── cli.py              # Click-based CLI entry point
├── config.py           # .gzkit.yaml parsing
├── gates/              # Gate implementations
│   ├── adr.py          # Gate 1: ADR management
│   ├── tdd.py          # Gate 2: Test verification
│   ├── docs.py         # Gate 3: Documentation checks
│   ├── bdd.py          # Gate 4: Behavior verification
│   └── human.py        # Gate 5: Attestation tracking
├── phases/             # Spec-kit phase model
│   ├── constitute.py   # Define constitutions/canon
│   ├── specify.py      # Create specs/briefs
│   ├── plan.py         # ADR and linkage
│   ├── implement.py    # Verification orchestration
│   └── analyze.py      # Audit and attestation
└── templates/          # Markdown templates for scaffolding
```

## Coding Conventions

- Ruff defaults: 4-space indent, 100-char lines, double quotes
- `snake_case` for modules/functions, `PascalCase` for classes
- Type annotations on all public functions
- Dataclasses or Pydantic for structured data
- No magic—explicit is better than implicit

## The Three Concerns

When implementing features, consider which concern is primary:

| Concern | Agent-facing? | Examples |
|---------|---------------|----------|
| **Specification** | Yes | Canon validation, constraint checking, acceptance criteria |
| **Methodology** | Shared | Phase transitions, gate sequencing, workflow state |
| **Governance** | No (human) | Attestation recording, audit trails, authority checks |

Agent-facing code should be **constraint-forward**: explicit rules, declarative intent, verification loops.

Human-facing code should be **ceremony-aware**: clear prompts, attestation recording, audit formatting.

## Commit Style

Conventional Commits: `feat(gates): add ADR validation` (72 char wrap)

Do NOT add Co-Authored-By trailers.

## Key Invariants

1. **Markdown-primary**: All governance artifacts are Markdown; structured data (YAML/JSON) only where necessary
2. **Human attestation is final**: Gate 5 cannot be automated or bypassed
3. **Determinism**: Same inputs → same outputs for all verification
4. **Explainability**: Every gate result must trace to specific evidence

## Testing Conventions

- Test files mirror source: `tests/gates/test_adr.py` for `src/gzkit/gates/adr.py`
- Test method naming: `test_<behavior>__<expectation>`
- Use unittest only—no pytest
- Mock external dependencies; no network calls in tests
