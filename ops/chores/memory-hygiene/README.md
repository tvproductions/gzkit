# memory-hygiene

Audit Claude Code auto-memory for process drift into governed artifacts.

- **Lane:** Lite
- **Vendor:** claude (Claude Code only)

Scans `~/.claude/projects/<project>/memory/` for feedback and project memories
that encode process corrections. These should live in skills, rules, or CLAUDE.md
instead.

```bash
uv run gz chores advise memory-hygiene
uv run gz chores run memory-hygiene
```
