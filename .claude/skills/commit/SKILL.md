---
name: commit
description: Stage, commit, and push changes. Use when committing code changes.
---

# Git Commit Ritual

Stage, commit, and push changes.

## Instructions

1. **Review changes** - Run `git status` and `git diff` to understand all changes

2. **Stage files** - Use `git add <files>` to stage relevant changes (be selective, not `git add -A`)

3. **Confirm staged** - Run `git diff --cached` to verify what will be committed

4. **Draft commit message** following Conventional Commits:
   - Format: `type(scope): description` (72 char max first line)
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
   - Scope: module or area affected (e.g., `gates`, `cli`, `config`)
   - Description: imperative mood, lowercase, no period

5. **Commit** using HEREDOC for proper formatting:

   ```bash
   git commit -m "$(cat <<'EOF'
   type(scope): short description

   Optional body with more detail if needed.
   EOF
   )"
   ```

6. **Push** to origin

7. **Verify** with `git log -1 --oneline`

## Policy

- Do NOT add Co-Authored-By trailers
- Do NOT use `--amend` unless explicitly requested
- Do NOT use `--force` push
- Do NOT stage unrelated or sensitive files
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
