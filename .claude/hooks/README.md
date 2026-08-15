# gzkit Claude Hooks

Current hook surface in gzkit:

- `verifier-pipe-gate.py`
  PreToolUse (`Bash`) hook that refuses a command piping a verifier
  (`unittest`, `behave`, `mkdocs --strict`, `gz check`, any
  ARB-wrapped verifier) into another process — the shell would
  report the last stage's exit, masking a failing run as green.
  Mechanizes `.gzkit/rules/tests.md` § Verification exit-code
  integrity; `pipefail` / `PIPESTATUS` opt out (GHI #589).
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
  PostToolUse (`Write|Edit`) hook that runs `ruff check` on
  edited Python files and surfaces findings to stderr (GHI #239).
- `ledger-writer.py`
  PostToolUse (`Write|Edit`) hook that records governance
  artifact edits via `gzkit.hooks.core.record_artifact_edit`.
- `stop-turn-feedback.py`
  Stop (`*`) hook that runs `ruff check` over git-dirty Python
  files at turn end and blocks the stop with agent-actionable
  prose; fail-open, one block per turn (ADR-0.0.70).
- `session-start-advisement.py`
  SessionStart (`*`) hook that surfaces the newest handoff and its
  advised steps via `additionalContext` (universal) and
  `initialUserMessage` (Claude-side upgrade seeding a real first
  turn). Binds by seeding, never by refusing; it ADVISES, and
  since 2026-08-15 that is the WHOLE mechanism — the PreToolUse
  resume gate is retired (operator ruling: a handoff is an advisor,
  not a gate-keeping nanny). `gz handoff decide` still books the
  operator's verbatim ruling to Layer 2 (GHI #757); nothing gates
  on the absence of one.
- `session-exit-bookmark.py`
  SessionEnd (`*`) hook that writes a CHECKPOINT handoff recording
  where the session stopped — the trigger ADR-0.0.65 never
  specified. Fires on `/exit` AND on `clear`. Books, never refuses;
  the bookmark is CHECKPOINT mode so it can never discharge a token
  surrender (GHI #756).

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
- `PreToolUse` `Write|Edit|NotebookEdit`: `session-staleness-check.py`,
  then `pipeline-gate.py`, then `obpi-completion-validator.py`,
  then `instruction-router.py`
- `PreToolUse` `Bash`: `verifier-pipe-gate.py`,
  then `pipeline-completion-reminder.py`,
  then `ghi-triage-chat-silence.py`
- `PostToolUse` `Edit|Write`: `post-edit-ruff.py`,
  then `ledger-writer.py`
- `Stop` `*`: `stop-turn-feedback.py`
- `SessionStart` `*`: `session-start-advisement.py`
- `SessionEnd` `*`: `session-exit-bookmark.py`
- Historical intake matrix:
  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/
claude-hooks-intake-matrix.md`
- Active successor contract:
  `docs/design/adr/pre-release/ADR-0.12.0-obpi-pipeline-enforcement-parity/
claude-pipeline-hooks-parity-matrix.md`
