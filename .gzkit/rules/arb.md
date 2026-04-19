---
id: arb
paths:
  - "**/*"
description: ARB (Agent Self-Reporting) middleware QA workflow
---

# ARB (Agent Self-Reporting) Middleware

**Version:** 1.3
**Status:** Active
**Last reviewed:** 2026-04-19 (reframe usage matrix keyed on attestation context; resolve scope contradiction with attestation-enrichment.md; GHI #229)

ARB is a QA middleware layer that wraps real verification steps (lint, type check, tests, etc.) and emits structured JSON receipts for deterministic validation and governance auditing.

---

## Core Concept

ARB intercepts QA command execution and records:

- **Execution metadata** (timestamp, duration, environment)
- **Input/output** (command, arguments, exit code, stderr/stdout)
- **Structured findings** (linting violations, type errors, test failures)
- **Receipt artifacts** (JSON schema-validated, persistent)

This allows agents and humans to:

1. Validate QA step outcomes programmatically
2. Aggregate recurring patterns across runs
3. File issues with deterministic evidence
4. Audit compliance and enforcement

---

## When to Use ARB

ARB usage is keyed on **attestation context**, not agent preference. The matrix
below is binding; the "optional" / "debug-only" framing of earlier drafts is
superseded.

| Context | ARB requirement |
|---|---|
| Heavy-lane attestation (ADR closeout, Heavy-lane OBPI completion, release ceremony) | **Mandatory.** Missing receipt IDs are fail-closed per `.gzkit/rules/attestation-enrichment.md` § Lane behavior — re-run under ARB and re-cite before attesting. |
| Lite-lane attestation (Lite OBPI completion, direct-fix commit body) | **Warned.** Missing receipt IDs record as narrative-only; prefer receipts when a QA claim appears in the attestation text. |
| Filing a defect GHI with QA evidence (lint violation, type error, test failure) | **Mandatory.** Use a receipt ID as the deterministic reference. |
| Debugging a failing QA step for deterministic replay | **Recommended.** The receipt is the artifact the operator or reviewer compares against. |
| Auditing QA compliance across an ADR or release cycle | **Mandatory.** `gz arb validate` / `gz arb patterns` read receipts, not narrative. |
| Aggregating recurring advice from recent lint/test/coverage runs | **Recommended.** |
| One-off interactive command with no attestation downstream | **Optional.** Use the tool directly; ARB adds ~5-10% overhead and receipts only help when consumed. |

> **Canonical invocations are locked by the table in
> `.gzkit/rules/attestation-enrichment.md` § Canonical invocations.** When this
> file's examples drift, the canonical table wins and this file is the defect.

---

## Available Commands

> Canonical QA invocations (lint, typecheck, tests, coverage, docs) are locked
> by the table in `.gzkit/rules/attestation-enrichment.md` (§ Receipt-ID
> Requirement). The examples below must stay aligned with that table — if they
> drift, the canonical table wins and this file is the defect.

### Wrap a QA Tool (Generic)

```bash
uv run gz arb ruff
uv run gz arb ruff --fix
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb typecheck
uv run gz arb coverage run -m unittest discover -s tests -t .
```

### Validate and Analyze Receipts

```bash
uv run gz arb validate
uv run gz arb validate --limit 50
uv run gz arb advise
uv run gz arb advise --limit 10
```

### Extract Recurring Anti-Patterns

```bash
uv run gz arb patterns
uv run gz arb patterns --compact
uv run gz arb patterns --json
```

---

## Receipt Schema and Storage

- **Lint receipt schema:** `data/schemas/arb_lint_receipt.schema.json` (`$id: gzkit.arb.lint_receipt.schema.json`)
- **Step receipt schema:** `data/schemas/arb_step_receipt.schema.json` (`$id: gzkit.arb.step_receipt.schema.json`)
- **Storage:** `artifacts/receipts/` (configurable via `arb.receipts_root` in `.gzkit.json`)

---

## Exit Codes

- **0:** Command succeeded; receipt created
- **1:** Command failed; receipt created with error status
- **2:** ARB internal error
