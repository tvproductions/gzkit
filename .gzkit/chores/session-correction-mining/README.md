# session-correction-mining

Mine Claude Code session transcripts under `~/.claude/projects/` for recurring
operator-correction patterns the self-reported insights stream missed. A
read-only stdlib miner detects corrective-marker operator messages that follow
assistant activity, clusters recurrences across distinct sessions, and emits
PII-scrubbed proposal records to
`.gzkit/chores/session-correction-mining/proofs/` when a pattern recurs ≥3 times
(ADR-0.0.70). Output is candidates only — nothing auto-promotes.

## Quick Start

```bash
uv run python -m gzkit.insights.correction_mining --dry-run
```

Drop `--dry-run` to write proposal records to `proofs/`.

```bash
uv run -m unittest tests/chores/test_session_correction_mining.py -q
```

## Lane

**lite**
