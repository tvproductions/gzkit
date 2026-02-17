# gz-obpi-audit

Audit a single OBPI brief against actual code/test evidence.

## Purpose

Detects **paperwork drift** — where work is done but the brief wasn't updated.

## Evidence Checks

| Check | Command |
|-------|---------|
| Find tests | `grep -rn "@covers.*ADR-{id}" tests/` |
| Run tests | `uv run -m unittest -v {test}` |
| Coverage | `uv run coverage report --include='{module}'` |

## Ledger Output

Writes proof to: `ADR-.../logs/obpi-audit.jsonl`

```json
{
  "obpi_id": "OBPI-X.Y.Z-NN",
  "brief_status_before": "Accepted",
  "brief_status_after": "Completed",
  "evidence": {...},
  "action_taken": "brief_updated"
}
```

## Related

- **Skill procedure:** `SKILL.md` (this folder)
- **Orchestrator:** `gz-obpi-reconcile` (runs audit for all briefs)
- **Table sync:** `gz-obpi-sync` (trusts briefs, doesn't verify)
