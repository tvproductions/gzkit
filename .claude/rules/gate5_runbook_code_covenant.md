---
paths:
  - "docs/**"
  - "src/gzkit/**"
---

# Gate 5 Runbook-Code Covenant (gzkit)

Documentation is a first-class deliverable and must track behavior changes in the same patch set.

## Three-layer documentation model

| Layer | Location | Purpose |
|---|---|---|
| Operator runbook | `docs/user/runbook.md` | daily execution workflow |
| Governance runbook | `docs/governance/governance_runbook.md` | governance-maintainer workflow |
| Command docs | `docs/user/commands/**` | command contracts and examples |

## Required updates when behavior changes

- Update command docs and examples.
- Update runbook flows and verification commands.
- Ensure attestation language remains explicit where required.

## Validation bundle

```bash
uv run gz lint
uv run gz validate --documents --surfaces
uv run mkdocs build --strict
```

## Anti-patterns

- Do not leave placeholder output examples.
- Do not update code without docs when command output changes.
- Do not declare completion without explicit human attestation for heavy/foundation scope.
