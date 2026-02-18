---
name: gz-adr-map
description: Build ADR-to-artifact traceability using gz state and repository search.
compatibility: GovZero v6 framework; manual mapping workflow
metadata:
  skill-version: "1.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
gz_command: state
invocation: uv run gz state --json
---

# gz-adr-map

Construct ADR traceability with the available `gz` and repo-local tooling.

## Procedure

```bash
# 1) ADR/OBPI graph from ledger
uv run gz state --json

# 2) Test coverage hints
rg -n '@covers\("ADR-' tests

# 3) Validate a target ADR's linked briefs
uv run gz adr audit-check ADR-0.3.0 --json
```

## Notes

- There is no dedicated `gz adr map` subcommand in this repository.
- This skill is intentionally workflow-based instead of a single command.

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/state.md`, `docs/user/commands/adr-audit-check.md`
