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
- The pipeline enforcement hooks are active in `.claude/settings.json`
  with the generated runtime order described below.

## Registration Order

- `PreToolUse` `ExitPlanMode`: `plan-audit-gate.py`
- `PostToolUse` `ExitPlanMode`: `pipeline-router.py`
- `PreToolUse` `Write|Edit`: `pipeline-gate.py`,
  then `instruction-router.py`
- `PreToolUse` `Bash`: `pipeline-completion-reminder.py`
- `PostToolUse` `Edit|Write`: `post-edit-ruff.py`,
  then `ledger-writer.py`
- Historical intake matrix:
  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/
claude-hooks-intake-matrix.md`
- Active successor contract:
  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/
claude-pipeline-hooks-parity-matrix.md`
