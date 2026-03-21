---
id: ADR-0.19.0-closeout-audit-processes
status: Proposed
semver: 0.19.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-18
promoted_from: ADR-pool.audit-system
---

# ADR-0.19.0-closeout-audit-processes: Closeout & Audit Processes

## Intent

Today, closing out an ADR requires manually chaining `gz closeout`, then running
each quality gate separately (`gz lint`, `gz test`, `gz typecheck`, optionally
`mkdocs build --strict` and `behave`), then running `gz attest`, then running
`gz audit`, then running `gz adr emit-receipt`. This is six or more manual
command invocations in a specific order, with no enforcement that the operator
completes the full sequence. The result is ADRs that are partially closed out —
attestation missing, audit never run, version never bumped, validation receipt
never emitted.

After this ADR, `gz closeout ADR-X.Y.Z` will be a single end-to-end command
that runs the entire closeout pipeline: OBPI verification, quality gates,
attestation prompt, version bump, and ledger recording. Similarly, `gz audit
ADR-X.Y.Z` will be a single command that verifies ledger completeness, runs
proof collection, creates audit artifacts, emits the validation receipt, and
transitions the ADR to Validated. Both commands will produce identical behavior
in gzkit and airlineops.

The scope is explicitly limited to orchestrating existing capabilities into
single commands. No new quality checks are added — the existing gates, tests,
and lint checks are wired into the pipeline.

---

## Decision

1. Consolidate `gz closeout` into a single orchestrated pipeline because the
   current multi-command workflow is error-prone and routinely incomplete.

2. Consolidate `gz audit` into a single orchestrated pipeline because manual
   audit artifact generation is tedious and skipped when operators are fatigued.

3. Subsume `gz gates` into the closeout pipeline because it duplicates
   verification that closeout must perform anyway. The standalone command
   becomes a deprecation alias.

4. Subsume manual `gz attest` invocation during closeout because attestation is
   a stage of closeout, not a separate operator responsibility.

5. Maintain cross-project parity with airlineops because divergent command
   contracts create operator confusion when switching between repositories.

### `closeout` pipeline stages

1. Checks OBPI completion (all briefs done)
2. Runs quality gates (lint, typecheck, test, docs, BDD per lane)
3. Records gate results in ledger
4. Prompts for human attestation
5. Records attestation in ledger
6. Bumps project version to match ADR semver
7. Marks ADR as Completed

### `audit` pipeline stages

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

## Alternatives Considered

- **Keep the multi-command workflow:** Rejected because operators routinely skip
  steps (attestation, audit, version bump), leaving ADRs in inconsistent states.
  ADR-0.19.0 was itself discovered with version stuck at 0.12.0 while releases
  had reached 0.18.0.

- **Create a shell script wrapper:** Rejected because shell scripts cannot enforce
  gate ordering, record ledger events atomically, or provide structured error
  recovery. The orchestration must live in the Python CLI for cross-platform
  reliability and ledger integration.

- **Merge closeout and audit into one command:** Rejected because closeout and
  audit are distinct governance phases — closeout is human-attested completion,
  audit is post-attestation reconciliation. Merging them conflates two different
  trust boundaries.

---

## Consequences

### Positive

- Operators run one command instead of six, eliminating the most common source
  of incomplete ADR lifecycle transitions.
- Version sync happens automatically during closeout, preventing version drift.
- Audit artifacts are generated deterministically, not manually assembled.

### Negative

- `gz gates` and manual `gz attest` during closeout become deprecated aliases,
  requiring operator re-training.
- The closeout command becomes more complex internally, requiring careful error
  handling for each pipeline stage.

## Non-Goals

- Adding new quality gates beyond what exists today. This ADR orchestrates
  existing checks, it does not create new ones.
- Automating the human attestation decision. The prompt presents evidence; the
  human decides.
- Making closeout/audit work across repositories simultaneously. Each repository
  runs its own pipeline independently.
