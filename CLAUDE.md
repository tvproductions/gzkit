# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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
- **ty** — Type checking (config in ty.toml)
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
uv run -m unittest discover tests    # Run all tests
uv run -m unittest tests.test_config # Run single test module
uv run -m unittest tests.test_config.TestGzkitConfig.test_load__valid_config  # Run single test
```

## Pre-commit Hooks

Pre-commit runs automatically on commit: ruff, ty, unittest, xenon (complexity C/C/C), interrogate (docstrings), gitleaks (secrets), unittest-only enforcement.

## Architecture

```text
src/gzkit/
├── cli.py              # Click-based CLI entry point
├── config.py           # .gzkit.json parsing and GzkitConfig dataclass
├── hooks/              # Git and agent hook infrastructure
│   ├── guards.py       # Policy enforcement (unittest-only)
│   ├── claude.py       # Claude Code hook generation
│   ├── copilot.py      # GitHub Copilot hook generation
│   └── core.py         # Shared hook utilities, ledger recording
├── schemas/            # JSON schemas for artifact validation
├── templates/          # Markdown templates for scaffolding
├── interview.py        # Interactive prompts for artifact creation
├── ledger.py           # Append-only governance event log
├── quality.py          # Code quality checks
├── skills.py           # Skill file management
├── sync.py             # Control surface synchronization
└── validate.py         # Schema validation utilities
```

## The Three Concerns

| Concern | Agent-facing? | Examples |
| ------- | ------------- | -------- |
| **Specification** | Yes | Canon validation, constraint checking, acceptance criteria |
| **Methodology** | Shared | Phase transitions, gate sequencing, workflow state |
| **Governance** | No (human) | Attestation recording, audit trails, authority checks |

Agent-facing code: **constraint-forward** (explicit rules, declarative intent, verification loops).

Human-facing code: **ceremony-aware** (clear prompts, attestation recording, audit formatting).

## Coding Conventions

- Ruff defaults: 4-space indent, 100-char lines, double quotes
- `snake_case` for modules/functions, `PascalCase` for classes
- Type annotations on all public functions
- Dataclasses for structured data
- No magic—explicit is better than implicit

## Commit Style

Conventional Commits: `feat(gates): add ADR validation` (72 char wrap)

Do NOT add Co-Authored-By trailers.

## Forbidden Practices

These are treated as dirty words—never use them:

- `pytest` — use unittest only
- `--no-verify` — fix issues, don't bypass pre-commit
- `--force` push — protect shared history

If something is broken, fix it. Don't bypass or ignore problems.

## Key Invariants

1. **Markdown-primary**: All governance artifacts are Markdown; structured data (YAML/JSON) only where necessary
2. **Human attestation is final**: Gate 5 cannot be automated or bypassed
3. **Determinism**: Same inputs → same outputs for all verification
4. **Explainability**: Every gate result must trace to specific evidence

## Testing Conventions

- Test files mirror source: `tests/test_config.py` for `src/gzkit/config.py`
- Test method naming: `test_<behavior>__<expectation>`
- Use unittest only—no pytest
- Mock external dependencies; no network calls in tests
