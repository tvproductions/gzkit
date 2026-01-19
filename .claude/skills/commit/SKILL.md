---
name: commit
description: Create a conventional commit and push. Use when committing code changes.
---

# Git Commit Ritual

Create a conventional commit for staged changes and push.

## Instructions

1. **Check status and diff** - Run `git status` and `git diff --cached` to understand what's staged

2. **Draft commit message** following Conventional Commits:
   - Format: `type(scope): description` (72 char max first line)
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
   - Scope: module or area affected (e.g., `gates`, `cli`, `config`)
   - Description: imperative mood, lowercase, no period

3. **Commit** using HEREDOC for proper formatting:
   ```bash
   git commit -m "$(cat <<'EOF'
   type(scope): short description

   Optional body with more detail if needed.
   EOF
   )"
   ```

4. **Push** to origin

5. **Verify** with `git log -1 --oneline`

## Policy

- Do NOT add Co-Authored-By trailers
- Do NOT use `--amend` unless explicitly requested
- Do NOT use `--force` push
- If pre-commit hooks fail, fix issues and retry

## Examples

```text
feat(gates): add ADR validation logic
fix(cli): handle missing config file gracefully
docs(readme): update installation instructions
refactor(config): extract path resolution to helper
test(gates): add coverage for edge cases
chore(deps): bump ruff to 0.9
```
