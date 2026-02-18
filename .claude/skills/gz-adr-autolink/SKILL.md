---
name: gz-adr-autolink
description: Maintain ADR verification links by scanning @covers decorators and updating docs.
compatibility: GovZero v6 framework; manual linkage workflow
metadata:
  skill-version: "1.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
gz_command: workflow
invocation: rg -n '@covers\("ADR-' tests
---

# gz-adr-autolink

Maintain ADR-to-test linkage using current repository workflows.

## Procedure

```bash
# 1) Discover coverage annotations
rg -n '@covers\("ADR-' tests

# 2) Validate linkage for target ADR
uv run gz adr audit-check ADR-0.3.0 --json

# 3) Re-lint after doc updates
uv run gz lint
```

## Notes

- There is no dedicated `gz adr autolink` command in this repository.
- Update ADR verification sections manually based on discovered coverage.

## References

- Command implementation: `src/gzkit/cli.py`
- Related docs: `docs/user/commands/adr-audit-check.md`
