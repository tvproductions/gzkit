# Local Agent Rules

- Order versioned identifiers semantically, never lexicographically. Example: `ADR-0.9.0` comes before `ADR-0.10.0`.
- Apply semantic-version ordering in ADR summaries, comparisons, and any operator-facing status narration.
- When adding imports in an Edit call, always include the code that uses them in the same edit. The post-edit ruff hook removes unused imports immediately — splitting import addition and usage across separate edits causes the import to be deleted before it's referenced.
- Always prefix `uv run gz` and `uv run -m gzkit` Bash commands with `PYTHONUTF8=1` on Windows. Rich console output contains Unicode characters (checkmarks, arrows, warning signs) that fail with `UnicodeEncodeError` on Windows legacy console (cp1252). Example: `PYTHONUTF8=1 uv run gz gates --adr ADR-0.1.0`.
