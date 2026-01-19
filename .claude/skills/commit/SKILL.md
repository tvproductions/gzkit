---
name: commit
description: Review, commit, and push changes. Use when committing code changes.
---

# Git Commit Ritual

Review changes, create a meaningful commit, and push.

## Workflow

1. **Explore** - Run `git status` and `git diff` to understand all changes in the working tree

2. **Clarify** - If anything is unclear about intent or scope, ask the user

3. **Fix first** - If anything is broken, weird, or unusual, fix it now (it's all our work, not "someone else's problem")

4. **Categorize** - Summarize changes and craft a meaningful commit message that captures the "why"

5. **Stage all and commit** - Run `git add -A` then commit (pre-commit hooks run for hygiene/tidy)

6. **Fix and retry** - If pre-commit hooks fail, fix the issues and retry (no `--no-verify`)

7. **Push** - Once commit succeeds, push to origin

## Commit Message Format

Conventional commits: `type(scope): description`

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- 72 char max first line, imperative mood, lowercase, no period

## Policy

- Fix issues we find - don't bypass or ignore them
- NEVER use `--no-verify` (treat it like a forbidden word)
- Do NOT use `--amend` or `--force`
- Do NOT add Co-Authored-By trailers

## Examples

```text
feat(gates): add ADR validation logic
fix(cli): handle missing config file gracefully
docs(readme): update installation instructions
refactor(config): extract path resolution to helper
test(gates): add coverage for edge cases
chore(deps): bump ruff to 0.9
```
