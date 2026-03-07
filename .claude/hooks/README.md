# gzkit Claude Hooks

Current hook surface in gzkit:

| Hook | Event | Purpose |
| --- | --- | --- |
| `instruction-router.py` | `PreToolUse` (`Write|Edit`) | Auto-surfaces `.github/instructions/*.instructions.md` constraints (informational only) |
| `post-edit-ruff.py` | `PostToolUse` (`Write|Edit`) | Runs `ruff check --fix` and `ruff format` on edited Python files (non-blocking) |
| `ledger-writer.py` | `PostToolUse` (`Write|Edit`) | Records governance artifact edits via `gzkit.hooks.core.record_artifact_edit` |

## Notes

- Blocking canonical hooks are intentionally deferred until compatibility
  adaptation is defined under `ADR-0.9.0-airlineops-surface-breadth-parity`.
- See intake matrix:
  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
