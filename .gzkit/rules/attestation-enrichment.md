---
id: attestation-enrichment
paths:
  - "**"
description: Pass user attestation and commit words verbatim; append concrete session-grounded characterization
---

# Attestation and Commit Message Enrichment

When the user provides a brief attestation or commit message (e.g., "attest
completed", "fix the thing"), pass their words through verbatim **and** append
substantive characterization so the ledger or git history carries real signal.
The user's words retain provenance; the agent's characterization supplies the
weight.

## Pattern

```
<user's verbatim words> — <concrete characterization grounded in session evidence>
```

The enrichment follows the em-dash and cites concrete facts gathered during
the work.

## What "substantive characterization" means

Enrichment must reference concrete facts the agent gathered during the
session:

- Decisions recorded (Absorb/Confirm/Exclude, chosen approach, rejected
  alternatives)
- Concrete evidence: test counts, coverage deltas, line counts, files changed
- File references with paths (and line numbers when relevant) for
  inspectability
- Rationale citing named dimensions, not vague adjectives

## Applies to

- `uv run gz obpi complete --attestation-text ...`
- `uv run gz adr emit-receipt ... --attestor ...`
- Any `gz` CLI accepting an attestation string
- `git commit -m "..."` messages (including HEREDOC form)

## Example

User says: `attest completed`

Agent passes to `--attestation-text`:

```
attest completed — Confirm decision: gzkit cli_audit + doc_coverage surface
architecturally superior (AST vs parser._actions private API, 5-surface
manifest-driven coverage, 76 vs 1 tests, frozen Pydantic vs dict[str,Any]);
no absorption of airlineops/opsdev/lib/cli_audit.py warranted.
```

## Anti-patterns

- Passing only the user's brief token without enrichment — loses signal
- Replacing the user's words with an agent-generated sentence — loses
  provenance
- Adding enrichment not grounded in concrete session evidence — fabrication
- Using vague adjectives ("good", "clean", "comprehensive") without naming
  the facts behind them
- Enriching with information from other sessions or unrelated work
