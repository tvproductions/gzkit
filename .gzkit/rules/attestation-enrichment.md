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

## Receipt-ID Requirement (Binding)

Narrative recall of "test counts, coverage deltas, files changed" is not
sufficient by itself. Even a fully honest agent's end-of-session summary is
post-hoc reconstruction: the reporting pathway and the execution pathway are
structurally separate (Lindsey et al. 2025 — the math-explanation pathway
and the math-execution pathway are distinct circuits; a model can produce a
plausible explanation of reasoning it did not actually perform).

The only faithful record of a QA step is the wrapped-command receipt. For
every claim category cited in an attestation, include at least one ARB
receipt ID (`artifacts/receipts/<id>.json`) produced by the **canonical
command** listed below. Parallel approximations (different scope, different
target tree, different flags) are not acceptable — GHI #199 traces the class
of failure where an ARB receipt reported exit 0 against `ty check .` while
the governance gate (`gz typecheck` → `ty check src`) reported exit 1.

| Claim category | Canonical invocation | Receipt name prefix |
|----------------|----------------------|---------------------|
| Lint clean | `uv run gz arb ruff` | `arb-ruff-` |
| Type check clean | `uv run gz arb typecheck` | `arb-step-typecheck-` |
| Tests pass | `uv run gz arb step --name unittest -- uv run -m unittest -q` | `arb-step-unittest-` |
| Coverage floor | `uv run gz arb coverage run -m unittest discover -s tests -t .` | `arb-step-coverage-` |
| Docs build clean | `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` | `arb-step-mkdocs-` |

Each canonical invocation above is locked by `CANONICAL_STEP_COMMANDS` in
`src/gzkit/arb/validator.py` and enforced by `gz arb validate` — a receipt
whose `step.name` is one of these labels but whose `step.command` diverges
is flagged as non-canonical provenance and counted as invalid. Extending
the table widens the provenance net; do not shrink it.

`gz arb typecheck` (added under GHI #199) wraps `uv run ty check src` — the
same command `gz typecheck` and `gz closeout` invoke. Do not author heavy-lane
type-check receipts via `gz arb ty check <custom-scope>`; the receipt will
drift from the gate and the attestation claim will be post-hoc false.

Receipt IDs should appear inline in the enrichment, e.g.
`(lint: receipt arb-2026-04-14T12-34-56-ruff)`. The citing agent must also
have verified that the receipt exists and its status matches the claim —
fabricating a receipt ID is the same failure as fabricating the claim.

**Lane behavior:**

- **Lite lane:** missing receipt IDs produce a warning. The attestation
  still records but is flagged as narrative-only.
- **Heavy lane:** missing receipt IDs are a fail-closed error. Heavy lane
  attestation without receipts is rejected; re-run the QA steps under ARB
  and re-cite.

**If you are the agent drafting the attestation and no receipts exist:**
run the relevant ARB-wrapped commands first, then draft the attestation
citing the fresh receipt IDs. Narrative substitutes are not acceptable.

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
no absorption of the external reference cli_audit module warranted.
Receipts: lint arb-2026-04-14T12-34-56-ruff; types arb-2026-04-14T12-35-02-ty;
tests arb-2026-04-14T12-36-18-unittest; coverage arb-2026-04-14T12-37-44-coverage.
```

## Anti-patterns

- Passing only the user's brief token without enrichment — loses signal
- Replacing the user's words with an agent-generated sentence — loses
  provenance
- Adding enrichment not grounded in concrete session evidence — fabrication
- Using vague adjectives ("good", "clean", "comprehensive") without naming
  the facts behind them
- Enriching with information from other sessions or unrelated work
