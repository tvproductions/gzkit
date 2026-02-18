---
name: gz-adr-check
description: Run blocking ADR evidence checks for a target ADR.
compatibility: GovZero v6 framework; CI-capable evidence gate
metadata:
  skill-version: "1.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
gz_command: adr audit-check
invocation: uv run gz adr audit-check <ADR-ID>
lifecycle_state: active
owner: gzkit-governance
last_reviewed: 2026-02-18
---

# gz-adr-check

Run the ADR evidence gate using `gz adr audit-check`.

## When to Use

- Before marking an ADR Completed/Validated
- During CI checks for a target ADR
- Before `gz closeout`, `gz attest`, or `gz audit`

## Invocation

```bash
uv run gz adr audit-check ADR-0.3.0
uv run gz adr audit-check ADR-0.3.0 --json
```

## Behavior

- Verifies linked OBPI briefs are complete and evidence-ready
- Returns non-zero on missing evidence or incomplete briefs
- Produces JSON output for automation when `--json` is used

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-audit-check.md`
