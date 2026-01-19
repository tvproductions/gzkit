---
description: Create a conventional commit for staged changes
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git commit:*), Bash(git log:*)
---

# Commit

Current staged changes: !`git diff --cached --stat`
Current branch: !`git branch --show-current`

Create a conventional commit for my staged changes:

1. Run `git diff --cached` to review the full diff
2. Draft a commit message following conventional commits: `type(scope): description`
   - Types: feat, fix, docs, style, refactor, test, chore
   - 72 char max first line, imperative mood, lowercase, no period
3. Commit using HEREDOC format
4. Verify with `git log -1 --oneline`

Policy:

- Do NOT add Co-Authored-By trailers
- Do NOT use --amend
- Do NOT push
