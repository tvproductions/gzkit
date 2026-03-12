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

- Blocking canonical hooks were deferred during `ADR-0.9.0`, but the active
  successor contract now lives under
  `ADR-0.12.0-obpi-pipeline-enforcement-parity`.
- Historical intake matrix:
  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
- Active successor contract:
  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/claude-pipeline-hooks-parity-matrix.md`
