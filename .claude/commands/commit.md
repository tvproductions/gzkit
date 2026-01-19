---
description: Review, commit, and push changes
allowed-tools: Bash(git *), Edit, Read
---

# Commit

Current branch: !`git branch --show-current`
Working tree: !`git status --short`

Review my changes and commit them:

1. **Explore** - Look at `git status` and `git diff` to understand all changes
2. **Clarify** - If anything is unclear, ask me about intent or scope
3. **Categorize** - Group related changes and summarize for a meaningful commit message
4. **Stage and commit** - Stage relevant files and commit (pre-commit hooks will run)
5. **Fix** - If pre-commit fails, fix/tidy as needed and retry
6. **Push** - Once commit succeeds, push to origin

Commit message format: `type(scope): description` (conventional commits, 72 char max)

Policy:

- Do NOT add Co-Authored-By trailers
- Do NOT use --amend or --force
