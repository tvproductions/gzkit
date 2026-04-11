# Plan-Audit-Receipt Contract

The plan-audit-receipt (`.claude/plans/.plan-audit-receipt.json`) is the handoff artifact linking plan mode to this pipeline:

```json
{
  "obpi_id": "OBPI-0.14.0-05",
  "timestamp": "2026-03-16T12:00:00Z",
  "verdict": "PASS",
  "plan_file": "my-plan-name.md",
  "gaps_found": 0
}
```

- Written by the `plan-audit-gate.py` hook when exiting plan mode
- Read by Stage 1 to locate the approved plan
- **verdict = PASS**: plan is aligned with OBPI brief -- proceed
- **verdict = FAIL**: plan has alignment gaps -- abort and resolve
