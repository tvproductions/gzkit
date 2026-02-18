---
name: gz-adr-verification
description: Verify ADR evidence and linkage using gz ADR/status checks.
compatibility: GovZero v6 framework; Gate 2/traceability workflow
metadata:
  skill-version: "6.1.0"
  govzero-framework-version: "v6"
  govzero-author: "GovZero governance team"
  govzero_layer: "Layer 1 — Evidence Gathering"
gz_command: adr audit-check
invocation: uv run gz adr audit-check <ADR-ID>
---

# gz-adr-verification

Verify ADR evidence and lifecycle readiness with current `gz` commands.

## Procedure

```bash
# Focused ADR evidence verification
uv run gz adr audit-check ADR-0.3.0 --json

# ADR lifecycle and gate summary
uv run gz adr status ADR-0.3.0 --json
uv run gz status --json
```

## Optional Coverage Discovery

```bash
rg -n '@covers\("ADR-' tests
```

## References

- Command implementation: `src/gzkit/cli.py`
- User docs: `docs/user/commands/adr-audit-check.md`, `docs/user/commands/adr-status.md`
