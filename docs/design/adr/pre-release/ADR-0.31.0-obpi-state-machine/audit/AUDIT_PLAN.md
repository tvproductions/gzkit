# AUDIT PLAN (Gate-5) — ADR-0.31.0

| Field | Value |
| ----- | ----- |
| ADR ID | ADR-0.31.0-obpi-state-machine |
| ADR Title | OBPI State Machine and Runtime Invariant Monitor |
| SemVer | 0.31.0 |
| ADR Dir | docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine |
| Audit Date | 2026-07-05 |
| Auditor(s) | g0 (operator, attesting); pipeline-orchestrator driver; spec-reviewer + quality-reviewer (independent) |

## Purpose

Confirm ADR-0.31.0 is complete by validating its claims with reproducible evidence and the bound fidelity gate — moving COMPLETED → VALIDATED.

**Audit Trigger:** Operator-invoked `/gz-adr-audit 0.31.0` (post-completion Gate-5 validation). Movement III Phase 1 KEEL; released as [v0.31.0].

## Scope & Inputs

**Thesis (from ADR § Decision / § Target Scope):** the airlock-critical *tracer* of a canonical OBPI state machine — the first end-to-end slice (schema → model → monitor → CLI → ledger), NOT the full eight-property machine. Three OBPIs:

- OBPI-01 `state-transition-models` — closed `OBPIState` enum + `State`/`Transition` Pydantic models + JSON schema (pure model layer).
- OBPI-02 `withdraw-supersede-transitions` — `gz obpi withdraw` / `gz obpi supersede` as monitor-validated first-class transitions emitting canonical events.
- OBPI-03 `runtime-invariant-monitor` — the load-bearing monitor at the artifact-graph write chokepoint refusing silent `status:` frontmatter drift (GHI #348 class).

**Primary contract surfaces:**

- `uv run gz obpi withdraw` / `uv run gz obpi supersede` (witnessed transitions)
- `uv run gz frontmatter reconcile` (monitor-guarded write chokepoint)
- `src/gzkit/core/obpi_state_machine.py` (`OBPIState`, `CANONICAL_TRANSITIONS`, `OBPI_STATES`)
- `src/gzkit/governance/obpi_transition_monitor.py` (`TransitionMonitor`)
- `src/gzkit/governance/frontmatter_coherence.py` (monitor integration)

## Planned Checks

| Check | Command / Method | Expected Signal | Status |
|-------|------------------|-----------------|--------|
| Ledger completeness (L2) | `uv run gz adr audit-check ADR-0.31.0` | All OBPIs PASS; exit 0 | Executed |
| Fidelity gate (bound, Step 3) | `uv run gz adr fidelity ADR-0.31.0` | 2/2 assertions pass; exit 0 | Executed |
| Independent REQ trace | spec-reviewer (read-only) | 18/18 REQs genuine, no cosmetic proofs | Executed |
| Independent structural coherence | quality-reviewer (read-only) | COHERENT integration into the ADR thesis | Executed |
| Full unit suite (VALIDATED confidence) | `uv run -m unittest -q` | All pass | Executed |

## Risk Focus

- **REQ-0.31.0-03-03 landing falsifier** — conflict-of-interest guard: the driver fixed the `covers-backfill` heuristic that had flagged it (GHI #667); independent spec-reviewer must confirm the test is genuinely semantic, not laundered.
- **Single-monitor integration claim** (Decision item 4) — does every governed-key writer pass the monitor, or only the reconcile chokepoint? (Surfaced the sibling-path gap → GHI #668.)
- **Terminal-status clobber** (GHI #348 class) reproducible via lifecycle verbs.

## Acceptance Criteria

- Ledger complete (audit-check exit 0); fidelity gate green.
- Both independent reviewers' verdicts recorded; all shortfalls resolved before VALIDATED.
- Proof logs under `audit/proofs/`; referenced in `AUDIT.md`.
- No edits to accepted/attested ADR or OBPI prose; corrections annotated forward via GHIs.
- Operator verbal audit attestation obtained; `validated` receipt emitted; `gz adr report` confirms Validated.
