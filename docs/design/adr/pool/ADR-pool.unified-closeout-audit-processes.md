---
id: ADR-pool.unified-closeout-audit-processes
status: Pool
parent: PRD-GZKIT-1.0.0
lane: Heavy
enabler: null
---

# ADR-pool.unified-closeout-audit-processes: Unified Closeout & Audit Processes

## Status

Pool

## Date

2026-03-18

## Parent PRD

[PRD-GZKIT-1.0.0](../../prd/PRD-GZKIT-1.0.0.md)

---

## Intent

Make **closeout** and **audit** each a single end-to-end orchestrated command that runs its full pipeline without manual subcommand chaining. Both commands must behave identically in gzkit and airlineops.

---

## Problem Statement

Today, closeout and audit are fragmented multi-step processes requiring manual orchestration:

**Closeout (current):**

1. `gz closeout ADR-X.Y.Z` — initiates only, does not run gates
2. `gz gates --adr ADR-X.Y.Z` — must be run separately to record gate results
3. `gz attest ADR-X.Y.Z --status completed` — blocked until gates are formally recorded

**Audit (current):**

1. Manual creation of audit plan and proofs directory
2. Separate execution of verification commands
3. Manual value demonstration
4. Separate receipt emission
5. Manual status update to Validated

**Cross-project inconsistency:**

- gzkit: `gz closeout` (initiates) + `gz gates` (quality) + `gz attest` (record)
- airlineops: `uv run -m opsdev gates` (quality only, different name, different scope)

Operators must remember different command names and manual sequences per project.

---

## Decision

Two orchestrated processes, same name and behavior in both projects:

### `closeout`

Single command that:

1. Checks OBPI completion (all briefs done)
2. Runs quality gates (lint, typecheck, test, docs, BDD per lane)
3. Records gate results
4. Prompts for human attestation
5. Records attestation
6. Marks ADR as Completed

### `audit`

Single command that:

1. Verifies ledger completeness (Layer 2 trust)
2. Runs Gate 5 verification checks
3. Demonstrates ADR value (capability walkthrough)
4. Creates audit artifacts (plan, proofs, report)
5. Emits validation receipt
6. Marks ADR as Validated

### Cross-project parity

- Same command names: `closeout`, `audit`
- Same pipeline stages in same order
- Same exit codes and error messages
- Shared contract: if it works in gzkit, it works in airlineops

---

## Target Scope

- `gz closeout ADR-X.Y.Z` — end-to-end closeout pipeline
- `gz audit ADR-X.Y.Z` — end-to-end audit pipeline
- Equivalent commands in airlineops (`opsdev closeout`, `opsdev audit`)
- Deprecate `gz gates` as a standalone command (subsumed by closeout)
- Deprecate manual `gz attest` during closeout (subsumed by closeout)

---

## Dependencies

- **Related:** ADR-pool.audit-system (covers audit artifact generation — may be subsumed by this ADR)
- **Related:** ADR-pool.airlineops-direct-governance-migration (cross-project command parity)

---

## Notes

- Anchor drift and dirty worktree issues that block closeout today should be resolvable within the closeout pipeline itself (re-emit + commit cycle)
- The closeout command should handle the emit-sync-emit pattern internally rather than requiring the operator to manually chain git-sync between receipt emissions
- Audit's value demonstration step (currently manual) could be partially automated by running ADR-specific CLI commands from the ADR's evidence section
