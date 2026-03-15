---
paths:
  - ".github/**"
  - "docs/design/adr/**"
---

# GitHub CLI Guardrails (gzkit)

Use `gh` only when explicitly requested by the user, an active brief, or closeout protocol.

## Allowed commands

```bash
gh auth status
gh issue create --label defect --title "..." --body "..."
gh issue list --search "ADR-X.Y.Z" --state open
gh issue close <number> --comment "Resolved by ADR-X.Y.Z closeout."
gh release create vX.Y.Z --title "vX.Y.Z" --notes-file RELEASE_NOTES.md
```

## Prohibited without explicit approval

- Repository/org settings mutations
- Secret/token management
- Force pushes
- Merging PRs without explicit human authorization

## Defect tracking requirement

When a defect cannot be fixed in the current patch:

1. `gh issue create --label defect ...`
2. Link the issue in the relevant ADR/OBPI evidence section.
