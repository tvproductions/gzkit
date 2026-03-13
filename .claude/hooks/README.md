# gzkit Claude Hooks

Current hook surface in gzkit:

- `instruction-router.py`
  PreToolUse (`Write|Edit`) hook that auto-surfaces
  `.github/instructions/*.instructions.md` constraints.
- `plan-audit-gate.py`
  PreToolUse (`ExitPlanMode`) hook that validates the latest
  OBPI plan against `.claude/plans/.plan-audit-receipt.json`.
- `pipeline-router.py`
  PostToolUse (`ExitPlanMode`) hook that routes PASS receipts into
  `gz-obpi-pipeline`.
- `pipeline-gate.py`
  PreToolUse (`Write|Edit`) hook that blocks `src/` and `tests/`
  writes until the active pipeline marker exists.
- `pipeline-completion-reminder.py`
  PreToolUse (`Bash`) hook that warns before `git commit` and
  `git push` when an active OBPI pipeline still appears incomplete.
- `post-edit-ruff.py`
  PostToolUse (`Write|Edit`) hook that runs `ruff check --fix`
  and `ruff format` on edited Python files.
- `ledger-writer.py`
  PostToolUse (`Write|Edit`) hook that records governance
  artifact edits via `gzkit.hooks.core.record_artifact_edit`.

## Notes

- The operator-facing `gz-plan-audit` skill and receipt contract are
  ported under `ADR-0.12.0-obpi-pipeline-enforcement-parity`.
- `plan-audit-gate.py`, `pipeline-router.py`, `pipeline-gate.py`,
  and `pipeline-completion-reminder.py` are generated locally but
  not yet active in `.claude/settings.json`.
  Registration and ordering stay with `OBPI-0.12.0-06`.
- Historical intake matrix:
  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/
claude-hooks-intake-matrix.md`
- Active successor contract:
  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/
claude-pipeline-hooks-parity-matrix.md`
