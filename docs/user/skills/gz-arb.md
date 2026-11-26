# /gz-arb

Wrap QA commands in ARB receipts for attestation evidence, or audit lint
patterns from the receipts.

---

## Purpose

`/gz-arb` runs gzkit's QA steps (ruff, ty, unittest, coverage, the docs build)
through the ARB middleware, which writes a schema-validated JSON receipt for each
run to `artifacts/receipts/`. Those receipt IDs are the attestation evidence
`AGENTS.md` § Attestation requires: the bare `gz lint`, `gz test` and `gz check`
commands produce no receipt.

## When to Use

- **Before attestation or closeout** — produce the receipt IDs that
  `gz obpi complete`, `gz adr emit-receipt` and Heavy-lane closeout claims cite.
- **Debugging a failing QA step** — keep a receipt of the failing run.
- **Tuning guardrails** — summarize recurring advice from recent lint receipts.
- **Auditing QA compliance** across an ADR or a release cycle.

For the per-change quality gate without receipts, use
[`/gz-check`](gz-check.md).

## What to Expect

The skill runs the canonical invocations, one per claim category; they are locked
by `CANONICAL_STEP_COMMANDS`, and `gz arb validate` flags a divergent command as
non-canonical provenance:

```bash
uv run gz arb ruff src tests
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run unittest-parallel -t . -s tests --buffer
uv run gz arb coverage
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
```

It then validates the receipts (`uv run gz arb validate`), summarizes them
(`uv run gz arb advise`) and, optionally, extracts recurring patterns
(`uv run gz arb patterns`).

**Success** looks like: each wrapped step exits 0 and `gz arb validate` reports
`invalid=0`, so the receipt IDs can be cited.

**Failure** looks like: a wrapped step exits 1 (the command failed; its receipt
is still written) or 2 (an ARB internal error). Fix the reported findings and
rerun.

## Invocation

```text
/gz-arb
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(none)* | — | Runs the receipt workflow with no arguments |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.claude/skills/gz-arb/SKILL.md` | Agent execution instructions | Read |
| `artifacts/receipts/` | Receipts written by each wrapped run | Write |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`gz arb`](../manpages/arb.md) | The CLI command group this skill wields |
| [`/gz-check`](gz-check.md) | The per-change quality gate; emits no ARB receipt |
| [`/git-sync`](git-sync.md) | Typically follows after quality checks pass |
