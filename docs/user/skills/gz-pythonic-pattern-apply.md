# /gz-pythonic-pattern-apply

Capture before/after evidence with mechanical-delta proof when a Pythonic-pattern rewrite is applied. Use after `/gz-pythonic-pattern-detect` flagged a candidate marked `applied` — the rewrite must be backed by a semantics-pinning test, a TDD GREEN receipt, and non-regressing xenon/radon deltas.

---

## Purpose

`/gz-pythonic-pattern-apply` exposes the evidence-capture pair to `/gz-pythonic-pattern-detect`. When a candidate from the detection report is applied as a Pythonic rewrite, this skill drives the operator/agent through:

- Before/after metric capture (xenon, radon)
- Red-Green-Refactor TDD discipline with a semantics-pinning test
- ARB GREEN receipt emission
- Authoring a structured evidence file per applied candidate
- Back-linking the detection-report row so the audit trail is two-way

## When to Use

- After `/gz-pythonic-pattern-detect` produced a candidates report and the operator has decided to apply a specific row
- Whenever a class-to-Pythonic refactor lands and the team needs a corpus of attested refactor moves (same shape as ARB receipts, but for refactors instead of QA claims)

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-pythonic-pattern-apply/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). One evidence file per applied candidate lands at `.gzkit/chores/pythonic-design-pattern-application/proofs/application-YYYY-MM-DD-HHMMSS-<short-slug>.md`, citing pattern named, source candidate, local Python example witness, example-derived role map, before/after code, xenon + radon deltas, semantics tests, and the ARB GREEN receipt ID. The detection-report row is updated from `_[applied | deferred | not-pythonic-rewrite]_` to `applied: <evidence-file-path>`.

## Invocation

```text
/gz-pythonic-pattern-apply
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-pythonic-pattern-apply/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-pythonic-pattern-apply/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-pythonic-pattern-apply/SKILL.md` | Codex mirror | Read |
| `src/gzkit/chores/pythonic-design-pattern-application/CHORE.md` | Chore canon (evidence-file template) | Read |
| `design-patterns-en.zip` | Local Python example corpus (`Python/src/<Pattern>/Conceptual/main.py`) | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-pythonic-pattern-detect`](gz-pythonic-pattern-detect.md) | Pair skill — surfaces candidates this one applies |
| [`/gz-arb`](gz-arb.md) | Wraps unit-test runs to produce the GREEN receipt this skill cites |
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
