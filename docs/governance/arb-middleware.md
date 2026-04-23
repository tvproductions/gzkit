# ARB Middleware — Agent Self-Reporting Receipts

This document is the deep-dive reference for ARB (Agent Self-Reporting), the
QA middleware layer that wraps real verification steps (lint, type check,
tests, coverage, docs build) and emits structured JSON receipts used as
attestation evidence.

The **binding rules** — the em-dash enrichment pattern, the canonical-invocations
table, lane behavior (Lite warn / Heavy fail-closed), and the worked example —
live in `AGENTS.md` § Attestation. Read that section first; this file expands
the middleware surface the rules depend on.

Consolidation lineage: `.gzkit/rules/attestation-enrichment.md` (retired
2026-04-23, ADR-0.0.20 OBPI-03) → AGENTS.md § Attestation (binding) + this
file (deep-dive).

## ARB Middleware — Core Concept

ARB (Agent Self-Reporting) is a QA middleware layer that wraps real
verification steps (lint, type check, tests, coverage, docs build) and
emits structured JSON receipts. Every claim in the Canonical invocations
table in `AGENTS.md` § Attestation is a thin wrapper over a real tool;
the receipt is the deterministic evidence artifact.

ARB intercepts QA command execution and records:

- **Execution metadata** (timestamp, duration, environment)
- **Input/output** (command, arguments, exit code, stderr/stdout)
- **Structured findings** (linting violations, type errors, test failures)
- **Receipt artifacts** (JSON schema-validated, persistent)

This lets agents and humans:

1. Validate QA step outcomes programmatically
2. Aggregate recurring patterns across runs
3. File issues with deterministic evidence
4. Audit compliance and enforcement

## Available commands

The canonical invocations (binding) live in `AGENTS.md` § Attestation. The
commands below are the practical surface for producing and consuming receipts.

### Wrap a QA tool

```bash
uv run gz arb ruff
uv run gz arb ruff --fix
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb typecheck
uv run gz arb coverage run -m unittest discover -s tests -t .
```

### Validate and analyze receipts

```bash
uv run gz arb validate
uv run gz arb validate --limit 50
uv run gz arb advise
uv run gz arb advise --limit 10
```

### Extract recurring anti-patterns

```bash
uv run gz arb patterns
uv run gz arb patterns --compact
uv run gz arb patterns --json
```

## Receipt schema and storage

- **Lint receipt schema:** `data/schemas/arb_lint_receipt.schema.json`
  (`$id: gzkit.arb.lint_receipt.schema.json`)
- **Step receipt schema:** `data/schemas/arb_step_receipt.schema.json`
  (`$id: gzkit.arb.step_receipt.schema.json`)
- **Storage:** `artifacts/receipts/` (configurable via `arb.receipts_root` in `.gzkit.json`)

## Exit codes

- **0:** Command succeeded; receipt created
- **1:** Command failed; receipt created with error status
- **2:** ARB internal error

## Rationale

### Why receipts, not narrative

Narrative recall is post-hoc reconstruction: the reporting pathway and the
execution pathway are structurally separate (Lindsey et al. 2025 — the
math-explanation pathway and the math-execution pathway are distinct circuits;
a model can produce a plausible explanation of reasoning it did not actually
perform). The only faithful record of a QA step is the wrapped-command receipt.

### Why canonical commands

GHI #199 traces the class of failure where an ARB receipt reported exit 0
against `ty check .` while the governance gate (`gz typecheck` → `ty check src`)
reported exit 1. Parallel approximations (different scope, different target
tree, different flags) drift from the gate. `gz arb typecheck` (GHI #199)
wraps `uv run ty check src` — the same command `gz typecheck` and
`gz closeout` invoke.

### TDD RED evidence is not ARB-shaped (GHI #157)

ARB step receipts encode `exit_status=0` as success and `exit_status=1` as
failure. A TDD RED test is the inverse — a first-run failure is the *correct*
outcome. Until the dedicated RED/GREEN receipt stream lands (tracked under
`ADR-pool.tdd-receipt-stream`), Gate 2 TDD claims cite ARB receipts only for
the GREEN side (`arb-step-unittest-*`); the RED side is recorded as
per-increment observed-output pasted into the commit body or OBPI
verification section, under the same observed-evidence discipline that
governs routing-skill output claims.
