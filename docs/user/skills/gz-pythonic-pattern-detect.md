# /gz-pythonic-pattern-detect

Surface Pythonic-design-pattern refactor candidates after ADR closeout. Use when ruff/ty are zeroed and complexity gates are green but the code shape still looks Java-flavored — Strategy classes that should be functions, Singletons that should be module-level constants, Visitor ladders that should be `match`. Wields the `pythonic-design-pattern-detection` chore.

---

## Purpose

`/gz-pythonic-pattern-detect` exposes the post-post-implementation pattern-shape audit. After idiom-level chores (`pythonic-refactoring`) and metric-level chores (`complexity-reduction-xenon`, `module-sloc-cap-radon`) have all passed, this skill drives the AST scanner over `src/` to flag class shapes whose Pythonic equivalent is cleaner. The local `design-patterns-en.zip` Python examples are the absorption surface — every disposition records the `Python/src/<Pattern>/Conceptual/main.py` witness, role map, and Pythonic collapse.

## When to Use

- After ADR closeout when the code is functionally complete but the shape still feels imported-from-Java
- During chore rotations when `pythonic-refactoring` reports zero ruff/ty findings — the next question is *"is the **shape** Pythonic?"*
- Before pairing with `/gz-pythonic-pattern-apply` to produce evidence for a specific refactor

## What to Expect

The skill reads its canonical execution contract from `.gzkit/skills/gz-pythonic-pattern-detect/SKILL.md` (mirrored into `.claude/skills/`, `.agents/skills/`, and `.github/skills/`). The scanner emits a candidates report at `.gzkit/chores/pythonic-design-pattern-detection/proofs/candidates-YYYY-MM-DD.md` listing every match with file:line, AST signal, Pythonic refactor target, local Python example path, output path, role map, and disposition. Reference-mode patterns (Bridge, Flyweight, Factory Method) are listed in `CHORE.md` for human-eye review since they admit no robust mechanical signal.

## Invocation

```text
/gz-pythonic-pattern-detect
```

| Argument / Flag | Required | Description |
|-----------------|----------|-------------|
| *(see SKILL.md)* | — | Arguments are defined by the canonical skill contract |

## Supporting Files

| File | Role | Read/Write |
|------|------|------------|
| `.gzkit/skills/gz-pythonic-pattern-detect/SKILL.md` | Canonical skill contract | Read |
| `.claude/skills/gz-pythonic-pattern-detect/SKILL.md` | Claude mirror | Read |
| `.agents/skills/gz-pythonic-pattern-detect/SKILL.md` | Codex mirror | Read |
| `src/gzkit/chores/pythonic-design-pattern-detection/scan.py` | AST scanner | Read |
| `src/gzkit/chores/pythonic-design-pattern-detection/CHORE.md` | Chore canon (full 22-pattern example table) | Read |
| `design-patterns-en.zip` | Local Python example corpus (`Python/src/<Pattern>/Conceptual/main.py`) | Read |

## Related Skills and Commands

| Related | Relationship |
|---------|-------------|
| [`/gz-pythonic-pattern-apply`](gz-pythonic-pattern-apply.md) | Pair skill — captures evidence when a candidate is applied |
| [`/gz-chore-runner`](gz-chore-runner.md) | Generic chore runner that wields the same `gz chores run` interface |
| [skills index](index.md) | Browse the full skill catalog |
| [governance runbook](../../governance/governance_runbook.md) | Workflow context |
