---
description: Review, commit, and push changes
allowed-tools: Bash(git *), Edit, Read
---

# Commit

Current branch: !`git branch --show-current`
Working tree: !`git status --short`

Review the repo and commit:

1. **Explore** - Look at `git status` and `git diff` to understand all changes
2. **Clarify** - If anything is unclear, ask me about intent or scope
3. **Fix first** - If anything is broken, weird, or unusual, fix it now (it's all our work)
4. **Categorize** - Summarize changes for a meaningful commit message
5. **Stage all and commit** - Run `git add -A` then commit (pre-commit hooks run for hygiene)
6. **Fix and retry** - If pre-commit fails, fix issues and retry (no --no-verify)
7. **Push** - Once commit succeeds, push to origin

Commit message format: `type(scope): description` (conventional commits, 72 char max)

Policy:

- Fix issues we find - don't bypass or ignore them
- NEVER use --no-verify (treat it like a forbidden word)
- Do NOT use --amend or --force
- Do NOT add Co-Authored-By trailers
