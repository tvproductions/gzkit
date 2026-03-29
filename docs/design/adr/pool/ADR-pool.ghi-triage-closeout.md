---
id: ADR-pool.ghi-triage-closeout
status: Pool
parent: PRD-GZKIT-1.0.0
lane: heavy
enabler: null
inspired_by: null
---

# ADR-pool.ghi-triage-closeout: GitHub Issue Triage and Closeout Integration

## Status

Pool

## Date

2026-03-29

## Parent PRD

PRD-GZKIT-1.0.0

## Context

GitHub Issues (GHIs) are used to track defects, enhancements, and attestation records.
Currently there is no `gz` command to view, triage, or associate GHIs with ADRs. Issue
review during ADR closeout relies on manual `gh issue list --search` invocations, making
it easy to leave orphaned issues open after work is complete.

## Decision

Add a `gz ghi` subcommand group that wraps `gh` CLI calls and correlates issues against
ADR identifiers for triage and closeout workflows.

## Proposed Surface

```text
gz ghi list                    # open issues, triage-friendly table
gz ghi check ADR-0.3.0        # issues referencing this ADR
gz ghi check --all             # issues by ADR association (orphans highlighted)
```

## Use Cases

1. **Triage** — operator reviews open issues with labels, age, and linked ADR context.
2. **Closeout gate** — before attestation, `gz ghi check ADR-X.Y.Z` surfaces associated
   issues so none are silently abandoned.
3. **Orphan detection** — `gz ghi check --all` highlights issues not linked to any ADR.

## Lane

Heavy — new CLI subcommand with docs, BDD, and manpage requirements.

## Consequences

- Closeout ceremony gains a reproducible issue-association check.
- Triage becomes a first-class governance surface rather than ad-hoc `gh` invocations.
- Requires `gh` CLI authenticated and available on PATH.
