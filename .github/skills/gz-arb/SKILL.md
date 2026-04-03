---
name: gz-arb
description: "ARCHIVED: Consolidated into gz-check. Use /gz-check for quality evidence workflows."
lifecycle_state: retired
archived_into: gz-check
deprecation_replaced_by: gz-check
deprecation_migration: "Use /gz-check directly."
deprecation_communication: "Consolidated during skill consolidation 2026-04-03."
deprecation_announced_on: "2026-04-03"
retired_on: "2026-04-03"
owner: gzkit-governance
last_reviewed: 2026-04-03
---

# gz-arb (ARCHIVED)

This skill has been consolidated into **gz-check**.

The canonical quality evidence sequence is now documented in `gz-check` § Full Quality Evidence Sequence:

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz check
```

Use `/gz-check` for all pre-merge, pre-attestation, and Gate 2/3 quality verification.