- Changing the ledger event schema. Existing event types are reused.

## Architectural Alignment

This ADR follows the existing command pattern established by `src/gzkit/cli.py`
where lifecycle commands (`closeout_cmd`, `audit_cmd`, `attest`) are top-level
functions that orchestrate calls to shared helpers in `src/gzkit/commands/common.py`
and append events via `src/gzkit/ledger.py` factory functions.

The closeout pipeline follows the precedent set by `gz obpi pipeline` in
`src/gzkit/pipeline_runtime.py` — sequential stage execution with fail-closed
gates between stages and ledger evidence at each transition.

### Anti-patterns to avoid

- Do not bypass the ledger by writing attestation state directly to ADR files.
  All state transitions flow through ledger events first.
- Do not shell out to `gz gates` or `gz attest` as subprocesses from within
  `closeout_cmd`. Call the underlying Python functions directly to maintain
  atomicity and error context.
- Do not create new event types when existing ones (`attested`, `gate_checked`,
  `closeout_initiated`, `audit_receipt_emitted`) already carry the needed semantics.

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 9
- Baseline Range: 5+
- Baseline Selected: 9
- Split Single-Narrative: 0
- Split Surface Boundary: 0
- Split State Anchor: 0
- Split Testability Ceiling: 0
- Split Total: 0
- Final Target OBPI Count: 9

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] OBPI-0.19.0-01: `gz closeout ADR-X.Y.Z` — end-to-end closeout pipeline
- [ ] OBPI-0.19.0-02: `gz audit ADR-X.Y.Z` — end-to-end audit pipeline
- [ ] OBPI-0.19.0-03: Equivalent commands in airlineops (`opsdev closeout`, `opsdev audit`)
- [ ] OBPI-0.19.0-04: Audit includes attestation record, gate results, evidence links
- [ ] OBPI-0.19.0-05: `audit_generated` event appended to ledger
- [ ] OBPI-0.19.0-06: Audit templates and evidence aggregation from ledger
- [ ] OBPI-0.19.0-07: ADR status transition: Completed → Validated (after audit)
- [ ] OBPI-0.19.0-08: Deprecate `gz gates` as a standalone command (subsumed by closeout)
- [ ] OBPI-0.19.0-09: Deprecate manual `gz attest` during closeout (subsumed by closeout) ---

## Target Scope

- `gz closeout ADR-X.Y.Z` — end-to-end closeout pipeline
- `gz audit ADR-X.Y.Z` — end-to-end audit pipeline
- Equivalent commands in airlineops (`opsdev closeout`, `opsdev audit`)
- Audit includes attestation record, gate results, evidence links
- `audit_generated` event appended to ledger
- Audit templates and evidence aggregation from ledger
- ADR status transition: Completed → Validated (after audit)
- Deprecate `gz gates` as a standalone command (subsumed by closeout)
- Deprecate manual `gz attest` during closeout (subsumed by closeout)

---

## Dependencies

- **Related:** ADR-pool.airlineops-direct-governance-migration (cross-project command parity)

---

## Notes

- Audit runs AFTER attestation (reconciliation, not proof)
- Audit directory: `docs/design/adr/{foundation|pre-release|<major>.0}/ADR-X.Y.Z-{slug}/audit/`
- Anchor drift and dirty worktree issues that block closeout today should be resolvable within the closeout pipeline itself (re-emit + commit cycle)
- The closeout command should handle the emit-sync-emit pattern internally rather than requiring the operator to manually chain git-sync between receipt emissions
- Audit's value demonstration step (currently manual) could be partially automated by running ADR-specific CLI commands from the ADR's evidence section

## Q&A Transcript

<!-- Interview transcript preserved for context -->

Promotion derived from `ADR-pool.audit-system` on 2026-03-18; executable scope was carried forward from the pool ADR instead of reseeded as placeholders.

## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

- Keep this work in the pool backlog until reprioritized.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.19.0 | Pending | | | |
