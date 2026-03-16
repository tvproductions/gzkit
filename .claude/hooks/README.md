# gzkit Claude Hooks

Current hook surface in gzkit:

- `session-staleness-check.py`
  PreToolUse (`Write|Edit`) hook that detects stale pipeline
  artifacts from previous sessions and emits warnings.
- `instruction-router.py`
  PreToolUse (`Write|Edit`) hook that auto-surfaces
  `.github/instructions/*.instructions.md` constraints.
- `obpi-completion-validator.py`
  PreToolUse (`Write|Edit`) hook that gates OBPI brief completion
  by checking ledger evidence before allowing status changes.
- `plan-audit-gate.py`
  PreToolUse (`ExitPlanMode`) hook that validates the latest
  OBPI plan against `.claude/plans/.plan-audit-receipt.json`.
- `pipeline-router.py`
  PostToolUse (`ExitPlanMode`) hook that routes PASS receipts into
  `uv run gz obpi pipeline`.
- `pipeline-gate.py`
  PreToolUse (`Write|Edit`) hook that blocks `src/` and `tests/`
  writes until the runtime-owned active pipeline marker exists.
- `pipeline-completion-reminder.py`
  PreToolUse (`Bash`) hook that warns before `git commit` and
  `git push` when an active OBPI runtime still appears incomplete.
- `post-edit-ruff.py`
  PostToolUse (`Write|Edit`) hook that runs `ruff check --fix`
  and `ruff format` on edited Python files.
- `ledger-writer.py`
  PostToolUse (`Write|Edit`) hook that records governance
  artifact edits via `gzkit.hooks.core.record_artifact_edit`.

## Notes

- The operator-facing `gz-plan-audit` skill and receipt contract are
  ported under `ADR-0.12.0-obpi-pipeline-enforcement-parity`.
- `src/gzkit/pipeline_runtime.py` is the canonical shared runtime used
  by the CLI and generated pipeline hooks.
- The pipeline enforcement hooks are active in `.claude/settings.json`
  with the generated runtime order described below.

## Registration Order

- `PreToolUse` `ExitPlanMode`: `plan-audit-gate.py`
- `PostToolUse` `ExitPlanMode`: `pipeline-router.py`
- `PreToolUse` `Write|Edit`: `session-staleness-check.py`,
  then `pipeline-gate.py`, then `obpi-completion-validator.py`,
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
