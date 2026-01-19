---
name: commit
description: Review, commit, and push changes. Use when committing code changes.
---

# Git Commit Ritual

Review changes, create a meaningful commit, and push.

## Workflow

1. **Explore** - Run `git status` and `git diff` to understand all changes in the working tree

2. **Clarify** - If anything is unclear about intent or scope, ask the user

3. **Categorize** - Group related changes and craft a meaningful commit message that captures the "why"

4. **Stage and commit** - Stage relevant files with `git add` and commit (pre-commit hooks will run for hygiene/tidy)

5. **Fix** - If pre-commit hooks fail, fix the issues and retry the commit

6. **Push** - Once commit succeeds, push to origin

## Commit Message Format

Conventional commits: `type(scope): description`

- Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- 72 char max first line, imperative mood, lowercase, no period

## Policy

- Do NOT add Co-Authored-By trailers
- Do NOT use `--amend` or `--force`

## Examples

```text
feat(gates): add ADR validation logic
fix(cli): handle missing config file gracefully
docs(readme): update installation instructions
refactor(config): extract path resolution to helper
test(gates): add coverage for edge cases
chore(deps): bump ruff to 0.9
```
