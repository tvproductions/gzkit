---
description: Stage, commit, and push changes
allowed-tools: Bash(git status:*), Bash(git diff:*), Bash(git add:*), Bash(git commit:*), Bash(git log:*), Bash(git push:*)
---

# Commit

Current branch: !`git branch --show-current`
Working tree status: !`git status --short`

Stage, commit, and push my changes:

1. Review `git status` and `git diff` to understand all changes
2. Stage the relevant files with `git add <files>` (be selective, not `git add -A`)
3. Review `git diff --cached` to confirm what will be committed
4. Draft a commit message following conventional commits: `type(scope): description`
   - Types: feat, fix, docs, style, refactor, test, chore
   - 72 char max first line, imperative mood, lowercase, no period
5. Commit using HEREDOC format
6. Push to origin
7. Verify with `git log -1 --oneline`

Policy:

- Do NOT add Co-Authored-By trailers
- Do NOT use --amend
- Do NOT use --force push
- Do NOT stage unrelated or sensitive files
