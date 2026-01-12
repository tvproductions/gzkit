# Methodology

Methodology defines **how work flows through phases**. It is the shared layer of the covenant.

## Purpose

Without methodology:

- Work happens in undefined order
- Dependencies are discovered late
- Status is unknowable
- Verification is ad-hoc

Methodology provides structure without bureaucracy.

## The Phase Model

gzkit inherits the spec-kit phase model:

```
constitute → specify → plan → implement → analyze
```

| Phase | Purpose | Primary Gate |
|-------|---------|--------------|
| Constitute | Define canon and constitutions | — |
| Specify | Create briefs with acceptance criteria | Gate 1 (ADR) |
| Plan | Manage ADRs and linkage | Gate 1 (ADR) |
| Implement | Build and verify | Gates 2, 3, 4 |
| Analyze | Audit and attest | Gate 5 (Human) |

## The Five Gates

Gates are verification checkpoints within phases:

| Gate | Name | Phase | Purpose |
|------|------|-------|---------|
| 1 | ADR | Specify/Plan | Record intent before implementation |
| 2 | TDD | Implement | Verify correctness through tests |
| 3 | Docs | Implement | Ensure docs match behavior |
| 4 | BDD | Implement | Verify external contracts |
| 5 | Human | Analyze | Human observes and attests |

Gates are:
- **Sequential** (Gate N requires Gate N-1)
- **Observable** (status is always knowable)
- **Evidence-producing** (each gate generates artifacts)

## Lane Doctrine

Not all work needs all gates. Lanes configure gate requirements:

| Lane | Gates | Trigger |
|------|-------|---------|
| **Lite** | 1, 2 | Internal changes only |
| **Heavy** | 1, 2, 3, 4, 5 | External contract changes |

### Lite Lane

For internal changes that don't affect external contracts:

- Refactoring
- Bug fixes (no API change)
- Internal tooling
- Performance improvements

Requires: ADR (intent) + TDD (tests)

### Heavy Lane

For changes that affect external contracts:

- New CLI commands
- API changes
- Schema changes
- User-facing error messages

Requires: All five gates including human attestation

## Workflow States

Work items progress through states:

```
Draft → Proposed → Accepted → [implementation] → Completed
                                              → Abandoned
                                              → Superseded
```

| State | Meaning |
|-------|---------|
| Draft | Being authored |
| Proposed | Ready for review |
| Accepted | Approved for implementation |
| Completed | All gates passed, human attested |
| Abandoned | Work stopped (Dropped) |
| Superseded | Replaced by newer ADR |

## For Agents

When working in a gzkit project:

1. **Respect phase order** — Don't implement before planning
2. **Complete gates sequentially** — Gate 2 requires Gate 1
3. **Generate evidence** — Each gate should produce artifacts
4. **Stop at Gate 5** — Human attestation is not your job

## For Humans

When overseeing agent work:

1. **Review at phase boundaries** — Check ADRs before implementation
2. **Monitor gate status** — `gz status` shows current state
3. **Attest when ready** — Gate 5 requires your observation
4. **Use lanes appropriately** — Don't heavy-lane internal changes
