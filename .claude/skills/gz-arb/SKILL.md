---
name: gz-arb
persona: main-session
description: Wrap QA commands in ARB receipts for attestation evidence. Use when producing Heavy-lane attestation evidence, diagnosing recurring lint patterns, or auditing QA compliance via receipts.
category: agent-operations
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-04-18
model: haiku
gz_command: arb advise
metadata:
  skill-version: "1.0.2"
revived_on: "2026-04-14"
revived_under: OBPI-0.25.0-33
revival_note: "ARB surface absorbed from airlineops/opsdev/arb under OBPI-0.25.0-33. The earlier retirement (2026-04-03, 'consolidated into gz-check') was itself drift — gz check never implemented ARB receipt emission, so the rule contract in .gzkit/rules/arb.md was referencing a nonexistent surface. Revival restores parity with the rule."
---

# gz arb

## Overview

Agent Self-Reporting middleware: wrap QA commands (ruff, ty, unittest, coverage) and emit schema-validated JSON receipts to `artifacts/receipts/`. These receipts are the canonical attestation evidence cited in Heavy-lane OBPI closeout claims per `AGENTS.md` § Attestation.

## When to Use

- Producing Heavy-lane attestation evidence (receipt IDs for lint, typecheck, tests, coverage)
- Debugging a failing QA step and needing a deterministic receipt artifact
- Summarizing recurring advice from recent lint runs to tune agent guardrails
- Auditing QA compliance across an ADR or release cycle

## Workflow

1. **Wrap the QA step via ARB** — pick the appropriate verb. For any claim
   category named in `AGENTS.md` § Attestation § Canonical invocations,
   use the canonical invocation from that table; those commands are locked
   by `CANONICAL_STEP_COMMANDS` and divergence is flagged by
   `gz arb validate` as non-canonical provenance (GHI #199).
   - `uv run gz arb ruff <paths>` — ruff lint (canonical for lint claims)
   - `uv run gz arb typecheck` — wraps `ty check src`, the same target as
     `gz typecheck` and `gz closeout` (canonical for type-check claims)
   - `uv run gz arb step --name unittest -- uv run -m unittest -q` —
     canonical for tests-pass claims
   - `uv run gz arb coverage run -m unittest discover -s tests -t .` —
     canonical for coverage-floor claims
   - `uv run gz arb step --name <name> -- <command>` — any step not named
     in the canonical table (diagnostic or bespoke QA only; not valid
     attestation provenance)
2. **Validate the emitted receipts** — `uv run gz arb validate --limit 20`
3. **Summarize recent receipts** — `uv run gz arb advise --limit 20`
4. **Extract recurring patterns** (optional) — `uv run gz arb patterns`
5. **Cite receipt IDs in the attestation** per `AGENTS.md` § Attestation

## Example

```bash
# Produce full attestation evidence for Heavy-lane closeout.
# Each invocation below is the canonical form per
# AGENTS.md § Attestation § Canonical invocations.
uv run gz arb ruff src tests
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb coverage run -m unittest discover -s tests -t .
uv run gz arb validate --limit 10
uv run gz arb advise --limit 10
```

## Output Contract

- `gz arb ruff` / `step` / `ty` / `coverage` — exit 0 on success, 1 on command failure, 2 on ARB internal error; receipt always emitted to `artifacts/receipts/<run_id>.json`
- `gz arb validate` — human text by default; `--json` for machine-readable
- `gz arb advise` — human text; `--json` for machine-readable
- `gz arb patterns` — Markdown report by default; `--compact` for one-liner; `--json` for machine-readable

## Validation

- Confirm receipts appear under `artifacts/receipts/` after each wrapped run.
- Run `uv run gz arb validate` and confirm `invalid=0` before citing receipt IDs in attestations.

## References

- Binding rule: `AGENTS.md` § Attestation (em-dash pattern + canonical invocations + lane behavior + receipt-ID discipline)
- Deep-dive: `docs/governance/arb-middleware.md` (core concept, command surface, receipt schema, exit codes, rationale)
- Command docs: `docs/user/commands/arb.md`
- Manpage: `docs/user/manpages/arb.md`
- Absorption record: OBPI-0.25.0-33 under ADR-0.25.0
