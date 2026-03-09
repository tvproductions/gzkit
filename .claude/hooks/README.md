# gzkit Claude Hooks

Current hook surface in gzkit:

- `instruction-router.py`
  PreToolUse (`Write|Edit`) hook that auto-surfaces
  `.github/instructions/*.instructions.md` constraints.
- `post-edit-ruff.py`
  PostToolUse (`Write|Edit`) hook that runs `ruff check --fix`
  and `ruff format` on edited Python files.
- `ledger-writer.py`
  PostToolUse (`Write|Edit`) hook that records governance
  artifact edits via `gzkit.hooks.core.record_artifact_edit`.

## Notes

- Blocking canonical hooks are intentionally deferred until compatibility
  adaptation is defined under `ADR-0.9.0-airlineops-surface-breadth-parity`.
- See intake matrix:
  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/
claude-hooks-intake-matrix.md`
