# gz-cookiecutter Python Stack

Status: configuration directive

This note captures the common and preferred Python packages and tools for a
future `gz-cookiecutter` project baseline. It is not a skill, ADR, or automatic
dependency grant. It records the stack gzkit should reach for when bootstrapping
Python-focused projects, while preserving the stdlib-first rule: third-party
runtime dependencies still need a concrete project need and explicit rationale.

## Purpose

`gz-cookiecutter` is the preferred Python project blueprint for gzkit-governed
repositories while gzkit is focused on Python. The stack aims for:

- fast local execution;
- strict static and runtime type discipline;
- native environment isolation;
- dependency restraint;
- clear architecture boundaries;
- enforceable quality gates;
- production-grade data and AI application paths when those domains are needed.

## Environment Management and Test Core

### uv

Role: next-generation package and project manager.

`uv` is the default project, dependency, lockfile, and virtual environment tool.
It replaces the usual `pip`, `pip-tools`, `venv`, and `virtualenv` workflow with
a fast, reproducible, Rust-powered project surface.

### python -m unittest

Role: native standard-library testing harness.

`unittest` is the default test engine. It keeps the test harness dependency-free,
stable across Python upgrades, and aligned with gzkit's stdlib-first doctrine.

## Quality Fortress

### Ruff

Role: linter and formatter.

`ruff` is the default style, import-order, lint, modernization, and formatting
gate. It replaces the common Black, Flake8, isort, and pyupgrade stack.

### ty

Role: static type checker.

`ty` is the preferred static typing gate for Python projects that follow the
Astral toolchain. It keeps type checking close to the same low-friction workflow
as `uv` and `ruff`.

### Xenon

Role: cyclomatic complexity gatekeeper.

`xenon` is the hard complexity gate, backed by Radon metrics. It blocks deeply
nested or over-complex functions before they become normalized in the codebase.

### Vulture

Role: AST dead code hunter.

`vulture` scans for unused variables, functions, methods, attributes, classes,
and modules. It is the preferred dead-code discovery tool, with findings routed
through review instead of blindly deleted.

### import-linter or Tach

Role: architectural dependency contract enforcer.

Use `import-linter` or Tach when a project needs explicit module boundary rules.
The intended use is to make architectural imports fail the build when a lower
layer reaches into a higher layer or when circular dependency pressure appears.

### cohesion

Role: class structural cohesion auditor.

`cohesion` measures Lack of Cohesion of Methods (LCOM). It is preferred for
class-heavy codebases where "god object" drift is a realistic risk.

### Bandit and Semgrep

Role: security scanning and semantic pattern enforcement.

`bandit` is the Python AST security scanner. `semgrep` is the semantic pattern
matcher for team-specific or project-specific bans that lint rules cannot
express cleanly.

### Coverage.py and Mutmut

Role: execution coverage and mutation testing.

`coverage.py` measures which lines and branches the `unittest` suite executes.
`mutmut` checks whether assertions are strong enough by mutating source behavior
and verifying that tests fail for meaningful behavioral changes.

## Type-Safe Web Architecture and AI Orchestration

These are preferred runtime packages when the project actually needs web API or
AI orchestration surfaces. They are not part of the minimum project scaffold.

### FastAPI

Role: high-performance async-first web framework.

FastAPI is the preferred web framework when a Python project needs typed HTTP
APIs, request validation, response serialization, and OpenAPI generation.

### Pydantic

Role: structural data parsing and runtime validation engine.

Pydantic is the preferred runtime validation engine at trust boundaries. It
turns untrusted inputs into typed objects with explicit validation errors and is
already a named departure from strict stdlib-only modeling in gzkit doctrine.

### Pydantic AI

Role: model-agnostic LLM orchestration.

Pydantic AI is the preferred candidate when a project needs schema-governed LLM
tool calls, agent inputs, and structured outputs. It should be chosen for typed
LLM workflows, not for casual prompt wrappers.

## High-Performance Data Engines

These are preferred runtime packages when the project actually needs analytical,
forecasting, or high-volume data processing surfaces.

### Polars

Role: multi-threaded DataFrame engine.

Polars is the preferred DataFrame engine for large, parallel, memory-conscious
data workflows. Its Apache Arrow foundation and lazy optimizer make it the
default choice over single-core DataFrame workflows when tabular performance
matters.

### Nixtla Ecosystem

Role: time-series forecasting and anomaly detection.

StatsForecast, NeuralForecast, and TimeGPT are the preferred time-series stack
when the project needs production forecasting, anomaly detection, or a path from
fast statistical models to deeper forecasting systems.

## Workflow and Pipeline Orchestration

These are preferred runtime packages when the project needs scheduled jobs,
task graphs, retries, observability, or operational workflow control beyond a
single command invocation.

### Prefect

Role: Python-native workflow orchestration.

Prefect is the preferred orchestrator when a Python project needs durable flows,
task-level retries, scheduling, state visibility, and operational control over
data or application workflows. It belongs in projects with real orchestration
needs, not in the minimum scaffold.

## Pipeline Execution Gauntlet

The target local and CI chain is linear: a failure at any blocking step stops the
pipeline.

```text
uv sync
uv run ruff format --check .
uv run ruff check .
uv run ty check
uv run python -m unittest -q
uv run coverage run -m unittest discover -s tests -t .
uv run coverage report
uv run xenon --max-absolute B --max-modules A --max-average A src
uv run vulture src tests
uv run lint-imports
uv run cohesion --below 70 src
uv run bandit -r src
uv run semgrep scan --config auto
uv run mutmut run
```

Mutation testing is expensive enough that a project may choose to run `mutmut`
on a scheduled or release gate first, then promote it to every-change blocking
once runtime cost is known.

## Scaffold Tiers

### Minimum Python scaffold

- `uv`
- `python -m unittest`
- `ruff`
- `ty`
- `coverage.py`

### Quality expansion

- `xenon`
- `vulture`
- `import-linter` or Tach
- `cohesion`
- `bandit`
- `semgrep`
- `mutmut`

### Domain expansion

- FastAPI for typed HTTP APIs
- Pydantic for trust-boundary validation
- Pydantic AI for typed LLM orchestration
- Prefect for scheduled flows and operational workflow orchestration
- Polars for high-performance tabular data
- Nixtla ecosystem for time-series systems

## Non-Goals

- This is not a universal Python dependency set.
- This is not a replacement for ADR-backed dependency rationale.
- This is not a generated skill surface.
- This does not imply every gzkit project needs web, AI, data, or forecasting
  packages.
- This does not relax stdlib-first defaults for capabilities Python already
  supplies directly.
