# GEMINI.md (src/gzkit/hooks)

This directory contains integration hooks for external tools and agents.

## Implementation Guidelines

- **Isolation:** Hooks should not rely heavily on the internal core of `gzkit` CLI unless strictly necessary, to maintain fast startup times and avoid breaking when CLI internals change.
- **Fail-Open:** Agent and IDE hooks should generally fail-open (e.g., if a hook errors, it should not break the user's primary workflow like committing or pushing, unless explicitly enforcing a covenant gate).
- **Subagents:** When defining system prompts for subagents within these hooks, always include a clear 'Why' parameter to ensure the subagent's context is narrowly focused on the task at hand.
