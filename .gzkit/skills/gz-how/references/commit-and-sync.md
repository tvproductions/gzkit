# Commit and sync

You are here with a change ready to land.

## Steps

1. **Sync generated surfaces** if you edited a skill, rule or canon:
   **`gz-agent-sync`** — `uv run gz agent sync control-surfaces` regenerates
   every mirror. Edit `.gzkit/skills/`, never a mirror.
2. **`gz-check`** — `git add -A`, then `uv run gz check`, the per-change gate.
   A pass counts only on a fully staged tree.
3. **Commit** through the hooks, never `--no-verify`. A commit touching `src/`
   or `tests/` carries a `Task:` trailer.
4. **Push.** The pre-push hook runs `gz check` again. **`git-sync`**
   (operator-invoked) runs the whole guarded ritual.

## Branches

- **A check fails** — its message names the rule and the recovery; fix and
  re-run. Read a verifier's exit status straight after it, never through a pipe.
- **`gz check --full`** adds the BDD tier and preflight; CI runs it.

## Only you can

Nothing by default; work lands on `main` directly.

## Then

Back to the flow the change belonged to, or [Session end](session-end.md).
