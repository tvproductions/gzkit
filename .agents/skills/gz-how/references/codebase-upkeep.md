# Codebase upkeep

Not feature work: keeping the codebase good to operate in. You are here with a
maintenance task, or time to spare.

## Steps

- **A scheduled or stale chore** → **`gz-chore-runner`**: show, plan, advise,
  run and validate one chore. `uv run gz chores status` shows which are stale.
- **Where the debt is** → **`gz-tech-debt-review`**: a line-grounded survey that
  routes each finding to a chore, an in-flight fix or at most one GHI.
- **Class shapes that should be plain Python** →
  **`gz-pythonic-pattern-detect`** finds candidates;
  **`gz-pythonic-pattern-apply`** records the evidence for each rewrite applied.
- **Toolchain and dependencies** → **`gz-deps-upgrade`**: uv, the Python
  runtime, `pyproject.toml` pins and `uv.lock` in one pass.
- **The foundation backlog** → **`gz-foundation-triage`** ranks it.
- **Hygiene** → **`gz-tidy`**.

## Branches

- **A finding is a defect** → [Defects and GHIs](defects-and-ghis.md).
- **A finding suggests a design** → [Idea to ADR](idea-to-adr.md).

## Only you can

Choose which upkeep to spend time on; a chore never outranks drawn work.

## Then

[Commit and sync](commit-and-sync.md).
