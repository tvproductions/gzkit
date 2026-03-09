# gzkit Claude Hooks

Current hook surface in gzkit:

## PreToolUse (Write|Edit)

- `obpi-completion-validator.py` **(blocking)**
  PreToolUse gate that checks `.gzkit/ledger.jsonl` for completion evidence
  before allowing OBPI brief status changes to "Completed". For Heavy/Foundation
  lane OBPIs, also requires human attestation evidence. Exits with code 2 to
  block premature completion. Adapted from airlineops canonical hook in OBPI-0.9.0-02.
- `instruction-router.py`
  PreToolUse hook that auto-surfaces
  `.github/instructions/*.instructions.md` constraints.

## PostToolUse (Edit|Write)

- `post-edit-ruff.py`
  PostToolUse hook that runs `ruff check --fix`
  and `ruff format` on edited Python files.
- `ledger-writer.py`
  PostToolUse hook that records governance artifact edits via
  `gzkit.hooks.core.record_artifact_edit`. Also handles OBPI completion
  recording (receipt emission, anchor capture) — covers the canonical
  `obpi-completion-recorder.py` functionality.

## Tranche History

| Tranche | OBPI | Hooks |
| --- | --- | --- |
| 1 (non-blocking) | OBPI-0.9.0-01 | `instruction-router.py`, `post-edit-ruff.py`, `README.md` |
| 2 (blocking/deferred) | OBPI-0.9.0-02 | `obpi-completion-validator.py` (imported), `obpi-completion-recorder.py` (already covered), 5 pipeline hooks (deferred) |

## Notes

- See intake matrix:
  `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`
- Deferred hooks (pipeline-gate, pipeline-router, plan-audit-gate,
  pipeline-completion-reminder, session-staleness-check) all depend on
  plan-mode lifecycle infrastructure not yet present in gzkit.
