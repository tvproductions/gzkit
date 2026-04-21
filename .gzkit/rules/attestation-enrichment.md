---
id: attestation-enrichment
paths:
  - "**"
description: Pass user attestation and commit words verbatim; append concrete session-grounded characterization. Canonical home for ARB middleware and receipt-ID discipline.
---

# Attestation, Commit Enrichment, and ARB Receipts

**Version:** 2.0
**Status:** Active
**Last reviewed:** 2026-04-21 (merged arb.md lane matrix in to close the duplicate-matrix drift Pass A row 2 surfaced; single canonical home for ARB lane behavior + canonical invocations + receipt-ID discipline).

## Pattern (binding)

```
<user's verbatim words> — <concrete characterization grounded in session evidence>
```

The user's words retain provenance; the em-dash enrichment supplies the weight.

## Canonical invocations (binding)

| Claim category | Canonical invocation | Receipt name prefix |
|----------------|----------------------|---------------------|
| Lint clean | `uv run gz arb ruff` | `arb-ruff-` |
| Type check clean | `uv run gz arb typecheck` | `arb-step-typecheck-` |
| Tests pass | `uv run gz arb step --name unittest -- uv run -m unittest -q` | `arb-step-unittest-` |
| Coverage floor | `uv run gz arb coverage run -m unittest discover -s tests -t .` | `arb-step-coverage-` |
| Docs build clean | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` | `arb-step-mkdocs-` |

Locked by `CANONICAL_STEP_COMMANDS` in `src/gzkit/arb/validator.py`; `gz arb validate` flags drift as non-canonical provenance. Extend (don't shrink) the table.

## Applies to

- `uv run gz obpi complete --attestation-text ...`
- `uv run gz adr emit-receipt ... --attestor ...`
- Any `gz` CLI accepting an attestation string
- `git commit -m "..."` messages (including HEREDOC form)

## Lane behavior

- **Lite lane:** missing receipt IDs produce a warning; attestation records but is flagged narrative-only.
- **Heavy lane:** missing receipt IDs are fail-closed; re-run under ARB and re-cite.

If no receipts exist, run the relevant ARB-wrapped commands first, then draft the attestation citing the fresh receipt IDs. Narrative substitutes are not acceptable.

## Enrichment content

Reference concrete session facts:

- Decisions recorded (Absorb/Confirm/Exclude, chosen approach, rejected alternatives)
- Concrete evidence: test counts, coverage deltas, line counts, files changed
- File references with paths and line numbers
- Rationale citing named dimensions, not vague adjectives

Receipt IDs appear inline, e.g. `(lint: receipt arb-2026-04-14T12-34-56-ruff)`. The citing agent must verify the receipt exists and its status matches the claim — fabricating a receipt ID is the same failure as fabricating the claim.

## Anti-patterns

- Passing only the user's brief token without enrichment — loses signal
- Replacing the user's words with an agent-generated sentence — loses provenance
- Adding enrichment not grounded in concrete session evidence — fabrication
- Using vague adjectives ("good", "clean", "comprehensive") without naming the facts
- Enriching with information from other sessions or unrelated work
- Authoring `arb-step-*` receipts with `exit_status=1` as "RED receipts" — pollutes the ARB corpus (see Rationale § TDD RED)

## Example

User says: `attest completed`

Agent passes to `--attestation-text`:

```
attest completed — Confirm decision: gzkit cli_audit + doc_coverage surface
architecturally superior (AST vs parser._actions private API, 5-surface
manifest-driven coverage, 76 vs 1 tests, frozen Pydantic vs dict[str,Any]);
no absorption of the external reference cli_audit module warranted.
Receipts: lint arb-2026-04-14T12-34-56-ruff; types arb-2026-04-14T12-35-02-ty;
tests arb-2026-04-14T12-36-18-unittest; coverage arb-2026-04-14T12-37-44-coverage.
```

## ARB Middleware — Core Concept

ARB (Agent Self-Reporting) is a QA middleware layer that wraps real verification steps (lint, type check, tests, etc.) and emits structured JSON receipts. Every claim in the Canonical invocations table above is a thin wrapper over a real tool; the receipt is the deterministic evidence artifact.

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

The invocations in § Canonical invocations are the binding set. The commands below are the practical surface for producing and consuming receipts.

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

- **Lint receipt schema:** `data/schemas/arb_lint_receipt.schema.json` (`$id: gzkit.arb.lint_receipt.schema.json`)
- **Step receipt schema:** `data/schemas/arb_step_receipt.schema.json` (`$id: gzkit.arb.step_receipt.schema.json`)
- **Storage:** `artifacts/receipts/` (configurable via `arb.receipts_root` in `.gzkit.json`)

## Exit codes

- **0:** Command succeeded; receipt created
- **1:** Command failed; receipt created with error status
- **2:** ARB internal error

## Rationale

### Why receipts, not narrative

Narrative recall is post-hoc reconstruction: the reporting pathway and the execution pathway are structurally separate (Lindsey et al. 2025 — the math-explanation pathway and the math-execution pathway are distinct circuits; a model can produce a plausible explanation of reasoning it did not actually perform). The only faithful record of a QA step is the wrapped-command receipt.

### Why canonical commands

GHI #199 traces the class of failure where an ARB receipt reported exit 0 against `ty check .` while the governance gate (`gz typecheck` → `ty check src`) reported exit 1. Parallel approximations (different scope, different target tree, different flags) drift from the gate. `gz arb typecheck` (GHI #199) wraps `uv run ty check src` — the same command `gz typecheck` and `gz closeout` invoke.

### TDD RED evidence is not ARB-shaped (GHI #157)

ARB step receipts encode `exit_status=0` as success and `exit_status=1` as failure. A TDD RED test is the inverse — a first-run failure is the *correct* outcome. Until the dedicated RED/GREEN receipt stream lands (tracked under `ADR-pool.tdd-receipt-stream`), Gate 2 TDD claims cite ARB receipts only for the GREEN side (`arb-step-unittest-*`); the RED side is recorded as per-increment observed-output pasted into the commit body or OBPI verification section, under the same observed-evidence discipline as `.gzkit/rules/tool-skill-runbook-alignment.md`.
